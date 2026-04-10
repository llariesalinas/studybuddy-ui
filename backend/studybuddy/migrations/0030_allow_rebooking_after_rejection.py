from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0029_alter_booking_status_rejected'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='booking',
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name='booking',
            constraint=models.UniqueConstraint(
                fields=('availability', 'session_date'),
                condition=Q(status__in=[
                    'Pending',
                    'Confirmed',
                    'Awaiting Payment Verification',
                    'Completed',
                ]),
                name='unique_active_booking_per_slot_date',
            ),
        ),
    ]
