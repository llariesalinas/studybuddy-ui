import json
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.utils.timezone import now
from django.db import transaction
from datetime import datetime,timedelta, date
from calendar import monthrange
from uuid import uuid4
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from django.utils.timezone import now
from django.db.models import Avg, Case, When, Value, IntegerField, Q
from collections import defaultdict
# algo
from .recommender.hybrid import recommend_tutors_hybrid
from .recommender.CF import build_rating_matrix

from .recommender.cbf import recommend_tutors
from .models import Booking, Course, Notification, PartnerInstitution, Payment, PaymentMethod, Preference, Rating, Subjects, Tutor, TutorAvailability, TutorAvailabilityOverride, TutorSubjects
from .serializers import (
    NotificationSerializer,
    SubjectSerializer,
    TutorDetailSerializer,
    TutorAvailabilityOverrideSerializer,
    TutorProfileSerializer,
    TutorProfileUpdateSerializer,
    TutorSearchSerializer,
)

from .models import (
    UserProfile,
    Booking,
    PartnerInstitution,
    Tutor,
    TutorSubjects
)
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from .models import UserProfile, Tutor


def normalize_email_domain(email):
    if not email or '@' not in email:
        return None

    return email.split('@', 1)[1].strip().lower()


def normalize_stored_domain(domain):
    if not domain:
        return None

    return domain.strip().lower().lstrip('@')


def get_active_institution_by_domain(domain):
    normalized_domain = normalize_stored_domain(domain)

    if not normalized_domain:
        return None

    return PartnerInstitution.objects.filter(
        school_email_domain__iexact=normalized_domain,
        is_active=True
    ).first()


WEEKDAY_MAP = {
    0: "Mon",
    1: "Tue",
    2: "Wed",
    3: "Thu",
    4: "Fri",
    5: "Sat",
    6: "Sun",
}

SESSION_SLOT_MINUTES = 30


def get_duration_hours_from_slot_count(slot_count):
    return round((slot_count * SESSION_SLOT_MINUTES) / 60, 2)


def get_duration_hours_for_bookings(bookings):
    return get_duration_hours_from_slot_count(len(bookings))

