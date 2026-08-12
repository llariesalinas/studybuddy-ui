from datetime import datetime, timedelta

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models import Q
from django.utils import timezone

from studybuddy.models import Booking, Tutor, TutorSubjects, UserProfile

from .models import ChatRoom, Message

SESSION_SLOT_MINUTES = 60


def full_name(profile):
    if not profile:
        return ''
    return f"{profile.fname} {profile.lname}".strip()


def get_canonical_room(tutee, tutor):
    room = ChatRoom.objects.filter(tutee=tutee, tutor=tutor, booking__isnull=True).first()

    if room:
        return room

    return ChatRoom.objects.create(tutee=tutee, tutor=tutor, booking=None)


def get_canonical_room_for_booking(booking):
    return get_canonical_room(booking.student, booking.tutor.profile)


def get_participant_user_ids(room):
    return [
        user_id
        for user_id in [room.tutee.user_id, room.tutor.user_id if room.tutor else None]
        if user_id
    ]


def get_participant_profile_ids(room):
    return [profile_id for profile_id in [room.tutee_id, room.tutor_id] if profile_id]


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
        'subject',
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


def get_booking_context_group_key(booking):
    if booking.booking_request_id:
        return ('booking_request_id', booking.booking_request_id)
    if booking.session_group_id:
        return ('session_group_id', booking.session_group_id)
    return ('id', booking.id)


def serialize_booking_context(booking, grouped_bookings=None):
    bookings = grouped_bookings if grouped_bookings is not None else get_booking_group(booking)

    if not bookings:
        return None

    representative = bookings[0]
    time_blocks = split_time_blocks(bookings)
    primary_block = time_blocks[0]
    subject = (
        representative.subject.subject_name
        if representative.subject
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
        # One server-side answer to "may the tutor still fix the meeting spot", read by both the
        # chat banner and the booking card so they cannot drift apart.
        'can_edit_location': representative.tutor_can_edit_location(),
        'session_mode': representative.session_mode,
        'meeting_link': representative.meeting_link,
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
        .filter(Q(status='Pending') | Q(status='Confirmed') | Q(session_date__gte=current_date))
        .select_related('availability', 'student', 'tutor__profile__course', 'subject')
        .order_by('session_date', 'availability__time_slot', 'id')
        .first()
    )

    if booking:
        context = serialize_booking_context(booking)

        if context is None:
            return None

        if booking.status == 'Pending':
            context['status_intent'] = (
                'pending_location' if booking.session_mode == 'F2F' else 'pending'
            )
        elif booking.status == 'Confirmed':
            session_naive = datetime.combine(booking.session_date, booking.availability.time_slot)
            session_start = timezone.make_aware(session_naive)
            duration_minutes = context.get('duration_hours', 0.5) * 60
            session_end = session_start + timedelta(minutes=duration_minutes)
            now = timezone.now()

            if now < session_start:
                context['status_intent'] = 'confirmed'
                context['status'] = 'Upcoming'
            elif session_start <= now <= session_end:
                context['status_intent'] = 'ongoing'
                context['status'] = 'Ongoing'
            else:
                context['status_intent'] = 'payment_required'
                context['status'] = 'Payment Required'
        else:
            context['status_intent'] = 'awaiting_payment'

        return context

    completed = (
        Booking.objects
        .filter(
            student=room.tutee,
            tutor__profile=room.tutor,
            status='Completed',
        )
        .exclude(rating__isnull=False)
        .select_related('availability', 'student', 'tutor__profile__course', 'subject')
        .order_by('-session_date', '-availability__time_slot', '-id')
        .first()
    )

    if completed:
        context = serialize_booking_context(completed)

        if context is None:
            return None

        context['status_intent'] = 'review_pending'
        return context

    week_ago = current_date - timedelta(days=7)
    terminal = (
        Booking.objects
        .filter(
            student=room.tutee,
            tutor__profile=room.tutor,
            status__in=['Rejected', 'Cancelled'],
            session_date__gte=week_ago,
        )
        .select_related('availability', 'student', 'tutor__profile__course', 'subject')
        .order_by('-session_date', '-availability__time_slot', '-id')
        .first()
    )

    if terminal:
        context = serialize_booking_context(terminal)

        if context is None:
            return None

        context['status_intent'] = terminal.status.lower()
        return context

    return None


