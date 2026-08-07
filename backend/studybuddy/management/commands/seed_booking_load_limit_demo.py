"""Restore the Grace Domingo / Paolo Ramirez booking-load-limit demo case lost in the
2026-07-16 taxonomy reseed (see docs/architecture/demo-data-testing-accounts.html,
"No Longer Seeded").

Creates two brand-new tutors from scratch and pushes their Accepted Session Load
(Tutor.accepted_session_load()) against their Session Load Limit
(Tutor.session_load_limit) to demonstrate the gate in
get_recommendation_candidate_tutors (views.py):
  - Grace Domingo: load == limit -- blocked, hidden from search.
  - Paolo Ramirez: load == limit - PAOLO_REMAINING_SLOTS -- still accepting.

Deliberately additive and reversible: creates nothing but the two tutors, one shared
seed tutee to own their bookings, and everything that cascades from those three
profiles. --remove deletes all of it. Does not reseed and never touches
seed_data.py's fixed-seed output.
"""
import datetime
from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from studybuddy.models import (
    Booking,
    Course,
    PartnerInstitution,
    Subjects,
    Tutor,
    TutorApplication,
    TutorAvailability,
    TutorSubjects,
    UserProfile,
    Wallet,
)

PASSWORD = 'studybuddy123'
INSTITUTION_DOMAIN = 'cpu.edu.ph'
PLACEHOLDER_SCHOOL_ID = 'demo/placeholder_school_id.png'
PLACEHOLDER_ENROLLMENT_PROOF = 'demo/placeholder_enrollment_proof.pdf'

GRACE_USERNAME = 'grace.domingo.demo@cpu.edu.ph'
GRACE_FNAME, GRACE_LNAME = 'Grace', 'Domingo'
PAOLO_USERNAME = 'paolo.ramirez.demo@cpu.edu.ph'
PAOLO_FNAME, PAOLO_LNAME = 'Paolo', 'Ramirez'

SEED_TUTEE_USERNAME = 'loadlimit.demo@cpu.edu.ph'
SEED_TUTEE_FNAME, SEED_TUTEE_LNAME = 'LoadLimit', 'Demo'

# Paolo sits `session_load_limit - PAOLO_REMAINING_SLOTS` sessions booked, i.e. still
# has PAOLO_REMAINING_SLOTS of headroom -- "still accepting" rather than "at the wall".
PAOLO_REMAINING_SLOTS = 2

AVAILABILITY_DAY = 'Mon'
AVAILABILITY_START_HOUR = 8  # one hourly slot per session, 08:00 onward
WEEKDAY_NAMES = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']


