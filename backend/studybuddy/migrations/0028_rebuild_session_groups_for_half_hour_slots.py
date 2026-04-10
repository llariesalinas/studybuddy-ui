import uuid
from datetime import datetime, timedelta

from django.db import migrations


SESSION_SLOT_MINUTES = 30


def rebuild_session_group_ids(apps, schema_editor):
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
                    + timedelta(minutes=SESSION_SLOT_MINUTES)
                ).time()

                if previous_end != booking.availability.time_slot:
                    current_group_id = uuid.uuid4()

            booking.session_group_id = current_group_id
            booking.save(update_fields=['session_group_id'])
            previous_booking = booking


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0027_post_session_payment_verification'),
    ]

    operations = [
        migrations.RunPython(rebuild_session_group_ids, migrations.RunPython.noop),
    ]
