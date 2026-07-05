from django.core.management.base import BaseCommand

from studybuddy.models import Course, InstitutionCourseCatalog, PartnerInstitution, Subjects

COURSE_CATEGORY_ALIASES = {
    "ABM": ("SHS-ABM",),
    "HUMMS": ("SHS-HUMSS",),
    "HUMSS": ("SHS-HUMSS",),
    "STEM": ("SHS-STEM",),
}


class Command(BaseCommand):
    help = (
        "Populate institution-scoped course catalogs by matching Subjects.category "
        "to Course.course_code. Existing entries are left untouched."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--institution-domain",
            help="Only populate one institution, matched by school_email_domain.",
        )

    def handle(self, *args, **options):
        domain = options.get("institution_domain")
        institutions = PartnerInstitution.objects.all().order_by("school_email_domain")
        if domain:
            institutions = institutions.filter(school_email_domain=domain)

        courses_by_code = {course.course_code: course for course in Course.objects.all()}
        if not courses_by_code:
            self.stdout.write(self.style.WARNING("No courses found. Nothing to populate."))
            return

        if not institutions.exists():
            self.stdout.write(self.style.WARNING("No matching institutions found."))
            return

        subjects = Subjects.objects.exclude(category__isnull=True).exclude(category="")
        rows = []
        skipped = 0
        before_count = InstitutionCourseCatalog.objects.count()

        courses_by_subject_category = {}
        for course_code, course in courses_by_code.items():
            categories = {course_code, *COURSE_CATEGORY_ALIASES.get(course_code, ())}
            for category in categories:
                courses_by_subject_category.setdefault(category, []).append(course)

        for institution in institutions:
            for subject in subjects:
                matching_courses = courses_by_subject_category.get(subject.category, [])
                if not matching_courses:
                    skipped += 1
                    continue

                if (
                    subject.owning_institution_id
                    and subject.owning_institution_id != institution.id
                ):
                    skipped += 1
                    continue

                for course in matching_courses:
                    rows.append(
                        InstitutionCourseCatalog(
                            institution=institution,
                            course=course,
                            subject=subject,
                        )
                    )

        InstitutionCourseCatalog.objects.bulk_create(rows, ignore_conflicts=True)
        after_count = InstitutionCourseCatalog.objects.count()

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {after_count - before_count} course-subject catalog entries "
                f"across {institutions.count()} institution(s)."
            )
        )
        if skipped:
            self.stdout.write(f"Skipped {skipped} unmatched or out-of-scope subject row(s).")
