"""Session display-status and dev-live-override logic shared by views and chat.

Pulled out of views.py so chat/services.py can compute the same Upcoming / Ongoing /
Payment Required status (and honor the same dev "force live" override) that the booking
screens use, without creating an import cycle -- views.py imports chat.services at module
level, so chat.services cannot import views.py back.

Does NOT handle: request/response plumbing, or persisting anything. Callers pass in bookings
and times; these functions return strings and dicts.
"""

from datetime import datetime, timedelta

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

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

    # Callers (get_session_group_bookings, get_booking_request_bookings, chat's sort_bookings)
    # already hand these in ordered; every booking in one group shares the same cache key, so
    # iteration order can't change which override is found.
    for booking in bookings:
        for key in get_dev_live_cache_keys_for_booking(booking):
            override = cache.get(key)
            if override:
                return override

    return None


def set_dev_live_override_for_bookings(bookings, override):
    # No sort needed here either -- see the comment in get_dev_live_override_for_bookings above.
    # This builds a set of every key across the group and writes all of them, so order plays no
    # part at all.
    keys = {
        key
        for booking in bookings
        for key in get_dev_live_cache_keys_for_booking(booking)
    }

    for key in keys:
        cache.set(key, override, DEV_LIVE_CACHE_TIMEOUT_SECONDS)


def clear_dev_live_override_for_bookings(bookings):
    # No sort needed here either -- see the comment in get_dev_live_override_for_bookings above.
    # This deletes every key unconditionally, so order can't affect the outcome.
    for booking in bookings:
        for key in get_dev_live_cache_keys_for_booking(booking):
            cache.delete(key)


def build_dev_live_override(phase):
    offsets = DEV_LIVE_PHASES[phase]
    current_time = timezone.localtime(timezone.now()).replace(second=0, microsecond=0)
    start_at = current_time + timedelta(minutes=offsets[0])
    end_at = current_time + timedelta(minutes=offsets[1])

    # start_at/end_at can land on different calendar dates (e.g. 'ending' is (-55, +5) minutes,
    # which crosses backward over midnight whenever `current_time` is within 55 minutes past
    # midnight). Both dates are stored explicitly -- collapsing to a single shared date silently
    # produced an inverted (empty) Ongoing window whenever the two datetimes fell on different
    # days, which get_display_status can't distinguish from "never started".
    return {
        "phase": phase,
        "date": start_at.date().isoformat(),
        "start_time": start_at.time().strftime("%H:%M"),
        "end_date": end_at.date().isoformat(),
        "end_time": end_at.time().strftime("%H:%M"),
        "forced_at": current_time.isoformat(),
    }


def apply_dev_live_override(bookings, session_date, start_time, end_time):
    override = get_dev_live_override_for_bookings(bookings)

    if not override:
        return session_date, start_time, session_date, end_time

    return (
        datetime.strptime(override["date"], "%Y-%m-%d").date(),
        datetime.strptime(override["start_time"], "%H:%M").time(),
        # .get() with a fallback to the start date keeps any override already sitting in cache
        # (6-hour TTL) from a pre-fix write from raising a KeyError after this deploy.
        datetime.strptime(override.get("end_date", override["date"]), "%Y-%m-%d").date(),
        datetime.strptime(override["end_time"], "%H:%M").time(),
    )


def get_display_status(raw_status, start_date, start_time, end_date, end_time):
    normalized = str(raw_status or '').lower()

    if normalized == 'confirmed':
        timezone_now = timezone.localtime()
        timezone_info = timezone.get_current_timezone()
        start_at = timezone.make_aware(datetime.combine(start_date, start_time), timezone_info)
        end_at = timezone.make_aware(datetime.combine(end_date, end_time), timezone_info)

        if timezone_now < start_at:
            return 'Upcoming'

        if start_at <= timezone_now < end_at:
            return 'Ongoing'

        return 'Payment Required'

    if normalized == 'awaiting payment verification':
        return 'Awaiting Verification'

    return raw_status


def apply_dev_confirmed_gate(display_status, has_dev_live_override, booking_status, tutor_confirmed):
    """Dev-tools-only guard: once dev tools are enabled, a Confirmed booking the tutor has
    marked attended reads "Payment Required" regardless of the clock, as soon as no live
    override is active -- so clearing an override on such a booking always lands here rather
    than back on a stale "Upcoming". Was duplicated identically at two call sites in views.py
    (build_combined_block, build_booking_detail_payload) before this extraction; chat is a
    third caller.
    """
    if (
        settings.BOOKING_DEV_TOOLS_ENABLED
        and not has_dev_live_override
        and booking_status == "Confirmed"
        and tutor_confirmed
    ):
        return "Payment Required"

    return display_status
