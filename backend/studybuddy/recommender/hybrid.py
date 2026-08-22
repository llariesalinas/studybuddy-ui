import logging

from ..models import Tutor
from .CF import (
    compute_cf_breakdown_with_fallback,
    compute_cf_score_with_fallback,
    get_peer_student_ids,
    top_k,
)
from .cbf import (
    compute_cbf_breakdown,
    compute_cbf_score,
    get_student_subject_codes,
    resolve_target_categories,
)
from .weights import DEFAULT_WEIGHTS, GROUP_CBF, GROUP_HYBRID, default_weights, load_weights
from .workload import get_upcoming_week_loads

logger = logging.getLogger(__name__)

# Shipped defaults, aliased from weights.py so there is one source of truth.
# Admin overrides arrive per-call via the `weights` argument; see
# docs/plans/2026-08-19-dynamic-algorithm-weights.md.
CBF_WEIGHT = DEFAULT_WEIGHTS[GROUP_HYBRID]['cbf']
CF_WEIGHT = DEFAULT_WEIGHTS[GROUP_HYBRID]['cf']

# Not admin-editable: this is the rating scale itself, and changing it would
# rescale every CF score rather than reweight it.
CF_MAX_RATING = 5

# Two hybrid scores are "the same" when they agree to this many decimals — the same
# precision the recommendation API returns, so a tie to the algorithm is also a tie
# on screen. Quantizing rather than comparing within an epsilon band is deliberate:
# a band is not transitive (A ties B, B ties C, A does not tie C), which leaves the
# sort ill-defined. See docs/adr/0009-tie-breaker-upcoming-week-load.md.
HYBRID_SCORE_PRECISION = 3


def hybrid_prediction(
    ratings,
    student_profile,
    tutor,
    requested_subject,
    student_subjects=None,
    peer_neighbors=None,
    global_neighbors=None,
    target_categories=None,
    weights=None,
):
    """target_categories should be precomputed once via
    cbf.resolve_target_categories() by callers that loop over many tutors for
    the same student/subject (see recommend_tutors_hybrid) so this isn't a
    per-tutor query; left as None it is resolved here instead.

    weights follows the same contract: load_weights() hits the database, so
    callers looping over tutors must load once and pass the result in."""
    if weights is None:
        weights = default_weights()

    if target_categories is None:
        target_categories = resolve_target_categories(
            requested_subject, student_subjects or get_student_subject_codes(student_profile)
        )

    if peer_neighbors is None:
        peer_neighbors = []
    if global_neighbors is None:
        global_neighbors = (
            top_k(ratings, student_profile.id) if student_profile.id in ratings else []
        )

    cbf_score = compute_cbf_score(
        student_profile,
        tutor,
        requested_subject,
        student_subjects=student_subjects,
        tutor_subjects=tutor.tutorsubjects_set.all(),
        target_categories=target_categories,
        weights=weights[GROUP_CBF],
    )

    tutor_id = tutor.profile_id

    cf_score = compute_cf_score_with_fallback(
        ratings,
        student_profile.id,
        tutor_id,
        peer_neighbors,
        global_neighbors,
    )

    if cf_score is None:
        cf_score = 0

    blend = weights[GROUP_HYBRID]
    hybrid_score = (blend['cbf'] * cbf_score) + (blend['cf'] * (cf_score / CF_MAX_RATING))

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
    peer_neighbors=None,
    global_neighbors=None,
    target_categories=None,
    weights=None,
):
    """Same computation as hybrid_prediction, but returns the full CBF/CF breakdown
    alongside the hybrid score. Used by the algorithm demo tool (recommender/demo.py).
    See hybrid_prediction for the target_categories and weights
    precompute-once contract."""
    if weights is None:
        weights = default_weights()

    if target_categories is None:
        target_categories = resolve_target_categories(
            requested_subject, student_subjects or get_student_subject_codes(student_profile)
        )

    if peer_neighbors is None:
        peer_neighbors = []
    if global_neighbors is None:
        global_neighbors = (
            top_k(ratings, student_profile.id) if student_profile.id in ratings else []
        )

    cbf = compute_cbf_breakdown(
        student_profile,
        tutor,
        requested_subject,
        student_subjects=student_subjects,
        tutor_subjects=tutor.tutorsubjects_set.all(),
        target_categories=target_categories,
        weights=weights[GROUP_CBF],
    )

    tutor_id = tutor.profile_id

    cf = compute_cf_breakdown_with_fallback(
        ratings,
        student_profile.id,
        tutor_id,
        peer_neighbors,
        global_neighbors,
    )

    cf_score_for_hybrid = cf["score"] if cf["score"] is not None else 0
    blend = weights[GROUP_HYBRID]
    hybrid_score = (blend['cbf'] * cbf["score"]) + (
        blend['cf'] * (cf_score_for_hybrid / CF_MAX_RATING)
    )

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


def recommend_tutors_hybrid(
    ratings, student_profile, requested_subject, candidate_qs=None, weights=None
):
    tutors = normalize_tutor_queryset(candidate_qs)
    student_subjects = get_student_subject_codes(student_profile)
    target_categories = resolve_target_categories(requested_subject, student_subjects)

    # Loaded once here, not inside the loop below: load_weights() is a query, and
    # this function scores every candidate tutor.
    if weights is None:
        weights = load_weights()

    student_id = student_profile.id
    peer_ids = get_peer_student_ids(ratings, student_profile) if student_id in ratings else []
    peer_neighbors = top_k(ratings, student_id, candidate_ids=peer_ids) if student_id in ratings else []
    global_neighbors = top_k(ratings, student_id) if student_id in ratings else []

    recommendations = []

    for tutor in tutors:
        score = hybrid_prediction(
            ratings,
            student_profile,
            tutor,
            requested_subject,
            student_subjects=student_subjects,
            peer_neighbors=peer_neighbors,
            global_neighbors=global_neighbors,
            target_categories=target_categories,
            weights=weights,
        )

        recommendations.append({
            "tutor": tutor,
            "score": score,
        })

    loads = get_upcoming_week_loads(
        [recommendation["tutor"].profile_id for recommendation in recommendations]
    )

    for recommendation in recommendations:
        recommendation["upcoming_week_load"] = loads.get(
            recommendation["tutor"].profile_id, 0
        )

    # Tie Breaker: tutors whose scores agree to HYBRID_SCORE_PRECISION are equally
    # good matches, so the one with fewer sessions booked in the coming week ranks
    # higher. profile_id is the final key so an equal-score/equal-load group still
    # has one defined order rather than whatever the database returned.
    recommendations.sort(
        key=lambda x: (
            -round(x["score"], HYBRID_SCORE_PRECISION),
            x["upcoming_week_load"],
            x["tutor"].profile_id,
        )
    )

    for index, recommendation in enumerate(recommendations[:10], start=1):
        tutor = recommendation["tutor"]
        logger.debug(
            "Hybrid ranking %s: tutor %s, score %.3f, upcoming week load %s",
            index,
            tutor.profile_id,
            recommendation["score"],
            recommendation["upcoming_week_load"],
        )

    return recommendations
