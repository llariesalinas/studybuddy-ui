"""Deterministic demo-data seed for the subjects taxonomy reseed.

Seeds the Preply-style subject catalog, a small set of hand-curated tutor/tutee personas
engineered to exercise every CBF/CF formula component, and a larger Faker-generated filler
population, so the superadmin algorithm demo tool has something real to show. See
docs/plans/2026-07-16-subjects-taxonomy-reseed.md and
docs/learning/2026-07-16-algorithm-demo-cheat-sheet.md.

Run `python manage.py reset_demo_data` first on a non-empty database — this command refuses
to run if any non-staff data already exists, to keep seeding deterministic and idempotent.

Local/dev use only.
"""
import random
from datetime import timedelta
from decimal import Decimal
from uuid import uuid4

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from faker import Faker

from studybuddy.models import (
    Booking, Course, PartnerInstitution, Payment, PaymentMethod, Preference,
    Rating, Strand, Subjects, Tutor, TutorApplication, TutorAvailability,
    TutorSubjects, UserProfile, Wallet,
)
from studybuddy.subject_taxonomy import CATEGORIES, SUBJECTS, slugify_subject_code

from ._year_level_scale import YEAR_RANGE_BY_COURSE, random_year_level

SEED = 20260716
PASSWORD = 'studybuddy123'
PLACEHOLDER_SCHOOL_ID = 'demo/placeholder_school_id.png'
PLACEHOLDER_ENROLLMENT_PROOF = 'demo/placeholder_enrollment_proof.pdf'
INSTITUTION_DOMAIN = 'cpu.edu.ph'

DAY_CHOICES = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
RATING_SCORE_WEIGHTS = [2, 5, 20, 40, 33]  # bell-curved toward 4-5, matches prior seed style

STRANDS = [
    ('STEM', 'Science, Technology, Engineering, and Mathematics'),
    ('ABM', 'Accountancy, Business, and Management'),
    ('HUMSS', 'Humanities and Social Sciences'),
    ('GAS', 'General Academic Strand'),
    ('ELEM', 'Elementary Education Base'),
    ('JHS', 'Junior High School Base'),
]

COURSES = [
    ('ELEMENTARY', 'Elementary Curriculum (Grades 1-6)', 'ELEM'),
    ('JUNIOR_HIGH', 'Junior High Curriculum (Grades 7-10)', 'JHS'),
    ('SHS-STEM', 'Senior High - STEM Track', 'STEM'),
    ('SHS-ABM', 'Senior High - ABM Track', 'ABM'),
    ('SHS-HUMSS', 'Senior High - HUMSS Track', 'HUMSS'),
    ('SHS-GAS', 'Senior High - GAS Track', 'GAS'),
    ('BSCS', 'BS Computer Science (CPU-CCS)', 'STEM'),
    ('BSIT', 'BS Information Technology (CPU-CCS)', 'STEM'),
    ('BSBA', 'BS Business Administration (CPU-CBA)', 'ABM'),
]

# 1-2 taxonomy categories a course's tutors/tutees are drawn from, so filler subject picks
# read as coherent rather than uniform-random across the whole catalog.
COURSE_CATEGORY_AFFINITY = {
    'ELEMENTARY': ['Mathematics & Data Sciences', 'Humanities & Social Sciences'],
    'JUNIOR_HIGH': ['Mathematics & Data Sciences', 'Natural Sciences'],
    'SHS-STEM': ['Mathematics & Data Sciences', 'Natural Sciences'],
    'SHS-ABM': ['Business, Finance & Economics'],
    'SHS-HUMSS': ['Humanities & Social Sciences'],
    'SHS-GAS': ['Humanities & Social Sciences', 'Mathematics & Data Sciences'],
    'BSCS': ['Technology & Computer Science', 'Mathematics & Data Sciences'],
    'BSIT': ['Technology & Computer Science'],
    'BSBA': ['Business, Finance & Economics'],
}

TEACHING_LEVEL_CHOICES = ['Elementary', 'High School', 'College']
TEACHING_LEVEL_WEIGHTS = [15, 25, 60]

RESPONSE_TIME_CHOICES = ['within_1_hour', 'within_few_hours', 'within_a_day']
RESPONSE_TIME_LABELS = {
    'within_1_hour': 'within 1 hour',
    'within_few_hours': 'within a few hours',
    'within_a_day': 'within a day',
}

