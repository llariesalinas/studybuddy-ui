import logging
import decimal
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Count, Q, Sum
from django.utils import timezone
from datetime import timedelta
from .models import (
    UserProfile, Tutor, Booking, WithdrawalRequest, 
    PartnerInstitution, Wallet, Transaction, PlatformActivity,
    TutorApplication, Payment
)
from .serializers import (
    AdminWithdrawalSerializer, AdminUserSerializer, 
    PartnerInstitutionSerializer, PlatformActivitySerializer,
    TutorApplicationSerializer
)
from .permissions import IsAdminUser, IsSuperAdminUser
from .email_utils import send_application_approved_email, send_application_rejected_email

logger = logging.getLogger(__name__)

class BaseAdminView(APIView):
    def get_queryset_for_user(self, request, queryset, user_path=''):
        profile = request.user.userprofile
        if profile.role == 'SuperAdmin':
            return queryset
        
        # Build the filter kwarg dynamically
        if user_path:
            kwarg = f"{user_path}__institution"
        else:
            kwarg = "institution"
            
        return queryset.filter(**{kwarg: profile.institution})

class AdminStatsView(BaseAdminView):
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

    def get(self, request):
        today = timezone.localtime(timezone.now()).date()
        month_start = today.replace(day=1)

        # Commissions this month
        qs_transactions = Transaction.objects.filter(created_at__date__gte=month_start)
        qs_activities = PlatformActivity.objects.order_by('-created_at')
        qs_tutors = Tutor.objects.all()
        qs_tutees = UserProfile.objects.filter(role='Tutee')
        qs_bookings = Booking.objects.filter(session_date=today, status='Confirmed')
        qs_withdrawals = WithdrawalRequest.objects.all()

        profile = request.user.userprofile
        if profile.role != 'SuperAdmin':
            inst = profile.institution
            qs_transactions = qs_transactions.filter(wallet__tutor__profile__institution=inst)
            qs_activities = qs_activities.filter(institution=inst)
            qs_tutors = qs_tutors.filter(profile__institution=inst)
            qs_tutees = qs_tutees.filter(institution=inst)
            qs_bookings = qs_bookings.filter(tutor__profile__institution=inst)
            qs_withdrawals = qs_withdrawals.filter(tutor__profile__institution=inst)

        commissions = qs_transactions.filter(
            transaction_type='commission_deduction'
        ).aggregate(total=Sum('amount'))['total'] or 0

        activities = qs_activities[:10]
        activity_serializer = PlatformActivitySerializer(activities, many=True)

        stats = {
            'total_tutors': qs_tutors.count(),
            'total_tutees': qs_tutees.count(),
            'active_sessions_today': qs_bookings.count(),
            'commissions_this_month': float(abs(commissions)),
            'pending_withdrawals': qs_withdrawals.filter(status='pending').count(),
            'failed_withdrawals': qs_withdrawals.filter(status='failed').count(),
            'recent_activity': activity_serializer.data
        }
        return Response(stats)

class AdminWithdrawalListView(BaseAdminView):
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

    def get(self, request):
        queryset = self.get_queryset_for_user(request, WithdrawalRequest.objects.select_related('tutor__profile__user').all(), user_path='tutor__profile')
        queryset = queryset.order_by('-requested_at')
        
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        serializer = AdminWithdrawalSerializer(queryset, many=True)
        return Response(serializer.data)

class AdminWithdrawalDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

    def patch(self, request, pk):
        queryset = self.get_queryset_for_user(request, WithdrawalRequest.objects.all(), user_path='tutor__profile')
        withdrawal = get_object_or_404(queryset, pk=pk)
        new_status = request.data.get('status')
        failure_reason = request.data.get('failure_reason', '')

        if new_status not in ['processed', 'rejected', 'failed', 'flagged']:
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

        withdrawal.status = new_status
        if failure_reason:
            withdrawal.failure_reason = failure_reason
            
        if new_status in ['processed', 'rejected', 'failed', 'flagged']:
            withdrawal.processed_at = timezone.now()
        
        if new_status in ['rejected', 'failed']:
            with transaction.atomic():
                wallet = Wallet.objects.select_for_update().get(tutor=withdrawal.tutor)
                principal_ref = f"WD-{withdrawal.id}-REV"
                fee_ref = f"WD-{withdrawal.id}-FEE-REV"
                changed_balance = False

                if not Transaction.objects.filter(
                    wallet=wallet,
                    reference_id__in=[principal_ref, str(withdrawal.id)]
                ).exists():
                    wallet.balance += withdrawal.amount
                    changed_balance = True
                    Transaction.objects.create(
                        wallet=wallet,
                        transaction_type='withdrawal_reversal',
                        amount=withdrawal.amount,
                        description=f"Reversal of cash-out request #{withdrawal.id}",
                        reference_id=principal_ref
                    )

                if (
                    withdrawal.provider_fee > 0
                    and not Transaction.objects.filter(wallet=wallet, reference_id=fee_ref).exists()
                ):
                    wallet.balance += withdrawal.provider_fee
                    changed_balance = True
                    Transaction.objects.create(
                        wallet=wallet,
                        transaction_type='cashout_fee_reversal',
                        amount=withdrawal.provider_fee,
                        description=f"Provider fee reversal for cash-out request #{withdrawal.id}",
                        reference_id=fee_ref
                    )

                if changed_balance:
                    wallet.save(update_fields=['balance'])

        withdrawal.save()

        # 🔥 Log the admin action to platform activity
        activity_map = {
            'processed': 'withdrawal_processed',
            'rejected': 'admin_action', # Using generic admin_action for rejection or failed
            'failed': 'withdrawal_failed',
            'flagged': 'admin_action'
        }
        
        PlatformActivity.objects.create(
            activity_type=activity_map.get(new_status, 'admin_action'),
            message=f"Admin marked withdrawal #{withdrawal.id} for {withdrawal.tutor.profile.fname} as {new_status}",
            institution=request.user.userprofile.institution
        )

        serializer = AdminWithdrawalSerializer(withdrawal)
        return Response(serializer.data)

class AdminUserListView(BaseAdminView):
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

    def get(self, request):
        queryset = self.get_queryset_for_user(request, UserProfile.objects.select_related('user', 'institution', 'tutor__wallet').all())
        queryset = queryset.order_by('-created_at')
        
        # Only show Tutees and Tutors to normal Admins
        profile = request.user.userprofile
        if profile.role != 'SuperAdmin':
            queryset = queryset.filter(role__in=['Tutee', 'Tutor'])
        
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(fname__icontains=search) | 
                Q(lname__icontains=search) | 
                Q(user__email__icontains=search)
            )

        role = request.query_params.get('role')
        if role:
            queryset = queryset.filter(role=role)
            
        status_filter = request.query_params.get('status')
        if status_filter == 'Suspended':
            queryset = queryset.filter(is_suspended=True)
        elif status_filter == 'Active':
            queryset = queryset.filter(is_suspended=False)

        serializer = AdminUserSerializer(queryset, many=True)
        return Response(serializer.data)

    def patch(self, request, pk=None):
        queryset = self.get_queryset_for_user(request, UserProfile.objects.all())
        profile = get_object_or_404(queryset, pk=pk)
        is_suspended = request.data.get('is_suspended')
        
        if is_suspended is not None:
            profile.is_suspended = is_suspended
            profile.save()
            
            PlatformActivity.objects.create(
                activity_type='admin_action',
                message=f"Admin {'suspended' if is_suspended else 'reactivated'} user {profile.fname} {profile.lname}",
                institution=request.user.userprofile.institution
            )
            
        serializer = AdminUserSerializer(profile)
        return Response(serializer.data)

    def delete(self, request, pk=None):
        queryset = self.get_queryset_for_user(request, UserProfile.objects.all())
        profile = get_object_or_404(queryset, pk=pk)
        user = profile.user
        
        PlatformActivity.objects.create(
            activity_type='admin_action',
            message=f"Admin deleted user {profile.fname} {profile.lname} ({user.email})",
            institution=request.user.userprofile.institution
        )
        
        user.delete() # This cascades to UserProfile
        return Response(status=status.HTTP_204_NO_CONTENT)

