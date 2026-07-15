from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0040_alter_transaction_transaction_type'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='tutoravailability',
            index=models.Index(
                fields=['day', 'time_slot', 'is_active'],
                name='studybuddy__day_524868_idx',
            ),
        ),
        migrations.AddIndex(
            model_name='booking',
            index=models.Index(
                fields=['session_date', 'availability', 'status'],
                name='studybuddy__session_2664d3_idx',
            ),
        ),
    ]
