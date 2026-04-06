from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0024_tutor_response_time_and_pinned_review'),
    ]

    operations = [
        migrations.AddField(
            model_name='subjects',
            name='category',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
