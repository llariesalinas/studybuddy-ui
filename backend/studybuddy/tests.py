import re
from datetime import date, time
from decimal import Decimal
from unittest.mock import Mock, patch
from uuid import uuid4

from django.core.cache import cache
from django.core import mail
from django.contrib.auth.models import User
from django.db import connection
from django.test import override_settings
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APITestCase
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken

from .chat.services import get_current_booking_context, get_current_booking_contexts, get_partner_context
from .models import (
    Booking,
    Course,
    EmailOTPChallenge,
    PartnerInstitution,
    Payment,
    PaymentMethod,
    Rating,
    Subjects,
    Tutor,
    TutorAvailability,
    TutorAvailabilityOverride,
    TutorSubjects,
    UserProfile,
    Transaction,
    TutorPayoutAccount,
    Wallet,
    WithdrawalRequest,
    Preference,
)
from .chat.models import ChatRoom, Message


class RecommendTutorsViewTests(APITestCase):
    def setUp(self):
        self.subject = Subjects.objects.create(
            subject_code="MATH101",
            subject_name="College Algebra",
            department="Math",
        )
        self.other_subject = Subjects.objects.create(
            subject_code="SCI101",
            subject_name="Science",
            department="Science",
        )
        self.student_user = User.objects.create_user(
            username="student",
            email="student@example.com",
            password="password",
        )
        self.student_profile = UserProfile.objects.create(
            user=self.student_user,
            fname="Student",
            mname="",
            lname="User",
            role="Tutee",
            year_level=11,
        )
        self.client.force_authenticate(user=self.student_user)
        self.search_date = date(2026, 5, 11)

    def create_tutor(
        self,
        username,
        subject=None,
        hourly_rate=200,
        can_online=True,
        can_f2f=False,
    ):
        user = User.objects.create_user(
            username=username,
            email=f"{username}@example.com",
            password="password",
        )
        profile = UserProfile.objects.create(
            user=user,
            fname=username.title(),
            mname="",
            lname="Tutor",
            role="Tutor",
            year_level=12,
        )
        tutor = Tutor.objects.create(
            profile=profile,
            hourly_rate=hourly_rate,
            can_online=can_online,
            can_f2f=can_f2f,
            teaching_level="SHS",
        )
        TutorSubjects.objects.create(
            tutor=tutor,
            subject=subject or self.subject,
            expertise_level=5,
        )
        return tutor

    def add_slots(self, tutor, slot_times):
        return [
            TutorAvailability.objects.create(
                tutor=tutor,
                day="Mon",
                time_slot=slot_time,
                is_active=True,
            )
            for slot_time in slot_times
        ]

    def recommend(self, **overrides):
        payload = {
            "subject": self.subject.subject_code,
            "preferred_mode": "Online",
            "min_budget": 100,
            "max_budget": 300,
            "date": self.search_date.isoformat(),
            "start_time": "14:00",
            "end_time": "15:00",
        }
        payload.update(overrides)
        return self.client.post("/api/recommend-tutors/", payload, format="json")

    def response_ids(self, response):
        return {item["id"] for item in response.data}

    def test_filters_by_subject_mode_and_budget(self):
        matching = self.create_tutor("matching")
        wrong_subject = self.create_tutor("science", subject=self.other_subject)
        f2f_only = self.create_tutor("f2f", can_online=False, can_f2f=True)
        expensive = self.create_tutor("expensive", hourly_rate=500)

        for tutor in [matching, wrong_subject, f2f_only, expensive]:
            self.add_slots(tutor, [time(14, 0), time(14, 30)])

        response = self.recommend()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.response_ids(response), {matching.profile_id})

    def test_multislot_search_requires_every_slot(self):
        complete = self.create_tutor("complete")
        incomplete = self.create_tutor("incomplete")
        self.add_slots(complete, [time(14, 0), time(14, 30)])
        self.add_slots(incomplete, [time(14, 0)])

        response = self.recommend()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.response_ids(response), {complete.profile_id})

    def test_booked_slot_excludes_tutor(self):
        available = self.create_tutor("available")
        booked = self.create_tutor("booked")
        self.add_slots(available, [time(14, 0), time(14, 30)])
        booked_slots = self.add_slots(booked, [time(14, 0), time(14, 30)])
        Booking.objects.create(
            student=self.student_profile,
            tutor=booked,
            availability=booked_slots[1],
            session_date=self.search_date,
            session_mode="Online",
            status="Confirmed",
        )

        response = self.recommend()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.response_ids(response), {available.profile_id})

    def test_availability_overrides_exclude_tutors(self):
        available = self.create_tutor("plain")
        full_day_blocked = self.create_tutor("fullday")
        slot_blocked = self.create_tutor("slot")
        self.add_slots(available, [time(14, 0), time(14, 30)])
        self.add_slots(full_day_blocked, [time(14, 0), time(14, 30)])
        slot_blocked_slots = self.add_slots(slot_blocked, [time(14, 0), time(14, 30)])
        TutorAvailabilityOverride.objects.create(
            tutor=full_day_blocked,
            override_date=self.search_date,
            is_full_day=True,
        )
        TutorAvailabilityOverride.objects.create(
            tutor=slot_blocked,
            override_date=self.search_date,
            availability=slot_blocked_slots[0],
            is_full_day=False,
        )

        response = self.recommend()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.response_ids(response), {available.profile_id})

    def test_missing_date_time_fields_remain_supported(self):
        tutor = self.create_tutor("legacy")

        response = self.recommend(date=None, start_time=None, end_time=None)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.response_ids(response), {tutor.profile_id})


