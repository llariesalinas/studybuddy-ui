from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from .views import(
                   complete_booking,
                   list_courses,
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
                    setup_profile,
                    profile_status,
                    get_tutor_profile
                   )
from . import views

print("STUDYBUDDY URLS LOADED")

urlpatterns = [
    #Base
    path('register/', register_user),
    path('login/', login_view),
    
    path('profile/status/', views.profile_status),
    path('preferences/', views.save_preferences),
    path('dashboard/', student_dashboard),
    path('tutee/profile/', views.get_tutee_profile),
    path('tutee/profile/update/', views.update_tutee_profile),  
    path('tutor/profile/', views.get_tutor_profile),
    path('tutor/subjects/', views.get_tutor_subjects),
    path('tutor/subjects/add/', views.add_tutor_subject),
    path('tutor/subjects/remove/<str:subject_code>/', views.remove_tutor_subject),
    path('search-tutors/', SearchTutorsView.as_view(), name='search-tutors'),
    path('subjects/',SubjectListView.as_view(), name='subjects'),
    path('courses/', list_courses),
    path('tutor-dashboard/', tutor_dashboard, name='tutor-dashboard'),
    path('tutors/<int:profile_id>/', tutor_detail),
    path('tutors/<int:tutor_id>/availability/', tutor_availability),
    path('profile/setup/', views.setup_profile),
    path('tutor/update/', views.update_tutor_profile),


    path('bookings/', views.list_bookings),
    path('bookings/<int:booking_id>/', views.booking_detail),
    path('payment-methods/', views.payment_methods),
<<<<<<< HEAD
    
=======

>>>>>>> 32c6f3b (Before Merging to Another Branch)
    #Dynamic
    
    path('bookings/confirm/', views.confirm_payment_and_book),
    path('template-availability/', template_availability),
    path('template-availability/<int:pk>/', template_availability),
    path('bookings/<int:booking_id>/complete/', complete_booking),
    path('bookings/<int:booking_id>/approve/', views.approve_booking),
    path('bookings/<int:booking_id>/reject/', views.reject_booking),
    path('tutor/setup/', views.tutor_setup),
    path('recommend-tutors/', views.recommend_tutors_view),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)