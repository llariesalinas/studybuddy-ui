from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.utils.timezone import now

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from django.utils.timezone import now


from .models import Subjects, TutorSubjects, Tutor, Booking
from .serializers import TutorSearchSerializer, SubjectSerializer

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

    # -----------------------
    # UPCOMING SESSIONS
    # -----------------------
    upcoming_bookings = Booking.objects.filter(
        student=user_profile,
        status='Confirmed',
        session_date__gte=now().date()
    ).select_related('tutor__profile', 'availability')

    upcoming = [
        {
            "id": booking.id,
            "subject": booking.tutor.profile.course or "General Tutoring",
            "tutor": f"{booking.tutor.profile.fname} {booking.tutor.profile.lname}",
            "date": booking.session_date,
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
    ).select_related('tutor__profile', 'availability')

    completed = [
        {
            "id": booking.id,
            "subject": booking.tutor.profile.course or "General Tutoring",
            "tutor": f"{booking.tutor.profile.fname} {booking.tutor.profile.lname}",
            "date": booking.session_date,
            "time": booking.availability.time_slot.strftime("%H:%M")
        }
        for booking in completed_bookings
    ]

    # -----------------------
    # RECOMMENDED TUTORS (Simple version)
    # -----------------------
    tutors = Tutor.objects.all().select_related('profile')[:3]

    recommendations = []

    for tutor in tutors:
        tutor_subjects = TutorSubjects.objects.filter(tutor=tutor).select_related('subject')

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
        tutor=tutor,
        session_date__gte=now().date()
    ).select_related("student")

    bookings_data = [
        {
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