"""Central email service for StudyBuddy.

All outbound mail routes through here so that retries, logging, the per-recipient
send cap, and template rendering live in one place. Two paths exist:

* Synchronous + hardened (login OTP): the user is waiting for the code, so it is
  sent in-request with a short timeout and a couple of retries, and raises on
  final failure so the caller can return an honest error.
* Asynchronous (password reset / changed notice): dispatched to Django-Q2 via
  ``async_task`` and delivered off the request thread by the ``qcluster`` worker,
  which also handles task-level retries.

Note: this module is deliberately named ``mailer`` (not ``email``) so it cannot
shadow Python's stdlib ``email`` package that Django's mail internals import.
"""
import logging
import time
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from django_q.tasks import async_task

from .models import EmailSendLog

logger = logging.getLogger(__name__)


class EmailRateLimitError(Exception):
    """Raised when a recipient has exceeded the hourly send cap for capped mail."""


def _recipient_for(user):
    return user.email or user.username


def recent_sent_count(recipient):
    """Number of successfully-sent emails to ``recipient`` in the last hour.

    Only ``sent`` rows count, so transient failures + retries never push a
    legitimate user over the cap.
    """
    window_start = timezone.now() - timedelta(hours=1)
    return EmailSendLog.objects.filter(
        recipient=recipient,
        status=EmailSendLog.STATUS_SENT,
        created_at__gte=window_start,
    ).count()


def is_send_allowed(recipient):
    return recent_sent_count(recipient) < settings.EMAIL_SEND_CAP_PER_HOUR


def _render(template_base, context):
    """Render the paired ``email/<base>.txt`` and ``email/<base>.html`` templates."""
    text_body = render_to_string(f"email/{template_base}.txt", context)
    html_body = render_to_string(f"email/{template_base}.html", context)
    return text_body, html_body


def _deliver(*, subject, text_body, html_body, recipient, purpose, timeout, max_attempts):
    """Send one multipart email, retrying transient failures up to ``max_attempts``.

    Writes exactly one ``EmailSendLog`` row for the final outcome of the call
    (sent on success, failed on the last exhausted attempt). Re-raises on final
    failure so callers (sync OTP) or the worker (async tasks) can react.
    """
    for attempt in range(1, max_attempts + 1):
        try:
            message = EmailMultiAlternatives(
                subject=subject,
                body=text_body,
                from_email=None,  # falls back to DEFAULT_FROM_EMAIL
                to=[recipient],
                connection=get_connection(timeout=timeout),
            )
            message.attach_alternative(html_body, "text/html")
            message.send()
        except Exception as exc:
            if attempt < max_attempts:
                time.sleep(settings.EMAIL_SEND_RETRY_BACKOFF * attempt)
                continue
            EmailSendLog.objects.create(
                recipient=recipient,
                purpose=purpose,
                status=EmailSendLog.STATUS_FAILED,
                error=str(exc)[:2000],
            )
            logger.exception(
                "Email send failed purpose=%s recipient=%s", purpose, recipient
            )
            raise
        else:
            EmailSendLog.objects.create(
                recipient=recipient,
                purpose=purpose,
                status=EmailSendLog.STATUS_SENT,
            )
            return


def _password_reset_url(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    return f"{settings.FRONTEND_URL.rstrip('/')}/reset-password/{uid}/{token}"


# --- Synchronous: login OTP (critical path) -------------------------------

def send_login_otp(user, code):
    """Send the login OTP synchronously. Raises EmailRateLimitError if capped,
    or the underlying exception if delivery fails after retries."""
    recipient = _recipient_for(user)
    if not is_send_allowed(recipient):
        raise EmailRateLimitError(recipient)

    ttl_minutes = max(1, settings.LOGIN_OTP_TTL_SECONDS // 60)
    text_body, html_body = _render("login_otp", {"code": code, "ttl_minutes": ttl_minutes})
    _deliver(
        subject="Your StudyBuddy login code",
        text_body=text_body,
        html_body=html_body,
        recipient=recipient,
        purpose=EmailSendLog.PURPOSE_LOGIN_OTP,
        timeout=settings.EMAIL_SYNC_TIMEOUT,
        max_attempts=settings.EMAIL_SYNC_MAX_ATTEMPTS,
    )


# --- Asynchronous task targets (run inside the qcluster worker) -----------
# These take serializable args (user_id) and re-fetch the user. max_attempts=1
# here because Django-Q2 owns task-level retries (see Q_CLUSTER).

def send_password_reset_email_task(user_id):
    user = User.objects.get(pk=user_id)
    text_body, html_body = _render(
        "password_reset", {"reset_url": _password_reset_url(user)}
    )
    _deliver(
        subject="Reset your StudyBuddy password",
        text_body=text_body,
        html_body=html_body,
        recipient=_recipient_for(user),
        purpose=EmailSendLog.PURPOSE_PASSWORD_RESET,
        timeout=settings.EMAIL_TIMEOUT,
        max_attempts=1,
    )


def send_password_changed_email_task(user_id):
    user = User.objects.get(pk=user_id)
    text_body, html_body = _render("password_changed", {})
    _deliver(
        subject="Your StudyBuddy password was changed",
        text_body=text_body,
        html_body=html_body,
        recipient=_recipient_for(user),
        purpose=EmailSendLog.PURPOSE_PASSWORD_CHANGED,
        timeout=settings.EMAIL_TIMEOUT,
        max_attempts=1,
    )


def send_document_renewal_reminder_email_task(user_id, role_label, days_remaining, due_at_iso):
    user = User.objects.get(pk=user_id)
    status_url = f"{settings.FRONTEND_URL.rstrip('/')}/application-status"
    text_body, html_body = _render(
        "document_renewal_reminder",
        {"days_remaining": days_remaining, "due_at": due_at_iso, "status_url": status_url},
    )
    _deliver(
        subject=f"Your StudyBuddy {role_label.capitalize()} verification renewal is due soon",
        text_body=text_body,
        html_body=html_body,
        recipient=_recipient_for(user),
        purpose=EmailSendLog.PURPOSE_DOCUMENT_RENEWAL_REMINDER,
        timeout=settings.EMAIL_TIMEOUT,
        max_attempts=1,
    )


# --- Enqueue helpers (called from views) ----------------------------------

def enqueue_password_reset(user):
    """Queue a password-reset email. Suppressed (not queued) if the recipient is
    over the send cap; password-reset is an abuse vector, so the cap applies."""
    recipient = _recipient_for(user)
    if not is_send_allowed(recipient):
        logger.warning("Password reset email suppressed by send cap for recipient=%s", recipient)
        return
    async_task("studybuddy.mailer.send_password_reset_email_task", user.id)


def enqueue_password_changed(user):
    """Queue a password-changed security notice. Not capped: users should always
    be told their password changed."""
    async_task("studybuddy.mailer.send_password_changed_email_task", user.id)


def enqueue_document_renewal_reminder(profile, role_label, days_remaining, due_at):
    """Queue a renewal-due reminder. Not capped: this is a one-per-window event driven by the
    caller's own dedup fields (reminder_7day_sent_at/reminder_1day_sent_at), not user-triggerable
    spam — same reasoning as enqueue_password_changed."""
    async_task(
        "studybuddy.mailer.send_document_renewal_reminder_email_task",
        profile.user.id,
        role_label,
        days_remaining,
        due_at.isoformat(),
    )
