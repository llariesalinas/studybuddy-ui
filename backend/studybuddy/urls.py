from django.urls import path
from .views import login_view, register_user

urlpatterns = [
  
    path('register/', register_user),
    path('login/', login_view),
]