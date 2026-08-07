"""Give one tutor in an existing tie group some Upcoming Week Load, so the Tie
Breaker (docs/adr/0009-tie-breaker-upcoming-week-load.md) can be seen working on
real data instead of only in tests.

Ties are already plentiful in the seeded data — what is missing is any *variation
in load* between tied tutors, so every tie falls through to the profile_id
fallback and the rule looks like it does nothing. This adds a few bookings to
whichever tied tutor currently ranks first, which pushes the tied peer above her.

Deliberately additive and reversible: it creates nothing but one clearly-labelled
tutee and that tutee's bookings, and `--remove` deletes both. It does not reseed,
and it never touches an existing user's data.
"""

from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from studybuddy.models import (
    TUTOR_ACCEPTED_SESSION_LOAD_STATUSES,
    Booking,
    Tutor,
    TutorAvailability,
    UserProfile,
)
from studybuddy.recommender.demo import build_algorithm_demo_recommendation
from studybuddy.recommender.workload import UPCOMING_WEEK_DAYS

# A tutee known to surface a tie group. Overridable with --tutee, since a reseed
# renumbers profiles; the command verifies the tie rather than trusting this.
DEFAULT_TUTEE_ID = 5089
DEFAULT_SESSION_COUNT = 3

SEED_TUTEE_USERNAME = 'tiebreak.demo@cpu.edu.ph'
SEED_TUTEE_FNAME = 'Tiebreak'
SEED_TUTEE_LNAME = 'Demo'
SEED_TUTEE_PASSWORD = 'studybuddy123'

WEEKDAY_NAMES = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']


class Command(BaseCommand):
    help = (
        'Add Upcoming Week Load to one tutor in an existing tie group so the Tie '
        'Breaker is demonstrable. Use --remove to undo.'
    )

    def add_arguments(self, parser):
        parser.add_argument('--tutee', type=int, default=DEFAULT_TUTEE_ID,
                            help='Tutee profile id whose ranking should show the tie.')
        parser.add_argument('--sessions', type=int, default=DEFAULT_SESSION_COUNT,
                            help='How many bookings to give the tied tutor.')
        parser.add_argument('--remove', action='store_true',
                            help='Delete the seeded bookings and the seed tutee.')

    def handle(self, *args, **options):
        if options['remove']:
            return self._remove()

        tutee = self._get_tutee(options['tutee'])
        group = self._find_tie_group(tutee)
        target = group[0]

        self.stdout.write(f'Tie group for {tutee.fname} {tutee.lname} (id {tutee.id}):')
        self._print_group(group)

        with transaction.atomic():
            seed_tutee = self._get_or_create_seed_tutee(tutee)
            created = self._create_bookings(target['tutor_id'], seed_tutee, options['sessions'])

        if not created:
            raise CommandError(
                f"Could not place any booking for {target['name']} — no free "
                'availability slot in the coming week. Try --sessions 1, or a '
                'different --tutee.'
            )

        self.stdout.write(self.style.SUCCESS(
            f"\nAdded {len(created)} booking(s) for {target['name']}:"
        ))
        for booking in created:
            self.stdout.write(f'  {booking.session_date} ({booking.availability.time_slot})')

        self.stdout.write('\nRanking now:')
        self._print_group(self._find_tie_group(tutee, required=False))
        self.stdout.write(
            '\nUndo with: python manage.py seed_tie_breaker_demo --remove'
        )

    # ------------------------------------------------------------------ helpers

    def _get_tutee(self, tutee_id):
        try:
            return UserProfile.objects.get(id=tutee_id, role='Tutee')
        except UserProfile.DoesNotExist:
            raise CommandError(f'No Tutee with profile id {tutee_id}.')

    def _find_tie_group(self, tutee, required=True):
        """The first tie group in this tutee's ranking, in rank order."""
        result = build_algorithm_demo_recommendation(tutee)
        rows = result.get('rows') or []

        if not rows and required:
            raise CommandError(
                f'No candidate tutors for tutee {tutee.id} ({result.get("reason")}).'
            )

        for row in rows:
            if row.get('tie_group_id') is not None:
                group_id = row['tie_group_id']
                return [r for r in rows if r.get('tie_group_id') == group_id]

        if required:
            raise CommandError(
                f'Tutee {tutee.id} has no tied tutors — nothing for the Tie Breaker '
                'to order. Try a different --tutee.'
            )
        return rows[:5]

    def _print_group(self, rows):
        for index, row in enumerate(rows, start=1):
            self.stdout.write(
                f"  {index}. {row['name']:<24} score {row['hybrid_score']:.3f}  "
                f"load {row['upcoming_week_load']}"
            )

    def _get_or_create_seed_tutee(self, like_tutee):
        """A dedicated tutee that exists only to own the seeded bookings, so no
        real account gets sessions it never booked. Mirrors the reference tutee's
        course/institution so it does not look foreign in admin screens."""
        profile = UserProfile.objects.filter(user__username=SEED_TUTEE_USERNAME).first()
        if profile:
            return profile

        user = User.objects.create_user(
            username=SEED_TUTEE_USERNAME,
            email=SEED_TUTEE_USERNAME,
            password=SEED_TUTEE_PASSWORD,
            first_name=SEED_TUTEE_FNAME,
            last_name=SEED_TUTEE_LNAME,
        )
        return UserProfile.objects.create(
            user=user,
            fname=SEED_TUTEE_FNAME,
            lname=SEED_TUTEE_LNAME,
            role='Tutee',
            course=like_tutee.course,
            year_level=like_tutee.year_level,
            institution=like_tutee.institution,
            bio='Holds seeded bookings for the Tie Breaker demo.',
            profile_completed=True,
        )

    def _create_bookings(self, tutor_id, seed_tutee, count):
        """One booking per distinct availability slot, dated on the next matching
        weekday inside the Upcoming Week Load window. Distinct slots keep clear of
        the (availability, session_date) unique constraint."""
        tutor = Tutor.objects.get(profile_id=tutor_id)
        today = timezone.localdate()
        window_end = today + timedelta(days=UPCOMING_WEEK_DAYS)

        created = []
        for availability in TutorAvailability.objects.filter(
            tutor=tutor, is_active=True
        ).order_by('time_slot'):
            if len(created) >= count:
                break

            session_date = self._next_date_for_day(availability.day, today, window_end)
            if session_date is None:
                continue

            if Booking.objects.filter(
                availability=availability,
                session_date=session_date,
                status__in=TUTOR_ACCEPTED_SESSION_LOAD_STATUSES,
            ).exists():
                continue

            created.append(Booking.objects.create(
                student=seed_tutee,
                tutor=tutor,
                availability=availability,
                session_date=session_date,
                session_mode='Online',
                status='Confirmed',
            ))

        return created

    def _next_date_for_day(self, day_name, today, window_end):
        if day_name not in WEEKDAY_NAMES:
            return None

        target = WEEKDAY_NAMES.index(day_name)
        offset = (target - today.weekday()) % 7
        session_date = today + timedelta(days=offset)
        return session_date if session_date < window_end else None

    def _remove(self):
        profile = UserProfile.objects.filter(user__username=SEED_TUTEE_USERNAME).first()
        if not profile:
            self.stdout.write('Nothing to remove — no seed tutee found.')
            return

        with transaction.atomic():
            deleted, _ = Booking.objects.filter(student=profile).delete()
            user = profile.user
            profile.delete()
            user.delete()

        self.stdout.write(self.style.SUCCESS(
            f'Removed the seed tutee and {deleted} related row(s).'
        ))
