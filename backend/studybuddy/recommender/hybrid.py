import logging

from ..models import Tutor
from .CF import compute_cf_breakdown, compute_cf_score, top_k
from .cbf import (
    compute_cbf_breakdown,
    compute_cbf_score,
    get_student_subject_codes,
    resolve_target_categories,
)

logger = logging.getLogger(__name__)

CBF_WEIGHT = 0.7
CF_WEIGHT = 0.3
CF_MAX_RATING = 5


def hybrid_prediction(
    ratings,
    student_profile,
    tutor,
    requested_subject,
    student_subjects=None,
    neighbors=None,
    target_categories=None,
):
    """target_categories should be precomputed once via
    cbf.resolve_target_categories() by callers that loop over many tutors for
    the same student/subject (see recommend_tutors_hybrid) so this isn't a
    per-tutor query; left as None it is resolved here instead."""
    if target_categories is None:
        target_categories = resolve_target_categories(
            requested_subject, student_subjects or get_student_subject_codes(student_profile)
        )

    cbf_score = compute_cbf_score(
        student_profile,
        tutor,
        requested_subject,
        student_subjects=student_subjects,
        tutor_subjects=tutor.tutorsubjects_set.all(),
        target_categories=target_categories,
    )

    tutor_id = tutor.profile_id

    cf_score = compute_cf_score(
        ratings,
        student_profile.id,
        tutor_id,
        neighbors=neighbors,
    )

    if cf_score is None:
        cf_score = 0

    hybrid_score = (CBF_WEIGHT * cbf_score) + (CF_WEIGHT * (cf_score / CF_MAX_RATING))

    logger.debug(
        "Hybrid score for tutor %s: CBF %.3f, CF %.3f, hybrid %.3f",
        tutor_id,
        cbf_score,
        cf_score,
        hybrid_score,
    )

    return hybrid_score


def hybrid_prediction_breakdown(
    ratings,
    student_profile,
    tutor,
    requested_subject,
    student_subjects=None,
    neighbors=None,
    target_categories=None,
):
    """Same computation as hybrid_prediction, but returns the full CBF/CF breakdown
    alongside the hybrid score. Used by the algorithm demo tool (recommender/demo.py).
    See hybrid_prediction for the target_categories precompute-once contract."""
    if target_categories is None:
        target_categories = resolve_target_categories(
            requested_subject, student_subjects or get_student_subject_codes(student_profile)
        )

    cbf = compute_cbf_breakdown(
        student_profile,
        tutor,
        requested_subject,
        student_subjects=student_subjects,
        tutor_subjects=tutor.tutorsubjects_set.all(),
        target_categories=target_categories,
    )

    tutor_id = tutor.profile_id

    cf = compute_cf_breakdown(
        ratings,
        student_profile.id,
        tutor_id,
        neighbors=neighbors,
    )

    cf_score_for_hybrid = cf["score"] if cf["score"] is not None else 0
    hybrid_score = (CBF_WEIGHT * cbf["score"]) + (CF_WEIGHT * (cf_score_for_hybrid / CF_MAX_RATING))

    return {
        "hybrid_score": hybrid_score,
        "cbf": cbf,
        "cf": cf,
    }


def normalize_tutor_queryset(candidate_qs=None):
    if candidate_qs is None:
        return Tutor.objects.select_related(
            "profile",
            "profile__course",
            "profile__course__strand",
        ).prefetch_related("tutorsubjects_set__subject")

    if hasattr(candidate_qs, "select_related"):
        return candidate_qs.select_related(
            "profile",
            "profile__course",
            "profile__course__strand",
        ).prefetch_related("tutorsubjects_set__subject")

    return candidate_qs


def recommend_tutors_hybrid(ratings, student_profile, requested_subject, candidate_qs=None):
    tutors = normalize_tutor_queryset(candidate_qs)
    student_subjects = get_student_subject_codes(student_profile)
    target_categories = resolve_target_categories(requested_subject, student_subjects)

    student_id = student_profile.id
    neighbors = top_k(ratings, student_id) if student_id in ratings else []

    recommendations = []

    for tutor in tutors:
        score = hybrid_prediction(
            ratings,
            student_profile,
            tutor,
            requested_subject,
            student_subjects=student_subjects,
            neighbors=neighbors,
            target_categories=target_categories,
        )

        recommendations.append({
            "tutor": tutor,
            "score": score,
        })

    recommendations.sort(
        key=lambda x: x["score"],
        reverse=True,
    )

    for index, recommendation in enumerate(recommendations[:10], start=1):
        tutor = recommendation["tutor"]
        logger.debug(
            "Hybrid ranking %s: tutor %s, score %.3f",
            index,
            tutor.profile_id,
            recommendation["score"],
        )

    return recommendations
