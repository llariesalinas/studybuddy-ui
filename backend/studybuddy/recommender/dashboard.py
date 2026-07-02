import logging
import time

from django.core.cache import cache

from ..models import Tutor
from .cbf import get_student_subject_codes
from .CF import build_rating_matrix
from .hybrid import recommend_tutors_hybrid
from .utils import filter_tutors_by_institution

logger = logging.getLogger(__name__)

CACHE_TTL_SECONDS = 600
DEFAULT_LIMIT = 5
DEFAULT_CACHE_VERSION = 2
VERSION_CACHE_KEY = "dash_recs:version"


def _cache_get(key):
    try:
        return cache.get(key)
    except Exception:
        logger.warning("Dashboard recs cache read failed", exc_info=True)
        return None


def _cache_set(key, value, timeout=CACHE_TTL_SECONDS):
    try:
        cache.set(key, value, timeout)
    except Exception:
        logger.warning("Dashboard recs cache write failed", exc_info=True)


def _dashboard_recs_cache_version():
    version = _cache_get(VERSION_CACHE_KEY)

    if version is None:
        return DEFAULT_CACHE_VERSION

    try:
        return int(version)
    except (TypeError, ValueError):
        logger.warning("Invalid dashboard recs cache version %r", version)
        return DEFAULT_CACHE_VERSION


def bump_dashboard_recs_cache_version():
    try:
        if cache.get(VERSION_CACHE_KEY) is None:
            cache.set(VERSION_CACHE_KEY, DEFAULT_CACHE_VERSION + 1, None)
            return

        cache.incr(VERSION_CACHE_KEY)
    except Exception:
        logger.warning("Dashboard recs cache version bump failed", exc_info=True)
        _cache_set(VERSION_CACHE_KEY, int(time.time()), None)


def dashboard_recs_cache_key(tutee, limit=DEFAULT_LIMIT):
    version = _dashboard_recs_cache_version()
    return f"dash_recs:v{version}:limit{limit}:{tutee.id}"


def _serialize(tutor):
    return {
        "id": tutor.profile.id,
        "name": f"{tutor.profile.fname} {tutor.profile.lname}",
        "rating": tutor.rating_average,
        "subjects": [ts.subject.subject_name for ts in tutor.tutorsubjects_set.all()],
        "hourlyRate": tutor.hourly_rate,
    }


def _fallback(tutee, limit):
    qs = filter_tutors_by_institution(
        Tutor.objects.select_related("profile").prefetch_related("tutorsubjects_set__subject"),
        tutee,
    )
    return [_serialize(tutor) for tutor in qs[:limit]]


def _limit_rows(rows, limit):
    if not isinstance(rows, list):
        logger.warning("Dashboard recs cache payload had unexpected type %s", type(rows).__name__)
        return []

    return rows[:limit]


def get_dashboard_recommendations(tutee, limit=DEFAULT_LIMIT):
    key = dashboard_recs_cache_key(tutee, limit=limit)

    cached = _cache_get(key)
    if cached is not None:
        rows = _limit_rows(cached, limit)
        logger.info(
            "Dashboard recs cache hit for tutee %s: returned %s",
            tutee.id,
            len(rows),
        )
        return rows

    started_at = time.perf_counter()

    subject_codes = get_student_subject_codes(tutee)
    if not subject_codes:
        data = _fallback(tutee, limit)
        _cache_set(key, data)
        logger.info(
            "Dashboard recs fallback for tutee %s: returned %s in %.3fs",
            tutee.id,
            len(data),
            time.perf_counter() - started_at,
        )
        return data

    candidate_qs = filter_tutors_by_institution(
        Tutor.objects.filter(
            tutorsubjects__subject__subject_code__in=subject_codes
        ).distinct(),
        tutee,
    )

    ratings = build_rating_matrix()
    ranked = recommend_tutors_hybrid(
        ratings,
        tutee,
        None,
        candidate_qs=candidate_qs,
    )

    data = [_serialize(recommendation["tutor"]) for recommendation in ranked[:limit]]

    _cache_set(key, data)
    logger.info(
        "Dashboard recs cache miss for tutee %s: scored %s, returned %s in %.3fs",
        tutee.id,
        len(ranked),
        len(data),
        time.perf_counter() - started_at,
    )
    return data
