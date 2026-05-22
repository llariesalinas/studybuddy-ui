from datetime import datetime, timedelta

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models import Q
from django.utils import timezone

from studybuddy.models import Booking, Tutor, UserProfile

from .models import ChatRoom, Message

SESSION_SLOT_MINUTES = 30


def full_name(profile):
    return f"{profile.fname} {profile.lname}".strip()


def get_canonical_room(tutee, tutor):
    room = ChatRoom.objects.filter(tutee=tutee, tutor=tutor, booking__isnull=True).first()

    if room:
        return room

    return ChatRoom.objects.create(tutee=tutee, tutor=tutor, booking=None)


def get_canonical_room_for_booking(booking):
    return get_canonical_room(booking.student, booking.tutor.profile)


def get_participant_user_ids(room):
    return [room.tutee.user_id, room.tutor.user_id]


def get_participant_profile_ids(room):
    return [room.tutee_id, room.tutor_id]


def user_is_room_member(user, room):
    try:
        profile = user.userprofile
    except Exception:
        return False

    return room.tutee_id == profile.id or room.tutor_id == profile.id


def sort_bookings(bookings):
    return sorted(bookings, key=lambda booking: (
        booking.session_date,
        booking.availability.time_slot,
        booking.id,
    ))


def get_booking_group(booking):
    if booking.booking_request_id:
        bookings = Booking.objects.filter(booking_request_id=booking.booking_request_id)
    elif booking.session_group_id:
        bookings = Booking.objects.filter(session_group_id=booking.session_group_id)
    else:
        bookings = Booking.objects.filter(id=booking.id)

    return sort_bookings(bookings.select_related(
        'availability',
        'student',
        'tutor__profile__course',
    ))


def split_time_blocks(bookings):
    sorted_bookings = sort_bookings(bookings)

    if not sorted_bookings:
        return []

    blocks = []
    current = [sorted_bookings[0]]

    for booking in sorted_bookings[1:]:
        previous = current[-1]
        previous_end = (
            datetime.combine(previous.session_date, previous.availability.time_slot)
            + timedelta(minutes=SESSION_SLOT_MINUTES)
        ).time()

        if previous.session_date == booking.session_date and previous_end == booking.availability.time_slot:
            current.append(booking)
            continue

        blocks.append(current)
        current = [booking]

    blocks.append(current)

    return [serialize_time_block(block) for block in blocks]


def serialize_time_block(bookings):
    sorted_bookings = sort_bookings(bookings)
    first = sorted_bookings[0]
    last = sorted_bookings[-1]
    end_time = (
        datetime.combine(last.session_date, last.availability.time_slot)
        + timedelta(minutes=SESSION_SLOT_MINUTES)
    ).time()

    return {
        'date': first.session_date.isoformat(),
        'startTime': first.availability.time_slot.strftime('%H:%M'),
        'endTime': end_time.strftime('%H:%M'),
        'duration_hours': len(sorted_bookings) * (SESSION_SLOT_MINUTES / 60),
    }


def serialize_booking_context(booking):
    bookings = get_booking_group(booking)

    if not bookings:
        return None

    representative = bookings[0]
    time_blocks = split_time_blocks(bookings)
    primary_block = time_blocks[0]
    subject = (
        representative.tutor.profile.course.course_name
        if representative.tutor.profile.course
        else 'General'
    )

    return {
        'id': representative.id,
        'booking_request_id': (
            str(representative.booking_request_id)
            if representative.booking_request_id
            else None
        ),
        'session_group_id': (
            str(representative.session_group_id)
            if representative.session_group_id
            else None
        ),
        'status': representative.status,
        'raw_status': representative.status,
        'subject': subject,
        'date': representative.session_date.isoformat(),
        'startTime': primary_block['startTime'],
        'endTime': primary_block['endTime'],
        'duration_hours': len(bookings) * (SESSION_SLOT_MINUTES / 60),
        'preferred_location': representative.preferred_location,
        'session_mode': representative.session_mode,
        'student': full_name(representative.student),
        'tuteeName': full_name(representative.student),
        'tutor': full_name(representative.tutor.profile),
        'time_blocks': time_blocks,
        'hasMultipleTimeBlocks': len(time_blocks) > 1,
        'detail_url': f'/booking-details/{representative.id}',
        'tutee_detail_url': f'/tuteeSessionDetails/{representative.id}',
    }


