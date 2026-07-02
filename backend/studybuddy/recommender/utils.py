def filter_tutors_by_institution(queryset, student_profile):
    institution_id = student_profile.institution_id
    if institution_id is None:
        return queryset.none()
    return queryset.filter(profile__institution_id=institution_id)
