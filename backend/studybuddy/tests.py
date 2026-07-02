import re
from io import StringIO
from datetime import date, time, timedelta
from decimal import Decimal
from unittest.mock import Mock, patch
from uuid import uuid4

from django.core.cache import cache
from django.core import mail
from django.core.management import call_command
from django.contrib.auth.models import User
from django.db import connection
from django.test import override_settings
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken

from .chat.services import get_current_booking_context, get_current_booking_contexts, get_partner_context
from .paymongo_money_movement import PayMongoCashOutError
from .views import credit_tutor_wallet, dev_add_wallet_funds, dev_remove_wallet_funds
from .models import (
    AdminAccountRequest,
    Booking,
    Course,
    EmailOTPChallenge,
    InstitutionRequest,
    PartnerInstitution,
    Payment,
    PaymentMethod,
    Rating,
    Subjects,
    SupportTicket,
    SessionCheckIn,
    Tutor,
    TutorAvailability,
    TutorAvailabilityOverride,
    TutorSubjects,
    UserProfile,
    Transaction,
    TutorApplication,
    TutorDocumentRenewalReview,
    TuteeApplication,
    TuteeDocumentRenewalReview,
    PlatformActivity,
    Wallet,
    WalletTopUp,
    WithdrawalRequest,
    Preference,
)
from .chat.models import ChatRoom, Message