def get_current_booking_contexts(rooms):
    room_list = list(rooms)
    if not room_list:
        return {}

    room_pairs = {
        (room.tutee_id, room.tutor_id)
        for room in room_list
        if room.tutee_id and room.tutor_id
    }
    if not room_pairs:
        return {room.id: None for room in room_list}

    tutee_ids = {tutee_id for tutee_id, _ in room_pairs}
    tutor_profile_ids = {tutor_id for _, tutor_id in room_pairs}
    current_date = timezone.localdate()

    def booking_pair(booking):
        return (booking.student_id, booking.tutor.profile_id)

    def base_booking_query():
        return (
            Booking.objects
            .filter(student_id__in=tutee_ids, tutor__profile_id__in=tutor_profile_ids)
            .select_related('availability', 'student', 'tutor__profile__course', 'subject')
        )

    selected = {}

    active_bookings = (
        base_booking_query()
        .filter(
            status__in=['Pending', 'Confirmed', 'Awaiting Payment Verification'],
        )
        .filter(Q(status='Pending') | Q(status='Confirmed') | Q(session_date__gte=current_date))
        .order_by('session_date', 'availability__time_slot', 'id')
    )
    for booking in active_bookings:
        pair = booking_pair(booking)
        if pair in room_pairs and pair not in selected:
            selected[pair] = booking

    missing_pairs = room_pairs - set(selected.keys())
    if missing_pairs:
        completed_bookings = (
            base_booking_query()
            .filter(status='Completed')
            .exclude(rating__isnull=False)
            .order_by('-session_date', '-availability__time_slot', '-id')
        )
        for booking in completed_bookings:
            pair = booking_pair(booking)
            if pair in missing_pairs and pair not in selected:
                selected[pair] = booking

    missing_pairs = room_pairs - set(selected.keys())
    if missing_pairs:
        week_ago = current_date - timedelta(days=7)
        terminal_bookings = (
            base_booking_query()
            .filter(status__in=['Rejected', 'Cancelled'], session_date__gte=week_ago)
            .order_by('-session_date', '-availability__time_slot', '-id')
        )
        for booking in terminal_bookings:
            pair = booking_pair(booking)
            if pair in missing_pairs and pair not in selected:
                selected[pair] = booking

    grouped_bookings = get_booking_groups_for_contexts(selected.values())
    context_by_pair = {}
    for pair, booking in selected.items():
        context = serialize_booking_context(
            booking,
            grouped_bookings.get(get_booking_context_group_key(booking), [booking]),
        )
        if context is None:
            context_by_pair[pair] = None
            continue

        if booking.status == 'Pending':
            context['status_intent'] = (
                'pending_location' if booking.session_mode == 'F2F' else 'pending'
            )
        elif booking.status == 'Confirmed':
            session_naive = datetime.combine(booking.session_date, booking.availability.time_slot)
            session_start = timezone.make_aware(session_naive)
            duration_minutes = context.get('duration_hours', 0.5) * 60
            session_end = session_start + timedelta(minutes=duration_minutes)
            now = timezone.now()

            if now < session_start:
                context['status_intent'] = 'confirmed'
                context['status'] = 'Upcoming'
            elif session_start <= now <= session_end:
                context['status_intent'] = 'ongoing'
                context['status'] = 'Ongoing'
            else:
                context['status_intent'] = 'payment_required'
                context['status'] = 'Payment Required'
        elif booking.status == 'Awaiting Payment Verification':
            context['status_intent'] = 'awaiting_payment'
        elif booking.status == 'Completed':
            context['status_intent'] = 'review_pending'
        else:
            context['status_intent'] = booking.status.lower()

        context_by_pair[pair] = context

    return {
        room.id: context_by_pair.get((room.tutee_id, room.tutor_id))
        for room in room_list
    }


def get_booking_groups_for_contexts(bookings):
    booking_list = list(bookings)
    if not booking_list:
        return {}

    booking_request_ids = {
        booking.booking_request_id
        for booking in booking_list
        if booking.booking_request_id
    }
    session_group_ids = {
        booking.session_group_id
        for booking in booking_list
        if not booking.booking_request_id and booking.session_group_id
    }
    booking_ids = {
        booking.id
        for booking in booking_list
        if not booking.booking_request_id and not booking.session_group_id
    }

    filters = Q()
    has_filter = False
    if booking_request_ids:
        filters |= Q(booking_request_id__in=booking_request_ids)
        has_filter = True
    if session_group_ids:
        filters |= Q(session_group_id__in=session_group_ids)
        has_filter = True
    if booking_ids:
        filters |= Q(id__in=booking_ids)
        has_filter = True

    if not has_filter:
        return {}

    groups = {}
    for booking in (
        Booking.objects
        .filter(filters)
        .select_related('availability', 'student', 'tutor__profile__course', 'subject')
    ):
        groups.setdefault(get_booking_context_group_key(booking), []).append(booking)

    return {
        key: sort_bookings(group)
        for key, group in groups.items()
    }



def get_completed_session_key(booking):
    return str(booking.session_group_id or booking.booking_request_id or booking.id)


_CURRENT_BOOKING_UNSET = object()


