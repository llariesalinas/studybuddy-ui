import logging

from ..models import Preference, Subjects, Tutor

logger = logging.getLogger(__name__)

W_SPECIFIC = 0.40
W_GENERAL = 0.20
W_EXPERTISE = 0.15
W_COURSE = 0.10
W_YEAR = 0.10
W_LEVEL = 0.05
TEACHING_LEVEL_MAX_YEAR = {'Elementary': 6, 'High School': 12, 'College': 16}

# Sentinel distinguishing "caller did not supply target_categories" (resolve it
# with a query) from "caller supplied an empty set" (there really are none).
_UNSET = object()


def get_student_subject_codes(student_profile):
    try:
        pref = Preference.objects.get(user=student_profile)
    except Preference.DoesNotExist:
        return []

    return list(pref.subjects.values_list('subject_code', flat=True))


def resolve_target_categories(requested_subject, subject_codes):
    """The set of non-null Subjects.category values for the "target" subject(s)
    a tutor is being matched against: the single requested subject when one was
    asked for, or the tutee's whole preference list as a fallback (see
    compute_cbf_breakdown). Callers looping over many tutors for the same
    student/subject should call this once and pass the result in as
    target_categories, instead of letting compute_cbf_breakdown resolve it
    per-tutor (which would be an N+1 query)."""
    codes = {requested_subject} if requested_subject else set(subject_codes)
    if not codes:
        return set()

    categories = Subjects.objects.filter(subject_code__in=codes).values_list(
        "category", flat=True
    )
    return {category for category in categories if category}


def compute_cbf_breakdown(
    student_profile,
    tutor,
    requested_subject,
    student_subjects=None,
    tutor_subjects=None,
    target_categories=_UNSET,
):
    """Same computation as compute_cbf_score, but returns each weighted sub-score
    alongside the total. Used by compute_cbf_score and by the algorithm demo tool
    (recommender/demo.py) to show the CBF formula's components, not just the total.

    Matching is graduated rather than all-or-nothing: an exact match on the
    requested subject (Specific) always outranks a same-field match (General),
    which always outranks an unrelated tutor. When requested_subject is falsy
    (e.g. the algorithm demo tool), the tutee's preference list stands in as the
    "target" subject set, so Specific/General/Expertise are computed against any
    subject in that list rather than a single requested one.

    target_categories lets a caller looping over many tutors precompute the
    target subject(s)' categories once via resolve_target_categories() and pass
    it in, avoiding a per-tutor query; if omitted it is resolved here.
    """
    student_course = student_profile.course
    student_year = student_profile.year_level
    subject_codes = (
        list(student_subjects)
        if student_subjects is not None
        else get_student_subject_codes(student_profile)
    )

    target_codes = {requested_subject} if requested_subject else set(subject_codes)

    if target_categories is _UNSET:
        target_categories = resolve_target_categories(requested_subject, subject_codes)

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

    exact_matches = [ts for ts in subjects if ts.subject.subject_code in target_codes]
    same_field_matches = [
        ts
        for ts in subjects
        if ts.subject.category and ts.subject.category in target_categories
    ]

    s_specific = 1 if exact_matches else 0
    s_general = 1 if (exact_matches or same_field_matches) else 0

    if exact_matches:
        s_expertise = (
            sum(ts.expertise_level for ts in exact_matches) / len(exact_matches)
        ) / 5
    elif same_field_matches:
        s_expertise = (
            sum(ts.expertise_level for ts in same_field_matches) / len(same_field_matches)
        ) / 5
    else:
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

    if (
        tutor_level in TEACHING_LEVEL_MAX_YEAR
        and student_year is not None
        and int(student_year) > TEACHING_LEVEL_MAX_YEAR[tutor_level]
    ):
        s_level = 0

    sub_scores = {
        "specific": (W_SPECIFIC, s_specific),
        "general": (W_GENERAL, s_general),
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
    target_categories=_UNSET,
):
    return compute_cbf_breakdown(
        student_profile,
        tutor,
        requested_subject,
        student_subjects=student_subjects,
        tutor_subjects=tutor_subjects,
        target_categories=target_categories,
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
    target_categories = resolve_target_categories(subject, student_subjects)
    results = []

    for tutor in tutors:
        score = compute_cbf_score(
            student_profile,
            tutor,
            subject,
            student_subjects=student_subjects,
            tutor_subjects=tutor.tutorsubjects_set.all(),
            target_categories=target_categories,
        )

        results.append({
            "tutor": tutor,
            "score": score,
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    logger.debug("CBF recommender finished with %s results", len(results))

    return results