def parse_request_date(date_string):
    try:
        return datetime.strptime(date_string, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


def get_override_maps(tutor, start_date, end_date):
    overrides = TutorAvailabilityOverride.objects.filter(
        tutor=tutor,
        override_date__range=(start_date, end_date)
    ).select_related('availability')

    full_day_dates = {
        override.override_date
        for override in overrides
        if override.is_full_day
    }

    slot_override_keys = {
        (override.availability_id, override.override_date)
        for override in overrides
        if not override.is_full_day and override.availability_id is not None
    }

    return full_day_dates, slot_override_keys


def has_confirmed_or_completed_booking_conflict(tutor, override_date, availability=None):
    booking_filter = Booking.objects.filter(
        tutor=tutor,
        session_date=override_date,
        status__in=["Confirmed", "Completed"]
    )

    if availability is not None:
        booking_filter = booking_filter.filter(availability=availability)

    return booking_filter.exists()


def slot_is_overridden(tutor, override_date, availability):
    return TutorAvailabilityOverride.objects.filter(
        tutor=tutor,
        override_date=override_date
    ).filter(
        Q(is_full_day=True) | Q(availability=availability)
    ).exists()

def get_booking_end_time(booking):
    return (
        datetime.combine(booking.session_date, booking.availability.time_slot)
        + timedelta(minutes=SESSION_SLOT_MINUTES)
    ).time()


def sort_bookings_for_session_group(bookings):
    return sorted(
        bookings,
        key=lambda booking: (booking.session_date, booking.availability.time_slot, booking.id)
    )


def group_slot_requests(slot_requests):
    grouped_slots = []
    current_group = []
    previous_slot = None

    for slot_request in slot_requests:
        if not current_group:
            current_group = [slot_request]
            previous_slot = slot_request
            continue

        previous_end = (
            datetime.combine(previous_slot["session_date"], previous_slot["availability"].time_slot)
            + timedelta(minutes=SESSION_SLOT_MINUTES)
        ).time()

        if (
            previous_slot["session_date"] == slot_request["session_date"]
            and previous_end == slot_request["availability"].time_slot
        ):
            current_group.append(slot_request)
        else:
            grouped_slots.append(current_group)
            current_group = [slot_request]

        previous_slot = slot_request

    if current_group:
        grouped_slots.append(current_group)

    return grouped_slots


def get_session_group_bookings(booking):
    if booking.session_group_id is None:
        booking_group = [booking]
    else:
        booking_group = list(
            Booking.objects.filter(session_group_id=booking.session_group_id)
            .select_related(
                'student__course',
                'tutor__profile__course',
                'tutor__profile__user',
                'availability',
                'payment__method',
                'rating'
            )
            .order_by('session_date', 'availability__time_slot', 'id')
        )

    return sort_bookings_for_session_group(booking_group)


def get_booking_request_bookings(booking):
    if booking.booking_request_id is None:
        return get_session_group_bookings(booking)

    booking_group = list(
        Booking.objects.filter(booking_request_id=booking.booking_request_id)
        .select_related(
            'student__course',
            'tutor__profile__course',
            'tutor__profile__user',
            'availability',
            'payment__method',
            'rating'
        )
        .order_by('session_date', 'availability__time_slot', 'id')
    )

    return sort_bookings_for_session_group(booking_group)


def get_representative_booking(bookings):
    sorted_group = sort_bookings_for_session_group(bookings)
    return sorted_group[0] if sorted_group else None


def get_session_notification_context(bookings):
    representative_booking = get_representative_booking(bookings)

    if not representative_booking:
        return {
            "subject": "session",
            "date": "an upcoming date",
            "tutor_name": "your tutor",
            "tutee_name": "the tutee",
        }

    subject = (
        representative_booking.tutor.profile.course.course_name
        if representative_booking.tutor.profile.course else "General"
    )
    date_label = representative_booking.session_date.strftime("%Y-%m-%d")
    tutor_name = f"{representative_booking.tutor.profile.fname} {representative_booking.tutor.profile.lname}"
    tutee_name = f"{representative_booking.student.fname} {representative_booking.student.lname}"

    return {
        "subject": subject,
        "date": date_label,
        "tutor_name": tutor_name,
        "tutee_name": tutee_name,
    }


def get_display_status(raw_status, session_date, start_time, end_time):
    normalized = str(raw_status or '').lower()

    if normalized == 'confirmed':
        timezone_now = timezone.localtime()
        timezone_info = timezone.get_current_timezone()
        start_at = timezone.make_aware(datetime.combine(session_date, start_time), timezone_info)
        end_at = timezone.make_aware(datetime.combine(session_date, end_time), timezone_info)

        if timezone_now < start_at:
            return 'Upcoming'

        if start_at <= timezone_now < end_at:
            return 'Ongoing'

        return 'Payment Required'

    if normalized == 'awaiting payment verification':
        return 'Awaiting Verification'

    return raw_status


def create_booking_status_notification(recipient, status_key, bookings, recipient_role=None):
    context = get_session_notification_context(bookings)

    messages = {
        "pending": f"New booking request received for {context['subject']} on {context['date']}. Please review and respond.",
        "confirmed": f"Your booking for {context['subject']} with {context['tutor_name']} has been accepted. The session is now upcoming.",
        "rejected": f"Your booking for {context['subject']} with {context['tutor_name']} on {context['date']} was rejected.",
        "awaiting_payment_verification": f"A tutee has confirmed their {context['subject']} session on {context['date']} and sent payment for review.",
        "completed": f"Your session for {context['subject']} with {context['tutor_name']} was marked complete. You can rate it anytime.",
    }

    if status_key == "cancelled":
        if recipient_role == "tutor":
            message = f"{context['tutee_name']} has cancelled your {context['subject']} session on {context['date']}."
        elif recipient_role == "tutee":
            message = f"Your {context['subject']} session on {context['date']} has been successfully cancelled"
        else:
            message = None
    else:
        message = messages.get(status_key)

    if not message:
        return

    Notification.objects.create(
        recipient=recipient,
        message=message
    )


def update_tutor_rating_average(tutor):
    aggregate = Rating.objects.filter(tutor=tutor).aggregate(average=Avg('rating_score'))
    tutor.rating_average = round(aggregate['average'] or 0, 2)
    tutor.save(update_fields=['rating_average'])


def get_payment_method_code(payment):
    return getattr(getattr(payment, 'method', None), 'code', None)


def get_payment_method_label(payment):
    method = getattr(payment, 'method', None)

    if not method:
        return None

    if method.code in {'GCASH', 'BANK', 'online'}:
        return 'Online Payment'

    return method.method_name


def serialize_payment_summary(representative_booking):
    payment = getattr(representative_booking, 'payment', None)

    if not payment:
        return {
            "transaction_id": None,
            "method": None,
            "amount_paid": 0,
            "tutor_earned": 0,
            "platform_fee": 0,
            "transaction_fee": 0,
            "status": "Pending",
            "receipt_image": None,
        }

    amount_paid = float(payment.amount)
    method = get_payment_method_label(payment)
    method_code = get_payment_method_code(payment)
    platform_fee = round(amount_paid * 0.16, 2)

    if method_code == "GCASH":
        transaction_fee = round(amount_paid * 0.04, 2)
    else:
        transaction_fee = 0

    tutor_earned = round(amount_paid - platform_fee - transaction_fee, 2)

    return {
        "transaction_id": payment.transaction_reference,
        "method": method,
        "amount_paid": amount_paid,
        "tutor_earned": tutor_earned,
        "platform_fee": platform_fee,
        "transaction_fee": transaction_fee,
        "status": payment.payment_status,
        "receipt_image": payment.receipt_image.url if payment.receipt_image else None,
    }
@api_view(['GET'])
def partner_institutions_list(request):

    institutions = PartnerInstitution.objects.filter(is_active=True).order_by('institution_name')

    data = [
        {
            "id": institution.id,
            "institution_name": institution.institution_name,
            "school_email_domain": normalize_stored_domain(institution.school_email_domain),
            "contact_person": institution.contact_person
        }
        for institution in institutions
    ]

    return Response(data)


@api_view(['POST'])
def register_user(request):

    email = request.data.get('email')
    password = request.data.get('password')
    fname = request.data.get('fname')
    mname = request.data.get('mname', '')
    lname = request.data.get('lname')
    role = request.data.get('role')
    institution_id = request.data.get('institution_id')

    # Validate required fields
    if not all([email, password, fname, lname, role, institution_id]):
        return Response(
            {"error": "Missing required fields"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        institution = PartnerInstitution.objects.get(id=institution_id, is_active=True)
    except PartnerInstitution.DoesNotExist:
        return Response(
            {"error": "Your institution is not a registered partner. Please contact support."},
            status=status.HTTP_400_BAD_REQUEST
        )

    email_domain = normalize_email_domain(email)
    institution_domain = normalize_stored_domain(institution.school_email_domain)

    if email_domain != institution_domain:
        return Response(
            {"error": "Your email domain does not match the selected institution. Please check and try again."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Prevent duplicate users
    if User.objects.filter(username=email).exists():
        return Response(
            {"error": "User already exists"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Create Django User
    user = User.objects.create_user(
        username=email,
        email=email,
        password=password
    )

    # Create UserProfile
    profile = UserProfile.objects.create(
        user=user,
        fname=fname,
        mname=mname,
        lname=lname,
        role=role,
        institution=institution
    )

    # 🔥 Create Tutor record if role is Tutor
    if role == "Tutor":
        Tutor.objects.create(profile=profile)

    return Response(
        {"message": "User registered successfully"},
        status=status.HTTP_201_CREATED
    )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_status(request):

    profile = request.user.userprofile

    return Response({
        "profile_completed": profile.profile_completed,
        "role": profile.role
    })

@api_view(['POST'])
def login_view(request):

    email = request.data.get("email")
    password = request.data.get("password")

    if not email or not password:
        return Response(
            {"error": "Email and password required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 🔥 authenticate using email as username
    user = authenticate(username=email, password=password)

    if user is None:
        return Response(
            {"error": "Invalid credentials"},
            status=status.HTTP_401_UNAUTHORIZED
        )

    refresh = RefreshToken.for_user(user)
    try:
        profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        return Response(
            {"error": "User profile not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    if not profile.is_domain_exempt:
        email_domain = normalize_email_domain(email)
        active_institution = get_active_institution_by_domain(email_domain)

        if active_institution is None:
            institution = profile.institution

            if institution and not institution.is_active:
                return Response(
                    {"error": "Your institution's access has been suspended. Please contact support."},
                    status=status.HTTP_403_FORBIDDEN
                )

            return Response(
                {"error": "Your institution is not a registered partner. Please contact support."},
                status=status.HTTP_403_FORBIDDEN
            )

        profile_domain = (
            normalize_stored_domain(profile.institution.school_email_domain)
            if profile.institution
            else None
        )

        if profile.institution_id and profile_domain != email_domain:
            return Response(
                {"error": "Your email domain does not match your registered institution. Please contact support."},
                status=status.HTTP_403_FORBIDDEN
            )

        if profile.institution_id != active_institution.id:
            profile.institution = active_institution
            profile.save(update_fields=['institution', 'updated_at'])

    return Response({
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "role": profile.role,
        "user_id": profile.id,
        "email": user.email,
        "fname": profile.fname,
        "lname": profile.lname
    })


@api_view(['GET'])
def list_courses(request):

    courses = Course.objects.all()

    data = [
        {
            "course_code": c.course_code,
            "course_name": c.course_name
        }
        for c in courses
    ]

    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_dashboard(request):

    user_profile = UserProfile.objects.get(user=request.user)

    today = now().date()

    # -----------------------
    # UPCOMING SESSIONS
    # -----------------------
    upcoming_bookings = Booking.objects.filter(
        student=user_profile,
        status='Confirmed',
        session_date__gte=today
    ).select_related(
        'tutor__profile__course',
        'availability'
    ).order_by('session_date', 'availability__time_slot')

    grouped_upcoming = defaultdict(list)

    for b in upcoming_bookings:
        grouped_upcoming[b.session_date].append(b)

    upcoming = []

    for session_date, day_bookings in grouped_upcoming.items():

        day_bookings.sort(key=lambda b: b.availability.time_slot)

        current_group = [day_bookings[0]]

        for booking in day_bookings[1:]:

            prev = current_group[-1]

            prev_end = (
                datetime.combine(session_date, prev.availability.time_slot)
                + timedelta(minutes=SESSION_SLOT_MINUTES)
            ).time()

            if booking.availability.time_slot == prev_end and booking.status == prev.status:
                current_group.append(booking)
            else:
                block = build_combined_block(current_group)

                upcoming.append({
                    "id": block["id"],
                    "subject": block["subject"],
                    "tutor": f"{current_group[0].tutor.profile.fname} {current_group[0].tutor.profile.lname}",
                    "date": block["date"].strftime("%Y-%m-%d"),
                    "time": f'{block["startTime"]} – {block["endTime"]}'
                })

                current_group = [booking]

        block = build_combined_block(current_group)

        upcoming.append({
            "id": block["id"],
            "subject": block["subject"],
            "tutor": f"{current_group[0].tutor.profile.fname} {current_group[0].tutor.profile.lname}",
            "date": block["date"].strftime("%Y-%m-%d"),
            "time": f'{block["startTime"]} – {block["endTime"]}'
        })

    # -----------------------
    # COMPLETED SESSIONS
    # -----------------------
    completed_bookings = Booking.objects.filter(
        student=user_profile,
        status='Completed'
    ).select_related(
        'tutor__profile__course',
        'availability'
    ).order_by('-session_date', 'availability__time_slot')

    grouped_completed = defaultdict(list)

    for b in completed_bookings:
        grouped_completed[b.session_date].append(b)

    completed = []

    for session_date, day_bookings in grouped_completed.items():

        day_bookings.sort(key=lambda b: b.availability.time_slot)

        current_group = [day_bookings[0]]

        for booking in day_bookings[1:]:

            prev = current_group[-1]

            prev_end = (
                datetime.combine(session_date, prev.availability.time_slot)
                + timedelta(minutes=SESSION_SLOT_MINUTES)
            ).time()

            if booking.availability.time_slot == prev_end and booking.status == prev.status:
                current_group.append(booking)
            else:
                block = build_combined_block(current_group)

                completed.append({
                    "id": block["id"],
                    "subject": block["subject"],
                    "tutor": f"{current_group[0].tutor.profile.fname} {current_group[0].tutor.profile.lname}",
                    "date": block["date"].strftime("%Y-%m-%d"),
                    "time": f'{block["startTime"]} – {block["endTime"]}'
                })

                current_group = [booking]

        block = build_combined_block(current_group)

        completed.append({
            "id": block["id"],
            "subject": block["subject"],
            "tutor": f"{current_group[0].tutor.profile.fname} {current_group[0].tutor.profile.lname}",
            "date": block["date"].strftime("%Y-%m-%d"),
            "time": f'{block["startTime"]} – {block["endTime"]}'
        })

    # -----------------------
    # RECOMMENDED TUTORS
    # -----------------------
    tutors = Tutor.objects.all().select_related('profile')[:3]

    recommendations = []

    for tutor in tutors:

        tutor_subjects = TutorSubjects.objects.filter(
            tutor=tutor
        ).select_related('subject')

        recommendations.append({
            "id": tutor.profile.id,
            "name": f"{tutor.profile.fname} {tutor.profile.lname}",
            "rating": tutor.rating_average,
            "subjects": [ts.subject.subject_name for ts in tutor_subjects],
            "hourlyRate": tutor.hourly_rate
        })

    return Response({
        "upcoming": upcoming,
        "completed": completed,
        "recommendations": recommendations
    })

#SearchTutors

class SearchTutorsView(APIView):

    def get(self, request):
        subject_code = request.query_params.get('subject')

        if not subject_code:
            return Response(
                {"error": "Subject is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        tutors = Tutor.objects.filter(
            tutorsubjects__subject__subject_code=subject_code
        ).select_related('profile').distinct()

        serializer = TutorSearchSerializer(tutors, many=True)
        return Response(serializer.data)
#Subject Serializer

class SubjectListView(ListAPIView):
    queryset = Subjects.objects.all()
    serializer_class = SubjectSerializer    



def build_combined_block(group):

    sorted_group = sort_bookings_for_session_group(group)
    first = sorted_group[0]
    last = sorted_group[-1]
    representative_booking = get_representative_booking(sorted_group)

    start_time = first.availability.time_slot

    end_time = (
        datetime.combine(first.session_date, last.availability.time_slot)
        + timedelta(minutes=SESSION_SLOT_MINUTES)
    ).time()

    duration = get_duration_hours_for_bookings(sorted_group)

    # ensure correct status
    group_status = first.status
    display_status = get_display_status(
        group_status,
        first.session_date,
        start_time,
        end_time
    )
    return {
        "id": representative_booking.id,
        "session_group_id": str(representative_booking.session_group_id) if representative_booking.session_group_id else None,
        "booking_request_id": str(representative_booking.booking_request_id) if representative_booking.booking_request_id else None,
        "status": display_status,
        "raw_status": group_status,
        "date": first.session_date,
        "student": f"{first.student.fname} {first.student.lname}",
        "tuteeName": f"{first.student.fname} {first.student.lname}",
        "tutor": f"{first.tutor.profile.fname} {first.tutor.profile.lname}",
        "tutee_confirmed": representative_booking.tutee_confirmed,
        "tutor_confirmed": representative_booking.tutor_confirmed,
        "rating": representative_booking.rating.rating_score if hasattr(representative_booking, "rating") else None,
        "rating_submitted": hasattr(representative_booking, "rating"),

        "subject": (
            first.tutor.profile.course.course_name
            if first.tutor.profile.course
            else "General"
        ),
        "startTime": start_time.strftime("%H:%M"),
        "endTime": end_time.strftime("%H:%M"),
        "duration_hours": duration
    }


def build_time_block_payload(bookings):

    sorted_bookings = sort_bookings_for_session_group(bookings)
    first_booking = sorted_bookings[0]
    last_booking = sorted_bookings[-1]

    start_time = first_booking.availability.time_slot
    end_time = (
        datetime.combine(first_booking.session_date, last_booking.availability.time_slot)
        + timedelta(minutes=SESSION_SLOT_MINUTES)
    ).time()

    return {
        "date": first_booking.session_date.strftime("%Y-%m-%d"),
        "startTime": start_time.strftime("%H:%M"),
        "endTime": end_time.strftime("%H:%M"),
        "duration_hours": get_duration_hours_for_bookings(sorted_bookings),
        "session_group_id": str(first_booking.session_group_id) if first_booking.session_group_id else None,
    }


def split_bookings_into_time_blocks(bookings):

    sorted_bookings = sort_bookings_for_session_group(bookings)

    if not sorted_bookings:
        return []

    grouped_blocks = []
    current_block = [sorted_bookings[0]]

    for booking in sorted_bookings[1:]:
        previous_booking = current_block[-1]
        previous_end = (
            datetime.combine(previous_booking.session_date, previous_booking.availability.time_slot)
            + timedelta(minutes=SESSION_SLOT_MINUTES)
        ).time()

        same_session_group = (
            previous_booking.session_group_id is not None
            and booking.session_group_id is not None
            and previous_booking.session_group_id == booking.session_group_id
        )
        is_contiguous = (
            previous_booking.session_date == booking.session_date
            and previous_end == booking.availability.time_slot
        )

        if same_session_group or is_contiguous:
            current_block.append(booking)
            continue

        grouped_blocks.append(current_block)
        current_block = [booking]

    grouped_blocks.append(current_block)

    return [build_time_block_payload(block) for block in grouped_blocks]


def build_booking_request_block(group):

    sorted_group = sort_bookings_for_session_group(group)
    representative_booking = get_representative_booking(sorted_group)
    first_booking = sorted_group[0]
    time_blocks = split_bookings_into_time_blocks(sorted_group)
    primary_block = time_blocks[0]
    group_status = first_booking.status

    return {
        "id": representative_booking.id,
        "session_group_id": str(representative_booking.session_group_id) if representative_booking.session_group_id else None,
        "booking_request_id": str(representative_booking.booking_request_id) if representative_booking.booking_request_id else None,
        "status": group_status,
        "raw_status": group_status,
        "date": first_booking.session_date,
        "student": f"{first_booking.student.fname} {first_booking.student.lname}",
        "tuteeName": f"{first_booking.student.fname} {first_booking.student.lname}",
        "tutor": f"{first_booking.tutor.profile.fname} {first_booking.tutor.profile.lname}",
        "tutee_confirmed": representative_booking.tutee_confirmed,
        "tutor_confirmed": representative_booking.tutor_confirmed,
        "rating": representative_booking.rating.rating_score if hasattr(representative_booking, "rating") else None,
        "rating_submitted": hasattr(representative_booking, "rating"),
        "subject": (
            first_booking.tutor.profile.course.course_name
            if first_booking.tutor.profile.course
            else "General"
        ),
        "startTime": primary_block["startTime"],
        "endTime": primary_block["endTime"],
        "duration_hours": get_duration_hours_for_bookings(sorted_group),
        "timeBlocks": time_blocks,
        "hasMultipleTimeBlocks": len(time_blocks) > 1,
    }

#Tutor Dashboard View

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def tutor_dashboard(request):

    profile = request.user.userprofile

    try:
        tutor = Tutor.objects.get(profile=profile)
    except Tutor.DoesNotExist:
        return Response({"error": "Tutor not found"}, status=404)

    # 📌 Completed sessions for earnings
    completed_bookings = Booking.objects.filter(
        tutor=tutor,
        status="Completed"
    ).select_related("payment", "payment__method")

    total_earnings = 0

    for b in completed_bookings:

        if hasattr(b, "payment") and b.payment:

            amount = float(b.payment.amount)

            platform_fee = amount * 0.16

            method_code = get_payment_method_code(b.payment)

            if method_code == "GCASH":
                transaction_fee = amount * 0.04
            else:
                transaction_fee = 0

            tutor_earned = amount - platform_fee - transaction_fee

            total_earnings += tutor_earned

    # 📌 Upcoming confirmed bookings
    upcoming = Booking.objects.filter(
        tutor=tutor,
        status="Confirmed",
        session_date__gte=timezone.now()
    ).select_related(
        "student",
        "tutor__profile__course",
        "availability"
    ).order_by("session_date", "availability__time_slot")

    # 🔥 GROUP BOOKINGS
    grouped_by_date = defaultdict(list)

    for b in upcoming:
        grouped_by_date[b.session_date].append(b)

    bookings_data = []

    for session_date, day_bookings in grouped_by_date.items():

        day_bookings.sort(key=lambda b: b.availability.time_slot)

        current_group = [day_bookings[0]]

        for booking in day_bookings[1:]:

            prev = current_group[-1]

            prev_end = (
                datetime.combine(session_date, prev.availability.time_slot)
                + timedelta(minutes=SESSION_SLOT_MINUTES)
            ).time()

            if booking.availability.time_slot == prev_end and booking.status == prev.status:
                current_group.append(booking)
            else:
                bookings_data.append(build_combined_block(current_group))
                current_group = [booking]

        bookings_data.append(build_combined_block(current_group))

    return Response({
        "total_sessions": tutor.total_sessions,
        "rating_average": tutor.rating_average,
        "hourly_rate": tutor.hourly_rate,
        "total_earnings": round(total_earnings, 2),
        "upcoming_bookings": bookings_data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_tutor_profile(request):

    profile = request.user.userprofile

    try:
        tutor = Tutor.objects.select_related(
            'profile__user',
            'profile__course',
            'pinned_review__student'
        ).get(profile=profile)
    except Tutor.DoesNotExist:
        return Response({"error": "Tutor not found"}, status=404)

    serializer = TutorProfileSerializer(tutor)
    return Response(serializer.data)

#Tutor Detail View
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def tutor_detail(request, profile_id):
    try:
        tutor = Tutor.objects.select_related(
            'profile',
            'pinned_review__student'
        ).prefetch_related(
            'tutorsubjects_set__subject'
        ).get(profile_id=profile_id)
    except Tutor.DoesNotExist:
        return Response({"error": "Tutor not found"}, status=404)

    serializer = TutorDetailSerializer(tutor)
    return Response(serializer.data)

#tutor availability schedule thing  vview

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def tutor_availability(request, tutor_id):

    tutor = get_object_or_404(Tutor, profile_id=tutor_id)
    today = date.today()
    month_offset = int(request.GET.get("month_offset", 0))

    total_months = (today.year * 12) + (today.month - 1) + month_offset
    target_year = total_months // 12
    target_month = (total_months % 12) + 1

    month_start = date(target_year, target_month, 1)
    month_end = date(target_year, target_month, monthrange(target_year, target_month)[1])

    calendar_start = month_start - timedelta(days=month_start.weekday())
    calendar_end = month_end + timedelta(days=(6 - month_end.weekday()))

    availability = TutorAvailability.objects.filter(
        tutor=tutor,
        is_active=True
    )

    relevant_bookings = Booking.objects.filter(
        tutor=tutor,
        session_date__range=(calendar_start, calendar_end),
        status__in=["Confirmed", "Pending", "Completed"]
    )
    full_day_dates, slot_override_keys = get_override_maps(
        tutor,
        calendar_start,
        calendar_end
    )

    booked_map = {
        (booking.availability_id, booking.session_date)
        for booking in relevant_bookings
    }

    weekday_order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    display_weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    weeks = []
    current_week_start = calendar_start

    while current_week_start <= calendar_end:
        days = []

        for weekday_index, weekday_name in enumerate(display_weekdays):
            current_date = current_week_start + timedelta(days=weekday_index)
            is_past = current_date < today
            day_slots = []

            for slot in availability:
                slot_weekday_index = weekday_order.index(slot.day)

                if slot_weekday_index != weekday_index:
                    continue

                is_overridden = (
                    current_date in full_day_dates
                    or (slot.id, current_date) in slot_override_keys
                )
                is_booked = (slot.id, current_date) in booked_map

                day_slots.append({
                    "id": slot.id,
                    "time_slot": slot.time_slot.strftime("%H:%M"),
                    "is_booked": is_booked or is_past or is_overridden,
                    "is_overridden": is_overridden
                })

            day_slots.sort(key=lambda slot: slot["time_slot"])

            days.append({
                "name": weekday_name,
                "date": current_date.isoformat(),
                "in_month": month_start <= current_date <= month_end,
                "is_past": is_past,
                "is_blocked": current_date in full_day_dates,
                "has_available": any(not slot["is_booked"] for slot in day_slots),
                "slots": day_slots
            })

        week_end = current_week_start + timedelta(days=6)
        weeks.append({
            "week_start": current_week_start.isoformat(),
            "week_end": week_end.isoformat(),
            "label": f"{current_week_start.strftime('%m/%d/%Y')} - {week_end.strftime('%m/%d/%Y')}",
            "days": days
        })

        current_week_start += timedelta(days=7)

    return Response({
        "month_label": month_start.strftime("%B %Y"),
        "month_start": month_start.isoformat(),
        "month_end": month_end.isoformat(),
        "month_offset": month_offset,
        "weeks": weeks
    })
    

#bulk booking request


"""@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_booking(request):

    tutor_id = request.data.get("tutor_id")
    slots = request.data.get("slots")

    if not slots:
        return Response({"error": "No slots provided"}, status=400)

    try:
        tutor = Tutor.objects.get(profile_id=tutor_id)
    except Tutor.DoesNotExist:
        return Response({"error": "Tutor not found"}, status=404)

    student = request.user.userprofile

    with transaction.atomic():

        for slot_data in slots:
            availability = TutorAvailability.objects.select_for_update().get(
                id=slot_data["availability_id"],
                tutor=tutor
            )

            if availability.is_booked:
                raise Exception("Slot already booked")

            Booking.objects.create(
                student=student,
                tutor=tutor,
                availability=availability,
                session_date=slot_data["session_date"],
                session_mode=slot_data["session_mode"]
            )

            availability.is_booked = True
            availability.save()

    return Response({"message": "Booking successful"})"""

#Confirm payment View 
# Confirm payment View 
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def confirm_payment_and_book(request):

    user_profile = get_object_or_404(UserProfile, user=request.user)

    tutor_id = request.data.get("tutor_id")
    slots = request.data.get("slots")
    method_id = request.data.get("payment_method")

    if isinstance(slots, str):
        try:
            slots = json.loads(slots)
        except json.JSONDecodeError:
            return Response({"error": "Invalid slots payload."}, status=400)

    if not slots:
        return Response({"error": "No slots selected"}, status=400)

    # Enforce that a booking request can only include slots from one date.
    requested_dates = {
        parse_request_date(slot.get("session_date"))
        for slot in slots
    }

    if None in requested_dates:
        return Response({"error": "Invalid session date format."}, status=400)

    if len(requested_dates) > 1:
        return Response(
            {"error": "You can only book multiple sessions on the same day."},
            status=400
        )

    if method_id:
        try:
            method = PaymentMethod.objects.get(method_id=method_id, is_active=True)
        except PaymentMethod.DoesNotExist:
            return Response({"error": "Invalid payment method."}, status=400)

        receipt_image = request.FILES.get('receipt_image')
        transaction_reference = request.data.get('transaction_reference')

        if method.code == 'online' and receipt_image is None:
            return Response({"error": "Receipt image is required for online payments."}, status=400)

        if method.code == 'online' and not str(transaction_reference or '').strip():
            return Response({"error": "Transaction reference is required for online payments."}, status=400)

    tutor = get_object_or_404(Tutor, profile_id=tutor_id)
    normalized_slots = []

    with transaction.atomic():
        for slot in slots:
            availability = get_object_or_404(
                TutorAvailability.objects.select_for_update(),
                id=slot["availability_id"],
                tutor=tutor
            )

            session_date = parse_request_date(slot.get("session_date"))

            if session_date is None:
                return Response(
                    {"error": "Invalid session date format."},
                    status=400
                )

            # 🚫 Prevent booking past dates
            if session_date < now().date():
                return Response(
                    {"error": "Cannot book a past date."},
                    status=400
                )

            # 🚫 Ensure weekday matches availability template
            if WEEKDAY_MAP[session_date.weekday()] != availability.day:
                return Response(
                    {"error": "Selected date does not match availability day."},
                    status=400
                )

            if slot_is_overridden(tutor, session_date, availability):
                return Response(
                    {"error": "This slot is unavailable on that date."},
                    status=400
                )

            # 🚫 Check conflict
            conflict_exists = Booking.objects.filter(
                availability=availability,
                session_date=session_date,
                status__in=["Confirmed", "Pending", "Completed"]
            ).exists()

            if conflict_exists:
                return Response(
                    {"error": "This slot is already booked for that date."},
                status=400
            )

            # 🧹 Cleanup cancelled booking
            Booking.objects.filter(
                availability=availability,
                session_date=session_date,
                status="Cancelled"
            ).delete()

            normalized_slots.append({
                "availability": availability,
                "session_date": session_date,
                "session_mode": "F2F" if slot["session_mode"] in ["F2F", "Face-to-face"] else "Online",
            })

        normalized_slots.sort(
            key=lambda normalized: (
                normalized["session_date"],
                normalized["availability"].time_slot
            )
        )

        created_bookings = []

        booking_request_id = uuid4()
        request_bookings = []

        for slot_group in group_slot_requests(normalized_slots):
            session_group_id = uuid4()

            for slot_request in slot_group:
                booking = Booking.objects.create(
                    student=user_profile,
                    tutor=tutor,
                    availability=slot_request["availability"],
                    session_date=slot_request["session_date"],
                    session_mode=slot_request["session_mode"],
                    session_group_id=session_group_id,
                    booking_request_id=booking_request_id,
                    status="Pending"
                )
                created_bookings.append(booking.id)
                request_bookings.append(booking)

        create_booking_status_notification(
            tutor.profile,
            "pending",
            request_bookings
        )

    return Response({
        "message": "Booking successful",
        "booking_ids": created_bookings
    })

# ==========================================
# TEMPLATE AVAILABILITY (Weekly Template)
# ==========================================

@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def template_availability(request, pk=None):

    profile = request.user.userprofile

    try:
        tutor = Tutor.objects.get(profile=profile)
    except Tutor.DoesNotExist:
        return Response({"error": "Tutor not found"}, status=404)

    # =========================
    # GET ALL SLOTS
    # =========================
    if request.method == 'GET':
        slots = TutorAvailability.objects.filter(tutor=tutor)

        data = [
            {
                "availability_id": slot.id,
                "day": slot.day,
                "day_display": slot.get_day_display(),
                "time_slot": slot.time_slot.strftime("%H:%M"),
                "is_active": slot.is_active,
                "is_booked": slot.is_booked
            }
            for slot in slots
        ]

        return Response(data)

    # =========================
    # CREATE SLOT
    # =========================
    if request.method == 'POST':

        day = request.data.get("day")
        time_str = request.data.get("time_slot")

        try:
            time_obj = datetime.strptime(time_str, "%H:%M").time()
        except Exception:
            return Response({"error": "Invalid time format"}, status=400)

        slot = TutorAvailability.objects.create(
            tutor=tutor,
            day=day,
            time_slot=time_obj,
            is_active=True,
            is_booked=False
        )

        return Response({
            "availability_id": slot.id,
            "day": slot.day,
            "day_display": slot.get_day_display(),
            "time_slot": slot.time_slot.strftime("%H:%M"),
            "is_active": slot.is_active,
            "is_booked": slot.is_booked
        }, status=201)

    # =========================
    # DELETE SLOT
    # =========================
    if request.method == 'DELETE':

        if pk is None:
            return Response({"error": "Slot ID required"}, status=400)

        slot = get_object_or_404(TutorAvailability, id=pk, tutor=tutor)
        slot.delete()

        return Response({"message": "Deleted successfully"})


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def availability_overrides(request):

    profile = request.user.userprofile

    try:
        tutor = Tutor.objects.get(profile=profile)
    except Tutor.DoesNotExist:
        return Response({"error": "Tutor not found"}, status=404)

    if request.method == 'GET':
        start_date = parse_request_date(request.GET.get('start'))
        end_date = parse_request_date(request.GET.get('end'))

        if start_date is None or end_date is None:
            today = date.today()
            start_date = today.replace(day=1)
            end_date = date(today.year, today.month, monthrange(today.year, today.month)[1])

        overrides = TutorAvailabilityOverride.objects.filter(
            tutor=tutor,
            override_date__range=(start_date, end_date)
        ).select_related('availability').order_by('override_date', 'availability__time_slot')

        serializer = TutorAvailabilityOverrideSerializer(overrides, many=True)
        return Response(serializer.data)

    override_date = parse_request_date(request.data.get('override_date'))

    if override_date is None:
        return Response({"error": "Valid override_date is required."}, status=400)

    if override_date < date.today():
        return Response({"error": "Cannot create overrides for past dates."}, status=400)

    raw_is_full_day = request.data.get('is_full_day', False)
    is_full_day = raw_is_full_day if isinstance(raw_is_full_day, bool) else str(raw_is_full_day).lower() == 'true'

    if is_full_day:
        if has_confirmed_or_completed_booking_conflict(tutor, override_date):
            return Response(
                {"error": "Cannot block a date with confirmed or completed bookings."},
                status=400
            )

        if TutorAvailabilityOverride.objects.filter(
            tutor=tutor,
            override_date=override_date,
            is_full_day=True
        ).exists():
            return Response({"error": "This date is already blocked."}, status=400)

        override = TutorAvailabilityOverride.objects.create(
            tutor=tutor,
            override_date=override_date,
            is_full_day=True
        )

        serializer = TutorAvailabilityOverrideSerializer(override)
        return Response(serializer.data, status=201)

    if TutorAvailabilityOverride.objects.filter(
        tutor=tutor,
        override_date=override_date,
        is_full_day=True
    ).exists():
        return Response({"error": "This date is already fully blocked."}, status=400)

    slot_ids = request.data.get('availability_ids') or []
    single_slot_id = request.data.get('availability_id')

    if single_slot_id is not None:
        slot_ids = [single_slot_id]

    if not slot_ids:
        return Response({"error": "At least one availability_id is required."}, status=400)

    try:
        slot_ids = [int(slot_id) for slot_id in slot_ids]
    except (TypeError, ValueError):
        return Response({"error": "availability_ids must be numeric."}, status=400)

    availabilities = list(
        TutorAvailability.objects.filter(
            tutor=tutor,
            id__in=slot_ids
        ).order_by('time_slot')
    )

    if len(availabilities) != len(set(slot_ids)):
        return Response({"error": "One or more selected slots do not exist."}, status=400)

    created_overrides = []

    with transaction.atomic():
        for availability in availabilities:
            if availability.day != WEEKDAY_MAP[override_date.weekday()]:
                return Response(
                    {"error": "Selected slot does not match the chosen date."},
                    status=400
                )

            if has_confirmed_or_completed_booking_conflict(tutor, override_date, availability=availability):
                return Response(
                    {"error": "Cannot block a slot with confirmed or completed bookings."},
                    status=400
                )

            if TutorAvailabilityOverride.objects.filter(
                tutor=tutor,
                override_date=override_date,
                availability=availability,
                is_full_day=False
            ).exists():
                return Response(
                    {"error": "One or more selected slots are already blocked for this date."},
                    status=400
                )

            created_overrides.append(
                TutorAvailabilityOverride.objects.create(
                    tutor=tutor,
                    override_date=override_date,
                    availability=availability,
                    is_full_day=False
                )
            )

    serializer = TutorAvailabilityOverrideSerializer(created_overrides, many=True)
    return Response(serializer.data, status=201)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_availability_override(request, override_id):

    profile = request.user.userprofile

    try:
        tutor = Tutor.objects.get(profile=profile)
    except Tutor.DoesNotExist:
        return Response({"error": "Tutor not found"}, status=404)

    override = get_object_or_404(
        TutorAvailabilityOverride,
        id=override_id,
        tutor=tutor
    )

    override.delete()
    return Response({"message": "Override removed successfully."})

#accept booking
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_booking(request, booking_id):

    booking = get_object_or_404(Booking, id=booking_id)
    session_group_bookings = get_booking_request_bookings(booking) if booking.status == "Pending" else get_session_group_bookings(booking)

    # Ensure tutor owns booking
    if request.user.userprofile != booking.tutor.profile:
        return Response({"error": "Unauthorized"}, status=403)

    if booking.status != "Pending":
        return Response({"error": "Only pending bookings can be approved."}, status=400)

    Booking.objects.filter(id__in=[group_booking.id for group_booking in session_group_bookings]).update(
        status="Confirmed",
        tutee_confirmed=False,
        tutor_confirmed=False,
    )

    create_booking_status_notification(
        booking.student,
        "confirmed",
        session_group_bookings
    )

    return Response({"message": "Booking confirmed successfully."})

#Reject booking
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_booking(request, booking_id):

    booking = get_object_or_404(Booking, id=booking_id)
    session_group_bookings = get_booking_request_bookings(booking) if booking.status == "Pending" else get_session_group_bookings(booking)

    if request.user.userprofile != booking.tutor.profile:
        return Response({"error": "Unauthorized"}, status=403)

    if booking.status != "Pending":
        return Response({"error": "Only pending bookings can be rejected."}, status=400)

    Booking.objects.filter(id__in=[group_booking.id for group_booking in session_group_bookings]).update(
        status="Rejected",
        tutee_confirmed=False,
        tutor_confirmed=False,
    )

    create_booking_status_notification(
        booking.student,
        "rejected",
        session_group_bookings
    )

    return Response({"message": "Booking rejected successfully."})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_booking(request, booking_id):

    profile = request.user.userprofile
    booking = get_object_or_404(
        Booking.objects.select_related(
            'student__course',
            'student__user',
            'tutor__profile__course',
            'tutor__profile__user',
            'availability'
        ),
        id=booking_id
    )

    if profile != booking.student:
        return Response({"error": "Unauthorized"}, status=403)

    session_group_bookings = get_session_group_bookings(booking)
    representative_booking = get_representative_booking(session_group_bookings)

    if not representative_booking:
        return Response({"error": "Booking not found."}, status=404)

    first_booking = session_group_bookings[0]
    last_booking = session_group_bookings[-1]
    start_time = first_booking.availability.time_slot
    end_time = (
        datetime.combine(first_booking.session_date, last_booking.availability.time_slot)
        + timedelta(minutes=SESSION_SLOT_MINUTES)
    ).time()

    display_status = get_display_status(
        representative_booking.status,
        representative_booking.session_date,
        start_time,
        end_time
    )

    if display_status != "Upcoming":
        return Response({"error": "Only upcoming sessions can be cancelled."}, status=400)

    if representative_booking.session_date <= timezone.localdate():
        return Response({"error": "Only future sessions can be cancelled before the session date."}, status=400)

    with transaction.atomic():
        Booking.objects.filter(id__in=[group_booking.id for group_booking in session_group_bookings]).update(
            status="Cancelled",
            tutee_confirmed=False,
            tutor_confirmed=False,
        )

        create_booking_status_notification(
            representative_booking.tutor.profile,
            "cancelled",
            session_group_bookings,
            recipient_role="tutor"
        )
        create_booking_status_notification(
            representative_booking.student,
            "cancelled",
            session_group_bookings,
            recipient_role="tutee"
        )

    return Response({"message": "Session cancelled successfully."}, status=200)




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_bookings(request):

    profile = request.user.userprofile

    if profile.role == "Tutor":
        bookings = Booking.objects.filter(
            tutor__profile=profile
        ).select_related('student', 'availability', 'tutor__profile', 'rating')
    else:
        bookings = Booking.objects.filter(
            student=profile
        ).select_related('student', 'availability', 'tutor__profile', 'rating')

    bookings = bookings.order_by("session_date", "availability__time_slot")

    grouped_bookings = defaultdict(list)

    for booking in bookings:
        if booking.status == "Pending" and booking.booking_request_id:
            group_key = f"request-{booking.booking_request_id}"
        else:
            group_key = str(booking.session_group_id) if booking.session_group_id else f"booking-{booking.id}"
        grouped_bookings[group_key].append(booking)

    final_data = []

    for group in grouped_bookings.values():
        representative_booking = get_representative_booking(group)

        if representative_booking and representative_booking.status == "Pending" and representative_booking.booking_request_id:
            final_data.append(build_booking_request_block(group))
        else:
            final_data.append(build_combined_block(group))

    final_data.sort(key=lambda booking: (booking["date"], booking["startTime"]))

    return Response(final_data)


def build_booking_detail_payload(session_group_bookings):
    representative_booking = get_representative_booking(session_group_bookings)
    first_booking = session_group_bookings[0]
    last_booking = session_group_bookings[-1]

    start_time = first_booking.availability.time_slot
    end_time = (
        datetime.combine(first_booking.session_date, last_booking.availability.time_slot)
        + timedelta(minutes=SESSION_SLOT_MINUTES)
    ).time()

    return {
        "id": representative_booking.id,
        "session_group_id": str(representative_booking.session_group_id) if representative_booking.session_group_id else None,
        "tutee_confirmed": representative_booking.tutee_confirmed,
        "tutor_confirmed": representative_booking.tutor_confirmed,
        "rating_submitted": hasattr(representative_booking, "rating"),
        "tutee": {
            "name": f"{representative_booking.student.fname} {representative_booking.student.lname}",
            "email": representative_booking.student.user.email,
            "course": representative_booking.student.course.course_name if representative_booking.student.course else None,
            "year_level": representative_booking.student.year_level,
            "bio": representative_booking.student.bio,
            "avatar": representative_booking.student.profile_picture.url if representative_booking.student.profile_picture else None,
        },
        "tutor": {
            "name": f"{representative_booking.tutor.profile.fname} {representative_booking.tutor.profile.lname}",
            "email": representative_booking.tutor.profile.user.email,
            "course": representative_booking.tutor.profile.course.course_name if representative_booking.tutor.profile.course else None,
            "year_level": representative_booking.tutor.profile.year_level,
            "bio": representative_booking.tutor.profile.bio,
            "avatar": representative_booking.tutor.profile.profile_picture.url if representative_booking.tutor.profile.profile_picture else None,
            "rating": representative_booking.tutor.rating_average,
            "hourly_rate": float(representative_booking.tutor.hourly_rate or 0),
            "subjects_taught": list(
                representative_booking.tutor.tutorsubjects_set.select_related('subject').values_list(
                    'subject__subject_name',
                    flat=True
                )
            ),
        },
        "session": {
            "subject": representative_booking.tutor.profile.course.course_name if representative_booking.tutor.profile.course else "General",
            "date": representative_booking.session_date.strftime("%Y-%m-%d"),
            "start_time": start_time.strftime("%H:%M"),
            "end_time": end_time.strftime("%H:%M"),
            "duration_hours": get_duration_hours_for_bookings(session_group_bookings),
            "rating": representative_booking.rating.rating_score if hasattr(representative_booking, "rating") else None,
            "status": get_display_status(
                representative_booking.status,
                representative_booking.session_date,
                start_time,
                end_time
            ),
            "raw_status": representative_booking.status,
            "session_mode": representative_booking.session_mode,
        },
        "payment": serialize_payment_summary(representative_booking),
    }


#Booking Detail View (for tutor to see details of a specific booking, including payment info)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def booking_detail(request, booking_id):

    booking = get_object_or_404(
        Booking.objects.select_related(
            'student__course',
            'student__user',
            'tutor__profile__course',
            'tutor__profile__user',
            'payment__method',
            'availability'
        ),
        id=booking_id
    )

    if request.user.userprofile not in (booking.tutor.profile, booking.student):
        return Response({"error": "Unauthorized"}, status=403)

    session_group_bookings = get_session_group_bookings(booking)
    return Response(build_booking_detail_payload(session_group_bookings))


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_session_payment(request, booking_id):

    profile = request.user.userprofile
    booking = get_object_or_404(
        Booking.objects.select_related('availability', 'tutor', 'tutor__profile'),
        id=booking_id
    )

    if profile != booking.student:
        return Response({"error": "Unauthorized"}, status=403)

    session_group_bookings = get_session_group_bookings(booking)

    if any(group_booking.status != "Confirmed" for group_booking in session_group_bookings):
        return Response({"error": "All session slots must be confirmed before payment submission."}, status=400)

    representative_booking = get_representative_booking(session_group_bookings)

    if hasattr(representative_booking, 'payment'):
        return Response({"error": "Payment has already been submitted for this session."}, status=400)

    method_id = request.data.get("payment_method")

    if not method_id:
        return Response({"error": "Payment method required."}, status=400)

    try:
        method = PaymentMethod.objects.get(method_id=method_id, is_active=True)
    except PaymentMethod.DoesNotExist:
        return Response({"error": "Invalid payment method."}, status=400)

    receipt_image = request.FILES.get('receipt_image')
    transaction_reference = request.data.get('transaction_reference')

    is_online_payment = method.code == 'online'

    if is_online_payment and receipt_image is None:
        return Response({"error": "Receipt image is required for online payments."}, status=400)

    if is_online_payment and not str(transaction_reference or '').strip():
        return Response({"error": "Transaction reference is required for online payments."}, status=400)

    duration_hours = get_duration_hours_for_bookings(session_group_bookings)
    amount = round(float(representative_booking.tutor.hourly_rate or 0) * duration_hours, 2)

    with transaction.atomic():
        Payment.objects.create(
            booking=representative_booking,
            amount=amount,
            method=method,
            transaction_reference=str(transaction_reference or '').strip() or None,
            receipt_image=receipt_image,
            payment_status="Pending",
            paid_at=now()
        )

        Booking.objects.filter(id__in=[group_booking.id for group_booking in session_group_bookings]).update(
            tutee_confirmed=True,
            status="Awaiting Payment Verification"
        )

        create_booking_status_notification(
            representative_booking.tutor.profile,
            "awaiting_payment_verification",
            session_group_bookings
        )

    return Response({"message": "Payment submitted successfully."}, status=201)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def tutor_confirm_booking(request, booking_id):

    profile = request.user.userprofile
    booking = get_object_or_404(
        Booking.objects.select_related('tutor', 'tutor__profile', 'availability'),
        id=booking_id
    )

    if profile != booking.tutor.profile:
        return Response({"error": "Unauthorized"}, status=403)

    session_group_bookings = get_session_group_bookings(booking)

    if any(group_booking.status != "Awaiting Payment Verification" for group_booking in session_group_bookings):
        return Response({"error": "This session is not awaiting payment verification."}, status=400)

    representative_booking = get_representative_booking(session_group_bookings)
    payment = getattr(representative_booking, 'payment', None)

    if not payment:
        return Response({"error": "Payment has not been submitted for this session."}, status=400)

    already_counted = all(group_booking.tutor_confirmed for group_booking in session_group_bookings)

    with transaction.atomic():
        Booking.objects.filter(id__in=[group_booking.id for group_booking in session_group_bookings]).update(
            tutor_confirmed=True,
            status="Completed"
        )

        if payment.payment_status != "Paid":
            payment.payment_status = "Paid"
            payment.save(update_fields=['payment_status'])

        if not already_counted:
            tutor = representative_booking.tutor
            tutor.total_sessions += 1
            tutor.save(update_fields=['total_sessions'])

        create_booking_status_notification(
            representative_booking.student,
            "completed",
            session_group_bookings
        )

    return Response({"message": "Session marked as completed successfully."})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_booking(request, booking_id):
    return tutor_confirm_booking(request, booking_id)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_session_rating(request, booking_id):

    profile = request.user.userprofile
    booking = get_object_or_404(
        Booking.objects.select_related('tutor', 'availability'),
        id=booking_id
    )

    if profile != booking.student:
        return Response({"error": "Unauthorized"}, status=403)

    session_group_bookings = get_session_group_bookings(booking)

    if any(group_booking.status != "Completed" for group_booking in session_group_bookings):
        return Response({"error": "You can only rate completed sessions."}, status=400)

    representative_booking = get_representative_booking(session_group_bookings)

    if hasattr(representative_booking, 'rating'):
        return Response({"error": "Rating has already been submitted for this session."}, status=400)

    try:
        rating_score = int(request.data.get("rating_score"))
    except (TypeError, ValueError):
        return Response({"error": "A valid rating_score is required."}, status=400)

    if rating_score < 1 or rating_score > 5:
        return Response({"error": "rating_score must be between 1 and 5."}, status=400)

    Rating.objects.create(
        booking=representative_booking,
        student=profile,
        tutor=representative_booking.tutor,
        rating_score=rating_score,
        comment=request.data.get("comment", "")
    )
    update_tutor_rating_average(representative_booking.tutor)

    return Response({"message": "Rating submitted successfully."}, status=201)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_notifications(request):

    notifications = Notification.objects.filter(
        recipient=request.user.userprofile
    ).order_by('-created_at')

    serializer = NotificationSerializer(notifications, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_notification_read(request, notification_id):

    notification = get_object_or_404(Notification, id=notification_id)

    if notification.recipient != request.user.userprofile:
        return Response({"error": "Unauthorized"}, status=403)

    notification.is_read = True
    notification.save(update_fields=['is_read'])

    return Response({"message": "Notification marked as read."})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_preferences(request):

    profile = request.user.userprofile

    pref, created = Preference.objects.get_or_create(user=profile)

    pref.save()

    subject_ids = request.data.get("subjects", [])

    if subject_ids:
        pref.subjects.set(subject_ids)

    return Response({
        "message": "Preferences saved successfully"
    })
@api_view(['POST'])
def tutor_setup(request):

    profile = request.user.userprofile
    tutor = Tutor.objects.get(profile=profile)

    tutor.teaching_level = request.data.get("teaching_level")

    tutor.can_online = request.data.get("can_online", True)
    tutor.can_f2f = request.data.get("can_f2f", False)

    tutor.hourly_rate = request.data.get("hourly_rate")
    tutor.response_time = request.data.get("response_time", tutor.response_time)

    tutor.save()

    profile.profile_completed = True
    profile.save()

    return Response({"message": "Tutor profile updated"})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def recommend_tutors_view(request):

    student_profile = request.user.userprofile

    subject = request.data.get("subject")
    preferred_mode = request.data.get("preferred_mode")

    if not subject:
        return Response(
            {"error": "Subject is required"},
            status=400
        )

    # Build rating matrix for CF
    ratings = build_rating_matrix()

    # Run Hybrid algorithm
    results = recommend_tutors_hybrid(
        ratings,
        student_profile,
        subject
    )

    # ⭐ DEBUG CONSOLE OUTPUT
    print("\n===================================")
    print(" HYBRID RECOMMENDATION RESULTS")
    print("===================================")

    for i, r in enumerate(results[:10], start=1):

        tutor = r["tutor"]
        score = r["score"]

        print(
            f"{i}. {tutor.profile.fname} {tutor.profile.lname} — Score: {score:.3f}"
        )

    print("===================================\n")

    data = []

    for r in results[:10]:

        tutor = r["tutor"]
        score = r["score"]

        tutor_subjects = TutorSubjects.objects.filter(
            tutor=tutor
        ).select_related("subject")

        subjects = [
            ts.subject.subject_name
            for ts in tutor_subjects
        ]

        data.append({
            "id": tutor.profile.id,
            "name": f"{tutor.profile.fname} {tutor.profile.lname}",
            "score": round(score, 3),
            "rating": tutor.rating_average,
            "hourly_rate": tutor.hourly_rate,
            "subjects": subjects
        })

    return Response(data, status=200)

#Setup Profile 
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def setup_profile(request):

    profile = request.user.userprofile

    course_code = request.data.get("course")

    if course_code:
        course = Course.objects.get(course_code=course_code)
        profile.course = course

    profile.year_level = request.data.get("year_level")
    profile.bio = request.data.get("bio")

    profile.profile_completed = True

    profile.save()

    return Response({
        "message": "Profile updated successfully"
    })

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_tutee_profile(request):

    profile = request.user.userprofile

    profile.fname = request.data.get("fname", profile.fname)
    profile.mname = request.data.get("mname", profile.mname)
    profile.lname = request.data.get("lname", profile.lname)

    course_code = request.data.get("course")

    if course_code:
        try:
            course = Course.objects.get(course_code=course_code)
            profile.course = course
        except Course.DoesNotExist:
            return Response({"error": "Invalid course"}, status=400)

    profile.year_level = request.data.get("year_level", profile.year_level)
    profile.bio = request.data.get("bio", profile.bio)

    profile.save()

    # ⭐ Update preference subjects
    subject_ids = request.data.get("subjects", [])

    pref, created = Preference.objects.get_or_create(user=profile)

    if subject_ids:
        pref.subjects.set(subject_ids)

    pref.save()

    return Response({"message": "Profile updated successfully"})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_tutee_profile(request):

    profile = request.user.userprofile

    try:
        pref = Preference.objects.get(user=profile)
        subject_ids = list(pref.subjects.values_list("subject_code", flat=True))
    except Preference.DoesNotExist:
        subject_ids = []

    return Response({
        "fname": profile.fname,
        "mname": profile.mname,
        "lname": profile.lname,
        "email": profile.user.email,
        "course": profile.course.course_code if profile.course else None,
        "year_level": profile.year_level,
        "bio": profile.bio,
        "subjects": subject_ids     # ⭐ important
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_tutor_subjects(request):

    profile = request.user.userprofile
    tutor = Tutor.objects.get(profile=profile)

    subjects = TutorSubjects.objects.filter(tutor=tutor).select_related('subject')

    data = [
        {
            "subject_code": ts.subject.subject_code,
            "subject_name": ts.subject.subject_name,
            "description": ts.description or ''
        }
        for ts in subjects
    ]

    return Response(data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_tutor_subject(request):

    profile = request.user.userprofile
    tutor = Tutor.objects.get(profile=profile)

    subject_code = request.data.get("subject_code")
    description = request.data.get("description", '')

    try:
        subject = Subjects.objects.get(subject_code=subject_code)
    except Subjects.DoesNotExist:
        return Response({"error": "Invalid subject"}, status=400)

    tutor_subject, created = TutorSubjects.objects.get_or_create(
        tutor=tutor,
        subject=subject,
        defaults={"expertise_level": 3, "description": description or ''}
    )

    if not created and description is not None:
        tutor_subject.description = description or ''
        tutor_subject.save(update_fields=['description'])

    return Response({"message": "Subject added"})

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_tutor_subject(request, subject_code):

    profile = request.user.userprofile
    tutor = Tutor.objects.get(profile=profile)

    tutor_subject = get_object_or_404(
        TutorSubjects,
        tutor=tutor,
        subject__subject_code=subject_code
    )

    tutor_subject.description = request.data.get("description", '') or ''
    tutor_subject.save(update_fields=['description'])

    return Response({"message": "Subject updated"})

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_tutor_subject(request, subject_code):

    profile = request.user.userprofile
    tutor = Tutor.objects.get(profile=profile)

    TutorSubjects.objects.filter(
        tutor=tutor,
        subject__subject_code=subject_code
    ).delete()

    return Response({"message": "Subject removed"})


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_tutor_profile(request):

    profile = request.user.userprofile
    tutor = Tutor.objects.select_related('pinned_review').get(profile=profile)

    serializer = TutorProfileUpdateSerializer(
        tutor,
        data=request.data,
        partial=True
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()

    return Response({
        "message": "Tutor profile updated successfully",
        "tutor": TutorProfileSerializer(tutor).data
    })

@api_view(['GET'])
def payment_methods(request):

    methods = PaymentMethod.objects.filter(is_active=True)

    data = [
        {
            "id": method.method_id,
            "name": method.method_name,
            "code": method.code
        }
        for method in methods
    ]

    return Response(data)
