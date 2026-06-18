# Generated manually to add an index on TutorApplication.application_status
# for faster filtering in admin list and login pending-check queries.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0053_booking_studybuddy__student_d2f4ac_idx_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tutorapplication',
            name='application_status',
            field=models.CharField(
                choices=[
                    ('pending', 'Pending Review'),
                    ('approved', 'Approved'),
                    ('rejected', 'Rejected'),
                ],
                db_index=True,
                default='pending',
                max_length=20,
            ),
        ),
    ]