class AdminInstitutionView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsSuperAdminUser]

    def get(self, request):
        institutions = PartnerInstitution.objects.all().order_by('institution_name')
        serializer = PartnerInstitutionSerializer(institutions, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PartnerInstitutionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            PlatformActivity.objects.create(
                activity_type='institution_added',
                message=f"New institution added: {serializer.data['institution_name']}",
                institution=request.user.userprofile.institution
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk=None):
        try:
            institution = PartnerInstitution.objects.get(pk=pk)
        except PartnerInstitution.DoesNotExist:
            return Response({"error": "Institution not found"}, status=status.HTTP_404_NOT_FOUND)
        
        data = request.data
        updated = False

        # Handle is_active (Deactivation/Reactivation)
        is_active = data.get('is_active')
        if is_active is not None:
            # Handle potential string booleans
            if isinstance(is_active, str):
                is_active = is_active.lower() == 'true'
            
            institution.is_active = bool(is_active)
            updated = True
            msg = f"Admin {'reactivated' if institution.is_active else 'deactivated'} institution {institution.institution_name}"
            PlatformActivity.objects.create(
                activity_type='admin_action',
                message=msg[:255],
                institution=request.user.userprofile.institution
            )

        if updated:
            institution.save()
            
        serializer = PartnerInstitutionSerializer(institution)
        return Response(serializer.data)

class AdminAnalyticsView(BaseAdminView):
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

    def get(self, request):
        # Sessions over time (last 30 days)
        today = timezone.localtime(timezone.now()).date()
        labels = []
        session_counts = []

        profile = request.user.userprofile
        qs_bookings = Booking.objects.all()
        qs_transactions = Transaction.objects.all()
        qs_tutors = Tutor.objects.all()

        if profile.role != 'SuperAdmin':
            inst = profile.institution
            qs_bookings = qs_bookings.filter(tutor__profile__institution=inst)
            qs_transactions = qs_transactions.filter(wallet__tutor__profile__institution=inst)
            qs_tutors = qs_tutors.filter(profile__institution=inst)
        else:
            # SuperAdmin can optionally filter by a specific institution
            institution_id = request.query_params.get('institution_id')
            if institution_id:
                try:
                    inst = PartnerInstitution.objects.get(pk=institution_id)
                    qs_bookings = qs_bookings.filter(tutor__profile__institution=inst)
                    qs_transactions = qs_transactions.filter(wallet__tutor__profile__institution=inst)
                    qs_tutors = qs_tutors.filter(profile__institution=inst)
                except PartnerInstitution.DoesNotExist:
                    pass

        thirty_days_ago = today - timedelta(days=29)
        daily_counts = (
            qs_bookings.filter(session_date__gte=thirty_days_ago, status='Completed')
            .values('session_date')
            .annotate(count=Count('id'))
        )
        counts_dict = {item['session_date']: item['count'] for item in daily_counts}

        for i in range(29, -1, -1):
            day = today - timedelta(days=i)
            labels.append(day.strftime('%b %d'))
            session_counts.append(counts_dict.get(day, 0))

        # Revenue Breakdown
        from decimal import Decimal
        qs_payments = Payment.objects.filter(
            booking__status='Completed',
            payment_status='Paid',
            booking__in=qs_bookings
        )
        gross_revenue = qs_payments.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        commission = gross_revenue * Decimal('0.10')
        tutor_payouts = gross_revenue - commission

        # Top Tutors
        top_tutors = qs_tutors.order_by('-total_sessions')[:5]
        top_tutors_data = [
            {
                'name': f"{t.profile.fname} {t.profile.lname}",
                'sessions': t.total_sessions,
                'rating': t.rating_average
            } for t in top_tutors
        ]

        return Response({
            'sessions_over_time': {
                'labels': labels,
                'data': session_counts
            },
            'revenue_summary': {
                'gross': float(gross_revenue),
                'commissions': float(commission),
                'payouts': float(tutor_payouts)
            },
            'top_tutors': top_tutors_data
        })


class SuperAdminInstitutionPerformanceView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsSuperAdminUser]

    def get(self, request):
        institutions = PartnerInstitution.objects.all()
        data = []

        from django.db.models import Avg
        from decimal import Decimal

        tutors_data = Tutor.objects.values('profile__institution_id').annotate(
            tutor_count=Count('profile_id'),
            avg_rating=Avg('rating_average')
        )
        tutors_dict = {item['profile__institution_id']: item for item in tutors_data}

        tutees_data = UserProfile.objects.filter(role='Tutee').values('institution_id').annotate(
            tutee_count=Count('id')
        )
        tutees_dict = {item['institution_id']: item['tutee_count'] for item in tutees_data}

        sessions_data = Booking.objects.filter(status='Completed').values('tutor__profile__institution_id').annotate(
            session_count=Count('id')
        )
        sessions_dict = {item['tutor__profile__institution_id']: item['session_count'] for item in sessions_data}

        payments_data = Payment.objects.filter(
            booking__status='Completed',
            payment_status='Paid'
        ).values('booking__tutor__profile__institution_id').annotate(
            total_amount=Sum('amount')
        )
        payments_dict = {item['booking__tutor__profile__institution_id']: item['total_amount'] for item in payments_data}

        for inst in institutions:
            t_data = tutors_dict.get(inst.id, {})
            tutors = t_data.get('tutor_count', 0)
            avg_rating = round(t_data.get('avg_rating') or 0, 2)

            tutees = tutees_dict.get(inst.id, 0)
            sessions = sessions_dict.get(inst.id, 0)

            gross = payments_dict.get(inst.id) or Decimal('0')
            revenue = gross * Decimal('0.10')

            data.append({
                'id': inst.id,
                'institution_name': inst.institution_name,
                'tutors': tutors,
                'tutees': tutees,
                'sessions': sessions,
                'revenue': float(abs(revenue)),
                'avg_rating': avg_rating
            })
            
        return Response(data)


