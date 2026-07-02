from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0055_deactivate_cash_payment'),
    ]

    operations = [
        migrations.CreateModel(
            name='SessionCheckIn',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_type', models.CharField(choices=[('venue_confirm', 'Venue confirmation'), ('midpoint_checkin', 'Mid-session check-in')], max_length=30)),
                ('response', models.CharField(choices=[('yes', 'Yes'), ('no', 'No'), ('good', 'Good'), ('issues', 'Having issues')], max_length=30)),
                ('responded_at', models.DateTimeField(auto_now_add=True)),
                ('booking', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='check_ins', to='studybuddy.booking')),
            ],
            options={
                'ordering': ['-responded_at'],
            },
        ),
        migrations.AddIndex(
            model_name='sessioncheckin',
            index=models.Index(fields=['booking', 'event_type'], name='studybuddy__booking_585ae7_idx'),
        ),
        migrations.AddIndex(
            model_name='sessioncheckin',
            index=models.Index(fields=['event_type', 'responded_at'], name='studybuddy__event_t_179b27_idx'),
        ),
        migrations.AddConstraint(
            model_name='sessioncheckin',
            constraint=models.UniqueConstraint(fields=('booking', 'event_type'), name='unique_session_check_in_per_booking_event'),
        ),
    ]