FILLER_TUTOR_COUNT = 150
FILLER_TUTEE_COUNT = 350

# Curated tutors: (key, fname, lname, course_code, year, teaching_level, can_online, can_f2f,
# hourly_rate, [(subject_name, expertise_level), ...])
CURATED_TUTORS = [
    ('T1', 'Marisol', 'Aquino', 'BSCS', 16, 'College', True, True, 350,
     [('Python', 5), ('Data Structures', 4), ('Algorithms', 4)]),
    ('T2', 'Benigno', 'Bautista', 'BSCS', 15, 'College', True, False, 280,
     [('C++', 3), ('Web Development', 3)]),
    ('T3', 'Corazon', 'Cruz', 'BSBA', 15, 'College', True, True, 300,
     [('Financial Accounting', 5), ('Microeconomics', 4)]),
    ('T4', 'Domingo', 'Diaz', 'BSCS', 16, 'College', True, False, 250,
     [('Python', 3)]),
    ('T5', 'Esperanza', 'Elizalde', 'SHS-STEM', 12, 'High School', True, False, 200,
     [('Python', 5)]),
    # Tier-1 programming core (see TIER1_TUTEE_KEYS): three more BSCS tutors so the
    # curated BSCS tutees have enough shared tutors to co-rate. Pearson runs over the
    # co-rated intersection only (CF.py), so a pair sharing 1 tutor scores 0 and is
    # dropped, and a pair sharing 2 always scores exactly +/-1 — neither is worth showing
    # a panel. Five shared tutors puts every pair at 3 or more.
    ('T6', 'Fidel', 'Fajardo', 'BSCS', 16, 'College', True, True, 320,
     [('Data Structures', 5), ('Algorithms', 4)]),
    ('T7', 'Gemma', 'Gatchalian', 'BSCS', 15, 'College', True, False, 290,
     [('Web Development', 5)]),
    ('T8', 'Hector', 'Hidalgo', 'BSCS', 16, 'College', True, True, 310,
     [('SQL', 4)]),
]

# Curated tutees: (key, fname, lname, course_code, year, [preferred_subject_name, ...])
CURATED_TUTEES = [
    ('S1', 'Felipe', 'Fernandez', 'BSCS', 14, ['Python', 'SQL']),
    ('S2', 'Gloria', 'Garcia', 'BSCS', 14, ['Python', 'Algorithms']),
    ('S3', 'Hernan', 'Herrera', 'BSCS', 15, ['Python', 'Data Structures']),
    ('S4', 'Imelda', 'Ignacio', 'BSCS', 13, ['SQL', 'Web Development']),
    ('S5', 'Jacinto', 'Jimenez', 'BSBA', 14, ['Financial Accounting', 'Marketing']),
    # S6 is the CF protagonist for the algorithm demo: a BSCS tutee with a real rating
    # history, as opposed to S1, who is deliberately left with none so the Cold-Start
    # path stays demonstrable. S6's preferences deliberately span Python/SQL/Data
    # Structures so the candidate pool comes out at five tutors — enough for the top-5
    # comparison table — and includes T5, whose High School teaching level zeroes the
    # Level sub-score against a college year.
    ('S6', 'Katrina', 'Katigbak', 'BSCS', 14, ['Python', 'SQL', 'Data Structures']),
    ('S7', 'Lorenzo', 'Lazaro', 'BSCS', 14, ['Python', 'Web Development']),
    ('S8', 'Milagros', 'Manalo', 'BSCS', 15, ['Web Development', 'C++']),
    ('S9', 'Nestor', 'Navarro', 'BSCS', 13, ['Web Development', 'SQL']),
    ('S10', 'Olivia', 'Ocampo', 'BSCS', 14, ['Python', 'Data Structures']),
]

# The BSCS tutees whose co-rating density the algorithm demo depends on. Enforced in
# _assert_guarantees: every pair must share at least MIN_CO_RATED tutors, and no pair may
# land on a degenerate +/-1 similarity.
TIER1_TUTEE_KEYS = ['S2', 'S3', 'S4', 'S6', 'S7', 'S8', 'S9', 'S10']
MIN_CO_RATED = 3