class AdminTutorApplicationListView(BaseAdminView):
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

    def get(self, request):
        status_filter = request.query_params.get('status')
        queryset = self.get_queryset_for_user(request, TutorApplication.objects.select_related('profile__user', 'profile__institution').all(), user_path='profile')
        queryset = queryset.order_by('-submitted_at')

        if status_filter:
            queryset = queryset.filter(application_status=status_filter)

        serializer = TutorApplicationSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)


class AdminTutorApplicationDetailView(BaseAdminView):
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

    def get(self, request, pk):
        queryset = self.get_queryset_for_user(request, TutorApplication.objects.all(), user_path='profile')
        application = get_object_or_404(queryset, pk=pk)
        serializer = TutorApplicationSerializer(application, context={'request': request})
        return Response(serializer.data)

    @transaction.atomic
    def patch(self, request, pk):
        queryset = self.get_queryset_for_user(request, TutorApplication.objects.all(), user_path='profile')
        application = get_object_or_404(queryset.select_for_update(), pk=pk)

        new_status = request.data.get('application_status')
        rejection_reason = request.data.get('rejection_reason', '')

        if new_status not in ['approved', 'rejected']:
            return Response({"error": "Invalid status. Must be 'approved' or 'rejected'."}, status=status.HTTP_400_BAD_REQUEST)

        application.application_status = new_status
        application.rejection_reason = rejection_reason if new_status == 'rejected' else ''
        application.reviewed_by = request.user.userprofile
        application.reviewed_at = timezone.now()
        application.save()

        # Log activity
        PlatformActivity.objects.create(
            activity_type='admin_action',
            message=f"Admin {request.user.userprofile.fname} {new_status} tutor application for {application.profile.fname} {application.profile.lname}",
            institution=request.user.userprofile.institution
        )

        # Send email notification
        try:
            if new_status == 'approved':
                send_application_approved_email(application.profile)
            else:
                send_application_rejected_email(application.profile, rejection_reason)
        except Exception:
            logger.exception("Failed to send screening result email for application_id=%s", application.id)

        return Response({"message": f"Application {new_status} successfully."})
