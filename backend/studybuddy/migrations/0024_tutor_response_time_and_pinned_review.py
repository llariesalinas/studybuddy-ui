from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0023_drop_legacy_booking_topic_column'),
    ]

    operations = [
        migrations.AddField(
            model_name='tutor',
            name='pinned_review',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='pinned_by_tutor',
                to='studybuddy.rating',
            ),
        ),
        migrations.AddField(
            model_name='tutor',
            name='response_time',
            field=models.CharField(
                blank=True,
                choices=[
                    ('within_1_hour', 'Within 1 hour'),
                    ('within_few_hours', 'Within a few hours'),
                    ('within_a_day', 'Within a day'),
                ],
                max_length=30,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='tutor',
            name='response_time_label',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