# Tier-1 programming core: eight BSCS tutees over five shared tutors, with deliberately
# opposed taste archetypes so Pearson lands on a believable spread instead of a wall of
# 1.00 — fundamentals-leaning (S2/S3/S10), mixed (S4/S7), web-leaning (S8/S9, which come
# out negative and are correctly filtered by the sim > 0 threshold in CF.top_k).
#
# Verified against a mirror of CF.py: relative to S6, similarities are S10 +0.970,
# S2 +0.853, S3 +0.852, S4 +0.308, and the CF prediction for T1 is
# 3.80 + (2.811 / 2.983) = 4.742, with S4 pulling backwards because he rated T1 below his
# own average. S6 rates T1 himself, which both makes T1 an already-rated candidate (so the
# demo can show prediction against actual) and puts T1 inside the co-rated set.
CURATED_RATINGS = [
    ('S6', 'T1', 5), ('S6', 'T2', 3), ('S6', 'T6', 5), ('S6', 'T7', 2), ('S6', 'T8', 4),
    ('S2', 'T1', 5), ('S2', 'T2', 3), ('S2', 'T6', 4), ('S2', 'T8', 4),
    ('S3', 'T1', 5), ('S3', 'T2', 2), ('S3', 'T6', 5), ('S3', 'T7', 3),
    ('S4', 'T1', 3), ('S4', 'T2', 2), ('S4', 'T7', 3), ('S4', 'T8', 5),
    ('S7', 'T1', 4), ('S7', 'T2', 4), ('S7', 'T6', 3), ('S7', 'T7', 4), ('S7', 'T8', 3),
    ('S8', 'T1', 2), ('S8', 'T2', 5), ('S8', 'T6', 2), ('S8', 'T7', 5),
    ('S9', 'T1', 3), ('S9', 'T2', 4), ('S9', 'T7', 5), ('S9', 'T8', 2),
    ('S10', 'T1', 4), ('S10', 'T2', 2), ('S10', 'T6', 5), ('S10', 'T7', 1), ('S10', 'T8', 3),
]

# Filler support ratings for T3/T4/T5, from courses that are NOT BSCS, so they never touch
# the tier-1 same-course CF neighborhood shared by S1 and S6. A side effect worth keeping:
# T4/T5 are candidates for S6 but have no BSCS peer rating them, so they fall through to the
# global pool and end up with no CF signal — the contrast that shows what CF contributes.
FILLER_SUPPORT_RATINGS = [
    ('T3', 'BSBA', [5, 4, 5]),
    ('T4', 'BSIT', [4, 4, 3]),
    ('T5', 'SHS-STEM', [5, 4, 4]),
]


