from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from .views import( login_view, 
                   register_user, 
                   student_dashboard, 
                   SearchTutorsView,
                   SubjectListView, tutor_availability, 
                   tutor_dashboard,
                    tutor_detail
                   )
from . import views

urlpatterns = [
  
    path('register/', register_user),
    path('login/', login_view),
    path('dashboard/', student_dashboard),
    path('search-tutors/', SearchTutorsView.as_view(), name='search-tutors'),
    path('subjects/',SubjectListView.as_view(), name='subjects'),
    path('tutor-dashboard/', tutor_dashboard, name='tutor-dashboard'),
    path('tutors/<int:profile_id>/', tutor_detail),
    path('tutors/<int:tutor_id>/availability/', tutor_availability),
    #path('bookings/bulk/', views.bulk_booking),
    #path('bookings/',create_booking),
    path('bookings/confirm/', views.confirm_payment_and_book),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)