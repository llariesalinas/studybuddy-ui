import base64
import json

from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Max
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from .models import ChatRoom, Message
from .serializers import ChatRoomSerializer, MessageSerializer
from studybuddy.models import UserProfile, Tutor
from .services import (
    broadcast_message,
    broadcast_room_updated,
    create_chat_message,
    get_canonical_room,
    get_current_booking_contexts,
)

DEFAULT_ROOM_PAGE_SIZE = 25
MAX_ROOM_PAGE_SIZE = 50


def get_room_page_size(request):
    try:
        requested = int(request.query_params.get('page_size', DEFAULT_ROOM_PAGE_SIZE))
    except (TypeError, ValueError):
        requested = DEFAULT_ROOM_PAGE_SIZE
    return max(1, min(requested, MAX_ROOM_PAGE_SIZE))


def encode_room_cursor(room):
    payload = {
        'updated_at': room.updated_at.isoformat(),
        'id': room.id,
    }
    encoded = base64.urlsafe_b64encode(json.dumps(payload).encode('utf-8')).decode('ascii')
    return encoded.rstrip('=')


def decode_room_cursor(cursor):
    if not cursor:
        return None
    try:
        padding = '=' * (-len(cursor) % 4)
        payload = json.loads(base64.urlsafe_b64decode(f'{cursor}{padding}').decode('utf-8'))
        updated_at = parse_datetime(payload['updated_at'])
        room_id = int(payload['id'])
        if updated_at is None:
            return None
        return updated_at, room_id
    except (TypeError, ValueError, KeyError, json.JSONDecodeError):
        return None

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def list_chat_rooms(request):
    """List all chat rooms for the logged-in user."""
    user_profile = request.user.userprofile
    page_size = get_room_page_size(request)
    rooms_qs = (
        ChatRoom.objects.filter(
            Q(tutee=user_profile) | Q(tutor=user_profile)
        )
        .select_related('tutee', 'tutor', 'ticket')
        .order_by('-updated_at', '-id')
    )

    cursor = decode_room_cursor(request.query_params.get('cursor'))
    if cursor:
        cursor_updated_at, cursor_id = cursor
        rooms_qs = rooms_qs.filter(
            Q(updated_at__lt=cursor_updated_at)
            | Q(updated_at=cursor_updated_at, id__lt=cursor_id)
        )

    rooms = list(
        rooms_qs[:page_size + 1]
    )
    has_more = len(rooms) > page_size
    if has_more:
        rooms = rooms[:page_size]
    next_cursor = encode_room_cursor(rooms[-1]) if has_more and rooms else None
    room_ids = [room.id for room in rooms]

    total_unread = (
        Message.objects
        .filter(
            Q(room__tutee=user_profile) | Q(room__tutor=user_profile),
            is_read=False,
        )
        .exclude(sender=request.user)
        .count()
    )

    # Unread counts for every room in a single aggregate query.
    unread_map = {
        row['room_id']: row['unread']
        for row in Message.objects
        .filter(room_id__in=room_ids, is_read=False)
        .exclude(sender=request.user)
        .values('room_id')
        .annotate(unread=Count('id'))
    }

    # Last message per room: one query for the latest ids, one to fetch them.
    last_ids = list(
        Message.objects
        .filter(room_id__in=room_ids)
        .values('room_id')
        .annotate(last_id=Max('id'))
        .values_list('last_id', flat=True)
    )
    last_message_map = {
        message.room_id: message
        for message in Message.objects.filter(id__in=last_ids).select_related('sender', 'sender__userprofile')
    }
    current_booking_map = get_current_booking_contexts(rooms)

    serializer = ChatRoomSerializer(rooms, many=True, context={
        'request': request,
        'unread_map': unread_map,
        'last_message_map': last_message_map,
        'current_booking_map': current_booking_map,
        'skip_partner_context': True,
    })
    return Response({
        'results': serializer.data,
        'next_cursor': next_cursor,
        'has_more': has_more,
        'total_unread': total_unread,
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_room_detail(request, room_id):
    """Full detail (incl. partner_context) for a single room, loaded when opened."""
    user_profile = request.user.userprofile
    room = get_object_or_404(ChatRoom.objects.select_related('tutee', 'tutor'), id=room_id)

    if room.tutee != user_profile and room.tutor != user_profile:
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

    serializer = ChatRoomSerializer(room, context={'request': request})
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

    messages_qs = room.messages.select_related('sender', 'sender__userprofile')
    after_id_raw = request.query_params.get('after_id')

    after_id = None
    if after_id_raw is not None:
        try:
            after_id = int(after_id_raw)
        except (TypeError, ValueError):
            after_id = None

    if after_id is not None:
        messages = list(messages_qs.filter(id__gt=after_id).order_by('id')[:50])
    else:
        messages = list(messages_qs.order_by('-created_at', '-id')[:50])[::-1]

    serializer = MessageSerializer(messages, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_room_read(request, room_id):
    """Mark messages in a room as read for the logged-in user."""
    user_profile = request.user.userprofile
    room = get_object_or_404(ChatRoom, id=room_id)

    if room.tutee != user_profile and room.tutor != user_profile:
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

    updated = room.messages.filter(is_read=False).exclude(sender=request.user).update(
        is_read=True,
        read_at=timezone.now()
    )

    if updated:
        broadcast_room_updated(room)

    return Response({"message": "Messages marked read.", "updated": updated})

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def start_inquiry_chat(request, tutor_profile_id):
    """Start or get an inquiry chat room with a tutor."""
    tutee_profile = request.user.userprofile
    tutor_profile = get_object_or_404(UserProfile, id=tutor_profile_id, role='Tutor')
    
    if tutee_profile == tutor_profile:
        return Response({"error": "Cannot chat with yourself"}, status=status.HTTP_400_BAD_REQUEST)

    existing_room = ChatRoom.objects.filter(
        tutee=tutee_profile,
        tutor=tutor_profile,
        booking__isnull=True
    ).first()
    room = existing_room or get_canonical_room(tutee_profile, tutor_profile)
    created = existing_room is None
    
    serializer = ChatRoomSerializer(room, context={'request': request})
    return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def send_message(request, room_id):
    """REST fallback for sending a message when WebSocket is unavailable."""
    user_profile = request.user.userprofile
    room = get_object_or_404(ChatRoom, id=room_id)

    if room.tutee != user_profile and room.tutor != user_profile:
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

    content = str(request.data.get('message') or '').strip()
    if not content:
        return Response({"error": "Message cannot be empty."}, status=status.HTTP_400_BAD_REQUEST)

    temp_id = request.data.get('temp_id')
    message = create_chat_message(
        room,
        request.user,
        content,
        message_type='text',
        metadata={},
        broadcast=False,
    )
    broadcast_message(room, message, temp_id=temp_id)

    message_data = MessageSerializer(message, context={'request': request}).data
    if temp_id:
        message_data['temp_id'] = temp_id

    return Response(
        {
            'message': message_data,
            'room': ChatRoomSerializer(room, context={'request': request}).data,
        },
        status=status.HTTP_201_CREATED,
    )
