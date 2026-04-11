import uuid
from datetime import datetime, timedelta

from django.db import migrations, models


def backfill_session_group_ids(apps, schema_editor):
    Booking = apps.get_model('studybuddy', 'Booking')

    bookings = (
        Booking.objects.select_related('availability')
        .order_by('tutor_id', 'student_id', 'session_date', 'availability__time_slot', 'id')
    )

    grouped_bookings = {}

    for booking in bookings:
        key = (booking.tutor_id, booking.student_id, booking.session_date)
        grouped_bookings.setdefault(key, []).append(booking)

    for booking_group in grouped_bookings.values():
        current_group_id = None
        previous_booking = None

        for booking in booking_group:
            if previous_booking is None:
                current_group_id = uuid.uuid4()
            else:
                previous_end = (
                    datetime.combine(previous_booking.session_date, previous_booking.availability.time_slot)
                    + timedelta(hours=1)
                ).time()

                if previous_end != booking.availability.time_slot:
                    current_group_id = uuid.uuid4()

            booking.session_group_id = current_group_id
            booking.save(update_fields=['session_group_id'])
            previous_booking = booking


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0026_tutoravailabilityoverride'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='session_group_id',
            field=models.UUIDField(blank=True, db_index=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='tutee_confirmed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='booking',
            name='tutor_confirmed',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='booking',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Confirmed', 'Confirmed'), ('Awaiting Payment Verification', 'Awaiting Payment Verification'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled')], default='Pending', max_length=40),
        ),
        migrations.AddField(
            model_name='payment',
            name='receipt_image',
            field=models.ImageField(blank=True, null=True, upload_to='payment_receipts/'),
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(max_length=255)),
                ('is_read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('recipient', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='notifications', to='studybuddy.userprofile')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.RunPython(backfill_session_group_ids, migrations.RunPython.noop),
    ]