def get_partner_context(room, user=None, current_booking=_CURRENT_BOOKING_UNSET):
    if room.room_type == 'support':
        return {
            'partner_name': 'Support Team',
            'partner_initials': 'ST',
            'partner_subtitle': 'Platform Support',
            'sessions_together': 0,
            'focused_hours': 0,
            'topics': [],
        }

    tutor = Tutor.objects.filter(profile=room.tutor).select_related('profile__course').first()
    completed_bookings = list(
        Booking.objects
        .filter(
            student=room.tutee,
            tutor=tutor,
            status='Completed',
        )
        .select_related('availability', 'tutor__profile__course')
        .order_by('session_date', 'availability__time_slot', 'id')
    ) if tutor else []
    session_keys = {get_completed_session_key(booking) for booking in completed_bookings}
    topics = []

    if tutor:
        topics = list(
            TutorSubjects.objects
            .filter(tutor=tutor)
            .select_related('subject')
            .order_by('subject__subject_name')
            .values_list('subject__subject_name', flat=True)
            .distinct()
        )

    if not topics:
        if current_booking is _CURRENT_BOOKING_UNSET:
            current_booking = get_current_booking_context(room)
        if current_booking and current_booking.get('subject') != 'General':
            topics = [current_booking['subject']]

    partner = room.tutor
    if user and user.is_authenticated:
        try:
            user_profile = user.userprofile
            if user_profile.id == room.tutor_id:
                partner = room.tutee
        except Exception:
            partner = room.tutor

    if partner is None:
        return {
            'partner_name': 'Support Team',
            'partner_initials': 'ST',
            'partner_subtitle': 'Platform Support',
            'sessions_together': 0,
            'focused_hours': 0,
            'topics': [],
        }

    subtitle_parts = []
    if partner.role:
        subtitle_parts.append(partner.role)
    if partner.course:
        subtitle_parts.append(partner.course.course_name)
    elif partner.year_level:
        subtitle_parts.append(f'Year {partner.year_level}')

    return {
        'partner_name': full_name(partner),
        'partner_initials': ''.join(
            part[0] for part in full_name(partner).split() if part
        )[:2].upper(),
        'partner_subtitle': ' - '.join(subtitle_parts),
        'sessions_together': len(session_keys),
        'focused_hours': len(completed_bookings) * (SESSION_SLOT_MINUTES / 60),
        'topics': topics[:6],
    }


def get_ticket_context(room):
    ticket = getattr(room, 'ticket', None)
    if not ticket:
        return None

    agent = ticket.assigned_agent
    return {
        'id': ticket.id,
        'subject': ticket.subject,
        'category': ticket.get_category_display(),
        'status': ticket.status,
        'created_at': ticket.created_at.isoformat() if ticket.created_at else None,
        'assigned_agent_name': full_name(agent) if agent else None,
    }


def serialize_message_payload(message, user=None):
    sender_name = ''
    sender_profile_id = None

    try:
        sender_profile = message.sender.userprofile
        sender_name = full_name(sender_profile)
        sender_profile_id = sender_profile.id
    except Exception:
        try:
            sender_name = message.sender.get_username()
        except Exception:
            sender_name = 'System'

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
        'is_me': message.sender_id == user.id if user and user.is_authenticated else None,
    }


def serialize_room_payload(room, user=None):
    last_message = room.messages.order_by('-created_at').first()
    unread_count = 0
    ticket_context = get_ticket_context(room)

    if user and user.is_authenticated:
        unread_count = room.messages.filter(is_read=False).exclude(sender=user).count()

    return {
        'id': room.id,
        'tutee': room.tutee_id,
        'tutor': room.tutor_id,
        'booking': room.booking_id,
        'created_at': room.created_at.isoformat(),
        'updated_at': room.updated_at.isoformat() if room.updated_at else None,
        'room_type': room.room_type,
        'tutee_name': full_name(room.tutee),
        'tutor_name': full_name(room.tutor) if room.tutor else 'Support Agent',
        'last_message': serialize_message_payload(last_message, user) if last_message else None,
        'unread_count': unread_count,
        'current_booking': get_current_booking_context(room),
        'partner_context': get_partner_context(room, user),
        'ticket_status': ticket_context['status'] if ticket_context else None,
        'ticket_context': ticket_context,
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


def create_chat_message(
    room,
    sender,
    content,
    message_type='text',
    metadata=None,
    broadcast=True,
    temp_id=None,
):
    message = Message.objects.create(
        room=room,
        sender=sender,
        content=content,
        message_type=message_type,
        metadata=metadata or {},
    )
    touch_room(room)

    if broadcast:
        broadcast_message(room, message, temp_id=temp_id)

    return message


def broadcast_message(room, message, temp_id=None):
    message_payload = serialize_message_payload(message)
    if temp_id:
        message_payload['temp_id'] = temp_id

    event = {
        'type': 'message',
        'room_id': room.id,
        'message': message_payload,
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
