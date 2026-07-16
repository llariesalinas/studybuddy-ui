"""Full demo-data wipe.

Deletes every non-staff user and everything cascading from them (profiles, tutors,
bookings, payments, ratings, preferences, chat, wallets, applications, ...), plus the
subject catalog and platform activity, while preserving Admin/SuperAdmin accounts.
Strands, Courses, and PartnerInstitutions survive (registration and the recommender's
course/strand affinity need them).

Reseeding is `seed_data`'s job: run `python manage.py reset_demo_data && python manage.py
seed_data` to rebuild the demo database. See docs/plans/2026-07-16-subjects-taxonomy-reseed.md.

Local/dev use only — this command deletes data.
"""
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from studybuddy.models import InstitutionRequest, PlatformActivity, Subjects


class Command(BaseCommand):
    help = 'Wipes all non-staff demo data and the subject catalog; admin accounts survive.'

    def handle(self, *args, **options):
        self.stdout.write('reset_demo_data: clearing non-staff data and the subject catalog')
        self._clear()
        self.stdout.write(self.style.SUCCESS('reset_demo_data complete.'))

    def _clear(self):
        """Delete all non-staff data while retaining administrator accounts."""
        demo_users = User.objects.filter(is_staff=False, is_superuser=False)
        deleted, _ = demo_users.delete()  # cascades profiles, tutors, bookings, wallets, ...
        PlatformActivity.objects.all().delete()
        InstitutionRequest.objects.all().delete()
        Subjects.objects.all().delete()
        self.stdout.write(f'  cleared: {deleted} rows cascaded from non-staff users')
