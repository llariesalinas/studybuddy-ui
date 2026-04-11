from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0031_online_payment_method'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='booking_request_id',
            field=models.UUIDField(blank=True, db_index=True, default=None, null=True),
        ),
    ]
