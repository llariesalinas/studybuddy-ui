from datetime import date, time
from decimal import Decimal
from unittest.mock import Mock, patch
from uuid import uuid4

from django.contrib.auth.models import User
from django.test import override_settings
from rest_framework.test import APITestCase

from .chat.services import get_current_booking_context, get_partner_context
from .models import (
    Booking,
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
