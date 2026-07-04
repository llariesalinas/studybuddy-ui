import logging

from django.db.models import Q

from ..models import UserProfile
from .cbf import get_student_subject_codes
from .CF import build_rating_matrix, top_k
from .hybrid import hybrid_prediction_breakdown, normalize_tutor_queryset
from .utils import filter_tutors_by_institution

logger = logging.getLogger(__name__)

DEFAULT_TUTEE_SEARCH_LIMIT = 20


def search_tutees(query, limit=DEFAULT_TUTEE_SEARCH_LIMIT):
    """Real Tutee profiles for the demo tool's searchable picker, with their
    registered subject preferences so the presenter can see who has data to show."""
    tutees = UserProfile.objects.filter(role="Tutee")

    for word in query.split():
        tutees = tutees.filter(Q(fname__icontains=word) | Q(lname__icontains=word))

    tutees = tutees.order_by("fname", "lname")[:limit]

    return [
        {
            "id": tutee.id,
            "name": f"{tutee.fname} {tutee.lname}",
            "subjects": get_student_subject_codes(tutee),
        }
        for tutee in tutees
    ]


def _candidate_tutors(tutee, subject_codes):
    candidate_qs = normalize_tutor_queryset().filter(
        tutorsubjects__subject__subject_code__in=subject_codes
    ).distinct()
    return filter_tutors_by_institution(candidate_qs, tutee)


def _neighbor_name_map(neighbor_ids):
    profiles = UserProfile.objects.filter(id__in=neighbor_ids)
    return {profile.id: f"{profile.fname} {profile.lname}" for profile in profiles}


def build_algorithm_demo_recommendation(tutee):
    """Runs the real hybrid recommender for a Tutee and returns every candidate
    Tutor's full Hybrid Score breakdown (CBF sub-scores, CF score + contributing
    Top-K Neighbors, Cold-Start flag) for the live panel demo tool. Mirrors
    get_dashboard_recommendations' candidate pool (subject preference match +
    institution filter) but returns the breakdown instead of a serialized list."""
    subject_codes = get_student_subject_codes(tutee)

    if not subject_codes:
        return {"reason": "no_preferences", "rows": []}

    candidate_tutors = list(_candidate_tutors(tutee, subject_codes))
    if not candidate_tutors:
        return {"reason": "no_candidates", "rows": []}

    ratings = build_rating_matrix()
    neighbors = top_k(ratings, tutee.id) if tutee.id in ratings else []
    neighbor_names = _neighbor_name_map(neighbor_id for neighbor_id, _ in neighbors)

    rows = []
    for tutor in candidate_tutors:
        breakdown = hybrid_prediction_breakdown(
            ratings,
            tutee,
            tutor,
            None,
            student_subjects=subject_codes,
            neighbors=neighbors,
        )
        cf = breakdown["cf"]

        rows.append({
            "tutor_id": tutor.profile_id,
            "name": f"{tutor.profile.fname} {tutor.profile.lname}",
            "hybrid_score": breakdown["hybrid_score"],
            "cold_start": cf["cold_start"],
            "rating_average": tutor.rating_average,
            "total_sessions": tutor.total_sessions,
            "tutor_subjects": [
                {"code": ts.subject.subject_code, "expertise_level": ts.expertise_level}
                for ts in tutor.tutorsubjects_set.all()
            ],
            "cbf": breakdown["cbf"],
            "cf": {
                "score": cf["score"],
                "neighbors": [
                    {
                        "neighbor_id": neighbor["neighbor_id"],
                        "name": neighbor_names.get(neighbor["neighbor_id"], "Unknown"),
                        "similarity": neighbor["similarity"],
                        "rating": neighbor["rating"],
                    }
                    for neighbor in cf["neighbors"]
                ],
            },
        })

    rows.sort(key=lambda row: row["hybrid_score"], reverse=True)
    return {"reason": None, "rows": rows}
