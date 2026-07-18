import logging

from django.db.models import Q

from ..models import Preference, UserProfile
from .cbf import get_student_subject_codes, resolve_target_categories
from .CF import build_rating_matrix, get_peer_student_ids, top_k
from .hybrid import hybrid_prediction_breakdown, normalize_tutor_queryset

logger = logging.getLogger(__name__)

DEFAULT_TUTEE_SEARCH_LIMIT = 500


def search_tutees(query, institution_id=None, limit=DEFAULT_TUTEE_SEARCH_LIMIT):
    """Real Tutee profiles for the demo tool's searchable picker, with their
    registered subject preferences so the presenter can see who has data to show.
    limit defaults high (not the old 20) because the frontend now fetches the
    full roster once for a client-side searchable dropdown, rather than
    re-querying per keystroke — see SuperAdminAlgorithmDemo.vue. Unscoped by
    institution unless institution_id is given, optionally narrowing the picker
    to one school — see _candidate_tutors for the matching filter on the tutor
    side."""
    tutees = UserProfile.objects.filter(role="Tutee")

    if institution_id:
        tutees = tutees.filter(institution_id=institution_id)

    for word in query.split():
        tutees = tutees.filter(Q(fname__icontains=word) | Q(lname__icontains=word))

    tutees = list(tutees.order_by("fname", "lname")[:limit])
    subjects_by_tutee_id = _bulk_student_subject_codes(tutees)

    return [
        {
            "id": tutee.id,
            "name": f"{tutee.fname} {tutee.lname}",
            "subjects": subjects_by_tutee_id.get(tutee.id, []),
        }
        for tutee in tutees
    ]


def _bulk_student_subject_codes(tutees):
    """Same data as get_student_subject_codes, but for a whole list of tutees in
    one query instead of one query pair per tutee — search_tutees can return up
    to DEFAULT_TUTEE_SEARCH_LIMIT (500) rows, so a per-tutee lookup here was a
    real N+1 (up to ~1000 extra queries per page load)."""
    rows = Preference.objects.filter(user__in=tutees).values_list(
        "user_id", "subjects__subject_code"
    )
    subjects_by_tutee_id = {}
    for tutee_id, subject_code in rows:
        if subject_code is None:
            continue
        subjects_by_tutee_id.setdefault(tutee_id, []).append(subject_code)
    return subjects_by_tutee_id


def _candidate_tutors(subject_codes, institution_id=None):
    """Same subject-matching candidate pool as production matching
    (get_recommendation_candidate_tutors / get_dashboard_recommendations) —
    unscoped by institution, any tutee can pair with any subject-matching
    tutor. Pass institution_id to narrow the candidate pool down to one
    institution instead (e.g. to demo matching within a single school)."""
    candidates = normalize_tutor_queryset().filter(
        tutorsubjects__subject__subject_code__in=subject_codes
    ).distinct()

    if institution_id:
        candidates = candidates.filter(profile__institution_id=institution_id)

    return candidates


def _neighbor_name_map(neighbor_ids):
    profiles = UserProfile.objects.filter(id__in=neighbor_ids)
    return {profile.id: f"{profile.fname} {profile.lname}" for profile in profiles}


def build_algorithm_demo_recommendation(tutee, institution_id=None):
    """Runs the real hybrid recommender for a Tutee and returns every candidate
    Tutor's full Hybrid Score breakdown (CBF sub-scores, CF score + contributing
    Top-K Neighbors, Cold-Start flag) for the live panel demo tool. Mirrors
    get_dashboard_recommendations' subject-preference-match candidate pool,
    unscoped by institution unless institution_id is given (see
    _candidate_tutors)."""
    subject_codes = get_student_subject_codes(tutee)

    if not subject_codes:
        return {"reason": "no_preferences", "rows": []}

    candidate_tutors = list(_candidate_tutors(subject_codes, institution_id))
    if not candidate_tutors:
        return {"reason": "no_candidates", "rows": []}

    ratings = build_rating_matrix()
    peer_ids = get_peer_student_ids(ratings, tutee) if tutee.id in ratings else []
    peer_neighbors = top_k(ratings, tutee.id, candidate_ids=peer_ids) if tutee.id in ratings else []
    global_neighbors = top_k(ratings, tutee.id) if tutee.id in ratings else []
    neighbor_names = _neighbor_name_map(
        neighbor_id
        for neighbor_id, _ in [*peer_neighbors, *global_neighbors]
    )
    target_categories = resolve_target_categories(None, subject_codes)

    rows = []
    for tutor in candidate_tutors:
        breakdown = hybrid_prediction_breakdown(
            ratings,
            tutee,
            tutor,
            None,
            student_subjects=subject_codes,
            peer_neighbors=peer_neighbors,
            global_neighbors=global_neighbors,
            target_categories=target_categories,
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
                "pool": cf["pool"],
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
