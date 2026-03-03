from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from .views import(
                   login_view, 
                   register_user, 
                   student_dashboard, 
                   SearchTutorsView,
                   SubjectListView, template_availability, tutor_availability, 
                   tutor_dashboard,
                    tutor_detail,
                    list_bookings,
                    approve_booking,
                    reject_booking,
                    booking_detail,
                   )
from . import views

print("STUDYBUDDY URLS LOADED")

urlpatterns = [
    #Base
    path('register/', register_user),
    path('login/', login_view),
    path('dashboard/', student_dashboard),
    path('search-tutors/', SearchTutorsView.as_view(), name='search-tutors'),
    path('subjects/',SubjectListView.as_view(), name='subjects'),
    path('tutor-dashboard/', tutor_dashboard, name='tutor-dashboard'),
    path('tutors/<int:profile_id>/', tutor_detail),
    path('tutors/<int:tutor_id>/availability/', tutor_availability),

    path('bookings/', views.list_bookings),
    path('bookings/<int:booking_id>/', views.booking_detail),
    path('payment-methods/', views.payment_methods),

    #Dynamic

    path('bookings/confirm/', views.confirm_payment_and_book),
    path('bookings/<int:booking_id>/complete/', views.complete_session),
    path('template-availability/', template_availability),
    path('template-availability/<int:pk>/', template_availability),
    path('bookings/<int:booking_id>/approve/', views.approve_booking),
    path('bookings/<int:booking_id>/reject/', views.reject_booking),
   
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)