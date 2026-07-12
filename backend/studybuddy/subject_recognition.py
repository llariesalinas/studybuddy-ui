from .models import Preference, Subjects, TutorSubjects

COURSE_CODE_GROUPS = (
    {"STEM", "SHS-STEM"},
    {"ABM", "SHS-ABM"},
    {"GAS", "SHS-GAS"},
    {"HUMMS", "HUMSS", "SHS-HUMSS"},
)


def equivalent_course_codes(course_code):
    normalized = str(course_code or "").strip()
    if not normalized:
        return set()

    for group in COURSE_CODE_GROUPS:
        if normalized in group:
            return set(group)

    return {normalized}


def recognized_subject_codes_for_profile(profile, course_code=None):
    course_codes = equivalent_course_codes(course_code or getattr(profile, "course_id", None))
    if not course_codes:
        return set()

    return set(
        Subjects.objects.filter(category__in=course_codes).values_list("subject_code", flat=True)
    )


def current_subject_codes_for_profile(profile):
    if profile.role == "Tutor":
        return set(
            TutorSubjects.objects.filter(tutor__profile=profile).values_list(
                "subject__subject_code",
                flat=True,
            )
        )

    return set(
        Preference.objects.filter(user=profile).values_list(
            "subjects__subject_code",
            flat=True,
        )
    )


def visible_subject_queryset_for_profile(profile):
    return Subjects.objects.all()


def subject_selection_queryset_for_profile(profile, course_code=None, include_current=False):
    recognized_codes = recognized_subject_codes_for_profile(profile, course_code=course_code)
    allowed_codes = set(recognized_codes)

    if include_current:
        allowed_codes.update(current_subject_codes_for_profile(profile))

    queryset = visible_subject_queryset_for_profile(profile)
    if not allowed_codes:
        return queryset.none(), recognized_codes

    return queryset.filter(subject_code__in=allowed_codes), recognized_codes


def invalid_new_subject_codes(profile, requested_codes, course_code=None):
    requested_codes = {str(code) for code in requested_codes if code}
    recognized_codes = recognized_subject_codes_for_profile(profile, course_code=course_code)
    current_codes = current_subject_codes_for_profile(profile)
    allowed_codes = recognized_codes | current_codes
    return requested_codes - allowed_codes


def subject_is_recognized_for_profile(profile, subject_code, course_code=None):
    return str(subject_code or "") in recognized_subject_codes_for_profile(
        profile,
        course_code=course_code,
    )
