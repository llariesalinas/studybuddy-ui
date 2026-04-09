from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0025_subjects_category'),
    ]

    operations = [
        migrations.CreateModel(
            name='TutorAvailabilityOverride',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('override_date', models.DateField()),
                ('is_full_day', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('availability', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='date_overrides', to='studybuddy.tutoravailability')),
                ('tutor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='availability_overrides', to='studybuddy.tutor')),
            ],
        ),
        migrations.AddConstraint(
            model_name='tutoravailabilityoverride',
            constraint=models.UniqueConstraint(condition=models.Q(('is_full_day', True)), fields=('tutor', 'override_date'), name='unique_full_day_override_per_tutor_date'),
        ),
        migrations.AddConstraint(
            model_name='tutoravailabilityoverride',
            constraint=models.UniqueConstraint(condition=models.Q(('is_full_day', False)), fields=('tutor', 'override_date', 'availability'), name='unique_slot_override_per_tutor_date_slot'),
        ),
    ]