def get_current_booking_context(room):
    current_date = timezone.localdate()
    booking = (
        Booking.objects
        .filter(
            student=room.tutee,
            tutor__profile=room.tutor,
            status__in=['Pending', 'Confirmed', 'Awaiting Payment Verification'],
        )
        .filter(Q(status='Pending') | Q(session_date__gte=current_date))
        .select_related('availability', 'student', 'tutor__profile__course')
        .order_by('session_date', 'availability__time_slot', 'id')
        .first()
    )

    if not booking:
        return None

    return serialize_booking_context(booking)


def serialize_message_payload(message, user=None):
    sender_name = ''
    sender_profile_id = None

    try:
        sender_profile = message.sender.userprofile
        sender_name = full_name(sender_profile)
        sender_profile_id = sender_profile.id
    except Exception:
        sender_name = message.sender.get_username()

    return {
        'id': message.id,
        'room': message.room_id,
        'sender': message.sender_id,
        'sender_id': message.sender_id,
        'sender_profile_id': sender_profile_id,
        'sender_name': sender_name,
        'content': message.content,
        'message': message.content,
        'message_type': message.message_type,
        'metadata': message.metadata or {},
        'created_at': message.created_at.isoformat(),
        'is_read': message.is_read,
        'read_at': message.read_at.isoformat() if message.read_at else None,
        'is_me': message.sender_id == user.id if user and user.is_authenticated else False,
    }


def serialize_room_payload(room, user=None):
    last_message = room.messages.order_by('-created_at').first()
    unread_count = 0

    if user and user.is_authenticated:
        unread_count = room.messages.filter(is_read=False).exclude(sender=user).count()

    return {
        'id': room.id,
        'tutee': room.tutee_id,
        'tutor': room.tutor_id,
        'booking': room.booking_id,
        'created_at': room.created_at.isoformat(),
        'updated_at': room.updated_at.isoformat() if room.updated_at else None,
        'tutee_name': full_name(room.tutee),
        'tutor_name': full_name(room.tutor),
        'last_message': serialize_message_payload(last_message, user) if last_message else None,
        'unread_count': unread_count,
        'current_booking': get_current_booking_context(room),
    }


def broadcast_to_room_and_users(room, event):
    channel_layer = get_channel_layer()

    if not channel_layer:
        return

    async_to_sync(channel_layer.group_send)(
        f'chat_{room.id}',
        {
            'type': 'chat_event',
            'event': event,
        }
    )

    for user_id in get_participant_user_ids(room):
        async_to_sync(channel_layer.group_send)(
            f'chat_user_{user_id}',
            {
                'type': 'user_event',
                'event': event,
            }
        )


def touch_room(room):
    room.updated_at = timezone.now()
    room.save(update_fields=['updated_at'])


def create_chat_message(room, sender, content, message_type='text', metadata=None, broadcast=True):
    message = Message.objects.create(
        room=room,
        sender=sender,
        content=content,
        message_type=message_type,
        metadata=metadata or {},
    )
    touch_room(room)

    if broadcast:
        broadcast_message(room, message)

    return message


def broadcast_message(room, message):
    event = {
        'type': 'message',
        'room_id': room.id,
        'message': serialize_message_payload(message),
        'room': serialize_room_payload(room),
    }
    broadcast_to_room_and_users(room, event)


def broadcast_room_updated(room):
    event = {
        'type': 'room_updated',
        'room_id': room.id,
        'room': serialize_room_payload(room),
    }
    broadcast_to_room_and_users(room, event)


def broadcast_booking_context_updated(room):
    event = {
        'type': 'booking_context_updated',
        'room_id': room.id,
        'room': serialize_room_payload(room),
        'booking': get_current_booking_context(room),
    }
    broadcast_to_room_and_users(room, event)


def create_booking_event(booking, actor, content, event_type):
    room = get_canonical_room_for_booking(booking)
    metadata = {
        'event_type': event_type,
        'booking': serialize_booking_context(booking),
    }
    message = create_chat_message(
        room=room,
        sender=actor,
        content=content,
        message_type='booking_event',
        metadata=metadata,
        broadcast=True,
    )
    broadcast_booking_context_updated(room)
    return message


def get_room_for_tutor_profile(tutee_profile, tutor_profile_id):
    tutor_profile = UserProfile.objects.get(id=tutor_profile_id, role='Tutor')
    tutor = Tutor.objects.get(profile=tutor_profile)
    return get_canonical_room(tutee_profile, tutor.profile)
