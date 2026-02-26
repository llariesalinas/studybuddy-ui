from django.urls import path
from .views import( login_view, 
                   register_user, 
                   student_dashboard, 
                   SearchTutorsView,
                   SubjectListView
                   )

urlpatterns = [
  
    path('register/', register_user),
    path('login/', login_view),
    path('dashboard/', student_dashboard),
    path('search-tutors/', SearchTutorsView.as_view(), name='search-tutors'),
    path('subjects/',SubjectListView.as_view(), name='subjects'),
]