import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
from .models import ChatRoom, Message

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        # Get token from query string
        query_string = self.scope.get('query_string', b'').decode()
        token = None
        for param in query_string.split('&'):
            if param.startswith('token='):
                token = param.split('=')[1]
                break

        # Validate User
        self.user = await self.get_user_from_token(token)
        
        if self.user == AnonymousUser() or not await self.is_member(self.user, self.room_id):
            await self.close()
        else:
            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message')
        
        if not message:
            return

        # Save message to DB
        saved_msg = await self.save_message(self.user, self.room_id, message)
        
        # Get profile for name and ID safely
        sender_info = await self.get_sender_info(self.user)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'id': saved_msg.id,
                'message': message,
                'sender_id': self.user.id,
                'sender_profile_id': sender_info['profile_id'],
                'sender_name': sender_info['name'],
                'created_at': saved_msg.created_at.isoformat()
            }
        )

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'id': event['id'],
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sender_profile_id': event['sender_profile_id'],
            'sender_name': event['sender_name'],
            'created_at': event['created_at']
        }))

    @database_sync_to_async
    def get_sender_info(self, user):
        try:
            profile = user.userprofile
            return {
                'name': f"{profile.fname} {profile.lname}",
                'profile_id': profile.id
            }
        except Exception:
            return {
                'name': user.email,
                'profile_id': None
            }

    @database_sync_to_async
    def get_user_from_token(self, token):
        if not token:
            return AnonymousUser()
        try:
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            return User.objects.get(id=user_id)
        except Exception:
            return AnonymousUser()

    @database_sync_to_async
    def is_member(self, user, room_id):
        try:
            room = ChatRoom.objects.get(id=room_id)
            # Try to get profile
            try:
                user_profile = user.userprofile
            except Exception:
                return False
                
            return room.tutee_id == user_profile.id or room.tutor_id == user_profile.id
        except ChatRoom.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, user, room_id, content):
        room = ChatRoom.objects.get(id=room_id)
        return Message.objects.create(
            room=room,
            sender=user,
            content=content
        )
