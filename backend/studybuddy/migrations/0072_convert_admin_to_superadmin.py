# Generated for the Admin -> SuperAdmin role consolidation.

from django.db import migrations, models


def convert_admin_to_superadmin(apps, schema_editor):
    UserProfile = apps.get_model('studybuddy', 'UserProfile')
    UserProfile.objects.filter(role='Admin').update(role='SuperAdmin')


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0071_booking_subject'),
    ]

    operations = [
        migrations.RunPython(
            convert_admin_to_superadmin,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='role',
            field=models.CharField(
                choices=[
                    ('Tutee', 'Tutee'),
                    ('Tutor', 'Tutor'),
                    ('SuperAdmin', 'SuperAdmin'),
                ],
                max_length=20,
            ),
        ),
    ]
