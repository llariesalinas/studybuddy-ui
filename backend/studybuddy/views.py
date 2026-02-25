from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import UserProfile


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
        "email": user.email
    })