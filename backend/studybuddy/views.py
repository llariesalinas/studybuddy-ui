import json
import logging
import decimal
import base64
import hashlib
import hmac
import secrets
import requests
from types import SimpleNamespace
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from . import mailer
from .mailer import EmailRateLimitError
from django.core.mail import send_mail
from django.utils.timezone import now
from django.utils.crypto import constant_time_compare
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.text import slugify
from django.db import transaction, IntegrityError
from datetime import datetime,timedelta, date
from calendar import monthrange
from uuid import uuid4
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, authentication_classes, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import AnonRateThrottle
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken


class LoginRateThrottle(AnonRateThrottle):
    """Per-IP throttle for unauthenticated auth endpoints (login/OTP)."""
    scope = 'login'


class RegisterRateThrottle(AnonRateThrottle):
    """Per-IP throttle for registration — more lenient than login to allow
    form correction attempts, but still capped to prevent abuse."""
    scope = 'register'
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from django.db.models import Avg, Case, When, Value, IntegerField, Q, Count
from collections import defaultdict
# algo
from .recommender.hybrid import recommend_tutors_hybrid
from .recommender.CF import build_rating_matrix

from .recommender.cbf import recommend_tutors
from .recommender.dashboard import (
    bump_dashboard_recs_cache_version,
    dashboard_recs_cache_key,
    get_dashboard_recommendations,
)
from .recommender.demo import build_algorithm_demo_recommendation, search_tutees
from .permissions import IsSuperAdminUser
from .subject_recognition import (
    invalid_new_subject_codes,
    recognized_subject_codes_for_profile,
    subject_is_recognized_for_profile,
    subject_selection_queryset_for_profile,
    visible_subject_queryset_for_profile,
)
from .subject_taxonomy import CATEGORIES as TAXONOMY_CATEGORIES
from django.core.cache import cache
from . import _verification_dev
from .models import Booking, Course, EmailOTPChallenge, Notification, PartnerInstitution, Payment, PaymentMethod, Preference, Rating, SessionCheckIn, Subjects, SupportTicket, Tutor, TutorApplication, TutorAvailability, TutorAvailabilityOverride, TutorDocumentRenewalReview, TutorSubjects, Wallet, PlatformActivity, Transaction, TuteeApplication, TuteeDocumentRenewalReview
from .serializers import (
    NotificationSerializer,
    SubjectSerializer,
    TutorApplicationSerializer,
    TutorDetailSerializer,
    TutorAvailabilityOverrideSerializer,
    TutorProfileSerializer,
    TutorProfileUpdateSerializer,
    TutorSearchSerializer,
    TuteeApplicationSerializer,
)
from .email_utils import send_application_received_email
from .chat.services import create_booking_event, get_canonical_room_for_booking
from .image_utils import compress_image, compress_if_image

from .models import (
    UserProfile,
    Booking,
    PartnerInstitution,
    Tutor,
    TutorSubjects,
    ACTIVE_BOOKING_STATUSES,
    GRACE_CUTOFF_HOURS,
)

logger = logging.getLogger(__name__)
TUTOR_SUBJECT_LIMIT = 8
DEFAULT_TUTOR_SUBJECT_EXPERTISE_LEVEL = 3
BOOKING_HORIZON_DAYS = 14
COUNTED_STRIKE_WALLET_DEDUCTION = decimal.Decimal('50.00')
MONTHLY_STRIKE_CAP = 3
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from .models import UserProfile, Tutor


def normalize_email_domain(email):
    if not email or '@' not in email:
        return None

    return email.split('@', 1)[1].strip().lower()


def normalize_stored_domain(domain):
    if not domain:
        return None

    return domain.strip().lower().lstrip('@')


def get_active_institution_by_domain(domain):
    normalized_domain = normalize_stored_domain(domain)

    if not normalized_domain:
        return None

    return PartnerInstitution.objects.filter(
        school_email_domain__iexact=normalized_domain,
        is_active=True
    ).first()


PASSWORD_RESET_GENERIC_MESSAGE = (
    "If an account with that email exists, password reset instructions have been sent."
)
OTP_ERROR_MESSAGE = "Invalid or expired verification code."
SUBJECT_NOT_RECOGNIZED_ERROR = "This subject is not recognized for your course catalog."


def get_tutor_onboarding_context(profile):
    tutor_onboarding_skipped_at = profile.tutor_onboarding_skipped_at
    tutor_onboarding_complete = bool(
        tutor_onboarding_skipped_at is not None
        or (profile.role == 'Tutor' and TutorApplication.objects.filter(profile=profile).exists())
    )

    return {
        "tutor_onboarding_skipped_at": (
            tutor_onboarding_skipped_at.isoformat() if tutor_onboarding_skipped_at else None
        ),
        "tutor_onboarding_complete": tutor_onboarding_complete,
    }


def build_login_response_payload(user, profile):
    refresh = RefreshToken.for_user(user)
    tutor_document_context = get_tutor_document_review_context(profile)

    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "role": profile.role,
        "user_id": user.id,
        "profile_id": profile.id,
        "email": user.email,
        "fname": profile.fname,
        "lname": profile.lname,
        **get_tutor_onboarding_context(profile),
        **tutor_document_context,
    }


EMPTY_DOCUMENT_REVIEW_CONTEXT = {
    "application_status": None,
    "document_renewal_status": None,
    "document_renewal_due_at": None,
    "document_renewal_rejection_reason": '',
    "document_renewal_required": False,
    "needs_document_renewal": False,
    "tutor_renewal_status": None,
    "tutor_renewal_required": False,
    "tutor_renewal_due_at": None,
    "tutor_renewal_rejection_reason": '',
    "can_submit_document_renewal": False,
}


def _maybe_send_renewal_reminder(application, role_label, document_renewal_status, due_at):
    """Opportunistic renewal reminder: fires from the read path (profile_status/login), not a
    scheduler. Only for a currently-verified application with a real due date — due/pending/
    rejected states already surface their own UI banner, no reminder needed. Dedup fields on the
    application make this safe to call on every read; at most one reminder fires per call, and the
    1-day window is checked first since it's the narrower/more urgent one. See
    docs/plans/2026-07-01-tutee-verification-phase4-email-devtools.md."""
    if document_renewal_status != 'verified' or due_at is None:
        return

    now = timezone.now()
    if due_at - timedelta(days=1) <= now < due_at and application.reminder_1day_sent_at is None:
        mailer.enqueue_document_renewal_reminder(application.profile, role_label, 1, due_at)
        application.reminder_1day_sent_at = now
        application.save(update_fields=['reminder_1day_sent_at'])
    elif due_at - timedelta(days=7) <= now < due_at - timedelta(days=1) and application.reminder_7day_sent_at is None:
        mailer.enqueue_document_renewal_reminder(application.profile, role_label, 7, due_at)
        application.reminder_7day_sent_at = now
        application.save(update_fields=['reminder_7day_sent_at'])


def get_document_review_context(application, role_label):
    """Builds the document-verification/renewal-status dict shared by the login payload and
    profile-status endpoint, from a TutorApplication or TuteeApplication instance. Role-generic —
    see docs/plans/2026-07-01-tutee-verification-phase1-model.md. ``role_label`` ('tutor'/'tutee')
    is used only for the opportunistic renewal-reminder email, added in
    docs/plans/2026-07-01-tutee-verification-phase4-email-devtools.md."""
    document_renewal_status = application.document_renewal_status()
    due_at = application.document_renewal_due_at()
    document_renewal_due_at = due_at.isoformat() if due_at else None
    can_submit_document_renewal = application.can_submit_document_renewal()

    document_renewal_rejection_reason = ''
    latest_renewal = application.latest_document_renewal_review()
    if latest_renewal and latest_renewal.status == 'rejected':
        document_renewal_rejection_reason = latest_renewal.rejection_reason

    document_renewal_required = document_renewal_status in ['due', 'pending', 'rejected']

    _maybe_send_renewal_reminder(application, role_label, document_renewal_status, due_at)

    return {
        "application_status": application.application_status,
        "document_renewal_status": document_renewal_status,
        "document_renewal_due_at": document_renewal_due_at,
        "document_renewal_rejection_reason": document_renewal_rejection_reason,
        "document_renewal_required": document_renewal_required,
        "needs_document_renewal": document_renewal_required,
        "tutor_renewal_status": document_renewal_status,
        "tutor_renewal_required": document_renewal_required,
        "tutor_renewal_due_at": document_renewal_due_at,
        "tutor_renewal_rejection_reason": document_renewal_rejection_reason,
        "can_submit_document_renewal": can_submit_document_renewal,
    }


def get_tutor_document_review_context(profile):
    if profile.role != 'Tutor':
        return dict(EMPTY_DOCUMENT_REVIEW_CONTEXT)

    try:
        application = profile.tutor_application
    except TutorApplication.DoesNotExist:
        return dict(EMPTY_DOCUMENT_REVIEW_CONTEXT)

    return get_document_review_context(application, 'tutor')


def get_role_document_review_context(profile):
    """Role-generic dispatcher used by profile_status: identical output to
    get_tutor_document_review_context for tutors (zero behavior change there), and the equivalent for
    tutees via Phase 1's get_document_review_context — see
    docs/plans/2026-07-01-tutee-verification-phase3-ui.md."""
    if profile.role == 'Tutor':
        return get_tutor_document_review_context(profile)

    if profile.role == 'Tutee':
        application = getattr(profile, 'tutee_application', None)
        if application is None:
            return dict(EMPTY_DOCUMENT_REVIEW_CONTEXT)
        return get_document_review_context(application, 'tutee')

    return dict(EMPTY_DOCUMENT_REVIEW_CONTEXT)


def tutee_verification_enforced():
    """True once the global grace-period cutover for tutee enrollment verification has passed.
    A single global date, not per-account, and unset (never enforced) by default — see
    docs/plans/2026-07-01-tutee-verification-phase2-gate.md."""
    # Dev-only runtime override (self-service verification dev tools). Guarded by the flag so the
    # production path does zero extra work — see docs/plans/2026-07-02-verification-dev-tools.md.
    if settings.VERIFICATION_DEV_TOOLS_ENABLED:
        override = _verification_dev.enforcement_override_get()
        if override is not None:
            return override

    cutover_str = settings.TUTEE_VERIFICATION_ENFORCEMENT_START_DATE
    if not cutover_str:
        return False

    try:
        cutover = date.fromisoformat(cutover_str)
    except ValueError:
        logger.error(
            "TUTEE_VERIFICATION_ENFORCEMENT_START_DATE is not a valid ISO date: %r. "
            "Treating tutee verification as not yet enforced.",
            cutover_str,
        )
        return False

    return timezone.now().date() >= cutover


def get_verification_application(profile):
    if profile.role == 'Tutor':
        return getattr(profile, 'tutor_application', None)
    if profile.role == 'Tutee':
        return getattr(profile, 'tutee_application', None)
    return None


def can_create_new_booking(profile):
    """Source-of-truth check for the forward-only booking gate: can this profile take on NEW work
    (a tutee creating a booking, a tutor accepting a pending booking request)? Existing bookings,
    wallet, and dashboard access are never affected by this check."""
    if profile.role == 'Tutee' and not tutee_verification_enforced():
        return True

    application = get_verification_application(profile)
    if application is None:
        return False

    if not (
        application.application_status == 'approved'
        and application.document_renewal_status() == 'verified'
    ):
        return False

    return not has_reached_monthly_strike_cap(profile)


def get_monthly_counted_strike_count(profile, reference_time=None):
    reference_time = timezone.localtime(reference_time or timezone.now())
    return SupportTicket.objects.filter(
        category='Late_Cancellation',
        resolution_verdict='counted',
        penalized_user=profile,
        created_at__year=reference_time.year,
        created_at__month=reference_time.month,
    ).count()


def has_reached_monthly_strike_cap(profile, reference_time=None):
    return get_monthly_counted_strike_count(profile, reference_time) >= MONTHLY_STRIKE_CAP


# --- Verification dev tools (self-service) ---------------------------------------------------------
# Gated by settings.VERIFICATION_DEV_TOOLS_ENABLED, checked first in each view (403 when off) so the
# endpoints are inert in production. Every action mutates only request.user's own application.
# See docs/plans/2026-07-02-verification-dev-tools.md.

def _verification_dev_readout(profile):
    application = get_verification_application(profile)
    due_at = application.document_renewal_due_at() if application else None
    return {
        "role": profile.role,
        "role_has_verification": _verification_dev.role_has_verification(profile),
        "application_status": application.application_status if application else None,
        "document_renewal_status": application.document_renewal_status() if application else None,
        "document_renewal_due_at": due_at.isoformat() if due_at else None,
        "tutee_verification_enforced": tutee_verification_enforced(),
        "enforcement_override": _verification_dev.enforcement_override_get(),
        "available_states": list(_verification_dev.VERIFICATION_STATES),
    }


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dev_verification_readout(request):
    if not settings.VERIFICATION_DEV_TOOLS_ENABLED:
        return Response({"error": "Verification dev tools are disabled."}, status=403)
    return Response(_verification_dev_readout(request.user.userprofile))


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def dev_verification_set_state(request):
    if not settings.VERIFICATION_DEV_TOOLS_ENABLED:
        return Response({"error": "Verification dev tools are disabled."}, status=403)

    profile = request.user.userprofile
    if not _verification_dev.role_has_verification(profile):
        return Response({"error": f"Verification does not apply to role {profile.role}."}, status=400)

    state = request.data.get("state")
    if state not in _verification_dev.VERIFICATION_STATES:
        return Response(
            {"error": "Invalid state.", "available_states": list(_verification_dev.VERIFICATION_STATES)},
            status=400,
        )

    with transaction.atomic():
        _verification_dev.set_verification_state(profile, state)

    PlatformActivity.objects.create(
        activity_type='admin_action',
        message=f"[DEV] {profile.fname} {profile.lname} set own verification state to '{state}'",
        institution=profile.institution,
    )
    return Response(_verification_dev_readout(profile))


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def dev_verification_set_enforcement(request):
    if not settings.VERIFICATION_DEV_TOOLS_ENABLED:
        return Response({"error": "Verification dev tools are disabled."}, status=403)

    mode = request.data.get("mode")
    if mode == "on":
        _verification_dev.enforcement_override_set(True)
    elif mode == "off":
        _verification_dev.enforcement_override_set(False)
    elif mode == "clear":
        _verification_dev.enforcement_override_clear()
    else:
        return Response({"error": "mode must be one of: on, off, clear."}, status=400)

    profile = request.user.userprofile
    PlatformActivity.objects.create(
        activity_type='admin_action',
        message=f"[DEV] {profile.fname} {profile.lname} set tutee verification enforcement override to '{mode}'",
        institution=profile.institution,
    )

    return Response(_verification_dev_readout(request.user.userprofile))


# --- Recommendation algorithm demo tool (staff-only) ------------------------------------------
# Gated by settings.ALGORITHM_DEMO_TOOLS_ENABLED, checked first in each view (403 when off), plus
# IsSuperAdminUser (not the looser IsAdminUser) since this reads other users' names and rating
# history — mirrors AdminUserVerificationDevToolsView, which restricts to SuperAdmin for the same
# reason. Backs the standalone HTML demo tool at
# docs/artifacts/2026-07-04-recommendation-algorithm-live-demo.html.
# See docs/plans/2026-07-04-recommendation-algorithm-demo-tool.md.

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSuperAdminUser])
def algorithm_demo_search_tutees(request):
    if not settings.ALGORITHM_DEMO_TOOLS_ENABLED:
        return Response({"error": "Algorithm demo tools are disabled."}, status=403)

    query = request.query_params.get('q', '').strip()
    institution_id = request.query_params.get('institution_id') or None
    return Response({"tutees": search_tutees(query, institution_id=institution_id)})


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSuperAdminUser])
def algorithm_demo_recommend(request):
    if not settings.ALGORITHM_DEMO_TOOLS_ENABLED:
        return Response({"error": "Algorithm demo tools are disabled."}, status=403)

    tutee_id = request.query_params.get('tutee_id')
    if not tutee_id:
        return Response({"error": "tutee_id is required."}, status=400)

    tutee = get_object_or_404(UserProfile, id=tutee_id, role="Tutee")
    institution_id = request.query_params.get('institution_id') or None
    result = build_algorithm_demo_recommendation(tutee, institution_id=institution_id)
    return Response(result)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsSuperAdminUser])
def algorithm_demo_recommend_whatif(request):
    """Re-run the recommender with what-if rating overrides applied in memory.

    POST rather than GET because the override list is a body, not a query, but
    this writes nothing — it is the read-only counterpart of
    algorithm_demo_recommend. Overrides let the demo panel retune a rating and
    watch the ranking respond while the numbers still come from the real
    recommender, instead of a second implementation in the frontend.
    """
    if not settings.ALGORITHM_DEMO_TOOLS_ENABLED:
        return Response({"error": "Algorithm demo tools are disabled."}, status=403)

    tutee_id = request.data.get('tutee_id')
    if not tutee_id:
        return Response({"error": "tutee_id is required."}, status=400)

    raw_overrides = request.data.get('overrides') or []
    if not isinstance(raw_overrides, list):
        return Response({"error": "overrides must be a list."}, status=400)

    overrides = []
    for entry in raw_overrides:
        if not isinstance(entry, dict):
            return Response({"error": "Each override must be an object."}, status=400)
        try:
            student_id = int(entry.get('student_id'))
            tutor_id = int(entry.get('tutor_id'))
            rating_score = int(entry.get('rating_score'))
        except (TypeError, ValueError):
            return Response(
                {"error": "Each override needs student_id, tutor_id and rating_score."},
                status=400,
            )
        if rating_score < 1 or rating_score > 5:
            return Response({"error": "rating_score must be between 1 and 5."}, status=400)
        overrides.append({
            "student_id": student_id,
            "tutor_id": tutor_id,
            "rating_score": rating_score,
        })

    tutee = get_object_or_404(UserProfile, id=tutee_id, role="Tutee")
    institution_id = request.data.get('institution_id') or None
    result = build_algorithm_demo_recommendation(
        tutee, institution_id=institution_id, overrides=overrides
    )
    return Response(result)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated, IsSuperAdminUser])
def algorithm_demo_update_rating(request):
    if not settings.ALGORITHM_DEMO_TOOLS_ENABLED:
        return Response({"error": "Algorithm demo tools are disabled."}, status=403)

    student_id = request.data.get('student_id')
    tutor_id = request.data.get('tutor_id')
    try:
        rating_score = int(request.data.get('rating_score'))
    except (TypeError, ValueError):
        return Response({"error": "A valid rating_score is required."}, status=400)
    if rating_score < 1 or rating_score > 5:
        return Response({"error": "rating_score must be between 1 and 5."}, status=400)

    rating = Rating.objects.filter(
        student_id=student_id, tutor_id=tutor_id
    ).order_by('-id').first()
    if rating is None:
        return Response({"error": "No existing rating found for this pair."}, status=404)

    rating.rating_score = rating_score
    rating.save(update_fields=['rating_score'])
    update_tutor_rating_average(rating.tutor)
    return Response({"ok": True, "rating_score": rating.rating_score})


def build_admin_profile_defaults(user):
    display_name = (
        user.get_full_name().strip()
        or user.email.split('@', 1)[0]
        or user.username
        or 'Admin'
    )
    name_parts = display_name.replace('.', ' ').replace('_', ' ').split()

    fname = user.first_name or (name_parts[0] if name_parts else 'Admin')
    lname = user.last_name or (' '.join(name_parts[1:]) if len(name_parts) > 1 else 'User')

    return {
        'fname': fname[:100],
        'mname': '',
        'lname': lname[:100],
        'role': 'SuperAdmin',
        'profile_completed': True,
        'is_domain_exempt': True,
        'is_suspended': False,
    }


def get_login_profile_for_user(user):
    try:
        profile = user.userprofile
    except UserProfile.DoesNotExist:
        if not (user.is_staff or user.is_superuser):
            return None

        profile = UserProfile.objects.create(
            user=user,
            **build_admin_profile_defaults(user),
        )

    if user.is_staff or user.is_superuser:
        updated_fields = []

        if profile.role != 'SuperAdmin':
            profile.role = 'SuperAdmin'
            updated_fields.append('role')

        if not profile.profile_completed:
            profile.profile_completed = True
            updated_fields.append('profile_completed')

        if not profile.is_domain_exempt:
            profile.is_domain_exempt = True
            updated_fields.append('is_domain_exempt')

        if updated_fields:
            updated_fields.append('updated_at')
            profile.save(update_fields=updated_fields)

    return profile


def generate_otp_code():
    return f"{secrets.randbelow(1000000):06d}"


def hash_otp_code(user_id, challenge_id, purpose, code):
    message = f"{purpose}:{user_id}:{challenge_id}:{code}".encode("utf-8")
    return hmac.new(
        settings.SECRET_KEY.encode("utf-8"),
        message,
        hashlib.sha256,
    ).hexdigest()


def verify_otp_code(challenge, code):
    expected_hash = hash_otp_code(
        challenge.user_id,
        challenge.challenge_id,
        challenge.purpose,
        str(code or ""),
    )
    return constant_time_compare(challenge.code_hash, expected_hash)


def get_login_otp_expiry():
    return timezone.now() + timedelta(seconds=settings.LOGIN_OTP_TTL_SECONDS)


def create_login_otp_challenge(user):
    EmailOTPChallenge.objects.filter(
        user=user,
        purpose=EmailOTPChallenge.PURPOSE_LOGIN,
        consumed_at__isnull=True,
    ).delete()

    code = generate_otp_code()
    challenge = EmailOTPChallenge(
        user=user,
        purpose=EmailOTPChallenge.PURPOSE_LOGIN,
        expires_at=get_login_otp_expiry(),
    )
    challenge.code_hash = hash_otp_code(
        user.id,
        challenge.challenge_id,
        challenge.purpose,
        code,
    )
    challenge.save()

    try:
        mailer.send_login_otp(user, code)
    except EmailRateLimitError:
        challenge.delete()
        raise
    except Exception:
        challenge.delete()
        logger.exception("Failed to send login OTP email for user_id=%s", user.id)
        raise

    if settings.DEBUG or settings.OTP_DEBUG_CODE_ENABLED:
        challenge.debug_code = code

    return challenge


def build_otp_challenge_response(challenge, message):
    payload = {
        "requires_2fa": True,
        "challenge_id": str(challenge.challenge_id),
        "message": message,
    }

    if (settings.DEBUG or settings.OTP_DEBUG_CODE_ENABLED) and hasattr(challenge, "debug_code"):
        payload["debug_code"] = challenge.debug_code

    return payload


def get_user_from_reset_uid(uid):
    try:
        user_id = force_str(urlsafe_base64_decode(uid))
        return User.objects.get(pk=user_id)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist, ValidationError):
        return None


def blacklist_user_refresh_tokens(user):
    try:
        for outstanding_token in OutstandingToken.objects.filter(user=user):
            BlacklistedToken.objects.get_or_create(token=outstanding_token)
    except Exception:
        logger.exception("Failed to blacklist outstanding refresh tokens for user_id=%s", user.id)


WEEKDAY_MAP = {
    0: "Mon",
    1: "Tue",
    2: "Wed",
    3: "Thu",
    4: "Fri",
    5: "Sat",
    6: "Sun",
}