class Command(BaseCommand):
    help = 'Seeds curated + filler demo data on the Preply-style subject taxonomy.'

    def handle(self, *args, **options):
        random.seed(SEED)
        Faker.seed(SEED)
        fake = Faker()

        if UserProfile.objects.filter(user__is_staff=False, user__is_superuser=False).exists():
            raise CommandError(
                'Non-staff data already exists. Run `python manage.py reset_demo_data` first.'
            )

        with transaction.atomic():
            self.stdout.write('Seeding academic foundation...')
            institution, courses_by_code = self._seed_academic_foundation()

            self.stdout.write('Seeding subject taxonomy...')
            subjects_by_category, subjects_by_name = self._seed_subjects()

            payment_methods = self._seed_payment_methods()

            self.stdout.write('Seeding curated personas...')
            curated = self._seed_curated_personas(
                institution, courses_by_code, subjects_by_name,
            )

            self.stdout.write(f'Seeding {FILLER_TUTOR_COUNT} filler tutors and '
                               f'{FILLER_TUTEE_COUNT} filler tutees...')
            fillers = self._seed_filler_population(
                fake, institution, courses_by_code, subjects_by_category,
            )

            self.stdout.write('Seeding bookings and ratings...')
            self._seed_bookings_and_ratings(curated, fillers, payment_methods)

            self.stdout.write('Recomputing tutor aggregates...')
            self._recompute_tutor_aggregates()

            self._assert_guarantees(curated, fillers)

        self.stdout.write(self.style.SUCCESS('Seeding complete.'))

    # ------------------------------------------------------------------ foundation

    def _seed_academic_foundation(self):
        for code, name in STRANDS:
            Strand.objects.update_or_create(
                strand_code=code, defaults={'strand_name': name},
            )

        for code, name, strand_code in COURSES:
            Course.objects.update_or_create(
                course_code=code,
                defaults={'course_name': name, 'strand_id': strand_code},
            )

        institution, _ = PartnerInstitution.objects.update_or_create(
            school_email_domain=INSTITUTION_DOMAIN,
            defaults={
                'institution_name': 'Central Philippine University',
                'is_active': True,
                'contact_person': 'Office of the Registrar / CCS Dean',
            },
        )

        courses_by_code = {
            c.course_code: c
            for c in Course.objects.filter(course_code__in=YEAR_RANGE_BY_COURSE)
        }
        return institution, courses_by_code

    def _seed_subjects(self):
        Subjects.objects.bulk_create([
            Subjects(
                subject_code=slugify_subject_code(name),
                subject_name=name,
                department=subgroup,
                category=category,
                status='approved',
            )
            for name, category, subgroup in SUBJECTS
        ])
        all_subjects = list(Subjects.objects.all())
        subjects_by_category = {category: [] for category in CATEGORIES}
        for subject in all_subjects:
            subjects_by_category.setdefault(subject.category, []).append(subject)
        subjects_by_name = {subject.subject_name: subject for subject in all_subjects}
        self.stdout.write(f'  seeded {len(all_subjects)} subjects across {len(CATEGORIES)} '
                           f'categories')
        return subjects_by_category, subjects_by_name

    def _seed_payment_methods(self):
        methods_data = [
            {'code': 'CASH', 'name': 'Cash Ledger'},
            {'code': 'PAYMONGO', 'name': 'PayMongo Online Framework (GCash/Maya)'},
        ]
        for m in methods_data:
            PaymentMethod.objects.get_or_create(
                code=m['code'], defaults={'method_name': m['name'], 'is_active': True},
            )
        return list(PaymentMethod.objects.filter(code__in=['CASH', 'PAYMONGO']))

    # ------------------------------------------------------------------ curated personas

    def _make_user(self, username, fname, lname, password_hash):
        return User(
            username=username, email=username, first_name=fname, last_name=lname,
            password=password_hash,
        )

    def _make_profile(self, user, fname, lname, role, course, year_level, institution, now):
        return UserProfile(
            user=user, fname=fname, lname=lname, role=role, course=course,
            year_level=year_level, bio=f'{role} at Central Philippine University.',
            profile_completed=True, institution=institution, is_suspended=False,
            created_at=now, updated_at=now,
        )

    def _make_tutor(self, profile, teaching_level, can_online, can_f2f, hourly_rate,
                     response_time, now):
        return Tutor(
            profile=profile, teaching_level=teaching_level, can_online=can_online,
            can_f2f=can_f2f, hourly_rate=Decimal(hourly_rate), rating_average=0,
            total_sessions=0, response_time=response_time,
            response_time_label=RESPONSE_TIME_LABELS[response_time], created_at=now,
        )

    def _make_tutor_application(self, profile, now):
        return TutorApplication(
            profile=profile, application_status='approved',
            school_id=PLACEHOLDER_SCHOOL_ID, enrollment_proof=PLACEHOLDER_ENROLLMENT_PROOF,
            submitted_at=now, updated_at=now, reviewed_at=now,
        )

    def _make_wallet(self, tutor, now):
        return Wallet(tutor=tutor, balance=Decimal('0.00'), pending_amount=Decimal('0.00'),
                       last_updated=now)

    def _contiguous_slots(self, start_hour, block_hours):
        import datetime
        slots = []
        current = datetime.datetime.combine(datetime.date.today(), datetime.time(start_hour, 0))
        end = current + datetime.timedelta(hours=block_hours)
        while current < end:
            slots.append(current.time())
            current += datetime.timedelta(minutes=30)
        return slots

    def _make_availability(self, tutor, now):
        rows = []
        days = random.sample(DAY_CHOICES, 3)
        for day in days:
            start_hour = random.randint(8, 13)
            block_hours = random.randint(4, 6)
            for time_slot in self._contiguous_slots(start_hour, block_hours):
                rows.append(TutorAvailability(
                    tutor=tutor, day=day, time_slot=time_slot, is_active=True,
                    is_booked=False, created_at=now,
                ))
        return rows

    def _seed_curated_personas(self, institution, courses_by_code, subjects_by_name):
        now = timezone.now()
        password_hash = make_password(PASSWORD)

        users, keys_in_order, profiles = [], [], []
        tutor_meta = []  # (key, fname, lname, teaching_level, can_online, can_f2f,
                          #  hourly_rate, subject_pairs)
        tutee_meta = []  # (key, fname, lname, preferred_names)

        for key, fname, lname, course_code, year, level, online, f2f, rate, subjects in \
                CURATED_TUTORS:
            username = f'{key.lower()}.{fname.lower()}.{lname.lower()}@{INSTITUTION_DOMAIN}'
            user = self._make_user(username, fname, lname, password_hash)
            users.append(user)
            keys_in_order.append(key)
            profiles.append((user, fname, lname, 'Tutor', courses_by_code[course_code], year))
            tutor_meta.append((key, fname, lname, level, online, f2f, rate, subjects))

        for key, fname, lname, course_code, year, preferred in CURATED_TUTEES:
            username = f'{key.lower()}.{fname.lower()}.{lname.lower()}@{INSTITUTION_DOMAIN}'
            user = self._make_user(username, fname, lname, password_hash)
            users.append(user)
            keys_in_order.append(key)
            profiles.append((user, fname, lname, 'Tutee', courses_by_code[course_code], year))
            tutee_meta.append((key, fname, lname, preferred))

        User.objects.bulk_create(users)

        profile_objs = [
            self._make_profile(user, fname, lname, role, course, year, institution, now)
            for user, fname, lname, role, course, year in profiles
        ]
        UserProfile.objects.bulk_create(profile_objs)

        profiles_by_key = dict(zip(keys_in_order, profile_objs))

        tutors_by_key = {}
        tutor_rows, application_rows, wallet_rows = [], [], []
        for key, fname, lname, level, online, f2f, rate, _subjects in tutor_meta:
            profile = profiles_by_key[key]
            response_time = random.choice(RESPONSE_TIME_CHOICES)
            tutor = self._make_tutor(profile, level, online, f2f, rate, response_time, now)
            tutors_by_key[key] = tutor
            tutor_rows.append(tutor)
            application_rows.append(self._make_tutor_application(profile, now))
            wallet_rows.append(self._make_wallet(tutor, now))

        Tutor.objects.bulk_create(tutor_rows)
        TutorApplication.objects.bulk_create(application_rows)
        Wallet.objects.bulk_create(wallet_rows)

        subject_rows, availability_rows = [], []
        for key, fname, lname, level, online, f2f, rate, subjects in tutor_meta:
            tutor = tutors_by_key[key]
            for subject_name, expertise in subjects:
                subject_rows.append(TutorSubjects(
                    tutor=tutor, subject=subjects_by_name[subject_name],
                    expertise_level=expertise,
                ))
            availability_rows.extend(self._make_availability(tutor, now))
        TutorSubjects.objects.bulk_create(subject_rows)
        TutorAvailability.objects.bulk_create(availability_rows)

        tutees_by_key = {}
        for key, fname, lname, preferred in tutee_meta:
            profile = profiles_by_key[key]
            tutees_by_key[key] = profile
            pref = Preference.objects.create(user=profile)
            pref.subjects.set([subjects_by_name[name] for name in preferred])

        return {'tutors_by_key': tutors_by_key, 'tutees_by_key': tutees_by_key}

    # ------------------------------------------------------------------ filler population

    def _seed_filler_population(self, fake, institution, courses_by_code, subjects_by_category):
        now = timezone.now()
        password_hash = make_password(PASSWORD)
        eligible_course_codes = [c for c in YEAR_RANGE_BY_COURSE if c in courses_by_code]

        tutor_users, tutor_profile_specs = [], []
        for i in range(FILLER_TUTOR_COUNT):
            fname, lname = fake.first_name(), fake.last_name()
            username = f'ftutor{i}.{fname.lower()}.{lname.lower()}@{INSTITUTION_DOMAIN}'
            course_code = random.choice(eligible_course_codes)
            year = random_year_level(course_code)
            tutor_users.append(self._make_user(username, fname, lname, password_hash))
            tutor_profile_specs.append((fname, lname, courses_by_code[course_code], year,
                                         course_code))

        tutee_users, tutee_profile_specs = [], []
        for i in range(FILLER_TUTEE_COUNT):
            fname, lname = fake.first_name(), fake.last_name()
            username = f'ftutee{i}.{fname.lower()}.{lname.lower()}@{INSTITUTION_DOMAIN}'
            course_code = random.choice(eligible_course_codes)
            year = random_year_level(course_code)
            tutee_users.append(self._make_user(username, fname, lname, password_hash))
            tutee_profile_specs.append((fname, lname, courses_by_code[course_code], year,
                                         course_code))

        User.objects.bulk_create(tutor_users)
        User.objects.bulk_create(tutee_users)

        tutor_profiles = [
            self._make_profile(user, fname, lname, 'Tutor', course, year, institution, now)
            for user, (fname, lname, course, year, _cc) in zip(tutor_users, tutor_profile_specs)
        ]
        UserProfile.objects.bulk_create(tutor_profiles)

        tutee_profiles = [
            self._make_profile(user, fname, lname, 'Tutee', course, year, institution, now)
            for user, (fname, lname, course, year, _cc) in zip(tutee_users, tutee_profile_specs)
        ]
        UserProfile.objects.bulk_create(tutee_profiles)

        tutor_rows, application_rows, wallet_rows = [], [], []
        for profile in tutor_profiles:
            level = random.choices(TEACHING_LEVEL_CHOICES, weights=TEACHING_LEVEL_WEIGHTS)[0]
            can_online = True
            can_f2f = random.random() < 0.3
            hourly_rate = random.randint(120, 450)
            response_time = random.choice(RESPONSE_TIME_CHOICES)
            tutor = self._make_tutor(
                profile, level, can_online, can_f2f, hourly_rate, response_time, now,
            )
            tutor_rows.append(tutor)
            application_rows.append(self._make_tutor_application(profile, now))
            wallet_rows.append(self._make_wallet(tutor, now))

        Tutor.objects.bulk_create(tutor_rows)
        TutorApplication.objects.bulk_create(application_rows)
        Wallet.objects.bulk_create(wallet_rows)

        subject_rows, availability_rows = [], []
        tutor_subjects_by_tutor = {}
        for tutor, (fname, lname, course, year, course_code) in zip(
            tutor_rows, tutor_profile_specs,
        ):
            categories = COURSE_CATEGORY_AFFINITY.get(course_code, list(CATEGORIES[:1]))
            candidates = [s for cat in categories for s in subjects_by_category.get(cat, [])]
            if not candidates:
                candidates = [s for group in subjects_by_category.values() for s in group]
            picks = random.sample(candidates, k=min(len(candidates), random.randint(2, 4)))
            tutor_subjects_by_tutor[tutor.profile_id] = picks
            for subject in picks:
                subject_rows.append(TutorSubjects(
                    tutor=tutor, subject=subject, expertise_level=random.randint(2, 5),
                ))
            availability_rows.extend(self._make_availability(tutor, now))

        TutorSubjects.objects.bulk_create(subject_rows)
        TutorAvailability.objects.bulk_create(availability_rows)

        tutee_subjects_by_tutee = {}
        for profile, (fname, lname, course, year, course_code) in zip(
            tutee_profiles, tutee_profile_specs,
        ):
            categories = COURSE_CATEGORY_AFFINITY.get(course_code, list(CATEGORIES[:1]))
            candidates = [s for cat in categories for s in subjects_by_category.get(cat, [])]
            if not candidates:
                candidates = [s for group in subjects_by_category.values() for s in group]
            picks = random.sample(candidates, k=min(len(candidates), random.randint(2, 4)))
            tutee_subjects_by_tutee[profile.pk] = picks
            pref = Preference.objects.create(user=profile)
            pref.subjects.set(picks)

        return {
            'tutors': tutor_rows,
            'tutees': tutee_profiles,
            'tutor_profile_specs': dict(zip(
                (t.profile_id for t in tutor_rows), tutor_profile_specs,
            )),
            'tutee_profile_specs': dict(zip(
                (p.pk for p in tutee_profiles), tutee_profile_specs,
            )),
            'tutor_subjects_by_tutor': tutor_subjects_by_tutor,
            'tutee_subjects_by_tutee': tutee_subjects_by_tutee,
        }

    # ------------------------------------------------------------------ bookings + ratings

    def _create_session(self, student, tutor, subject, availability_pool, used_pairs,
                         payment_methods, score):
        """Creates one Completed booking + payment + rating for (student, tutor).

        Returns True on success, False if no free (slot, date) pair could be found after
        a bounded number of attempts.
        """
        slots = availability_pool.get(tutor.profile_id) or []
        if not slots:
            return False

        for _attempt in range(20):
            slot = random.choice(slots)
            days_ago = random.randint(1, 90)
            session_date = timezone.now().date() - timedelta(days=days_ago)
            pair_key = (slot.pk, session_date)
            if pair_key in used_pairs:
                continue
            used_pairs.add(pair_key)

            session_mode = 'Online' if tutor.can_online else 'F2F'
            booking = Booking.objects.create(
                student=student, tutor=tutor, availability=slot, subject=subject,
                session_date=session_date, session_mode=session_mode, status='Completed',
                tutee_confirmed=True, tutor_confirmed=True,
                session_group_id=uuid4(), booking_request_id=uuid4(),
            )
            Payment.objects.create(
                booking=booking, method=random.choice(payment_methods),
                amount=tutor.hourly_rate, payment_status='Paid',
                transaction_reference=f'TXN-{uuid4().hex[:10].upper()}',
                paid_at=timezone.now(),
            )
            Rating.objects.create(
                booking=booking, student=student, tutor=tutor, rating_score=score,
                comment='Great session, learned a lot.' if score >= 3
                else 'Session covered the basics.',
            )
            return True

        return False

    def _pick_subject(self, tutor, student_subjects, tutor_subjects_by_tutor):
        tutor_subjects = tutor_subjects_by_tutor.get(tutor.profile_id) or []
        if not tutor_subjects:
            return None
        overlap = [s for s in tutor_subjects if s in student_subjects]
        return random.choice(overlap) if overlap else random.choice(tutor_subjects)

    def _seed_bookings_and_ratings(self, curated, fillers, payment_methods):
        used_pairs = set()
        availability_pool = {
            tutor.profile_id: list(
                TutorAvailability.objects.filter(tutor=tutor)
            )
            for tutor in list(curated['tutors_by_key'].values()) + fillers['tutors']
        }

        # Curated ratings: the scripted tier-1 CF story (S6 protagonist, S1 cold-start).
        for tutee_key, tutor_key, score in CURATED_RATINGS:
            student = curated['tutees_by_key'][tutee_key]
            tutor = curated['tutors_by_key'][tutor_key]
            subject = TutorSubjects.objects.filter(tutor=tutor).first().subject
            self._create_session(
                student, tutor, subject, availability_pool, used_pairs, payment_methods, score,
            )

        # Filler support ratings for T3/T4/T5 — designated non-BSCS cohorts, never touching
        # S1's BSCS same-course CF neighborhood.
        tutee_specs = fillers['tutee_profile_specs']
        tutees_by_course = {}
        for tutee in fillers['tutees']:
            course_code = tutee_specs[tutee.pk][4]
            tutees_by_course.setdefault(course_code, []).append(tutee)

        for tutor_key, course_code, scores in FILLER_SUPPORT_RATINGS:
            tutor = curated['tutors_by_key'][tutor_key]
            pool = tutees_by_course.get(course_code, [])
            chosen = pool[:len(scores)]
            for student, score in zip(chosen, scores):
                student_subjects = fillers['tutee_subjects_by_tutee'].get(student.pk, [])
                subject = self._pick_subject(
                    tutor, student_subjects, {tutor.profile_id: [
                        ts.subject for ts in TutorSubjects.objects.filter(tutor=tutor)
                    ]},
                )
                self._create_session(
                    student, tutor, subject, availability_pool, used_pairs, payment_methods,
                    score,
                )

        # Filler <-> filler sessions: every filler tutee rates 2 random filler tutors, which
        # also seeds most filler tutors past the 3-rating floor.
        filler_tutors = fillers['tutors']
        tutor_subjects_by_tutor = fillers['tutor_subjects_by_tutor']
        tutee_subjects_by_tutee = fillers['tutee_subjects_by_tutee']
        rating_counts = {tutor.profile_id: 0 for tutor in filler_tutors}

        for tutee in fillers['tutees']:
            chosen_tutors = random.sample(filler_tutors, k=min(2, len(filler_tutors)))
            for tutor in chosen_tutors:
                subject = self._pick_subject(
                    tutor, tutee_subjects_by_tutee.get(tutee.pk, []), tutor_subjects_by_tutor,
                )
                score = random.choices(range(1, 6), weights=RATING_SCORE_WEIGHTS)[0]
                if self._create_session(
                    tutee, tutor, subject, availability_pool, used_pairs, payment_methods,
                    score,
                ):
                    rating_counts[tutor.profile_id] += 1

        # Repair pass: top up any filler tutor still short of 3 ratings.
        short_tutors = [
            tutor for tutor in filler_tutors if rating_counts[tutor.profile_id] < 3
        ]
        for tutor in short_tutors:
            needed = 3 - rating_counts[tutor.profile_id]
            candidates = random.sample(fillers['tutees'], k=min(needed * 3, len(fillers['tutees'])))
            filled = 0
            for tutee in candidates:
                if filled >= needed:
                    break
                subject = self._pick_subject(
                    tutor, tutee_subjects_by_tutee.get(tutee.pk, []), tutor_subjects_by_tutor,
                )
                score = random.choices(range(1, 6), weights=RATING_SCORE_WEIGHTS)[0]
                if self._create_session(
                    tutee, tutor, subject, availability_pool, used_pairs, payment_methods,
                    score,
                ):
                    filled += 1
                    rating_counts[tutor.profile_id] += 1

    # ------------------------------------------------------------------ aggregates + checks

    def _recompute_tutor_aggregates(self):
        for tutor in Tutor.objects.all():
            ratings = Rating.objects.filter(tutor=tutor)
            completed = Booking.objects.filter(tutor=tutor, status='Completed').count()
            if ratings.exists():
                avg = sum(r.rating_score for r in ratings) / ratings.count()
                tutor.rating_average = round(avg, 2)
            tutor.total_sessions = completed
            tutor.save(update_fields=['rating_average', 'total_sessions'])

    def _assert_guarantees(self, curated, fillers):
        exempt_tutee_ids = {
            curated['tutees_by_key']['S1'].pk, curated['tutees_by_key']['S5'].pk,
        }

        all_tutors = list(curated['tutors_by_key'].values()) + fillers['tutors']
        for tutor in all_tutors:
            count = Rating.objects.filter(tutor=tutor).count()
            if count < 3:
                raise CommandError(
                    f'Guarantee violated: tutor profile {tutor.profile_id} has only '
                    f'{count} ratings (need >= 3).'
                )

        all_tutees = list(curated['tutees_by_key'].values()) + fillers['tutees']
        for tutee in all_tutees:
            if tutee.pk in exempt_tutee_ids:
                continue
            count = Rating.objects.filter(student=tutee).count()
            if count < 2:
                raise CommandError(
                    f'Guarantee violated: tutee profile {tutee.pk} has only {count} ratings '
                    f'given (need >= 2).'
                )

        self.stdout.write('  guarantees verified: every tutor >= 3 ratings received, every '
                           'non-exempt tutee >= 2 ratings given.')

        self._assert_tier1_co_rating_density(curated)

    def _assert_tier1_co_rating_density(self, curated):
        """The algorithm demo is only worth showing if similarity is a real number.

        CF.sim computes Pearson over the co-rated intersection, so a tier-1 pair sharing
        one tutor scores 0 and is dropped by the sim > 0 threshold, and a pair sharing
        exactly two always scores exactly +/-1 whatever the values are. Both produce a
        demo that either has no neighbors or shows a wall of 1.00. This asserts the
        density the curated matrix was designed for, so a later edit to CURATED_RATINGS
        cannot quietly reintroduce it.
        """
        from studybuddy.recommender.CF import sim

        ratings = {}
        for key in TIER1_TUTEE_KEYS:
            tutee = curated['tutees_by_key'][key]
            ratings[key] = {
                rating.tutor_id: rating.rating_score
                for rating in Rating.objects.filter(student=tutee)
            }

        for index, key in enumerate(TIER1_TUTEE_KEYS):
            for other in TIER1_TUTEE_KEYS[index + 1:]:
                shared = len(set(ratings[key]) & set(ratings[other]))
                if shared < MIN_CO_RATED:
                    raise CommandError(
                        f'Guarantee violated: tier-1 tutees {key} and {other} co-rate only '
                        f'{shared} tutors (need >= {MIN_CO_RATED}, or Pearson is degenerate).'
                    )

                similarity = sim(ratings, key, other)
                if abs(abs(similarity) - 1.0) < 1e-9:
                    raise CommandError(
                        f'Guarantee violated: tier-1 tutees {key} and {other} have a '
                        f'degenerate similarity of {similarity:+.3f}.'
                    )

        self.stdout.write(
            f'  guarantees verified: all {len(TIER1_TUTEE_KEYS)} tier-1 tutees co-rate '
            f'>= {MIN_CO_RATED} tutors pairwise with no degenerate similarity.'
        )
