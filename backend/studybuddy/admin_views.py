from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db import transaction
from django.db.models import Count, Q, Sum
from django.utils import timezone
from datetime import timedelta
from .models import (
    UserProfile, Tutor, Booking, WithdrawalRequest, 
    PartnerInstitution, Wallet, Transaction, PlatformActivity
)
from .serializers import (
    AdminWithdrawalSerializer, AdminUserSerializer, 
    PartnerInstitutionSerializer, PlatformActivitySerializer
)
from .permissions import IsAdminUser

class AdminStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

    def get(self, request):
        today = timezone.localtime(timezone.now()).date()
        month_start = today.replace(day=1)

        # Commissions this month
        commissions = Transaction.objects.filter(
            transaction_type='commission_deduction',
            created_at__date__gte=month_start
        ).aggregate(total=Sum('amount'))['total'] or 0

        # Recent activities
        activities = PlatformActivity.objects.order_by('-created_at')[:10]
        activity_serializer = PlatformActivitySerializer(activities, many=True)

        stats = {
            'total_tutors': Tutor.objects.count(),
            'total_tutees': UserProfile.objects.filter(role='Tutee').count(),
            'active_sessions_today': Booking.objects.filter(session_date=today, status='Confirmed').count(),
            'commissions_this_month': float(abs(commissions)),
            'pending_withdrawals': WithdrawalRequest.objects.filter(status='pending').count(),
            'failed_withdrawals': WithdrawalRequest.objects.filter(status='failed').count(),
            'recent_activity': activity_serializer.data
        }
        return Response(stats)

class AdminWithdrawalListView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

    def get(self, request):
        queryset = WithdrawalRequest.objects.all().order_by('-requested_at')
        
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        serializer = AdminWithdrawalSerializer(queryset, many=True)
        return Response(serializer.data)

class AdminWithdrawalDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

    def patch(self, request, pk):
        withdrawal = WithdrawalRequest.objects.get(pk=pk)
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
            message=f"Admin marked withdrawal #{withdrawal.id} for {withdrawal.tutor.profile.fname} as {new_status}"
        )

        serializer = AdminWithdrawalSerializer(withdrawal)
        return Response(serializer.data)

class AdminUserListView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

    def get(self, request):
        queryset = UserProfile.objects.select_related('user', 'institution', 'tutor__wallet').all().order_by('-created_at')
        
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
        profile = UserProfile.objects.get(pk=pk)
        is_suspended = request.data.get('is_suspended')
        
        if is_suspended is not None:
            profile.is_suspended = is_suspended
            profile.save()
            
            PlatformActivity.objects.create(
                activity_type='admin_action',
                message=f"Admin {'suspended' if is_suspended else 'reactivated'} user {profile.fname} {profile.lname}"
            )
            
        serializer = AdminUserSerializer(profile)
        return Response(serializer.data)

    def delete(self, request, pk=None):
        profile = UserProfile.objects.get(pk=pk)
        user = profile.user
        
        PlatformActivity.objects.create(
            activity_type='admin_action',
            message=f"Admin deleted user {profile.fname} {profile.lname} ({user.email})"
        )
        
        user.delete() # This cascades to UserProfile
        return Response(status=status.HTTP_204_NO_CONTENT)

class AdminInstitutionView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

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
                message=f"New institution added: {serializer.data['institution_name']}"
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
                message=msg[:255]
            )

        if updated:
            institution.save()
            
        serializer = PartnerInstitutionSerializer(institution)
        return Response(serializer.data)

class AdminAnalyticsView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

    def get(self, request):
        # Sessions over time (last 30 days)
        today = timezone.localtime(timezone.now()).date()
        labels = []
        session_counts = []
        
        for i in range(29, -1, -1):
            day = today - timedelta(days=i)
            labels.append(day.strftime('%b %d'))
            count = Booking.objects.filter(session_date=day, status='Completed').count()
            session_counts.append(count)

        # Revenue Breakdown
        total_revenue = Transaction.objects.filter(transaction_type='session_credit').aggregate(Sum('amount'))['amount__sum'] or 0
        total_commissions = Transaction.objects.filter(transaction_type='commission_deduction').aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Top Tutors
        top_tutors = Tutor.objects.order_by('-total_sessions')[:5]
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
                'gross': float(total_revenue + abs(total_commissions)),
                'commissions': float(abs(total_commissions)),
                'payouts': float(total_revenue)
            },
            'top_tutors': top_tutors_data
        })
