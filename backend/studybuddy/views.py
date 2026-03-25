from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.utils.timezone import now
from django.db import transaction
from datetime import datetime,timedelta, date
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
from django.db.models import Case, When, Value, IntegerField

\
from collections import defaultdict
# algo
from .recommender.hybrid import recommend_tutors_hybrid
from .recommender.CF import build_rating_matrix
from .recommender.cbf import recommend_tutors
from .models import Payment, PaymentMethod, Subjects, TutorAvailability, TutorSubjects, Tutor, Booking,Course,Preference
from .models import Payment, PaymentMethod, Subjects, TutorAvailability, TutorSubjects, Tutor, Booking, PaymentMethod
from .serializers import TutorDetailSerializer, TutorSearchSerializer, SubjectSerializer

from .models import (
    UserProfile,
    Booking,
    Tutor,
    TutorSubjects
)
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from .models import UserProfile, Tutor


@api_view(['POST'])
def register_user(request):

    email = request.data.get('email')
    password = request.data.get('password')
    fname = request.data.get('fname')
    mname = request.data.get('mname', '')
    lname = request.data.get('lname')
    role = request.data.get('role')

    # Validate required fields
    if not all([email, password, fname, lname, role]):
        return Response(
            {"error": "Missing required fields"},
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
        role=role
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
                + timedelta(hours=1)
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
                + timedelta(hours=1)
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

    first = group[0]
    last = group[-1]

    start_time = first.availability.time_slot

    end_time = (
        datetime.combine(first.session_date, last.availability.time_slot)
        + timedelta(hours=1)
    ).time()

    duration = len(group)

    # ensure correct status
    group_status = first.status

    return {
        "id": first.id,
        "status": group_status,
        "date": first.session_date,
        "tuteeName": f"{first.student.fname} {first.student.lname}",

        "subject": (
            first.tutor.profile.course.course_name
            if first.tutor.profile.course
            else "General"
        ),

        "topic": "",
        "startTime": start_time.strftime("%H:%M"),
        "endTime": end_time.strftime("%H:%M"),
        "duration_hours": duration
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

    # 📌 Get completed bookings
    completed_bookings = Booking.objects.filter(
        tutor=tutor,
        status="Completed"
    ).select_related("payment")


    total_earnings = 0

    for b in completed_bookings:


        if hasattr(b, "payment") and b.payment:

            amount = float(b.payment.amount)


        if hasattr(b, "payment") and b.payment:
            amount = float(b.payment.amount)

            platform_fee = amount * 0.16

            method = b.payment.method.method_name if b.payment.method else None

            if method == "GCash":
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
                + timedelta(hours=1)
            ).time()

            if booking.availability.time_slot == prev_end and booking.status == prev.status:
                current_group.append(booking)
            else:
                bookings_data.append(build_combined_block(current_group))
                current_group = [booking]

        bookings_data.append(build_combined_block(current_group))

    # 📌 Get completed bookings
    completed_bookings = Booking.objects.filter(
        tutor=tutor,
        status="Completed"
    ).select_related("payment")

    total_earnings = 0

    for b in completed_bookings:
        if hasattr(b, "payment"):
            amount = float(b.payment.amount)
            platform_fee = amount * 0.16
            transaction_fee = amount * 0.04
            tutor_earned = amount - platform_fee - transaction_fee
            total_earnings += tutor_earned

    upcoming = Booking.objects.filter(
        tutor=tutor

            total_earnings += tutor_earned

    upcoming = Booking.objects.filter(
        tutor=tutor,
        status="Confirmed",          # must match your exact DB value
        session_date__gte=timezone.now()

    ).order_by("session_date")

    bookings_data = [
        {
            "id": b.id,
            "student": f"{b.student.fname} {b.student.lname}",
            "subject": b.tutor.profile.course or "General",
            "date": b.session_date,
            "status": b.status
        }
        for b in upcoming
    ]
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
        tutor = Tutor.objects.get(profile=profile)
    except Tutor.DoesNotExist:
        return Response({"error": "Tutor not found"}, status=404)

    return Response({
        "fname": profile.fname,
        "lname": profile.lname,
        "email": profile.user.email,
        "course": profile.course.course_code if profile.course else None,
        "year_level": profile.year_level,
        "bio": profile.bio,

        "hourly_rate": tutor.hourly_rate,
        "teaching_level": tutor.teaching_level,
        "can_online": tutor.can_online,
        "can_f2f": tutor.can_f2f,
        "rating_average": tutor.rating_average,
        "total_sessions": tutor.total_sessions
    })

=======
>>>>>>> origin/main
#Tutor Detail View
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def tutor_detail(request, profile_id):
    try:
        tutor = Tutor.objects.select_related('profile').get(profile_id=profile_id)
    except Tutor.DoesNotExist:
        return Response({"error": "Tutor not found"}, status=404)

    serializer = TutorDetailSerializer(tutor)
    return Response(serializer.data)

#tutor availability schedule thing  vview

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def tutor_availability(request, tutor_id):

    tutor = get_object_or_404(Tutor, profile_id=tutor_id)

    date_str = request.GET.get("date")
    if not date_str:
        return Response({"error": "Date parameter is required."}, status=400)

    try:
        session_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return Response({"error": "Invalid date format."}, status=400)

    # 🔥 STEP 1 — Calculate week boundaries (Mon–Sun)
    week_start = session_date - timedelta(days=session_date.weekday())
    week_end = week_start + timedelta(days=6)

    # 🔥 STEP 2 — Fetch all bookings for that week
    weekly_bookings = Booking.objects.filter(
        tutor=tutor,
        session_date__range=(week_start, week_end),
        status__in=["Confirmed", "Pending", "Completed"]
    )

    # 🔥 STEP 3 — Create fast lookup set
    booked_map = {
        (booking.availability_id, booking.session_date)
        for booking in weekly_bookings
    }

    # 🔥 STEP 4 — Get recurring weekly availability template
    availability = TutorAvailability.objects.filter(
        tutor=tutor,
        is_active=True
    )

    weekday_order = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]

    data = []

    for slot in availability:

        # Determine actual date for this slot in selected week
        slot_weekday_index = weekday_order.index(slot.day)
        slot_date = week_start + timedelta(days=slot_weekday_index)

        # 🚫 Block past dates
        is_past = slot_date < date.today()

        # 🔴 Block if booked in DB
        is_booked = (slot.id, slot_date) in booked_map

        data.append({
            "id": slot.id,
            "day": slot.get_day_display(),
            "date": slot_date,
            "time_slot": slot.time_slot.strftime("%H:%M"),
            "is_booked": is_booked or is_past
        })

    return Response(data)
    

# Confirm payment View 
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def confirm_payment_and_book(request):

    user_profile = get_object_or_404(UserProfile, user=request.user)

    tutor_id = request.data.get("tutor_id")
    slots = request.data.get("slots")
    method_id = request.data.get("payment_method")

    if not slots:
        return Response({"error": "No slots selected"}, status=400)

    if not method_id:
        return Response({"error": "Payment method required"}, status=400)

    tutor = get_object_or_404(Tutor, profile_id=tutor_id)

    try:
        method = PaymentMethod.objects.get(method_id=method_id, is_active=True)
    except PaymentMethod.DoesNotExist:
        return Response({"error": "Invalid payment method"}, status=400)

    created_bookings = []

    weekday_map = {
        0: "Mon",
        1: "Tue",
        2: "Wed",
        3: "Thu",
        4: "Fri",
        5: "Sat",
        6: "Sun",
    }
    total_amount = 0  #  accumulate total for multi-slot

    with transaction.atomic():

        for slot in slots:

            availability = get_object_or_404(
                TutorAvailability.objects.select_for_update(),
                id=slot["availability_id"],
                tutor=tutor
            )

            # Convert string to date
            try:
                session_date = datetime.strptime(
                    slot["session_date"], "%Y-%m-%d"
                ).date()
            except ValueError:
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
            if weekday_map[session_date.weekday()] != availability.day:
                return Response(
                    {"error": "Selected date does not match availability day."},
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

            #  Create booking
            booking = Booking.objects.create(
                student=user_profile,
                tutor=tutor,
                availability=availability,
                session_date=session_date,
                session_mode=slot["session_mode"],

                status="Pending"  # Better than Pending if already paid

                status="Confirmed"   # 🔥 Better than Pending if already paid

            )

            created_bookings.append(booking.id)

            total_amount += tutor.hourly_rate


        # ✅ Create ONE payment record per booking
        for booking_id in created_bookings:
            Payment.objects.create(
                booking_id=booking_id,
                amount=tutor.hourly_rate,
                method=method,
                payment_status="Paid",
                paid_at=now()
            )


        # ✅ Optional: update tutor stats
        tutor.total_sessions += len(created_bookings)
        tutor.save()

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
    
#accept booking
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_booking(request, booking_id):

    booking = get_object_or_404(Booking, id=booking_id)

    # Ensure tutor owns booking
    if request.user.userprofile != booking.tutor.profile:
        return Response({"error": "Unauthorized"}, status=403)

    if booking.status != "Pending":
        return Response({"error": "Only pending bookings can be approved."}, status=400)

    # Confirm ALL slots belonging to this session
    Booking.objects.filter(
        tutor=booking.tutor,
        student=booking.student,
        session_date=booking.session_date,
        status="Pending"
    ).update(status="Confirmed")

    return Response({"message": "Booking confirmed successfully."})

#Reject booking
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_booking(request, booking_id):

    booking = get_object_or_404(Booking, id=booking_id)

    if request.user.userprofile != booking.tutor.profile:
        return Response({"error": "Unauthorized"}, status=403)

    if booking.status != "Pending":
        return Response({"error": "Only pending bookings can be rejected."}, status=400)

    # Delete ALL slots belonging to the same session
    Booking.objects.filter(
        tutor=booking.tutor,
        student=booking.student,
        session_date=booking.session_date,
        status="Pending"
    ).delete()

    return Response({"message": "Booking rejected and removed."})




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_bookings(request):

    profile = request.user.userprofile

    if profile.role == "Tutor":
        bookings = Booking.objects.filter(
            tutor__profile=profile
        )
    else:
        bookings = Booking.objects.filter(
            student=profile
        )

    bookings = bookings.order_by("session_date", "availability__time_slot")

    grouped_by_date = defaultdict(list)

    for b in bookings:
        grouped_by_date[b.session_date].append(b)

    final_data = []

    for session_date, day_bookings in grouped_by_date.items():

        day_bookings.sort(key=lambda b: b.availability.time_slot)

        current_group = [day_bookings[0]]

        for booking in day_bookings[1:]:

            prev = current_group[-1]

            prev_end = (
                datetime.combine(session_date, prev.availability.time_slot)
                + timedelta(hours=1)
            ).time()

            if booking.availability.time_slot == prev_end and booking.status == prev.status:
                current_group.append(booking)
            else:
                final_data.append(build_combined_block(current_group))
                current_group = [booking]

        final_data.append(build_combined_block(current_group))

    return Response(final_data)
#Booking Detail View (for tutor to see details of a specific booking, including payment info)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def booking_detail(request, booking_id):

    booking = get_object_or_404(
        Booking.objects.select_related(
            'student__course',
            'tutor__profile__course',
            'payment__method',
            'availability'
        ),
        id=booking_id
    )

    # Ensure tutor owns this booking
    if request.user.userprofile != booking.tutor.profile:
        return Response({"error": "Unauthorized"}, status=403)

    # -------------------------------------------------
    # FIND ALL CONSECUTIVE BOOKINGS FOR THIS SESSION
    # -------------------------------------------------
    related_bookings = Booking.objects.filter(
        tutor=booking.tutor,
        student=booking.student,
        session_date=booking.session_date,
        status=booking.status
    ).select_related("availability").order_by("availability__time_slot")

    start_time = related_bookings.first().availability.time_slot

    end_time = (
        datetime.combine(
            booking.session_date,
            related_bookings.last().availability.time_slot
        ) + timedelta(hours=1)
    ).time()

    duration_hours = related_bookings.count()

    # Safe Payment Handling
    # -------------------------
    amount_paid = 0
    platform_fee = 0
    transaction_fee = 0
    tutor_earned = 0
    payment_status = "Pending"
    transaction_id = None
    method = None

    if hasattr(booking, "payment") and booking.payment:

        amount_paid = float(booking.payment.amount)
        payment_status = booking.payment.payment_status
        transaction_id = booking.payment.transaction_reference


        method = booking.payment.method.method_name if booking.payment.method else None

        platform_fee = round(amount_paid * 0.16, 2)

        # 🔥 GET REAL METHOD FROM DB
        method = booking.payment.method.method_name if booking.payment.method else None

        # Platform fee always applies
        platform_fee = round(amount_paid * 0.16, 2)

        # Only apply transaction fee if GCash

        if method == "GCash":
            transaction_fee = round(amount_paid * 0.04, 2)
        else:
            transaction_fee = 0

        tutor_earned = round(amount_paid - platform_fee - transaction_fee, 2)

    return Response({
        "id": booking.id,

        "tutee": {
            "name": f"{booking.student.fname} {booking.student.lname}",
            "email": booking.student.user.email,

            "course": (
                booking.student.course.course_name
                if booking.student.course
                else None
            ),

            "year_level": booking.student.year_level,
            "bio": booking.student.bio,
            "avatar": booking.student.profile_picture.url if booking.student.profile_picture else None
        },

        "session": {


            "subject": (
                booking.tutor.profile.course.course_name
                if booking.tutor.profile.course
                else "General"
            ),

            "topic": "",
            "date": booking.session_date.strftime("%Y-%m-%d"),

            "start_time": start_time.strftime("%H:%M"),
            "end_time": end_time.strftime("%H:%M"),
            "duration_hours": duration_hours,

            "start_time": booking.availability.time_slot.strftime("%H:%M"),
            "end_time": (
                datetime.combine(date.today(), booking.availability.time_slot)
                + timedelta(hours=1)
            ).time().strftime("%H:%M"),

            "rating": booking.rating.rating_score if hasattr(booking, "rating") else None,
            "status": booking.status
        },

        "payment": {
            "transaction_id": transaction_id,
            "method": method,
            "amount_paid": amount_paid,
            "tutor_earned": tutor_earned,
            "platform_fee": platform_fee,
            "transaction_fee": transaction_fee,
            "status": payment_status
        }
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

>>>>>>> origin/main
#Complete booking view (tutor marks session as completed, updates earnings, etc.)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_booking(request, booking_id):

    with transaction.atomic():

        profile = request.user.userprofile

        try:
            tutor = Tutor.objects.get(profile=profile)
            booking = Booking.objects.get(id=booking_id, tutor=tutor)
        except (Tutor.DoesNotExist, Booking.DoesNotExist):
            return Response({"error": "Booking not found"}, status=404)

        #    DEBUG AFTER booking is defined
        print("===== DEBUG STATUS =====")
        print("DB booking.status:", booking.status)
        print("========================")

        # Temporarily remove status check for testing
        booking.status = "Completed"
        booking.save()

        tutor.total_sessions += 1
        tutor.save()

    return Response({"message": "Session marked as completed successfully."})
<<<<<<< HEAD


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
            "subject_name": ts.subject.subject_name
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

    try:
        subject = Subjects.objects.get(subject_code=subject_code)
    except Subjects.DoesNotExist:
        return Response({"error": "Invalid subject"}, status=400)

    TutorSubjects.objects.get_or_create(
        tutor=tutor,
        subject=subject,
        defaults={"expertise_level": 3}
    )

    return Response({"message": "Subject added"})

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
    tutor = Tutor.objects.get(profile=profile)

    tutor.hourly_rate = request.data.get("hourly_rate", tutor.hourly_rate)
    tutor.teaching_level = request.data.get("teaching_level", tutor.teaching_level)

    tutor.can_online = request.data.get("can_online", tutor.can_online)
    tutor.can_f2f = request.data.get("can_f2f", tutor.can_f2f)

    tutor.save()

    return Response({
        "message": "Tutor profile updated successfully"
    })

@api_view(['GET'])
def payment_methods(request):

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

