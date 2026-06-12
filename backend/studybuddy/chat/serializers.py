from rest_framework import serializers
from .models import ChatRoom, Message
from .services import get_current_booking_context, get_partner_context

class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    sender_profile_id = serializers.SerializerMethodField()
    is_me = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            'id',
            'room',
            'sender',
            'sender_name',
            'sender_profile_id',
            'content',
            'message_type',
            'metadata',
            'created_at',
            'is_read',
            'read_at',
            'is_me',
        ]

    def get_sender_name(self, obj):
        # System messages (e.g. support-ticket events) have no sender; serializing
        # them must never dereference a missing sender, or the whole endpoint 500s.
        if not obj.sender:
            return "System"
        try:
            profile = obj.sender.userprofile
            return f"{profile.fname} {profile.lname}"
        except Exception:
            pass
        try:
            return obj.sender.username
        except Exception:
            return 'System'

    def get_sender_profile_id(self, obj):
        try:
            return obj.sender.userprofile.id
        except Exception:
            return None

    def get_sender_profile_id(self, obj):
        if not obj.sender:
            return None
        try:
            return obj.sender.userprofile.id
        except Exception:
            return None

    def get_is_me(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.sender_id == request.user.id
        return None

class ChatRoomSerializer(serializers.ModelSerializer):
    tutee_name = serializers.SerializerMethodField()
    tutor_name = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    current_booking = serializers.SerializerMethodField()
    partner_context = serializers.SerializerMethodField()
    ticket_status = serializers.SerializerMethodField()
    ticket = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = [
            'id',
            'tutee',
            'tutor',
            'booking',
            'created_at',
            'updated_at',
            'room_type',
            'tutee_name',
            'tutor_name',
            'last_message',
            'unread_count',
            'current_booking',
            'partner_context',
            'ticket_status',
            'ticket',
        ]

    def get_ticket_status(self, obj):
        if hasattr(obj, 'ticket') and obj.ticket:
            return obj.ticket.status
        return None

    def get_ticket(self, obj):
        if hasattr(obj, 'ticket') and obj.ticket:
            ticket = obj.ticket
            return {
                'id': ticket.id,
                'subject': ticket.subject,
                'category': ticket.category,
                'status': ticket.status,
                'description': ticket.description,
            }
        return None

    def _current_booking(self, obj):
        # Memoize per room so current_booking and partner_context don't both
        # recompute the (expensive) current-booking lookup.
        booking_map = self.context.get('current_booking_map')
        if booking_map is not None:
            return booking_map.get(obj.id)

        cache = self.context.setdefault('_booking_ctx_cache', {})
        if obj.id not in cache:
            cache[obj.id] = get_current_booking_context(obj)
        return cache[obj.id]

    def get_tutee_name(self, obj):
        if obj.tutee:
            return f"{obj.tutee.fname} {obj.tutee.lname}"
        return "User"

    def get_tutor_name(self, obj):
        if obj.room_type == 'support':
            if obj.tutor:
                return f"{obj.tutor.fname} {obj.tutor.lname}"
            return "Support Agent"
        if obj.tutor:
            return f"{obj.tutor.fname} {obj.tutor.lname}"
        return "Tutor"

    def get_last_message(self, obj):
        last_map = self.context.get('last_message_map')
        if last_map is not None:
            last_msg = last_map.get(obj.id)
        else:
            last_msg = obj.messages.order_by('-created_at').first()
        if last_msg:
            return MessageSerializer(last_msg, context=self.context).data
        return None

    def get_unread_count(self, obj):
        unread_map = self.context.get('unread_map')
        if unread_map is not None:
            return unread_map.get(obj.id, 0)
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.messages.filter(is_read=False).exclude(sender=request.user).count()
        return 0

    def get_current_booking(self, obj):
        return self._current_booking(obj)

    def get_partner_context(self, obj):
        # The sidebar list never renders partner_context; it's only shown for the
        # opened room (fetched via the room-detail endpoint). Skipping it here
        # removes the bulk of the per-room queries.
        if self.context.get('skip_partner_context'):
            return None
        request = self.context.get('request')
        user = request.user if request and request.user.is_authenticated else None
        return get_partner_context(obj, user, current_booking=self._current_booking(obj))
