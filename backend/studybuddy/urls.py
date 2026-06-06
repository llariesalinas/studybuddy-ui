from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from rest_framework_simplejwt.views import TokenRefreshView
from .views import(
                   cancel_booking,
                   complete_booking,
                   list_courses,
                   login_view, 
                   list_notifications,
                   mark_notification_read,
                   register_user, 
                   submit_session_payment,
                   submit_session_rating,
                   student_dashboard, 
                   SearchTutorsView,
                   SubjectListView, template_availability, tutor_availability, 
                   tutor_confirm_booking,
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
from .admin_views import (
    AdminStatsView, AdminWithdrawalListView, AdminWithdrawalDetailView,
    AdminUserListView, AdminInstitutionView, AdminAnalyticsView,
    AdminTutorApplicationListView, AdminTutorApplicationDetailView
)
from . import views

print("STUDYBUDDY URLS LOADED")

urlpatterns = [
    # Admin Routes
    path('admin/stats/', AdminStatsView.as_view()),
    path('admin/withdrawals/', AdminWithdrawalListView.as_view()),
    path('admin/withdrawals/<int:pk>/', AdminWithdrawalDetailView.as_view()),
    path('admin/tutor-applications/', AdminTutorApplicationListView.as_view()),
    path('admin/tutor-applications/<int:pk>/', AdminTutorApplicationDetailView.as_view()),
    path('admin/users/', AdminUserListView.as_view()),
    path('admin/users/<int:pk>/', AdminUserListView.as_view()),
    path('admin/institutions/', AdminInstitutionView.as_view()),
    path('admin/institutions/<int:pk>/', AdminInstitutionView.as_view()),
    path('admin/analytics/', AdminAnalyticsView.as_view()),
    path('admin/support/tickets/', views.admin_list_tickets),
    path('admin/support/tickets/<int:ticket_id>/claim/', views.admin_claim_ticket),
    path('admin/support/tickets/<int:ticket_id>/resolve/', views.admin_resolve_ticket),

    path('support/tickets/create/', views.create_support_ticket),
    path('support/tickets/my/', views.list_my_tickets),
    path('register/', register_user),
    path('login/', login_view),
    path('login/verify-otp/', views.login_verify_otp),
    path('login/resend-otp/', views.login_resend_otp),
    path('password-reset/request/', views.password_reset_request),
    path('password-reset/confirm/', views.password_reset_confirm),
    path('logout/', views.logout_view),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/status/', views.profile_status),
    path('preferences/', views.save_preferences),
    path('partner-institutions/', views.partner_institutions_list),
    path('dashboard/', student_dashboard),
    path('tutee/profile/', views.get_tutee_profile),
    path('tutee/profile/avatar/', views.upload_tutee_avatar),
    path('tutee/profile/update/', views.update_tutee_profile),
    path('tutor/profile/', views.get_tutor_profile),
    path('tutor/profile/avatar/', views.upload_tutor_avatar),
    path('tutor/subjects/', views.get_tutor_subjects),
    path('tutor/subjects/add/', views.add_tutor_subject),
    path('tutor/subjects/update/<str:subject_code>/', views.update_tutor_subject),
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
    #Dynamic
    
    path('bookings/confirm/', views.confirm_payment_and_book),
    path('bookings/<int:booking_id>/submit-payment/', submit_session_payment),
    path('bookings/<int:booking_id>/tutor-confirm/', tutor_confirm_booking),
    path('bookings/<int:booking_id>/rating/', submit_session_rating),
    path('bookings/<int:booking_id>/cancel/', cancel_booking),
    path('template-availability/', template_availability),
    path('template-availability/<int:pk>/', template_availability),
    path('availability-overrides/', views.availability_overrides),
    path('availability-overrides/<int:override_id>/', views.delete_availability_override),
    path('bookings/<int:booking_id>/complete/', complete_booking),
    path('bookings/<uuid:booking_request_id>/location/', views.update_booking_location),
    path('bookings/<int:booking_id>/approve/', views.approve_booking),
    path('bookings/<int:booking_id>/reject/', views.reject_booking),
    path('notifications/', list_notifications),
    path('notifications/<int:notification_id>/read/', mark_notification_read),
    path('wallet/', views.wallet_status),
    path('wallet/transactions/', views.wallet_transactions),
    path('wallet/payout-destinations/', views.payout_destinations),
    path('wallet/payout-destinations/<int:account_id>/', views.payout_destinations),
    path('wallet/receiving-institutions/', views.receiving_institutions),
    path('wallet/cash-outs/', views.cash_outs),
    path('wallet/paymongo/callback/', views.paymongo_cashout_callback),
    path('wallet/withdraw/', views.cash_outs),
    path('wallet/withdrawals/', views.list_withdrawals),
    path('payments/initiate/', views.initiate_online_payment),
    path('bookings/<int:booking_id>/verify-online-payment/', views.verify_online_payment),
    path('tutor/setup/', views.tutor_setup),
    path('recommend-tutors/', views.recommend_tutors_view),
    path('chat/', include('studybuddy.chat.urls')),
]

if settings.DEBUG:
    urlpatterns += [path('dev/wallet/add/', views.dev_add_wallet_funds)]
    urlpatterns += [path('dev/wallet/remove/', views.dev_remove_wallet_funds)]
    urlpatterns += [
        path(
            'dev/bookings/<int:booking_id>/ready-for-payment/',
            views.dev_mark_booking_ready_for_payment
        )
    ]
