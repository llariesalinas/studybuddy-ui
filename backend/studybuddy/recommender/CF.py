from collections import defaultdict
from ..models import Rating, Tutor
import math


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
def top_k(ratings, student_id, k=5):

    similarities = []

    for other_student in ratings:

        if other_student == student_id:
            continue

        similarity = sim(ratings, student_id, other_student)
            
       # if similarity >= 0:
           # similarities.append(other_student,similarity)
            
        similarities.append((other_student,similarity))

    similarities.sort(key=lambda x: x[1], reverse=True)

    return similarities[:k]


# -----------------------------
# PREDICT RATING
# -----------------------------
def compute_cf_score(ratings, student_id, tutor_id, k=5, neighbors=None):

    if student_id not in ratings:
        return None

    if neighbors is None:
        neighbors = top_k(ratings, student_id, k)

    numerator = 0
    denominator = 0

    student_avg = sum(ratings[student_id].values()) / len(ratings[student_id])

    for neighbor, similarity in neighbors:

        if tutor_id not in ratings.get(neighbor, {}):
            continue

        neighbor_avg = sum(ratings[neighbor].values()) / len(ratings[neighbor])

        numerator += similarity * (
            ratings[neighbor][tutor_id] - neighbor_avg
        )

        denominator += abs(similarity)

    if denominator == 0:
        return None

    return student_avg + (numerator / denominator)


# -----------------------------
# RECOMMEND TUTORS
# -----------------------------
def recommend_tutors_cf(student_profile, k=5):

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