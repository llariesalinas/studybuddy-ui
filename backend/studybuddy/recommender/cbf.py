from ..models import (
    Preference,
    Tutor,
    TutorSubjects
)

# -----------------------------
# WEIGHTS
# -----------------------------

W_SUBJECT = 0.35
W_EXPERTISE = 0.20
W_COURSE = 0.20
W_YEAR = 0.15
W_LEVEL = 0.10


# -----------------------------
# COMPUTE CBF SCORE
# -----------------------------

def compute_cbf_score(student_profile, tutor, requested_subject):

    print("\n==============================")
    print("Running CBF for Tutor:", tutor.profile.fname, tutor.profile.lname)

    # -----------------------------
    # STUDENT DATA
    # -----------------------------

    student_course = student_profile.course
    student_year = student_profile.year_level

    try:
        pref = Preference.objects.get(user=student_profile)

        student_subjects = list(
            pref.subjects.values_list("subject_code", flat=True)
        )

    except Preference.DoesNotExist:
        student_subjects = []

    # Add requested booking subject
    if requested_subject and requested_subject not in student_subjects:
        student_subjects.append(requested_subject)

    print("Student Subjects:", student_subjects)


    # -----------------------------
    # TUTOR DATA
    # -----------------------------

    tutor_profile = tutor.profile
    tutor_course = tutor_profile.course
    tutor_year = tutor_profile.year_level
    tutor_level = tutor.teaching_level

    tutor_subjects = TutorSubjects.objects.filter(tutor=tutor)

    tutor_subject_codes = [
        ts.subject.subject_code for ts in tutor_subjects
    ]

    print("Tutor Subjects:", tutor_subject_codes)


    # -----------------------------
    # SUBJECT MATCH + EXPERTISE
    # -----------------------------

    matching_expertise = []

    for ts in tutor_subjects:

        if ts.subject.subject_code in student_subjects:

            matching_expertise.append(ts.expertise_level)

    if matching_expertise:

        s_subject = 1
        ex_ave = sum(matching_expertise) / len(matching_expertise)
        s_expertise = ex_ave / 5

    else:

        s_subject = 0
        s_expertise = 0

    print("Subject Match Score:", s_subject)
    print("Expertise Score:", round(s_expertise, 3))


    # -----------------------------
    # COURSE SIMILARITY
    # -----------------------------

    s_course = 0

    if student_course == tutor_course:

        s_course = 1

    elif (
        student_course
        and tutor_course
        and student_course.strand == tutor_course.strand
    ):

        s_course = 0.5

    print("Course Score:", s_course)


    # -----------------------------
    # YEAR SIMILARITY
    # -----------------------------

    if student_year and tutor_year:

        year_diff = abs(student_year - tutor_year)
        s_year = 1 / (1 + year_diff)

    else:

        s_year = 0

    print("Year Score:", round(s_year, 3))


    # -----------------------------
    # TEACHING LEVEL RULE
    # -----------------------------

    s_level = 1

    if tutor_level == "SHS" and int(student_year) > 12:
        s_level = 0

    print("Teaching Level Score:", s_level)


    # -----------------------------
    # FINAL SCORE
    # -----------------------------

    score = (
        W_SUBJECT * s_subject +
        W_EXPERTISE * s_expertise +
        W_COURSE * s_course +
        W_YEAR * s_year +
        W_LEVEL * s_level
    )

    print("FINAL SCORE:", round(score, 3))
    print("==============================")

    return score


# -----------------------------
# RECOMMEND TUTORS
# -----------------------------

def recommend_tutors(student_profile, subject=None, preferred_mode=None):

    print("\n===== STARTING CBF RECOMMENDER =====")

    tutors = Tutor.objects.all().select_related("profile")

    # -----------------------------
    # FILTER BY MODE
    # -----------------------------

    if preferred_mode == "Online":
        tutors = tutors.filter(can_online=True)

    if preferred_mode == "Face-to-face":
        tutors = tutors.filter(can_f2f=True)

    results = []

    for tutor in tutors:

        score = compute_cbf_score(
            student_profile,
            tutor,
            subject
        )

        results.append({
            "tutor": tutor,
            "score": score
        })

    # Sort highest score first
    results.sort(key=lambda x: x["score"], reverse=True)

    print("===== RECOMMENDER FINISHED =====\n")

    return results