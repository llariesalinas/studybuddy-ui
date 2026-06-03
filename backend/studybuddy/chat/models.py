from django.db import models
from django.conf import settings
from django.utils import timezone
from studybuddy.models import Booking, UserProfile

class ChatRoom(models.Model):
    # Participants in the chat
    tutee = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='tutee_chat_rooms')
    tutor = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='tutor_chat_rooms', null=True)
    
    # Optional booking. If present, it's a booking-specific chat.
    # If null, it's a pre-booking inquiry.
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='chat_room', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(default=timezone.now)

    ROOM_TYPES = [
        ('regular', 'Regular'),
        ('support', 'Support'),
    ]

    room_type = models.CharField(max_length=10, choices=ROOM_TYPES, default='regular')

    class Meta:
        constraints = [
            # Ensure only one "inquiry" chat (no booking) exists between a tutee and tutor
            models.UniqueConstraint(
                fields=['tutee', 'tutor'],
                condition=models.Q(booking__isnull=True),
                name='unique_inquiry_chat'
            )
        ]

    def __str__(self):
        if self.booking:
            return f"Chat for Booking {self.booking.id} ({self.tutee.fname} & {self.tutor.fname})"
        return f"Inquiry Chat: {self.tutee.fname} & {self.tutor.fname}"

class Message(models.Model):
    MESSAGE_TYPES = [
        ('text', 'Text'),
        ('system', 'System'),
        ('booking_event', 'Booking event'),
    ]

    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages', null=True, blank=True)
    content = models.TextField()
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='text')
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender.username}: {self.content[:20]}"
