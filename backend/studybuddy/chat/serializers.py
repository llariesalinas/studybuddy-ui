from rest_framework import serializers
from .models import ChatRoom, Message
from django.contrib.auth.models import User

class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    is_me = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['id', 'sender', 'sender_name', 'content', 'created_at', 'is_read', 'is_me']

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

    class Meta:
        model = ChatRoom
        fields = ['id', 'tutee', 'tutor', 'booking', 'created_at', 'tutee_name', 'tutor_name', 'last_message']

    def get_tutee_name(self, obj):
        return f"{obj.tutee.fname} {obj.tutee.lname}"

    def get_tutor_name(self, obj):
        return f"{obj.tutor.fname} {obj.tutor.lname}"

    def get_last_message(self, obj):
        last_msg = obj.messages.order_by('-created_at').first()
        if last_msg:
            return MessageSerializer(last_msg, context=self.context).data
        return None
