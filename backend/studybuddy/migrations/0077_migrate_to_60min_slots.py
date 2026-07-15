from django.db import migrations


def delete_half_hour_slots(apps, schema_editor):
    """
    Delete all TutorAvailability rows whose time_slot falls on a :30 minute mark.
    These were created under the old 30-minute granularity. Going forward the system
    uses 60-minute (top-of-hour) slots only.

    Linked Booking rows are removed automatically via on_delete=CASCADE since this
    is a development environment with no real user data.
    """
    TutorAvailability = apps.get_model('studybuddy', 'TutorAvailability')
    deleted_count, _ = TutorAvailability.objects.filter(time_slot__minute__gt=0).delete()
    print(f'  Deleted {deleted_count} half-hour TutorAvailability slot(s).')


def noop(apps, schema_editor):
    """No reverse migration — data cannot be reconstructed."""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0076_subjects_proposed_application_and_more'),
    ]

    operations = [
        migrations.RunPython(delete_half_hour_slots, noop),
    ]
