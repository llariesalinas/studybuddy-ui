from django.core.mail import get_connection, send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def _get_smtp_connection():
    """
    Returns an SMTP email connection if SMTP credentials are configured in settings/env,
    otherwise returns None (falling back to Django's default configured backend, e.g. console).
    """
    if (not getattr(settings, 'EMAIL_HOST', None) or
        not getattr(settings, 'EMAIL_HOST_USER', None) or
        not getattr(settings, 'EMAIL_HOST_PASSWORD', None) or
        settings.EMAIL_HOST_PASSWORD == 'your-gmail-app-password' or
        settings.EMAIL_HOST_USER == ''):
        return None
    try:
        return get_connection(
            backend='django.core.mail.backends.smtp.EmailBackend',
            host=settings.EMAIL_HOST,
            port=settings.EMAIL_PORT,
            username=settings.EMAIL_HOST_USER,
            password=settings.EMAIL_HOST_PASSWORD,
            use_tls=settings.EMAIL_USE_TLS,
            use_ssl=settings.EMAIL_USE_SSL,
            timeout=settings.EMAIL_TIMEOUT
        )
    except Exception:
        logger.exception("Failed to initialize dedicated SMTP connection for tutor screening")
        return None

def send_application_received_email(profile):
    subject = "Your StudyBuddy Tutor Application"
    message = (
        f"Hi {profile.fname},\n\n"
        "Thank you for applying to be a tutor on StudyBuddy! We have received your application and documents.\n\n"
        "Our team will review your submission within 1-3 business days. You will receive an email once a decision has been made.\n\n"
        "If you have any questions, feel free to contact us at StudyBuddySupport@gmail.com.\n\n"
        "Best regards,\n"
        "The StudyBuddy Team"
    )
    try:
        connection = _get_smtp_connection()
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [profile.user.email],
            connection=connection,
            fail_silently=False,
        )
        logger.info("Sent application received email to %s (using connection: %s)", profile.user.email, connection)
    except Exception:
        logger.exception("Failed to send application received email to %s", profile.user.email)

def send_application_approved_email(profile):
    subject = "Congratulations! Your StudyBuddy Tutor Application was Approved"
    login_url = f"{settings.FRONTEND_URL.rstrip('/')}/login"
    message = (
        f"Hi {profile.fname},\n\n"
        "Great news! Your application to become a tutor on StudyBuddy has been approved.\n\n"
        "You can now log in to the platform and complete your tutor profile setup:\n"
        f"{login_url}\n\n"
        "Welcome to the team!\n\n"
        "Best regards,\n"
        "The StudyBuddy Team"
    )
    try:
        connection = _get_smtp_connection()
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [profile.user.email],
            connection=connection,
            fail_silently=False,
        )
        logger.info("Sent application approved email to %s (using connection: %s)", profile.user.email, connection)
    except Exception:
        logger.exception("Failed to send application approved email to %s", profile.user.email)

def send_application_rejected_email(profile, reason):
    subject = "Update regarding your StudyBuddy Tutor Application"
    status_url = f"{settings.FRONTEND_URL.rstrip('/')}/application-status"
    message = (
        f"Hi {profile.fname},\n\n"
        "Thank you for your interest in becoming a tutor on StudyBuddy.\n\n"
        "After reviewing your application, we are unable to approve it at this time for the following reason:\n"
        f"\"{reason}\"\n\n"
        "Don't worry—rejection is not permanent. You can re-apply by logging in and resubmitting your documents with the necessary corrections here:\n"
        f"{status_url}\n\n"
        "If you have any questions, please reach out to StudyBuddySupport@gmail.com.\n\n"
        "Best regards,\n"
        "The StudyBuddy Team"
    )
    try:
        connection = _get_smtp_connection()
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [profile.user.email],
            connection=connection,
            fail_silently=False,
        )
        logger.info("Sent application rejected email to %s (using connection: %s)", profile.user.email, connection)
    except Exception:
        logger.exception("Failed to send application rejected email to %s", profile.user.email)

