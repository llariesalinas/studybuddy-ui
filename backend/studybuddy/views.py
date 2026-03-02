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
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from django.utils.timezone import now
from django.db.models import Case, When, Value, IntegerField


from .models import Payment, Subjects, TutorAvailability, TutorSubjects, Tutor, Booking
from .serializers import TutorDetailSerializer, TutorSearchSerializer, SubjectSerializer

from .models import (
    UserProfile,
    Booking,
    Tutor,
    TutorSubjects
)
@api_view(['POST'])
def register_user(request):

    email = request.data.get('email')
    password = request.data.get('password')
    fname = request.data.get('fname')
    mname = request.data.get('mname', '')
    lname = request.data.get('lname')
    role = request.data.get('role')

    if not all([email, password, fname, lname, role]):
        return Response(
            {"error": "Missing required fields"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(username=email).exists():
        return Response(
            {"error": "User already exists"},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = User.objects.create_user(
        username=email,
        email=email,
        password=password
    )

    UserProfile.objects.create(
        user=user,
        fname=fname,
        mname=mname,
        lname=lname,
        role=role
    )

    return Response(
        {"message": "User registered successfully"},
        status=status.HTTP_201_CREATED
    )

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
@permission_classes([IsAuthenticated])
def student_dashboard(request):

    user_profile = UserProfile.objects.get(user=request.user)

    today = now().date()

    # -----------------------
    # UPCOMING SESSIONS
    # -----------------------
    upcoming_bookings = Booking.objects.filter(
        student=user_profile,
        status='Confirmed',   # MUST match booking creation
        session_date__gte=today
    ).select_related(
        'tutor__profile',
        'availability'
    ).order_by('session_date', 'availability__time_slot')

    upcoming = [
        {
            "id": booking.id,
            "subject": booking.tutor.profile.course or "General Tutoring",
            "tutor": f"{booking.tutor.profile.fname} {booking.tutor.profile.lname}",
            "date": booking.session_date.strftime("%Y-%m-%d"),
            "time": booking.availability.time_slot.strftime("%H:%M")
        }
        for booking in upcoming_bookings
    ]

    # -----------------------
    # COMPLETED SESSIONS
    # -----------------------
    completed_bookings = Booking.objects.filter(
        student=user_profile,
        status='Completed'
    ).select_related(
        'tutor__profile',
        'availability'
    ).order_by('-session_date')

    completed = [
        {
            "id": booking.id,
            "subject": booking.tutor.profile.course or "General Tutoring",
            "tutor": f"{booking.tutor.profile.fname} {booking.tutor.profile.lname}",
            "date": booking.session_date.strftime("%Y-%m-%d"),
            "time": booking.availability.time_slot.strftime("%H:%M")
        }
        for booking in completed_bookings
    ]

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


#Tutor Dashboard View

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def tutor_dashboard(request):
    profile = request.user.userprofile

    try:
        tutor = Tutor.objects.get(profile=profile)
    except Tutor.DoesNotExist:
        return Response({"error": "Tutor not found"}, status=404)

    upcoming = Booking.objects.filter(
    tutor=tutor
).annotate(
    status_priority=Case(
        When(status="Confirmed", then=Value(0)),
        When(status="Pending", then=Value(1)),
        When(status="Completed", then=Value(2)),
        default=Value(3),
        output_field=IntegerField(),
    )
).order_by("status_priority", "session_date")

    bookings_data = [
    {
        "id": b.id,  # ← REQUIRED
        "student": f"{b.student.fname} {b.student.lname}",
        "date": b.session_date,
        "status": b.status
    }
    for b in upcoming
]

    return Response({
        "total_sessions": tutor.total_sessions,
        "rating_average": tutor.rating_average,
        "hourly_rate": tutor.hourly_rate,
        "upcoming_bookings": bookings_data
    })

#Booking details view

"""@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_booking(request):

    profile = request.user.userprofile
    availability_id = request.data.get("availability")
    session_date = request.data.get("session_date")
    session_mode = request.data.get("session_mode")

    try:
        availability = TutorAvailability.objects.get(id=availability_id)
    except TutorAvailability.DoesNotExist:
        return Response({"error": "Invalid availability"}, status=404)

    if availability.is_booked:
        return Response({"error": "Slot already booked"}, status=400)

    booking = Booking.objects.create(
        student=profile,
        tutor=availability.tutor,
        availability=availability,
        session_date=session_date,
        session_mode=session_mode
    )

    availability.is_booked = True
    availability.save()

    return Response({"message": "Booking successful"})"""


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
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def confirm_payment_and_book(request):

    user_profile = get_object_or_404(UserProfile, user=request.user)

    tutor_id = request.data.get("tutor_id")
    slots = request.data.get("slots")

    if not slots:
        return Response({"error": "No slots selected"}, status=400)

    tutor = get_object_or_404(Tutor, profile_id=tutor_id)

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

<<<<<<< HEAD
            # 🚫 Block past dates
=======
>>>>>>> origin/main
            if session_date < now().date():
                return Response(
                    {"error": "Cannot book sessions in the past."},
                    status=400
                )

            # 🚫 Ensure weekday matches availability template
            if weekday_map[session_date.weekday()] != availability.day:
                return Response(
                    {"error": "Selected date does not match availability day."},
                    status=400
                )

            # 🚫 Prevent double booking
            conflict_exists = Booking.objects.filter(
                availability=availability,
                session_date=session_date
            ).exists()

            if conflict_exists:
                return Response(
                    {"error": "This slot is already booked for that date."},
                    status=400
                )

            # ✅ Create booking
            booking = Booking.objects.create(
                student=user_profile,
                tutor=tutor,
                availability=availability,
                session_date=session_date,
                session_mode=slot["session_mode"],
                status="Confirmed"
            )

            # ✅ Create payment record
            Payment.objects.create(
                booking=booking,
                amount=tutor.hourly_rate,
                payment_status="Paid",
                paid_at=now()
            )

            created_bookings.append(booking.id)

    return Response({
        "message": "Booking successful",
        "booking_ids": created_bookings
    })

#Complete session view (tutor marks session as completed)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_session(request, booking_id):

    with transaction.atomic():

        booking = get_object_or_404(Booking, id=booking_id)

        # ✅ Only tutor can complete their own session
        if request.user.userprofile != booking.tutor.profile:
            return Response(
                {"error": "You are not authorized to complete this session."},
                status=403
            )

        if booking.status == "Completed":
            return Response(
                {"error": "This session is already marked as completed."},
                status=400
            )

        if booking.status != "Confirmed":
            return Response(
                {"error": "Only confirmed sessions can be completed."},
                status=400
            )

        # 1️⃣ Mark as completed
        booking.status = "Completed"
        booking.save()

        # 2️⃣ Increase tutor total sessions
        tutor = booking.tutor
        tutor.total_sessions += 1
        tutor.save()

    return Response({"message": "Session completed successfully."})



