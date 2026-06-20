import logging
import decimal
import csv
from decimal import Decimal
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Avg, Count, Q, Sum
from django.utils import timezone
from django.utils.timesince import timesince
from datetime import timedelta
from .models import (
    AdminAccountRequest, InstitutionRequest,
    UserProfile, Tutor, Booking, WithdrawalRequest,
    PartnerInstitution, Wallet, Transaction, PlatformActivity,
    TutorApplication, Payment, TutorSubjects, Subjects, SupportTicket
)
from .serializers import (
    AdminAccountRequestSerializer, InstitutionRequestSerializer,
    AdminWithdrawalSerializer, AdminUserSerializer, 
    PartnerInstitutionSerializer, PlatformActivitySerializer,
    TutorApplicationSerializer
)
from .permissions import IsAdminUser, IsSuperAdminUser
from .email_utils import send_application_approved_email, send_application_rejected_email

logger = logging.getLogger(__name__)

ANALYTICS_PERIODS = {
    '7d': 7,
    '30d': 30,
    '3m': 90,
    'all': None,
}


def parse_bool(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in ('1', 'true', 'yes', 'on')
    return bool(value)

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
        enrollment_trend = []

        for i in range(13, -1, -1):
            day = today - timedelta(days=i)
            enrollment_trend.append({
                'date': day.isoformat(),
                'new_tutors': qs_tutors.filter(profile__user__date_joined__date=day).count(),
                'new_tutees': qs_tutees.filter(user__date_joined__date=day).count(),
            })

        # Institution-scoped dashboard metrics (None for SuperAdmin = platform-wide)
        inst = None if profile.role == 'SuperAdmin' else profile.institution

        new_members_this_month = (
            qs_tutors.filter(profile__user__date_joined__date__gte=month_start).count()
            + qs_tutees.filter(user__date_joined__date__gte=month_start).count()
        )

        # Sessions per week + 30-day completion rate
        week_start = today - timedelta(days=today.weekday())
        last_week_start = week_start - timedelta(days=7)
        window_start = today - timedelta(days=30)
        active_statuses = ['Confirmed', 'Completed']

        qs_all_bookings = Booking.objects.all()
        if inst:
            qs_all_bookings = qs_all_bookings.filter(tutor__profile__institution=inst)

        sessions_this_week = qs_all_bookings.filter(
            session_date__gte=week_start, status__in=active_statuses
        ).count()
        sessions_last_week = qs_all_bookings.filter(
            session_date__gte=last_week_start, session_date__lt=week_start,
            status__in=active_statuses
        ).count()

        window_bookings = qs_all_bookings.filter(session_date__gte=window_start)
        completed_sessions = window_bookings.filter(status='Completed').count()
        cancelled_sessions = window_bookings.filter(status__in=['Cancelled', 'Rejected']).count()
        completion_denom = completed_sessions + cancelled_sessions
        completion_rate = round(completed_sessions / completion_denom * 100, 1) if completion_denom else 0.0

        # Subject demand (tutee preferences) vs supply (tutor subjects)
        demand_filter = Q(preference__user__role='Tutee')
        supply_filter = Q()
        if inst:
            demand_filter &= Q(preference__user__institution=inst)
            supply_filter = Q(tutorsubjects__tutor__profile__institution=inst)

        demand_rows = (
            Subjects.objects.annotate(
                demand=Count('preference', filter=demand_filter, distinct=True),
                supply=Count('tutorsubjects', filter=supply_filter, distinct=True),
            )
            .filter(demand__gt=0)
            .order_by('-demand')[:5]
        )
        subject_demand = [
            {
                'subject_name': s.subject_name,
                'demand': s.demand,
                'supply': s.supply,
                'gap': s.demand > 0 and s.supply == 0,
            }
            for s in demand_rows
        ]

        # Top tutors by completed sessions (+ avg rating)
        qs_top = qs_tutors.select_related('profile', 'profile__course').annotate(
            completed=Count('tutor_bookings', filter=Q(tutor_bookings__status='Completed'), distinct=True),
            avg_rating=Avg('ratings__rating_score'),
        ).order_by('-completed')[:4]
        top_tutors = [
            {
                'name': f"{t.profile.fname} {t.profile.lname}".strip(),
                'completed_sessions': t.completed,
                'avg_rating': round(t.avg_rating, 1) if t.avg_rating else 0.0,
                'course': t.profile.course.course_code if t.profile.course else '',
            }
            for t in qs_top
        ]

        stats = {
            'institution_name': inst.institution_name if inst else 'All institutions',
            'total_tutors': qs_tutors.count(),
            'total_tutees': qs_tutees.count(),
            'active_sessions_today': qs_bookings.count(),
            'commissions_this_month': float(abs(commissions)),
            'pending_withdrawals': qs_withdrawals.filter(status='pending').count(),
            'failed_withdrawals': qs_withdrawals.filter(status='failed').count(),
            'recent_activity': activity_serializer.data,
            'enrollment_trend': enrollment_trend,
            'new_members_this_month': new_members_this_month,
            'sessions_this_week': sessions_this_week,
            'sessions_last_week': sessions_last_week,
            'completed_sessions': completed_sessions,
            'cancelled_sessions': cancelled_sessions,
            'completion_rate': completion_rate,
            'subject_demand': subject_demand,
            'top_tutors': top_tutors,
        }
        return Response(stats)


class AdminOperationalQueueView(BaseAdminView):
    """Institution-scoped operational to-do feed for the Admin dashboard.

    Groups the items an institution admin must act on (withdrawals, support
    tickets, tutor applications) into summary rows. Each row routes to the
    existing screen that resolves it; the dashboard performs no mutations.
    """
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

    def get(self, request):
        profile = request.user.userprofile
        inst = None if profile.role == 'SuperAdmin' else profile.institution

        withdrawals = WithdrawalRequest.objects.filter(status__in=['pending', 'failed'])
        tickets = SupportTicket.objects.filter(status__in=['Open', 'In_Progress'])
        applications = TutorApplication.objects.filter(application_status='pending')
        if inst:
            withdrawals = withdrawals.filter(tutor__profile__institution=inst)
            tickets = tickets.filter(user__institution=inst)
            applications = applications.filter(profile__institution=inst)

        items = []

        wd_count = withdrawals.count()
        if wd_count:
            failed = withdrawals.filter(status='failed').count()
            total_amount = withdrawals.aggregate(total=Sum('amount'))['total'] or 0
            meta = f"PHP {float(total_amount):,.0f} total"
            if failed:
                meta += f" - {failed} failed"
            items.append({
                'type': 'withdrawal',
                'title': f"{wd_count} withdrawal{'s' if wd_count != 1 else ''} need review",
                'meta': meta,
                'route': '/admin/withdrawals',
            })

        ticket_count = tickets.count()
        if ticket_count:
            unassigned = tickets.filter(status='Open').count()
            items.append({
                'type': 'support',
                'title': f"{ticket_count} open support ticket{'s' if ticket_count != 1 else ''}",
                'meta': f"{unassigned} unassigned",
                'route': '/admin/support',
            })

        app_count = applications.count()
        if app_count:
            items.append({
                'type': 'tutor_application',
                'title': f"{app_count} tutor application{'s' if app_count != 1 else ''}",
                'meta': 'Awaiting screening',
                'route': '/admin/users',
            })

        return Response({'count': wd_count + ticket_count + app_count, 'items': items})


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

        serializer = AdminUserSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def patch(self, request, pk=None):
        queryset = self.get_queryset_for_user(request, UserProfile.objects.all())
        profile = get_object_or_404(queryset, pk=pk)
        actor = request.user.userprofile
        changed_fields = []
        is_suspended = request.data.get('is_suspended')
        
        if is_suspended is not None:
            profile.is_suspended = parse_bool(is_suspended)
            changed_fields.append('is_suspended')

        if 'role' in request.data:
            if actor.role != 'SuperAdmin':
                return Response({'error': 'Only SuperAdmin can change roles.'}, status=status.HTTP_403_FORBIDDEN)

            role = request.data.get('role')
            valid_roles = [choice[0] for choice in UserProfile.ROLE_CHOICES]
            if role not in valid_roles:
                return Response({'error': 'Invalid role.'}, status=status.HTTP_400_BAD_REQUEST)

            profile.role = role
            changed_fields.append('role')

        if 'institution' in request.data:
            if actor.role != 'SuperAdmin':
                return Response({'error': 'Only SuperAdmin can change institutions.'}, status=status.HTTP_403_FORBIDDEN)

            institution_id = request.data.get('institution')
            if institution_id in ('', None):
                profile.institution = None
            else:
                profile.institution = get_object_or_404(PartnerInstitution, pk=institution_id)
            changed_fields.append('institution')

        if 'is_domain_exempt' in request.data:
            if actor.role != 'SuperAdmin':
                return Response({'error': 'Only SuperAdmin can change domain exemptions.'}, status=status.HTTP_403_FORBIDDEN)

            profile.is_domain_exempt = parse_bool(request.data.get('is_domain_exempt'))
            changed_fields.append('is_domain_exempt')

        if changed_fields:
            profile.save(update_fields=list(set(changed_fields)) + ['updated_at'])

            PlatformActivity.objects.create(
                activity_type='admin_action',
                message=f"Admin updated {profile.fname} {profile.lname}: {', '.join(sorted(set(changed_fields)))}",
                institution=actor.institution
            )
            
        serializer = AdminUserSerializer(profile, context={'request': request})
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


class AdminPendingActionsView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsSuperAdminUser]

    def get(self, request):
        items = []

        for req in InstitutionRequest.objects.filter(status='pending'):
            items.append({
                'type': 'institution_request',
                'id': req.id,
                'title': f"New institution: {req.institution_name}",
                'meta': f"{req.school_email_domain} · submitted {timesince(req.created_at)} ago",
                'created_at': req.created_at,
            })

        for inst in PartnerInstitution.objects.filter(is_active=False):
            items.append({
                'type': 'institution_activation',
                'id': inst.id,
                'title': 'Institution pending activation',
                'meta': f"{inst.institution_name} · added {timesince(inst.date_added)} ago",
                'created_at': inst.date_added,
            })

        admin_requests = AdminAccountRequest.objects.filter(status='pending').select_related(
            'institution',
            'requesting_admin__user',
            'target_user__user',
        )
        for req in admin_requests:
            requester_email = req.requesting_admin.user.email
            items.append({
                'type': 'admin_account_request',
                'id': req.id,
                'title': 'Admin account request',
                'meta': f"{req.institution.institution_name} · from {requester_email}",
                'created_at': req.created_at,
            })

        partner_domains = {
            domain.strip().lower()
            for domain in PartnerInstitution.objects.filter(is_active=True)
                .values_list('school_email_domain', flat=True)
            if domain
        }
        profiles = UserProfile.objects.filter(
            is_domain_exempt=False,
            profile_completed=True,
        ).exclude(role='SuperAdmin').select_related('user')

        for profile in profiles:
            email = profile.user.email or ''
            domain = email.split('@')[-1].strip().lower() if '@' in email else ''
            if domain and domain not in partner_domains:
                items.append({
                    'type': 'domain_exemption',
                    'id': profile.id,
                    'title': 'Domain exemption review',
                    'meta': f"{email} · profile complete",
                    'created_at': profile.user.date_joined,
                })

        items.sort(key=lambda item: item['created_at'])
        return Response({'count': len(items), 'items': items})


class InstitutionRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

    def get(self, request):
        if request.user.userprofile.role != 'SuperAdmin':
            return Response({'error': 'Only SuperAdmin can view institution requests.'}, status=status.HTTP_403_FORBIDDEN)

        queryset = InstitutionRequest.objects.all()
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        serializer = InstitutionRequestSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = InstitutionRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            PlatformActivity.objects.create(
                activity_type='institution_added',
                message=f"Institution request submitted: {serializer.data['institution_name']}",
                institution=request.user.userprofile.institution
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk=None):
        if request.user.userprofile.role != 'SuperAdmin':
            return Response({'error': 'Only SuperAdmin can review institution requests.'}, status=status.HTTP_403_FORBIDDEN)

        institution_request = get_object_or_404(InstitutionRequest, pk=pk)
        action = str(request.data.get('action', '')).strip().lower()
        if action not in ('approve', 'reject'):
            return Response({'error': "Action must be 'approve' or 'reject'."}, status=status.HTTP_400_BAD_REQUEST)

        if institution_request.status != 'pending':
            return Response({'error': 'Only pending requests can be reviewed.'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            institution_request.status = 'approved' if action == 'approve' else 'rejected'
            institution_request.reviewed_by = request.user
            institution_request.reviewed_at = timezone.now()
            institution_request.save(update_fields=['status', 'reviewed_by', 'reviewed_at'])

            if action == 'approve':
                institution, _created = PartnerInstitution.objects.update_or_create(
                    school_email_domain=institution_request.school_email_domain,
                    defaults={
                        'institution_name': institution_request.institution_name,
                        'contact_person': institution_request.contact_person,
                        'is_active': True,
                    }
                )
                PlatformActivity.objects.create(
                    activity_type='institution_added',
                    message=f"Institution approved: {institution.institution_name}",
                    institution=institution
                )
            else:
                PlatformActivity.objects.create(
                    activity_type='admin_action',
                    message=f"Institution request rejected: {institution_request.institution_name}",
                    institution=request.user.userprofile.institution
                )

        serializer = InstitutionRequestSerializer(institution_request)
        return Response(serializer.data)


class AdminAccountRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

    def get(self, request):
        if request.user.userprofile.role != 'SuperAdmin':
            return Response({'error': 'Only SuperAdmin can view admin account requests.'}, status=status.HTTP_403_FORBIDDEN)

        queryset = AdminAccountRequest.objects.select_related(
            'requesting_admin__user',
            'institution',
            'target_user__user',
        ).all()
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        serializer = AdminAccountRequestSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        actor = request.user.userprofile
        data = request.data.copy()

        if actor.role == 'Admin':
            if not actor.institution:
                return Response({'error': 'Admin account must belong to an institution.'}, status=status.HTTP_400_BAD_REQUEST)
            data['institution'] = actor.institution_id

        serializer = AdminAccountRequestSerializer(data=data)
        if serializer.is_valid():
            serializer.save(requesting_admin=actor)
            PlatformActivity.objects.create(
                activity_type='admin_action',
                message=f"Admin account request submitted for {serializer.instance.institution.institution_name}",
                institution=serializer.instance.institution
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk=None):
        if request.user.userprofile.role != 'SuperAdmin':
            return Response({'error': 'Only SuperAdmin can review admin account requests.'}, status=status.HTTP_403_FORBIDDEN)

        admin_request = get_object_or_404(
            AdminAccountRequest.objects.select_related('institution', 'target_user'),
            pk=pk
        )
        action = str(request.data.get('action', '')).strip().lower()
        if action not in ('approve', 'reject'):
            return Response({'error': "Action must be 'approve' or 'reject'."}, status=status.HTTP_400_BAD_REQUEST)

        if admin_request.status != 'pending':
            return Response({'error': 'Only pending requests can be reviewed.'}, status=status.HTTP_400_BAD_REQUEST)

        target_user_id = request.data.get('target_user_id') or request.data.get('target_user')
        if target_user_id:
            admin_request.target_user = get_object_or_404(UserProfile, pk=target_user_id)

        if action == 'approve' and not admin_request.target_user:
            return Response({'error': 'target_user_id is required to approve an admin request.'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            admin_request.status = 'approved' if action == 'approve' else 'rejected'
            admin_request.reviewed_at = timezone.now()
            admin_request.save(update_fields=['status', 'target_user', 'reviewed_at'])

            if action == 'approve':
                target = admin_request.target_user
                target.role = 'Admin'
                target.institution = admin_request.institution
                target.save(update_fields=['role', 'institution', 'updated_at'])
                message = f"Admin account approved: {target.fname} {target.lname}"
            else:
                message = f"Admin account request rejected for {admin_request.institution.institution_name}"

            PlatformActivity.objects.create(
                activity_type='admin_action',
                message=message[:255],
                institution=admin_request.institution
            )

        serializer = AdminAccountRequestSerializer(admin_request)
        return Response(serializer.data)


class AdminAnalyticsView(BaseAdminView):
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

    def get(self, request):
        today = timezone.localtime(timezone.now()).date()
        period = request.query_params.get('period', '30d')
        if period not in ANALYTICS_PERIODS:
            period = '30d'

        days = ANALYTICS_PERIODS[period]
        labels = []
        session_counts = []

        profile = request.user.userprofile
        qs_bookings = Booking.objects.all()
        qs_tutors = Tutor.objects.all()

        if profile.role != 'SuperAdmin':
            inst = profile.institution
            qs_bookings = qs_bookings.filter(tutor__profile__institution=inst)
            qs_tutors = qs_tutors.filter(profile__institution=inst)
        else:
            # SuperAdmin can optionally filter by a specific institution
            institution_id = request.query_params.get('institution_id')
            if institution_id:
                try:
                    inst = PartnerInstitution.objects.get(pk=institution_id)
                    qs_bookings = qs_bookings.filter(tutor__profile__institution=inst)
                    qs_tutors = qs_tutors.filter(profile__institution=inst)
                except PartnerInstitution.DoesNotExist:
                    pass

        if days is None:
            earliest = qs_bookings.order_by('session_date').values_list('session_date', flat=True).first()
            start_date = earliest or today
            chart_days = max((today - start_date).days + 1, 1)
        else:
            start_date = today - timedelta(days=days - 1)
            chart_days = days

        period_bookings = qs_bookings.filter(session_date__gte=start_date) if days is not None else qs_bookings
        completed_bookings = period_bookings.filter(status='Completed')

        daily_counts = (
            completed_bookings
            .values('session_date')
            .annotate(count=Count('id'))
        )
        counts_dict = {item['session_date']: item['count'] for item in daily_counts}

        for i in range(chart_days - 1, -1, -1):
            day = today - timedelta(days=i)
            labels.append(day.strftime('%b %d'))
            session_counts.append(counts_dict.get(day, 0))

        qs_payments = Payment.objects.filter(
            booking__status='Completed',
            payment_status='Paid',
            booking__in=completed_bookings
        )
        gross_revenue = qs_payments.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        commission = gross_revenue * Decimal('0.10')
        tutor_payouts = gross_revenue - commission

        total_sessions = period_bookings.count()
        completed_sessions = completed_bookings.count()
        completion_rate = round((completed_sessions / total_sessions) * 100, 1) if total_sessions else 0

        top_tutors = qs_tutors.order_by('-total_sessions')[:5]
        top_tutors_data = []
        for tutor in top_tutors:
            tutor_gross = qs_payments.filter(booking__tutor=tutor).aggregate(total=Sum('amount'))['total'] or Decimal('0')
            top_tutors_data.append({
                'name': f"{tutor.profile.fname} {tutor.profile.lname}",
                'sessions': tutor.total_sessions,
                'rating': tutor.rating_average,
                'earnings': float(tutor_gross * Decimal('0.90')),
            })

        subject_popularity = list(
            TutorSubjects.objects.filter(
                tutor__in=qs_tutors,
                tutor__tutor_bookings__in=completed_bookings
            )
            .values('subject__subject_name')
            .annotate(booking_count=Count('tutor__tutor_bookings'))
            .order_by('-booking_count')[:10]
        )
        subject_popularity = [
            {
                'subject_name': item['subject__subject_name'] or 'General',
                'booking_count': item['booking_count'],
            }
            for item in subject_popularity
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
            'completion_rate': completion_rate,
            'subject_popularity': subject_popularity,
            'top_tutors': top_tutors_data
        })


class AdminAnalyticsExportView(BaseAdminView):
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

    def get(self, request):
        today = timezone.localtime(timezone.now()).date()
        period = request.query_params.get('period', '30d')
        if period not in ANALYTICS_PERIODS:
            period = '30d'

        days = ANALYTICS_PERIODS[period]
        start_date = None if days is None else today - timedelta(days=days - 1)
        profile = request.user.userprofile
        institutions = PartnerInstitution.objects.all().order_by('institution_name')

        if profile.role != 'SuperAdmin':
            institutions = institutions.filter(pk=profile.institution_id)
        else:
            institution_id = request.query_params.get('institution_id')
            if institution_id:
                institutions = institutions.filter(pk=institution_id)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="studybuddy-analytics.csv"'
        writer = csv.writer(response)
        writer.writerow([
            'date',
            'institution',
            'tutors',
            'tutees',
            'sessions',
            'completion_rate',
            'gross_revenue',
            'commissions',
        ])

        for inst in institutions:
            bookings = Booking.objects.filter(tutor__profile__institution=inst)
            if start_date:
                bookings = bookings.filter(session_date__gte=start_date)

            completed = bookings.filter(status='Completed')
            payments = Payment.objects.filter(
                booking__in=completed,
                payment_status='Paid',
            )
            gross = payments.aggregate(total=Sum('amount'))['total'] or Decimal('0')
            commissions = gross * Decimal('0.10')
            total_sessions = bookings.count()
            completed_sessions = completed.count()
            completion_rate = round((completed_sessions / total_sessions) * 100, 1) if total_sessions else 0

            writer.writerow([
                today.isoformat(),
                inst.institution_name,
                Tutor.objects.filter(profile__institution=inst).count(),
                UserProfile.objects.filter(role='Tutee', institution=inst).count(),
                completed_sessions,
                completion_rate,
                float(gross),
                float(commissions),
            ])

        return response


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
        total_sessions_data = Booking.objects.values('tutor__profile__institution_id').annotate(
            session_count=Count('id')
        )
        total_sessions_dict = {item['tutor__profile__institution_id']: item['session_count'] for item in total_sessions_data}

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
            total_sessions = total_sessions_dict.get(inst.id, 0)
            completion_rate = round((sessions / total_sessions) * 100, 1) if total_sessions else 0

            gross = payments_dict.get(inst.id) or Decimal('0')
            revenue = gross * Decimal('0.10')

            data.append({
                'id': inst.id,
                'institution_name': inst.institution_name,
                'tutors': tutors,
                'tutees': tutees,
                'sessions': sessions,
                'completion_rate': completion_rate,
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
