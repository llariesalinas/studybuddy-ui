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

    class Meta:
        model = ChatRoom
        fields = [
            'id',
            'tutee',
            'tutor',
            'booking',
            'created_at',
            'updated_at',
            'tutee_name',
            'tutor_name',
            'last_message',
            'unread_count',
            'current_booking',
            'partner_context',
        ]

    def _current_booking(self, obj):
        # Memoize per room so current_booking and partner_context don't both
        # recompute the (expensive) current-booking lookup.
        cache = self.context.setdefault('_booking_ctx_cache', {})
        if obj.id not in cache:
            cache[obj.id] = get_current_booking_context(obj)
        return cache[obj.id]

    def get_tutee_name(self, obj):
        return f"{obj.tutee.fname} {obj.tutee.lname}"

    def get_tutor_name(self, obj):
        return f"{obj.tutor.fname} {obj.tutor.lname}"

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
