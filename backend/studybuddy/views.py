from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import UserProfile

@api_view(['GET'])
def get_users(request):
    users = User.objects.all().values('id', 'username', 'email')
    return Response({'users': list(users)})

@api_view(['POST'])
def register_user(request):
    email = request.data.get('email')
    password = request.data.get('password')
    fname = request.data.get('fname')
    mname = request.data.get('mname')
    lname = request.data.get('lname')
    role = request.data.get('role')

    # Check if user exists
    if User.objects.filter(username=email).exists():
        return Response({"error": "User already exists"}, status=400)

    # Create auth_user
    user = User.objects.create_user(
        username=email,
        email=email,
        password=password
    )

    # Create UserProfile
    UserProfile.objects.create(
        user=user,
        fname=fname,
        mname=mname,
        lname=lname,
        role=role
    )

    return Response({"message": "User registered successfully"})