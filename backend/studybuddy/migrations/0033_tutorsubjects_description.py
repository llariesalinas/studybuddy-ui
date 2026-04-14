from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0032_booking_request_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='tutorsubjects',
            name='description',
            field=models.TextField(blank=True, default=''),
        ),
    ]
