from ..models import Tutor
from .CF import compute_cf_score
from .cbf import compute_cbf_score


# ---------------------------------------------
# HYBRID SCORE FOR ONE TUTOR
# ---------------------------------------------
def hybrid_prediction(ratings, student_profile, tutor, requested_subject):

    # -----------------------------
    # CBF SCORE
    # -----------------------------
    cbf_score = compute_cbf_score(
        student_profile,
        tutor,
        requested_subject
    )

    # -----------------------------
    # CF SCORE
    # -----------------------------
    tutor_id = tutor.profile_id

    cf_score = compute_cf_score(
        ratings,
        student_profile.id,
        tutor_id
    )

    if cf_score is None:
        cf_score = 0

    # -----------------------------
    # HYBRID SCORE
    # -----------------------------
    hybrid_score = (0.7 * cbf_score) + (0.3 * (cf_score / 5))

    # -----------------------------
    # DEBUG OUTPUT
    # -----------------------------
    print("\n-----------------------------------")
    print(f"Tutor: {tutor.profile.fname} {tutor.profile.lname}")
    print(f"CBF Score: {cbf_score:.3f}")
    print(f"CF Score: {cf_score:.3f}")
    print(f"Hybrid Score: {hybrid_score:.3f}")
    print("-----------------------------------")

    return hybrid_score


# ---------------------------------------------
# HYBRID RECOMMENDATION LIST
# ---------------------------------------------
def recommend_tutors_hybrid(ratings, student_profile, requested_subject):

    tutors = Tutor.objects.select_related("profile")

    recommendations = []

    for tutor in tutors:

        score = hybrid_prediction(
            ratings,
            student_profile,
            tutor,
            requested_subject
        )

        recommendations.append({
            "tutor": tutor,
            "score": score
        })

    # Sort tutors by score
    recommendations.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    # -----------------------------
    # PRINT FINAL RANKING
    # -----------------------------
    print("\n===================================")
    print("FINAL HYBRID RANKING")
    print("===================================")

    for i, r in enumerate(recommendations[:10], start=1):

        tutor = r["tutor"]
        score = r["score"]

        print(
            f"{i}. {tutor.profile.fname} {tutor.profile.lname} — Score: {score:.3f}"
        )

    print("===================================\n")

    return recommendations