class Command(BaseCommand):
    help = (
        'Seed Grace Domingo (at her Session Load Limit, hidden from search) and Paolo '
        'Ramirez (still accepting) to demo the Accepted Session Load gate. Use --remove '
        'to undo.'
    )

    def add_arguments(self, parser):
        parser.add_argument('--remove', action='store_true',
                             help='Delete the two seeded tutors and the seed tutee.')

    def handle(self, *args, **options):
        if options['remove']:
            return self._remove()

        with transaction.atomic():
            institution = self._get_institution()
            course = self._get_course()
            subject = self._get_subject()
            seed_tutee = self._get_or_create_seed_tutee(institution, course)

            grace, grace_created = self._get_or_create_tutor(
                GRACE_USERNAME, GRACE_FNAME, GRACE_LNAME, institution, course, subject,
            )
            paolo, paolo_created = self._get_or_create_tutor(
                PAOLO_USERNAME, PAOLO_FNAME, PAOLO_LNAME, institution, course, subject,
            )

            if grace_created:
                self._fill_load(grace, seed_tutee, grace.session_load_limit)
            if paolo_created:
                self._fill_load(
                    paolo, seed_tutee, paolo.session_load_limit - PAOLO_REMAINING_SLOTS,
                )

        self._print_summary(grace, paolo)

    # ------------------------------------------------------------------ lookups

    def _get_institution(self):
        institution = PartnerInstitution.objects.filter(
            school_email_domain=INSTITUTION_DOMAIN,
        ).first()
        if institution is None:
            raise CommandError(
                'No PartnerInstitution for cpu.edu.ph found. Run `python manage.py '
                'seed_data` first.'
            )
        return institution

    def _get_course(self):
        course = Course.objects.filter(course_code='BSCS').first() or Course.objects.first()
        if course is None:
            raise CommandError('No Course found. Run `python manage.py seed_data` first.')
        return course

    def _get_subject(self):
        subject = (
            Subjects.objects.filter(subject_name='Python').first()
            or Subjects.objects.first()
        )
        if subject is None:
            raise CommandError('No Subjects found. Run `python manage.py seed_data` first.')
        return subject

    # ------------------------------------------------------------------ creation

    def _get_or_create_seed_tutee(self, institution, course):
        profile = UserProfile.objects.filter(user__username=SEED_TUTEE_USERNAME).first()
        if profile:
            return profile

        user = User.objects.create_user(
            username=SEED_TUTEE_USERNAME, email=SEED_TUTEE_USERNAME, password=PASSWORD,
            first_name=SEED_TUTEE_FNAME, last_name=SEED_TUTEE_LNAME,
        )
        return UserProfile.objects.create(
            user=user, fname=SEED_TUTEE_FNAME, lname=SEED_TUTEE_LNAME, role='Tutee',
            course=course, year_level=1, institution=institution, profile_completed=True,
            bio='Holds seeded bookings for the Session Load Limit demo.',
        )

    def _get_or_create_tutor(self, username, fname, lname, institution, course, subject):
        existing_profile = UserProfile.objects.filter(user__username=username).first()
        if existing_profile:
            return Tutor.objects.get(profile=existing_profile), False

        now = timezone.now()
        user = User.objects.create_user(
            username=username, email=username, password=PASSWORD,
            first_name=fname, last_name=lname,
        )
        profile = UserProfile.objects.create(
            user=user, fname=fname, lname=lname, role='Tutor', course=course, year_level=3,
            institution=institution, profile_completed=True,
            bio=f'{fname} {lname} -- seeded for the Session Load Limit demo.',
        )
        tutor = Tutor.objects.create(
            profile=profile, teaching_level='College', can_online=True, can_f2f=False,
            hourly_rate=300, response_time='within_a_day',
        )
        # session_load_limit has a model default of 10; set it explicitly so this command
        # never depends on that default silently drifting.
        tutor.session_load_limit = 10
        tutor.save(update_fields=['session_load_limit'])

        TutorApplication.objects.create(
            profile=profile, application_status='approved',
            school_id=PLACEHOLDER_SCHOOL_ID, enrollment_proof=PLACEHOLDER_ENROLLMENT_PROOF,
            submitted_at=now, updated_at=now, reviewed_at=now,
        )
        Wallet.objects.get_or_create(tutor=tutor)
        TutorSubjects.objects.create(tutor=tutor, subject=subject, expertise_level=4)

        for i in range(tutor.session_load_limit):
            TutorAvailability.objects.create(
                tutor=tutor, day=AVAILABILITY_DAY,
                time_slot=datetime.time(AVAILABILITY_START_HOUR + i, 0),
                is_active=True, is_booked=False,
            )
        return tutor, True

    def _fill_load(self, tutor, seed_tutee, count):
        if count <= 0:
            return

        today = timezone.localdate()
        session_date = self._next_weekday(today, AVAILABILITY_DAY)
        slots = list(
            TutorAvailability.objects.filter(tutor=tutor).order_by('time_slot')[:count]
        )
        if len(slots) < count:
            raise CommandError(
                f'{tutor.profile.fname} {tutor.profile.lname} only has {len(slots)} '
                f'availability slots, need {count}.'
            )

        for slot in slots:
            Booking.objects.create(
                student=seed_tutee, tutor=tutor, availability=slot, session_date=session_date,
                session_mode='Online', status='Confirmed',
            )

    def _next_weekday(self, today, day_name):
        target = WEEKDAY_NAMES.index(day_name)
        offset = (target - today.weekday()) % 7
        return today + timedelta(days=offset)

    # ------------------------------------------------------------------ output

    def _print_summary(self, grace, paolo):
        self.stdout.write(self.style.SUCCESS('\nSession Load Limit demo seeded:'))
        for tutor in (grace, paolo):
            accepted = tutor.accepted_session_load()
            limit = tutor.session_load_limit
            gate = (
                'HIDDEN from search (load limit reached)'
                if accepted >= limit else 'still accepting bookings'
            )
            self.stdout.write(
                f'  {tutor.profile.fname} {tutor.profile.lname}: {accepted}/{limit} '
                f'accepted -- {gate}'
            )
        self.stdout.write(
            '\nUndo with: python manage.py seed_booking_load_limit_demo --remove'
        )

    def _remove(self):
        removed_any = False
        for username in (GRACE_USERNAME, PAOLO_USERNAME, SEED_TUTEE_USERNAME):
            profile = UserProfile.objects.filter(user__username=username).first()
            if not profile:
                continue
            user = profile.user
            profile.delete()
            user.delete()
            removed_any = True

        if removed_any:
            self.stdout.write(self.style.SUCCESS(
                'Removed the Session Load Limit demo tutors and seed tutee.'
            ))
        else:
            self.stdout.write('Nothing to remove -- no seeded tutors found.')
