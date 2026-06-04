from django.urls import path
from . import views

urlpatterns = [
    path('rooms/', views.list_chat_rooms, name='chat-rooms'),
    path('rooms/<int:room_id>/', views.get_room_detail, name='chat-room-detail'),
    path('rooms/<int:room_id>/history/', views.get_message_history, name='chat-history'),
    path('rooms/<int:room_id>/messages/', views.send_message, name='chat-send-message'),
    path('rooms/<int:room_id>/read/', views.mark_room_read, name='chat-read'),
    path('start/<int:tutor_profile_id>/', views.start_inquiry_chat, name='chat-start'),
]
