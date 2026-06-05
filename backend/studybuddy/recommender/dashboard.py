import logging

from django.core.cache import cache

from ..models import Tutor
from .cbf import get_student_subject_codes
from .CF import build_rating_matrix
from .hybrid import recommend_tutors_hybrid

logger = logging.getLogger(__name__)

CACHE_TTL_SECONDS = 600
DEFAULT_LIMIT = 10


def dashboard_recs_cache_key(tutee):
    return f"dash_recs:{tutee.id}"


def _serialize(tutor):
    return {
        "id": tutor.profile.id,
        "name": f"{tutor.profile.fname} {tutor.profile.lname}",
        "rating": tutor.rating_average,
        "subjects": [ts.subject.subject_name for ts in tutor.tutorsubjects_set.all()],
        "hourlyRate": tutor.hourly_rate,
    }


def _fallback(limit):
    tutors = (
        Tutor.objects.select_related("profile")
        .prefetch_related("tutorsubjects_set__subject")[:limit]
    )
    return [_serialize(tutor) for tutor in tutors]


def _cache_get(key):
    try:
        return cache.get(key)
    except Exception:
        logger.warning("Dashboard recs cache read failed", exc_info=True)
        return None


def _cache_set(key, value):
    try:
        cache.set(key, value, CACHE_TTL_SECONDS)
    except Exception:
        logger.warning("Dashboard recs cache write failed", exc_info=True)


def get_dashboard_recommendations(tutee, limit=DEFAULT_LIMIT):
    key = dashboard_recs_cache_key(tutee)

    cached = _cache_get(key)
    if cached is not None:
        return cached

    subject_codes = get_student_subject_codes(tutee)
    if not subject_codes:
        return _fallback(limit)

    candidate_qs = Tutor.objects.filter(
        tutorsubjects__subject__subject_code__in=subject_codes
    ).distinct()

    ratings = build_rating_matrix()
    ranked = recommend_tutors_hybrid(
        ratings,
        tutee,
        None,
        candidate_qs=candidate_qs,
    )

    data = [_serialize(recommendation["tutor"]) for recommendation in ranked[:limit]]

    _cache_set(key, data)
    return data
