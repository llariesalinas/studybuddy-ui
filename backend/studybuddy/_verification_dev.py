"""Dev-only helpers for exercising enrollment verification without the real 90-day renewal clock or
admin approval.

Gating lives at the view layer (``settings.VERIFICATION_DEV_TOOLS_ENABLED``); this module performs
no gating itself. Shared by the self-service profile panel and the SuperAdmin verification dev tools
(Phase 4) so the state-manipulation logic exists once.

WARNING: ``set_verification_state`` is destructive — it overwrites and deletes the profile's real
application and renewal-review rows to land on an exact state. Dev/test use only.
"""

from datetime import timedelta

from django.core.cache import cache
from django.utils import timezone

from .models import (
    TutorApplication,
    TuteeApplication,
    TutorDocumentRenewalReview,
    TuteeDocumentRenewalReview,
)

# --- Enforcement override (cache-based, three-state) ---
#
# Value semantics: True/False = force that value; key absent (None) = defer to the env default in
# tutee_verification_enforced(). Consulted there only when VERIFICATION_DEV_TOOLS_ENABLED is on.

_ENFORCEMENT_OVERRIDE_KEY = "dev:tutee_verification_enforced"


def enforcement_override_get():
    """Return True/False when an override is set, or None to defer to the env default."""
    return cache.get(_ENFORCEMENT_OVERRIDE_KEY)


def enforcement_override_set(value):
    cache.set(_ENFORCEMENT_OVERRIDE_KEY, bool(value), None)


def enforcement_override_clear():
    cache.delete(_ENFORCEMENT_OVERRIDE_KEY)


# --- State setter ---

VERIFICATION_STATES = (
    "not_submitted",
    "initial_pending",
    "initial_rejected",
    "verified",
    "renewal_due",
    "renewal_pending",
    "renewal_rejected",
)

# role -> (Application model, DocumentRenewalReview model, profile related_name)
_MODELS_BY_ROLE = {
    "Tutor": (TutorApplication, TutorDocumentRenewalReview, "tutor_application"),
    "Tutee": (TuteeApplication, TuteeDocumentRenewalReview, "tutee_application"),
}


def role_has_verification(profile):
    return profile.role in _MODELS_BY_ROLE


def set_verification_state(profile, state):
    """Deterministically force ``profile``'s own application into exactly ``state``.

    Idempotent: wipes conflicting renewal-review rows and fabricates only the one the target state
    requires (synthetic rows use empty file fields, which is ORM-legal). ``not_submitted`` deletes
    the application entirely. Must run inside a transaction (caller wraps it).
    """
    models = _MODELS_BY_ROLE.get(profile.role)
    if models is None:
        raise ValueError(f"Verification does not apply to role {profile.role!r}")
    if state not in VERIFICATION_STATES:
        raise ValueError(f"Unknown verification state {state!r}")

    application_cls, review_cls, related_name = models

    if state == "not_submitted":
        app = getattr(profile, related_name, None)
        if app is not None:
            app.delete()  # cascades to renewal reviews
        return

    app = getattr(profile, related_name, None)
    if app is None:
        app = application_cls.objects.create(profile=profile)

    # Clean slate: drop all renewal reviews; re-create only what the target state needs.
    app.document_renewal_reviews.all().delete()
    now = timezone.now()
    interval = application_cls.DOCUMENT_RENEWAL_INTERVAL_DAYS

    if state == "initial_pending":
        app.application_status = "pending"
        app.reviewed_at = None
        app.rejection_reason = ""
    elif state == "initial_rejected":
        app.application_status = "rejected"
        app.reviewed_at = now
        app.rejection_reason = "Dev-set rejected state."
    elif state == "verified":
        # Fresh approval -> due_at is a full interval out -> document_renewal_status() == 'verified'.
        app.application_status = "approved"
        app.reviewed_at = now
        app.rejection_reason = ""
    elif state == "renewal_due":
        # Backdate the approval clock past the interval so document_renewal_status() == 'due'.
        app.application_status = "approved"
        app.reviewed_at = now - timedelta(days=interval + 1)
        app.rejection_reason = ""
    elif state == "renewal_pending":
        app.application_status = "approved"
        app.reviewed_at = now
        review_cls.objects.create(profile=profile, application=app, status="pending")
    elif state == "renewal_rejected":
        app.application_status = "approved"
        app.reviewed_at = now
        review_cls.objects.create(
            profile=profile,
            application=app,
            status="rejected",
            reviewed_at=now,
            rejection_reason="Dev-set renewal rejected state.",
        )

    # Clear reminder dedup so a demo can immediately re-trigger renewal reminders.
    app.reminder_7day_sent_at = None
    app.reminder_1day_sent_at = None
    app.save()
