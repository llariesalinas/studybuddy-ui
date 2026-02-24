from django.urls import path
from .views import get_users, register_user

urlpatterns = [
    path('users/', get_users),
    path('register/', register_user),
]