from django.db import migrations, models
from django.utils import timezone


def preserve_completed_setup(apps, schema_editor):
    Profile = apps.get_model('studybuddy', 'UserProfile')
    Tutor = apps.get_model('studybuddy', 'Tutor')
    Application = apps.get_model('studybuddy', 'TutorApplication')
    # Existing submitted applications with a configured tutor rate predate this marker.
    # Include tutors whose subjects have since been removed.
    profiles = Tutor.objects.filter(hourly_rate__isnull=False).values('profile_id')
    applications = Application.objects.values('profile_id')
    Profile.objects.filter(pk__in=profiles).filter(
        models.Q(pk__in=applications) | models.Q(tutor_onboarding_skipped_at__isnull=False)
    ).update(tutor_setup_completed_at=timezone.now())


def merge_system_categories(apps, schema_editor):
    Category = apps.get_model('studybuddy', 'SubjectCategory')
    Subject = apps.get_model('studybuddy', 'Subjects')
    system = list(Category.objects.filter(is_system=True).order_by('pk'))
    if not system:
        Category.objects.update_or_create(
            name='Uncategorized', defaults={'is_system': True, 'display_order': 999},
        )
        return
    canonical = next((row for row in system if row.name == 'Uncategorized'), system[0])
    for duplicate in system:
        if duplicate.pk != canonical.pk:
            Subject.objects.filter(category_id=duplicate.pk).update(category_id=canonical.pk)
            duplicate.delete()


class Migration(migrations.Migration):
    dependencies = [('studybuddy', '0086_trusteddevice')]

    operations = [
        migrations.AddField(
            model_name='userprofile', name='tutor_setup_completed_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.RunPython(preserve_completed_setup, migrations.RunPython.noop),
        migrations.RunPython(merge_system_categories, migrations.RunPython.noop),
    ]
