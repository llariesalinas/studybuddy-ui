from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase


class ReviewIntegrityMigrationTests(TransactionTestCase):
    def test_upgrade_merges_duplicate_fallbacks_and_preserves_established_tutors(self):
        before = [('studybuddy', '0086_trusteddevice')]
        after = [('studybuddy', '0088_unique_system_subject_category')]
        executor = MigrationExecutor(connection)
        executor.migrate(before)
        apps = executor.loader.project_state(before).apps
        try:
            Category = apps.get_model('studybuddy', 'SubjectCategory')
            Subject = apps.get_model('studybuddy', 'Subjects')
            User = apps.get_model('auth', 'User')
            Profile = apps.get_model('studybuddy', 'UserProfile')
            Tutor = apps.get_model('studybuddy', 'Tutor')
            Application = apps.get_model('studybuddy', 'TutorApplication')
            canonical, _ = Category.objects.get_or_create(
                name='Uncategorized', defaults={'is_system': True},
            )
            duplicate = Category.objects.create(name='Renamed fallback', is_system=True)
            subject = Subject.objects.create(
                subject_code='migration-review', subject_name='Migration subject', category=duplicate,
            )
            established = Profile.objects.create(
                user=User.objects.create(username='established-review'), role='Tutor',
                fname='Established', lname='Tutor',
            )
            Tutor.objects.create(profile=established, hourly_rate=200)
            Application.objects.create(profile=established, application_status='approved')
            beginner = Profile.objects.create(
                user=User.objects.create(username='beginner-review'), role='Tutor',
                fname='New', lname='Tutor',
            )
            Tutor.objects.create(profile=beginner, hourly_rate=None)
            Application.objects.create(profile=beginner, application_status='approved')

            executor = MigrationExecutor(connection)
            executor.migrate(after)
            apps = executor.loader.project_state(after).apps
            Category = apps.get_model('studybuddy', 'SubjectCategory')
            Subject = apps.get_model('studybuddy', 'Subjects')
            Profile = apps.get_model('studybuddy', 'UserProfile')
            self.assertEqual(Category.objects.filter(is_system=True).count(), 1)
            self.assertEqual(Subject.objects.get(pk=subject.pk).category_id, canonical.pk)
            self.assertIsNotNone(Profile.objects.get(pk=established.pk).tutor_setup_completed_at)
            self.assertIsNone(Profile.objects.get(pk=beginner.pk).tutor_setup_completed_at)
        finally:
            MigrationExecutor(connection).migrate(after)
