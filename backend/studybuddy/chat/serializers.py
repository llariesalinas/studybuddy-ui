from rest_framework import serializers
from .models import ChatRoom, Message
from .services import get_current_booking_context

class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    is_me = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            'id',
            'room',
            'sender',
            'sender_name',
            'content',
            'message_type',
            'metadata',
            'created_at',
            'is_read',
            'read_at',
            'is_me',
        ]

    def get_sender_name(self, obj):
        try:
            profile = obj.sender.userprofile
            return f"{profile.fname} {profile.lname}"
        except Exception:
            return obj.sender.username

    def get_is_me(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.sender_id == request.user.id
        return False

class ChatRoomSerializer(serializers.ModelSerializer):
    tutee_name = serializers.SerializerMethodField()
    tutor_name = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    current_booking = serializers.SerializerMethodField()

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
        ]

    def get_tutee_name(self, obj):
        return f"{obj.tutee.fname} {obj.tutee.lname}"

    def get_tutor_name(self, obj):
        return f"{obj.tutor.fname} {obj.tutor.lname}"

    def get_last_message(self, obj):
        last_msg = obj.messages.order_by('-created_at').first()
        if last_msg:
            return MessageSerializer(last_msg, context=self.context).data
        return None

    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.messages.filter(is_read=False).exclude(sender=request.user).count()
        return 0

    def get_current_booking(self, obj):
        return get_current_booking_context(obj)
