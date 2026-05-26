import logging

from ..models import Tutor
from .CF import compute_cf_score
from .cbf import compute_cbf_score, get_student_subject_codes

logger = logging.getLogger(__name__)


def hybrid_prediction(ratings, student_profile, tutor, requested_subject, student_subjects=None):
    cbf_score = compute_cbf_score(
        student_profile,
        tutor,
        requested_subject,
        student_subjects=student_subjects,
        tutor_subjects=tutor.tutorsubjects_set.all(),
    )

    tutor_id = tutor.profile_id

    cf_score = compute_cf_score(
        ratings,
        student_profile.id,
        tutor_id,
    )

    if cf_score is None:
        cf_score = 0

    hybrid_score = (0.7 * cbf_score) + (0.3 * (cf_score / 5))

    logger.debug(
        "Hybrid score for tutor %s: CBF %.3f, CF %.3f, hybrid %.3f",
        tutor_id,
        cbf_score,
        cf_score,
        hybrid_score,
    )

    return hybrid_score


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
    recommendations = []

    for tutor in tutors:
        score = hybrid_prediction(
            ratings,
            student_profile,
            tutor,
            requested_subject,
            student_subjects=student_subjects,
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
