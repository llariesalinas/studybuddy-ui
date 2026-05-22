import json
from urllib.parse import parse_qs
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
from .models import ChatRoom, Message
from .services import (
    broadcast_message,
    get_participant_profile_ids,
    get_participant_user_ids,
    touch_room,
)

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        token = self.get_token_from_query()

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
        event_type = data.get('type', 'message')

        if event_type == 'typing':
            await self.broadcast_typing(bool(data.get('is_typing')))
            return

        if event_type == 'read':
            receipt = await self.mark_messages_read()
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_event',
                    'event': receipt,
                }
            )
            for user_id in receipt.get('participant_user_ids', []):
                await self.channel_layer.group_send(
                    f'chat_user_{user_id}',
                    {
                        'type': 'user_event',
                        'event': receipt,
                    }
                )
            return

        message = str(data.get('message') or '').strip()

        if not message:
            return

        # Save message to DB
        saved_msg = await self.save_message(self.user, self.room_id, message)
        await self.broadcast_saved_message(saved_msg.id)

    async def chat_event(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event['event']))

    def get_token_from_query(self):
        query_string = self.scope.get('query_string', b'').decode()
        return parse_qs(query_string).get('token', [None])[0]

    async def broadcast_typing(self, is_typing):
        sender_info = await self.get_sender_info(self.user)
        event = {
            'type': 'typing',
            'room_id': int(self.room_id),
            'sender_id': self.user.id,
            'sender_profile_id': sender_info['profile_id'],
            'sender_name': sender_info['name'],
            'is_typing': is_typing,
        }

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_event',
                'event': event,
            }
        )

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
        message = Message.objects.create(
            room=room,
            sender=user,
            content=content,
            message_type='text'
        )
        touch_room(room)
        return message

    @database_sync_to_async
    def broadcast_saved_message(self, message_id):
        message = Message.objects.select_related('room', 'sender').get(id=message_id)
        broadcast_message(message.room, message)

    @database_sync_to_async
    def mark_messages_read(self):
        room = ChatRoom.objects.get(id=self.room_id)
        updated = room.messages.filter(is_read=False).exclude(sender=self.user).update(
            is_read=True,
            read_at=timezone.now()
        )
        return {
            'type': 'read_receipt',
            'room_id': room.id,
            'reader_id': self.user.id,
            'participant_user_ids': get_participant_user_ids(room),
            'participant_profile_ids': get_participant_profile_ids(room),
            'updated': updated,
        }


class ChatUpdatesConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        token = self.get_token_from_query()
        self.user = await self.get_user_from_token(token)

        if self.user == AnonymousUser():
            await self.close()
            return

        self.group_name = f'chat_user_{self.user.id}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def user_event(self, event):
        await self.send(text_data=json.dumps(event['event']))

    def get_token_from_query(self):
        query_string = self.scope.get('query_string', b'').decode()
        return parse_qs(query_string).get('token', [None])[0]

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
