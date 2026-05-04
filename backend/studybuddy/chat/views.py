from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import ChatRoom, Message
from .serializers import ChatRoomSerializer, MessageSerializer
from studybuddy.models import UserProfile, Tutor

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def list_chat_rooms(request):
    """List all chat rooms for the logged-in user."""
    user_profile = request.user.userprofile
    rooms = ChatRoom.objects.filter(
        Q(tutee=user_profile) | Q(tutor=user_profile)
    ).order_by('-created_at')
    
    serializer = ChatRoomSerializer(rooms, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_message_history(request, room_id):
    """Get the message history for a specific room."""
    user_profile = request.user.userprofile
    room = get_object_or_404(ChatRoom, id=room_id)
    
    # Security: Ensure user is part of the room
    if room.tutee != user_profile and room.tutor != user_profile:
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
    
    messages = list(room.messages.order_by('-created_at')[:50])[::-1]
    serializer = MessageSerializer(messages, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def start_inquiry_chat(request, tutor_profile_id):
    """Start or get an inquiry chat room with a tutor."""
    tutee_profile = request.user.userprofile
    tutor_profile = get_object_or_404(UserProfile, id=tutor_profile_id, role='Tutor')
    
    if tutee_profile == tutor_profile:
        return Response({"error": "Cannot chat with yourself"}, status=status.HTTP_400_BAD_REQUEST)

    # Find or create a room without a booking (inquiry)
    room, created = ChatRoom.objects.get_or_create(
        tutee=tutee_profile,
        tutor=tutor_profile,
        booking=None
    )
    
    serializer = ChatRoomSerializer(room, context={'request': request})
    return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
