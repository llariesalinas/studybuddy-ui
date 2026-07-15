import logging

from ..models import Preference, Tutor
from ..subject_recognition import recognized_subject_codes_for_profile

logger = logging.getLogger(__name__)

W_SUBJECT = 0.35
W_EXPERTISE = 0.20
W_COURSE = 0.20
W_YEAR = 0.15
W_LEVEL = 0.10


def get_student_subject_codes(student_profile):
    try:
        pref = Preference.objects.get(user=student_profile)
    except Preference.DoesNotExist:
        return []

    recognized_codes = recognized_subject_codes_for_profile(student_profile)
    return [
        code
        for code in pref.subjects.values_list("subject_code", flat=True)
        if code in recognized_codes
    ]


def compute_cbf_breakdown(
    student_profile,
    tutor,
    requested_subject,
    student_subjects=None,
    tutor_subjects=None,
):
    """Same computation as compute_cbf_score, but returns each weighted sub-score
    alongside the total. Used by compute_cbf_score and by the algorithm demo tool
    (recommender/demo.py) to show the CBF formula's components, not just the total."""
    student_course = student_profile.course
    student_year = student_profile.year_level
    subject_codes = (
        list(student_subjects)
        if student_subjects is not None
        else get_student_subject_codes(student_profile)
    )

    if requested_subject and requested_subject not in subject_codes:
        subject_codes.append(requested_subject)

    tutor_profile = tutor.profile
    tutor_course = tutor_profile.course
    tutor_year = tutor_profile.year_level
    tutor_level = tutor.teaching_level
    subjects = (
        list(tutor_subjects)
        if tutor_subjects is not None
        else list(tutor.tutorsubjects_set.all())
    )

    tutor_subject_codes = [ts.subject.subject_code for ts in subjects]
    matching_expertise = [
        ts.expertise_level
        for ts in subjects
        if ts.subject.subject_code in subject_codes
    ]

    if matching_expertise:
        s_subject = 1
        s_expertise = (sum(matching_expertise) / len(matching_expertise)) / 5
    else:
        s_subject = 0
        s_expertise = 0

    s_course = 0

    if student_course == tutor_course:
        s_course = 1
    elif (
        student_course
        and tutor_course
        and student_course.strand == tutor_course.strand
    ):
        s_course = 0.5

    if student_year and tutor_year:
        year_diff = abs(student_year - tutor_year)
        s_year = 1 / (1 + year_diff)
    else:
        s_year = 0

    s_level = 1

    if tutor_level == "SHS" and student_year is not None and int(student_year) > 12:
        s_level = 0

    sub_scores = {
        "subject": (W_SUBJECT, s_subject),
        "expertise": (W_EXPERTISE, s_expertise),
        "course": (W_COURSE, s_course),
        "year": (W_YEAR, s_year),
        "level": (W_LEVEL, s_level),
    }

    breakdown = {
        name: {"weight": weight, "value": value, "contribution": weight * value}
        for name, (weight, value) in sub_scores.items()
    }
    breakdown["score"] = sum(part["contribution"] for part in breakdown.values())
    breakdown["tutor_subject_codes"] = tutor_subject_codes

    logger.debug(
        "CBF score for tutor %s: %.3f (student subjects=%s, tutor subjects=%s)",
        tutor.profile_id,
        breakdown["score"],
        subject_codes,
        tutor_subject_codes,
    )

    return breakdown


def compute_cbf_score(
    student_profile,
    tutor,
    requested_subject,
    student_subjects=None,
    tutor_subjects=None,
):
    return compute_cbf_breakdown(
        student_profile,
        tutor,
        requested_subject,
        student_subjects=student_subjects,
        tutor_subjects=tutor_subjects,
    )["score"]


def recommend_tutors(student_profile, subject=None, preferred_mode=None):
    logger.debug("Starting CBF recommender")

    tutors = Tutor.objects.select_related(
        "profile",
        "profile__course",
        "profile__course__strand",
    ).prefetch_related("tutorsubjects_set__subject")

    if preferred_mode == "Online":
        tutors = tutors.filter(can_online=True)

    if preferred_mode == "Face-to-face":
        tutors = tutors.filter(can_f2f=True)

    student_subjects = get_student_subject_codes(student_profile)
    results = []

    for tutor in tutors:
        score = compute_cbf_score(
            student_profile,
            tutor,
            subject,
            student_subjects=student_subjects,
            tutor_subjects=tutor.tutorsubjects_set.all(),
        )

        results.append({
            "tutor": tutor,
            "score": score,
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    logger.debug("CBF recommender finished with %s results", len(results))

    return results
