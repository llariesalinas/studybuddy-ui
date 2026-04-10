from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0028_rebuild_session_groups_for_half_hour_slots'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='status',
            field=models.CharField(
                choices=[
                    ('Pending', 'Pending'),
                    ('Confirmed', 'Confirmed'),
                    ('Awaiting Payment Verification', 'Awaiting Payment Verification'),
                    ('Completed', 'Completed'),
                    ('Rejected', 'Rejected'),
                    ('Cancelled', 'Cancelled'),
                ],
                default='Pending',
                max_length=40,
            ),
        ),
    ]