class ChatFeatureTests(APITestCase):
    def setUp(self):
        self.tutee_user = User.objects.create_user(
            username="chat-tutee",
            email="chat-tutee@example.com",
            password="password",
        )
        self.tutee_profile = UserProfile.objects.create(
            user=self.tutee_user,
            fname="Chat",
            mname="",
            lname="Tutee",
            role="Tutee",
        )
        self.tutor_user = User.objects.create_user(
            username="chat-tutor",
            email="chat-tutor@example.com",
            password="password",
        )
        self.tutor_profile = UserProfile.objects.create(
            user=self.tutor_user,
            fname="Chat",
            mname="",
            lname="Tutor",
            role="Tutor",
        )
        self.tutor = Tutor.objects.create(
            profile=self.tutor_profile,
            hourly_rate=250,
            can_online=True,
            can_f2f=True,
            teaching_level="SHS",
        )
        self.subject = Subjects.objects.create(
            subject_code="ETH101",
            subject_name="Ethics",
            department="Humanities",
        )
        TutorSubjects.objects.create(
            tutor=self.tutor,
            subject=self.subject,
            expertise_level=5,
        )
        self.availability = TutorAvailability.objects.create(
            tutor=self.tutor,
            day="Mon",
            time_slot=time(14, 0),
            is_active=True,
        )
        self.booking_request_id = uuid4()
        self.booking = Booking.objects.create(
            student=self.tutee_profile,
            tutor=self.tutor,
            availability=self.availability,
            session_date=date(2026, 5, 18),
            session_mode="F2F",
            preferred_location="Library",
            booking_request_id=self.booking_request_id,
            status="Pending",
        )

    def make_booking(self, status, session_mode='F2F', preferred_location='Library',
                     session_date=None, days_ago=0):
        from datetime import date, timedelta
        from uuid import uuid4
        # Cancel the setUp booking so it doesn't interfere with this test's query
        self.booking.status = 'Cancelled'
        self.booking.session_date = date.today() - timedelta(days=8)
        self.booking.save(update_fields=['status', 'session_date'])
        d = session_date or (date.today() - timedelta(days=days_ago))
        return Booking.objects.create(
            student=self.tutee_profile,
            tutor=self.tutor,
            availability=self.availability,
            session_date=d,
            session_mode=session_mode,
            preferred_location=preferred_location,
            booking_request_id=uuid4(),
            status=status,
        )

    def make_extra_tutor_room(self, username, updated_at=None):
        user = User.objects.create_user(
            username=username,
            email=f"{username}@example.com",
            password="password",
        )
        profile = UserProfile.objects.create(
            user=user,
            fname=username.title(),
            mname="",
            lname="Tutor",
            role="Tutor",
        )
        tutor = Tutor.objects.create(
            profile=profile,
            hourly_rate=250,
            can_online=True,
            can_f2f=True,
            teaching_level="SHS",
        )
        availability = TutorAvailability.objects.create(
            tutor=tutor,
            day="Mon",
            time_slot=time(14, 0),
            is_active=True,
        )
        room = ChatRoom.objects.create(
            tutee=self.tutee_profile,
            tutor=profile,
            **({'updated_at': updated_at} if updated_at else {}),
        )
        return user, profile, tutor, availability, room

    def test_status_intent_pending_f2f_returns_pending_location(self):
        room = ChatRoom.objects.create(tutee=self.tutee_profile, tutor=self.tutor_profile)
        booking = self.make_booking('Pending', session_mode='F2F')
        context = get_current_booking_context(room)
        self.assertIsNotNone(context)
        self.assertEqual(context['status_intent'], 'pending_location')

    def test_status_intent_pending_online_returns_pending(self):
        room = ChatRoom.objects.create(tutee=self.tutee_profile, tutor=self.tutor_profile)
        booking = self.make_booking('Pending', session_mode='Online')
        context = get_current_booking_context(room)
        self.assertIsNotNone(context)
        self.assertEqual(context['status_intent'], 'pending')

    def test_status_intent_confirmed_returns_confirmed(self):
        from datetime import date
        room = ChatRoom.objects.create(tutee=self.tutee_profile, tutor=self.tutor_profile)
        self.make_booking('Confirmed', session_date=date(2026, 6, 10))
        context = get_current_booking_context(room)
        self.assertIsNotNone(context)
        self.assertEqual(context['status_intent'], 'confirmed')

    def test_confirmed_future_session_returns_upcoming(self):
        from datetime import date, timedelta
        room = ChatRoom.objects.create(tutee=self.tutee_profile, tutor=self.tutor_profile)
        future_date = date.today() + timedelta(days=2)
        self.make_booking('Confirmed', session_date=future_date)
        context = get_current_booking_context(room)
        self.assertIsNotNone(context)
        self.assertEqual(context['status_intent'], 'confirmed')
        self.assertEqual(context['status'], 'Upcoming')

    def test_confirmed_active_session_returns_ongoing(self):
        from django.utils import timezone
        from datetime import timedelta
        from uuid import uuid4
        room = ChatRoom.objects.create(tutee=self.tutee_profile, tutor=self.tutor_profile)
        now_local = timezone.localtime(timezone.now())
        active_availability = TutorAvailability.objects.create(
            tutor=self.tutor,
            day="Mon",
            time_slot=(now_local - timedelta(minutes=10)).time(),
            is_active=True,
        )
        self.booking.status = 'Cancelled'
        self.booking.save()

        Booking.objects.create(
            student=self.tutee_profile,
            tutor=self.tutor,
            availability=active_availability,
            session_date=now_local.date(),
            session_mode='Online',
            booking_request_id=uuid4(),
            status='Confirmed',
        )
        context = get_current_booking_context(room)
        self.assertIsNotNone(context)
        self.assertEqual(context['status_intent'], 'ongoing')
        self.assertEqual(context['status'], 'Ongoing')

    def test_confirmed_past_session_returns_payment_required(self):
        from datetime import date, timedelta
        room = ChatRoom.objects.create(tutee=self.tutee_profile, tutor=self.tutor_profile)
        past_date = date.today() - timedelta(days=1)
        self.make_booking('Confirmed', session_date=past_date)
        context = get_current_booking_context(room)
        self.assertIsNotNone(context)
        self.assertEqual(context['status_intent'], 'payment_required')
        self.assertEqual(context['status'], 'Payment Required')

    def test_status_intent_awaiting_payment_returns_awaiting_payment(self):
        from datetime import date
        room = ChatRoom.objects.create(tutee=self.tutee_profile, tutor=self.tutor_profile)
        self.make_booking('Awaiting Payment Verification', session_date=date(2026, 6, 10))
        context = get_current_booking_context(room)
        self.assertIsNotNone(context)
        self.assertEqual(context['status_intent'], 'awaiting_payment')

    def test_status_intent_completed_unrated_returns_review_pending(self):
        room = ChatRoom.objects.create(tutee=self.tutee_profile, tutor=self.tutor_profile)
        self.make_booking('Completed', days_ago=1)
        context = get_current_booking_context(room)
        self.assertIsNotNone(context)
        self.assertEqual(context['status_intent'], 'review_pending')

    def test_status_intent_completed_rated_returns_none(self):
        room = ChatRoom.objects.create(tutee=self.tutee_profile, tutor=self.tutor_profile)
        booking = self.make_booking('Completed', days_ago=1)
        Rating.objects.create(
            booking=booking,
            student=self.tutee_profile,
            tutor=self.tutor,
            rating_score=5,
        )
        context = get_current_booking_context(room)
        self.assertIsNone(context)

    def test_status_intent_rejected_recent_returns_rejected(self):
        room = ChatRoom.objects.create(tutee=self.tutee_profile, tutor=self.tutor_profile)
        self.make_booking('Rejected', days_ago=2)
        context = get_current_booking_context(room)
        self.assertIsNotNone(context)
        self.assertEqual(context['status_intent'], 'rejected')

    def test_status_intent_cancelled_recent_returns_cancelled(self):
        room = ChatRoom.objects.create(tutee=self.tutee_profile, tutor=self.tutor_profile)
        self.make_booking('Cancelled', days_ago=3)
        context = get_current_booking_context(room)
        self.assertIsNotNone(context)
        self.assertEqual(context['status_intent'], 'cancelled')

    def test_status_intent_terminal_older_than_7_days_returns_none(self):
        room = ChatRoom.objects.create(tutee=self.tutee_profile, tutor=self.tutor_profile)
        self.make_booking('Rejected', days_ago=8)
        context = get_current_booking_context(room)
        self.assertIsNone(context)

    def test_chat_rooms_endpoint_returns_paginated_payload(self):
        from django.utils import timezone
        from datetime import timedelta

        base_time = timezone.now()
        rooms = []
        for index in range(4):
            *_, room = self.make_extra_tutor_room(
                f"page-tutor-{index}",
                updated_at=base_time - timedelta(minutes=index),
            )
            rooms.append(room)

        self.client.force_authenticate(user=self.tutee_user)
        response = self.client.get("/api/chat/rooms/?page_size=2")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertTrue(response.data["has_more"])
        self.assertIsNotNone(response.data["next_cursor"])
        self.assertEqual(response.data["total_unread"], 0)
        self.assertEqual(
            [room["id"] for room in response.data["results"]],
            [rooms[0].id, rooms[1].id],
        )

    def test_chat_rooms_cursor_returns_next_page_without_duplicates(self):
        from django.utils import timezone
        from datetime import timedelta

        base_time = timezone.now()
        for index in range(4):
            self.make_extra_tutor_room(
                f"cursor-tutor-{index}",
                updated_at=base_time - timedelta(minutes=index),
            )

        self.client.force_authenticate(user=self.tutee_user)
        first_page = self.client.get("/api/chat/rooms/?page_size=2")
        second_page = self.client.get(
            f"/api/chat/rooms/?page_size=2&cursor={first_page.data['next_cursor']}"
        )

        first_ids = {room["id"] for room in first_page.data["results"]}
        second_ids = {room["id"] for room in second_page.data["results"]}
        self.assertEqual(first_page.status_code, 200)
        self.assertEqual(second_page.status_code, 200)
        self.assertEqual(len(second_ids), 2)
        self.assertFalse(first_ids & second_ids)
        self.assertFalse(second_page.data["has_more"])

    def test_chat_rooms_total_unread_includes_rooms_outside_page(self):
        from django.utils import timezone
        from datetime import timedelta

        base_time = timezone.now()
        for index in range(3):
            tutor_user, *_, room = self.make_extra_tutor_room(
                f"unread-tutor-{index}",
                updated_at=base_time - timedelta(minutes=index),
            )
            Message.objects.create(
                room=room,
                sender=tutor_user,
                content=f"Unread {index}",
                is_read=False,
            )

        self.client.force_authenticate(user=self.tutee_user)
        response = self.client.get("/api/chat/rooms/?page_size=1")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["total_unread"], 3)

    def test_batched_current_booking_context_matches_single_room_helper(self):
        from datetime import timedelta
        from uuid import uuid4

        today = date.today()
        room_pending = ChatRoom.objects.create(tutee=self.tutee_profile, tutor=self.tutor_profile)

        _, confirmed_profile, confirmed_tutor, confirmed_availability, room_confirmed = (
            self.make_extra_tutor_room("bulk-confirmed")
        )
        Booking.objects.create(
            student=self.tutee_profile,
            tutor=confirmed_tutor,
            availability=confirmed_availability,
            session_date=today + timedelta(days=2),
            session_mode="Online",
            booking_request_id=uuid4(),
            status="Confirmed",
        )

        _, completed_profile, completed_tutor, completed_availability, room_completed = (
            self.make_extra_tutor_room("bulk-completed")
        )
        Booking.objects.create(
            student=self.tutee_profile,
            tutor=completed_tutor,
            availability=completed_availability,
            session_date=today - timedelta(days=1),
            session_mode="Online",
            booking_request_id=uuid4(),
            status="Completed",
        )

        _, terminal_profile, terminal_tutor, terminal_availability, room_terminal = (
            self.make_extra_tutor_room("bulk-terminal")
        )
        Booking.objects.create(
            student=self.tutee_profile,
            tutor=terminal_tutor,
            availability=terminal_availability,
            session_date=today - timedelta(days=2),
            session_mode="Online",
            booking_request_id=uuid4(),
            status="Cancelled",
        )

        *_, room_none = self.make_extra_tutor_room("bulk-none")
        rooms = [room_pending, room_confirmed, room_completed, room_terminal, room_none]
        batched_contexts = get_current_booking_contexts(rooms)

        for room in rooms:
            self.assertEqual(batched_contexts[room.id], get_current_booking_context(room))

    def test_chat_room_list_query_count_does_not_scale_per_room(self):
        from django.utils import timezone
        from datetime import timedelta
        from uuid import uuid4

        base_time = timezone.now()
        for index in range(6):
            _, _, tutor, availability, room = self.make_extra_tutor_room(
                f"query-tutor-{index}",
                updated_at=base_time - timedelta(minutes=index),
            )
            Booking.objects.create(
                student=self.tutee_profile,
                tutor=tutor,
                availability=availability,
                session_date=date.today() + timedelta(days=index + 1),
                session_mode="Online",
                booking_request_id=uuid4(),
                status="Pending",
            )

        self.client.force_authenticate(user=self.tutee_user)
        with CaptureQueriesContext(connection) as two_room_queries:
            two_room_response = self.client.get("/api/chat/rooms/?page_size=2")
        with CaptureQueriesContext(connection) as six_room_queries:
            six_room_response = self.client.get("/api/chat/rooms/?page_size=6")

        self.assertEqual(two_room_response.status_code, 200)
        self.assertEqual(six_room_response.status_code, 200)
        self.assertLessEqual(len(six_room_queries), len(two_room_queries) + 3)

    def test_partner_context_counts_completed_session_groups_and_hours(self):
        room = ChatRoom.objects.create(tutee=self.tutee_profile, tutor=self.tutor_profile)
        second_slot = TutorAvailability.objects.create(
            tutor=self.tutor,
            day="Mon",
            time_slot=time(14, 30),
            is_active=True,
        )
        first_group_id = uuid4()
        self.booking.status = 'Cancelled'
        self.booking.save(update_fields=['status'])
        Booking.objects.create(
            student=self.tutee_profile,
            tutor=self.tutor,
            availability=self.availability,
            session_date=date(2026, 5, 19),
            session_mode="Online",
            session_group_id=first_group_id,
            status="Completed",
        )
        Booking.objects.create(
            student=self.tutee_profile,
            tutor=self.tutor,
            availability=second_slot,
            session_date=date(2026, 5, 19),
            session_mode="Online",
            session_group_id=first_group_id,
            status="Completed",
        )
        Booking.objects.create(
            student=self.tutee_profile,
            tutor=self.tutor,
            availability=self.availability,
            session_date=date(2026, 5, 20),
            session_mode="Online",
            status="Completed",
        )

        context = get_partner_context(room, self.tutee_user)

        self.assertEqual(context['sessions_together'], 2)
        self.assertEqual(context['focused_hours'], 1.5)

    def test_partner_context_returns_tutor_topics(self):
        room = ChatRoom.objects.create(tutee=self.tutee_profile, tutor=self.tutor_profile)
        context = get_partner_context(room, self.tutee_user)

        self.assertEqual(context['topics'], ['Ethics'])

    def test_room_read_endpoint_marks_other_user_messages_read(self):
        room = ChatRoom.objects.create(tutee=self.tutee_profile, tutor=self.tutor_profile)
        message = Message.objects.create(
            room=room,
            sender=self.tutor_user,
            content="Please confirm the location.",
        )
        self.client.force_authenticate(user=self.tutee_user)

        response = self.client.post(f"/api/chat/rooms/{room.id}/read/")

        message.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(message.is_read)
        self.assertIsNotNone(message.read_at)

    def test_message_history_returns_latest_messages_in_display_order(self):
        room = ChatRoom.objects.create(tutee=self.tutee_profile, tutor=self.tutor_profile)
        for index in range(55):
            Message.objects.create(
                room=room,
                sender=self.tutee_user if index % 2 == 0 else self.tutor_user,
                content=f"Message {index}",
            )
        self.client.force_authenticate(user=self.tutee_user)

        response = self.client.get(f"/api/chat/rooms/{room.id}/history/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 50)
        self.assertEqual(response.data[0]["content"], "Message 5")
        self.assertEqual(response.data[-1]["content"], "Message 54")

    def test_message_history_after_id_returns_newer_messages(self):
        room = ChatRoom.objects.create(tutee=self.tutee_profile, tutor=self.tutor_profile)
        first = Message.objects.create(room=room, sender=self.tutee_user, content="First")
        second = Message.objects.create(room=room, sender=self.tutor_user, content="Second")
        third = Message.objects.create(room=room, sender=self.tutee_user, content="Third")
        self.client.force_authenticate(user=self.tutee_user)

        response = self.client.get(f"/api/chat/rooms/{room.id}/history/?after_id={first.id}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual([message["id"] for message in response.data], [second.id, third.id])

    def test_non_member_cannot_load_message_history(self):
        other_user = User.objects.create_user(
            username="chat-history-other",
            email="chat-history-other@example.com",
            password="password",
        )
        UserProfile.objects.create(
            user=other_user,
            fname="History",
            mname="",
            lname="Other",
            role="Tutee",
        )
        room = ChatRoom.objects.create(tutee=self.tutee_profile, tutor=self.tutor_profile)
        self.client.force_authenticate(user=other_user)

        response = self.client.get(f"/api/chat/rooms/{room.id}/history/")

        self.assertEqual(response.status_code, 403)

    def test_message_history_serializes_system_message_without_sender(self):
        room = ChatRoom.objects.create(tutee=self.tutee_profile, tutor=self.tutor_profile)
        Message.objects.create(
            room=room,
            sender=None,
            content="System note",
            message_type="system",
        )
        self.client.force_authenticate(user=self.tutee_user)

        response = self.client.get(f"/api/chat/rooms/{room.id}/history/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["sender_name"], "System")
        self.assertIsNone(response.data[0]["sender_profile_id"])

    def test_pending_location_update_posts_booking_event_to_canonical_room(self):
        self.client.force_authenticate(user=self.tutor_user)

        response = self.client.patch(
            f"/api/bookings/{self.booking_request_id}/location/",
            {"preferred_location": "Study Hall 2"},
            format="json",
        )

        self.booking.refresh_from_db()
        room = ChatRoom.objects.get(tutee=self.tutee_profile, tutor=self.tutor_profile)
        message = room.messages.latest("created_at")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.booking.preferred_location, "Study Hall 2")
        self.assertEqual(message.message_type, "booking_event")
        self.assertEqual(message.metadata["event_type"], "location_updated")
        self.assertEqual(message.metadata["booking"]["preferred_location"], "Study Hall 2")

    def test_tutee_can_send_message_via_rest(self):
        room = ChatRoom.objects.create(tutee=self.tutee_profile, tutor=self.tutor_profile)
        self.client.force_authenticate(user=self.tutee_user)

        response = self.client.post(
            f"/api/chat/rooms/{room.id}/messages/",
            {"message": "Hello!", "temp_id": "temp-1"},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Message.objects.filter(room=room, message_type="text").count(), 1)
        self.assertEqual(response.data["message"]["content"], "Hello!")
        self.assertEqual(response.data["message"]["temp_id"], "temp-1")
        self.assertTrue(response.data["message"]["is_me"])
        self.assertEqual(response.data["room"]["id"], room.id)
        self.assertEqual(response.data["room"]["last_message"]["content"], "Hello!")

    def test_tutor_can_send_message_via_rest(self):
        room = ChatRoom.objects.create(tutee=self.tutee_profile, tutor=self.tutor_profile)
        self.client.force_authenticate(user=self.tutor_user)

        response = self.client.post(
            f"/api/chat/rooms/{room.id}/messages/",
            {"message": "Hi!"},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Message.objects.filter(room=room, message_type="text").count(), 1)

    def test_non_member_cannot_send_message_via_rest(self):
        other_user = User.objects.create_user(
            username="chat-other",
            email="chat-other@example.com",
            password="password",
        )
        UserProfile.objects.create(
            user=other_user,
            fname="Chat",
            mname="",
            lname="Other",
            role="Tutee",
        )
        room = ChatRoom.objects.create(tutee=self.tutee_profile, tutor=self.tutor_profile)
        self.client.force_authenticate(user=other_user)

        response = self.client.post(
            f"/api/chat/rooms/{room.id}/messages/",
            {"message": "Nope"},
            format="json",
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(Message.objects.filter(room=room, message_type="text").count(), 0)

    def test_empty_rest_message_returns_400(self):
        room = ChatRoom.objects.create(tutee=self.tutee_profile, tutor=self.tutor_profile)
        self.client.force_authenticate(user=self.tutee_user)

        response = self.client.post(
            f"/api/chat/rooms/{room.id}/messages/",
            {"message": "   "},
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_unauthenticated_rest_message_returns_401(self):
        room = ChatRoom.objects.create(tutee=self.tutee_profile, tutor=self.tutor_profile)

        response = self.client.post(
            f"/api/chat/rooms/{room.id}/messages/",
            {"message": "Hello!"},
            format="json",
        )

        self.assertEqual(response.status_code, 401)


class OnlinePaymentInitiationTests(APITestCase):
    def setUp(self):
        self.tutee_user = User.objects.create_user(
            username="payment-tutee",
            email="payment-tutee@example.com",
            password="password",
        )
        self.tutee_profile = UserProfile.objects.create(
            user=self.tutee_user,
            fname="Payment",
            mname="",
            lname="Tutee",
            role="Tutee",
        )
        self.tutor_user = User.objects.create_user(
            username="payment-tutor",
            email="payment-tutor@example.com",
            password="password",
        )
        self.tutor_profile = UserProfile.objects.create(
            user=self.tutor_user,
            fname="Payment",
            mname="",
            lname="Tutor",
            role="Tutor",
        )
        self.tutor = Tutor.objects.create(
            profile=self.tutor_profile,
            hourly_rate=Decimal("280.00"),
            can_online=True,
            can_f2f=True,
            teaching_level="SHS",
        )
        self.availability = TutorAvailability.objects.create(
            tutor=self.tutor,
            day="Mon",
            time_slot=time(14, 0),
            is_active=True,
        )
        self.booking = Booking.objects.create(
            student=self.tutee_profile,
            tutor=self.tutor,
            availability=self.availability,
            session_date=date(2026, 4, 12),
            session_mode="Online",
            booking_request_id=uuid4(),
            status="Confirmed",
        )
        self.client.force_authenticate(user=self.tutee_user)

    def paymongo_response(self, status_code, payload):
        response = Mock()
        response.status_code = status_code
        response.json.return_value = payload
        return response

    def success_payload(self, session_id="cs_test_123"):
        return {
            "data": {
                "id": session_id,
                "attributes": {
                    "checkout_url": "https://checkout.paymongo.com/test-session",
                },
            },
        }

    def retrieve_payload(self, status_value="paid"):
        return {
            "data": {
                "id": "cs_test_123",
                "attributes": {
                    "status": status_value,
                },
            },
        }

    def create_pending_paymongo_payment(self):
        method = PaymentMethod.objects.create(
            code="PAYMONGO",
            method_name="Pay Online (GCash / Card)",
            is_active=True,
        )
        return Payment.objects.create(
            booking=self.booking,
            amount=Decimal("140.00"),
            method=method,
            payment_status="Pending",
            transaction_reference="cs_test_123",
        )

    def create_second_request_slot(self):
        second_availability = TutorAvailability.objects.create(
            tutor=self.tutor,
            day="Mon",
            time_slot=time(14, 30),
            is_active=True,
        )
        return Booking.objects.create(
            student=self.tutee_profile,
            tutor=self.tutor,
            availability=second_availability,
            session_date=self.booking.session_date,
            session_mode="Online",
            session_group_id=self.booking.session_group_id,
            booking_request_id=self.booking.booking_request_id,
            status=self.booking.status,
        )

    @patch("studybuddy.views.requests.post")
    def test_initiate_online_payment_accepts_paymongo_200_success(self, mock_post):
        mock_post.return_value = self.paymongo_response(200, self.success_payload())

        response = self.client.post(
            "/api/payments/initiate/",
            {"booking_id": self.booking.id},
            format="json",
        )

        payment = Payment.objects.get(booking=self.booking)
        payload = mock_post.call_args.kwargs["json"]
        attributes = payload["data"]["attributes"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["payment_url"],
            "https://checkout.paymongo.com/test-session",
        )
        self.assertEqual(payment.amount, Decimal("140.00"))
        self.assertEqual(payment.method.code, "PAYMONGO")
        self.assertEqual(payment.payment_status, "Pending")
        self.assertEqual(payment.transaction_reference, "cs_test_123")
        self.assertIn(f"SB-BK-{self.booking.id}", attributes["description"])
        self.assertEqual(
            attributes["line_items"][0]["name"],
            f"StudyBuddy SB-BK-{self.booking.id}",
        )

    @patch("studybuddy.views.requests.post")
    def test_initiate_online_payment_accepts_paymongo_201_success(self, mock_post):
        mock_post.return_value = self.paymongo_response(201, self.success_payload("cs_test_201"))

        response = self.client.post(
            "/api/payments/initiate/",
            {"booking_id": self.booking.id},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["payment_url"],
            "https://checkout.paymongo.com/test-session",
        )
        self.assertEqual(
            Payment.objects.get(booking=self.booking).transaction_reference,
            "cs_test_201",
        )

    @patch("studybuddy.views.requests.post")
    def test_initiate_online_payment_returns_paymongo_validation_error(self, mock_post):
        mock_post.return_value = self.paymongo_response(
            400,
            {"errors": [{"code": "parameter_invalid", "detail": "Invalid payment method type."}]},
        )

        response = self.client.post(
            "/api/payments/initiate/",
            {"booking_id": self.booking.id},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"], "Invalid payment method type.")
        self.assertFalse(Payment.objects.filter(booking=self.booking).exists())

    @patch("studybuddy.views.requests.post")
    def test_initiate_online_payment_returns_paymongo_auth_error(self, mock_post):
        mock_post.return_value = self.paymongo_response(
            401,
            {"errors": [{"code": "secret_key_invalid", "detail": "Invalid API key."}]},
        )

        response = self.client.post(
            "/api/payments/initiate/",
            {"booking_id": self.booking.id},
            format="json",
        )

        self.assertEqual(response.status_code, 502)
        self.assertEqual(
            response.data["error"],
            "Payment provider authentication failed. Check the PayMongo secret key.",
        )
        self.assertFalse(Payment.objects.filter(booking=self.booking).exists())

    @patch("studybuddy.views.requests.post")
    def test_initiate_online_payment_requires_checkout_url_on_success(self, mock_post):
        mock_post.return_value = self.paymongo_response(
            200,
            {"data": {"id": "cs_missing_url", "attributes": {}}},
        )

        response = self.client.post(
            "/api/payments/initiate/",
            {"booking_id": self.booking.id},
            format="json",
        )

        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.data["error"], "Payment provider did not return a checkout URL.")
        self.assertFalse(Payment.objects.filter(booking=self.booking).exists())

    @patch("studybuddy.views.requests.get")
    def test_verify_online_payment_marks_paymongo_payment_paid(self, mock_get):
        payment = self.create_pending_paymongo_payment()
        mock_get.return_value = self.paymongo_response(200, self.retrieve_payload("paid"))

        response = self.client.post(f"/api/bookings/{self.booking.id}/verify-online-payment/")

        payment.refresh_from_db()
        self.booking.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["session"]["status"], "Awaiting Verification")
        self.assertEqual(payment.payment_status, "Paid")
        self.assertIsNotNone(payment.paid_at)
        self.assertEqual(self.booking.status, "Awaiting Payment Verification")
        self.assertTrue(self.booking.tutee_confirmed)

    @patch("studybuddy.views.requests.get")
    def test_verify_online_payment_updates_all_booking_request_slots(self, mock_get):
        second_booking = self.create_second_request_slot()
        self.create_pending_paymongo_payment()
        mock_get.return_value = self.paymongo_response(200, self.retrieve_payload("paid"))

        response = self.client.post(f"/api/bookings/{self.booking.id}/verify-online-payment/")

        self.booking.refresh_from_db()
        second_booking.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["session"]["status"], "Awaiting Verification")
        self.assertEqual(self.booking.status, "Awaiting Payment Verification")
        self.assertEqual(second_booking.status, "Awaiting Payment Verification")
        self.assertTrue(self.booking.tutee_confirmed)
        self.assertTrue(second_booking.tutee_confirmed)

    @patch("studybuddy.views.requests.get")
    @patch("studybuddy.views.requests.post")
    def test_verify_payment_returns_all_booking_request_slots(self, mock_post, mock_get):
        """Response must include all booking_request_id siblings, not just session_group siblings."""
        second_booking = self.create_second_request_slot()
        self.create_pending_paymongo_payment()

        mock_get.return_value = self.paymongo_response(200, self.retrieve_payload("paid"))

        response = self.client.post(
            f"/api/bookings/{self.booking.id}/verify-online-payment/",
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        # Both slots should be reflected in the response. With 2 x 30-min slots the
        # duration_hours must be 1.0; if the bug is present (get_session_group_bookings
        # is used and session_group_id is None) only one slot is included → 0.5.
        self.assertEqual(response.data["session"]["duration_hours"], 1.0)
        _ = second_booking  # referenced to avoid unused-variable warning

    def test_manual_payment_submission_updates_all_session_group_slots(self):
        second_booking = self.create_second_request_slot()
        method = PaymentMethod.objects.create(
            code="CASH",
            method_name="Cash",
            is_active=True,
        )

        response = self.client.post(
            f"/api/bookings/{self.booking.id}/submit-payment/",
            {"payment_method": method.method_id},
        )

        self.booking.refresh_from_db()
        second_booking.refresh_from_db()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(self.booking.status, "Awaiting Payment Verification")
        self.assertEqual(second_booking.status, "Awaiting Payment Verification")
        self.assertTrue(self.booking.tutee_confirmed)
        self.assertTrue(second_booking.tutee_confirmed)

    def test_tutor_completion_updates_all_session_group_slots(self):
        second_booking = self.create_second_request_slot()
        self.booking.status = "Awaiting Payment Verification"
        self.booking.tutee_confirmed = True
        self.booking.save(update_fields=["status", "tutee_confirmed"])
        second_booking.status = "Awaiting Payment Verification"
        second_booking.tutee_confirmed = True
        second_booking.save(update_fields=["status", "tutee_confirmed"])
        method = PaymentMethod.objects.create(
            code="CASH",
            method_name="Cash",
            is_active=True,
        )
        Payment.objects.create(
            booking=self.booking,
            amount=Decimal("280.00"),
            method=method,
            payment_status="Pending",
        )
        self.client.force_authenticate(user=self.tutor_user)

        response = self.client.post(f"/api/bookings/{self.booking.id}/tutor-confirm/")

        self.booking.refresh_from_db()
        second_booking.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.booking.status, "Completed")
        self.assertEqual(second_booking.status, "Completed")
        self.assertTrue(self.booking.tutor_confirmed)
        self.assertTrue(second_booking.tutor_confirmed)

    def test_tutor_completion_credits_wallet_for_paymongo_payment(self):
        self.booking.status = "Awaiting Payment Verification"
        self.booking.tutee_confirmed = True
        self.booking.save(update_fields=["status", "tutee_confirmed"])
        method = PaymentMethod.objects.create(
            code="PAYMONGO",
            method_name="Pay Online (GCash / Card)",
            is_active=True,
        )
        Payment.objects.create(
            booking=self.booking,
            amount=Decimal("280.00"),
            method=method,
            payment_status="Paid",
            transaction_reference="cs_test_wallet",
        )
        self.client.force_authenticate(user=self.tutor_user)

        response = self.client.post(f"/api/bookings/{self.booking.id}/tutor-confirm/")

        wallet = Wallet.objects.get(tutor=self.tutor)
        transaction = Transaction.objects.get(reference_id=f"BK-{self.booking.id}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(wallet.balance, Decimal("252.00"))
        self.assertEqual(transaction.transaction_type, "session_credit")
        self.assertEqual(transaction.amount, Decimal("252.00"))
        self.assertIn("Student: Payment Tutee", transaction.description)
        self.assertNotIn("Transaction ID", transaction.description)

    def test_wallet_transactions_include_paymongo_transaction_id(self):
        self.booking.status = "Awaiting Payment Verification"
        self.booking.tutee_confirmed = True
        self.booking.save(update_fields=["status", "tutee_confirmed"])
        method = PaymentMethod.objects.create(
            code="PAYMONGO",
            method_name="Pay Online (GCash / Card)",
            is_active=True,
        )
        Payment.objects.create(
            booking=self.booking,
            amount=Decimal("280.00"),
            method=method,
            payment_status="Paid",
            transaction_reference="cs_test_wallet",
        )
        self.client.force_authenticate(user=self.tutor_user)
        self.client.post(f"/api/bookings/{self.booking.id}/tutor-confirm/")
        Transaction.objects.filter(reference_id=f"BK-{self.booking.id}").update(
            description=(
                "Session Credit for 2026-04-12 (Less 10% Platform Fee) "
                "- Transaction ID: cs_test_wallet"
            )
        )

        response = self.client.get("/api/wallet/transactions/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["reference_id"], f"BK-{self.booking.id}")
        self.assertEqual(response.data[0]["payment_transaction_id"], "cs_test_wallet")
        self.assertEqual(response.data[0]["student_name"], "Payment Tutee")
        self.assertIn("Student: Payment Tutee", response.data[0]["description"])
        self.assertNotIn("Transaction ID", response.data[0]["description"])

    def test_tutor_completion_does_not_duplicate_wallet_credit(self):
        self.booking.status = "Awaiting Payment Verification"
        self.booking.tutee_confirmed = True
        self.booking.save(update_fields=["status", "tutee_confirmed"])
        method = PaymentMethod.objects.create(
            code="PAYMONGO",
            method_name="Pay Online (GCash / Card)",
            is_active=True,
        )
        Payment.objects.create(
            booking=self.booking,
            amount=Decimal("280.00"),
            method=method,
            payment_status="Paid",
            transaction_reference="cs_test_wallet",
        )
        self.client.force_authenticate(user=self.tutor_user)

        first_response = self.client.post(f"/api/bookings/{self.booking.id}/tutor-confirm/")
        second_response = self.client.post(f"/api/bookings/{self.booking.id}/tutor-confirm/")

        wallet = Wallet.objects.get(tutor=self.tutor)

        self.assertEqual(first_response.status_code, 200)
        self.assertEqual(second_response.status_code, 400)
        self.assertEqual(wallet.balance, Decimal("252.00"))
        self.assertEqual(Transaction.objects.filter(reference_id=f"BK-{self.booking.id}").count(), 1)

    @patch("studybuddy.views.requests.get")
    def test_verify_online_payment_rejects_incomplete_checkout(self, mock_get):
        payment = self.create_pending_paymongo_payment()
        mock_get.return_value = self.paymongo_response(200, self.retrieve_payload("active"))

        response = self.client.post(f"/api/bookings/{self.booking.id}/verify-online-payment/")

        payment.refresh_from_db()
        self.booking.refresh_from_db()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"], "Online payment has not been completed yet.")
        self.assertEqual(payment.payment_status, "Pending")
        self.assertEqual(self.booking.status, "Confirmed")
        self.assertFalse(self.booking.tutee_confirmed)

    def test_verify_online_payment_requires_paymongo_payment(self):
        response = self.client.post(f"/api/bookings/{self.booking.id}/verify-online-payment/")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"], "No PayMongo checkout is pending for this session.")


class PaymentMethodTests(APITestCase):
    def test_payment_methods_hides_legacy_online_methods_when_paymongo_exists(self):
        PaymentMethod.objects.all().delete()

        PaymentMethod.objects.create(
            code="CASH",
            method_name="Cash",
            is_active=True,
        )
        PaymentMethod.objects.create(
            code="ONLINE",
            method_name="Online Payment",
            is_active=True,
        )
        PaymentMethod.objects.create(
            code="online",
            method_name="Online Payment",
            is_active=True,
        )
        PaymentMethod.objects.create(
            code="PAYMONGO",
            method_name="Pay Online (GCash / Card)",
            is_active=True,
        )

        response = self.client.get("/api/payment-methods/")
        codes = [method["code"] for method in response.data]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(codes, ["CASH", "PAYMONGO"])


@override_settings(
    PAYMONGO_WALLET_ID="wallet_test",
    PAYMONGO_CASHOUT_CALLBACK_URL="https://api.test/api/wallet/paymongo/callback/",
    CASHOUT_PROVIDER_FEE_PHP="10",
    CASHOUT_MIN_PHP="500",
)
class TutorCashOutTests(APITestCase):
    def setUp(self):
        self.tutor_user = User.objects.create_user(
            username="cashout-tutor",
            email="cashout-tutor@example.com",
            password="password",
        )
        self.tutor_profile = UserProfile.objects.create(
            user=self.tutor_user,
            fname="Cash",
            mname="",
            lname="Tutor",
            role="Tutor",
        )
        self.tutor = Tutor.objects.create(
            profile=self.tutor_profile,
            hourly_rate=Decimal("300.00"),
            can_online=True,
            can_f2f=True,
            teaching_level="SHS",
        )
        self.wallet = Wallet.objects.get(tutor=self.tutor)
        self.wallet.balance = Decimal("1000.00")
        self.wallet.save(update_fields=["balance"])
        self.client.force_authenticate(user=self.tutor_user)

    def create_account(self, provider="instapay", is_active=True):
        return TutorPayoutAccount.objects.create(
            tutor=self.tutor,
            destination_type="gcash",
            provider=provider,
            receiving_institution_id="inst_gcash",
            receiving_institution_name="GCash",
            receiving_institution_code="GCASH",
            account_number="09171234567",
            account_name="Cash Tutor",
            is_active=is_active,
        )

    def provider_result(self, status_value="pending", transaction_id="wt_test_123"):
        return {
            "id": transaction_id,
            "status": status_value,
            "provider": "paymongo",
            "reference_number": "PMO-123",
            "fee": Decimal("0.00"),
            "net_amount": Decimal("500.00"),
        }

    def callback_payload(self, status_value="failed", transaction_id="wt_test_123"):
        return {
            "data": {
                "id": transaction_id,
                "attributes": {
                    "status": status_value,
                    "provider": "paymongo",
                    "reference_number": "PMO-123",
                    "provider_error": {"detail": "Receiving account rejected the transfer."},
                },
            }
        }

    def test_create_list_and_deactivate_payout_destination(self):
        payload = {
            "destination_type": "gcash",
            "provider": "instapay",
            "receiving_institution_id": "inst_gcash",
            "receiving_institution_name": "GCash",
            "receiving_institution_code": "GCASH",
            "account_number": "09171234567",
            "account_name": "Cash Tutor",
        }

        create_response = self.client.post("/api/wallet/payout-destinations/", payload, format="json")
        list_response = self.client.get("/api/wallet/payout-destinations/")
        account_id = create_response.data["id"]
        patch_response = self.client.patch(
            f"/api/wallet/payout-destinations/{account_id}/",
            {"is_active": False},
            format="json",
        )

        self.assertEqual(create_response.status_code, 201)
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(len(list_response.data), 1)
        self.assertEqual(patch_response.status_code, 200)
        self.assertFalse(patch_response.data["is_active"])

    def test_cashout_rejects_invalid_amount_and_insufficient_balance(self):
        account = self.create_account()

        small_response = self.client.post(
            "/api/wallet/cash-outs/",
            {"amount": "499.99", "payout_account_id": account.id},
            format="json",
        )
        insufficient_response = self.client.post(
            "/api/wallet/cash-outs/",
            {"amount": "995.00", "payout_account_id": account.id},
            format="json",
        )

        self.assertEqual(small_response.status_code, 400)
        self.assertEqual(insufficient_response.status_code, 400)
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal("1000.00"))

    @patch("studybuddy.views.create_wallet_transaction")
    def test_cashout_deducts_amount_and_fee_and_stores_provider_data(self, mock_create):
        account = self.create_account()
        mock_create.return_value = self.provider_result()

        response = self.client.post(
            "/api/wallet/cash-outs/",
            {"amount": "500.00", "payout_account_id": account.id},
            format="json",
        )

        self.wallet.refresh_from_db()
        withdrawal = WithdrawalRequest.objects.get(id=response.data["id"])

        self.assertEqual(response.status_code, 201)
        self.assertEqual(self.wallet.balance, Decimal("490.00"))
        self.assertEqual(withdrawal.status, "pending")
        self.assertEqual(withdrawal.provider_wallet_transaction_id, "wt_test_123")
        self.assertEqual(withdrawal.provider_reference_number, "PMO-123")
        self.assertEqual(withdrawal.provider_fee, Decimal("10.00"))
        self.assertTrue(
            Transaction.objects.filter(
                wallet=self.wallet,
                transaction_type="withdrawal",
                amount=Decimal("-500.00"),
            ).exists()
        )
        self.assertTrue(
            Transaction.objects.filter(
                wallet=self.wallet,
                transaction_type="cashout_fee",
                amount=Decimal("-10.00"),
            ).exists()
        )

    @patch("studybuddy.views.create_wallet_transaction")
    def test_failed_callback_refunds_amount_and_fee_once(self, mock_create):
        account = self.create_account()
        mock_create.return_value = self.provider_result()

        create_response = self.client.post(
            "/api/wallet/cash-outs/",
            {"amount": "500.00", "payout_account_id": account.id},
            format="json",
        )
        self.client.force_authenticate(user=None)

        first_callback = self.client.post(
            "/api/wallet/paymongo/callback/",
            self.callback_payload(),
            format="json",
        )
        second_callback = self.client.post(
            "/api/wallet/paymongo/callback/",
            self.callback_payload(),
            format="json",
        )

        self.wallet.refresh_from_db()
        withdrawal = WithdrawalRequest.objects.get(id=create_response.data["id"])

        self.assertEqual(first_callback.status_code, 200)
        self.assertEqual(second_callback.status_code, 200)
        self.assertEqual(withdrawal.status, "failed")
        self.assertEqual(self.wallet.balance, Decimal("1000.00"))
        self.assertEqual(
            Transaction.objects.filter(
                wallet=self.wallet,
                transaction_type__in=["withdrawal_reversal", "cashout_fee_reversal"],
            ).count(),
            2,
        )


class TuteeProfileTests(APITestCase):
    def setUp(self):
        self.tutee_user = User.objects.create_user(
            username="tutee-test",
            email="tutee@example.com",
            password="password",
        )
        self.tutee_profile = UserProfile.objects.create(
            user=self.tutee_user,
            fname="Tutee",
            mname="",
            lname="Test",
            role="Tutee",
            year_level=11,
        )

    def test_get_profile_includes_avatar_url(self):
        self.client.force_authenticate(user=self.tutee_user)
        response = self.client.get('/api/tutee/profile/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('profile_picture_url', response.data)

    def test_upload_avatar_success(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        self.client.force_authenticate(user=self.tutee_user)
        image = SimpleUploadedFile("avatar.jpg", b"file_content", content_type="image/jpeg")
        response = self.client.post('/api/tutee/profile/avatar/', {'avatar': image}, format='multipart')
        self.assertEqual(response.status_code, 200)
        self.assertIn('profile_picture_url', response.data)

    def test_update_profile_can_clear_course_and_subjects(self):
        course = Course.objects.create(
            course_code="BSCS",
            course_name="BS Computer Science",
        )
        subject = Subjects.objects.create(
            subject_code="MATH101",
            subject_name="College Algebra",
            department="Math",
            category="College",
        )
        self.tutee_profile.course = course
        self.tutee_profile.save()
        preference = Preference.objects.create(user=self.tutee_profile)
        preference.subjects.add(subject)

        self.client.force_authenticate(user=self.tutee_user)
        response = self.client.put('/api/tutee/profile/update/', {
            "course": "",
            "year_level": 7,
            "subjects": [],
        }, format='json')

        self.assertEqual(response.status_code, 200)
        self.tutee_profile.refresh_from_db()
        preference.refresh_from_db()
        self.assertIsNone(self.tutee_profile.course)
        self.assertEqual(preference.subjects.count(), 0)


class TutorProfileTests(APITestCase):
    def setUp(self):
        self.tutor_user = User.objects.create_user(
            username="tutor-test",
            email="tutor@example.com",
            password="password",
        )
        self.tutor_profile = UserProfile.objects.create(
            user=self.tutor_user,
            fname="Tutor",
            mname="",
            lname="Test",
            role="Tutor",
            year_level=12,
        )
        self.tutor = Tutor.objects.create(
            profile=self.tutor_profile,
            hourly_rate=Decimal("250.00"),
            can_online=True,
            can_f2f=True,
            teaching_level="SHS",
        )

    def test_get_profile_includes_profile_picture_url(self):
        self.client.force_authenticate(user=self.tutor_user)
        response = self.client.get('/api/tutor/profile/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('profile_picture_url', response.data)

    def test_upload_avatar_success(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        self.client.force_authenticate(user=self.tutor_user)
        image = SimpleUploadedFile("avatar.jpg", b"fake_image_content", content_type="image/jpeg")
        response = self.client.post('/api/tutor/profile/avatar/', {'avatar': image}, format='multipart')
        self.assertEqual(response.status_code, 200)
        self.assertIn('profile_picture_url', response.data)

    def test_upload_avatar_rejects_non_image(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        self.client.force_authenticate(user=self.tutor_user)
        document = SimpleUploadedFile("avatar.pdf", b"fake_pdf_content", content_type="application/pdf")
        response = self.client.post('/api/tutor/profile/avatar/', {'avatar': document}, format='multipart')
        self.assertEqual(response.status_code, 400)

    def test_upload_avatar_rejects_missing_file(self):
        self.client.force_authenticate(user=self.tutor_user)
        response = self.client.post('/api/tutor/profile/avatar/', {}, format='multipart')
        self.assertEqual(response.status_code, 400)


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    FRONTEND_URL="https://studybuddy.example",
    LOGIN_OTP_TTL_SECONDS=600,
    LOGIN_OTP_MAX_ATTEMPTS=2,
    REST_FRAMEWORK={
        "DEFAULT_AUTHENTICATION_CLASSES": (
            "rest_framework_simplejwt.authentication.JWTAuthentication",
        ),
        "DEFAULT_THROTTLE_RATES": {
            "anon": "1000/min",
            "user": "1000/min",
            "login": "1000/min",
        },
    },
)
class EmailAuthTests(APITestCase):
    def setUp(self):
        cache.clear()
        mail.outbox = []
        self.institution = PartnerInstitution.objects.create(
            institution_name="Example University",
            school_email_domain="example.edu",
            is_active=True,
        )
        self.user = User.objects.create_user(
            username="student@example.edu",
            email="student@example.edu",
            password="password",
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            fname="Email",
            mname="",
            lname="Auth",
            role="Tutee",
            institution=self.institution,
        )

    def login(self):
        return self.client.post(
            "/api/login/",
            {"email": self.user.email, "password": "password"},
            format="json",
        )

    def latest_otp_code(self):
        match = re.search(r"\b(\d{6})\b", mail.outbox[-1].body)
        self.assertIsNotNone(match)
        return match.group(1)

    def reset_link_parts(self):
        match = re.search(r"/reset-password/([^/\s]+)/([^/\s]+)", mail.outbox[-1].body)
        self.assertIsNotNone(match)
        return match.group(1), match.group(2)

    def test_login_sends_otp_challenge_instead_of_tokens_then_verify_returns_tokens(self):
        response = self.login()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["requires_2fa"])
        self.assertIn("challenge_id", response.data)
        self.assertNotIn("access", response.data)
        self.assertEqual(len(mail.outbox), 1)

        challenge = EmailOTPChallenge.objects.get(
            challenge_id=response.data["challenge_id"]
        )
        self.assertEqual(challenge.user, self.user)

        verify_response = self.client.post(
            "/api/login/verify-otp/",
            {
                "challenge_id": response.data["challenge_id"],
                "code": self.latest_otp_code(),
            },
            format="json",
        )

        self.assertEqual(verify_response.status_code, 200)
        self.assertIn("access", verify_response.data)
        self.assertIn("refresh", verify_response.data)
        self.assertEqual(verify_response.data["email"], self.user.email)
        challenge.refresh_from_db()
        self.assertIsNotNone(challenge.consumed_at)

    @patch("studybuddy.views.generate_otp_code", side_effect=["123456", "654321"])
    def test_resend_replaces_otp_code_and_increments_resend_count(self, _generate_otp_code):
        login_response = self.login()
        old_code = self.latest_otp_code()

        resend_response = self.client.post(
            "/api/login/resend-otp/",
            {"challenge_id": login_response.data["challenge_id"]},
            format="json",
        )

        self.assertEqual(resend_response.status_code, 200)
        self.assertEqual(len(mail.outbox), 2)
        challenge = EmailOTPChallenge.objects.get(
            challenge_id=login_response.data["challenge_id"]
        )
        self.assertEqual(challenge.resend_count, 1)
        self.assertEqual(challenge.attempt_count, 0)

        old_code_response = self.client.post(
            "/api/login/verify-otp/",
            {
                "challenge_id": login_response.data["challenge_id"],
                "code": old_code,
            },
            format="json",
        )
        self.assertEqual(old_code_response.status_code, 400)

        new_code_response = self.client.post(
            "/api/login/verify-otp/",
            {
                "challenge_id": login_response.data["challenge_id"],
                "code": self.latest_otp_code(),
            },
            format="json",
        )
        self.assertEqual(new_code_response.status_code, 200)

    def test_otp_verify_locks_after_max_attempts(self):
        login_response = self.login()
        actual_code = self.latest_otp_code()
        first_wrong_code = "000000" if actual_code != "000000" else "000001"
        second_wrong_code = "111111" if actual_code != "111111" else "111112"

        first_response = self.client.post(
            "/api/login/verify-otp/",
            {
                "challenge_id": login_response.data["challenge_id"],
                "code": first_wrong_code,
            },
            format="json",
        )
        second_response = self.client.post(
            "/api/login/verify-otp/",
            {
                "challenge_id": login_response.data["challenge_id"],
                "code": second_wrong_code,
            },
            format="json",
        )

        self.assertEqual(first_response.status_code, 400)
        self.assertEqual(second_response.status_code, 429)
        challenge = EmailOTPChallenge.objects.get(
            challenge_id=login_response.data["challenge_id"]
        )
        self.assertEqual(challenge.attempt_count, 2)

    def test_password_reset_request_is_generic_and_confirm_resets_password(self):
        RefreshToken.for_user(self.user)
        self.assertTrue(OutstandingToken.objects.filter(user=self.user).exists())

        known_response = self.client.post(
            "/api/password-reset/request/",
            {"email": self.user.email},
            format="json",
        )
        unknown_response = self.client.post(
            "/api/password-reset/request/",
            {"email": "missing@example.edu"},
            format="json",
        )

        self.assertEqual(known_response.status_code, 200)
        self.assertEqual(unknown_response.status_code, 200)
        self.assertEqual(known_response.data, unknown_response.data)
        self.assertEqual(len(mail.outbox), 1)

        uid, token = self.reset_link_parts()
        confirm_response = self.client.post(
            "/api/password-reset/confirm/",
            {
                "uid": uid,
                "token": token,
                "password": "NewStudyBuddyPassword123!",
                "password_confirm": "NewStudyBuddyPassword123!",
            },
            format="json",
        )

        self.assertEqual(confirm_response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewStudyBuddyPassword123!"))
        self.assertEqual(
            BlacklistedToken.objects.filter(token__user=self.user).count(),
            OutstandingToken.objects.filter(user=self.user).count(),
        )
        self.assertEqual(len(mail.outbox), 2)

    def test_password_reset_confirm_validates_password_confirmation(self):
        self.client.post(
            "/api/password-reset/request/",
            {"email": self.user.email},
            format="json",
        )
        uid, token = self.reset_link_parts()

        response = self.client.post(
            "/api/password-reset/confirm/",
            {
                "uid": uid,
                "token": token,
                "password": "NewStudyBuddyPassword123!",
                "password_confirm": "DifferentStudyBuddyPassword123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.user.refresh_from_db()
        self.assertFalse(self.user.check_password("NewStudyBuddyPassword123!"))


class RecommenderNeighborReuseTests(APITestCase):
    def setUp(self):
        # student 1 is our target; students 2 and 3 are potential neighbors.
        self.ratings = {
            1: {10: 5, 11: 4},
            2: {10: 4, 11: 5, 12: 3},
            3: {10: 2, 11: 1, 12: 5},
        }

    def test_compute_cf_score_uses_supplied_neighbors(self):
        from studybuddy.recommender import CF

        neighbors = CF.top_k(self.ratings, 1)

        with patch.object(CF, "top_k") as mocked_top_k:
            score = CF.compute_cf_score(
                self.ratings, 1, 12, neighbors=neighbors
            )

        mocked_top_k.assert_not_called()
        self.assertIsNotNone(score)

    def test_compute_cf_score_matches_with_and_without_neighbors(self):
        from studybuddy.recommender import CF

        neighbors = CF.top_k(self.ratings, 1)

        without = CF.compute_cf_score(self.ratings, 1, 12)
        with_neighbors = CF.compute_cf_score(self.ratings, 1, 12, neighbors=neighbors)

        self.assertEqual(without, with_neighbors)

    def test_recommend_hybrid_computes_neighbors_once(self):
        from studybuddy.recommender import hybrid

        # three candidate tutors, but neighbors should be computed only once
        tutors = [Mock(profile_id=i, tutorsubjects_set=Mock()) for i in range(3)]
        for t in tutors:
            t.tutorsubjects_set.all.return_value = []

        student_profile = Mock(id=1, course=None, year_level=None)

        with patch.object(hybrid, "top_k", return_value=[]) as mocked_top_k, \
             patch.object(hybrid, "get_student_subject_codes", return_value=[]), \
             patch.object(hybrid, "compute_cbf_score", return_value=0.0), \
             patch.object(hybrid, "normalize_tutor_queryset", return_value=tutors):
            hybrid.recommend_tutors_hybrid(self.ratings, student_profile, None)

        self.assertEqual(mocked_top_k.call_count, 1)

    def test_recommend_hybrid_handles_student_with_no_ratings(self):
        from studybuddy.recommender import hybrid

        tutor = Mock(profile_id=99, tutorsubjects_set=Mock())
        tutor.tutorsubjects_set.all.return_value = []
        student_profile = Mock(id=4242, course=None, year_level=None)  # not in ratings

        with patch.object(hybrid, "get_student_subject_codes", return_value=[]), \
             patch.object(hybrid, "compute_cbf_score", return_value=0.5), \
             patch.object(hybrid, "normalize_tutor_queryset", return_value=[tutor]):
            results = hybrid.recommend_tutors_hybrid(self.ratings, student_profile, None)

        self.assertEqual(len(results), 1)  # did not raise


class DashboardRecommendationServiceTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.subject = Subjects.objects.create(
            subject_code="IT101",
            subject_name="Intro to IT",
            department="IT",
        )
        self.other_subject = Subjects.objects.create(
            subject_code="BIO101",
            subject_name="Biology",
            department="Science",
        )
        self.student_user = User.objects.create_user(
            username="dash-student", email="dash@example.com", password="password",
        )
        self.student = UserProfile.objects.create(
            user=self.student_user, fname="Dash", mname="", lname="Student",
            role="Tutee", year_level=11,
        )

    def _make_tutor(self, username, subject):
        user = User.objects.create_user(
            username=username, email=f"{username}@example.com", password="password",
        )
        profile = UserProfile.objects.create(
            user=user, fname=username.title(), mname="", lname="Tutor",
            role="Tutor", year_level=12,
        )
        tutor = Tutor.objects.create(
            profile=profile, hourly_rate=200, can_online=True, can_f2f=False,
            teaching_level="SHS",
        )
        TutorSubjects.objects.create(tutor=tutor, subject=subject, expertise_level=5)
        return tutor

    def _set_preferences(self, *subjects):
        pref, _ = Preference.objects.get_or_create(user=self.student)
        pref.subjects.set([s.subject_code for s in subjects])

    def test_returns_only_tutors_teaching_preference_subjects(self):
        from studybuddy.recommender.dashboard import get_dashboard_recommendations

        match = self._make_tutor("itmatch", self.subject)
        self._make_tutor("biomatch", self.other_subject)
        self._set_preferences(self.subject)

        data = get_dashboard_recommendations(self.student)

        ids = {row["id"] for row in data}
        self.assertEqual(ids, {match.profile.id})

    def test_response_shape_matches_widget_contract(self):
        from studybuddy.recommender.dashboard import get_dashboard_recommendations

        self._make_tutor("itmatch", self.subject)
        self._set_preferences(self.subject)

        row = get_dashboard_recommendations(self.student)[0]

        self.assertEqual(
            set(row.keys()), {"id", "name", "rating", "subjects", "hourlyRate"},
        )

    def test_cold_start_returns_fallback_when_no_preferences(self):
        from studybuddy.recommender.dashboard import get_dashboard_recommendations

        for index in range(7):
            self._make_tutor(f"anytutor{index}", self.subject)
        # no preferences set

        data = get_dashboard_recommendations(self.student)

        self.assertEqual(len(data), 5)

    def test_returns_top_five_from_hybrid_algorithm_order(self):
        from studybuddy.recommender import dashboard

        tutors = [self._make_tutor(f"itmatch{index}", self.subject) for index in range(7)]
        self._set_preferences(self.subject)

        ranked = [
            {"tutor": tutor, "score": 1 - (index / 10)}
            for index, tutor in enumerate(reversed(tutors))
        ]

        with patch.object(dashboard, "recommend_tutors_hybrid", return_value=ranked):
            data = dashboard.get_dashboard_recommendations(self.student)

        self.assertEqual(len(data), 5)
        self.assertEqual(
            [row["id"] for row in data],
            [recommendation["tutor"].profile.id for recommendation in ranked[:5]],
        )

    def test_cache_hit_is_defensively_limited_to_five(self):
        from studybuddy.recommender.dashboard import (
            dashboard_recs_cache_key,
            get_dashboard_recommendations,
        )

        cache.set(
            dashboard_recs_cache_key(self.student),
            [
                {
                    "id": index,
                    "name": f"Cached Tutor {index}",
                    "rating": 5,
                    "subjects": ["Intro to IT"],
                    "hourlyRate": 200,
                }
                for index in range(8)
            ],
        )

        data = get_dashboard_recommendations(self.student)

        self.assertEqual(len(data), 5)
        self.assertEqual([row["id"] for row in data], [0, 1, 2, 3, 4])

    def test_second_call_served_from_cache_without_recompute(self):
        from studybuddy.recommender import dashboard

        self._make_tutor("itmatch", self.subject)
        self._set_preferences(self.subject)

        dashboard.get_dashboard_recommendations(self.student)  # warms cache

        with patch.object(dashboard, "recommend_tutors_hybrid") as mocked:
            dashboard.get_dashboard_recommendations(self.student)

        mocked.assert_not_called()

    def test_degrades_gracefully_when_cache_read_fails(self):
        from studybuddy.recommender import dashboard

        match = self._make_tutor("itmatch", self.subject)
        self._set_preferences(self.subject)

        with patch.object(dashboard.cache, "get", side_effect=Exception("redis down")):
            data = dashboard.get_dashboard_recommendations(self.student)

        ids = {row["id"] for row in data}
        self.assertEqual(ids, {match.profile.id})


class StudentDashboardRecommendationTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.subject = Subjects.objects.create(
            subject_code="IT201", subject_name="Data Structures", department="IT",
        )
        self.other_subject = Subjects.objects.create(
            subject_code="HIST201", subject_name="History", department="Arts",
        )
        self.student_user = User.objects.create_user(
            username="dv-student", email="dv@example.com", password="password",
        )
        self.student = UserProfile.objects.create(
            user=self.student_user, fname="Dee", mname="", lname="Vee",
            role="Tutee", year_level=11,
        )
        self.client.force_authenticate(user=self.student_user)

    def _make_tutor(self, username, subject):
        user = User.objects.create_user(
            username=username, email=f"{username}@example.com", password="password",
        )
        profile = UserProfile.objects.create(
            user=user, fname=username.title(), mname="", lname="Tutor",
            role="Tutor", year_level=12,
        )
        tutor = Tutor.objects.create(
            profile=profile, hourly_rate=200, can_online=True, can_f2f=False,
            teaching_level="SHS",
        )
        TutorSubjects.objects.create(tutor=tutor, subject=subject, expertise_level=5)
        return tutor

    def test_dashboard_recommends_subject_matched_tutors(self):
        matches = [self._make_tutor(f"itone{index}", self.subject) for index in range(7)]
        self._make_tutor("histone", self.other_subject)
        pref, _ = Preference.objects.get_or_create(user=self.student)
        pref.subjects.set([self.subject.subject_code])

        response = self.client.get("/api/dashboard/")

        self.assertEqual(response.status_code, 200)
        ids = {row["id"] for row in response.data["recommendations"]}
        self.assertEqual(len(response.data["recommendations"]), 5)
        self.assertTrue(ids.issubset({tutor.profile.id for tutor in matches}))
        self.assertEqual(
            set(response.data["recommendations"][0].keys()),
            {"id", "name", "rating", "subjects", "hourlyRate"},
        )

    def test_saving_preferences_busts_dashboard_cache(self):
        from studybuddy.recommender.dashboard import dashboard_recs_cache_key

        self._make_tutor("itone", self.subject)
        pref, _ = Preference.objects.get_or_create(user=self.student)
        pref.subjects.set([self.subject.subject_code])

        # warm the cache
        self.client.get("/api/dashboard/")
        self.assertIsNotNone(cache.get(dashboard_recs_cache_key(self.student)))

        # changing preferences must clear it
        response = self.client.post(
            "/api/preferences/", {"subjects": [self.subject.subject_code]},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(cache.get(dashboard_recs_cache_key(self.student)))

    def test_submitting_rating_bumps_dashboard_cache_version(self):
        from studybuddy.recommender.dashboard import dashboard_recs_cache_key

        tutor = self._make_tutor("ratedtutor", self.subject)
        availability = TutorAvailability.objects.create(
            tutor=tutor,
            day="Mon",
            time_slot=time(9, 0),
            is_active=True,
        )
        booking = Booking.objects.create(
            student=self.student,
            tutor=tutor,
            availability=availability,
            session_date=date(2026, 6, 1),
            session_mode="Online",
            booking_request_id=uuid4(),
            status="Completed",
        )

        old_key = dashboard_recs_cache_key(self.student)

        response = self.client.post(
            f"/api/bookings/{booking.id}/rating/",
            {"rating_score": 5},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertNotEqual(old_key, dashboard_recs_cache_key(self.student))

    def test_tutor_subject_change_bumps_dashboard_cache_version(self):
        from studybuddy.recommender.dashboard import dashboard_recs_cache_key

        tutor = self._make_tutor("subjecttutor", self.subject)
        new_subject = Subjects.objects.create(
            subject_code="IT301",
            subject_name="Algorithms",
            department="IT",
        )

        old_key = dashboard_recs_cache_key(self.student)
        self.client.force_authenticate(user=tutor.profile.user)

        response = self.client.post(
            "/api/tutor/subjects/add/",
            {"subject_code": new_subject.subject_code},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(old_key, dashboard_recs_cache_key(self.student))

    def test_tutor_profile_change_bumps_dashboard_cache_version(self):
        from studybuddy.recommender.dashboard import dashboard_recs_cache_key

        tutor = self._make_tutor("profiletutor", self.subject)

        old_key = dashboard_recs_cache_key(self.student)
        self.client.force_authenticate(user=tutor.profile.user)

        response = self.client.put(
            "/api/tutor/update/",
            {
                "hourly_rate": 250,
                "teaching_level": "SHS",
                "can_online": True,
                "can_f2f": False,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(old_key, dashboard_recs_cache_key(self.student))


class DashboardLoadPerformanceTests(APITestCase):
    """Phase 1 verification: the dedicated recommendations endpoint plus
    query-count regression guards for the N+1 fixes in list_bookings and
    student_dashboard. The N+1 guard asserts the query count is constant as the
    number of bookings grows — if a per-row query crept back in, doubling the
    bookings would raise the count."""

    def setUp(self):
        cache.clear()
        self.course = Course.objects.create(
            course_code="BSIT", course_name="BS Information Technology",
        )
        self.subject = Subjects.objects.create(
            subject_code="PERF101", subject_name="Performance", department="IT",
        )
        self.student_user = User.objects.create_user(
            username="perf-student", email="perf-student@example.com", password="password",
        )
        self.student = UserProfile.objects.create(
            user=self.student_user, fname="Perf", mname="", lname="Student",
            role="Tutee", year_level=11, course=self.course,
        )
        self.tutor_user = User.objects.create_user(
            username="perf-tutor", email="perf-tutor@example.com", password="password",
        )
        self.tutor_profile = UserProfile.objects.create(
            user=self.tutor_user, fname="Perf", mname="", lname="Tutor",
            role="Tutor", year_level=12, course=self.course,
        )
        self.tutor = Tutor.objects.create(
            profile=self.tutor_profile, hourly_rate=200, can_online=True,
            can_f2f=True, teaching_level="SHS",
        )
        TutorSubjects.objects.create(
            tutor=self.tutor, subject=self.subject, expertise_level=5,
        )
        self.availability = TutorAvailability.objects.create(
            tutor=self.tutor, day="Mon", time_slot=time(14, 0), is_active=True,
        )
        self.client.force_authenticate(user=self.student_user)

    def _make_completed(self, count, start_day):
        """Create `count` Completed bookings on distinct dates, each rated.

        Distinct session_dates avoid the (availability, session_date) unique
        constraint. Rating rows are created directly so they exercise the
        select_related('rating') path without bumping the recs cache version.
        """
        from datetime import timedelta
        base = date(2026, 1, 1) + timedelta(days=start_day)
        for offset in range(count):
            booking = Booking.objects.create(
                student=self.student, tutor=self.tutor, availability=self.availability,
                session_date=base + timedelta(days=offset),
                session_mode="Online", status="Completed",
            )
            Rating.objects.create(
                booking=booking, student=self.student, tutor=self.tutor, rating_score=5,
            )

    def _count_queries(self, url):
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        return len(ctx)

    def test_recommendations_endpoint_returns_only_recommendations(self):
        response = self.client.get("/api/recommendations/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("recommendations", response.data)
        self.assertNotIn("upcoming", response.data)
        self.assertNotIn("completed", response.data)

    def test_recommendations_endpoint_requires_auth(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/recommendations/")
        self.assertIn(response.status_code, (401, 403))

    def test_student_dashboard_has_no_n_plus_one(self):
        self._make_completed(3, start_day=0)
        self.client.get("/api/dashboard/")  # warm the (cached) recommendations
        first = self._count_queries("/api/dashboard/")
        self._make_completed(3, start_day=400)
        second = self._count_queries("/api/dashboard/")
        self.assertEqual(
            first, second,
            f"student_dashboard query count grew with booking count "
            f"({first} -> {second}); a per-row (N+1) query likely regressed.",
        )

    def test_list_bookings_has_no_n_plus_one(self):
        self._make_completed(3, start_day=0)
        first = self._count_queries("/api/bookings/")
        self._make_completed(3, start_day=400)
        second = self._count_queries("/api/bookings/")
        self.assertEqual(
            first, second,
            f"list_bookings query count grew with booking count "
            f"({first} -> {second}); a per-row (N+1) query likely regressed.",
        )