class SuperAdminRedesignApiTests(APITestCase):
    def setUp(self):
        self.institution = PartnerInstitution.objects.create(
            institution_name="Central Philippine University",
            school_email_domain="cpu.edu.ph",
            is_active=True,
            contact_person="Registrar",
        )
        self.inactive_institution = PartnerInstitution.objects.create(
            institution_name="Dormant College",
            school_email_domain="dormant.edu.ph",
            is_active=False,
        )
        self.super_user = User.objects.create_user(
            username="superadmin",
            email="superadmin@studybuddy.test",
            password="password",
        )
        self.super_profile = UserProfile.objects.create(
            user=self.super_user,
            fname="Super",
            mname="",
            lname="Admin",
            role="SuperAdmin",
            profile_completed=True,
            is_domain_exempt=True,
        )
        self.admin_user = User.objects.create_user(
            username="admin",
            email="admin@cpu.edu.ph",
            password="password",
        )
        self.admin_profile = UserProfile.objects.create(
            user=self.admin_user,
            fname="Inst",
            mname="",
            lname="Admin",
            role="Admin",
            institution=self.institution,
            profile_completed=True,
        )
        self.target_user = User.objects.create_user(
            username="target",
            email="target@cpu.edu.ph",
            password="password",
        )
        self.target_profile = UserProfile.objects.create(
            user=self.target_user,
            fname="Target",
            mname="",
            lname="User",
            role="Tutee",
            institution=self.institution,
            profile_completed=True,
        )
        self.domain_user = User.objects.create_user(
            username="external",
            email="external@gmail.com",
            password="password",
        )
        self.domain_profile = UserProfile.objects.create(
            user=self.domain_user,
            fname="External",
            mname="",
            lname="Learner",
            role="Tutee",
            profile_completed=True,
            is_domain_exempt=False,
        )
        self.client.force_authenticate(user=self.super_user)

    def test_pending_actions_aggregates_superadmin_only_items(self):
        InstitutionRequest.objects.create(
            institution_name="West Visayas State University",
            school_email_domain="wvsu.edu.ph",
            contact_person="WVSU Admin",
            contact_email="admin@wvsu.edu.ph",
        )
        AdminAccountRequest.objects.create(
            requesting_admin=self.admin_profile,
            institution=self.institution,
            note="Promote target user.",
        )

        response = self.client.get("/api/admin/pending-actions/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 4)
        self.assertEqual(
            {
                item["type"]
                for item in response.data["items"]
            },
            {
                "institution_request",
                "institution_activation",
                "admin_account_request",
                "domain_exemption",
            },
        )

    def test_institution_request_approval_creates_active_partner_institution(self):
        request_obj = InstitutionRequest.objects.create(
            institution_name="West Visayas State University",
            school_email_domain="wvsu.edu.ph",
            contact_person="WVSU Admin",
            contact_email="admin@wvsu.edu.ph",
        )

        response = self.client.patch(
            f"/api/admin/institution-requests/{request_obj.id}/",
            {"action": "approve"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "approved")
        self.assertTrue(
            PartnerInstitution.objects.filter(
                school_email_domain="wvsu.edu.ph",
                is_active=True,
            ).exists()
        )

    def test_superadmin_can_patch_role_institution_and_domain_exemption(self):
        response = self.client.patch(
            f"/api/admin/users/{self.target_profile.id}/",
            {
                "role": "Admin",
                "institution": self.inactive_institution.id,
                "is_domain_exempt": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.target_profile.refresh_from_db()
        self.assertEqual(self.target_profile.role, "Admin")
        self.assertEqual(self.target_profile.institution, self.inactive_institution)
        self.assertTrue(self.target_profile.is_domain_exempt)

    def test_admin_account_request_approval_promotes_target_user(self):
        request_obj = AdminAccountRequest.objects.create(
            requesting_admin=self.admin_profile,
            institution=self.institution,
            note="Promote target user.",
        )

        response = self.client.patch(
            f"/api/admin/admin-account-requests/{request_obj.id}/",
            {"action": "approve", "target_user_id": self.target_profile.id},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.target_profile.refresh_from_db()
        self.assertEqual(self.target_profile.role, "Admin")
        self.assertEqual(self.target_profile.institution, self.institution)

    def test_analytics_includes_completion_subject_popularity_and_csv(self):
        course = Course.objects.create(course_code="MATH", course_name="Mathematics")
        subject = Subjects.objects.create(
            subject_code="ALG101",
            subject_name="College Algebra",
            department="Math",
        )
        tutor_user = User.objects.create_user(
            username="tutor",
            email="tutor@cpu.edu.ph",
            password="password",
        )
        tutor_profile = UserProfile.objects.create(
            user=tutor_user,
            fname="Tutor",
            mname="",
            lname="One",
            role="Tutor",
            institution=self.institution,
            course=course,
            profile_completed=True,
        )
        tutor = Tutor.objects.create(
            profile=tutor_profile,
            hourly_rate=Decimal("500.00"),
            total_sessions=1,
        )
        TutorSubjects.objects.create(tutor=tutor, subject=subject, expertise_level=5)
        availability = TutorAvailability.objects.create(
            tutor=tutor,
            day="Mon",
            time_slot=time(9, 0),
            is_active=True,
        )
        booking = Booking.objects.create(
            student=self.target_profile,
            tutor=tutor,
            availability=availability,
            session_date=date.today(),
            session_mode="Online",
            status="Completed",
        )
        payment_method = PaymentMethod.objects.create(code="online", method_name="Online Payment")
        Payment.objects.create(
            booking=booking,
            method=payment_method,
            amount=Decimal("500.00"),
            payment_status="Paid",
        )

        response = self.client.get("/api/admin/analytics/?period=7d")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["completion_rate"], 100.0)
        self.assertEqual(response.data["subject_popularity"][0]["subject_name"], "College Algebra")
        self.assertEqual(response.data["top_tutors"][0]["earnings"], 450.0)

        export_response = self.client.get("/api/admin/analytics/export/?period=7d")
        self.assertEqual(export_response.status_code, 200)
        self.assertEqual(export_response["Content-Type"], "text/csv")
        self.assertIn("date,institution,tutors,tutees,sessions,completion_rate,gross_revenue,commissions", export_response.content.decode())


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

    def test_falls_back_to_subject_matches_when_exact_availability_is_empty(self):
        matching = self.create_tutor("fallback")
        wrong_subject = self.create_tutor("wrongsubject", subject=self.other_subject)
        f2f_only = self.create_tutor("f2ffallback", can_online=False, can_f2f=True)
        expensive = self.create_tutor("fallbackexpensive", hourly_rate=500)

        response = self.recommend()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.response_ids(response), {matching.profile_id})

    def test_fallback_excludes_known_booking_conflicts(self):
        fallback = self.create_tutor("fallbacksafe")
        booked = self.create_tutor("fallbackbooked")
        booked_slots = self.add_slots(booked, [time(14, 0), time(14, 30)])
        Booking.objects.create(
            student=self.student_profile,
            tutor=booked,
            availability=booked_slots[0],
            session_date=self.search_date,
            session_mode="Online",
            status="Confirmed",
        )

        response = self.recommend()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.response_ids(response), {fallback.profile_id})

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
        from datetime import date, timedelta
        room = ChatRoom.objects.create(tutee=self.tutee_profile, tutor=self.tutor_profile)
        self.make_booking('Confirmed', session_date=date.today() + timedelta(days=1))
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
        from datetime import date, timedelta
        room = ChatRoom.objects.create(tutee=self.tutee_profile, tutor=self.tutor_profile)
        self.make_booking('Awaiting Payment Verification', session_date=date.today() + timedelta(days=1))
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

    def test_partner_context_skipped_for_support_rooms(self):
        room = ChatRoom.objects.create(
            tutee=self.tutee_profile,
            tutor=None,
            room_type='support',
        )
        self.client.force_authenticate(user=self.tutee_user)

        response = self.client.get(f"/api/chat/rooms/{room.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.data['partner_context'])

    def test_ticket_context_exposes_subject_category_and_status(self):
        room = ChatRoom.objects.create(
            tutee=self.tutee_profile,
            tutor=None,
            room_type='support',
        )
        SupportTicket.objects.create(
            user=self.tutee_profile,
            chatroom=room,
            category='Technical',
            subject='Cannot join session',
            description='Video call will not load.',
            status='Open',
        )
        self.client.force_authenticate(user=self.tutee_user)

        response = self.client.get(f"/api/chat/rooms/{room.id}/")

        self.assertEqual(response.status_code, 200)
        ticket_context = response.data['ticket_context']
        self.assertEqual(ticket_context['subject'], 'Cannot join session')
        self.assertEqual(ticket_context['category'], 'Technical Problem')
        self.assertEqual(ticket_context['status'], 'Open')
        self.assertIsNotNone(ticket_context['created_at'])
        self.assertIsNone(ticket_context['assigned_agent_name'])

    def test_support_room_read_endpoint_handles_unassigned_ticket_broadcast(self):
        room = ChatRoom.objects.create(
            tutee=self.tutee_profile,
            tutor=None,
            room_type='support',
        )
        SupportTicket.objects.create(
            user=self.tutee_profile,
            chatroom=room,
            category='Dispute',
            subject='Need help with tutor',
            description='The conversation needs moderation.',
            status='Open',
        )
        message = Message.objects.create(
            room=room,
            sender=None,
            content='Ticket created.',
        )
        self.client.force_authenticate(user=self.tutee_user)

        response = self.client.post(f"/api/chat/rooms/{room.id}/read/")

        message.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(message.is_read)
        self.assertIsNotNone(message.read_at)

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
    CASHOUT_MIN_PHP="50",
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

    def destination_fields(self, **overrides):
        fields = {
            "destination_type": "gcash",
            "receiving_institution_id": "inst_gcash",
            "receiving_institution_name": "GCash",
            "receiving_institution_code": "GCASH",
            "account_number": "09171234567",
            "account_name": "Cash Tutor",
        }
        fields.update(overrides)
        return fields

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

    def test_cashout_rejects_invalid_amount_and_insufficient_balance(self):
        destination = self.destination_fields()

        small_response = self.client.post(
            "/api/wallet/cash-outs/",
            {"amount": "49.99", **destination},
            format="json",
        )
        insufficient_response = self.client.post(
            "/api/wallet/cash-outs/",
            {"amount": "995.00", **destination},
            format="json",
        )

        self.assertEqual(small_response.status_code, 400)
        self.assertEqual(insufficient_response.status_code, 400)
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal("1000.00"))

    @patch("studybuddy.views.create_wallet_transaction")
    def test_cashout_deducts_amount_and_fee_and_stores_provider_data(self, mock_create):
        destination = self.destination_fields()
        mock_create.return_value = self.provider_result()

        response = self.client.post(
            "/api/wallet/cash-outs/",
            {"amount": "500.00", **destination},
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
        destination = self.destination_fields()
        mock_create.return_value = self.provider_result()

        create_response = self.client.post(
            "/api/wallet/cash-outs/",
            {"amount": "500.00", **destination},
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

    @patch("studybuddy.views.create_wallet_transaction")
    def test_cashout_with_inline_destination_fields_succeeds(self, mock_create):
        destination = self.destination_fields()
        mock_create.return_value = self.provider_result()

        response = self.client.post(
            "/api/wallet/cash-outs/",
            {"amount": "500.00", "note": "Rent money", **destination},
            format="json",
        )

        self.wallet.refresh_from_db()
        withdrawal = WithdrawalRequest.objects.get(id=response.data["id"])

        self.assertIn(response.status_code, (200, 201))
        self.assertEqual(self.wallet.balance, Decimal("490.00"))
        self.assertEqual(withdrawal.method, destination["destination_type"])
        self.assertEqual(withdrawal.account_number, destination["account_number"])
        self.assertEqual(withdrawal.account_name, destination["account_name"])
        self.assertEqual(withdrawal.note, "Rent money")

    @patch("studybuddy.views.create_wallet_transaction")
    def test_recent_cash_outs_returns_last_four_most_recent_first(self, mock_create):
        mock_create.return_value = self.provider_result()
        destination = self.destination_fields()
        self.wallet.balance = Decimal("10000.00")
        self.wallet.save(update_fields=["balance"])
        statuses = ["pending", "processed", "rejected", "failed", "flagged", "processed"]

        created_ids = []
        for status_value in statuses:
            response = self.client.post(
                "/api/wallet/cash-outs/",
                {"amount": "500.00", **destination},
                format="json",
            )
            withdrawal = WithdrawalRequest.objects.get(id=response.data["id"])
            withdrawal.status = status_value
            withdrawal.save(update_fields=["status"])
            created_ids.append(withdrawal.id)

        response = self.client.get("/api/wallet/cash-outs/recent/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 4)
        self.assertEqual(
            [item["id"] for item in response.data],
            list(reversed(created_ids[-4:])),
        )

    @patch("studybuddy.views.create_wallet_transaction")
    def test_cashout_new_destination_requires_confirmation(self, mock_create):
        mock_create.return_value = self.provider_result()
        self.wallet.balance = Decimal("2000.00")
        self.wallet.save(update_fields=["balance"])
        known_destination = self.destination_fields()

        self.client.post(
            "/api/wallet/cash-outs/",
            {"amount": "500.00", **known_destination},
            format="json",
        )

        different_destination = self.destination_fields(
            destination_type="bank",
            receiving_institution_id="inst_bdo",
            receiving_institution_name="BDO",
            receiving_institution_code="BDO",
            account_number="0011223344",
            account_name="Cash Tutor",
            bank_name="BDO",
        )

        rejected_response = self.client.post(
            "/api/wallet/cash-outs/",
            {"amount": "500.00", **different_destination},
            format="json",
        )

        self.assertEqual(rejected_response.status_code, 409)
        self.assertEqual(
            rejected_response.data["error"], "new_destination_confirmation_required"
        )
        self.assertEqual(WithdrawalRequest.objects.filter(tutor=self.tutor).count(), 1)

        confirmed_response = self.client.post(
            "/api/wallet/cash-outs/",
            {
                "amount": "500.00",
                "confirm_new_destination": True,
                **different_destination,
            },
            format="json",
        )

        self.assertIn(confirmed_response.status_code, (200, 201))
        self.assertEqual(WithdrawalRequest.objects.filter(tutor=self.tutor).count(), 2)

    @patch("studybuddy.views.create_wallet_transaction")
    def test_cashout_matching_recent_destination_skips_confirmation(self, mock_create):
        mock_create.return_value = self.provider_result()
        destination = self.destination_fields()

        self.client.post(
            "/api/wallet/cash-outs/",
            {"amount": "500.00", **destination},
            format="json",
        )
        self.wallet.balance = Decimal("1000.00")
        self.wallet.save(update_fields=["balance"])

        response = self.client.post(
            "/api/wallet/cash-outs/",
            {"amount": "500.00", **destination},
            format="json",
        )

        self.assertIn(response.status_code, (200, 201))

    @patch("studybuddy.views.create_wallet_transaction")
    def test_cashout_first_time_destination_skips_confirmation_when_no_history(self, mock_create):
        mock_create.return_value = self.provider_result()
        destination = self.destination_fields()
        self.assertFalse(WithdrawalRequest.objects.filter(tutor=self.tutor).exists())

        response = self.client.post(
            "/api/wallet/cash-outs/",
            {"amount": "500.00", **destination},
            format="json",
        )

        self.assertIn(response.status_code, (200, 201))

    @override_settings(PAYMONGO_WALLET_ID="", PAYMONGO_CASHOUT_MOCK=True)
    @patch("studybuddy.paymongo_money_movement.requests.post")
    def test_cashout_mock_mode_succeeds_without_wallet_id_or_http_call(self, mock_post):
        destination = self.destination_fields()

        response = self.client.post(
            "/api/wallet/cash-outs/",
            {"amount": "500.00", **destination},
            format="json",
        )

        withdrawal = WithdrawalRequest.objects.get(id=response.data["id"])

        self.assertEqual(response.status_code, 201)
        self.assertEqual(withdrawal.status, "processed")
        self.assertEqual(withdrawal.provider_wallet_transaction_id, f"mock_wtx_{withdrawal.id}")
        mock_post.assert_not_called()


@override_settings(
    PAYMONGO_WALLET_ID="wallet_test",
    PAYMONGO_CASHOUT_CALLBACK_URL="https://api.test/api/wallet/paymongo/callback/",
    CASHOUT_PROVIDER_FEE_PHP="10",
    CASHOUT_MIN_PHP="50",
)
class WalletCashOutEdgeCaseTests(APITestCase):
    def setUp(self):
        self.tutor_user = User.objects.create_user(
            username="cashout-edge-tutor",
            email="cashout-edge-tutor@example.com",
            password="password",
        )
        self.tutor_profile = UserProfile.objects.create(
            user=self.tutor_user,
            fname="Edge",
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

    def destination_fields(self, **overrides):
        fields = {
            "destination_type": "gcash",
            "receiving_institution_id": "inst_gcash",
            "receiving_institution_name": "GCash",
            "receiving_institution_code": "GCASH",
            "account_number": "09171234567",
            "account_name": "Edge Tutor",
        }
        fields.update(overrides)
        return fields

    def provider_result(self, transaction_id="wt_test_edge"):
        return {
            "id": transaction_id,
            "status": "pending",
            "provider": "paymongo",
            "reference_number": "PMO-EDGE",
            "fee": Decimal("0.00"),
            "net_amount": Decimal("0.00"),
        }

    @patch("studybuddy.views.create_wallet_transaction")
    def test_cashout_same_destination_works_across_different_amounts(self, mock_create):
        self.wallet.balance = Decimal("100000.00")
        self.wallet.save(update_fields=["balance"])
        destination = self.destination_fields()
        mock_create.return_value = self.provider_result()

        first_response = self.client.post(
            "/api/wallet/cash-outs/",
            {"amount": "600.00", **destination},
            format="json",
        )
        second_response = self.client.post(
            "/api/wallet/cash-outs/",
            {"amount": "50000.00", **destination},
            format="json",
        )

        self.assertEqual(first_response.status_code, 201)
        self.assertEqual(second_response.status_code, 201)
        self.assertEqual(
            WithdrawalRequest.objects.filter(
                tutor=self.tutor, account_number=destination["account_number"]
            ).count(),
            2,
        )

    @patch("studybuddy.views.create_wallet_transaction")
    def test_cashout_allows_exact_cap_amount(self, mock_create):
        self.wallet.balance = Decimal("100000.00")
        self.wallet.save(update_fields=["balance"])
        destination = self.destination_fields()
        mock_create.return_value = self.provider_result()

        response = self.client.post(
            "/api/wallet/cash-outs/",
            {"amount": "50000.00", **destination},
            format="json",
        )

        self.assertEqual(response.status_code, 201)

    def test_cashout_rejects_amount_above_cap(self):
        self.wallet.balance = Decimal("100000.00")
        self.wallet.save(update_fields=["balance"])
        destination = self.destination_fields()

        response = self.client.post(
            "/api/wallet/cash-outs/",
            {"amount": "50000.01", **destination},
            format="json",
        )

        self.wallet.refresh_from_db()
        self.assertEqual(response.status_code, 400)
        self.assertIn("Maximum cash-out", response.data["error"])
        self.assertEqual(self.wallet.balance, Decimal("100000.00"))
        self.assertFalse(WithdrawalRequest.objects.filter(tutor=self.tutor).exists())

    def test_cashout_rejects_missing_destination_type(self):
        destination = self.destination_fields()
        destination.pop("destination_type")

        response = self.client.post(
            "/api/wallet/cash-outs/",
            {"amount": "500.00", **destination},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(WithdrawalRequest.objects.filter(tutor=self.tutor).exists())

    def test_cashout_rejects_invalid_destination_type(self):
        destination = self.destination_fields(destination_type="paypal")

        response = self.client.post(
            "/api/wallet/cash-outs/",
            {"amount": "500.00", **destination},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(WithdrawalRequest.objects.filter(tutor=self.tutor).exists())

    def test_cashout_rejects_missing_account_number(self):
        destination = self.destination_fields()
        destination.pop("account_number")

        response = self.client.post(
            "/api/wallet/cash-outs/",
            {"amount": "500.00", **destination},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(WithdrawalRequest.objects.filter(tutor=self.tutor).exists())

    def test_cashout_rejects_missing_account_name(self):
        destination = self.destination_fields()
        destination.pop("account_name")

        response = self.client.post(
            "/api/wallet/cash-outs/",
            {"amount": "500.00", **destination},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(WithdrawalRequest.objects.filter(tutor=self.tutor).exists())

    def test_cashout_rejects_missing_bank_name_for_bank_destination(self):
        destination = self.destination_fields(
            destination_type="bank",
            receiving_institution_id="bdo",
            receiving_institution_name="BDO",
            receiving_institution_code="BDO",
        )

        response = self.client.post(
            "/api/wallet/cash-outs/",
            {"amount": "500.00", **destination},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(WithdrawalRequest.objects.filter(tutor=self.tutor).exists())

    def test_cashout_rejects_missing_receiving_institution(self):
        destination = self.destination_fields()
        destination.pop("receiving_institution_id")
        destination.pop("receiving_institution_name")

        response = self.client.post(
            "/api/wallet/cash-outs/",
            {"amount": "500.00", **destination},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(WithdrawalRequest.objects.filter(tutor=self.tutor).exists())

    @patch("studybuddy.views.create_wallet_transaction")
    def test_cashout_synchronous_paymongo_failure_reverses_immediately(self, mock_create):
        destination = self.destination_fields()
        mock_create.side_effect = PayMongoCashOutError("Receiving account rejected the transfer.")

        response = self.client.post(
            "/api/wallet/cash-outs/",
            {"amount": "500.00", **destination},
            format="json",
        )

        self.wallet.refresh_from_db()
        withdrawal = WithdrawalRequest.objects.get(id=response.data["id"])

        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.data["provider_error_message"], "Receiving account rejected the transfer.")
        self.assertEqual(withdrawal.status, "failed")
        self.assertEqual(self.wallet.balance, Decimal("1000.00"))
        self.assertEqual(
            Transaction.objects.filter(
                wallet=self.wallet,
                transaction_type__in=["withdrawal_reversal", "cashout_fee_reversal"],
            ).count(),
            2,
        )

    @patch("studybuddy.views.create_wallet_transaction")
    def test_cashout_new_destination_requires_confirmation(self, mock_create):
        WithdrawalRequest.objects.create(
            tutor=self.tutor,
            amount=Decimal("500.00"),
            method="bank",
            receiving_institution_id="bdo",
            receiving_institution_name="BDO",
            account_number="123456",
            account_name="Cash Tutor",
            status="pending",
        )
        mock_create.return_value = self.provider_result()

        destination = self.destination_fields(
            destination_type="bank",
            receiving_institution_id="bpi",
            receiving_institution_name="BPI",
            receiving_institution_code="BPI",
            account_number="123456",
            account_name="Cash Tutor",
            bank_name="BPI",
        )

        unconfirmed_response = self.client.post(
            "/api/wallet/cash-outs/",
            {"amount": "500.00", **destination},
            format="json",
        )

        self.assertEqual(unconfirmed_response.status_code, 409)
        self.assertEqual(
            WithdrawalRequest.objects.filter(tutor=self.tutor, receiving_institution_id="bpi").count(),
            0,
        )

        confirmed_response = self.client.post(
            "/api/wallet/cash-outs/",
            {"amount": "500.00", "confirm_new_destination": True, **destination},
            format="json",
        )

        self.assertEqual(confirmed_response.status_code, 201)
        self.assertEqual(
            WithdrawalRequest.objects.filter(tutor=self.tutor, receiving_institution_id="bpi").count(),
            1,
        )

    def test_payout_destinations_endpoints_removed(self):
        get_response = self.client.get("/api/wallet/payout-destinations/")
        post_response = self.client.post(
            "/api/wallet/payout-destinations/",
            self.destination_fields(),
            format="json",
        )

        self.assertEqual(get_response.status_code, 404)
        self.assertEqual(post_response.status_code, 404)


class WalletCashInTests(APITestCase):
    def setUp(self):
        self.tutor_user = User.objects.create_user(
            username="cashin-tutor",
            email="cashin-tutor@example.com",
            password="password",
        )
        self.tutor_profile = UserProfile.objects.create(
            user=self.tutor_user,
            fname="CashIn",
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
        self.client.force_authenticate(user=self.tutor_user)

    def paymongo_response(self, status_code, payload):
        response = Mock()
        response.status_code = status_code
        response.json.return_value = payload
        return response

    def checkout_session_payload(self, session_id="cs_topup_123"):
        return {
            "data": {
                "id": session_id,
                "attributes": {"checkout_url": "https://checkout.paymongo.com/topup-session"},
            },
        }

    def retrieve_payload(self, status_value="paid"):
        return {
            "data": {
                "id": "cs_topup_123",
                "attributes": {"status": status_value},
            },
        }

    @patch("studybuddy.views.requests.post")
    def test_initiate_cash_in_creates_pending_topup_and_checkout(self, mock_post):
        mock_post.return_value = self.paymongo_response(200, self.checkout_session_payload())

        response = self.client.post("/api/wallet/cash-in/", {"amount": "500.00"}, format="json")

        topup = WalletTopUp.objects.get(id=response.data["id"])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["checkout_url"], "https://checkout.paymongo.com/topup-session")
        self.assertEqual(topup.status, "pending")
        self.assertEqual(topup.amount, Decimal("500.00"))
        self.assertEqual(topup.provider_reference, "cs_topup_123")

    def test_initiate_cash_in_rejects_invalid_amount(self):
        response = self.client.post("/api/wallet/cash-in/", {"amount": "0"}, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertFalse(WalletTopUp.objects.filter(tutor=self.tutor).exists())

    def test_initiate_cash_in_rejects_amount_below_minimum(self):
        response = self.client.post("/api/wallet/cash-in/", {"amount": "49.99"}, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("Minimum cash-in", response.data["error"])
        self.assertFalse(WalletTopUp.objects.filter(tutor=self.tutor).exists())

    @patch("studybuddy.views.requests.post")
    def test_initiate_cash_in_marks_failed_on_missing_checkout_url(self, mock_post):
        mock_post.return_value = self.paymongo_response(
            200, {"data": {"id": "cs_missing_url", "attributes": {}}}
        )

        response = self.client.post("/api/wallet/cash-in/", {"amount": "500.00"}, format="json")

        topup = WalletTopUp.objects.get(tutor=self.tutor)
        self.assertEqual(response.status_code, 502)
        self.assertEqual(topup.status, "failed")

    @patch("studybuddy.views.requests.post")
    def test_initiate_cash_in_marks_failed_on_provider_error(self, mock_post):
        mock_post.return_value = self.paymongo_response(
            400, {"errors": [{"detail": "Invalid line item."}]}
        )

        response = self.client.post("/api/wallet/cash-in/", {"amount": "500.00"}, format="json")

        topup = WalletTopUp.objects.get(tutor=self.tutor)
        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.data["error"], "Invalid line item.")
        self.assertEqual(topup.status, "failed")

    @patch("studybuddy.views.requests.post")
    def test_initiate_cash_in_marks_failed_on_network_error(self, mock_post):
        import requests

        mock_post.side_effect = requests.RequestException("connection reset")

        response = self.client.post("/api/wallet/cash-in/", {"amount": "500.00"}, format="json")

        topup = WalletTopUp.objects.get(tutor=self.tutor)
        self.assertEqual(response.status_code, 502)
        self.assertEqual(topup.status, "failed")

    @patch("studybuddy.views.requests.get")
    @patch("studybuddy.views.requests.post")
    def test_verify_cash_in_credits_wallet_exactly_once(self, mock_post, mock_get):
        mock_post.return_value = self.paymongo_response(200, self.checkout_session_payload())
        mock_get.return_value = self.paymongo_response(200, self.retrieve_payload("paid"))

        create_response = self.client.post("/api/wallet/cash-in/", {"amount": "500.00"}, format="json")
        topup_id = create_response.data["id"]

        first_verify = self.client.post(f"/api/wallet/cash-in/{topup_id}/verify/")
        second_verify = self.client.post(f"/api/wallet/cash-in/{topup_id}/verify/")

        self.wallet.refresh_from_db()
        self.assertEqual(first_verify.status_code, 200)
        self.assertEqual(second_verify.status_code, 200)
        self.assertEqual(self.wallet.balance, Decimal("500.00"))
        self.assertEqual(mock_get.call_count, 1)
        self.assertEqual(
            Transaction.objects.filter(wallet=self.wallet, transaction_type="cash_in").count(),
            1,
        )

    @patch("studybuddy.views.requests.get")
    @patch("studybuddy.views.requests.post")
    def test_verify_cash_in_rejects_unpaid_checkout(self, mock_post, mock_get):
        mock_post.return_value = self.paymongo_response(200, self.checkout_session_payload())
        mock_get.return_value = self.paymongo_response(200, self.retrieve_payload("pending"))

        create_response = self.client.post("/api/wallet/cash-in/", {"amount": "500.00"}, format="json")
        response = self.client.post(f"/api/wallet/cash-in/{create_response.data['id']}/verify/")

        self.wallet.refresh_from_db()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.wallet.balance, Decimal("0.00"))

    def test_verify_cash_in_rejects_missing_provider_reference(self):
        topup = WalletTopUp.objects.create(tutor=self.tutor, amount=Decimal("500.00"), status="pending")

        response = self.client.post(f"/api/wallet/cash-in/{topup.id}/verify/")

        self.assertEqual(response.status_code, 400)

    @patch("studybuddy.views.requests.get")
    @patch("studybuddy.views.requests.post")
    def test_verify_cash_in_returns_502_on_provider_error(self, mock_post, mock_get):
        mock_post.return_value = self.paymongo_response(200, self.checkout_session_payload())
        mock_get.return_value = self.paymongo_response(500, {"errors": []})

        create_response = self.client.post("/api/wallet/cash-in/", {"amount": "500.00"}, format="json")
        response = self.client.post(f"/api/wallet/cash-in/{create_response.data['id']}/verify/")

        self.wallet.refresh_from_db()
        self.assertEqual(response.status_code, 502)
        self.assertEqual(self.wallet.balance, Decimal("0.00"))

    @patch("studybuddy.views.requests.post")
    def test_verify_cash_in_404s_for_another_tutors_topup(self, mock_post):
        mock_post.return_value = self.paymongo_response(200, self.checkout_session_payload())
        create_response = self.client.post("/api/wallet/cash-in/", {"amount": "500.00"}, format="json")
        topup_id = create_response.data["id"]

        other_user = User.objects.create_user(
            username="other-cashin-tutor",
            email="other-cashin-tutor@example.com",
            password="password",
        )
        other_profile = UserProfile.objects.create(
            user=other_user, fname="Other", mname="", lname="Tutor", role="Tutor",
        )
        Tutor.objects.create(
            profile=other_profile,
            hourly_rate=Decimal("300.00"),
            can_online=True,
            can_f2f=True,
            teaching_level="SHS",
        )
        self.client.force_authenticate(user=other_user)

        response = self.client.post(f"/api/wallet/cash-in/{topup_id}/verify/")

        self.assertEqual(response.status_code, 404)


class SessionCreditWalletTests(APITestCase):
    def setUp(self):
        self.tutee_profile = UserProfile.objects.create(
            user=User.objects.create_user(
                username="credit-tutee", email="credit-tutee@example.com", password="password",
            ),
            fname="Credit",
            mname="",
            lname="Tutee",
            role="Tutee",
        )
        self.tutor_profile = UserProfile.objects.create(
            user=User.objects.create_user(
                username="credit-tutor", email="credit-tutor@example.com", password="password",
            ),
            fname="Credit",
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
        self.availability = TutorAvailability.objects.create(
            tutor=self.tutor, day="Mon", time_slot=time(14, 0), is_active=True,
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

    def create_payment(self, code, amount=Decimal("1000.00")):
        method, _ = PaymentMethod.objects.get_or_create(
            code=code, defaults={"method_name": code, "is_active": True}
        )
        return Payment.objects.create(
            booking=self.booking, amount=amount, method=method, payment_status="Paid",
        )

    def test_paymongo_settled_booking_credits_90_percent(self):
        self.create_payment("PAYMONGO")

        credit_tutor_wallet(self.booking)

        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal("900.00"))
        self.assertTrue(
            Transaction.objects.filter(
                wallet=self.wallet, transaction_type="session_credit", amount=Decimal("900.00"),
            ).exists()
        )

    def test_cash_booking_deducts_10_percent_commission(self):
        self.create_payment("CASH")

        credit_tutor_wallet(self.booking)

        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal("-100.00"))
        self.assertTrue(
            Transaction.objects.filter(
                wallet=self.wallet, transaction_type="commission_deduction", amount=Decimal("-100.00"),
            ).exists()
        )

    def test_credit_tutor_wallet_is_idempotent(self):
        self.create_payment("PAYMONGO")

        credit_tutor_wallet(self.booking)
        credit_tutor_wallet(self.booking)

        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal("900.00"))
        self.assertEqual(
            Transaction.objects.filter(wallet=self.wallet, transaction_type="session_credit").count(),
            1,
        )


class WalletStatusAndTransactionsTests(APITestCase):
    def setUp(self):
        self.tutor_user = User.objects.create_user(
            username="status-tutor", email="status-tutor@example.com", password="password",
        )
        self.tutor_profile = UserProfile.objects.create(
            user=self.tutor_user, fname="Status", mname="", lname="Tutor", role="Tutor",
        )
        self.tutor = Tutor.objects.create(
            profile=self.tutor_profile,
            hourly_rate=Decimal("300.00"),
            can_online=True,
            can_f2f=True,
            teaching_level="SHS",
        )
        self.wallet = Wallet.objects.get(tutor=self.tutor)
        self.wallet.balance = Decimal("750.00")
        self.wallet.pending_amount = Decimal("50.00")
        self.wallet.save(update_fields=["balance", "pending_amount"])
        self.client.force_authenticate(user=self.tutor_user)

    def test_wallet_status_returns_balance_and_cashout_settings(self):
        response = self.client.get("/api/wallet/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["balance"], 750.00)
        self.assertEqual(response.data["pending_amount"], 50.00)
        self.assertIn("cashin_minimum", response.data)
        self.assertIn("cashout_minimum", response.data)
        self.assertIn("cashout_provider_fee", response.data)

    def test_wallet_transactions_returns_history_ordered_newest_first(self):
        older = Transaction.objects.create(
            wallet=self.wallet,
            transaction_type="session_credit",
            amount=Decimal("100.00"),
            description="Older credit",
        )
        newer = Transaction.objects.create(
            wallet=self.wallet,
            transaction_type="cash_in",
            amount=Decimal("200.00"),
            description="Newer top-up",
        )

        response = self.client.get("/api/wallet/transactions/")

        self.assertEqual(response.status_code, 200)
        ids = [tx["id"] for tx in response.data]
        self.assertEqual(ids[0], newer.id)
        self.assertIn(older.id, ids)


class DevWalletFundsTests(APITestCase):
    """Calls the dev_add/remove_wallet_funds views directly via APIRequestFactory.

    /api/dev/wallet/add/ and /remove/ are only added to urlpatterns when
    settings.DEBUG is True at process startup (see urls.py); override_settings
    in a test can't retroactively register them. Calling the view functions
    directly exercises their real DEBUG check without depending on urlconf.
    """

    def setUp(self):
        self.factory = APIRequestFactory()
        self.tutor_user = User.objects.create_user(
            username="dev-funds-tutor", email="dev-funds-tutor@example.com", password="password",
        )
        self.tutor_profile = UserProfile.objects.create(
            user=self.tutor_user, fname="Dev", mname="", lname="Tutor", role="Tutor",
        )
        self.tutor = Tutor.objects.create(
            profile=self.tutor_profile,
            hourly_rate=Decimal("300.00"),
            can_online=True,
            can_f2f=True,
            teaching_level="SHS",
        )
        self.wallet = Wallet.objects.get(tutor=self.tutor)

    def call_view(self, view, amount):
        request = self.factory.post(f"/api/dev/wallet/_/", {"amount": amount}, format="json")
        force_authenticate(request, user=self.tutor_user)
        return view(request)

    @override_settings(DEBUG=True)
    def test_dev_add_wallet_funds_increases_balance(self):
        response = self.call_view(dev_add_wallet_funds, "300")

        self.wallet.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.wallet.balance, Decimal("300.00"))

    @override_settings(DEBUG=True)
    def test_dev_remove_wallet_funds_decreases_balance(self):
        self.wallet.balance = Decimal("300.00")
        self.wallet.save(update_fields=["balance"])

        response = self.call_view(dev_remove_wallet_funds, "100")

        self.wallet.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.wallet.balance, Decimal("200.00"))

    @override_settings(DEBUG=False)
    def test_dev_wallet_funds_404s_when_debug_disabled(self):
        add_response = self.call_view(dev_add_wallet_funds, "300")
        remove_response = self.call_view(dev_remove_wallet_funds, "100")

        self.assertEqual(add_response.status_code, 404)
        self.assertEqual(remove_response.status_code, 404)


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


class TutorDocumentRenewalTests(APITestCase):
    def setUp(self):
        from datetime import timedelta
        from django.utils import timezone

        self.institution = PartnerInstitution.objects.create(
            institution_name="CPU",
            school_email_domain="cpu.edu",
            is_active=True,
        )
        self.other_institution = PartnerInstitution.objects.create(
            institution_name="Other University",
            school_email_domain="other.edu",
            is_active=True,
        )
        self.tutor_user = User.objects.create_user(
            username="renewal-tutor@cpu.edu",
            email="renewal-tutor@cpu.edu",
            password="password",
        )
        self.tutor_profile = UserProfile.objects.create(
            user=self.tutor_user,
            fname="Renewal",
            mname="",
            lname="Tutor",
            role="Tutor",
            institution=self.institution,
        )
        Tutor.objects.create(profile=self.tutor_profile)
        self.reviewed_at = timezone.now() - timedelta(days=91)
        self.application = TutorApplication.objects.create(
            profile=self.tutor_profile,
            school_id=self.upload("initial-id.jpg", b"initial-id", "image/jpeg"),
            enrollment_proof=self.upload("initial-rf.pdf", b"initial-rf", "application/pdf"),
            application_status="approved",
            reviewed_at=self.reviewed_at,
        )
        self.admin_user = User.objects.create_user(
            username="admin@cpu.edu",
            email="admin@cpu.edu",
            password="password",
        )
        self.admin_profile = UserProfile.objects.create(
            user=self.admin_user,
            fname="Admin",
            mname="",
            lname="User",
            role="Admin",
            institution=self.institution,
        )
        self.other_admin_user = User.objects.create_user(
            username="admin@other.edu",
            email="admin@other.edu",
            password="password",
        )
        UserProfile.objects.create(
            user=self.other_admin_user,
            fname="Other",
            mname="",
            lname="Admin",
            role="Admin",
            institution=self.other_institution,
        )

    def upload(self, name, content, content_type):
        from django.core.files.uploadedfile import SimpleUploadedFile

        return SimpleUploadedFile(name, content, content_type=content_type)

    def renewal_payload(self):
        return {
            "school_id": self.upload("renewal-id.jpg", b"renewal-id", "image/jpeg"),
            "enrollment_proof": self.upload("renewal-rf.pdf", b"renewal-rf", "application/pdf"),
            "reason_to_tutor": "Still enrolled and available to tutor.",
        }

    def test_profile_status_exposes_due_document_renewal_state(self):
        self.client.force_authenticate(user=self.tutor_user)

        response = self.client.get("/api/profile/status/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["application_status"], "approved")
        self.assertEqual(response.data["document_renewal_status"], "due")
        self.assertTrue(response.data["can_submit_document_renewal"])
        self.assertIsNotNone(response.data["document_renewal_due_at"])

    def test_tutor_can_submit_due_document_renewal(self):
        self.client.force_authenticate(user=self.tutor_user)

        response = self.client.post(
            "/api/tutor-application/renewal/",
            self.renewal_payload(),
            format="multipart",
        )

        self.assertEqual(response.status_code, 201)
        renewal = TutorDocumentRenewalReview.objects.get(application=self.application)
        self.assertEqual(renewal.status, "pending")
        self.assertEqual(response.data["document_renewal_status"], "pending")

    def test_legacy_resubmit_endpoint_creates_document_renewal_for_approved_tutor(self):
        self.client.force_authenticate(user=self.tutor_user)

        response = self.client.post(
            "/api/tutor-application/resubmit/",
            self.renewal_payload(),
            format="multipart",
        )

        self.assertEqual(response.status_code, 201)
        self.application.refresh_from_db()
        self.assertEqual(self.application.application_status, "approved")
        self.assertEqual(TutorDocumentRenewalReview.objects.filter(status="pending").count(), 1)

    def test_tutor_cannot_submit_verified_document_renewal_before_due(self):
        from django.utils import timezone

        self.application.reviewed_at = timezone.now()
        self.application.save(update_fields=["reviewed_at"])
        self.client.force_authenticate(user=self.tutor_user)

        response = self.client.post(
            "/api/tutor-application/renewal/",
            self.renewal_payload(),
            format="multipart",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(TutorDocumentRenewalReview.objects.count(), 0)

    def test_admin_can_approve_document_renewal_and_due_date_moves_forward(self):
        renewal = TutorDocumentRenewalReview.objects.create(
            application=self.application,
            profile=self.tutor_profile,
            school_id=self.upload("pending-id.jpg", b"pending-id", "image/jpeg"),
            enrollment_proof=self.upload("pending-rf.pdf", b"pending-rf", "application/pdf"),
            status="pending",
        )
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.patch(
            f"/api/admin/tutor-document-renewals/{renewal.id}/",
            {"application_status": "approved"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        renewal.refresh_from_db()
        self.assertEqual(renewal.status, "approved")
        self.assertEqual(self.application.document_renewal_status(), "verified")
        self.assertGreater(self.application.document_renewal_due_at(), renewal.reviewed_at)

    def test_admin_can_reject_document_renewal_and_tutor_can_resubmit(self):
        renewal = TutorDocumentRenewalReview.objects.create(
            application=self.application,
            profile=self.tutor_profile,
            school_id=self.upload("pending-id.jpg", b"pending-id", "image/jpeg"),
            enrollment_proof=self.upload("pending-rf.pdf", b"pending-rf", "application/pdf"),
            status="pending",
        )
        self.client.force_authenticate(user=self.admin_user)

        reject_response = self.client.patch(
            f"/api/admin/tutor-document-renewals/{renewal.id}/",
            {
                "application_status": "rejected",
                "rejection_reason": "RF is not for the current term.",
            },
            format="json",
        )

        self.assertEqual(reject_response.status_code, 200)
        renewal.refresh_from_db()
        self.assertEqual(renewal.status, "rejected")
        self.client.force_authenticate(user=self.tutor_user)
        resubmit_response = self.client.post(
            "/api/tutor-application/renewal/",
            self.renewal_payload(),
            format="multipart",
        )
        self.assertEqual(resubmit_response.status_code, 201)
        self.assertEqual(TutorDocumentRenewalReview.objects.filter(status="pending").count(), 1)

    def test_admin_cannot_review_other_institution_document_renewal(self):
        renewal = TutorDocumentRenewalReview.objects.create(
            application=self.application,
            profile=self.tutor_profile,
            school_id=self.upload("pending-id.jpg", b"pending-id", "image/jpeg"),
            enrollment_proof=self.upload("pending-rf.pdf", b"pending-rf", "application/pdf"),
            status="pending",
        )
        self.client.force_authenticate(user=self.other_admin_user)

        response = self.client.patch(
            f"/api/admin/tutor-document-renewals/{renewal.id}/",
            {"application_status": "approved"},
            format="json",
        )

        self.assertEqual(response.status_code, 404)
        renewal.refresh_from_db()
        self.assertEqual(renewal.status, "pending")


class ApplicationVerificationSharedBaseTests(APITestCase):
    """Proves TutorApplication and TuteeApplication share identical renewal-cadence
    behavior via their common abstract base (Phase 1 of tutee enrollment verification,
    see docs/plans/2026-07-01-tutee-verification-phase1-model.md)."""

    def setUp(self):
        self.institution = PartnerInstitution.objects.create(
            institution_name="CPU",
            school_email_domain="cpu.edu",
            is_active=True,
        )
        self.tutor_user = User.objects.create_user(
            username="shared-base-tutor@cpu.edu",
            email="shared-base-tutor@cpu.edu",
            password="password",
        )
        self.tutor_profile = UserProfile.objects.create(
            user=self.tutor_user,
            fname="Shared",
            mname="",
            lname="Tutor",
            role="Tutor",
            institution=self.institution,
        )
        self.tutee_user = User.objects.create_user(
            username="shared-base-tutee@cpu.edu",
            email="shared-base-tutee@cpu.edu",
            password="password",
        )
        self.tutee_profile = UserProfile.objects.create(
            user=self.tutee_user,
            fname="Shared",
            mname="",
            lname="Tutee",
            role="Tutee",
            institution=self.institution,
        )

    def upload(self, name, content, content_type):
        from django.core.files.uploadedfile import SimpleUploadedFile

        return SimpleUploadedFile(name, content, content_type=content_type)

    def make_application(self, model, profile, reviewed_at):
        return model.objects.create(
            profile=profile,
            school_id=self.upload("id.jpg", b"id", "image/jpeg"),
            enrollment_proof=self.upload("rf.pdf", b"rf", "application/pdf"),
            application_status="approved",
            reviewed_at=reviewed_at,
        )

    def assert_shared_renewal_behavior(self, model, review_model, profile):
        from datetime import timedelta
        from django.utils import timezone

        due_reviewed_at = timezone.now() - timedelta(days=91)
        application = self.make_application(model, profile, due_reviewed_at)

        # Verified just after approval, due once DOCUMENT_RENEWAL_INTERVAL_DAYS has elapsed.
        self.assertEqual(
            application.document_renewal_due_at(),
            due_reviewed_at + timedelta(days=model.DOCUMENT_RENEWAL_INTERVAL_DAYS),
        )
        self.assertEqual(application.document_renewal_status(), "due")
        self.assertTrue(application.can_submit_document_renewal())

        # A pending renewal review takes precedence over "due".
        pending_renewal = review_model.objects.create(
            application=application,
            profile=profile,
            school_id=self.upload("renewal-id.jpg", b"renewal-id", "image/jpeg"),
            enrollment_proof=self.upload("renewal-rf.pdf", b"renewal-rf", "application/pdf"),
            status="pending",
        )
        self.assertEqual(application.latest_document_renewal_review(), pending_renewal)
        self.assertEqual(application.document_renewal_status(), "pending")
        self.assertFalse(application.can_submit_document_renewal())

        # Approving the renewal moves the renewal clock forward and re-verifies.
        pending_renewal.status = "approved"
        pending_renewal.reviewed_at = timezone.now()
        pending_renewal.save(update_fields=["status", "reviewed_at"])
        self.assertEqual(application.latest_approved_document_review_at(), pending_renewal.reviewed_at)
        self.assertEqual(application.document_renewal_status(), "verified")
        self.assertGreater(application.document_renewal_due_at(), due_reviewed_at)

        # A rejected renewal makes the application resubmittable, not "verified".
        pending_renewal.status = "rejected"
        pending_renewal.reviewed_at = timezone.now()
        pending_renewal.save(update_fields=["status", "reviewed_at"])
        self.assertEqual(application.document_renewal_status(), "rejected")
        self.assertTrue(application.can_submit_document_renewal())

    def test_tutor_application_shared_renewal_behavior(self):
        self.assert_shared_renewal_behavior(
            TutorApplication, TutorDocumentRenewalReview, self.tutor_profile
        )

    def test_tutee_application_shared_renewal_behavior(self):
        self.assert_shared_renewal_behavior(
            TuteeApplication, TuteeDocumentRenewalReview, self.tutee_profile
        )

    def test_reminder_dedup_fields_default_null_for_both_roles(self):
        tutor_application = self.make_application(
            TutorApplication, self.tutor_profile, timezone_now_minus_days(1)
        )
        tutee_application = self.make_application(
            TuteeApplication, self.tutee_profile, timezone_now_minus_days(1)
        )

        for application in (tutor_application, tutee_application):
            self.assertIsNone(application.reminder_7day_sent_at)
            self.assertIsNone(application.reminder_1day_sent_at)

    def test_generalized_document_review_context_matches_tutor_shape(self):
        from .views import get_document_review_context, get_tutor_document_review_context

        due_reviewed_at = timezone_now_minus_days(91)
        tutor_application = self.make_application(TutorApplication, self.tutor_profile, due_reviewed_at)
        tutee_application = self.make_application(TuteeApplication, self.tutee_profile, due_reviewed_at)

        tutor_context = get_tutor_document_review_context(self.tutor_profile)
        generalized_tutor_context = get_document_review_context(tutor_application)
        generalized_tutee_context = get_document_review_context(tutee_application)

        self.assertEqual(tutor_context, generalized_tutor_context)
        self.assertEqual(set(generalized_tutor_context.keys()), set(generalized_tutee_context.keys()))
        self.assertEqual(generalized_tutee_context["document_renewal_status"], "due")
        self.assertTrue(generalized_tutee_context["can_submit_document_renewal"])


def timezone_now_minus_days(days):
    from datetime import timedelta
    from django.utils import timezone

    return timezone.now() - timedelta(days=days)


class BookingVerificationGateTests(APITestCase):
    """Phase 2 of tutee enrollment verification: can_create_new_booking gates new booking creation
    (tutee) and accepting a pending booking request (tutor). See
    docs/plans/2026-07-01-tutee-verification-phase2-gate.md."""

    ENFORCED = {'TUTEE_VERIFICATION_ENFORCEMENT_START_DATE': '2020-01-01'}
    NOT_YET_ENFORCED = {'TUTEE_VERIFICATION_ENFORCEMENT_START_DATE': None}
    MALFORMED = {'TUTEE_VERIFICATION_ENFORCEMENT_START_DATE': 'not-a-date'}

    def setUp(self):
        from datetime import timedelta
        from django.utils import timezone
        from .views import WEEKDAY_MAP

        self.institution = PartnerInstitution.objects.create(
            institution_name="CPU",
            school_email_domain="cpu.edu",
            is_active=True,
        )
        self.tutee_user = User.objects.create_user(
            username="gate-tutee@cpu.edu",
            email="gate-tutee@cpu.edu",
            password="password",
        )
        self.tutee_profile = UserProfile.objects.create(
            user=self.tutee_user,
            fname="Gate",
            mname="",
            lname="Tutee",
            role="Tutee",
            institution=self.institution,
        )
        self.tutor_user = User.objects.create_user(
            username="gate-tutor@cpu.edu",
            email="gate-tutor@cpu.edu",
            password="password",
        )
        self.tutor_profile = UserProfile.objects.create(
            user=self.tutor_user,
            fname="Gate",
            mname="",
            lname="Tutor",
            role="Tutor",
            institution=self.institution,
        )
        self.tutor = Tutor.objects.create(
            profile=self.tutor_profile,
            hourly_rate=Decimal("280.00"),
            can_online=True,
            can_f2f=True,
            teaching_level="SHS",
        )
        self.future_date = timezone.now().date() + timedelta(days=30)
        self.availability = TutorAvailability.objects.create(
            tutor=self.tutor,
            day=WEEKDAY_MAP[self.future_date.weekday()],
            time_slot=time(14, 0),
            is_active=True,
        )

    def upload(self, name, content, content_type):
        from django.core.files.uploadedfile import SimpleUploadedFile

        return SimpleUploadedFile(name, content, content_type=content_type)

    def make_verified_application(self, model, profile):
        return model.objects.create(
            profile=profile,
            school_id=self.upload("id.jpg", b"id", "image/jpeg"),
            enrollment_proof=self.upload("rf.pdf", b"rf", "application/pdf"),
            application_status="approved",
            reviewed_at=timezone_now_minus_days(1),
        )

    def make_due_application(self, model, profile):
        return model.objects.create(
            profile=profile,
            school_id=self.upload("id.jpg", b"id", "image/jpeg"),
            enrollment_proof=self.upload("rf.pdf", b"rf", "application/pdf"),
            application_status="approved",
            reviewed_at=timezone_now_minus_days(91),
        )

    def post_confirm_booking(self):
        self.client.force_authenticate(user=self.tutee_user)
        return self.client.post(
            "/api/bookings/confirm/",
            {
                "tutor_id": self.tutor_profile.id,
                "slots": [{
                    "availability_id": self.availability.id,
                    "session_date": self.future_date.isoformat(),
                    "session_mode": "Online",
                }],
            },
            format="json",
        )

    @override_settings(**ENFORCED)
    def test_tutee_without_application_blocked_once_enforced(self):
        response = self.post_confirm_booking()

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data.get("code"), "verification_required")

    @override_settings(**NOT_YET_ENFORCED)
    def test_tutee_without_application_allowed_during_grace_period(self):
        response = self.post_confirm_booking()

        self.assertEqual(response.status_code, 200)

    @override_settings(**MALFORMED)
    def test_malformed_enforcement_date_fails_safe_as_not_enforced(self):
        response = self.post_confirm_booking()

        self.assertEqual(response.status_code, 200)

    @override_settings(**ENFORCED)
    def test_tutee_with_verified_application_can_book(self):
        self.make_verified_application(TuteeApplication, self.tutee_profile)

        response = self.post_confirm_booking()

        self.assertEqual(response.status_code, 200)

    @override_settings(**ENFORCED)
    def test_tutee_with_due_renewal_blocked(self):
        self.make_due_application(TuteeApplication, self.tutee_profile)

        response = self.post_confirm_booking()

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data.get("code"), "verification_required")

    def create_pending_booking(self):
        return Booking.objects.create(
            student=self.tutee_profile,
            tutor=self.tutor,
            availability=self.availability,
            session_date=self.future_date,
            session_mode="Online",
            booking_request_id=uuid4(),
            status="Pending",
        )

    def test_tutor_without_application_blocked_from_approving(self):
        booking = self.create_pending_booking()
        self.client.force_authenticate(user=self.tutor_user)

        response = self.client.post(f"/api/bookings/{booking.id}/approve/")

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data.get("code"), "verification_required")
        booking.refresh_from_db()
        self.assertEqual(booking.status, "Pending")

    def test_tutor_with_verified_application_can_approve_booking(self):
        self.make_verified_application(TutorApplication, self.tutor_profile)
        booking = self.create_pending_booking()
        self.client.force_authenticate(user=self.tutor_user)

        response = self.client.post(f"/api/bookings/{booking.id}/approve/")

        self.assertEqual(response.status_code, 200)
        booking.refresh_from_db()
        self.assertEqual(booking.status, "Confirmed")

    def test_tutor_with_due_renewal_blocked_from_approving(self):
        self.make_due_application(TutorApplication, self.tutor_profile)
        booking = self.create_pending_booking()
        self.client.force_authenticate(user=self.tutor_user)

        response = self.client.post(f"/api/bookings/{booking.id}/approve/")

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data.get("code"), "verification_required")
        booking.refresh_from_db()
        self.assertEqual(booking.status, "Pending")


class TuteeVerificationPhase3Tests(APITestCase):
    """Phase 3 of tutee enrollment verification: the mirrored tutee-facing endpoints, admin views, and
    the profile_status role dispatcher. See docs/plans/2026-07-01-tutee-verification-phase3-ui.md."""

    def setUp(self):
        self.institution = PartnerInstitution.objects.create(
            institution_name="CPU",
            school_email_domain="cpu.edu",
            is_active=True,
        )
        self.other_institution = PartnerInstitution.objects.create(
            institution_name="Other University",
            school_email_domain="other.edu",
            is_active=True,
        )
        self.tutee_user = User.objects.create_user(
            username="phase3-tutee@cpu.edu",
            email="phase3-tutee@cpu.edu",
            password="password",
        )
        self.tutee_profile = UserProfile.objects.create(
            user=self.tutee_user,
            fname="Phase3",
            mname="",
            lname="Tutee",
            role="Tutee",
            institution=self.institution,
        )
        self.admin_user = User.objects.create_user(
            username="phase3-admin@cpu.edu",
            email="phase3-admin@cpu.edu",
            password="password",
        )
        self.admin_profile = UserProfile.objects.create(
            user=self.admin_user,
            fname="Phase3",
            mname="",
            lname="Admin",
            role="Admin",
            institution=self.institution,
        )
        self.other_admin_user = User.objects.create_user(
            username="phase3-admin@other.edu",
            email="phase3-admin@other.edu",
            password="password",
        )
        UserProfile.objects.create(
            user=self.other_admin_user,
            fname="Other",
            mname="",
            lname="Admin",
            role="Admin",
            institution=self.other_institution,
        )

    def upload(self, name, content, content_type):
        from django.core.files.uploadedfile import SimpleUploadedFile

        return SimpleUploadedFile(name, content, content_type=content_type)

    def test_tutee_application_status_returns_404_when_none_exists(self):
        self.client.force_authenticate(user=self.tutee_user)

        response = self.client.get("/api/tutee-application/status/")

        self.assertEqual(response.status_code, 404)

    def test_tutee_application_resubmit_creates_initial_application_when_none_exists(self):
        self.client.force_authenticate(user=self.tutee_user)

        response = self.client.post(
            "/api/tutee-application/resubmit/",
            {
                "school_id": self.upload("id.jpg", b"id", "image/jpeg"),
                "enrollment_proof": self.upload("rf.pdf", b"rf", "application/pdf"),
                "reason_to_tutor": "First time submitting",
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, 200)
        application = TuteeApplication.objects.get(profile=self.tutee_profile)
        self.assertEqual(application.application_status, "pending")
        self.assertEqual(
            PlatformActivity.objects.filter(activity_type="tutee_application").count(), 1
        )

    def test_tutee_application_resubmit_rejected_goes_back_to_pending(self):
        application = TuteeApplication.objects.create(
            profile=self.tutee_profile,
            school_id=self.upload("id.jpg", b"id", "image/jpeg"),
            enrollment_proof=self.upload("rf.pdf", b"rf", "application/pdf"),
            application_status="rejected",
            rejection_reason="Blurry photo",
        )
        self.client.force_authenticate(user=self.tutee_user)

        response = self.client.post(
            "/api/tutee-application/resubmit/",
            {
                "school_id": self.upload("new-id.jpg", b"new-id", "image/jpeg"),
                "enrollment_proof": self.upload("new-rf.pdf", b"new-rf", "application/pdf"),
                "reason_to_tutor": "Resubmitting",
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, 200)
        application.refresh_from_db()
        self.assertEqual(application.application_status, "pending")
        self.assertEqual(
            PlatformActivity.objects.filter(activity_type="tutee_application").count(), 1
        )

    def test_tutee_document_renewal_submit_when_due(self):
        application = TuteeApplication.objects.create(
            profile=self.tutee_profile,
            school_id=self.upload("id.jpg", b"id", "image/jpeg"),
            enrollment_proof=self.upload("rf.pdf", b"rf", "application/pdf"),
            application_status="approved",
            reviewed_at=timezone_now_minus_days(91),
        )
        self.client.force_authenticate(user=self.tutee_user)

        response = self.client.post(
            "/api/tutee-application/renewal/",
            {
                "school_id": self.upload("new-id.jpg", b"new-id", "image/jpeg"),
                "enrollment_proof": self.upload("new-rf.pdf", b"new-rf", "application/pdf"),
                "reason_to_tutor": "Still enrolled",
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["document_renewal_status"], "pending")
        renewal = TuteeDocumentRenewalReview.objects.get(application=application)
        self.assertEqual(renewal.status, "pending")

    def test_admin_tutee_application_list_combines_applications_and_renewals(self):
        TuteeApplication.objects.create(
            profile=self.tutee_profile,
            school_id=self.upload("id.jpg", b"id", "image/jpeg"),
            enrollment_proof=self.upload("rf.pdf", b"rf", "application/pdf"),
            application_status="pending",
        )
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.get("/api/admin/tutee-applications/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["applicant_name"], "Phase3 Tutee")

    def test_admin_can_approve_initial_tutee_application(self):
        application = TuteeApplication.objects.create(
            profile=self.tutee_profile,
            school_id=self.upload("id.jpg", b"id", "image/jpeg"),
            enrollment_proof=self.upload("rf.pdf", b"rf", "application/pdf"),
            application_status="pending",
        )
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.patch(
            f"/api/admin/tutee-applications/{application.id}/",
            {"application_status": "approved"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        application.refresh_from_db()
        self.assertEqual(application.application_status, "approved")

    def test_admin_can_approve_tutee_document_renewal_and_resets_dedup_fields(self):
        application = TuteeApplication.objects.create(
            profile=self.tutee_profile,
            school_id=self.upload("id.jpg", b"id", "image/jpeg"),
            enrollment_proof=self.upload("rf.pdf", b"rf", "application/pdf"),
            application_status="approved",
            reviewed_at=timezone_now_minus_days(91),
            reminder_7day_sent_at=timezone_now_minus_days(3),
            reminder_1day_sent_at=timezone_now_minus_days(1),
        )
        renewal = TuteeDocumentRenewalReview.objects.create(
            application=application,
            profile=self.tutee_profile,
            school_id=self.upload("pending-id.jpg", b"pending-id", "image/jpeg"),
            enrollment_proof=self.upload("pending-rf.pdf", b"pending-rf", "application/pdf"),
            status="pending",
        )
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.patch(
            f"/api/admin/tutee-document-renewals/{renewal.id}/",
            {"application_status": "approved"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        application.refresh_from_db()
        self.assertEqual(application.document_renewal_status(), "verified")
        self.assertIsNone(application.reminder_7day_sent_at)
        self.assertIsNone(application.reminder_1day_sent_at)

    def test_admin_cannot_review_other_institution_tutee_document_renewal(self):
        application = TuteeApplication.objects.create(
            profile=self.tutee_profile,
            school_id=self.upload("id.jpg", b"id", "image/jpeg"),
            enrollment_proof=self.upload("rf.pdf", b"rf", "application/pdf"),
            application_status="approved",
            reviewed_at=timezone_now_minus_days(91),
        )
        renewal = TuteeDocumentRenewalReview.objects.create(
            application=application,
            profile=self.tutee_profile,
            school_id=self.upload("pending-id.jpg", b"pending-id", "image/jpeg"),
            enrollment_proof=self.upload("pending-rf.pdf", b"pending-rf", "application/pdf"),
            status="pending",
        )
        self.client.force_authenticate(user=self.other_admin_user)

        response = self.client.patch(
            f"/api/admin/tutee-document-renewals/{renewal.id}/",
            {"application_status": "approved"},
            format="json",
        )

        self.assertEqual(response.status_code, 404)
        renewal.refresh_from_db()
        self.assertEqual(renewal.status, "pending")

    @override_settings(TUTEE_VERIFICATION_ENFORCEMENT_START_DATE='2020-01-01')
    def test_profile_status_dispatches_to_tutee_context_and_exposes_enforcement_flag(self):
        TuteeApplication.objects.create(
            profile=self.tutee_profile,
            school_id=self.upload("id.jpg", b"id", "image/jpeg"),
            enrollment_proof=self.upload("rf.pdf", b"rf", "application/pdf"),
            application_status="approved",
            reviewed_at=timezone_now_minus_days(91),
        )
        self.client.force_authenticate(user=self.tutee_user)

        response = self.client.get("/api/profile/status/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["document_renewal_status"], "due")
        self.assertTrue(response.data["tutee_verification_enforced"])

    def test_profile_status_for_tutee_with_no_application_returns_empty_context(self):
        self.client.force_authenticate(user=self.tutee_user)

        response = self.client.get("/api/profile/status/")

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.data["document_renewal_status"])
        self.assertFalse(response.data["document_renewal_required"])


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

    def test_staff_user_without_profile_can_login_as_admin(self):
        admin_user = User.objects.create_user(
            username="admin@example.edu",
            email="admin@example.edu",
            password="password",
            is_staff=True,
        )

        login_response = self.client.post(
            "/api/login/",
            {"email": admin_user.email, "password": "password"},
            format="json",
        )

        self.assertEqual(login_response.status_code, 200)
        self.assertTrue(login_response.data["requires_2fa"])

        profile = UserProfile.objects.get(user=admin_user)
        self.assertEqual(profile.role, "Admin")
        self.assertTrue(profile.profile_completed)
        self.assertTrue(profile.is_domain_exempt)

        verify_response = self.client.post(
            "/api/login/verify-otp/",
            {
                "challenge_id": login_response.data["challenge_id"],
                "code": self.latest_otp_code(),
            },
            format="json",
        )

        self.assertEqual(verify_response.status_code, 200)
        self.assertEqual(verify_response.data["role"], "Admin")
        self.assertEqual(verify_response.data["email"], admin_user.email)

    def test_staff_user_with_superadmin_profile_keeps_superadmin_on_login(self):
        admin_user = User.objects.create_user(
            username="superadmin@example.edu",
            email="superadmin@example.edu",
            password="password",
            is_staff=True,
        )
        UserProfile.objects.create(
            user=admin_user,
            fname="Super",
            mname="",
            lname="Admin",
            role="SuperAdmin",
            profile_completed=True,
            is_domain_exempt=True,
        )

        login_response = self.client.post(
            "/api/login/",
            {"email": admin_user.email, "password": "password"},
            format="json",
        )

        self.assertEqual(login_response.status_code, 200)

        verify_response = self.client.post(
            "/api/login/verify-otp/",
            {
                "challenge_id": login_response.data["challenge_id"],
                "code": self.latest_otp_code(),
            },
            format="json",
        )

        self.assertEqual(verify_response.status_code, 200)
        self.assertEqual(verify_response.data["role"], "SuperAdmin")

        profile = UserProfile.objects.get(user=admin_user)
        self.assertEqual(profile.role, "SuperAdmin")

    def test_make_superadmin_command_promotes_existing_user(self):
        target_user = User.objects.create_user(
            username="target@example.edu",
            email="target@example.edu",
            password="password",
        )
        profile = UserProfile.objects.create(
            user=target_user,
            fname="Target",
            mname="",
            lname="User",
            role="Tutee",
            profile_completed=False,
            is_domain_exempt=False,
            is_suspended=True,
        )

        output = StringIO()
        call_command("make_superadmin", target_user.email, stdout=output)

        profile.refresh_from_db()
        self.assertEqual(profile.role, "SuperAdmin")
        self.assertTrue(profile.profile_completed)
        self.assertTrue(profile.is_domain_exempt)
        self.assertFalse(profile.is_suspended)
        self.assertIn("Promoted target@example.edu to SuperAdmin.", output.getvalue())

    def test_make_superadmin_command_prefers_login_username_when_email_is_duplicated(self):
        legacy_user = User.objects.create_user(
            username="duplicate",
            email="duplicate@example.edu",
            password="password",
        )
        legacy_profile = UserProfile.objects.create(
            user=legacy_user,
            fname="Legacy",
            mname="",
            lname="Admin",
            role="Admin",
        )
        login_user = User.objects.create_user(
            username="duplicate@example.edu",
            email="duplicate@example.edu",
            password="password",
        )
        login_profile = UserProfile.objects.create(
            user=login_user,
            fname="Login",
            mname="",
            lname="Admin",
            role="Admin",
        )

        output = StringIO()
        call_command("make_superadmin", login_user.email, stdout=output)

        legacy_profile.refresh_from_db()
        login_profile.refresh_from_db()
        self.assertEqual(legacy_profile.role, "Admin")
        self.assertEqual(login_profile.role, "SuperAdmin")
        self.assertIn(f"Promoting login username match user_id={login_user.id}.", output.getvalue())

    def test_staff_user_without_profile_gets_admin_profile_status(self):
        admin_user = User.objects.create_user(
            username="status-admin@example.edu",
            email="status-admin@example.edu",
            password="password",
            is_staff=True,
        )
        self.client.force_authenticate(user=admin_user)

        response = self.client.get("/api/profile/status/")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["profile_completed"])
        self.assertEqual(response.data["role"], "Admin")

        profile = UserProfile.objects.get(user=admin_user)
        self.assertEqual(profile.role, "Admin")
        self.assertTrue(profile.is_domain_exempt)

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

    def test_list_bookings_does_not_merge_same_group_across_dates(self):
        group_id = uuid4()
        Booking.objects.create(
            student=self.student,
            tutor=self.tutor,
            availability=self.availability,
            session_date=date(2026, 6, 6),
            session_mode="Online",
            session_group_id=group_id,
            status="Rejected",
        )
        Booking.objects.create(
            student=self.student,
            tutor=self.tutor,
            availability=self.availability,
            session_date=date(2026, 6, 10),
            session_mode="Online",
            session_group_id=group_id,
            status="Rejected",
        )

        response = self.client.get("/api/bookings/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(
            [str(booking["date"]) for booking in response.data],
            ["2026-06-06", "2026-06-10"],
        )

    def test_student_can_hide_rejected_dashboard_pill_without_hiding_for_tutor(self):
        booking = Booking.objects.create(
            student=self.student,
            tutor=self.tutor,
            availability=self.availability,
            session_date=date(2026, 6, 6),
            session_mode="Online",
            status="Rejected",
        )

        response = self.client.delete(f"/api/bookings/{booking.id}/dashboard-pill/")

        self.assertEqual(response.status_code, 200)
        booking.refresh_from_db()
        self.assertIsNotNone(booking.dashboard_hidden_by_student_at)
        self.assertIsNone(booking.dashboard_hidden_by_tutor_at)

        student_response = self.client.get("/api/bookings/")
        self.assertTrue(student_response.data[0]["dashboard_hidden_by_current_user"])

        self.client.force_authenticate(user=self.tutor_user)
        tutor_response = self.client.get("/api/bookings/")
        self.assertFalse(tutor_response.data[0]["dashboard_hidden_by_current_user"])

    def test_hide_dashboard_pill_applies_to_all_slots_in_group(self):
        group_id = uuid4()
        next_availability = TutorAvailability.objects.create(
            tutor=self.tutor,
            day="Mon",
            time_slot=time(14, 30),
            is_active=True,
        )
        first_booking = Booking.objects.create(
            student=self.student,
            tutor=self.tutor,
            availability=self.availability,
            session_date=date(2026, 6, 6),
            session_mode="Online",
            session_group_id=group_id,
            status="Cancelled",
        )
        second_booking = Booking.objects.create(
            student=self.student,
            tutor=self.tutor,
            availability=next_availability,
            session_date=date(2026, 6, 6),
            session_mode="Online",
            session_group_id=group_id,
            status="Cancelled",
        )

        response = self.client.delete(f"/api/bookings/{first_booking.id}/dashboard-pill/")

        self.assertEqual(response.status_code, 200)
        first_booking.refresh_from_db()
        second_booking.refresh_from_db()
        self.assertIsNotNone(first_booking.dashboard_hidden_by_student_at)
        self.assertIsNotNone(second_booking.dashboard_hidden_by_student_at)
        self.assertEqual(
            sorted(response.data["hidden_booking_ids"]),
            sorted([first_booking.id, second_booking.id]),
        )

    def test_hide_dashboard_pill_rejects_active_or_completed_statuses(self):
        booking = Booking.objects.create(
            student=self.student,
            tutor=self.tutor,
            availability=self.availability,
            session_date=date(2026, 6, 6),
            session_mode="Online",
            status="Completed",
        )

        response = self.client.delete(f"/api/bookings/{booking.id}/dashboard-pill/")

        self.assertEqual(response.status_code, 400)
        booking.refresh_from_db()
        self.assertIsNone(booking.dashboard_hidden_by_student_at)

    def test_hide_dashboard_pill_rejects_unauthorized_users(self):
        booking = Booking.objects.create(
            student=self.student,
            tutor=self.tutor,
            availability=self.availability,
            session_date=date(2026, 6, 6),
            session_mode="Online",
            status="Cancelled",
        )
        other_user = User.objects.create_user(
            username="other-student",
            email="other-student@example.com",
            password="password",
        )
        UserProfile.objects.create(
            user=other_user,
            fname="Other",
            mname="",
            lname="Student",
            role="Tutee",
            year_level=11,
            course=self.course,
        )
        self.client.force_authenticate(user=other_user)

        response = self.client.delete(f"/api/bookings/{booking.id}/dashboard-pill/")

        self.assertEqual(response.status_code, 403)
        booking.refresh_from_db()
        self.assertIsNone(booking.dashboard_hidden_by_student_at)


class SessionCheckInTests(APITestCase):
    def setUp(self):
        self.course = Course.objects.create(
            course_code="CHECK101",
            course_name="Session Checks",
        )
        self.student_user = User.objects.create_user(
            username="check-student",
            email="check-student@example.com",
            password="password",
        )
        self.student = UserProfile.objects.create(
            user=self.student_user,
            fname="Check",
            mname="",
            lname="Student",
            role="Tutee",
            year_level=11,
            course=self.course,
        )
        self.tutor_user = User.objects.create_user(
            username="check-tutor",
            email="check-tutor@example.com",
            password="password",
        )
        self.tutor_profile = UserProfile.objects.create(
            user=self.tutor_user,
            fname="Check",
            mname="",
            lname="Tutor",
            role="Tutor",
            year_level=12,
            course=self.course,
        )
        self.tutor = Tutor.objects.create(
            profile=self.tutor_profile,
            hourly_rate=200,
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
            student=self.student,
            tutor=self.tutor,
            availability=self.availability,
            session_date=date(2026, 6, 15),
            session_mode="F2F",
            preferred_location="Library",
            status="Confirmed",
        )
        self.client.force_authenticate(user=self.student_user)

    def test_tutee_can_record_venue_confirmation(self):
        response = self.client.post(
            f"/api/bookings/{self.booking.id}/venue-confirmation/",
            {"response": "yes"},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["response"], "yes")
        self.assertTrue(
            SessionCheckIn.objects.filter(
                booking=self.booking,
                event_type=SessionCheckIn.EVENT_VENUE_CONFIRM,
                response="yes",
            ).exists()
        )

    def test_venue_confirmation_is_f2f_only(self):
        self.booking.session_mode = "Online"
        self.booking.save(update_fields=["session_mode"])

        response = self.client.post(
            f"/api/bookings/{self.booking.id}/venue-confirmation/",
            {"response": "yes"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(SessionCheckIn.objects.exists())

    def test_tutee_can_record_midpoint_check_in(self):
        response = self.client.post(
            f"/api/bookings/{self.booking.id}/midpoint-check-in/",
            {"response": "issues"},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["response"], "issues")
        self.assertTrue(
            SessionCheckIn.objects.filter(
                booking=self.booking,
                event_type=SessionCheckIn.EVENT_MIDPOINT_CHECKIN,
                response="issues",
            ).exists()
        )

    def test_duplicate_check_in_returns_existing_response(self):
        first = self.client.post(
            f"/api/bookings/{self.booking.id}/midpoint-check-in/",
            {"response": "good"},
            format="json",
        )
        second = self.client.post(
            f"/api/bookings/{self.booking.id}/midpoint-check-in/",
            {"response": "issues"},
            format="json",
        )

        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(second.data["response"], "good")
        self.assertEqual(
            SessionCheckIn.objects.filter(
                booking=self.booking,
                event_type=SessionCheckIn.EVENT_MIDPOINT_CHECKIN,
            ).count(),
            1,
        )

    def test_booking_detail_includes_check_in_state(self):
        SessionCheckIn.objects.create(
            booking=self.booking,
            event_type=SessionCheckIn.EVENT_VENUE_CONFIRM,
            response="no",
        )

        response = self.client.get(f"/api/bookings/{self.booking.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["check_ins"]["venue_confirm"]["response"], "no")
        self.assertIsNone(response.data["check_ins"]["midpoint_checkin"])

    def test_other_users_cannot_record_check_in(self):
        other_user = User.objects.create_user(
            username="check-other",
            email="check-other@example.com",
            password="password",
        )
        UserProfile.objects.create(
            user=other_user,
            fname="Other",
            mname="",
            lname="User",
            role="Tutee",
            year_level=11,
        )
        self.client.force_authenticate(user=other_user)

        response = self.client.post(
            f"/api/bookings/{self.booking.id}/midpoint-check-in/",
            {"response": "good"},
            format="json",
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(SessionCheckIn.objects.exists())


class DevLiveSessionTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.course = Course.objects.create(
            course_code="DEVLIVE",
            course_name="Dev Live",
        )
        self.student_user = User.objects.create_user(
            username="dev-live-student",
            email="dev-live-student@example.com",
            password="password",
        )
        self.student = UserProfile.objects.create(
            user=self.student_user,
            fname="Dev",
            mname="",
            lname="Student",
            role="Tutee",
            year_level=11,
            course=self.course,
        )
        self.tutor_user = User.objects.create_user(
            username="dev-live-tutor",
            email="dev-live-tutor@example.com",
            password="password",
        )
        self.tutor_profile = UserProfile.objects.create(
            user=self.tutor_user,
            fname="Dev",
            mname="",
            lname="Tutor",
            role="Tutor",
            year_level=12,
            course=self.course,
        )
        self.tutor = Tutor.objects.create(
            profile=self.tutor_profile,
            hourly_rate=200,
            can_online=True,
            can_f2f=True,
            teaching_level="SHS",
        )
        TutorSubjects.objects.create(
            tutor=self.tutor,
            subject=Subjects.objects.create(
                subject_code="DEV101",
                subject_name="Dev QA",
                department="QA",
            ),
            expertise_level=5,
        )
        self.availability = TutorAvailability.objects.create(
            tutor=self.tutor,
            day="Mon",
            time_slot=time(14, 0),
            is_active=True,
        )
        self.booking = Booking.objects.create(
            student=self.student,
            tutor=self.tutor,
            availability=self.availability,
            session_date=date.today() + timedelta(days=3),
            session_mode="F2F",
            preferred_location="Library",
            status="Confirmed",
        )
        self.client.force_authenticate(user=self.student_user)

    def tearDown(self):
        cache.clear()

    @override_settings(DEBUG=False)
    def test_force_live_returns_404_when_debug_is_false(self):
        response = self.client.post(
            f"/api/dev/bookings/{self.booking.id}/force-live/",
            {"phase": "start"},
            format="json",
        )

        self.assertEqual(response.status_code, 404)

    @override_settings(DEBUG=True)
    def test_force_live_rejects_unrelated_users(self):
        other_user = User.objects.create_user(
            username="dev-live-other",
            email="dev-live-other@example.com",
            password="password",
        )
        UserProfile.objects.create(
            user=other_user,
            fname="Other",
            mname="",
            lname="User",
            role="Tutee",
            year_level=11,
            course=self.course,
        )
        self.client.force_authenticate(user=other_user)

        response = self.client.post(
            f"/api/dev/bookings/{self.booking.id}/force-live/",
            {"phase": "start"},
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    @override_settings(DEBUG=True)
    def test_force_live_updates_detail_and_list_payloads(self):
        response = self.client.post(
            f"/api/dev/bookings/{self.booking.id}/force-live/",
            {"phase": "midpoint"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["session"]["status"], "Ongoing")

        list_response = self.client.get("/api/bookings/")
        self.assertEqual(list_response.status_code, 200)
        booking_payload = next(
            item for item in list_response.data if item["id"] == self.booking.id
        )

        self.assertEqual(booking_payload["status"], "Ongoing")
        self.assertEqual(str(booking_payload["date"]), response.data["session"]["date"])
        self.assertEqual(booking_payload["startTime"], response.data["session"]["start_time"])
        self.assertEqual(booking_payload["endTime"], response.data["session"]["end_time"])

    @override_settings(DEBUG=True)
    def test_tutor_can_force_and_clear_live_session(self):
        self.client.force_authenticate(user=self.tutor_user)

        force_response = self.client.post(
            f"/api/dev/bookings/{self.booking.id}/force-live/",
            {"phase": "ending"},
            format="json",
        )
        self.assertEqual(force_response.status_code, 200)
        self.assertEqual(force_response.data["session"]["status"], "Ongoing")

        clear_response = self.client.post(
            f"/api/dev/bookings/{self.booking.id}/clear-force-live/",
            format="json",
        )

        self.assertEqual(clear_response.status_code, 200)
        self.assertEqual(clear_response.data["session"]["status"], "Upcoming")


class TutorCashInTests(APITestCase):
    def setUp(self):
        self.tutor_user = User.objects.create_user(
            username="cashin-tutor",
            email="cashin-tutor@example.com",
            password="password",
        )
        self.tutor_profile = UserProfile.objects.create(
            user=self.tutor_user,
            fname="Cash",
            mname="",
            lname="In",
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
        self.wallet.balance = Decimal("-50.00")
        self.wallet.save(update_fields=["balance"])
        self.client.force_authenticate(user=self.tutor_user)

    def checkout_ok(self):
        class Resp:
            status_code = 200

            @staticmethod
            def json():
                return {
                    "data": {
                        "id": "cs_test_123",
                        "attributes": {"checkout_url": "https://pm.test/checkout/cs_test_123"},
                    }
                }
        return Resp()

    def checkout_paid(self):
        class Resp:
            status_code = 200

            @staticmethod
            def json():
                return {"data": {"attributes": {"status": "paid"}}}
        return Resp()

    def make_topup(self, status_value="pending", ref="cs_test_123", amount="100.00"):
        return WalletTopUp.objects.create(
            tutor=self.tutor,
            amount=Decimal(amount),
            status=status_value,
            provider="paymongo",
            provider_reference=ref,
        )

    def test_initiate_rejects_invalid_amount(self):
        response = self.client.post(
            "/api/wallet/cash-in/", {"amount": "0"}, format="json"
        )
        self.assertEqual(response.status_code, 400)

    def test_non_tutor_gets_403(self):
        plain = User.objects.create_user(username="plain", email="p@e.com", password="x")
        self.client.force_authenticate(user=plain)
        response = self.client.post(
            "/api/wallet/cash-in/", {"amount": "100"}, format="json"
        )
        self.assertEqual(response.status_code, 403)

    @patch("studybuddy.views.requests.post")
    def test_initiate_creates_topup_and_returns_checkout_url(self, mock_post):
        mock_post.return_value = self.checkout_ok()
        response = self.client.post(
            "/api/wallet/cash-in/", {"amount": "50.00"}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["checkout_url"], "https://pm.test/checkout/cs_test_123")
        topup = WalletTopUp.objects.get(id=response.data["id"])
        self.assertEqual(topup.status, "pending")
        self.assertEqual(topup.amount, Decimal("50.00"))
        self.assertEqual(topup.provider_reference, "cs_test_123")
        sent = mock_post.call_args.kwargs["json"]
        self.assertEqual(
            sent["data"]["attributes"]["line_items"][0]["amount"], 5000
        )

    @patch("studybuddy.views.requests.get")
    def test_verify_credits_wallet_and_writes_transaction(self, mock_get):
        mock_get.return_value = self.checkout_paid()
        topup = self.make_topup()

        response = self.client.post(f"/api/wallet/cash-in/{topup.id}/verify/")

        self.assertEqual(response.status_code, 200)
        topup.refresh_from_db()
        self.wallet.refresh_from_db()
        self.assertEqual(topup.status, "paid")
        self.assertIsNotNone(topup.paid_at)
        self.assertEqual(self.wallet.balance, Decimal("50.00"))
        self.assertTrue(
            Transaction.objects.filter(
                wallet=self.wallet,
                transaction_type="cash_in",
                amount=Decimal("100.00"),
                reference_id=f"TOPUP-{topup.id}",
            ).exists()
        )

    @patch("studybuddy.views.requests.get")
    def test_verify_is_idempotent(self, mock_get):
        mock_get.return_value = self.checkout_paid()
        topup = self.make_topup()

        first = self.client.post(f"/api/wallet/cash-in/{topup.id}/verify/")
        second = self.client.post(f"/api/wallet/cash-in/{topup.id}/verify/")

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal("50.00"))
        self.assertEqual(
            Transaction.objects.filter(reference_id=f"TOPUP-{topup.id}").count(), 1
        )

    @patch("studybuddy.views.requests.get")
    def test_verify_unpaid_returns_400_and_no_credit(self, mock_get):
        class Unpaid:
            status_code = 200

            @staticmethod
            def json():
                return {"data": {"attributes": {"status": "unpaid"}}}
        mock_get.return_value = Unpaid()
        topup = self.make_topup()

        response = self.client.post(f"/api/wallet/cash-in/{topup.id}/verify/")

        self.assertEqual(response.status_code, 400)
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal("-50.00"))
        topup.refresh_from_db()
        self.assertEqual(topup.status, "pending")


class AvatarCompressionTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="tutor_avatar",
            email="tutor_avatar@example.com",
            password="password",
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            fname="Avatar",
            mname="",
            lname="Tutor",
            role="Tutor",
            year_level=12,
        )
        Tutor.objects.create(
            profile=self.profile,
            hourly_rate=200,
            teaching_level="College",
        )
        self.client.force_authenticate(user=self.user)

    def _png_upload(self, name, size):
        from io import BytesIO
        from PIL import Image
        from django.core.files.uploadedfile import SimpleUploadedFile

        buffer = BytesIO()
        Image.new("RGB", size, (120, 80, 200)).save(buffer, format="PNG")
        buffer.seek(0)
        return SimpleUploadedFile(name, buffer.read(), content_type="image/png")

    def test_oversized_image_is_compressed_to_webp(self):
        from io import BytesIO
        from PIL import Image

        upload = self._png_upload("huge.png", (1000, 1000))
        response = self.client.post(
            "/api/tutor/profile/avatar/", {"avatar": upload}, format="multipart"
        )

        self.assertEqual(response.status_code, 200)
        self.profile.refresh_from_db()
        self.assertTrue(self.profile.profile_picture.name.endswith(".webp"))

        self.profile.profile_picture.open()
        stored = Image.open(BytesIO(self.profile.profile_picture.read()))
        self.assertEqual(stored.format, "WEBP")
        self.assertLessEqual(max(stored.size), 512)

    def test_unreadable_image_is_rejected(self):
        from django.core.files.uploadedfile import SimpleUploadedFile

        bogus = SimpleUploadedFile(
            "broken.png", b"not a real image", content_type="image/png"
        )
        response = self.client.post(
            "/api/tutor/profile/avatar/", {"avatar": bogus}, format="multipart"
        )

        self.assertEqual(response.status_code, 400)


class AdminDashboardMetricsTests(APITestCase):
    """Phase 1: institution-scoped /admin/stats metrics + operational queue."""

    def setUp(self):
        self.inst = PartnerInstitution.objects.create(
            institution_name="College of Computer Studies",
            school_email_domain="ccs.edu.ph",
            is_active=True,
        )
        self.other_inst = PartnerInstitution.objects.create(
            institution_name="Other College",
            school_email_domain="other.edu.ph",
            is_active=True,
        )

        admin_user = User.objects.create_user(
            username="inst_admin", email="admin@ccs.edu.ph", password="password"
        )
        self.admin_profile = UserProfile.objects.create(
            user=admin_user, fname="Inst", mname="", lname="Admin",
            role="Admin", institution=self.inst, year_level=16,
        )
        self.client.force_authenticate(user=admin_user)

        self.subject = Subjects.objects.create(
            subject_code="CS101", subject_name="Data Structures", department="CS"
        )

        # Tutee in-institution with a subject preference (demand)
        tutee_user = User.objects.create_user(
            username="ccs_tutee", email="tutee@ccs.edu.ph", password="password"
        )
        tutee_profile = UserProfile.objects.create(
            user=tutee_user, fname="Tess", mname="", lname="Tutee",
            role="Tutee", institution=self.inst, year_level=14,
        )
        pref = Preference.objects.create(user=tutee_profile)
        pref.subjects.add(self.subject)

        # Tutor in-institution teaching the subject (supply) + completed sessions
        tutor_user = User.objects.create_user(
            username="ccs_tutor", email="tutor@ccs.edu.ph", password="password"
        )
        tutor_profile = UserProfile.objects.create(
            user=tutor_user, fname="Tom", mname="", lname="Tutor",
            role="Tutor", institution=self.inst, year_level=16,
        )
        self.tutor = Tutor.objects.create(
            profile=tutor_profile, hourly_rate=200, teaching_level="College"
        )
        TutorSubjects.objects.create(tutor=self.tutor, subject=self.subject, expertise_level=5)

        availability = TutorAvailability.objects.create(
            tutor=self.tutor, day="Mon", time_slot=time(9, 0), is_active=True
        )
        # 1 completed + 1 cancelled this week -> completion_rate 50.0, sessions_this_week counts completed only via active_statuses
        completed = Booking.objects.create(
            student=tutee_profile, tutor=self.tutor, availability=availability,
            session_date=date.today(), session_mode="Online", status="Completed",
        )
        Booking.objects.create(
            student=tutee_profile, tutor=self.tutor, availability=availability,
            session_date=date.today(), session_mode="Online", status="Cancelled",
        )
        Rating.objects.create(
            booking=completed, student=tutee_profile, tutor=self.tutor, rating_score=5
        )

        # Operational queue items in-institution
        WithdrawalRequest.objects.create(
            tutor=self.tutor, amount=Decimal("500.00"), method="gcash", status="pending"
        )
        SupportTicket.objects.create(
            user=tutee_profile, category="Technical", subject="Cannot log in",
            description="help", status="Open",
        )

        # Out-of-institution noise that must be excluded by scoping
        other_tutor_user = User.objects.create_user(
            username="other_tutor", email="t@other.edu.ph", password="password"
        )
        other_tutor_profile = UserProfile.objects.create(
            user=other_tutor_user, fname="Olive", mname="", lname="Other",
            role="Tutor", institution=self.other_inst, year_level=16,
        )
        other_tutor = Tutor.objects.create(
            profile=other_tutor_profile, hourly_rate=200, teaching_level="College"
        )
        WithdrawalRequest.objects.create(
            tutor=other_tutor, amount=Decimal("999.00"), method="gcash", status="pending"
        )

    def test_stats_includes_institution_scoped_metrics(self):
        response = self.client.get("/api/admin/stats")
        self.assertEqual(response.status_code, 200)
        data = response.data

        self.assertEqual(data["institution_name"], "College of Computer Studies")
        self.assertEqual(data["sessions_this_week"], 1)  # only the Completed one
        self.assertEqual(data["completed_sessions"], 1)
        self.assertEqual(data["cancelled_sessions"], 1)
        self.assertEqual(data["completion_rate"], 50.0)

        self.assertTrue(any(s["subject_name"] == "Data Structures" for s in data["subject_demand"]))
        self.assertEqual(len(data["top_tutors"]), 1)
        self.assertEqual(data["top_tutors"][0]["completed_sessions"], 1)
        self.assertEqual(data["top_tutors"][0]["avg_rating"], 5.0)

    def test_operational_queue_is_scoped(self):
        response = self.client.get("/api/admin/operational-queue/")
        self.assertEqual(response.status_code, 200)
        data = response.data

        # 1 withdrawal (own inst, not the other) + 1 open ticket = 2
        self.assertEqual(data["count"], 2)
        types = {item["type"] for item in data["items"]}
        self.assertIn("withdrawal", types)
        self.assertIn("support", types)


class SupportTicketEscalationTests(APITestCase):
    def setUp(self):
        self.institution = PartnerInstitution.objects.create(
            institution_name="Central Philippine University",
            school_email_domain="cpu.edu.ph",
            is_active=True,
        )
        self.other_institution = PartnerInstitution.objects.create(
            institution_name="Other University",
            school_email_domain="other.edu.ph",
            is_active=True,
        )
        self.admin_user = User.objects.create_user(
            username="support_admin",
            email="admin@cpu.edu.ph",
            password="password",
        )
        self.admin_profile = UserProfile.objects.create(
            user=self.admin_user,
            fname="Ada",
            mname="",
            lname="Admin",
            role="Admin",
            institution=self.institution,
        )
        self.super_user = User.objects.create_user(
            username="super_support",
            email="super@studybuddy.test",
            password="password",
        )
        self.super_profile = UserProfile.objects.create(
            user=self.super_user,
            fname="Sam",
            mname="",
            lname="Super",
            role="SuperAdmin",
            profile_completed=True,
            is_domain_exempt=True,
        )
        self.tutee_user = User.objects.create_user(
            username="support_tutee",
            email="tutee@cpu.edu.ph",
            password="password",
        )
        self.tutee_profile = UserProfile.objects.create(
            user=self.tutee_user,
            fname="Tina",
            mname="",
            lname="Tutee",
            role="Tutee",
            institution=self.institution,
        )
        self.room = ChatRoom.objects.create(
            tutee=self.tutee_profile,
            tutor=self.admin_profile,
            room_type="support",
        )
        self.ticket = SupportTicket.objects.create(
            user=self.tutee_profile,
            category="Technical",
            subject="Cannot join session",
            description="The call page will not load.",
            status="In_Progress",
            assigned_agent=self.admin_profile,
            chatroom=self.room,
        )

    def test_admin_escalates_ticket_to_superadmin_queue(self):
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.post(
            f"/api/admin/support/tickets/{self.ticket.id}/escalate/",
            {"reason": "Payment records need platform access."},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.ticket.refresh_from_db()
        self.room.refresh_from_db()
        self.assertEqual(self.ticket.status, "Escalated")
        self.assertEqual(self.ticket.escalation_reason, "Payment records need platform access.")
        self.assertEqual(self.ticket.escalated_by, self.admin_profile)
        self.assertIsNotNone(self.ticket.escalated_at)
        self.assertIsNone(self.ticket.assigned_agent)
        self.assertIsNone(self.room.tutor)
        self.assertTrue(
            Message.objects.filter(
                room=self.room,
                sender=None,
                content="This support ticket has been escalated to SuperAdmin support.",
            ).exists()
        )

        admin_list = self.client.get("/api/admin/support/tickets/")
        self.assertNotIn(self.ticket.id, [ticket["id"] for ticket in admin_list.data])

        self.client.force_authenticate(user=self.super_user)
        super_list = self.client.get("/api/admin/support/tickets/")
        escalated_ticket = next(ticket for ticket in super_list.data if ticket["id"] == self.ticket.id)
        self.assertEqual(escalated_ticket["status"], "Escalated")
        self.assertEqual(escalated_ticket["escalation_reason"], "Payment records need platform access.")

    def test_escalation_requires_reason_and_institution_scope(self):
        self.client.force_authenticate(user=self.admin_user)

        missing_reason = self.client.post(
            f"/api/admin/support/tickets/{self.ticket.id}/escalate/",
            {"reason": "   "},
            format="json",
        )

        self.assertEqual(missing_reason.status_code, 400)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, "In_Progress")

        other_admin_user = User.objects.create_user(
            username="other_admin",
            email="admin@other.edu.ph",
            password="password",
        )
        UserProfile.objects.create(
            user=other_admin_user,
            fname="Omar",
            mname="",
            lname="Admin",
            role="Admin",
            institution=self.other_institution,
        )
        self.client.force_authenticate(user=other_admin_user)

        cross_institution = self.client.post(
            f"/api/admin/support/tickets/{self.ticket.id}/escalate/",
            {"reason": "Needs platform review."},
            format="json",
        )

        self.assertEqual(cross_institution.status_code, 404)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, "In_Progress")

    def test_superadmin_claims_and_resolves_escalated_ticket(self):
        self.client.force_authenticate(user=self.admin_user)
        self.client.post(
            f"/api/admin/support/tickets/{self.ticket.id}/escalate/",
            {"reason": "Needs platform review."},
            format="json",
        )

        admin_resolve = self.client.post(f"/api/admin/support/tickets/{self.ticket.id}/resolve/")
        self.assertEqual(admin_resolve.status_code, 403)

        self.client.force_authenticate(user=self.super_user)
        claim = self.client.post(f"/api/admin/support/tickets/{self.ticket.id}/claim/")
        self.assertEqual(claim.status_code, 200)
        self.ticket.refresh_from_db()
        self.room.refresh_from_db()
        self.assertEqual(self.ticket.status, "Escalated")
        self.assertEqual(self.ticket.assigned_agent, self.super_profile)
        self.assertEqual(self.room.tutor, self.super_profile)

        resolve = self.client.post(f"/api/admin/support/tickets/{self.ticket.id}/resolve/")
        self.assertEqual(resolve.status_code, 200)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, "Resolved")


class InstitutionScopedMatchingTests(APITestCase):
    def setUp(self):
        cache.clear()

        self.inst_a = PartnerInstitution.objects.create(
            institution_name="Central Philippine University",
            school_email_domain="cpu.edu.ph",
            is_active=True,
            contact_person="Registrar",
        )
        self.inst_b = PartnerInstitution.objects.create(
            institution_name="Western Visayas University",
            school_email_domain="wvu.edu.ph",
            is_active=True,
            contact_person="Registrar",
        )
        self.subject = Subjects.objects.create(
            subject_code="SCOPE101",
            subject_name="Scoping Test Subject",
            department="Test",
        )

        # Tutee from inst_a
        tutee_user = User.objects.create_user(
            username="scope_tutee_a", email="tutee@cpu.edu.ph", password="pass"
        )
        self.tutee = UserProfile.objects.create(
            user=tutee_user, fname="Ana", mname="", lname="Cruz",
            role="Tutee", institution=self.inst_a,
        )

        # Tutor from inst_a
        tutor_a_user = User.objects.create_user(
            username="scope_tutor_a", email="tutor_a@cpu.edu.ph", password="pass"
        )
        tutor_a_profile = UserProfile.objects.create(
            user=tutor_a_user, fname="Ben", mname="", lname="Santos",
            role="Tutor", institution=self.inst_a,
        )
        self.tutor_a = Tutor.objects.create(
            profile=tutor_a_profile, hourly_rate=250,
            can_online=True, can_f2f=True, teaching_level="SHS",
        )
        TutorSubjects.objects.create(
            tutor=self.tutor_a, subject=self.subject, expertise_level=5
        )

        # Tutor from inst_b
        tutor_b_user = User.objects.create_user(
            username="scope_tutor_b", email="tutor_b@wvu.edu.ph", password="pass"
        )
        tutor_b_profile = UserProfile.objects.create(
            user=tutor_b_user, fname="Cal", mname="", lname="Ramos",
            role="Tutor", institution=self.inst_b,
        )
        self.tutor_b = Tutor.objects.create(
            profile=tutor_b_profile, hourly_rate=250,
            can_online=True, can_f2f=True, teaching_level="SHS",
        )
        TutorSubjects.objects.create(
            tutor=self.tutor_b, subject=self.subject, expertise_level=5
        )

        # Tutor with no institution
        tutor_null_user = User.objects.create_user(
            username="scope_tutor_null", email="tutor_null@example.com", password="pass"
        )
        tutor_null_profile = UserProfile.objects.create(
            user=tutor_null_user, fname="Dan", mname="", lname="Lee",
            role="Tutor", institution=None,
        )
        self.tutor_null = Tutor.objects.create(
            profile=tutor_null_profile, hourly_rate=250,
            can_online=True, can_f2f=True, teaching_level="SHS",
        )
        TutorSubjects.objects.create(
            tutor=self.tutor_null, subject=self.subject, expertise_level=5
        )

    def _set_preferences(self, *subjects):
        pref, _ = Preference.objects.get_or_create(user=self.tutee)
        pref.subjects.set([s.subject_code for s in subjects])

    def test_helper_filters_by_institution(self):
        from .recommender.utils import filter_tutors_by_institution
        qs = filter_tutors_by_institution(Tutor.objects.all(), self.tutee)
        self.assertIn(self.tutor_a, qs)
        self.assertNotIn(self.tutor_b, qs)
        self.assertNotIn(self.tutor_null, qs)

    def test_helper_returns_empty_when_tutee_has_no_institution(self):
        from .recommender.utils import filter_tutors_by_institution
        no_inst_user = User.objects.create_user(
            username="scope_no_inst", email="noinst@test.com", password="pass"
        )
        no_inst_tutee = UserProfile.objects.create(
            user=no_inst_user, fname="No", mname="", lname="Inst",
            role="Tutee", institution=None,
        )
        qs = filter_tutors_by_institution(Tutor.objects.all(), no_inst_tutee)
        self.assertFalse(qs.exists())

    def test_recommend_returns_same_institution_tutors(self):
        self.client.force_authenticate(user=self.tutee.user)
        resp = self.client.post(
            "/api/recommend-tutors/",
            {"subject": "SCOPE101"},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        ids = {r["id"] for r in resp.data}
        self.assertIn(self.tutor_a.profile.id, ids)

    def test_recommend_excludes_other_institution_tutor(self):
        self.client.force_authenticate(user=self.tutee.user)
        resp = self.client.post(
            "/api/recommend-tutors/",
            {"subject": "SCOPE101"},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        ids = {r["id"] for r in resp.data}
        self.assertNotIn(self.tutor_b.profile.id, ids)

    def test_recommend_tutee_no_institution_gets_empty_list(self):
        no_inst_user = User.objects.create_user(
            username="scope_no_inst2", email="noinst2@test.com", password="pass"
        )
        UserProfile.objects.create(
            user=no_inst_user, fname="No", mname="", lname="Inst",
            role="Tutee", institution=None,
        )
        self.client.force_authenticate(user=no_inst_user)
        resp = self.client.post(
            "/api/recommend-tutors/",
            {"subject": "SCOPE101"},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data, [])

    def test_recommend_null_institution_tutor_not_shown(self):
        self.client.force_authenticate(user=self.tutee.user)
        resp = self.client.post(
            "/api/recommend-tutors/",
            {"subject": "SCOPE101"},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        ids = {r["id"] for r in resp.data}
        self.assertNotIn(self.tutor_null.profile.id, ids)

    def test_dashboard_widget_respects_institution(self):
        from studybuddy.recommender import dashboard
        self._set_preferences(self.subject)
        data = dashboard.get_dashboard_recommendations(self.tutee)
        ids = {row["id"] for row in data}
        self.assertNotIn(self.tutor_b.profile.id, ids)
        self.assertNotIn(self.tutor_null.profile.id, ids)

    def test_dashboard_fallback_respects_institution(self):
        from studybuddy.recommender import dashboard
        # tutee has no preferences set, so get_student_subject_codes returns []
        # and the code falls through to _fallback
        data = dashboard.get_dashboard_recommendations(self.tutee)
        ids = {row["id"] for row in data}
        self.assertNotIn(self.tutor_b.profile.id, ids)
        self.assertNotIn(self.tutor_null.profile.id, ids)

    def test_search_tutors_respects_institution(self):
        self.client.force_authenticate(user=self.tutee.user)
        resp = self.client.get("/api/search-tutors/", {"subject": "SCOPE101"})
        self.assertEqual(resp.status_code, 200)
        ids = {r["profile_id"] for r in resp.data}
        self.assertIn(self.tutor_a.profile.id, ids)
        self.assertNotIn(self.tutor_b.profile.id, ids)
        self.assertNotIn(self.tutor_null.profile.id, ids)

    def test_search_tutors_requires_authentication(self):
        resp = self.client.get("/api/search-tutors/", {"subject": "SCOPE101"})
        self.assertEqual(resp.status_code, 401)