SESSION_SLOT_MINUTES = 60


def get_duration_hours_from_slot_count(slot_count):
    return round((slot_count * SESSION_SLOT_MINUTES) / 60, 2)


def get_duration_hours_for_bookings(bookings):
    return get_duration_hours_from_slot_count(len(bookings))

def parse_request_date(date_string):
    try:
        return datetime.strptime(date_string, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


def get_override_maps(tutor, start_date, end_date):
    overrides = TutorAvailabilityOverride.objects.filter(
        tutor=tutor,
        override_date__range=(start_date, end_date)
    ).select_related('availability')

    full_day_dates = {
        override.override_date
        for override in overrides
        if override.is_full_day
    }

    slot_override_keys = {
        (override.availability_id, override.override_date)
        for override in overrides
        if not override.is_full_day and override.availability_id is not None
    }

    return full_day_dates, slot_override_keys


def has_confirmed_or_completed_booking_conflict(tutor, override_date, availability=None):
    booking_filter = Booking.objects.filter(
        tutor=tutor,
        session_date=override_date,
        status__in=["Confirmed", "Completed"]
    )

    if availability is not None:
        booking_filter = booking_filter.filter(availability=availability)

    return booking_filter.exists()


def slot_is_overridden(tutor, override_date, availability):
    return TutorAvailabilityOverride.objects.filter(
        tutor=tutor,
        override_date=override_date
    ).filter(
        Q(is_full_day=True) | Q(availability=availability)
    ).exists()

def get_booking_end_time(booking):
    return (
        datetime.combine(booking.session_date, booking.availability.time_slot)
        + timedelta(minutes=SESSION_SLOT_MINUTES)
    ).time()


def sort_bookings_for_session_group(bookings):
    return sorted(
        bookings,
        key=lambda booking: (booking.session_date, booking.availability.time_slot, booking.id)
    )


def group_slot_requests(slot_requests):
    grouped_slots = []
    current_group = []
    previous_slot = None

    for slot_request in slot_requests:
        if not current_group:
            current_group = [slot_request]
            previous_slot = slot_request
            continue

        previous_end = (
            datetime.combine(previous_slot["session_date"], previous_slot["availability"].time_slot)
            + timedelta(minutes=SESSION_SLOT_MINUTES)
        ).time()

        if (
            previous_slot["session_date"] == slot_request["session_date"]
            and previous_end == slot_request["availability"].time_slot
        ):
            current_group.append(slot_request)
        else:
            grouped_slots.append(current_group)
            current_group = [slot_request]

        previous_slot = slot_request

    if current_group:
        grouped_slots.append(current_group)

    return grouped_slots


def get_session_group_bookings(booking):
    if booking.session_group_id is None:
        booking_group = [booking]
    else:
        booking_group = list(
            Booking.objects.filter(session_group_id=booking.session_group_id)
            .select_related(
                'student__course',
                'tutor__profile__course',
                'tutor__profile__user',
                'availability',
                'payment__method',
                'rating'
            )
            .order_by('session_date', 'availability__time_slot', 'id')
        )

    return sort_bookings_for_session_group(booking_group)


def get_tutor_acceptance_load_snapshot(tutor):
    accepted_session_load = tutor.accepted_session_load()
    session_load_limit = int(tutor.session_load_limit or 0)
    return {
        "accepted_session_load": accepted_session_load,
        "session_load_limit": session_load_limit,
        "session_load_remaining": max(session_load_limit - accepted_session_load, 0),
    }


def get_booking_request_bookings(booking):
    if booking.booking_request_id is None:
        return get_session_group_bookings(booking)

    booking_group = list(
        Booking.objects.filter(booking_request_id=booking.booking_request_id)
        .select_related(
            'student__course',
            'tutor__profile__course',
            'tutor__profile__user',
            'availability',
            'payment__method',
            'rating'
        )
        .order_by('session_date', 'availability__time_slot', 'id')
    )

    return sort_bookings_for_session_group(booking_group)


def get_dashboard_pill_bookings(booking):
    base_queryset = Booking.objects.select_related(
        'student__course',
        'student__user',
        'tutor__profile__course',
        'tutor__profile__user',
        'availability',
        'payment__method',
        'rating',
    ).filter(
        student=booking.student,
        tutor=booking.tutor,
        session_date=booking.session_date,
        status=booking.status,
    )

    if booking.booking_request_id:
        booking_group = base_queryset.filter(booking_request_id=booking.booking_request_id)
    elif booking.session_group_id:
        booking_group = base_queryset.filter(session_group_id=booking.session_group_id)
    else:
        booking_group = base_queryset.filter(id=booking.id)

    return sort_bookings_for_session_group(
        booking_group.order_by('session_date', 'availability__time_slot', 'id')
    )


def get_representative_booking(bookings):
    if bookings is None:
        return None

    if hasattr(bookings, "first"):
        return bookings.first()

    if isinstance(bookings, (list, tuple)):
        sorted_group = sort_bookings_for_session_group(bookings)
        return sorted_group[0] if sorted_group else None

    for booking in bookings:
        return booking

    return None


def booking_subject_label(booking):
    return booking.subject.subject_name if booking.subject else "General"


def get_dashboard_hidden_for_profile(bookings, profile):
    if not profile:
        return False

    for booking in bookings:
        if profile == booking.student:
            if booking.dashboard_hidden_by_student_at:
                return True
        elif profile == booking.tutor.profile and booking.dashboard_hidden_by_tutor_at:
            return True

    return False


def get_session_notification_context(bookings):
    representative_booking = get_representative_booking(bookings)

    if not representative_booking:
        return {
            "subject": "session",
            "date": "an upcoming date",
            "tutor_name": "your tutor",
            "tutee_name": "the tutee",
        }

    subject = booking_subject_label(representative_booking)
    date_label = representative_booking.session_date.strftime("%Y-%m-%d")
    tutor_name = f"{representative_booking.tutor.profile.fname} {representative_booking.tutor.profile.lname}"
    tutee_name = f"{representative_booking.student.fname} {representative_booking.student.lname}"

    return {
        "subject": subject,
        "date": date_label,
        "tutor_name": tutor_name,
        "tutee_name": tutee_name,
    }


DEV_LIVE_PHASES = {
    'upcoming': (12, 72),
    'start': (-5, 55),
    'midpoint': (-30, 30),
    'ending': (-55, 5),
    'handoff': (-70, -10),
}
DEV_LIVE_CACHE_TIMEOUT_SECONDS = 60 * 60 * 6


def get_dev_live_cache_keys_for_booking(booking):
    if booking.status == "Pending" and booking.booking_request_id:
        return [f"studybuddy:dev-live:request:{booking.booking_request_id}"]

    if booking.session_group_id:
        return [f"studybuddy:dev-live:group:{booking.session_group_id}"]

    if booking.booking_request_id:
        return [f"studybuddy:dev-live:request:{booking.booking_request_id}"]

    return [f"studybuddy:dev-live:booking:{booking.id}"]


def get_dev_live_override_for_bookings(bookings):
    if not settings.BOOKING_DEV_TOOLS_ENABLED:
        return None

    for booking in sort_bookings_for_session_group(bookings):
        for key in get_dev_live_cache_keys_for_booking(booking):
            override = cache.get(key)
            if override:
                return override

    return None


def set_dev_live_override_for_bookings(bookings, override):
    keys = {
        key
        for booking in sort_bookings_for_session_group(bookings)
        for key in get_dev_live_cache_keys_for_booking(booking)
    }

    for key in keys:
        cache.set(key, override, DEV_LIVE_CACHE_TIMEOUT_SECONDS)


def clear_dev_live_override_for_bookings(bookings):
    for booking in sort_bookings_for_session_group(bookings):
        for key in get_dev_live_cache_keys_for_booking(booking):
            cache.delete(key)


def build_dev_live_override(phase):
    offsets = DEV_LIVE_PHASES[phase]
    current_time = timezone.localtime(timezone.now()).replace(second=0, microsecond=0)
    start_at = current_time + timedelta(minutes=offsets[0])
    end_at = current_time + timedelta(minutes=offsets[1])

    return {
        "phase": phase,
        "date": start_at.date().isoformat(),
        "start_time": start_at.time().strftime("%H:%M"),
        "end_time": end_at.time().strftime("%H:%M"),
        "forced_at": current_time.isoformat(),
    }


def apply_dev_live_override(bookings, session_date, start_time, end_time):
    override = get_dev_live_override_for_bookings(bookings)

    if not override:
        return session_date, start_time, end_time

    return (
        datetime.strptime(override["date"], "%Y-%m-%d").date(),
        datetime.strptime(override["start_time"], "%H:%M").time(),
        datetime.strptime(override["end_time"], "%H:%M").time(),
    )


def get_display_status(raw_status, session_date, start_time, end_time):
    normalized = str(raw_status or '').lower()

    if normalized == 'confirmed':
        timezone_now = timezone.localtime()
        timezone_info = timezone.get_current_timezone()
        start_at = timezone.make_aware(datetime.combine(session_date, start_time), timezone_info)
        end_at = timezone.make_aware(datetime.combine(session_date, end_time), timezone_info)

        if timezone_now < start_at:
            return 'Upcoming'

        if start_at <= timezone_now < end_at:
            return 'Ongoing'

        return 'Payment Required'

    if normalized == 'awaiting payment verification':
        return 'Awaiting Verification'

    return raw_status


def get_current_display_status_for_booking(booking):
    session_group_bookings = get_session_group_bookings(booking)
    representative_booking = get_representative_booking(session_group_bookings)
    first_booking = session_group_bookings[0]
    last_booking = session_group_bookings[-1]

    start_time = first_booking.availability.time_slot
    end_time = (
        datetime.combine(first_booking.session_date, last_booking.availability.time_slot)
        + timedelta(minutes=SESSION_SLOT_MINUTES)
    ).time()
    session_date, start_time, end_time = apply_dev_live_override(
        session_group_bookings,
        representative_booking.session_date,
        start_time,
        end_time,
    )

    return get_display_status(representative_booking.status, session_date, start_time, end_time)


def create_booking_status_notification(
    recipient,
    status_key,
    bookings,
    recipient_role=None,
    actor_role=None,
    reason=None,
    cancellation_deadline=None,
    is_born_late=False,
):
    context = get_session_notification_context(bookings)

    messages = {
        "pending": f"New booking request received for {context['subject']} on {context['date']}. Please review and respond.",
        "confirmed": f"Your booking for {context['subject']} with {context['tutor_name']} is confirmed. The session is now upcoming.",
        "rejected": f"Your booking for {context['subject']} with {context['tutor_name']} on {context['date']} was rejected.",
        "awaiting_payment_verification": f"A tutee has confirmed their {context['subject']} session on {context['date']} and sent payment for review.",
        "completed": f"Your session for {context['subject']} with {context['tutor_name']} was marked complete. You can rate it anytime.",
    }

    if status_key == "cancelled":
        actor = actor_role or "tutee"
        if recipient_role == "tutor":
            if actor == "tutor":
                message = f"You cancelled your {context['subject']} session on {context['date']}."
            else:
                message = f"{context['tutee_name']} has cancelled your {context['subject']} session on {context['date']}."
        elif recipient_role == "tutee":
            if actor == "tutor":
                message = f"Your {context['subject']} session on {context['date']} was cancelled by {context['tutor_name']}."
            else:
                message = f"Your {context['subject']} session on {context['date']} has been successfully cancelled."
        else:
            message = None

        if message and reason:
            message = f"{message} Reason: {reason}"
    else:
        message = messages.get(status_key)

    if status_key == 'confirmed' and message:
        if is_born_late:
            message = f'{message} This booking has no penalty-free cancellation window.'
        elif cancellation_deadline:
            message = f'{message} Cancel without a strike before {cancellation_deadline}.'

    if not message:
        return

    Notification.objects.create(
        recipient=recipient,
        message=message
    )


def update_tutor_rating_average(tutor):
    aggregate = Rating.objects.filter(tutor=tutor).aggregate(average=Avg('rating_score'))
    tutor.rating_average = round(aggregate['average'] or 0, 2)
    tutor.save(update_fields=['rating_average'])


def get_payment_method_code(payment):
    return getattr(getattr(payment, 'method', None), 'code', None)


# All codes that the UI labels as "Online Payment"
ONLINE_LABEL_CODES = {'online', 'PAYMONGO', 'GCASH', 'BANK'}

# Codes whose payments are settled via PayMongo and should auto-credit the tutor wallet.
# GCASH and BANK are excluded: they may be settled via a separate manual or external flow.
PAYMONGO_SETTLED_CODES = {'online', 'PAYMONGO'}


def get_payment_method_label(payment):
    method = getattr(payment, 'method', None)

    if not method:
        return None

    if method.code in ONLINE_LABEL_CODES:
        return 'Online Payment'

    return method.method_name


def get_wallet_transaction_payment_reference(wallet_transaction):
    reference_id = wallet_transaction.reference_id or ''

    if not reference_id.startswith('BK-'):
        return None

    try:
        booking_id = int(reference_id.removeprefix('BK-'))
    except ValueError:
        return None

    payment = Payment.objects.filter(booking_id=booking_id).only('transaction_reference').first()
    if not payment:
        return None

    return payment.transaction_reference


def get_wallet_transaction_student_name(wallet_transaction):
    reference_id = wallet_transaction.reference_id or ''

    if not reference_id.startswith('BK-'):
        return None

    try:
        booking_id = int(reference_id.removeprefix('BK-'))
    except ValueError:
        return None

    booking = Booking.objects.filter(id=booking_id).select_related('student').first()
    if not booking:
        return None

    return f"{booking.student.fname} {booking.student.lname}".strip() or None


def get_wallet_transaction_description(wallet_transaction, student_name=None):
    description = wallet_transaction.description

    if wallet_transaction.transaction_type != 'session_credit' or not student_name:
        return description

    base_description = description.split(' - Transaction ID:', 1)[0]
    base_description = base_description.split(' - Student:', 1)[0]
    return f"{base_description} - Student: {student_name}"


def build_absolute_media_url(request, field_file):
    if not field_file:
        return None

    file_url = field_file.url
    if request is None:
        return file_url

    return request.build_absolute_uri(file_url)


def serialize_payment_summary(representative_booking, request=None):
    payment = getattr(representative_booking, 'payment', None)

    if not payment:
        return {
            "transaction_id": None,
            "method": None,
            "amount_paid": 0,
            "tutor_earned": 0,
            "platform_fee": 0,
            "transaction_fee": 0,
            "status": "Pending",
            "receipt_image": None,
        }

    amount_paid = float(payment.amount)
    method = get_payment_method_label(payment)
    method_code = get_payment_method_code(payment)
    platform_fee = round(amount_paid * 0.16, 2)

    if method_code == "GCASH":
        transaction_fee = round(amount_paid * 0.04, 2)
    else:
        transaction_fee = 0

    tutor_earned = round(amount_paid - platform_fee - transaction_fee, 2)

    return {
        "transaction_id": payment.transaction_reference,
        "method": method,
        "amount_paid": amount_paid,
        "tutor_earned": tutor_earned,
        "platform_fee": platform_fee,
        "transaction_fee": transaction_fee,
        "status": payment.payment_status,
        "receipt_image": build_absolute_media_url(request, payment.receipt_image),
    }


def serialize_session_check_ins(representative_booking):
    responses = {
        SessionCheckIn.EVENT_VENUE_CONFIRM: None,
        SessionCheckIn.EVENT_MIDPOINT_CHECKIN: None,
    }

    check_ins = getattr(representative_booking, 'prefetched_check_ins', None)
    if check_ins is None:
        check_ins = representative_booking.check_ins.all()

    for check_in in check_ins:
        responses[check_in.event_type] = {
            "id": check_in.id,
            "response": check_in.response,
            "responded_at": check_in.responded_at.isoformat(),
        }

    return responses


def get_tutee_owned_booking_or_403(request, booking_id):
    profile = request.user.userprofile
    booking = get_object_or_404(
        Booking.objects.select_related(
            'student',
            'availability',
            'tutor__profile',
        ),
        id=booking_id,
    )

    if profile != booking.student:
        return None, Response({"error": "Unauthorized"}, status=403)

    return booking, None


def create_session_check_in_response(booking, event_type, response_value):
    return SessionCheckIn.objects.get_or_create(
        booking=booking,
        event_type=event_type,
        defaults={"response": response_value},
    )
@api_view(['GET'])
@authentication_classes([])
def partner_institutions_list(request):

    institutions = PartnerInstitution.objects.filter(is_active=True).order_by('institution_name')

    data = [
        {
            "id": institution.id,
            "institution_name": institution.institution_name,
            "school_email_domain": normalize_stored_domain(institution.school_email_domain),
            "contact_person": institution.contact_person
        }
        for institution in institutions
    ]

    return Response(data)


@api_view(['POST'])
@authentication_classes([])
@throttle_classes([RegisterRateThrottle])
@transaction.atomic
def register_user(request):

    email = request.data.get('email')
    password = request.data.get('password')
    fname = request.data.get('fname')
    mname = request.data.get('mname', '')
    lname = request.data.get('lname')
    role = request.data.get('role')
    institution_id = request.data.get('institution_id')

    # Validate required fields
    if not all([email, password, fname, lname, role, institution_id]):
        return Response(
            {"error": "Missing required fields"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        institution = PartnerInstitution.objects.get(id=institution_id, is_active=True)
    except PartnerInstitution.DoesNotExist:
        return Response(
            {"error": "Your institution is not a registered partner. Please contact support."},
            status=status.HTTP_400_BAD_REQUEST
        )

    email_domain = normalize_email_domain(email)
    institution_domain = normalize_stored_domain(institution.school_email_domain)

    if email_domain != institution_domain:
        return Response(
            {"error": "Your email domain does not match the selected institution. Please check and try again."},
            status=status.HTTP_400_BAD_REQUEST
        )

    existing_user = User.objects.filter(username=email).first()

    if existing_user and hasattr(existing_user, 'userprofile'):
        return Response(
            {"error": "User already exists"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if existing_user:
        logger.warning(
            "Recovering orphaned auth_user without profile: email=%s user_id=%s",
            email,
            existing_user.id,
        )
        user = existing_user
        user.email = email
        user.set_password(password)
        user.save(update_fields=["email", "password"])
    else:
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password
        )

    if hasattr(user, 'userprofile'):
        profile = user.userprofile
        profile.fname = fname
        profile.mname = mname
        profile.lname = lname
        profile.role = role
        profile.institution = institution
        profile.save()
    else:
        profile = UserProfile.objects.create(
            user=user,
            fname=fname,
            mname=mname,
            lname=lname,
            role=role,
            institution=institution
        )

    # 🔥 Create/Update Tutor record if role is Tutor
    if role == "Tutor":
        Tutor.objects.get_or_create(profile=profile)

    PlatformActivity.objects.create(
        activity_type='registration',
        message=f"New {role} registered: {fname} {lname} ({email})",
        institution=profile.institution
    )

    logger.info(
        "Registered user in database: email=%s user_id=%s profile_id=%s role=%s institution_id=%s",
        email,
        user.id,
        profile.id,
        role,
        institution_id,
    )

    return Response(
        {"message": "User registered successfully"},
        status=status.HTTP_201_CREATED
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_status(request):

    profile = get_login_profile_for_user(request.user)

    if profile is None:
        return Response(
            {"error": "User profile not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    document_context = get_role_document_review_context(profile)
    wallet_negative = False
    tutor_subject_count = 0
    # Default True (never gated) for non-Tutors and Tutors with no Tutor row yet — the commission
    # gate only applies once a Tutor record exists to accept terms on. See ADR-0010.
    commission_terms_accepted = True
    if profile.role == 'Tutor':
        tutor = getattr(profile, 'tutor', None)
        if tutor is not None:
            wallet = Wallet.objects.filter(tutor=tutor).first()
            wallet_negative = bool(wallet and wallet.balance < 0)
            tutor_subject_count = TutorSubjects.objects.filter(tutor=tutor).count()
            commission_terms_accepted = tutor.commission_terms_accepted_at is not None

    return Response({
        "profile_completed": profile.profile_completed,
        "role": profile.role,
        "wallet_negative": wallet_negative,
        "tutee_verification_enforced": tutee_verification_enforced(),
        **get_tutor_onboarding_context(profile),
        "tutor_subject_count": tutor_subject_count,
        "tutor_subjects_completed": tutor_subject_count > 0,
        "commission_terms_accepted": commission_terms_accepted,
        **document_context
    })

@api_view(['POST'])
@authentication_classes([])
@throttle_classes([LoginRateThrottle])
def login_view(request):

    email = request.data.get("email")
    password = request.data.get("password")

    if not email or not password:
        return Response(
            {"error": "Email and password required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 🔥 authenticate using email as username
    user = authenticate(username=email, password=password)

    if user is None:
        return Response(
            {"error": "Invalid credentials"},
            status=status.HTTP_401_UNAUTHORIZED
        )

    profile = get_login_profile_for_user(user)
    if profile is None:
        return Response(
            {"error": "User profile not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    if profile.is_suspended:
        return Response(
            {"error": "Your account has been suspended. Please contact administration for more details."},
            status=status.HTTP_403_FORBIDDEN
        )

    if not profile.is_domain_exempt and profile.role != 'SuperAdmin':
        email_domain = normalize_email_domain(email)
        active_institution = get_active_institution_by_domain(email_domain)

        if active_institution is None:
            institution = profile.institution

            if institution and not institution.is_active:
                return Response(
                    {"error": "Your institution's access has been suspended. Please contact support."},
                    status=status.HTTP_403_FORBIDDEN
                )

            return Response(
                {"error": "Your institution is not a registered partner. Please contact support."},
                status=status.HTTP_403_FORBIDDEN
            )

        profile_domain = (
            normalize_stored_domain(profile.institution.school_email_domain)
            if profile.institution
            else None
        )

        if profile.institution_id and profile_domain != email_domain:
            return Response(
                {"error": "Your email domain does not match your registered institution. Please contact support."},
                status=status.HTTP_403_FORBIDDEN
            )

        if profile.institution_id != active_institution.id:
            profile.institution = active_institution
            profile.save(update_fields=['institution', 'updated_at'])

    if settings.LOGIN_OTP_DISABLED:
        return Response(build_login_response_payload(user, profile))

    try:
        challenge = create_login_otp_challenge(user)
    except EmailRateLimitError:
        return Response(
            {"error": "Too many verification emails. Please wait a while and try again."},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )
    except Exception:
        return Response(
            {"error": "Unable to send verification code. Please try again."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return Response(
        build_otp_challenge_response(
            challenge,
            "A verification code has been sent to your email.",
        )
    )


@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
@throttle_classes([LoginRateThrottle])
def password_reset_request(request):
    email = str(request.data.get("email") or "").strip()

    if email:
        user = User.objects.filter(Q(username__iexact=email) | Q(email__iexact=email)).first()
        if user and user.is_active and user.has_usable_password():
            try:
                mailer.enqueue_password_reset(user)
            except Exception:
                logger.exception("Failed to queue password reset email for user_id=%s", user.id)

    return Response({"message": PASSWORD_RESET_GENERIC_MESSAGE})


@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
@throttle_classes([LoginRateThrottle])
def password_reset_confirm(request):
    uid = request.data.get("uid") or request.data.get("uidb64")
    token = request.data.get("token")
    password = request.data.get("password")
    password_confirm = request.data.get("password_confirm")

    if not all([uid, token, password, password_confirm]):
        return Response(
            {"error": "UID, token, password, and password confirmation are required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if password != password_confirm:
        return Response(
            {"error": "Passwords do not match."},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = get_user_from_reset_uid(uid)
    if user is None or not default_token_generator.check_token(user, token):
        return Response(
            {"error": "Invalid or expired password reset link."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        validate_password(password, user)
    except ValidationError as exc:
        return Response(
            {"error": exc.messages},
            status=status.HTTP_400_BAD_REQUEST
        )

    user.set_password(password)
    user.save(update_fields=["password"])
    blacklist_user_refresh_tokens(user)

    try:
        mailer.enqueue_password_changed(user)
    except Exception:
        logger.exception("Failed to queue password changed notification for user_id=%s", user.id)

    return Response({"message": "Password has been reset successfully."})


@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
@throttle_classes([LoginRateThrottle])
def login_verify_otp(request):
    challenge_id = request.data.get("challenge_id")
    code = request.data.get("code")

    if not challenge_id or not code:
        return Response(
            {"error": "Challenge ID and code are required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    challenge = EmailOTPChallenge.objects.select_related('user').filter(
        challenge_id=challenge_id,
        purpose=EmailOTPChallenge.PURPOSE_LOGIN,
    ).first()

    if challenge is None or challenge.consumed_at is not None or challenge.expires_at <= timezone.now():
        return Response({"error": OTP_ERROR_MESSAGE}, status=status.HTTP_400_BAD_REQUEST)

    if challenge.attempt_count >= settings.LOGIN_OTP_MAX_ATTEMPTS:
        return Response(
            {"error": "Too many verification attempts. Please request a new code."},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )

    if not verify_otp_code(challenge, code):
        challenge.attempt_count += 1
        challenge.save(update_fields=['attempt_count'])

        if challenge.attempt_count >= settings.LOGIN_OTP_MAX_ATTEMPTS:
            return Response(
                {"error": "Too many verification attempts. Please request a new code."},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        return Response({"error": OTP_ERROR_MESSAGE}, status=status.HTTP_400_BAD_REQUEST)

    try:
        profile = UserProfile.objects.get(user=challenge.user)
    except UserProfile.DoesNotExist:
        return Response(
            {"error": "User profile not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    if profile.is_suspended:
        return Response(
            {"error": "Your account has been suspended. Please contact administration for more details."},
            status=status.HTTP_403_FORBIDDEN
        )

    challenge.consumed_at = timezone.now()
    challenge.save(update_fields=['consumed_at'])

    return Response(build_login_response_payload(challenge.user, profile))


@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
@throttle_classes([LoginRateThrottle])
def login_resend_otp(request):
    challenge_id = request.data.get("challenge_id")

    if not challenge_id:
        return Response(
            {"error": "Challenge ID is required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    challenge = EmailOTPChallenge.objects.select_related('user').filter(
        challenge_id=challenge_id,
        purpose=EmailOTPChallenge.PURPOSE_LOGIN,
    ).first()

    if challenge is None or challenge.consumed_at is not None:
        return Response({"error": OTP_ERROR_MESSAGE}, status=status.HTTP_400_BAD_REQUEST)

    if challenge.attempt_count >= settings.LOGIN_OTP_MAX_ATTEMPTS:
        return Response(
            {"error": "Too many verification attempts. Please start login again."},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )

    code = generate_otp_code()
    new_hash = hash_otp_code(
        challenge.user_id,
        challenge.challenge_id,
        challenge.purpose,
        code,
    )
    new_expiry = get_login_otp_expiry()

    try:
        mailer.send_login_otp(challenge.user, code)
    except EmailRateLimitError:
        return Response(
            {"error": "Too many verification emails. Please wait a while and try again."},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )
    except Exception:
        logger.exception("Failed to resend login OTP email for user_id=%s", challenge.user_id)
        return Response(
            {"error": "Unable to send verification code. Please try again."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    challenge.code_hash = new_hash
    challenge.expires_at = new_expiry
    challenge.attempt_count = 0
    challenge.resend_count += 1
    challenge.save(update_fields=['code_hash', 'expires_at', 'attempt_count', 'resend_count'])

    if settings.DEBUG or settings.OTP_DEBUG_CODE_ENABLED:
        challenge.debug_code = code

    return Response(
        build_otp_challenge_response(
            challenge,
            "A new verification code has been sent to your email.",
        )
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """Blacklist the supplied refresh token so it can no longer be used."""
    refresh = request.data.get("refresh")
    if not refresh:
        return Response(
            {"error": "Refresh token required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        RefreshToken(refresh).blacklist()
    except TokenError:
        # Token already invalid/expired/blacklisted — logout is idempotent.
        return Response({"message": "Logged out."}, status=status.HTTP_200_OK)

    return Response({"message": "Logged out."}, status=status.HTTP_200_OK)


@api_view(['GET'])
def list_courses(request):

    courses = Course.objects.all()

    data = [
        {
            "course_code": c.course_code,
            "course_name": c.course_name
        }
        for c in courses
    ]

    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_dashboard(request):

    user_profile = UserProfile.objects.get(user=request.user)

    today = now().date()

    # -----------------------
    # UPCOMING SESSIONS
    # -----------------------
    upcoming_bookings = Booking.objects.filter(
        student=user_profile,
        status='Confirmed',
        session_date__gte=today
    ).select_related(
        'student',
        'tutor__profile__course',
        'availability',
        'rating'
    ).order_by('session_date', 'availability__time_slot')

    grouped_upcoming = defaultdict(list)

    for b in upcoming_bookings:
        grouped_upcoming[b.session_date].append(b)

    upcoming = []

    for session_date, day_bookings in grouped_upcoming.items():

        day_bookings.sort(key=lambda b: b.availability.time_slot)

        current_group = [day_bookings[0]]

        for booking in day_bookings[1:]:

            prev = current_group[-1]

            prev_end = (
                datetime.combine(session_date, prev.availability.time_slot)
                + timedelta(minutes=SESSION_SLOT_MINUTES)
            ).time()

            if booking.availability.time_slot == prev_end and booking.status == prev.status:
                current_group.append(booking)
            else:
                block = build_combined_block(current_group)

                upcoming.append({
                    "id": block["id"],
                    "subject": block["subject"],
                    "tutor": f"{current_group[0].tutor.profile.fname} {current_group[0].tutor.profile.lname}",
                    "date": block["date"].strftime("%Y-%m-%d"),
                    "time": f'{block["startTime"]} – {block["endTime"]}'
                })

                current_group = [booking]

        block = build_combined_block(current_group)

        upcoming.append({
            "id": block["id"],
            "subject": block["subject"],
            "tutor": f"{current_group[0].tutor.profile.fname} {current_group[0].tutor.profile.lname}",
            "date": block["date"].strftime("%Y-%m-%d"),
            "time": f'{block["startTime"]} – {block["endTime"]}'
        })

    # -----------------------
    # COMPLETED SESSIONS
    # -----------------------
    completed_bookings = Booking.objects.filter(
        student=user_profile,
        status='Completed'
    ).select_related(
        'student',
        'tutor__profile__course',
        'availability',
        'rating'
    ).order_by('-session_date', 'availability__time_slot')

    grouped_completed = defaultdict(list)

    for b in completed_bookings:
        grouped_completed[b.session_date].append(b)

    completed = []

    for session_date, day_bookings in grouped_completed.items():

        day_bookings.sort(key=lambda b: b.availability.time_slot)

        current_group = [day_bookings[0]]

        for booking in day_bookings[1:]:

            prev = current_group[-1]

            prev_end = (
                datetime.combine(session_date, prev.availability.time_slot)
                + timedelta(minutes=SESSION_SLOT_MINUTES)
            ).time()

            if booking.availability.time_slot == prev_end and booking.status == prev.status:
                current_group.append(booking)
            else:
                block = build_combined_block(current_group)

                completed.append({
                    "id": block["id"],
                    "subject": block["subject"],
                    "tutor": f"{current_group[0].tutor.profile.fname} {current_group[0].tutor.profile.lname}",
                    "date": block["date"].strftime("%Y-%m-%d"),
                    "time": f'{block["startTime"]} – {block["endTime"]}'
                })

                current_group = [booking]

        block = build_combined_block(current_group)

        completed.append({
            "id": block["id"],
            "subject": block["subject"],
            "tutor": f"{current_group[0].tutor.profile.fname} {current_group[0].tutor.profile.lname}",
            "date": block["date"].strftime("%Y-%m-%d"),
            "time": f'{block["startTime"]} – {block["endTime"]}'
        })

    # -----------------------
    # RECOMMENDED TUTORS (hybrid algorithm, cached per tutee)
    # -----------------------
    recommendations = get_dashboard_recommendations(user_profile)

    return Response({
        "upcoming": upcoming,
        "completed": completed,
        "recommendations": recommendations
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_recommendations(request):
    """Return only the (cached) dashboard recommendations.

    The tutee dashboard previously called student_dashboard just to read
    `recommendations`, discarding its all-time `upcoming`/`completed` payloads.
    This serves the cached recs directly via get_dashboard_recommendations
    (recommender/dashboard.py), turning that call into a cache hit.
    """
    user_profile = request.user.userprofile
    return Response({
        "recommendations": get_dashboard_recommendations(user_profile)
    })

#SearchTutors

class SearchTutorsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        subject_code = request.query_params.get('subject')

        if not subject_code:
            return Response(
                {"error": "Subject is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        student_profile = request.user.userprofile
        if not subject_is_recognized_for_profile(student_profile, subject_code):
            return Response(
                {"error": SUBJECT_NOT_RECOGNIZED_ERROR},
                status=status.HTTP_400_BAD_REQUEST,
            )
        tutors = Tutor.objects.filter(
            tutorsubjects__subject__subject_code=subject_code
        ).select_related('profile').distinct()

        serializer = TutorSearchSerializer(tutors, many=True)
        return Response(serializer.data)
#Subject Serializer

class SubjectListView(ListAPIView):
    serializer_class = SubjectSerializer

    def get_queryset(self):
        search_query = self.request.query_params.get('search', '').strip()
        user = self.request.user
        if not user.is_authenticated or not hasattr(user, 'userprofile'):
            queryset = Subjects.objects.filter(status='approved')
            if search_query:
                queryset = queryset.filter(
                    Q(subject_name__icontains=search_query)
                    | Q(subject_code__icontains=search_query)
                )
            return queryset

        profile = user.userprofile
        catalog_scope = self.request.query_params.get('catalog_scope')
        course_code = self.request.query_params.get('course_code')
        include_current = self.request.query_params.get('include_current') in {'1', 'true', 'True'}

        if catalog_scope == 'all':
            queryset = visible_subject_queryset_for_profile(profile).filter(status='approved')
            if search_query:
                queryset = queryset.filter(
                    Q(subject_name__icontains=search_query)
                    | Q(subject_code__icontains=search_query)
                )
            return queryset

        queryset, recognized_codes = subject_selection_queryset_for_profile(
            profile,
            course_code=course_code,
            include_current=include_current,
        )
        self.recognized_codes = recognized_codes
        if not include_current:
            # recognized_codes are already approved-status by construction; only re-filter
            # here when the caller didn't ask to keep the profile's current (possibly
            # pending, e.g. a tutor's own proposed-but-unreviewed) subjects.
            queryset = queryset.filter(status='approved')
        if search_query:
            queryset = queryset.filter(
                Q(subject_name__icontains=search_query)
                | Q(subject_code__icontains=search_query)
            )
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['recognized_codes'] = getattr(self, 'recognized_codes', set())
        return context



def build_combined_block(group, profile=None):

    sorted_group = sort_bookings_for_session_group(group)
    first = sorted_group[0]
    last = sorted_group[-1]
    representative_booking = get_representative_booking(sorted_group)

    start_time = first.availability.time_slot
    end_time = (
        datetime.combine(first.session_date, last.availability.time_slot)
        + timedelta(minutes=SESSION_SLOT_MINUTES)
    ).time()
    has_dev_live_override = get_dev_live_override_for_bookings(sorted_group) is not None
    session_date, start_time, end_time = apply_dev_live_override(
        sorted_group,
        first.session_date,
        start_time,
        end_time,
    )

    duration = get_duration_hours_for_bookings(sorted_group)

    # ensure correct status
    group_status = first.status
    display_status = get_display_status(
        group_status,
        session_date,
        start_time,
        end_time
    )

    if (
        settings.BOOKING_DEV_TOOLS_ENABLED
        and not has_dev_live_override
        and representative_booking.status == "Confirmed"
        and representative_booking.tutor_confirmed
    ):
        display_status = "Payment Required"

    return {
        "id": representative_booking.id,
        "session_group_id": str(representative_booking.session_group_id) if representative_booking.session_group_id else None,
        "booking_request_id": str(representative_booking.booking_request_id) if representative_booking.booking_request_id else None,
        "status": display_status,
        "raw_status": group_status,
        "date": session_date,
        "student": f"{first.student.fname} {first.student.lname}",
        "tuteeName": f"{first.student.fname} {first.student.lname}",
        "tutor": f"{first.tutor.profile.fname} {first.tutor.profile.lname}",
        "tutee_confirmed": representative_booking.tutee_confirmed,
        "tutor_confirmed": representative_booking.tutor_confirmed,
        "rating": representative_booking.rating.rating_score if hasattr(representative_booking, "rating") else None,
        "rating_submitted": hasattr(representative_booking, "rating"),

        "subject": booking_subject_label(first),
        "startTime": start_time.strftime("%H:%M"),
        "endTime": end_time.strftime("%H:%M"),
        "duration_hours": duration,
        "preferred_location": first.preferred_location,
        "can_edit_location": representative_booking.tutor_can_edit_location(),
        "session_mode": first.session_mode,
        "dashboard_hidden_by_current_user": get_dashboard_hidden_for_profile(sorted_group, profile),
    }


def build_time_block_payload(bookings):

    sorted_bookings = sort_bookings_for_session_group(bookings)
    first_booking = sorted_bookings[0]
    last_booking = sorted_bookings[-1]

    start_time = first_booking.availability.time_slot
    end_time = (
        datetime.combine(first_booking.session_date, last_booking.availability.time_slot)
        + timedelta(minutes=SESSION_SLOT_MINUTES)
    ).time()

    return {
        "date": first_booking.session_date.strftime("%Y-%m-%d"),
        "startTime": start_time.strftime("%H:%M"),
        "endTime": end_time.strftime("%H:%M"),
        "duration_hours": get_duration_hours_for_bookings(sorted_bookings),
        "session_group_id": str(first_booking.session_group_id) if first_booking.session_group_id else None,
    }


def split_bookings_into_time_blocks(bookings):

    sorted_bookings = sort_bookings_for_session_group(bookings)

    if not sorted_bookings:
        return []

    grouped_blocks = []
    current_block = [sorted_bookings[0]]

    for booking in sorted_bookings[1:]:
        previous_booking = current_block[-1]
        previous_end = (
            datetime.combine(previous_booking.session_date, previous_booking.availability.time_slot)
            + timedelta(minutes=SESSION_SLOT_MINUTES)
        ).time()

        same_session_group = (
            previous_booking.session_group_id is not None
            and booking.session_group_id is not None
            and previous_booking.session_group_id == booking.session_group_id
        )
        is_contiguous = (
            previous_booking.session_date == booking.session_date
            and previous_end == booking.availability.time_slot
        )

        if same_session_group and is_contiguous:
            current_block.append(booking)
            continue

        grouped_blocks.append(current_block)
        current_block = [booking]

    grouped_blocks.append(current_block)

    return [build_time_block_payload(block) for block in grouped_blocks]


def build_booking_request_block(group, profile=None):

    sorted_group = sort_bookings_for_session_group(group)
    representative_booking = get_representative_booking(sorted_group)
    first_booking = sorted_group[0]
    time_blocks = split_bookings_into_time_blocks(sorted_group)
    primary_block = time_blocks[0]
    group_status = first_booking.status

    return {
        "id": representative_booking.id,
        "session_group_id": str(representative_booking.session_group_id) if representative_booking.session_group_id else None,
        "booking_request_id": str(representative_booking.booking_request_id) if representative_booking.booking_request_id else None,
        "status": group_status,
        "raw_status": group_status,
        "date": first_booking.session_date,
        "student": f"{first_booking.student.fname} {first_booking.student.lname}",
        "tuteeName": f"{first_booking.student.fname} {first_booking.student.lname}",
        "tutor": f"{first_booking.tutor.profile.fname} {first_booking.tutor.profile.lname}",
        "tutee_confirmed": representative_booking.tutee_confirmed,
        "tutor_confirmed": representative_booking.tutor_confirmed,
        "rating": representative_booking.rating.rating_score if hasattr(representative_booking, "rating") else None,
        "rating_submitted": hasattr(representative_booking, "rating"),
        "subject": booking_subject_label(first_booking),
        "startTime": primary_block["startTime"],
        "endTime": primary_block["endTime"],
        "duration_hours": get_duration_hours_for_bookings(sorted_group),
        "preferred_location": first_booking.preferred_location,
        "session_mode": first_booking.session_mode,
        "time_blocks": time_blocks,
        "hasMultipleTimeBlocks": len(time_blocks) > 1,
        "dashboard_hidden_by_current_user": get_dashboard_hidden_for_profile(sorted_group, profile),
    }

#Tutor Dashboard View

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def tutor_dashboard(request):

    profile = request.user.userprofile

    try:
        tutor = Tutor.objects.get(profile=profile)
    except Tutor.DoesNotExist:
        return Response({"error": "Tutor not found"}, status=404)

    load_snapshot = get_tutor_acceptance_load_snapshot(tutor)

    # 📌 Completed sessions for earnings
    completed_bookings = Booking.objects.filter(
        tutor=tutor,
        status="Completed"
    ).select_related("payment", "payment__method")

    total_earnings = 0

    for b in completed_bookings:

        if hasattr(b, "payment") and b.payment:

            amount = float(b.payment.amount)

            platform_fee = amount * 0.16

            method_code = get_payment_method_code(b.payment)

            if method_code == "GCASH":
                transaction_fee = amount * 0.04
            else:
                transaction_fee = 0

            tutor_earned = amount - platform_fee - transaction_fee

            total_earnings += tutor_earned

    # 📌 Upcoming confirmed bookings
    upcoming = Booking.objects.filter(
        tutor=tutor,
        status__in=["Pending", "Confirmed", "Awaiting Payment Verification"],
        session_date__gte=timezone.now().date()
    ).select_related(
        "student",
        "tutor__profile__course",
        "availability"
    ).order_by("session_date", "availability__time_slot")

    # 🔥 GROUP BOOKINGS
    grouped_by_date = defaultdict(list)

    for b in upcoming:
        grouped_by_date[b.session_date].append(b)

    bookings_data = []

    for session_date, day_bookings in grouped_by_date.items():

        day_bookings.sort(key=lambda b: b.availability.time_slot)

        current_group = [day_bookings[0]]

        for booking in day_bookings[1:]:

            prev = current_group[-1]

            prev_end = (
                datetime.combine(session_date, prev.availability.time_slot)
                + timedelta(minutes=SESSION_SLOT_MINUTES)
            ).time()

            if booking.availability.time_slot == prev_end and booking.status == prev.status:
                current_group.append(booking)
            else:
                bookings_data.append(build_combined_block(current_group))
                current_group = [booking]

        bookings_data.append(build_combined_block(current_group))

    return Response({
        "total_sessions": tutor.total_sessions,
        "rating_average": tutor.rating_average,
        "hourly_rate": tutor.hourly_rate,
        "commission_terms_accepted_at": tutor.commission_terms_accepted_at,
        "total_earnings": round(total_earnings, 2),
        "session_load_limit": load_snapshot["session_load_limit"],
        "accepted_session_load": load_snapshot["accepted_session_load"],
        "session_load_remaining": load_snapshot["session_load_remaining"],
        "upcoming_bookings": bookings_data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_tutor_profile(request):

    profile = request.user.userprofile

    try:
        tutor = Tutor.objects.select_related(
            'profile__user',
            'profile__course',
            'pinned_review__student'
        ).get(profile=profile)
    except Tutor.DoesNotExist:
        return Response({"error": "Tutor not found"}, status=404)

    serializer = TutorProfileSerializer(tutor, context={'request': request})
    return Response(serializer.data)

#Tutor Detail View
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def tutor_detail(request, profile_id):
    try:
        tutor = Tutor.objects.select_related(
            'profile',
            'pinned_review__student'
        ).prefetch_related(
            'tutorsubjects_set__subject'
        ).get(profile_id=profile_id)
    except Tutor.DoesNotExist:
        return Response({"error": "Tutor not found"}, status=404)

    serializer = TutorDetailSerializer(tutor, context={'request': request})
    return Response(serializer.data)

#tutor availability schedule thing  vview

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def tutor_availability(request, tutor_id):

    tutor = get_object_or_404(Tutor, profile_id=tutor_id)
    if not can_create_new_booking(tutor.profile):
        return Response(
            {
                'error': 'This tutor is not currently eligible to accept new bookings.',
                'code': 'tutor_booking_gate_closed',
            },
            status=403,
        )
    current_now = timezone.localtime(timezone.now())
    today = current_now.date()
    month_offset = int(request.GET.get("month_offset", 0))

    total_months = (today.year * 12) + (today.month - 1) + month_offset
    target_year = total_months // 12
    target_month = (total_months % 12) + 1

    month_start = date(target_year, target_month, 1)
    month_end = date(target_year, target_month, monthrange(target_year, target_month)[1])

    calendar_start = month_start - timedelta(days=month_start.weekday())
    calendar_end = month_end + timedelta(days=(6 - month_end.weekday()))

    availability = TutorAvailability.objects.filter(
        tutor=tutor,
        is_active=True
    )

    relevant_bookings = Booking.objects.filter(
        tutor=tutor,
        session_date__range=(calendar_start, calendar_end),
        status__in=ACTIVE_BOOKING_STATUSES
    )
    full_day_dates, slot_override_keys = get_override_maps(
        tutor,
        calendar_start,
        calendar_end
    )

    booked_map = {
        (booking.availability_id, booking.session_date)
        for booking in relevant_bookings
    }

    weekday_order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    display_weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    weeks = []
    current_week_start = calendar_start

    while current_week_start <= calendar_end:
        days = []

        for weekday_index, weekday_name in enumerate(display_weekdays):
            current_date = current_week_start + timedelta(days=weekday_index)
            is_past_day = current_date < today
            day_slots = []

            for slot in availability:
                slot_weekday_index = weekday_order.index(slot.day)

                if slot_weekday_index != weekday_index:
                    continue

                is_overridden = (
                    current_date in full_day_dates
                    or (slot.id, current_date) in slot_override_keys
                )
                is_booked = (slot.id, current_date) in booked_map

                # Check if the slot time has already passed today
                is_slot_past = is_past_day or (current_date == today and slot.time_slot < current_now.time())

                day_slots.append({
                    "id": slot.id,
                    "time_slot": slot.time_slot.strftime("%H:%M"),
                    "is_booked": is_booked or is_slot_past or is_overridden,
                    "is_overridden": is_overridden
                })

            day_slots.sort(key=lambda slot: slot["time_slot"])

            days.append({
                "name": weekday_name,
                "date": current_date.isoformat(),
                "in_month": month_start <= current_date <= month_end,
                "is_past": is_past_day,
                "is_blocked": current_date in full_day_dates,
                "has_available": any(not slot["is_booked"] for slot in day_slots),
                "slots": day_slots
            })

        week_end = current_week_start + timedelta(days=6)
        weeks.append({
            "week_start": current_week_start.isoformat(),
            "week_end": week_end.isoformat(),
            "label": f"{current_week_start.strftime('%m/%d/%Y')} - {week_end.strftime('%m/%d/%Y')}",
            "days": days
        })

        current_week_start += timedelta(days=7)

    return Response({
        "month_label": month_start.strftime("%B %Y"),
        "month_start": month_start.isoformat(),
        "month_end": month_end.isoformat(),
        "month_offset": month_offset,
        "weeks": weeks
    })


#bulk booking request


"""@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_booking(request):

    tutor_id = request.data.get("tutor_id")
    slots = request.data.get("slots")

    if not slots:
        return Response({"error": "No slots provided"}, status=400)

    try:
        tutor = Tutor.objects.get(profile_id=tutor_id)
    except Tutor.DoesNotExist:
        return Response({"error": "Tutor not found"}, status=404)

    student = request.user.userprofile

    with transaction.atomic():

        for slot_data in slots:
            availability = TutorAvailability.objects.select_for_update().get(
                id=slot_data["availability_id"],
                tutor=tutor
            )

            if availability.is_booked:
                raise Exception("Slot already booked")

            Booking.objects.create(
                student=student,
                tutor=tutor,
                availability=availability,
                session_date=slot_data["session_date"],
                session_mode=slot_data["session_mode"]
            )

            availability.is_booked = True
            availability.save()

    return Response({"message": "Booking successful"})"""

#Confirm payment View
# Confirm payment View
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def confirm_payment_and_book(request):

    user_profile = get_object_or_404(UserProfile, user=request.user)

    if user_profile.role == 'Tutee' and not can_create_new_booking(user_profile):
        return Response(
            {
                "error": "Please verify your enrollment before booking a new session.",
                "code": "verification_required",
            },
            status=403,
        )

    tutor_id = request.data.get("tutor_id")
    slots = request.data.get("slots")
    method_id = request.data.get("payment_method")
    subject_code = request.data.get("subject")
    preferred_location = request.data.get('preferred_location', '').strip()

    if isinstance(slots, str):
        try:
            slots = json.loads(slots)
        except json.JSONDecodeError:
            return Response({"error": "Invalid slots payload."}, status=400)

    if not slots:
        return Response({"error": "No slots selected"}, status=400)

    # Enforce that a booking request can only include slots from one date.
    requested_dates = {
        parse_request_date(slot.get("session_date"))
        for slot in slots
    }

    if None in requested_dates:
        return Response({"error": "Invalid session date format."}, status=400)

    if len(requested_dates) > 1:
        return Response(
            {"error": "You can only book multiple sessions on the same day."},
            status=400
        )

    # Determine session mode from first slot
    first_slot_mode = slots[0].get('session_mode', '')
    is_f2f = first_slot_mode in ['F2F', 'Face-to-face']
    if is_f2f and not preferred_location:
        return Response({"error": "Preferred location is required for Face-to-face sessions."}, status=400)

    if method_id:
        try:
            method = PaymentMethod.objects.get(method_id=method_id, is_active=True)
        except PaymentMethod.DoesNotExist:
            return Response({"error": "Invalid payment method."}, status=400)

        receipt_image = request.FILES.get('receipt_image')
        transaction_reference = request.data.get('transaction_reference')
        required_method_code = 'CASH' if is_f2f else 'PAYMONGO'

        if method.code != required_method_code:
            return Response({"error": "Payment method does not match this session's mode."}, status=400)

        if method.code == 'PAYMONGO' and receipt_image is None:
            return Response({"error": "Receipt image is required for online payments."}, status=400)

        if method.code == 'PAYMONGO' and not str(transaction_reference or '').strip():
            return Response({"error": "Transaction reference is required for online payments."}, status=400)

        if method.code == 'CASH' and receipt_image is None:
            return Response({"error": "Receipt image is required for cash payments."}, status=400)

    tutor = get_object_or_404(Tutor, profile_id=tutor_id)
    subject = None
    if subject_code:
        if not subject_is_recognized_for_profile(user_profile, subject_code):
            return Response(
                {"error": SUBJECT_NOT_RECOGNIZED_ERROR},
                status=400,
            )
        subject = Subjects.objects.filter(subject_code=subject_code).first()
    normalized_slots = []

    with transaction.atomic():
        wallet, _ = Wallet.objects.get_or_create(tutor=tutor)
        if wallet.balance < 0:
            return Response(
                {'error': 'This tutor cannot accept bookings while their wallet balance is negative.'},
                status=409,
            )

        load_snapshot = get_tutor_acceptance_load_snapshot(tutor)
        if load_snapshot['accepted_session_load'] >= load_snapshot['session_load_limit']:
            return Response(
                {
                    'error': 'This tutor has reached their accepted session limit.',
                    'code': 'session_load_limit_reached',
                    **load_snapshot,
                },
                status=409,
            )

        for slot in slots:
            availability = get_object_or_404(
                TutorAvailability.objects.select_for_update(),
                id=slot["availability_id"],
                tutor=tutor
            )

            session_date = parse_request_date(slot.get("session_date"))

            if session_date is None:
                return Response(
                    {"error": "Invalid session date format."},
                    status=400
                )

            # 🚫 Prevent booking past dates/times
            current_now = timezone.localtime(timezone.now())
            if session_date > current_now.date() + timedelta(days=BOOKING_HORIZON_DAYS):
                return Response(
                    {'error': f'Sessions can only be booked up to {BOOKING_HORIZON_DAYS} days ahead.'},
                    status=400,
                )
            if session_date < current_now.date():
                return Response(
                    {"error": "Cannot book a past date."},
                    status=400
                )
            if session_date == current_now.date() and availability.time_slot < current_now.time():
                return Response(
                    {"error": "Cannot book a past time slot."},
                    status=400
                )

            # 🚫 Ensure weekday matches availability template
            if WEEKDAY_MAP[session_date.weekday()] != availability.day:
                return Response(
                    {"error": "Selected date does not match availability day."},
                    status=400
                )

            if slot_is_overridden(tutor, session_date, availability):
                return Response(
                    {"error": "This slot is unavailable on that date."},
                    status=400
                )

            # 🚫 Check conflict
            conflict_exists = Booking.objects.filter(
                availability=availability,
                session_date=session_date,
                status__in=ACTIVE_BOOKING_STATUSES
            ).exists()

            if conflict_exists:
                return Response(
                    {"error": "This slot is already booked for that date."},
                status=400
            )

            # 🧹 Cleanup cancelled booking
            Booking.objects.filter(
                availability=availability,
                session_date=session_date,
                status="Cancelled"
            ).delete()

            normalized_slots.append({
                "availability": availability,
                "session_date": session_date,
                "session_mode": "F2F" if slot["session_mode"] in ["F2F", "Face-to-face"] else "Online",
            })

        normalized_slots.sort(
            key=lambda normalized: (
                normalized["session_date"],
                normalized["availability"].time_slot
            )
        )

        created_bookings = []

        booking_request_id = uuid4()
        request_bookings = []

        for slot_group in group_slot_requests(normalized_slots):
            session_group_id = uuid4()
            session_mode = slot_group[0]['session_mode']
            meeting_link = (
                f'https://meet.jit.si/studybuddy-{uuid4().hex}'
                if session_mode == 'Online'
                else ''
            )
            session_start = timezone.make_aware(
                datetime.combine(slot_group[0]['session_date'], slot_group[0]['availability'].time_slot),
                timezone.get_current_timezone(),
            )
            is_born_late = current_now >= session_start - timedelta(hours=GRACE_CUTOFF_HOURS)

            for slot_request in slot_group:
                booking = Booking.objects.create(
                    student=user_profile,
                    tutor=tutor,
                    availability=slot_request["availability"],
                    subject=subject,
                    session_date=slot_request["session_date"],
                    session_mode=slot_request["session_mode"],
                    preferred_location=preferred_location,
                    session_group_id=session_group_id,
                    booking_request_id=booking_request_id,
                    status='Confirmed',
                    meeting_link=meeting_link,
                    is_born_late=is_born_late,
                )
                created_bookings.append(booking.id)
                request_bookings.append(booking)

        representative_booking = get_representative_booking(request_bookings)
        session_start = timezone.make_aware(
            datetime.combine(
                representative_booking.session_date,
                representative_booking.availability.time_slot,
            ),
            timezone.get_current_timezone(),
        )
        cancellation_deadline = session_start - timedelta(hours=GRACE_CUTOFF_HOURS)
        deadline_copy = timezone.localtime(cancellation_deadline).strftime('%b %d, %Y %I:%M %p')
        for recipient in (tutor.profile, user_profile):
            create_booking_status_notification(
                recipient,
                'confirmed',
                request_bookings,
                cancellation_deadline=deadline_copy,
                is_born_late=representative_booking.is_born_late,
            )
        room = get_canonical_room_for_booking(representative_booking)
        from studybuddy.chat.models import Message
        Message.objects.create(
            room=room,
            sender=None,
            content='This chat was opened automatically when the booking was confirmed.',
        )
        transaction.on_commit(
            lambda booking=representative_booking: mailer.enqueue_booking_confirmed(
                booking.tutor.profile.user,
                booking,
            )
        )

    if request_bookings:
        create_booking_event(
            request_bookings[0],
            request.user,
            'Booking confirmed instantly.',
            'booking_confirmed'
        )

    return Response({
        'message': 'Booking confirmed instantly.',
        'booking_ids': created_bookings,
        'meeting_link': request_bookings[0].meeting_link if request_bookings else '',
        'preferred_location': preferred_location,
        'is_born_late': request_bookings[0].is_born_late if request_bookings else False,
        'cancellation_deadline': cancellation_deadline.isoformat() if request_bookings else None,
    })

# ==========================================
# TEMPLATE AVAILABILITY (Weekly Template)
# ==========================================

@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def template_availability(request, pk=None):

    profile = request.user.userprofile

    try:
        tutor = Tutor.objects.get(profile=profile)
    except Tutor.DoesNotExist:
        return Response({"error": "Tutor not found"}, status=404)

    # =========================
    # GET ALL SLOTS
    # =========================
    if request.method == 'GET':
        slots = TutorAvailability.objects.filter(tutor=tutor)

        data = [
            {
                "availability_id": slot.id,
                "day": slot.day,
                "day_display": slot.get_day_display(),
                "time_slot": slot.time_slot.strftime("%H:%M"),
                "is_active": slot.is_active,
                "is_booked": slot.is_booked
            }
            for slot in slots
        ]

        return Response(data)

    # =========================
    # CREATE SLOT
    # =========================
    if request.method == 'POST':

        day = request.data.get("day")
        time_str = request.data.get("time_slot")

        try:
            time_obj = datetime.strptime(time_str, "%H:%M").time()
        except Exception:
            return Response({"error": "Invalid time format"}, status=400)

        slot = TutorAvailability.objects.create(
            tutor=tutor,
            day=day,
            time_slot=time_obj,
            is_active=True,
            is_booked=False
        )

        return Response({
            "availability_id": slot.id,
            "day": slot.day,
            "day_display": slot.get_day_display(),
            "time_slot": slot.time_slot.strftime("%H:%M"),
            "is_active": slot.is_active,
            "is_booked": slot.is_booked
        }, status=201)

    # =========================
    # DELETE SLOT
    # =========================
    if request.method == 'DELETE':

        if pk is None:
            return Response({"error": "Slot ID required"}, status=400)

        slot = get_object_or_404(TutorAvailability, id=pk, tutor=tutor)
        slot.delete()

        return Response({"message": "Deleted successfully"})


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def availability_overrides(request):

    profile = request.user.userprofile

    try:
        tutor = Tutor.objects.get(profile=profile)
    except Tutor.DoesNotExist:
        return Response({"error": "Tutor not found"}, status=404)

    if request.method == 'GET':
        start_date = parse_request_date(request.GET.get('start'))
        end_date = parse_request_date(request.GET.get('end'))

        if start_date is None or end_date is None:
            today = date.today()
            start_date = today.replace(day=1)
            end_date = date(today.year, today.month, monthrange(today.year, today.month)[1])

        overrides = TutorAvailabilityOverride.objects.filter(
            tutor=tutor,
            override_date__range=(start_date, end_date)
        ).select_related('availability').order_by('override_date', 'availability__time_slot')

        serializer = TutorAvailabilityOverrideSerializer(overrides, many=True)
        return Response(serializer.data)

    override_date = parse_request_date(request.data.get('override_date'))

    if override_date is None:
        return Response({"error": "Valid override_date is required."}, status=400)

    if override_date < date.today():
        return Response({"error": "Cannot create overrides for past dates."}, status=400)

    raw_is_full_day = request.data.get('is_full_day', False)
    is_full_day = raw_is_full_day if isinstance(raw_is_full_day, bool) else str(raw_is_full_day).lower() == 'true'

    if is_full_day:
        if has_confirmed_or_completed_booking_conflict(tutor, override_date):
            return Response(
                {"error": "Cannot block a date with confirmed or completed bookings."},
                status=400
            )

        if TutorAvailabilityOverride.objects.filter(
            tutor=tutor,
            override_date=override_date,
            is_full_day=True
        ).exists():
            return Response({"error": "This date is already blocked."}, status=400)

        override = TutorAvailabilityOverride.objects.create(
            tutor=tutor,
            override_date=override_date,
            is_full_day=True
        )

        serializer = TutorAvailabilityOverrideSerializer(override)
        return Response(serializer.data, status=201)

    if TutorAvailabilityOverride.objects.filter(
        tutor=tutor,
        override_date=override_date,
        is_full_day=True
    ).exists():
        return Response({"error": "This date is already fully blocked."}, status=400)

    slot_ids = request.data.get('availability_ids') or []
    single_slot_id = request.data.get('availability_id')

    if single_slot_id is not None:
        slot_ids = [single_slot_id]

    if not slot_ids:
        return Response({"error": "At least one availability_id is required."}, status=400)

    try:
        slot_ids = [int(slot_id) for slot_id in slot_ids]
    except (TypeError, ValueError):
        return Response({"error": "availability_ids must be numeric."}, status=400)

    availabilities = list(
        TutorAvailability.objects.filter(
            tutor=tutor,
            id__in=slot_ids
        ).order_by('time_slot')
    )

    if len(availabilities) != len(set(slot_ids)):
        return Response({"error": "One or more selected slots do not exist."}, status=400)

    created_overrides = []

    with transaction.atomic():
        for availability in availabilities:
            if availability.day != WEEKDAY_MAP[override_date.weekday()]:
                return Response(
                    {"error": "Selected slot does not match the chosen date."},
                    status=400
                )

            if has_confirmed_or_completed_booking_conflict(tutor, override_date, availability=availability):
                return Response(
                    {"error": "Cannot block a slot with confirmed or completed bookings."},
                    status=400
                )

            if TutorAvailabilityOverride.objects.filter(
                tutor=tutor,
                override_date=override_date,
                availability=availability,
                is_full_day=False
            ).exists():
                return Response(
                    {"error": "One or more selected slots are already blocked for this date."},
                    status=400
                )

            created_overrides.append(
                TutorAvailabilityOverride.objects.create(
                    tutor=tutor,
                    override_date=override_date,
                    availability=availability,
                    is_full_day=False
                )
            )

    serializer = TutorAvailabilityOverrideSerializer(created_overrides, many=True)
    return Response(serializer.data, status=201)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_availability_override(request, override_id):

    profile = request.user.userprofile

    try:
        tutor = Tutor.objects.get(profile=profile)
    except Tutor.DoesNotExist:
        return Response({"error": "Tutor not found"}, status=404)

    override = get_object_or_404(
        TutorAvailabilityOverride,
        id=override_id,
        tutor=tutor
    )

    override.delete()
    return Response({"message": "Override removed successfully."})



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_booking(request, booking_id):

    profile = request.user.userprofile
    booking = get_object_or_404(
        Booking.objects.select_related(
            'student__course',
            'student__user',
            'tutor__profile__course',
            'tutor__profile__user',
            'availability'
        ),
        id=booking_id
    )

    # Either party may cancel.
    is_student = profile == booking.student
    is_tutor = profile == booking.tutor.profile
    if not (is_student or is_tutor):
        return Response({"error": "Unauthorized"}, status=403)

    actor_role = "tutee" if is_student else "tutor"

    # Reason is required.
    reason = str(request.data.get("reason", "")).strip()
    if len(reason) < 5:
        return Response(
            {"error": "Please provide a reason for cancelling (at least 5 characters)."},
            status=400
        )

    # Group lookup mirrors approve/reject.
    if booking.status == "Pending":
        session_group_bookings = get_booking_request_bookings(booking)
    else:
        session_group_bookings = get_session_group_bookings(booking)

    representative_booking = get_representative_booking(session_group_bookings)

    if not representative_booking:
        return Response({"error": "Booking not found."}, status=404)

    first_booking = session_group_bookings[0]
    last_booking = session_group_bookings[-1]
    start_time = first_booking.availability.time_slot
    end_time = (
        datetime.combine(first_booking.session_date, last_booking.availability.time_slot)
        + timedelta(minutes=SESSION_SLOT_MINUTES)
    ).time()

    raw_status = representative_booking.status
    display_status = get_display_status(
        raw_status,
        representative_booking.session_date,
        start_time,
        end_time
    )

    if display_status != 'Upcoming':
        return Response(
            {'error': 'Only upcoming sessions can be cancelled.'},
            status=400
        )

    session_start = timezone.make_aware(
        datetime.combine(first_booking.session_date, first_booking.availability.time_slot),
        timezone.get_current_timezone(),
    )
    is_late_cancellation = timezone.localtime(timezone.now()) >= (
        session_start - timedelta(hours=GRACE_CUTOFF_HOURS)
    )

    with transaction.atomic():
        Booking.objects.filter(id__in=[group_booking.id for group_booking in session_group_bookings]).update(
            status="Cancelled",
            tutee_confirmed=False,
            tutor_confirmed=False,
            cancellation_reason=reason,
            cancelled_by_role=actor_role,
        )

        if is_late_cancellation:
            aggrieved_party = representative_booking.tutor.profile if is_student else representative_booking.student
            SupportTicket.objects.create(
                user=aggrieved_party,
                booking=representative_booking,
                category='Late_Cancellation',
                subject='Late Cancellation review',
                description=(
                    f'A {actor_role} cancelled this session after the Grace Cutoff. '
                    f'Reason: {reason}'
                ),
                reported_by_system=True,
                penalized_user=profile,
            )

        create_booking_status_notification(
            representative_booking.tutor.profile,
            "cancelled",
            session_group_bookings,
            recipient_role="tutor",
            actor_role=actor_role,
            reason=reason,
        )
        create_booking_status_notification(
            representative_booking.student,
            "cancelled",
            session_group_bookings,
            recipient_role="tutee",
            actor_role=actor_role,
            reason=reason,
        )

    # Timeline event is best-effort: the cancellation itself must never fail
    # because logging the chat event did.
    representative_booking.refresh_from_db()
    try:
        create_booking_event(
            representative_booking,
            request.user,
            f"Session cancelled by {actor_role}. Reason: {reason}",
            "booking_cancelled",
        )
    except Exception:
        logger.exception(
            "Cancellation succeeded but recording the booking event failed for booking %s",
            representative_booking.id,
        )

    return Response({"message": "Session cancelled successfully."}, status=200)




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_bookings(request):

    profile = request.user.userprofile

    if profile.role == "Tutor":
        bookings = Booking.objects.filter(
            tutor__profile=profile
        ).select_related('student', 'availability', 'tutor__profile__course', 'rating')
    else:
        bookings = Booking.objects.filter(
            student=profile
        ).select_related('student', 'availability', 'tutor__profile__course', 'rating')

    bookings = bookings.order_by("session_date", "availability__time_slot")

    grouped_bookings = defaultdict(list)

    for booking in bookings:
        booking_date_key = booking.session_date.isoformat()

        if booking.status == "Pending" and booking.booking_request_id:
            group_key = f"request-{booking_date_key}-{booking.booking_request_id}"
        else:
            group_key = (
                f"group-{booking_date_key}-{booking.session_group_id}"
                if booking.session_group_id
                else f"booking-{booking.id}"
            )
        grouped_bookings[group_key].append(booking)

    final_data = []

    for group in grouped_bookings.values():
        representative_booking = get_representative_booking(group)

        if representative_booking and representative_booking.status == "Pending" and representative_booking.booking_request_id:
            final_data.append(build_booking_request_block(group, profile))
        else:
            final_data.append(build_combined_block(group, profile))

    final_data.sort(key=lambda booking: (booking["date"], booking["startTime"]))

    return Response(final_data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def dismiss_dashboard_pill(request, booking_id):
    profile = request.user.userprofile
    booking = get_object_or_404(
        Booking.objects.select_related(
            'student',
            'tutor__profile',
            'availability',
        ),
        id=booking_id,
    )

    is_student = profile == booking.student
    is_tutor = profile == booking.tutor.profile

    if not (is_student or is_tutor):
        return Response({"error": "Unauthorized"}, status=403)

    if booking.status not in ("Rejected", "Cancelled"):
        return Response(
            {"error": "Only rejected or cancelled schedule pills can be removed."},
            status=400,
        )

    session_group_bookings = get_dashboard_pill_bookings(booking)

    if not session_group_bookings:
        return Response({"error": "Booking not found."}, status=404)

    hidden_field = "dashboard_hidden_by_student_at" if is_student else "dashboard_hidden_by_tutor_at"
    Booking.objects.filter(
        id__in=[group_booking.id for group_booking in session_group_bookings]
    ).update(**{hidden_field: timezone.now()})

    return Response({
        "message": "Schedule pill removed from dashboard.",
        "hidden_booking_ids": [group_booking.id for group_booking in session_group_bookings],
    })


def build_booking_detail_payload(session_group_bookings, request=None):
    representative_booking = get_representative_booking(session_group_bookings)
    first_booking = session_group_bookings[0]
    last_booking = session_group_bookings[-1]

    start_time = first_booking.availability.time_slot
    end_time = (
        datetime.combine(first_booking.session_date, last_booking.availability.time_slot)
        + timedelta(minutes=SESSION_SLOT_MINUTES)
    ).time()
    has_dev_live_override = get_dev_live_override_for_bookings(session_group_bookings) is not None
    session_date, start_time, end_time = apply_dev_live_override(
        session_group_bookings,
        representative_booking.session_date,
        start_time,
        end_time,
    )
    display_status = get_display_status(
        representative_booking.status,
        session_date,
        start_time,
        end_time
    )

    if (
        settings.BOOKING_DEV_TOOLS_ENABLED
        and not has_dev_live_override
        and representative_booking.status == "Confirmed"
        and representative_booking.tutor_confirmed
    ):
        display_status = "Payment Required"

    return {
        "id": representative_booking.id,
        "session_group_id": str(representative_booking.session_group_id) if representative_booking.session_group_id else None,
        "tutee_confirmed": representative_booking.tutee_confirmed,
        "tutor_confirmed": representative_booking.tutor_confirmed,
        "rating_submitted": hasattr(representative_booking, "rating"),
        "tutee": {
            "name": f"{representative_booking.student.fname} {representative_booking.student.lname}",
            "email": representative_booking.student.user.email,
            "course": representative_booking.student.course.course_name if representative_booking.student.course else None,
            "year_level": representative_booking.student.year_level,
            "bio": representative_booking.student.bio,
            "avatar": build_absolute_media_url(request, representative_booking.student.profile_picture),
        },
        "tutor": {
            "name": f"{representative_booking.tutor.profile.fname} {representative_booking.tutor.profile.lname}",
            "email": representative_booking.tutor.profile.user.email,
            "course": representative_booking.tutor.profile.course.course_name if representative_booking.tutor.profile.course else None,
            "year_level": representative_booking.tutor.profile.year_level,
            "bio": representative_booking.tutor.profile.bio,
            "avatar": build_absolute_media_url(request, representative_booking.tutor.profile.profile_picture),
            "rating": representative_booking.tutor.rating_average,
            "hourly_rate": float(representative_booking.tutor.hourly_rate or 0),
            "subjects_taught": list(
                representative_booking.tutor.tutorsubjects_set.select_related('subject').values_list(
                    'subject__subject_name',
                    flat=True
                )
            ),
        },
        "session": {
            "subject": booking_subject_label(representative_booking),
            "date": session_date.strftime("%Y-%m-%d"),
            "start_time": start_time.strftime("%H:%M"),
            "end_time": end_time.strftime("%H:%M"),
            "duration_hours": get_duration_hours_for_bookings(session_group_bookings),
            "rating": representative_booking.rating.rating_score if hasattr(representative_booking, "rating") else None,
            "status": display_status,
            "raw_status": representative_booking.status,
            "session_mode": representative_booking.session_mode,
            "preferred_location": representative_booking.preferred_location,
        },
        "payment": serialize_payment_summary(representative_booking, request=request),
        "check_ins": serialize_session_check_ins(representative_booking),
    }


#Booking Detail View (for tutor to see details of a specific booking, including payment info)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def booking_detail(request, booking_id):

    booking = get_object_or_404(
        Booking.objects.select_related(
            'student__course',
            'student__user',
            'tutor__profile__course',
            'tutor__profile__user',
            'payment__method',
            'availability'
        ),
        id=booking_id
    )

    if request.user.userprofile not in (booking.tutor.profile, booking.student):
        return Response({"error": "Unauthorized"}, status=403)

    session_group_bookings = get_booking_request_bookings(booking)
    return Response(build_booking_detail_payload(session_group_bookings, request=request))


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def confirm_session_venue(request, booking_id):
    booking, error_response = get_tutee_owned_booking_or_403(request, booking_id)
    if error_response:
        return error_response

    if booking.session_mode != "F2F":
        return Response(
            {"error": "Venue confirmation is only available for face-to-face sessions."},
            status=400,
        )

    response_value = str(request.data.get("response", "")).strip().lower()
    valid_responses = {
        SessionCheckIn.RESPONSE_VENUE_YES,
        SessionCheckIn.RESPONSE_VENUE_NO,
    }

    if response_value not in valid_responses:
        return Response({"error": "Response must be 'yes' or 'no'."}, status=400)

    check_in, created = create_session_check_in_response(
        booking,
        SessionCheckIn.EVENT_VENUE_CONFIRM,
        response_value,
    )

    return Response(
        {
            "id": check_in.id,
            "event_type": check_in.event_type,
            "response": check_in.response,
            "responded_at": check_in.responded_at.isoformat(),
            "created": created,
        },
        status=201 if created else 200,
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def record_midpoint_check_in(request, booking_id):
    booking, error_response = get_tutee_owned_booking_or_403(request, booking_id)
    if error_response:
        return error_response

    if get_current_display_status_for_booking(booking).lower() != 'ongoing':
        return Response(
            {"error": "Mid-session check-ins are only available while the session is ongoing."},
            status=409,
        )

    response_value = str(request.data.get("response", "")).strip().lower()
    valid_responses = {
        SessionCheckIn.RESPONSE_MIDPOINT_GOOD,
        SessionCheckIn.RESPONSE_MIDPOINT_ISSUES,
    }

    if response_value not in valid_responses:
        return Response({"error": "Response must be 'good' or 'issues'."}, status=400)

    check_in, created = create_session_check_in_response(
        booking,
        SessionCheckIn.EVENT_MIDPOINT_CHECKIN,
        response_value,
    )

    return Response(
        {
            "id": check_in.id,
            "event_type": check_in.event_type,
            "response": check_in.response,
            "responded_at": check_in.responded_at.isoformat(),
            "created": created,
        },
        status=201 if created else 200,
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_session_payment(request, booking_id):

    profile = request.user.userprofile
    booking = get_object_or_404(
        Booking.objects.select_related('availability', 'tutor', 'tutor__profile'),
        id=booking_id
    )

    if profile != booking.student:
        return Response({"error": "Unauthorized"}, status=403)

    session_group_bookings = get_booking_request_bookings(booking)

    if any(group_booking.status != "Confirmed" for group_booking in session_group_bookings):
        return Response({"error": "All session slots must be confirmed before payment submission."}, status=400)

    representative_booking = get_representative_booking(session_group_bookings)

    if hasattr(representative_booking, 'payment'):
        return Response({"error": "Payment has already been submitted for this session."}, status=400)

    method_id = request.data.get("payment_method")

    if not method_id:
        return Response({"error": "Payment method required."}, status=400)

    try:
        method = PaymentMethod.objects.get(method_id=method_id, is_active=True)
    except PaymentMethod.DoesNotExist:
        return Response({"error": "Invalid payment method."}, status=400)

    receipt_image = request.FILES.get('receipt_image')
    transaction_reference = request.data.get('transaction_reference')
    required_method_code = 'CASH' if representative_booking.session_mode == 'F2F' else 'PAYMONGO'

    if method.code != required_method_code:
        return Response({"error": "Payment method does not match this session's mode."}, status=400)

    if method.code == 'PAYMONGO' and receipt_image is None:
        return Response({"error": "Receipt image is required for online payments."}, status=400)

    if method.code == 'PAYMONGO' and not str(transaction_reference or '').strip():
        return Response({"error": "Transaction reference is required for online payments."}, status=400)

    if method.code == 'CASH' and receipt_image is None:
        return Response({"error": "Receipt image is required for cash payments."}, status=400)

    if receipt_image is not None:
        receipt_image = compress_if_image(receipt_image)

    duration_hours = get_duration_hours_for_bookings(session_group_bookings)
    amount = round(float(representative_booking.tutor.hourly_rate or 0) * duration_hours, 2)

    with transaction.atomic():
        Payment.objects.create(
            booking=representative_booking,
            amount=amount,
            method=method,
            transaction_reference=str(transaction_reference or '').strip() or None,
            receipt_image=receipt_image,
            payment_status="Pending",
            paid_at=now()
        )

        Booking.objects.filter(id__in=[group_booking.id for group_booking in session_group_bookings]).update(
            tutee_confirmed=True,
            status="Awaiting Payment Verification"
        )

        create_booking_status_notification(
            representative_booking.tutor.profile,
            "awaiting_payment_verification",
            session_group_bookings
        )

    return Response({"message": "Payment submitted successfully."}, status=201)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def tutor_confirm_booking(request, booking_id):

    profile = request.user.userprofile
    booking = get_object_or_404(
        Booking.objects.select_related('tutor', 'tutor__profile', 'availability'),
        id=booking_id
    )

    if profile != booking.tutor.profile:
        return Response({"error": "Unauthorized"}, status=403)

    session_group_bookings = get_booking_request_bookings(booking)

    if any(group_booking.status != "Awaiting Payment Verification" for group_booking in session_group_bookings):
        return Response({"error": "This session is not awaiting payment verification."}, status=400)

    representative_booking = get_representative_booking(session_group_bookings)
    payment = getattr(representative_booking, 'payment', None)

    if not payment:
        return Response({"error": "Payment has not been submitted for this session."}, status=400)

    already_counted = all(group_booking.tutor_confirmed for group_booking in session_group_bookings)

    with transaction.atomic():
        Booking.objects.filter(id__in=[group_booking.id for group_booking in session_group_bookings]).update(
            tutor_confirmed=True,
            status="Completed"
        )

        if payment.payment_status != "Paid":
            payment.payment_status = "Paid"
            payment.save(update_fields=['payment_status'])

        if not already_counted:
            tutor = representative_booking.tutor
            tutor.total_sessions += 1
            tutor.save(update_fields=['total_sessions'])

        create_booking_status_notification(
            representative_booking.student,
            "completed",
            session_group_bookings
        )

        # Credit the tutor's wallet if payment was online
        credit_tutor_wallet(representative_booking)

        PlatformActivity.objects.create(
            activity_type='booking_completed',
            message=f"Session completed: {representative_booking.student.fname} with {representative_booking.tutor.profile.fname}",
            institution=representative_booking.tutor.profile.institution
        )

    return Response({"message": "Session marked as completed successfully."})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_booking(request, booking_id):
    return tutor_confirm_booking(request, booking_id)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def dev_force_booking_live(request, booking_id):
    if not settings.BOOKING_DEV_TOOLS_ENABLED:
        return Response(status=404)

    profile = request.user.userprofile
    booking = get_object_or_404(
        Booking.objects.select_related('student', 'tutor__profile', 'availability'),
        id=booking_id,
    )

    if profile not in (booking.student, booking.tutor.profile):
        return Response({"error": "Unauthorized"}, status=403)

    session_group_bookings = get_session_group_bookings(booking)

    if any(group_booking.status != "Confirmed" for group_booking in session_group_bookings):
        return Response(
            {"error": "Only confirmed sessions can be forced live."},
            status=400,
        )

    phase = str(request.data.get("phase", "start")).strip().lower()
    if phase not in DEV_LIVE_PHASES:
        return Response(
            {"error": "Phase must be 'upcoming', 'start', 'midpoint', 'ending', or 'handoff'."},
            status=400,
        )

    set_dev_live_override_for_bookings(
        session_group_bookings,
        build_dev_live_override(phase),
    )
    refreshed_group = get_session_group_bookings(booking)

    return Response(build_booking_detail_payload(refreshed_group))


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def dev_clear_booking_live(request, booking_id):
    if not settings.BOOKING_DEV_TOOLS_ENABLED:
        return Response(status=404)

    profile = request.user.userprofile
    booking = get_object_or_404(
        Booking.objects.select_related('student', 'tutor__profile', 'availability'),
        id=booking_id,
    )

    if profile not in (booking.student, booking.tutor.profile):
        return Response({"error": "Unauthorized"}, status=403)

    session_group_bookings = get_session_group_bookings(booking)
    clear_dev_live_override_for_bookings(session_group_bookings)
    refreshed_group = get_session_group_bookings(booking)

    return Response(build_booking_detail_payload(refreshed_group))


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def dev_mark_booking_ready_for_payment(request, booking_id):
    if not settings.BOOKING_DEV_TOOLS_ENABLED:
        return Response(status=404)

    profile = request.user.userprofile
    booking = get_object_or_404(
        Booking.objects.select_related('tutor', 'tutor__profile', 'availability'),
        id=booking_id
    )

    if profile != booking.tutor.profile:
        return Response({"error": "Unauthorized"}, status=403)

    session_group_bookings = get_booking_request_bookings(booking)

    if any(group_booking.status != "Confirmed" for group_booking in session_group_bookings):
        return Response(
            {"error": "Only confirmed sessions can be made ready for payment."},
            status=400
        )

    with transaction.atomic():
        Booking.objects.filter(
            id__in=[group_booking.id for group_booking in session_group_bookings]
        ).update(tutor_confirmed=True)

    refreshed_group = get_booking_request_bookings(booking)

    return Response(build_booking_detail_payload(refreshed_group))


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_session_rating(request, booking_id):

    profile = request.user.userprofile
    booking = get_object_or_404(
        Booking.objects.select_related('tutor', 'availability'),
        id=booking_id
    )

    if profile != booking.student:
        return Response({"error": "Unauthorized"}, status=403)

    session_group_bookings = get_booking_request_bookings(booking)

    if any(group_booking.status != "Completed" for group_booking in session_group_bookings):
        return Response({"error": "You can only rate completed sessions."}, status=400)

    representative_booking = get_representative_booking(session_group_bookings)

    if hasattr(representative_booking, 'rating'):
        return Response({"error": "Rating has already been submitted for this session."}, status=400)

    try:
        rating_score = int(request.data.get("rating_score"))
    except (TypeError, ValueError):
        return Response({"error": "A valid rating_score is required."}, status=400)

    if rating_score < 1 or rating_score > 5:
        return Response({"error": "rating_score must be between 1 and 5."}, status=400)

    Rating.objects.create(
        booking=representative_booking,
        student=profile,
        tutor=representative_booking.tutor,
        rating_score=rating_score,
        comment=request.data.get("comment", "")
    )
    update_tutor_rating_average(representative_booking.tutor)
    bump_dashboard_recs_cache_version()

    return Response({"message": "Rating submitted successfully."}, status=201)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_notifications(request):

    notifications = Notification.objects.filter(
        recipient=request.user.userprofile
    ).select_related('recipient').order_by('-created_at')

    serializer = NotificationSerializer(notifications, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_notification_read(request, notification_id):

    notification = get_object_or_404(Notification, id=notification_id)

    if notification.recipient != request.user.userprofile:
        return Response({"error": "Unauthorized"}, status=403)

    notification.is_read = True
    notification.save(update_fields=['is_read'])

    return Response({"message": "Notification marked as read."})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_preferences(request):

    profile = request.user.userprofile

    pref, created = Preference.objects.get_or_create(user=profile)

    pref.save()

    subject_ids = request.data.get("subjects", [])

    invalid_codes = invalid_new_subject_codes(profile, subject_ids)
    if invalid_codes:
        return Response(
            {
                "error": "Some subjects are no longer recognized for your course catalog.",
                "invalid_subjects": sorted(invalid_codes),
            },
            status=400,
        )

    if "subjects" in request.data:
        pref.subjects.set(subject_ids)

    cache.delete(dashboard_recs_cache_key(profile))

    return Response({
        "message": "Preferences saved successfully"
    })
@api_view(['POST'])
def tutor_setup(request):

    profile = request.user.userprofile
    tutor = Tutor.objects.get(profile=profile)

    # Reactive Gate: a tutor must acknowledge the commission disclosure before an hourly rate is
    # ever accepted, mirroring the "Continue" button's Proactive Gate in TutorPreferenceSetup.vue
    # (see ADR-0010). Already-accepted tutors keep re-submitting this on every profile edit, which
    # is fine — commission_terms_accepted_at only needs to be set once.
    if not tutor.commission_terms_accepted_at and not request.data.get("commission_terms_accepted"):
        return Response(
            {"error": "Please acknowledge the platform commission before continuing."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    tutor.teaching_level = request.data.get("teaching_level")

    tutor.can_online = request.data.get("can_online", True)
    tutor.can_f2f = request.data.get("can_f2f", False)

    tutor.hourly_rate = request.data.get("hourly_rate")
    tutor.response_time = request.data.get("response_time", tutor.response_time)

    if not tutor.commission_terms_accepted_at:
        tutor.commission_terms_accepted_at = timezone.now()

    tutor.save()
    bump_dashboard_recs_cache_version()

    profile.profile_completed = True
    profile.save()

    return Response({"message": "Tutor profile updated"})


@api_view(['POST'])
def accept_commission_terms(request):
    """Retroactive commission-disclosure acceptance for tutors who completed onboarding before
    this gate existed (see ADR-0010). Separate from tutor_setup's inline acceptance so an
    already-onboarded tutor isn't forced to resubmit their full profile just to acknowledge the
    commission rate."""

    profile = request.user.userprofile
    tutor = Tutor.objects.get(profile=profile)

    if not tutor.commission_terms_accepted_at:
        tutor.commission_terms_accepted_at = timezone.now()
        tutor.save(update_fields=['commission_terms_accepted_at'])

    return Response({"commission_terms_accepted_at": tutor.commission_terms_accepted_at})


# Which filter actually produced a result set. The client cannot infer this from the tutor list, and
# without it the results header claims date availability that was never checked.
MATCH_STAGE_EXACT = 'exact'
MATCH_STAGE_DATE_ONLY = 'date_only'
MATCH_STAGE_SUBJECT_ONLY = 'subject_only'

# Mon-first, matching how tutors read their own weekly schedule. Alphabetical order would be
# meaningless to a tutee reading "usually teaches" chips.
WEEKDAY_ORDER = [WEEKDAY_MAP[index] for index in sorted(WEEKDAY_MAP)]


def parse_recommendation_time(time_string):
    if not time_string:
        return None

    for time_format in ("%H:%M", "%H:%M:%S"):
        try:
            return datetime.strptime(str(time_string), time_format).time()
        except ValueError:
            continue

    return None


def get_recommendation_time_slots(start_time_string, end_time_string):
    start_time = parse_recommendation_time(start_time_string)
    end_time = parse_recommendation_time(end_time_string)

    if not start_time or not end_time or end_time <= start_time:
        return None

    current = datetime.combine(date.today(), start_time)
    end_at = datetime.combine(date.today(), end_time)
    slots = []

    while current < end_at:
        slots.append(current.time())
        current += timedelta(minutes=SESSION_SLOT_MINUTES)

    return slots


def get_available_slot_times_by_tutor(tutor_ids, session_date):
    """Map tutor_id -> set of time slots still bookable on session_date.

    A slot drops out if it is booked, blocked by a full-day or single-slot override, or already in
    the past. That is the same rule tutor_availability_calendar applies per day, so search and the
    tutor's own calendar cannot disagree about whether a day has anything left. Tutors with nothing
    left are simply absent from the returned map.

    Bulk by design: the candidate loop above already runs per-tutor queries, so this must not add
    another N+1 on top.
    """
    if not tutor_ids:
        return {}

    weekday = WEEKDAY_MAP[session_date.weekday()]
    current_now = timezone.localtime(timezone.now())

    slots = list(
        TutorAvailability.objects.filter(
            tutor_id__in=tutor_ids,
            day=weekday,
            is_active=True,
        ).values_list('tutor_id', 'id', 'time_slot')
    )

    if not slots:
        return {}

    slot_ids = [slot_id for _, slot_id, _ in slots]

    booked_slot_ids = set(
        Booking.objects.filter(
            availability_id__in=slot_ids,
            session_date=session_date,
            status__in=ACTIVE_BOOKING_STATUSES,
        ).values_list('availability_id', flat=True)
    )

    overrides = TutorAvailabilityOverride.objects.filter(
        tutor_id__in=tutor_ids,
        override_date=session_date,
    ).values_list('tutor_id', 'availability_id', 'is_full_day')

    blocked_all_day = {tutor_id for tutor_id, _, is_full_day in overrides if is_full_day}
    blocked_slot_ids = {
        availability_id
        for _, availability_id, is_full_day in overrides
        if not is_full_day and availability_id is not None
    }

    available = {}

    for tutor_id, slot_id, time_slot in slots:
        if tutor_id in blocked_all_day:
            continue

        if slot_id in booked_slot_ids or slot_id in blocked_slot_ids:
            continue

        if session_date == current_now.date() and time_slot < current_now.time():
            continue

        available.setdefault(tutor_id, set()).add(time_slot)

    return available


def get_recommendation_candidate_tutors(
    subject,
    preferred_mode=None,
    min_budget=None,
    max_budget=None,
    requested_date=None,
    start_time=None,
    end_time=None,
):
    base_candidates = Tutor.objects.filter(
        tutorsubjects__subject__subject_code=subject,
        profile__tutor_application__application_status='approved',
    )
    eligible_candidate_ids = []
    for candidate in base_candidates.distinct():
        wallet, _ = Wallet.objects.get_or_create(tutor=candidate)
        load_snapshot = get_tutor_acceptance_load_snapshot(candidate)
        if (
            wallet.balance >= 0
            and load_snapshot['accepted_session_load'] < load_snapshot['session_load_limit']
            and not has_reached_monthly_strike_cap(candidate.profile)
        ):
            eligible_candidate_ids.append(candidate.profile_id)
    base_candidates = base_candidates.filter(profile_id__in=eligible_candidate_ids)

    if preferred_mode == "Online":
        base_candidates = base_candidates.filter(can_online=True)
    elif preferred_mode in ["Face-to-face", "F2F"]:
        base_candidates = base_candidates.filter(can_f2f=True)

    if min_budget not in [None, ""]:
        base_candidates = base_candidates.filter(hourly_rate__gte=min_budget)

    if max_budget not in [None, ""]:
        base_candidates = base_candidates.filter(hourly_rate__lte=max_budget)

    session_date = parse_request_date(requested_date)
    required_slots = get_recommendation_time_slots(start_time, end_time)

    if not session_date:
        return base_candidates.distinct(), MATCH_STAGE_SUBJECT_ONLY

    # One availability read for the whole candidate set, already accounting for bookings, both
    # override kinds, and past times. Tutors with nothing left on this date are absent from the map.
    candidate_ids = list(base_candidates.values_list('profile_id', flat=True).distinct())
    available_by_tutor = get_available_slot_times_by_tutor(candidate_ids, session_date)

    # Stage 1: every requested slot is free.
    if required_slots:
        required = set(required_slots)
        exact_ids = [
            tutor_id
            for tutor_id, available_times in available_by_tutor.items()
            if required <= available_times
        ]

        if exact_ids:
            return (
                base_candidates.filter(profile_id__in=exact_ids).distinct(),
                MATCH_STAGE_EXACT,
            )

    # Stage 2: something is free that day, just not the requested window.
    if available_by_tutor:
        return (
            base_candidates.filter(profile_id__in=list(available_by_tutor)).distinct(),
            MATCH_STAGE_DATE_ONLY,
        )

    # Stage 3: nothing on that date. The date is dropped entirely rather than used to exclude —
    # filtering by a date we just abandoned would be incoherent, and a tutor booked solid on the 9th
    # may be the best choice for the 10th. The caller surfaces this as a banner.
    return base_candidates.distinct(), MATCH_STAGE_SUBJECT_ONLY


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def recommend_tutors_view(request):

    student_profile = request.user.userprofile

    subject = request.data.get("subject")
    preferred_mode = request.data.get("preferred_mode")
    min_budget = request.data.get("min_budget")
    max_budget = request.data.get("max_budget")
    requested_date = request.data.get("date")
    start_time = request.data.get("start_time")
    end_time = request.data.get("end_time")

    if not subject:
        return Response(
            {"error": "Subject is required"},
            status=400
        )

    if not subject_is_recognized_for_profile(student_profile, subject):
        return Response(
            {"error": SUBJECT_NOT_RECOGNIZED_ERROR},
            status=400,
        )

    # A date is required. Without this an unreadable date parsed to None and was treated as "no date
    # given", which silently skipped both date stages and returned every tutor for the subject.
    session_date = parse_request_date(requested_date)

    if session_date is None:
        return Response(
            {"error": "A valid session date (YYYY-MM-DD) is required."},
            status=400,
        )

    today = timezone.localtime(timezone.now()).date()

    if session_date < today:
        return Response({"error": "Cannot search a past date."}, status=400)

    if session_date > today + timedelta(days=BOOKING_HORIZON_DAYS):
        return Response(
            {"error": f"Sessions can only be booked up to {BOOKING_HORIZON_DAYS} days ahead."},
            status=400,
        )

    ratings = build_rating_matrix()
    candidate_qs, match_stage = get_recommendation_candidate_tutors(
        subject,
        preferred_mode=preferred_mode,
        min_budget=min_budget,
        max_budget=max_budget,
        requested_date=requested_date,
        start_time=start_time,
        end_time=end_time,
    )

    results = recommend_tutors_hybrid(
        ratings,
        student_profile,
        subject,
        candidate_qs=candidate_qs,
    )

    logger.debug(
        "Recommendation request for subject %s scored %s candidate tutors",
        subject,
        len(results),
    )

    ranked = results[:10]

    # The recurring weekly pattern, used for the "usually teaches" chips on fallback results. One
    # query for the whole page rather than one per tutor.
    ranked_tutor_ids = [r["tutor"].profile_id for r in ranked]
    days_by_tutor = {}

    for tutor_id, day in TutorAvailability.objects.filter(
        tutor_id__in=ranked_tutor_ids,
        is_active=True,
    ).values_list('tutor_id', 'day').distinct():
        days_by_tutor.setdefault(tutor_id, set()).add(day)

    data = []

    for r in ranked:

        tutor = r["tutor"]
        score = r["score"]

        tutor_subjects = tutor.tutorsubjects_set.all()

        subjects = [
            ts.subject.subject_name
            for ts in tutor_subjects
        ]

        tutor_days = days_by_tutor.get(tutor.profile_id, set())

        data.append({
            "id": tutor.profile.id,
            "name": f"{tutor.profile.fname} {tutor.profile.lname}",
            "score": round(score, 3),
            "rating": tutor.rating_average,
            "hourly_rate": tutor.hourly_rate,
            "total_sessions": tutor.total_sessions,
            "available_days": [day for day in WEEKDAY_ORDER if day in tutor_days],
            "subjects": subjects
        })

    return Response({"match_stage": match_stage, "tutors": data}, status=200)

#Setup Profile
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def setup_profile(request):

    profile = request.user.userprofile

    course_code = request.data.get("course")

    if course_code:
        course = Course.objects.get(course_code=course_code)
        profile.course = course

    profile.year_level = request.data.get("year_level")
    profile.bio = request.data.get("bio")

    profile.profile_completed = True

    profile.save()

    return Response({
        "message": "Profile updated successfully"
    })

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_tutee_profile(request):

    profile = request.user.userprofile

    profile.fname = request.data.get("fname", profile.fname)
    profile.mname = request.data.get("mname", profile.mname)
    profile.lname = request.data.get("lname", profile.lname)

    if "course" in request.data:
        course_code = request.data.get("course")

        if course_code:
            try:
                course = Course.objects.get(course_code=course_code)
                profile.course = course
            except Course.DoesNotExist:
                return Response({"error": "Invalid course"}, status=400)
        else:
            profile.course = None

    profile.year_level = request.data.get("year_level", profile.year_level)
    profile.bio = request.data.get("bio", profile.bio)

    subject_ids = request.data.get("subjects", [])
    invalid_codes = invalid_new_subject_codes(profile, subject_ids, course_code=profile.course_id)
    if invalid_codes:
        return Response(
            {
                "error": "Some subjects are no longer recognized for your course catalog.",
                "invalid_subjects": sorted(invalid_codes),
            },
            status=400,
        )

    profile.save()

    # ⭐ Update preference subjects
    subject_ids = request.data.get("subjects", [])

    pref, created = Preference.objects.get_or_create(user=profile)

    if "subjects" in request.data:
        pref.subjects.set(subject_ids)

    pref.save()

    cache.delete(dashboard_recs_cache_key(profile))

    return Response({"message": "Profile updated successfully"})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_tutee_profile(request):

    profile = request.user.userprofile

    try:
        pref = Preference.objects.get(user=profile)
        subject_ids = list(pref.subjects.values_list("subject_code", flat=True))
    except Preference.DoesNotExist:
        subject_ids = []

    return Response({
        "fname": profile.fname,
        "mname": profile.mname,
        "lname": profile.lname,
        "email": profile.user.email,
        "course": profile.course.course_code if profile.course else None,
        "year_level": profile.year_level,
        "bio": profile.bio,
        "subjects": subject_ids,
        "profile_picture_url": request.build_absolute_uri(profile.profile_picture.url) if profile.profile_picture else None,
        "updated_at": profile.updated_at.isoformat() if profile.updated_at else None
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_tutee_avatar(request):
    if 'avatar' not in request.FILES:
        return Response({'error': 'No avatar provided'}, status=400)

    avatar = request.FILES['avatar']
    if not avatar.content_type.startswith('image/'):
        return Response({'error': 'File must be an image'}, status=400)

    if avatar.size > settings.MAX_DOCUMENT_UPLOAD_SIZE:
        return Response({'error': 'Image must be under 5MB'}, status=400)

    try:
        compressed = compress_image(avatar)
    except Exception:
        return Response({'error': 'Invalid image file'}, status=400)

    profile = request.user.userprofile
    if profile.profile_picture:
        profile.profile_picture.delete(save=False)
    profile.profile_picture = compressed
    profile.save()

    return Response({
        "profile_picture_url": request.build_absolute_uri(profile.profile_picture.url)
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_tutor_avatar(request):
    if 'avatar' not in request.FILES:
        return Response({'error': 'No avatar provided'}, status=400)

    avatar = request.FILES['avatar']
    if not avatar.content_type.startswith('image/'):
        return Response({'error': 'File must be an image'}, status=400)

    if avatar.size > settings.MAX_DOCUMENT_UPLOAD_SIZE:
        return Response({'error': 'Image must be under 5MB'}, status=400)

    try:
        compressed = compress_image(avatar)
    except Exception:
        return Response({'error': 'Invalid image file'}, status=400)

    profile = request.user.userprofile
    if profile.profile_picture:
        profile.profile_picture.delete(save=False)
    profile.profile_picture = compressed
    profile.save()

    return Response({
        "profile_picture_url": request.build_absolute_uri(profile.profile_picture.url)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_tutor_subjects(request):

    profile = request.user.userprofile
    tutor = Tutor.objects.get(profile=profile)

    subjects = TutorSubjects.objects.filter(tutor=tutor).select_related('subject')
    recognized_codes = recognized_subject_codes_for_profile(profile)

    data = [
        {
            "subject_code": ts.subject.subject_code,
            "subject_name": ts.subject.subject_name,
            "department": ts.subject.department,
            "category": ts.subject.category,
            "description": ts.description or '',
            "status": ts.subject.status,
            "is_recognized": ts.subject.subject_code in recognized_codes,
        }
        for ts in subjects
    ]

    return Response(data)


def generate_proposed_subject_code(subject_name):
    max_length = Subjects._meta.get_field('subject_code').max_length
    base_code = slugify(subject_name).upper() or 'SUBJECT'
    base_code = base_code[:max_length]
    candidate = base_code
    suffix = 2

    while Subjects.objects.filter(subject_code=candidate).exists():
        suffix_text = f'-{suffix}'
        candidate = f'{base_code[:max_length - len(suffix_text)]}{suffix_text}'
        suffix += 1

    return candidate


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def propose_tutor_subject(request):
    profile = request.user.userprofile
    if profile.role != 'Tutor':
        return Response({"error": "Only tutors can propose subjects."}, status=403)

    tutor = get_object_or_404(Tutor, profile=profile)
    if TutorSubjects.objects.filter(tutor=tutor).count() >= TUTOR_SUBJECT_LIMIT:
        return Response(
            {"error": f"You can add up to {TUTOR_SUBJECT_LIMIT} subjects only."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    subject_name = str(request.data.get('subject_name') or '').strip()
    category = str(request.data.get('category') or '').strip()
    description = str(request.data.get('description') or '').strip()
    keywords = str(request.data.get('keywords') or '').strip()

    if not subject_name or not category:
        return Response(
            {"error": "Subject name and category are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if category not in TAXONOMY_CATEGORIES:
        return Response(
            {"error": "Select a category from the taxonomy."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    application = TutorApplication.objects.filter(profile=profile).first()
    subject = Subjects.objects.create(
        subject_code=generate_proposed_subject_code(subject_name),
        subject_name=subject_name,
        category=category,
        keywords=keywords,
        status='pending',
        proposed_by_tutor=tutor,
        proposed_application=application,
    )
    TutorSubjects.objects.create(
        tutor=tutor,
        subject=subject,
        expertise_level=DEFAULT_TUTOR_SUBJECT_EXPERTISE_LEVEL,
        description=description,
    )

    return Response(
        {
            "subject_code": subject.subject_code,
            "subject_name": subject.subject_name,
            "category": subject.category,
            "keywords": subject.keywords,
            "description": description,
            "status": subject.status,
        },
        status=status.HTTP_201_CREATED,
    )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_tutor_subject(request):

    profile = request.user.userprofile
    tutor = Tutor.objects.get(profile=profile)

    subject_code = request.data.get("subject_code")
    description = request.data.get("description", '')

    try:
        subject = Subjects.objects.get(subject_code=subject_code)
    except Subjects.DoesNotExist:
        return Response({"error": "Invalid subject"}, status=400)

    if not subject_is_recognized_for_profile(profile, subject_code):
        return Response(
            {"error": SUBJECT_NOT_RECOGNIZED_ERROR},
            status=400,
        )

    tutor_subject, created = TutorSubjects.objects.get_or_create(
        tutor=tutor,
        subject=subject,
        defaults={"expertise_level": 3, "description": description or ''}
    )

    if not created and description is not None:
        tutor_subject.description = description or ''
        tutor_subject.save(update_fields=['description'])

    bump_dashboard_recs_cache_version()

    return Response({"message": "Subject added"})

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_tutor_subject(request, subject_code):

    profile = request.user.userprofile
    tutor = Tutor.objects.get(profile=profile)

    tutor_subject = get_object_or_404(
        TutorSubjects,
        tutor=tutor,
        subject__subject_code=subject_code
    )

    tutor_subject.description = request.data.get("description", '') or ''
    tutor_subject.save(update_fields=['description'])

    bump_dashboard_recs_cache_version()

    return Response({"message": "Subject updated"})

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_tutor_subject(request, subject_code):

    profile = request.user.userprofile
    tutor = Tutor.objects.get(profile=profile)

    subject = Subjects.objects.filter(
        subject_code=subject_code,
        proposed_by_tutor=tutor,
        status='pending',
    ).first()
    deleted_count, _ = TutorSubjects.objects.filter(
        tutor=tutor,
        subject__subject_code=subject_code
    ).delete()

    if deleted_count and subject is not None:
        subject.delete()

    if deleted_count:
        bump_dashboard_recs_cache_version()

    return Response({"message": "Subject removed"})


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_tutor_profile(request):

    profile = request.user.userprofile
    tutor = Tutor.objects.select_related('pinned_review').get(profile=profile)

    serializer = TutorProfileUpdateSerializer(
        tutor,
        data=request.data,
        partial=True
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    bump_dashboard_recs_cache_version()

    return Response({
        "message": "Tutor profile updated successfully",
        "tutor": TutorProfileSerializer(tutor).data
    })

@api_view(['GET'])
def payment_methods(request):
    active_methods = list(PaymentMethod.objects.filter(is_active=True).order_by('method_id'))
    has_paymongo = any(method.code == 'PAYMONGO' for method in active_methods)
    methods = []
    seen_codes = set()

    for method in active_methods:
        code = method.code

        if has_paymongo and str(code).lower() == 'online':
            continue

        if code in seen_codes:
            continue

        seen_codes.add(code)
        methods.append(method)

    data = [
        {
            "id": method.method_id,
            "name": method.method_name,
            "code": method.code
        }
        for method in methods
    ]

    return Response(data)


def get_paymongo_error_message(response_body):
    errors = response_body.get("errors") if isinstance(response_body, dict) else None

    if isinstance(errors, list) and errors:
        first_error = errors[0]

        if isinstance(first_error, dict):
            return (
                first_error.get("detail")
                or first_error.get("message")
                or first_error.get("code")
                or "PayMongo rejected the checkout session."
            )

    return "PayMongo rejected the checkout session."


def get_paymongo_auth_headers():
    secret_key = settings.PAYMONGO_SECRET_KEY
    auth_str = f"{secret_key}:"
    encoded_auth = base64.b64encode(auth_str.encode()).decode()

    return {
        "Content-Type": "application/json",
        "Authorization": f"Basic {encoded_auth}"
    }


def get_paymongo_payment_statuses(response_body):
    if not isinstance(response_body, dict):
        return []

    data = response_body.get('data') or {}
    attributes = data.get('attributes') or {}
    statuses = [
        attributes.get('status'),
        attributes.get('payment_status'),
    ]

    payment_intent = attributes.get('payment_intent') or data.get('payment_intent')

    if isinstance(payment_intent, dict):
        payment_intent_attributes = payment_intent.get('attributes') or {}
        statuses.extend([
            payment_intent.get('status'),
            payment_intent_attributes.get('status'),
            payment_intent_attributes.get('payment_status'),
        ])

    payments = attributes.get('payments') or data.get('payments') or []

    if isinstance(payments, dict):
        payments = payments.get('data') or []

    for payment in payments if isinstance(payments, list) else []:
        if not isinstance(payment, dict):
            continue

        payment_attributes = payment.get('attributes') or {}
        statuses.extend([
            payment.get('status'),
            payment_attributes.get('status'),
            payment_attributes.get('payment_status'),
        ])

    return [str(value).lower() for value in statuses if value]


def is_paymongo_checkout_paid(response_body):
    paid_statuses = {'paid', 'succeeded', 'success', 'completed'}
    return any(status_value in paid_statuses for status_value in get_paymongo_payment_statuses(response_body))


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_booking_location(request, booking_request_id):
    profile = request.user.userprofile
    try:
        tutor = Tutor.objects.get(profile=profile)
    except Tutor.DoesNotExist:
        return Response({"error": "Not a tutor"}, status=403)

    new_location = request.data.get('preferred_location', '').strip()

    if not new_location:
        return Response({"error": "Location cannot be empty for Face-to-Face sessions."}, status=400)

    # This used to require status="Pending", which Instant Booking (ADR-0008) stopped producing —
    # so the edit had become unreachable and an audited value could never be corrected. The window
    # is now the Grace Cutoff, evaluated per booking by Booking.tutor_can_edit_location().
    editable_bookings = Booking.objects.filter(
        booking_request_id=booking_request_id,
        tutor=tutor,
    ).select_related('student', 'tutor__profile', 'availability')

    booking = editable_bookings.first()

    if booking is None:
        return Response({"error": "No matching bookings found."}, status=404)

    if not booking.tutor_can_edit_location():
        return Response(
            {
                "error": (
                    "This location can no longer be changed. Face-to-face locations lock "
                    f"{GRACE_CUTOFF_HOURS} hours before the session starts."
                )
            },
            status=400,
        )

    editable_bookings.update(preferred_location=new_location)

    # Posts a live chat message into the shared room and refreshes both sides' booking context, so
    # the tutee sees the change immediately rather than travelling to a stale address.
    booking.preferred_location = new_location
    create_booking_event(
        booking,
        request.user,
        f"Face-to-face location updated to {new_location}.",
        "location_updated"
    )

    return Response({"message": "Location updated."})

# --- WALLET & PAYMENT VIEWS ---
from .models import Transaction, WithdrawalRequest, WalletTopUp
from .paymongo_money_movement import (
    PayMongoCashOutError,
    create_wallet_transaction,
    list_receiving_institutions,
    normalize_wallet_transaction,
)

PAYMONGO_REQUEST_TIMEOUT = 20  # seconds

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def wallet_status(request):
    """Returns the tutor's wallet balance and pending amount."""
    try:
        tutor = Tutor.objects.get(profile__user=request.user)
    except Tutor.DoesNotExist:
        return Response({"error": "Not a tutor"}, status=403)

    wallet, created = Wallet.objects.get_or_create(tutor=tutor)

    return Response({
        "balance": float(wallet.balance),
        "pending_amount": float(wallet.pending_amount),
        "currency": "PHP",
        "cashin_minimum": float(get_cashin_minimum()),
        "cashout_minimum": float(get_cashout_minimum()),
        "cashout_maximum": float(get_cashout_maximum()),
        "cashout_provider_fee": float(get_cashout_provider_fee()),
    })


def get_cashin_minimum():
    return decimal.Decimal(str(settings.CASHIN_MIN_PHP)).quantize(decimal.Decimal('0.01'))


def get_cashout_minimum():
    return decimal.Decimal(str(settings.CASHOUT_MIN_PHP)).quantize(decimal.Decimal('0.01'))


def get_cashout_maximum():
    return decimal.Decimal(str(settings.CASHOUT_MAX_PHP)).quantize(decimal.Decimal('0.01'))


def get_cashout_provider_fee():
    return decimal.Decimal(str(settings.CASHOUT_PROVIDER_FEE_PHP)).quantize(decimal.Decimal('0.01'))


def parse_money_amount(value):
    try:
        amount = decimal.Decimal(str(value)).quantize(decimal.Decimal('0.01'))
    except (decimal.InvalidOperation, TypeError, ValueError):
        return None

    return amount if amount > 0 else None


def get_request_tutor(request):
    try:
        return Tutor.objects.get(profile__user=request.user)
    except Tutor.DoesNotExist:
        return None


def get_cashout_callback_url(request):
    configured_url = getattr(settings, 'PAYMONGO_CASHOUT_CALLBACK_URL', '')
    base_url = configured_url or request.build_absolute_uri('/api/wallet/paymongo/callback/')

    # Append a shared-secret token so the inbound callback can be authenticated.
    secret = getattr(settings, 'PAYMONGO_CASHOUT_CALLBACK_SECRET', '')
    if secret:
        separator = '&' if '?' in base_url else '?'
        return f"{base_url}{separator}token={secret}"

    return base_url


def serialize_cash_out(withdrawal):
    return {
        "id": withdrawal.id,
        "amount": float(withdrawal.amount),
        "method": withdrawal.method,
        "receiving_institution_id": withdrawal.receiving_institution_id,
        "receiving_institution_name": withdrawal.receiving_institution_name,
        "receiving_institution_code": withdrawal.receiving_institution_code,
        "account_number": withdrawal.account_number,
        "account_name": withdrawal.account_name,
        "bank_name": withdrawal.bank_name,
        "status": withdrawal.status,
        "failure_reason": withdrawal.failure_reason,
        "provider": withdrawal.provider,
        "provider_wallet_transaction_id": withdrawal.provider_wallet_transaction_id,
        "provider_reference_number": withdrawal.provider_reference_number,
        "provider_status": withdrawal.provider_status,
        "provider_error_code": withdrawal.provider_error_code,
        "provider_error_message": withdrawal.provider_error_message,
        "provider_fee": float(withdrawal.provider_fee),
        "net_amount": float(withdrawal.net_amount),
        "callback_received_at": withdrawal.callback_received_at,
        "requested_at": withdrawal.requested_at,
        "processed_at": withdrawal.processed_at,
        "note": withdrawal.note,
    }


def cashout_method_display(withdrawal):
    if withdrawal.method == 'gcash':
        return 'Digital Wallet'
    return withdrawal.get_method_display()


def serialize_cash_in(topup):
    return {
        "id": topup.id,
        "amount": float(topup.amount),
        "status": topup.status,
        "provider": topup.provider,
        "provider_reference": topup.provider_reference,
        "created_at": topup.created_at,
        "paid_at": topup.paid_at,
    }


def update_cash_out_provider_fields(withdrawal, provider_data, callback_received=False):
    provider_status = provider_data.get('status') or withdrawal.provider_status

    withdrawal.provider_wallet_transaction_id = (
        provider_data.get('id') or withdrawal.provider_wallet_transaction_id
    )
    withdrawal.provider = provider_data.get('provider') or withdrawal.provider
    withdrawal.provider_reference_number = (
        provider_data.get('reference_number') or withdrawal.provider_reference_number
    )
    withdrawal.provider_status = provider_status
    withdrawal.provider_error_code = (
        provider_data.get('provider_error_code') or withdrawal.provider_error_code
    )
    withdrawal.provider_error_message = (
        provider_data.get('provider_error_message') or withdrawal.provider_error_message
    )

    provider_fee = provider_data.get('fee')
    if provider_fee and provider_fee > 0:
        withdrawal.provider_fee = provider_fee

    net_amount = provider_data.get('net_amount')
    if net_amount and net_amount > 0:
        withdrawal.net_amount = net_amount

    if callback_received:
        withdrawal.callback_received_at = timezone.now()


def reverse_failed_cash_out(withdrawal):
    wallet = Wallet.objects.select_for_update().get(tutor=withdrawal.tutor)
    principal_ref = f"WD-{withdrawal.id}-REV"
    fee_ref = f"WD-{withdrawal.id}-FEE-REV"
    changed_balance = False

    if not Transaction.objects.filter(wallet=wallet, reference_id=principal_ref).exists():
        wallet.balance += withdrawal.amount
        changed_balance = True
        Transaction.objects.create(
            wallet=wallet,
            transaction_type='withdrawal_reversal',
            amount=withdrawal.amount,
            description=f"Cash-out reversal for failed request #{withdrawal.id}",
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
            description=f"Provider fee reversal for failed cash-out #{withdrawal.id}",
            reference_id=fee_ref
        )

    if changed_balance:
        wallet.save(update_fields=['balance'])


def log_cash_out_activity(withdrawal):
    # Auto-processed cash-outs never pass through the admin review path, so record the
    # terminal outcome here to keep the admin activity feed complete. Non-terminal
    # (pending/processing) resolutions log nothing -- the later callback resolves them.
    activity_type = {
        'processed': 'withdrawal_processed',
        'failed': 'withdrawal_failed',
    }.get(withdrawal.status)
    if not activity_type:
        return

    profile = withdrawal.tutor.profile
    outcome = 'processed' if withdrawal.status == 'processed' else 'failed'
    PlatformActivity.objects.create(
        activity_type=activity_type,
        message=f"Cash-out #{withdrawal.id} for {profile.fname} {outcome}",
        institution=profile.institution,
    )


def apply_cash_out_provider_result(withdrawal, provider_data, callback_received=False):
    with transaction.atomic():
        locked_withdrawal = WithdrawalRequest.objects.select_for_update().get(pk=withdrawal.pk)
        update_cash_out_provider_fields(locked_withdrawal, provider_data, callback_received)
        provider_status = (locked_withdrawal.provider_status or '').lower()

        if provider_status == 'succeeded':
            locked_withdrawal.status = 'processed'
            locked_withdrawal.processed_at = locked_withdrawal.processed_at or timezone.now()
        elif provider_status == 'failed':
            locked_withdrawal.status = 'failed'
            locked_withdrawal.processed_at = locked_withdrawal.processed_at or timezone.now()
            if locked_withdrawal.provider_error_message and not locked_withdrawal.failure_reason:
                locked_withdrawal.failure_reason = locked_withdrawal.provider_error_message
            reverse_failed_cash_out(locked_withdrawal)

        locked_withdrawal.save()
        log_cash_out_activity(locked_withdrawal)
        return locked_withdrawal

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def wallet_transactions(request):
    """Returns the history of credits and withdrawals."""
    try:
        tutor = Tutor.objects.get(profile__user=request.user)
    except Tutor.DoesNotExist:
        return Response({"error": "Not a tutor"}, status=403)

    wallet, _ = Wallet.objects.get_or_create(tutor=tutor)
    transactions = Transaction.objects.filter(wallet=wallet).order_by('-created_at')

    data = []
    for tx in transactions:
        payment_transaction_id = get_wallet_transaction_payment_reference(tx)
        student_name = get_wallet_transaction_student_name(tx)
        description = get_wallet_transaction_description(tx, student_name)
        data.append({
            "id": tx.id,
            "transaction_type": tx.transaction_type,
            "amount": float(tx.amount),
            "description": description,
            "reference_id": tx.reference_id,
            "payment_transaction_id": payment_transaction_id,
            "student_name": student_name,
            "created_at": tx.created_at
        })
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_withdrawals(request):
    """Returns the tutor's withdrawal history."""
    try:
        tutor = Tutor.objects.get(profile__user=request.user)
    except Tutor.DoesNotExist:
        return Response({"error": "Not a tutor"}, status=403)

    withdrawals = WithdrawalRequest.objects.filter(tutor=tutor).order_by('-requested_at')

    data = []
    for w in withdrawals:
        data.append({
            "id": w.id,
            "amount": float(w.amount),
            "method": w.method,
            "account_number": w.account_number,
            "account_name": w.account_name,
            "status": w.status,
            "requested_at": w.requested_at,
            "processed_at": w.processed_at
        })
    return Response(data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_withdrawal(request):
    """Creates a new withdrawal request."""
    try:
        tutor = Tutor.objects.get(profile__user=request.user)
    except Tutor.DoesNotExist:
        return Response({"error": "Not a tutor"}, status=403)

    wallet, _ = Wallet.objects.get_or_create(tutor=tutor)

    amount = request.data.get('amount')
    if not amount or decimal.Decimal(str(amount)) > wallet.balance:
        return Response({"error": "Insufficient balance"}, status=400)

    minimum_amount = get_cashout_minimum()
    if decimal.Decimal(str(amount)) < minimum_amount:
        return Response({"error": f"Minimum withdrawal is PHP {minimum_amount}."}, status=400)

    with transaction.atomic():
        withdrawal = WithdrawalRequest.objects.create(
            tutor=tutor,
            amount=amount,
            method=request.data.get('method'),
            account_number=request.data.get('account_number'),
            account_name=request.data.get('account_name'),
            bank_name=request.data.get('bank_name', ''),
            status='pending'
        )

        wallet.balance -= decimal.Decimal(str(amount))
        wallet.save()

        Transaction.objects.create(
            wallet=wallet,
            transaction_type='withdrawal',
            amount=-decimal.Decimal(str(amount)),
            description=f"Withdrawal request via {cashout_method_display(withdrawal)}",
            reference_id=f"WD-{withdrawal.id}"
        )

    return Response({"status": "pending", "id": withdrawal.id})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def receiving_institutions(request):
    try:
        provider_response = list_receiving_institutions()
    except PayMongoCashOutError as exc:
        return Response({"error": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

    return Response(provider_response.get('data', provider_response))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_withdrawals(request):
    tutor = get_request_tutor(request)
    if tutor is None:
        return Response({"error": "Not a tutor"}, status=403)

    withdrawals = WithdrawalRequest.objects.filter(tutor=tutor).order_by('-requested_at')
    return Response([serialize_cash_out(withdrawal) for withdrawal in withdrawals])


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_withdrawal(request):
    return cash_outs(request)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def cash_outs(request):
    tutor = get_request_tutor(request)
    if tutor is None:
        return Response({"error": "Not a tutor"}, status=403)

    if request.method == 'GET':
        withdrawals = WithdrawalRequest.objects.filter(tutor=tutor).order_by('-requested_at')
        return Response([serialize_cash_out(withdrawal) for withdrawal in withdrawals])

    amount = parse_money_amount(request.data.get('amount'))
    if amount is None:
        return Response({"error": "Enter a valid cash-out amount."}, status=400)

    minimum_amount = get_cashout_minimum()
    if amount < minimum_amount:
        return Response({"error": f"Minimum cash-out is PHP {minimum_amount}."}, status=400)

    maximum_amount = get_cashout_maximum()
    if amount > maximum_amount:
        return Response({"error": f"Maximum cash-out per request is PHP {maximum_amount}."}, status=400)

    destination_type = request.data.get('destination_type')
    if destination_type not in ('gcash', 'bank'):
        return Response({"error": "Select a valid destination type (gcash or bank)."}, status=400)

    account_number = request.data.get('account_number')
    if not account_number:
        return Response({"error": "Enter the destination account number."}, status=400)

    account_name = request.data.get('account_name')
    if not account_name:
        return Response({"error": "Enter the destination account name."}, status=400)

    receiving_institution_id = request.data.get('receiving_institution_id')
    receiving_institution_name = request.data.get('receiving_institution_name')
    if not receiving_institution_id or not receiving_institution_name:
        return Response({"error": "Select the receiving institution."}, status=400)

    receiving_institution_code = request.data.get('receiving_institution_code', '')
    bank_name = request.data.get('bank_name')
    if destination_type == 'bank' and not bank_name:
        return Response({"error": "Enter the destination bank name."}, status=400)
    note = request.data.get('note', '')

    recent_withdrawals = list(
        WithdrawalRequest.objects.filter(tutor=tutor).order_by('-requested_at')[:4]
    )
    has_history = len(recent_withdrawals) > 0
    matches_recent_destination = any(
        previous.method == destination_type
        and previous.receiving_institution_id == receiving_institution_id
        and previous.account_number == account_number
        and previous.account_name == account_name
        for previous in recent_withdrawals
    )

    if has_history and not matches_recent_destination and request.data.get('confirm_new_destination') is not True:
        return Response({"error": "new_destination_confirmation_required"}, status=409)

    destination = SimpleNamespace(
        destination_type=destination_type,
        receiving_institution_id=receiving_institution_id,
        receiving_institution_name=receiving_institution_name,
        receiving_institution_code=receiving_institution_code,
        account_number=account_number,
        account_name=account_name,
        bank_name=bank_name,
    )

    with transaction.atomic():
        wallet, _ = Wallet.objects.select_for_update().get_or_create(tutor=tutor)
        provider_fee = get_cashout_provider_fee()
        total_deducted = amount + provider_fee

        if total_deducted > wallet.balance:
            return Response({"error": "Insufficient balance for cash-out amount plus provider fee."}, status=400)

        withdrawal = WithdrawalRequest.objects.create(
            tutor=tutor,
            amount=amount,
            method=destination_type,
            receiving_institution_id=receiving_institution_id,
            receiving_institution_name=receiving_institution_name,
            receiving_institution_code=receiving_institution_code,
            account_number=account_number,
            account_name=account_name,
            bank_name=bank_name,
            note=note,
            provider='paymongo',
            provider_fee=provider_fee,
            net_amount=amount,
            status='pending',
        )

        wallet.balance -= total_deducted
        wallet.save(update_fields=['balance'])

        Transaction.objects.create(
            wallet=wallet,
            transaction_type='withdrawal',
            amount=-amount,
            description=f"Cash-out request via {cashout_method_display(withdrawal)}",
            reference_id=f"WD-{withdrawal.id}"
        )

        if provider_fee > 0:
            Transaction.objects.create(
                wallet=wallet,
                transaction_type='cashout_fee',
                amount=-provider_fee,
                description=f"Provider fee for cash-out request #{withdrawal.id}",
                reference_id=f"WD-{withdrawal.id}-FEE"
            )

    try:
        provider_data = create_wallet_transaction(
            settings.PAYMONGO_WALLET_ID,
            destination,
            amount,
            get_cashout_callback_url(request),
            withdrawal.id,
        )
    except PayMongoCashOutError as exc:
        provider_data = {
            'status': 'failed',
            'provider': 'paymongo',
            'provider_error_message': str(exc),
        }
        withdrawal = apply_cash_out_provider_result(withdrawal, provider_data)
        return Response(serialize_cash_out(withdrawal), status=status.HTTP_502_BAD_GATEWAY)

    withdrawal = apply_cash_out_provider_result(withdrawal, provider_data)
    return Response(serialize_cash_out(withdrawal), status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recent_cash_outs(request):
    tutor = get_request_tutor(request)
    if tutor is None:
        return Response({"error": "Not a tutor"}, status=403)

    withdrawals = WithdrawalRequest.objects.filter(tutor=tutor).order_by('-requested_at')[:4]
    return Response([serialize_cash_out(withdrawal) for withdrawal in withdrawals])


request_withdrawal = cash_outs


@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def paymongo_cashout_callback(request):
    # Authenticate the callback with the shared secret token when configured.
    secret = getattr(settings, 'PAYMONGO_CASHOUT_CALLBACK_SECRET', '')
    if secret:
        provided = request.query_params.get('token', '')
        if not constant_time_compare(provided, secret):
            logger.warning("Rejected PayMongo cashout callback: invalid or missing token.")
            return Response({"error": "Unauthorized."}, status=status.HTTP_403_FORBIDDEN)
    else:
        logger.warning(
            "PayMongo cashout callback received without signature verification "
            "(PAYMONGO_CASHOUT_CALLBACK_SECRET not set)."
        )

    provider_data = normalize_wallet_transaction(request.data)
    provider_transaction_id = provider_data.get('id')

    if not provider_transaction_id:
        return Response({"error": "Missing wallet transaction id."}, status=400)

    withdrawal = get_object_or_404(
        WithdrawalRequest,
        provider_wallet_transaction_id=provider_transaction_id
    )
    withdrawal = apply_cash_out_provider_result(
        withdrawal,
        provider_data,
        callback_received=True
    )

    return Response({"status": withdrawal.status})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_online_payment(request):
    """Creates a PayMongo Checkout Session."""
    booking_id = request.data.get('booking_id')
    booking = get_object_or_404(Booking, id=booking_id, student__user=request.user)

    # Calculate amount: Hourly Rate * Duration (sum of slots)
    group_bookings = get_booking_request_bookings(booking)
    representative_booking = get_representative_booking(group_bookings)
    duration_hours = get_duration_hours_for_bookings(group_bookings)
    total_amount = decimal.Decimal(str(representative_booking.tutor.hourly_rate)) * decimal.Decimal(
        str(duration_hours)
    )

    # PayMongo amount in centavos
    amount_cents = int(total_amount * decimal.Decimal("100"))
    reference_code = f"SB-BK-{representative_booking.id}"

    url = "https://api.paymongo.com/v1/checkout_sessions"
    payload = {
        "data": {
            "attributes": {
                "send_email_receipt": True,
                "show_description": True,
                "show_line_items": True,
                "description": (
                    f"StudyBuddy {reference_code} - Session with "
                    f"{representative_booking.tutor.profile.fname}"
                ),
                "line_items": [
                    {
                        "currency": "PHP",
                        "amount": amount_cents,
                        "description": f"Tutoring Session Fee ({reference_code})",
                        "name": f"StudyBuddy {reference_code}",
                        "quantity": 1
                    }
                ],
                "payment_method_types": ["gcash", "card", "paymaya"],
                "success_url": f"{settings.FRONTEND_URL}/tuteeSessionDetails/{representative_booking.id}?payment=success",
                "cancel_url": f"{settings.FRONTEND_URL}/payment-tutee/{representative_booking.id}?payment=cancelled",
            }
        }
    }

    try:
        response = requests.post(
            url,
            json=payload,
            headers=get_paymongo_auth_headers(),
            timeout=PAYMONGO_REQUEST_TIMEOUT,
        )
        try:
            res_data = response.json()
        except ValueError:
            res_data = {"raw": getattr(response, "text", "")}

        logger.info(
            "PayMongo checkout response status=%s",
            response.status_code,
        )

        if response.status_code in (200, 201):
            checkout_url = (
                res_data
                .get('data', {})
                .get('attributes', {})
                .get('checkout_url')
            )

            if not checkout_url:
                logger.error("PayMongo checkout response missing checkout_url: %s", res_data)
                error_response = {
                    "error": "Payment provider did not return a checkout URL.",
                }

                if settings.DEBUG or settings.PAYMONGO_DEBUG_ERRORS_ENABLED:
                    error_response["provider_status"] = response.status_code
                    error_response["provider_error"] = res_data

                return Response(error_response, status=status.HTTP_502_BAD_GATEWAY)

            # Store payment record
            method_online, _ = PaymentMethod.objects.get_or_create(
                code='PAYMONGO',
                defaults={'method_name': 'Pay Online (GCash / Card)', 'is_active': True}
            )

            payment, _ = Payment.objects.get_or_create(
                booking=representative_booking,
                defaults={
                    'amount': total_amount,
                    'method': method_online,
                    'payment_status': 'Pending'
                }
            )
            payment.amount = total_amount
            payment.method = method_online
            payment.payment_status = 'Pending'
            payment.transaction_reference = res_data.get('data', {}).get('id')
            payment.save(update_fields=[
                'amount',
                'method',
                'payment_status',
                'transaction_reference',
            ])

            return Response({"payment_url": checkout_url})

        provider_message = get_paymongo_error_message(res_data)
        logger.error(
            "PayMongo checkout failed status=%s error=%s body=%s",
            response.status_code,
            provider_message,
            res_data,
        )

        if response.status_code == 401:
            error_response = {
                "error": "Payment provider authentication failed. Check the PayMongo secret key.",
            }
            response_status = status.HTTP_502_BAD_GATEWAY
        else:
            error_response = {"error": provider_message}
            response_status = (
                status.HTTP_400_BAD_REQUEST
                if response.status_code == 400
                else status.HTTP_502_BAD_GATEWAY
            )

        if settings.DEBUG or settings.PAYMONGO_DEBUG_ERRORS_ENABLED:
            error_response["provider_status"] = response.status_code
            error_response["provider_error"] = res_data

        return Response(error_response, status=response_status)
    except requests.RequestException as exc:
        logger.error("Payment initiation request failed: %s", exc)
        return Response(
            {"error": "Could not reach the payment provider. Please try again."},
            status=status.HTTP_502_BAD_GATEWAY,
        )
    except Exception as e:
        logger.error(f"Payment Initiation Exception: {str(e)}")
        return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_online_payment(request, booking_id):
    profile = request.user.userprofile
    booking = get_object_or_404(
        Booking.objects.select_related('availability', 'tutor', 'tutor__profile'),
        id=booking_id
    )

    if profile != booking.student:
        return Response({"error": "Unauthorized"}, status=403)

    session_group_bookings = get_booking_request_bookings(booking)
    representative_booking = get_representative_booking(session_group_bookings)
    payment = getattr(representative_booking, 'payment', None)

    if not payment or getattr(payment.method, 'code', None) != 'PAYMONGO':
        return Response({"error": "No PayMongo checkout is pending for this session."}, status=400)

    if not payment.transaction_reference:
        return Response({"error": "Missing PayMongo checkout session reference."}, status=400)

    url = f"https://api.paymongo.com/v1/checkout_sessions/{payment.transaction_reference}"

    try:
        response = requests.get(
            url,
            headers=get_paymongo_auth_headers(),
            timeout=PAYMONGO_REQUEST_TIMEOUT,
        )

        try:
            res_data = response.json()
        except ValueError:
            res_data = {"raw": getattr(response, "text", "")}

        logger.info(
            "PayMongo checkout retrieve response status=%s",
            response.status_code,
        )

        if response.status_code != 200:
            provider_message = get_paymongo_error_message(res_data)
            logger.error(
                "PayMongo checkout retrieve failed status=%s error=%s body=%s",
                response.status_code,
                provider_message,
                res_data,
            )
            error_response = {"error": provider_message}

            if settings.DEBUG or settings.PAYMONGO_DEBUG_ERRORS_ENABLED:
                error_response["provider_status"] = response.status_code
                error_response["provider_error"] = res_data

            return Response(error_response, status=status.HTTP_502_BAD_GATEWAY)

        if not is_paymongo_checkout_paid(res_data):
            error_response = {
                "error": "Online payment has not been completed yet.",
                "provider_payment_statuses": get_paymongo_payment_statuses(res_data),
            }

            if settings.DEBUG or settings.PAYMONGO_DEBUG_ERRORS_ENABLED:
                error_response["provider_status"] = response.status_code
                error_response["provider_error"] = res_data

            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)

        already_submitted = all(
            group_booking.status == "Awaiting Payment Verification"
            and group_booking.tutee_confirmed
            for group_booking in session_group_bookings
        )

        with transaction.atomic():
            payment.payment_status = "Paid"
            payment.paid_at = now()
            payment.save(update_fields=['payment_status', 'paid_at'])

            Booking.objects.filter(
                id__in=[group_booking.id for group_booking in session_group_bookings]
            ).update(
                tutee_confirmed=True,
                status="Awaiting Payment Verification"
            )

            if not already_submitted:
                create_booking_status_notification(
                    representative_booking.tutor.profile,
                    "awaiting_payment_verification",
                    session_group_bookings
                )

        representative_booking.refresh_from_db()
        refreshed_group = get_booking_request_bookings(representative_booking)
        return Response(build_booking_detail_payload(refreshed_group))
    except requests.RequestException as exc:
        logger.error("Payment verification request failed: %s", exc)
        return Response(
            {"error": "Could not reach the payment provider. Please try again."},
            status=status.HTTP_502_BAD_GATEWAY,
        )
    except Exception as e:
        logger.error(f"Payment Verification Exception: {str(e)}")
        return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def credit_tutor_wallet(booking):
    session_group = get_session_group_bookings(booking)
    rep_booking = get_representative_booking(session_group)

    payment = getattr(rep_booking, 'payment', None)
    if not payment or payment.payment_status != 'Paid':
        return

    ref_id = f"BK-{rep_booking.id}"
    if Transaction.objects.filter(reference_id=ref_id).exists():
        return

    COMMISSION_RATE = decimal.Decimal('0.10')
    total_amount = payment.amount
    commission = total_amount * COMMISSION_RATE

    with transaction.atomic():
        wallet, _ = Wallet.objects.get_or_create(tutor=rep_booking.tutor)

        if payment.method.code in PAYMONGO_SETTLED_CODES:
            tutor_share = total_amount - commission
            wallet.balance += tutor_share
            wallet.save(update_fields=['balance'])
            student_name = f"{rep_booking.student.fname} {rep_booking.student.lname}".strip()
            student_note = f" - Student: {student_name}" if student_name else ""
            Transaction.objects.create(
                wallet=wallet,
                transaction_type='session_credit',
                amount=tutor_share,
                description=(
                    f"Session Credit for {rep_booking.session_date} "
                    f"(Less 10% Platform Fee){student_note}"
                ),
                reference_id=ref_id
            )
        elif payment.method.code == 'CASH':
            wallet.balance -= commission
            wallet.save()
            Transaction.objects.create(
                wallet=wallet,
                transaction_type='commission_deduction',
                amount=-commission,
                description=f"Platform Commission for {rep_booking.session_date} (10% of ₱{total_amount})",
                reference_id=ref_id
            )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_cash_in(request):
    """Create a PayMongo Checkout Session for a wallet top-up."""
    tutor = get_request_tutor(request)
    if tutor is None:
        return Response({"error": "Not a tutor"}, status=403)

    amount = parse_money_amount(request.data.get('amount'))
    if amount is None:
        return Response({"error": "Enter a valid cash-in amount."}, status=400)

    minimum_amount = get_cashin_minimum()
    if amount < minimum_amount:
        return Response({"error": f"Minimum cash-in is PHP {minimum_amount}."}, status=400)

    topup = WalletTopUp.objects.create(
        tutor=tutor, amount=amount, status='pending', provider='paymongo'
    )

    amount_cents = int(amount * decimal.Decimal("100"))
    label = f"StudyBuddy Wallet Top-Up TOPUP-{topup.id}"
    url = "https://api.paymongo.com/v1/checkout_sessions"
    payload = {
        "data": {
            "attributes": {
                "line_items": [
                    {
                        "currency": "PHP",
                        "amount": amount_cents,
                        "name": label,
                        "quantity": 1,
                    }
                ],
                "payment_method_types": ["gcash", "card", "paymaya"],
                "description": label,
                "success_url": f"{settings.FRONTEND_URL}/tch-wallet?cashin=success&id={topup.id}",
                "cancel_url": f"{settings.FRONTEND_URL}/tch-wallet?cashin=cancelled&id={topup.id}",
            }
        }
    }

    try:
        response = requests.post(
            url,
            json=payload,
            headers=get_paymongo_auth_headers(),
            timeout=PAYMONGO_REQUEST_TIMEOUT,
        )
        try:
            res_data = response.json()
        except ValueError:
            res_data = {"raw": getattr(response, "text", "")}

        if response.status_code in (200, 201):
            checkout_url = (
                res_data.get('data', {}).get('attributes', {}).get('checkout_url')
            )
            if not checkout_url:
                topup.status = 'failed'
                topup.save(update_fields=['status'])
                return Response(
                    {"error": "Payment provider did not return a checkout URL."},
                    status=status.HTTP_502_BAD_GATEWAY,
                )

            topup.provider_reference = res_data['data']['id']
            topup.save(update_fields=['provider_reference'])
            return Response({"checkout_url": checkout_url, "id": topup.id})

        topup.status = 'failed'
        topup.save(update_fields=['status'])
        provider_message = get_paymongo_error_message(res_data)
        logger.error(
            "Cash-in checkout failed status=%s error=%s", response.status_code, provider_message
        )
        return Response({"error": provider_message}, status=status.HTTP_502_BAD_GATEWAY)
    except requests.RequestException as exc:
        topup.status = 'failed'
        topup.save(update_fields=['status'])
        logger.error("Cash-in checkout request failed: %s", exc)
        return Response(
            {"error": "Could not reach the payment provider. Please try again."},
            status=status.HTTP_502_BAD_GATEWAY,
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_cash_in(request, topup_id):
    """Confirm a PayMongo checkout was paid and credit the wallet (idempotent)."""
    tutor = get_request_tutor(request)
    if tutor is None:
        return Response({"error": "Not a tutor"}, status=403)

    topup = get_object_or_404(WalletTopUp, id=topup_id, tutor=tutor)

    if topup.status == 'paid':
        wallet, _ = Wallet.objects.get_or_create(tutor=tutor)
        payload = serialize_cash_in(topup)
        payload["balance"] = float(wallet.balance)
        return Response(payload)

    if not topup.provider_reference:
        return Response({"error": "No PayMongo checkout for this top-up."}, status=400)

    url = f"https://api.paymongo.com/v1/checkout_sessions/{topup.provider_reference}"
    try:
        response = requests.get(
            url, headers=get_paymongo_auth_headers(), timeout=PAYMONGO_REQUEST_TIMEOUT
        )
        try:
            res_data = response.json()
        except ValueError:
            res_data = {"raw": getattr(response, "text", "")}
    except requests.RequestException as exc:
        logger.error("Cash-in verify request failed: %s", exc)
        return Response(
            {"error": "Could not reach the payment provider. Please try again."},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    if response.status_code != 200:
        return Response(
            {"error": "Payment provider error."}, status=status.HTTP_502_BAD_GATEWAY
        )

    if not is_paymongo_checkout_paid(res_data):
        return Response({"error": "Payment not completed yet."}, status=400)

    with transaction.atomic():
        wallet = Wallet.objects.select_for_update().get(tutor=tutor)
        topup.refresh_from_db()
        if topup.status != 'paid':
            topup.status = 'paid'
            topup.paid_at = timezone.now()
            topup.save(update_fields=['status', 'paid_at'])

            ref_id = f"TOPUP-{topup.id}"
            if not Transaction.objects.filter(reference_id=ref_id).exists():
                wallet.balance += topup.amount
                wallet.save(update_fields=['balance'])
                Transaction.objects.create(
                    wallet=wallet,
                    transaction_type='cash_in',
                    amount=topup.amount,
                    description=f"Wallet Top-Up {ref_id}",
                    reference_id=ref_id,
                )

    wallet.refresh_from_db()
    payload = serialize_cash_in(topup)
    payload["balance"] = float(wallet.balance)
    return Response(payload)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def dev_add_wallet_funds(request):
    if not settings.BOOKING_DEV_TOOLS_ENABLED:
        return Response(status=404)
    try:
        tutor = request.user.userprofile.tutor
    except Exception:
        return Response({'error': 'No tutor profile found for this user.'}, status=400)
    amount = decimal.Decimal(str(request.data.get('amount', 500)))
    if amount <= 0:
        return Response({'error': 'Amount must be positive.'}, status=400)
    with transaction.atomic():
        wallet, _ = Wallet.objects.get_or_create(tutor=tutor)
        wallet.balance += amount
        wallet.save()
        Transaction.objects.create(
            wallet=wallet,
            transaction_type='session_credit',
            amount=amount,
            description='Dev credit (testing only)',
            reference_id=f'DEV-{timezone.now().timestamp()}'
        )
    return Response({'balance': str(wallet.balance)})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def dev_remove_wallet_funds(request):
    if not settings.BOOKING_DEV_TOOLS_ENABLED:
        return Response(status=404)
    try:
        tutor = request.user.userprofile.tutor
    except Exception:
        return Response({'error': 'No tutor profile found for this user.'}, status=400)
    amount = decimal.Decimal(str(request.data.get('amount', 500)))
    if amount <= 0:
        return Response({'error': 'Amount must be positive.'}, status=400)
    with transaction.atomic():
        wallet, _ = Wallet.objects.get_or_create(tutor=tutor)
        wallet.balance -= amount
        wallet.save()
        Transaction.objects.create(
            wallet=wallet,
            transaction_type='commission_deduction',
            amount=-amount,
            description='Dev debit (testing only)',
            reference_id=f'DEV-{timezone.now().timestamp()}'
        )
    return Response({'balance': str(wallet.balance)})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_support_ticket(request):
    user_profile = request.user.userprofile
    data = request.data

    with transaction.atomic():
        from studybuddy.chat.models import ChatRoom
        from .models import SupportTicket
        room = ChatRoom.objects.create(
            room_type='support',
            tutee=user_profile
        )

        ticket = SupportTicket.objects.create(
            user=user_profile,
            category=data.get('category'),
            subject=data.get('subject'),
            description=data.get('description'),
            booking_id=data.get('booking_id'),
            transaction_id=data.get('transaction_id'),
            chatroom=room
        )

        from studybuddy.chat.models import Message
        Message.objects.create(
            room=room,
            sender=None,
            content=f"Ticket #{ticket.id} created. Category: {ticket.category}. An agent will assist you shortly."
        )

    return Response({"message": "Ticket created", "ticket_id": ticket.id, "room_id": room.id}, status=201)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def admin_claim_ticket(request, ticket_id):
    profile = request.user.userprofile
    if profile.role != 'SuperAdmin':
        return Response(status=403)

    from .models import SupportTicket
    queryset = SupportTicket.objects.select_related('chatroom').all()
    if profile.role != 'SuperAdmin':
        queryset = queryset.filter(user__institution=profile.institution)

    ticket = get_object_or_404(queryset, id=ticket_id)
    if ticket.status == 'Escalated' and profile.role != 'SuperAdmin':
        return Response({"error": "Escalated tickets must be handled by a SuperAdmin."}, status=403)

    try:
        with transaction.atomic():
            ticket.assigned_agent = profile
            if ticket.status != 'Escalated':
                ticket.status = 'In_Progress'

            ticket.chatroom.tutor = profile

            ticket.save(update_fields=['assigned_agent', 'status', 'updated_at'])
            ticket.chatroom.save(update_fields=['tutor', 'updated_at'])
    except IntegrityError:
        return Response(
            {"error": "User already has an active support ticket claimed by you."},
            status=status.HTTP_400_BAD_REQUEST
        )

    return Response({"message": "Ticket claimed"})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def admin_escalate_ticket(request, ticket_id):
    profile = request.user.userprofile
    if profile.role != 'Admin':
        return Response(status=403)

    reason = str(request.data.get('reason', '')).strip()
    if not reason:
        return Response({"error": "Escalation reason is required."}, status=status.HTTP_400_BAD_REQUEST)

    from .models import SupportTicket
    ticket = get_object_or_404(
        SupportTicket.objects.select_related('chatroom').filter(user__institution=profile.institution),
        id=ticket_id,
    )
    if ticket.status == 'Resolved':
        return Response({"error": "Resolved tickets cannot be escalated."}, status=status.HTTP_400_BAD_REQUEST)
    if ticket.status == 'Escalated':
        return Response({"error": "Ticket is already escalated."}, status=status.HTTP_400_BAD_REQUEST)

    with transaction.atomic():
        ticket.status = 'Escalated'
        ticket.escalation_reason = reason
        ticket.escalated_by = profile
        ticket.escalated_at = timezone.now()
        ticket.assigned_agent = None
        ticket.save(update_fields=[
            'status',
            'escalation_reason',
            'escalated_by',
            'escalated_at',
            'assigned_agent',
            'updated_at',
        ])

        if ticket.chatroom:
            ticket.chatroom.tutor = None
            ticket.chatroom.save(update_fields=['tutor', 'updated_at'])

            from studybuddy.chat.models import Message
            Message.objects.create(
                room=ticket.chatroom,
                sender=None,
                content="This support ticket has been escalated to SuperAdmin support.",
            )

    return Response({
        "message": "Ticket escalated",
        "status": "Escalated",
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_my_tickets(request):
    user_profile = request.user.userprofile
    from .models import SupportTicket
    tickets = SupportTicket.objects.filter(user=user_profile).order_by('-created_at')

    data = []
    for ticket in tickets:
        data.append({
            "id": ticket.id,
            "category": ticket.category,
            "subject": ticket.subject,
            "description": ticket.description,
            "status": ticket.status,
            "booking_id": ticket.booking_id,
            "transaction_id": ticket.transaction_id,
            "chatroom_id": ticket.chatroom_id,
            "assigned_agent": f"{ticket.assigned_agent.fname} {ticket.assigned_agent.lname}" if ticket.assigned_agent else None,
            "created_at": ticket.created_at,
            "updated_at": ticket.updated_at,
        })
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_list_tickets(request):
    profile = request.user.userprofile
    if profile.role != 'SuperAdmin':
        return Response(status=403)

    from .models import SupportTicket
    tickets = SupportTicket.objects.select_related('user', 'assigned_agent', 'escalated_by').all().order_by('-created_at')

    if profile.role == 'SuperAdmin':
        tickets = tickets.filter(Q(status='Escalated') | Q(escalated_at__isnull=False))
    else:
        tickets = tickets.filter(user__institution=profile.institution).exclude(status='Escalated')

    data = []
    for ticket in tickets:
        data.append({
            "id": ticket.id,
            "user": {
                "id": ticket.user.id,
                "name": f"{ticket.user.fname} {ticket.user.lname}",
                "role": ticket.user.role
            },
            "category": ticket.category,
            "subject": ticket.subject,
            "description": ticket.description,
            "status": ticket.status,
            "booking_id": ticket.booking_id,
            "transaction_id": ticket.transaction_id,
            "chatroom_id": ticket.chatroom_id,
            "assigned_agent": f"{ticket.assigned_agent.fname} {ticket.assigned_agent.lname}" if ticket.assigned_agent else None,
            "assigned_agent_id": ticket.assigned_agent_id,
            "escalation_reason": ticket.escalation_reason,
            "escalated_by": f"{ticket.escalated_by.fname} {ticket.escalated_by.lname}" if ticket.escalated_by else None,
            "escalated_at": ticket.escalated_at,
            "created_at": ticket.created_at,
            "updated_at": ticket.updated_at,
        })
    return Response(data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def admin_resolve_ticket(request, ticket_id):
    profile = request.user.userprofile
    if profile.role != 'SuperAdmin':
        return Response(status=403)

    from .models import SupportTicket
    queryset = SupportTicket.objects.all()
    if profile.role != 'SuperAdmin':
        queryset = queryset.filter(user__institution=profile.institution)

    ticket = get_object_or_404(queryset.select_for_update(), id=ticket_id)
    if ticket.status == 'Escalated' and profile.role != 'SuperAdmin':
        return Response({"error": "Escalated tickets must be resolved by a SuperAdmin."}, status=403)

    verdict = request.data.get('verdict')
    if ticket.category == 'Late_Cancellation':
        if verdict not in {'excused', 'counted'}:
            return Response({'error': 'A Late Cancellation requires an excused or counted verdict.'}, status=400)
        if ticket.resolution_verdict:
            return Response({'error': 'This Late Cancellation has already been resolved.'}, status=400)
        ticket.resolution_verdict = verdict
        if verdict == 'counted' and ticket.penalized_user and ticket.penalized_user.role == 'Tutor':
            tutor = Tutor.objects.select_for_update().get(profile=ticket.penalized_user)
            wallet, _ = Wallet.objects.select_for_update().get_or_create(tutor=tutor)
            wallet.balance -= COUNTED_STRIKE_WALLET_DEDUCTION
            wallet.save(update_fields=['balance', 'last_updated'])
            Transaction.objects.create(
                wallet=wallet,
                transaction_type='counted_strike',
                amount=-COUNTED_STRIKE_WALLET_DEDUCTION,
                description='Counted Strike Penalty for a Late Cancellation.',
                reference_id=f'LT-{ticket.id}',
            )

    ticket.status = 'Resolved'
    ticket.save(update_fields=['status', 'resolution_verdict', 'updated_at'])

    from studybuddy.chat.models import Message
    if ticket.chatroom:
        Message.objects.create(
            room=ticket.chatroom,
            sender=None,
            content='This support ticket has been marked as Resolved. The chat is now closed.',
        )

    return Response({
        'message': 'Ticket resolved',
        'status': 'Resolved',
        'resolution_verdict': ticket.resolution_verdict,
        'monthly_counted_strikes': get_monthly_counted_strike_count(ticket.penalized_user)
        if ticket.penalized_user else 0,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def tutor_application_status(request):
    try:
        application = TutorApplication.objects.get(profile=request.user.userprofile)
        serializer = TutorApplicationSerializer(application, context={'request': request})
        return Response(serializer.data)
    except TutorApplication.DoesNotExist:
        return Response({"error": "No application found for this user."}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def skip_tutor_onboarding_verification(request):
    profile = request.user.userprofile
    if profile.role != 'Tutor':
        return Response({"error": "Only tutors can skip tutor verification."}, status=403)

    profile.tutor_onboarding_skipped_at = timezone.now()
    profile.save(update_fields=['tutor_onboarding_skipped_at', 'updated_at'])
    return Response({
        "tutor_onboarding_skipped_at": profile.tutor_onboarding_skipped_at.isoformat(),
        "tutor_onboarding_complete": True,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def tutor_application_submit(request):
    profile = request.user.userprofile
    if profile.role != 'Tutor':
        return Response({"error": "Only tutors can submit tutor verification."}, status=403)
    if TutorApplication.objects.filter(profile=profile).exists():
        return Response(
            {"error": "A tutor application already exists."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    school_id = request.FILES.get('school_id')
    enrollment_proof = request.FILES.get('enrollment_proof')
    if not school_id or not enrollment_proof:
        return Response(
            {"error": "Please provide both your School ID and Proof of Enrollment."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if (
        school_id.size > settings.MAX_DOCUMENT_UPLOAD_SIZE
        or enrollment_proof.size > settings.MAX_DOCUMENT_UPLOAD_SIZE
    ):
        return Response(
            {
                "error": (
                    "Each uploaded file must be under 5 MB. "
                    "Please compress your images and try again."
                )
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    school_id = compress_if_image(school_id)
    enrollment_proof = compress_if_image(enrollment_proof)
    application = TutorApplication.objects.create(
        profile=profile,
        school_id=school_id,
        enrollment_proof=enrollment_proof,
        application_status='pending',
        submitted_at=timezone.now(),
    )
    Subjects.objects.filter(
        proposed_by_tutor__profile=profile,
        proposed_application__isnull=True,
        status='pending',
    ).update(proposed_application=application)

    def _send_confirmation():
        try:
            send_application_received_email(profile)
        except Exception:
            logger.exception(
                "Failed to send tutor application received email for profile_id=%s", profile.id
            )

    transaction.on_commit(_send_confirmation)
    return Response(
        TutorApplicationSerializer(application, context={'request': request}).data,
        status=status.HTTP_201_CREATED,
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def tutor_application_resubmit(request):
    try:
        application = TutorApplication.objects.select_for_update().get(profile=request.user.userprofile)
    except TutorApplication.DoesNotExist:
        return Response({"error": "No application found to resubmit."}, status=status.HTTP_404_NOT_FOUND)

    school_id = request.FILES.get('school_id')
    enrollment_proof = request.FILES.get('enrollment_proof')
    reason_to_tutor = request.data.get('reason_to_tutor', '')

    if not school_id or not enrollment_proof:
        return Response(
            {"error": "Please provide both your School ID and Proof of Enrollment to resubmit."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if (school_id.size > settings.MAX_DOCUMENT_UPLOAD_SIZE
            or enrollment_proof.size > settings.MAX_DOCUMENT_UPLOAD_SIZE):
        return Response(
            {"error": "Each uploaded file must be under 5 MB. Please compress your images and try again."},
            status=status.HTTP_400_BAD_REQUEST
        )

    school_id = compress_if_image(school_id)
    enrollment_proof = compress_if_image(enrollment_proof)

    if application.application_status == 'approved':
        return create_tutor_document_renewal_submission(
            request,
            application,
            school_id,
            enrollment_proof,
            reason_to_tutor,
        )

    if application.application_status != 'rejected':
        return Response(
            {"error": "Your application is still being processed. It cannot be resubmitted right now."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Update application
    application.school_id = school_id
    application.enrollment_proof = enrollment_proof
    application.application_status = 'pending'
    application.rejection_reason = ''
    application.reviewed_at = None
    application.reviewed_by = None
    application.save()

    # Log activity
    PlatformActivity.objects.create(
        activity_type='tutor_application',
        message=f"Tutor application resubmitted: {request.user.userprofile.fname} {request.user.userprofile.lname}",
        institution=request.user.userprofile.institution
    )

    # Optional: Send email confirmation
    try:
        send_application_received_email(request.user.userprofile)
    except Exception:
        logger.exception("Failed to send tutor application resubmission email for profile_id=%s", request.user.userprofile.id)

    return Response({"message": "Application resubmitted successfully. It is now back under review."})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def tutor_document_renewal_submit(request):
    try:
        application = TutorApplication.objects.select_for_update().get(profile=request.user.userprofile)
    except TutorApplication.DoesNotExist:
        return Response({"error": "No approved tutor application found."}, status=status.HTTP_404_NOT_FOUND)

    school_id = request.FILES.get('school_id')
    enrollment_proof = request.FILES.get('enrollment_proof')
    reason_to_tutor = request.data.get('reason_to_tutor', '')

    if not school_id or not enrollment_proof:
        return Response(
            {"error": "Please provide both your School ID and updated Enrollment/RF document."},
            status=status.HTTP_400_BAD_REQUEST
        )

    school_id = compress_if_image(school_id)
    enrollment_proof = compress_if_image(enrollment_proof)

    return create_tutor_document_renewal_submission(
        request,
        application,
        school_id,
        enrollment_proof,
        reason_to_tutor,
    )


def create_tutor_document_renewal_submission(request, application, school_id, enrollment_proof, reason_to_tutor):
    if application.application_status != 'approved':
        return Response(
            {"error": "Only approved tutors can submit recurring document renewals."},
            status=status.HTTP_400_BAD_REQUEST
        )

    renewal_status = application.document_renewal_status()
    if renewal_status == 'pending':
        return Response(
            {"error": "Your updated documents are already pending review."},
            status=status.HTTP_400_BAD_REQUEST
        )
    if renewal_status == 'verified':
        return Response(
            {"error": "Your enrollment documents are still current."},
            status=status.HTTP_400_BAD_REQUEST
        )

    renewal = TutorDocumentRenewalReview.objects.create(
        application=application,
        profile=request.user.userprofile,
        school_id=school_id,
        enrollment_proof=enrollment_proof,
        reason_to_tutor=reason_to_tutor,
        status='pending',
    )

    PlatformActivity.objects.create(
        activity_type='tutor_application',
        message=f"Tutor document renewal submitted: {request.user.userprofile.fname} {request.user.userprofile.lname}",
        institution=request.user.userprofile.institution
    )

    return Response({
        "message": "Updated documents submitted successfully. They are now under review.",
        "renewal_id": renewal.id,
        **get_tutor_document_review_context(request.user.userprofile),
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def tutee_application_status(request):
    try:
        application = TuteeApplication.objects.get(profile=request.user.userprofile)
        serializer = TuteeApplicationSerializer(application, context={'request': request})
        return Response(serializer.data)
    except TuteeApplication.DoesNotExist:
        return Response({"error": "No application found for this user."}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def tutee_application_resubmit(request):
    school_id = request.FILES.get('school_id')
    enrollment_proof = request.FILES.get('enrollment_proof')
    reason_to_tutor = request.data.get('reason_to_tutor', '')

    if not school_id or not enrollment_proof:
        return Response(
            {"error": "Please provide both your School ID and Proof of Enrollment to resubmit."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if (school_id.size > settings.MAX_DOCUMENT_UPLOAD_SIZE
            or enrollment_proof.size > settings.MAX_DOCUMENT_UPLOAD_SIZE):
        return Response(
            {"error": "Each uploaded file must be under 5 MB. Please compress your images and try again."},
            status=status.HTTP_400_BAD_REQUEST
        )

    school_id = compress_if_image(school_id)
    enrollment_proof = compress_if_image(enrollment_proof)

    # Unlike tutors (who submit documents at registration), tutees register free and submit
    # verification documents later — so this is also the first-time submission endpoint, not just
    # resubmission. See docs/plans/2026-07-01-tutee-verification-phase3-ui.md.
    application, created = TuteeApplication.objects.select_for_update().get_or_create(
        profile=request.user.userprofile,
        defaults={
            'school_id': school_id,
            'enrollment_proof': enrollment_proof,
            'application_status': 'pending',
        }
    )

    if created:
        PlatformActivity.objects.create(
            activity_type='tutee_application',
            message=f"Tutee application submitted: {request.user.userprofile.fname} {request.user.userprofile.lname}",
            institution=request.user.userprofile.institution
        )
        try:
            send_application_received_email(request.user.userprofile, role_label='tutee')
        except Exception:
            logger.exception(
                "Failed to send tutee application received email for profile_id=%s",
                request.user.userprofile.id,
            )
        return Response({"message": "Application submitted successfully. It is now under review."})

    if application.application_status == 'approved':
        return create_tutee_document_renewal_submission(
            request,
            application,
            school_id,
            enrollment_proof,
            reason_to_tutor,
        )

    if application.application_status != 'rejected':
        return Response(
            {"error": "Your application is still being processed. It cannot be resubmitted right now."},
            status=status.HTTP_400_BAD_REQUEST
        )

    application.school_id = school_id
    application.enrollment_proof = enrollment_proof
    application.application_status = 'pending'
    application.rejection_reason = ''
    application.reviewed_at = None
    application.reviewed_by = None
    application.save()

    PlatformActivity.objects.create(
        activity_type='tutee_application',
        message=f"Tutee application resubmitted: {request.user.userprofile.fname} {request.user.userprofile.lname}",
        institution=request.user.userprofile.institution
    )

    try:
        send_application_received_email(request.user.userprofile, role_label='tutee')
    except Exception:
        logger.exception(
            "Failed to send tutee application resubmission email for profile_id=%s",
            request.user.userprofile.id,
        )

    return Response({"message": "Application resubmitted successfully. It is now back under review."})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def tutee_document_renewal_submit(request):
    try:
        application = TuteeApplication.objects.select_for_update().get(profile=request.user.userprofile)
    except TuteeApplication.DoesNotExist:
        return Response({"error": "No approved tutee application found."}, status=status.HTTP_404_NOT_FOUND)

    school_id = request.FILES.get('school_id')
    enrollment_proof = request.FILES.get('enrollment_proof')
    reason_to_tutor = request.data.get('reason_to_tutor', '')

    if not school_id or not enrollment_proof:
        return Response(
            {"error": "Please provide both your School ID and updated Enrollment/RF document."},
            status=status.HTTP_400_BAD_REQUEST
        )

    school_id = compress_if_image(school_id)
    enrollment_proof = compress_if_image(enrollment_proof)

    return create_tutee_document_renewal_submission(
        request,
        application,
        school_id,
        enrollment_proof,
        reason_to_tutor,
    )


def create_tutee_document_renewal_submission(request, application, school_id, enrollment_proof, reason_to_tutor):
    if application.application_status != 'approved':
        return Response(
            {"error": "Only approved tutees can submit recurring document renewals."},
            status=status.HTTP_400_BAD_REQUEST
        )

    renewal_status = application.document_renewal_status()
    if renewal_status == 'pending':
        return Response(
            {"error": "Your updated documents are already pending review."},
            status=status.HTTP_400_BAD_REQUEST
        )
    if renewal_status == 'verified':
        return Response(
            {"error": "Your enrollment documents are still current."},
            status=status.HTTP_400_BAD_REQUEST
        )

    renewal = TuteeDocumentRenewalReview.objects.create(
        application=application,
        profile=request.user.userprofile,
        school_id=school_id,
        enrollment_proof=enrollment_proof,
        reason_to_tutor=reason_to_tutor,
        status='pending',
    )

    PlatformActivity.objects.create(
        activity_type='tutee_application',
        message=f"Tutee document renewal submitted: {request.user.userprofile.fname} {request.user.userprofile.lname}",
        institution=request.user.userprofile.institution
    )

    return Response({
        "message": "Updated documents submitted successfully. They are now under review.",
        "renewal_id": renewal.id,
        **get_document_review_context(application, 'tutee'),
    }, status=status.HTTP_201_CREATED)
