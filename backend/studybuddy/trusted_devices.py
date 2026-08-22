"""Device trust for the login OTP.

A browser that has cleared the email OTP once is issued an opaque device token. Later logins
that present a live token skip the challenge entirely, so the OTP is a first-time-on-this-device
step rather than a per-login one. Trust expires on a sliding window
(``settings.TRUSTED_DEVICE_TTL_SECONDS``): every accepted login pushes the expiry forward, so an
actively used browser stays trusted and an abandoned one lapses back to a full challenge.

Only the HMAC of the issued secret is ever stored. The raw token exists in the login response and
in the client's storage, never in the database.
"""
import hashlib
import hmac
import secrets
from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.crypto import constant_time_compare

from .models import TrustedDevice

DEVICE_TOKEN_SEPARATOR = '.'
DEVICE_SECRET_BYTES = 32
USER_AGENT_MAX_LENGTH = 255


def hash_device_token(device_id, secret):
    """HMAC a device secret the same way login codes are hashed -- never store the raw secret."""
    message = f"device:{device_id}:{secret}".encode("utf-8")
    return hmac.new(
        settings.SECRET_KEY.encode("utf-8"),
        message,
        hashlib.sha256,
    ).hexdigest()


def get_trusted_device_expiry():
    return timezone.now() + timedelta(seconds=settings.TRUSTED_DEVICE_TTL_SECONDS)


def get_request_ip(request):
    forwarded = (request.META.get('HTTP_X_FORWARDED_FOR') or '').split(',')[0].strip()
    return forwarded or request.META.get('REMOTE_ADDR') or None


def split_device_token(raw_token):
    """Split a raw "<device_id>.<secret>" token, or return (None, None) if it is malformed."""
    device_id, separator, secret = str(raw_token or '').partition(DEVICE_TOKEN_SEPARATOR)
    if not separator or not device_id or not secret:
        return None, None
    return device_id, secret


def issue_trusted_device(user, request):
    """Create a trusted device for this browser and return the raw token to hand the client."""
    secret = secrets.token_urlsafe(DEVICE_SECRET_BYTES)
    device = TrustedDevice(
        user=user,
        expires_at=get_trusted_device_expiry(),
        user_agent=(request.META.get('HTTP_USER_AGENT') or '')[:USER_AGENT_MAX_LENGTH],
        last_ip=get_request_ip(request),
    )
    device.token_hash = hash_device_token(device.device_id, secret)
    device.save()

    return f"{device.device_id}{DEVICE_TOKEN_SEPARATOR}{secret}"


def consume_trusted_device(user, raw_token, request):
    """Return True if this token is a live trust for this user, sliding its expiry forward.

    Deliberately silent on failure: expired, revoked, forged, and someone else's token all fall
    through to the normal OTP challenge rather than telling the caller which one it was.
    """
    device_id, secret = split_device_token(raw_token)
    if device_id is None:
        return False

    try:
        device = TrustedDevice.objects.get(device_id=device_id, user=user)
    except (TrustedDevice.DoesNotExist, ValidationError, ValueError):
        return False

    if not device.is_active:
        return False

    if not constant_time_compare(device.token_hash, hash_device_token(device.device_id, secret)):
        return False

    device.expires_at = get_trusted_device_expiry()
    device.last_used_at = timezone.now()
    device.last_ip = get_request_ip(request)
    device.save(update_fields=['expires_at', 'last_used_at', 'last_ip'])

    return True


def revoke_trusted_devices(user, raw_token=None):
    """Revoke every live trust for a user, or just the one the raw token names."""
    devices = TrustedDevice.objects.filter(user=user, revoked_at__isnull=True)

    if raw_token is not None:
        device_id, _ = split_device_token(raw_token)
        if device_id is None:
            return 0
        devices = devices.filter(device_id=device_id)

    try:
        return devices.update(revoked_at=timezone.now())
    except (ValidationError, ValueError):
        # A malformed UUID in the filter -- nothing to revoke, and not worth a 500.
        return 0
