from collections import defaultdict
from ..models import Rating, Tutor, UserProfile
import math


DEFAULT_NEIGHBOR_COUNT = 5
POSITIVE_SIMILARITY_THRESHOLD = 0


# -----------------------------
# BUILD RATING MATRIX
# -----------------------------
def build_rating_matrix():

    ratings = defaultdict(dict)

    all_ratings = Rating.objects.select_related(
        "student",
        "tutor"
    )

    for r in all_ratings:

        student_id = r.student.id
        tutor_id = r.tutor.profile_id

        ratings[student_id][tutor_id] = r.rating_score

    return ratings


# -----------------------------
# PEARSON SIMILARITY
# -----------------------------
def sim(ratings, u, v):

    common = set(ratings[u]) & set(ratings[v])

    if not common:
        return 0

    u_avg = sum(ratings[u][i] for i in common) / len(common)
    v_avg = sum(ratings[v][i] for i in common) / len(common)

    numerator = sum(
        (ratings[u][i] - u_avg) *
        (ratings[v][i] - v_avg)
        for i in common
    )

    den1 = math.sqrt(
        sum((ratings[u][i] - u_avg) ** 2 for i in common)
    )

    den2 = math.sqrt(
        sum((ratings[v][i] - v_avg) ** 2 for i in common)
    )

    if den1 * den2 == 0:
        return 0

    return numerator / (den1 * den2)


# -----------------------------
# FIND TOP-K NEIGHBORS
# -----------------------------
def top_k(ratings, student_id, k=DEFAULT_NEIGHBOR_COUNT, candidate_ids=None):

    similarities = []

    candidates = candidate_ids if candidate_ids is not None else ratings

    for other_student in candidates:

        if other_student == student_id or other_student not in ratings:
            continue

        similarity = sim(ratings, student_id, other_student)

        if similarity > POSITIVE_SIMILARITY_THRESHOLD:
            similarities.append((other_student, similarity))

    similarities.sort(key=lambda x: x[1], reverse=True)

    return similarities[:k]


def get_peer_student_ids(ratings, student_profile):
    """Return rated students in the tutee's exact course using one query."""
    if student_profile.course_id is None:
        return []

    return list(
        UserProfile.objects.filter(
            id__in=ratings.keys(), course_id=student_profile.course_id
        ).exclude(
            id=student_profile.id
        ).values_list("id", flat=True)
    )


# -----------------------------
# PREDICT RATING
# -----------------------------
def compute_cf_breakdown(
    ratings, student_id, tutor_id, k=DEFAULT_NEIGHBOR_COUNT, neighbors=None
):
    """Same computation as compute_cf_score, but also returns which neighbors
    contributed a rating for this tutor and whether the student is Cold-Start
    (no Rating history at all). Used by compute_cf_score and by the algorithm
    demo tool (recommender/demo.py) to show which peers drove the CF score.

    Every term of the prediction is returned, not just the total, because the
    demo tool renders the derivation itself: student_avg is the baseline the
    prediction starts from, and each neighbor carries the neighbor_avg its
    deviation is measured against, so the panel can follow
    student_avg + (numerator / denominator) end to end. student_rating is the
    student's own score for this tutor when one exists — the candidate pool
    does not exclude already-rated tutors (see demo._candidate_tutors), so the
    demo surfaces the prediction alongside the real score as an accuracy check.
    """

    if student_id not in ratings:
        return {
            "score": None,
            "cold_start": True,
            "neighbors": [],
            "student_avg": None,
            "student_rating": None,
            "numerator": 0,
            "denominator": 0,
        }

    if neighbors is None:
        neighbors = top_k(ratings, student_id, k)

    numerator = 0
    denominator = 0
    contributing = []

    student_avg = sum(ratings[student_id].values()) / len(ratings[student_id])

    for neighbor, similarity in neighbors:

        if tutor_id not in ratings.get(neighbor, {}):
            continue

        neighbor_avg = sum(ratings[neighbor].values()) / len(ratings[neighbor])
        neighbor_rating = ratings[neighbor][tutor_id]
        deviation = neighbor_rating - neighbor_avg

        numerator += similarity * deviation
        denominator += abs(similarity)

        contributing.append({
            "neighbor_id": neighbor,
            "similarity": similarity,
            "rating": neighbor_rating,
            "neighbor_avg": neighbor_avg,
            "deviation": deviation,
            "weighted": similarity * deviation,
            # Size of the co-rated set Pearson was computed over. Below 3 the
            # similarity is degenerate (2 items always give exactly +/-1), so
            # the demo can warn instead of presenting it as meaningful.
            "co_rated_count": len(set(ratings[student_id]) & set(ratings.get(neighbor, {}))),
        })

    base = {
        "cold_start": False,
        "neighbors": contributing,
        "student_avg": student_avg,
        "student_rating": ratings[student_id].get(tutor_id),
        "numerator": numerator,
        "denominator": denominator,
    }

    if denominator == 0:
        return {**base, "score": None}

    return {**base, "score": student_avg + (numerator / denominator)}


def compute_cf_score(
    ratings, student_id, tutor_id, k=DEFAULT_NEIGHBOR_COUNT, neighbors=None
):
    return compute_cf_breakdown(ratings, student_id, tutor_id, k=k, neighbors=neighbors)["score"]


def compute_cf_breakdown_with_fallback(
    ratings, student_id, tutor_id, peer_neighbors, global_neighbors
):
    """Use the peer prediction when available, otherwise the global prediction."""
    peer_breakdown = compute_cf_breakdown(
        ratings, student_id, tutor_id, neighbors=peer_neighbors
    )
    if peer_breakdown["cold_start"]:
        return {**peer_breakdown, "pool": None}
    if peer_breakdown["score"] is not None:
        return {**peer_breakdown, "pool": "peer"}

    global_breakdown = compute_cf_breakdown(
        ratings, student_id, tutor_id, neighbors=global_neighbors
    )
    pool = "global" if global_breakdown["score"] is not None else None
    return {**global_breakdown, "pool": pool}


def compute_cf_score_with_fallback(
    ratings, student_id, tutor_id, peer_neighbors, global_neighbors
):
    return compute_cf_breakdown_with_fallback(
        ratings, student_id, tutor_id, peer_neighbors, global_neighbors
    )["score"]


# -----------------------------
# RECOMMEND TUTORS
# -----------------------------
def recommend_tutors_cf(student_profile, k=DEFAULT_NEIGHBOR_COUNT):

    ratings = build_rating_matrix()

    student_id = student_profile.id

    tutors = Tutor.objects.all()

    results = []

    for tutor in tutors:

        tutor_id = tutor.profile_id

        # skip tutors already rated
        if tutor_id in ratings.get(student_id, {}):
            continue

        score = compute_cf_score(ratings, student_id, tutor_id, k)

        if score is not None:

            results.append({
                "tutor": tutor,
                "score": score
            })

    results.sort(key=lambda x: x["score"], reverse=True)

    return results
