import logging
from datetime import timedelta

from django.db.models import Count
from django.utils import timezone

from ..models import TUTOR_ACCEPTED_SESSION_LOAD_STATUSES, Booking

logger = logging.getLogger(__name__)

UPCOMING_WEEK_DAYS = 7


def get_upcoming_week_loads(tutor_ids):
    """Upcoming Week Load for each of tutor_ids: the number of sessions the tutor
    has booked in the next UPCOMING_WEEK_DAYS days, Manila-local (settings.TIME_ZONE),
    counting today and excluding day 7.

    This is the Tie Breaker's ranking input (see
    docs/adr/0009-tie-breaker-upcoming-week-load.md) and is deliberately *not*
    Tutor.accepted_session_load(): that one has no date bound, so a session left at
    'Awaiting Payment Verification' counts as active load forever, and it collapses a
    multi-session package to one. Here each dated occurrence inside the window counts
    separately, because within a fixed week every session is real burden.

    Returns {tutor_profile_id: count} as a single grouped aggregate — one query for the
    whole candidate set, never one per tutor. Tutors with nothing booked in the window
    are absent from the map, so callers must default them to 0.
    """
    tutor_ids = list(tutor_ids)

    if not tutor_ids:
        return {}

    today = timezone.localdate()

    rows = (
        Booking.objects.filter(
            tutor_id__in=tutor_ids,
            status__in=TUTOR_ACCEPTED_SESSION_LOAD_STATUSES,
            session_date__gte=today,
            session_date__lt=today + timedelta(days=UPCOMING_WEEK_DAYS),
        )
        .values("tutor_id")
        .annotate(load=Count("id"))
    )

    loads = {row["tutor_id"]: row["load"] for row in rows}

    logger.debug(
        "Upcoming Week Load from %s for %s tutors: %s with sessions booked",
        today,
        len(tutor_ids),
        len(loads),
    )

    return loads
