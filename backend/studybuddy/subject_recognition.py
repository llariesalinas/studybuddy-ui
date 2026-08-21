from .models import Preference, Subjects, TutorSubjects


def recognized_subject_codes_for_profile(profile, course_code=None):
    return set(Subjects.objects.filter(status='approved').values_list('subject_code', flat=True))


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
    # select_related('category'): SubjectSerializer renders the category by name, which is a
    # per-row query on a foreign key without it.
    return Subjects.objects.filter(status='approved').select_related('category')


def subject_selection_queryset_for_profile(profile, course_code=None, include_current=False):
    recognized_codes = recognized_subject_codes_for_profile(profile, course_code=course_code)
    allowed_codes = set(recognized_codes)

    if include_current:
        # Current subjects may include a tutor's own pending proposed subjects, which the
        # approved-only visible queryset would otherwise hide from their selection list.
        allowed_codes.update(current_subject_codes_for_profile(profile))

    queryset = Subjects.objects.filter(subject_code__in=allowed_codes).select_related(
        'category'
    )
    return queryset, recognized_codes


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
