"""Targeted clear + demo reseed for the thesis defense.

Clears demo-seedable data (Tutee/Tutor users and everything cascading from them,
plus PlatformActivity and InstitutionRequest) while preserving Admin/SuperAdmin
accounts, then reseeds the database so each of the thesis's 5 Specific Objectives
has named, discoverable scenarios. See docs/plans/2026-07-05-demo-data-reset.md
and docs/artifacts/2026-07-05-demo-data-testing-guide.md.

Local/dev use only — this command deletes data.
"""
import io
import random
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from uuid import uuid4

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker

from ._year_level_scale import COLLEGE_YEAR_OFFSET, YEAR_RANGE_BY_COURSE, random_year_level
from studybuddy.models import (
    Booking, Course, InstitutionCourseCatalog, InstitutionRequest, PartnerInstitution, Payment,
    PaymentMethod, PlatformActivity, Preference, Rating, Strand, Subjects,
    Transaction, Tutor, TutorApplication, TutorAvailability, TutorSubjects,
    TuteeApplication, UserProfile, Wallet, WalletTopUp, WithdrawalRequest,
)

SEED = 20260705
PASSWORD = 'studybuddy123'
BACKFILL_DAYS = 60          # history window for signups/bookings/transactions
RENEWAL_SAFE_DAYS = 60      # < 90-day renewal interval, keeps documents 'verified'
COMMISSION_RATE = Decimal('0.10')
INSTAPAY_CAP = Decimal('50000')
ZERO_RATING_SHARE = 0.15    # share of tutors deliberately left with no history
PLACEHOLDER_IMAGE = 'demo/placeholder_school_id.png'

WEEKDAY_BY_DAY = {'Mon': 0, 'Tue': 1, 'Wed': 2, 'Thu': 3, 'Fri': 4, 'Sat': 5, 'Sun': 6}

INSTITUTIONS = [
    {'domain': 'cpu.edu.ph', 'name': 'Central Philippine University',
     'contact': 'Office of the Registrar / CCS Dean'},
    {'domain': 'north.edu.ph', 'name': 'North University',
     'contact': 'Office of Student Affairs'},
]

# Per-institution pool sizes and tier split (tutees and tutors mirror each other
# so every tutee tier has legitimately matching tutors).
POOL_PER_INSTITUTION = 100
TIER_SPLIT = [
    ('ELEMENTARY', 15), ('JUNIOR_HIGH', 20),
    ('SHS-STEM', 7), ('SHS-ABM', 6), ('SHS-HUMSS', 6), ('SHS-GAS', 6),
    ('BSCS', 15), ('BSIT', 15), ('BSBA', 10),
]

# Subjects with tutee demand but deliberately zero tutor supply, so the admin
# dashboard's subject-demand "gap" indicator has a real case to show.
GAP_SUBJECT_CODES = {'GAS-DR', 'BUS-401'}

# Miguel Torres's core subjects are reserved from CPU filler tutors so the named
# CBF/CF scenarios stay top-ranked regardless of random filler profiles.
RESERVED_SUBJECT_CODES = {'CS-211', 'CS-212'}

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
    ('BSCS', 'BS Computer Science (CCS)', 'STEM'),
    ('BSIT', 'BS Information Technology (CCS)', 'STEM'),
    ('BSBA', 'BS Business Administration (CBA)', 'ABM'),
    # Intentionally seeded with no subjects/catalog entries: the empty course used
    # to demo the live "add subjects to a course" flow on the Admin Course Catalog.
    ('BA-POLSCI', 'Political Science', 'HUMSS'),
]

COURSE_CATEGORY_ALIASES = {
    'ABM': ('SHS-ABM',),
    'HUMMS': ('SHS-HUMSS',),
    'HUMSS': ('SHS-HUMSS',),
    'STEM': ('SHS-STEM',),
}

BASIC_ED_CORE = [
    ('ENG', 'English'), ('MTH', 'Mathematics'), ('SCI', 'Science'),
    ('FIL', 'Filipino'), ('AP', 'Araling Panlipunan'),
]

SHS_SUBJECTS = {
    'SHS-STEM': [
        ('STEM-PC', 'Pre-Calculus'), ('STEM-BC', 'Basic Calculus'),
        ('STEM-GP', 'General Physics 1'), ('STEM-GC', 'General Chemistry 1'),
    ],
    'SHS-ABM': [
        ('ABM-FAB', 'Fundamentals of Accountancy & Business 1'), ('ABM-BM', 'Business Mathematics'),
        ('ABM-OM', 'Organization and Management'), ('ABM-AE', 'Applied Economics'),
    ],
    'SHS-HUMSS': [
        ('HUM-CW', 'Creative Writing'), ('HUM-DI', 'Disciplines & Ideas in the Social Sciences'),
        ('HUM-PG', 'Philippine Politics and Governance'), ('HUM-TR', 'Trends, Networks & Critical Thinking'),
    ],
    'SHS-GAS': [
        ('GAS-RS', 'Practical Research 1'), ('GAS-HP', 'Humanities 1'),
        ('GAS-EM', 'Elective Mathematics'), ('GAS-DR', 'Disaster Readiness and Risk Reduction'),
    ],
}

COLLEGE_SUBJECTS = {
    'BSCS': {
        1: [('CS-111', 'CS 111 - Introduction to Computing'), ('CS-112', 'CS 112 - Computer Programming 1')],
        2: [('CS-211', 'CS 211 - Data Structures and Algorithms'), ('CS-212', 'CS 212 - Discrete Structures 1')],
        3: [('CS-311', 'CS 311 - Information Management'), ('CS-321', 'CS 321 - Design and Analysis of Algorithms')],
        4: [('CS-412', 'CS 412 - Artificial Intelligence'), ('CS-421', 'CS 421 - Software Engineering 2')],
    },
    'BSIT': {
        1: [('IT-111', 'IT 111 - Introduction to Computing Technology'), ('IT-112', 'IT 112 - Programming Fundamentals')],
        2: [('IT-212', 'IT 212 - Web Systems and Technologies 1'), ('IT-221', 'IT 221 - Database Management Systems 1')],
        3: [('IT-312', 'IT 312 - Web Systems 2'), ('IT-313', 'IT 313 - Information Assurance and Security 1')],
        4: [('IT-411', 'IT 411 - Systems Integration and Architecture'), ('IT-412', 'IT 412 - Capstone Project 1')],
    },
    'BSBA': {
        1: [('BUS-101', 'BUS 101 - Principles of Business Management'), ('ACC-101', 'ACC 101 - Accounting Principles')],
        2: [('BUS-201', 'BUS 201 - Marketing Management'), ('ECO-201', 'ECO 201 - Managerial Economics')],
        3: [('BUS-301', 'BUS 301 - Human Resource Management'), ('FIN-301', 'FIN 301 - Financial Management')],
        4: [('BUS-401', 'BUS 401 - Strategic Management'), ('BUS-402', 'BUS 402 - Business Research')],
    },
}

DEPARTMENT_BY_COURSE = {
    'BSCS': 'Computer Science', 'BSIT': 'Information Technology', 'BSBA': 'Business',
    'SHS-STEM': 'STEM', 'SHS-ABM': 'ABM', 'SHS-HUMSS': 'HUMSS', 'SHS-GAS': 'GAS',
}

AVAILABILITY_ARCHETYPES = [
    # (days pool, days count, start-hour range, block hours) — deliberate variety
    ('wide',    ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'], 5, (8, 10), 6),
    ('standard', ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'], 3, (8, 13), 4),
    ('evening', ['Mon', 'Tue', 'Wed', 'Thu'], 3, (17, 17), 3),
    ('weekend', ['Sat', 'Sun'], 2, (8, 12), 5),
]

# --- Named personas (all CPU) -----------------------------------------------------------------
PERSONA_TUTEES = {
    'bea':   {'fname': 'Bea', 'lname': 'Santos', 'course': 'BSCS', 'year': 14,
              'prefs': ['CS-211', 'CS-212'],
              'story': 'Cold-Start Tutee: no rating history, Hybrid = 0.7 * CBF only'},
    'carlo': {'fname': 'Carlo', 'lname': 'Reyes', 'course': 'BSCS', 'year': 15,
              'prefs': ['CS-211', 'CS-311'],
              'story': 'CBF and CF agree: both point at Miguel Torres'},
    'diane': {'fname': 'Diane', 'lname': 'Cruz', 'course': 'BSCS', 'year': 14,
              'prefs': ['CS-211'],
              'story': 'CF overrides CBF: neighbors pull ranking to Elena Bautista'},
}

PERSONA_TUTORS = {
    'miguel': {'fname': 'Miguel', 'lname': 'Torres', 'course': 'BSCS', 'year': 15,
               'teaching_level': 'College', 'rate': 300,
               'subjects': [('CS-211', 5), ('CS-212', 4), ('CS-311', 4)],
               'story': 'Tutor Alpha: strongest CBF fit; loved by Cluster A, panned by Cluster B'},
    'elena':  {'fname': 'Elena', 'lname': 'Bautista', 'course': 'BSIT', 'year': 15,
               'teaching_level': 'College', 'rate': 280,
               'subjects': [('CS-211', 2), ('IT-221', 5), ('IT-212', 4)],
               'story': 'Tutor Beta: weaker CBF fit but beloved by Cluster B - the CF-override target'},
    'anchor1': {'fname': 'Ramon', 'lname': 'Aquino', 'course': 'BSCS', 'year': 16,
                'teaching_level': 'College', 'rate': 250,
                'subjects': [('CS-111', 4), ('CS-112', 4)],
                'story': 'CF anchor: rated by every cluster member, creating the Pearson signal'},
    'anchor2': {'fname': 'Cecilia', 'lname': 'Mercado', 'course': 'BSIT', 'year': 16,
                'teaching_level': 'College', 'rate': 250,
                'subjects': [('IT-111', 4), ('IT-112', 3)],
                'story': 'CF anchor: the second shared rated tutor Pearson similarity needs'},
    'nico':   {'fname': 'Nico', 'lname': 'Villareal', 'course': 'BSIT', 'year': 14,
               'teaching_level': 'College', 'rate': 200,
               'subjects': [('IT-212', 3), ('IT-221', 3)],
               'story': 'Brand-new tutor: zero sessions, zero ratings (empty-state UI)'},
    'grace':  {'fname': 'Grace', 'lname': 'Domingo', 'course': 'BSCS', 'year': 16,
               'teaching_level': 'College', 'rate': 320,
               'subjects': [('CS-311', 5), ('CS-321', 4)],
               'story': 'Fully-booked: Accepted Session Load 10/10 - new accepts blocked'},
    'paolo':  {'fname': 'Paolo', 'lname': 'Ramirez', 'course': 'BSIT', 'year': 16,
               'teaching_level': 'College', 'rate': 310,
               'subjects': [('IT-312', 5), ('IT-313', 4)],
               'story': 'Near-limit: Accepted Session Load 8/10 - still accepting'},
    'isabel': {'fname': 'Isabel', 'lname': 'Fernandez', 'course': 'BSBA', 'year': 16,
               'teaching_level': 'College', 'rate': 450,
               'subjects': [('ACC-101', 5), ('FIN-301', 5), ('BUS-201', 4)],
               'story': 'High-earner: heavy session history, top-ups, withdrawals in every state'},
}

ADMINS = [
    {'email': 'demo.admin@cpu.edu.ph', 'fname': 'Carmen', 'lname': 'Ledesma', 'domain': 'cpu.edu.ph'},
    {'email': 'demo.admin@north.edu.ph', 'fname': 'Victor', 'lname': 'Salcedo', 'domain': 'north.edu.ph'},
]

# 1x1 white PNG so ImageField paths resolve to a real file in media/.
PLACEHOLDER_PNG_BYTES = bytes.fromhex(
    '89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489'
    '0000000d49444154789c626001000000ffff03000006000557bfabd40000000049454e44ae426082'
)


class Command(BaseCommand):
    help = ('DESTRUCTIVE (local/dev only): clears demo data (preserving Admin/SuperAdmin logins) '
            'and reseeds named thesis-defense scenarios. See docs/plans/2026-07-05-demo-data-reset.md.')

    # ------------------------------------------------------------------ helpers

    def _now(self):
        return timezone.localtime(timezone.now())

    def _today(self):
        return self._now().date()

    def _growth_days_ago(self, max_days=BACKFILL_DAYS):
        """Growth-shaped backdating: skews toward the present so trend charts rise."""
        return int(max_days * (random.random() ** 1.8))

    def _aware(self, d, hour=10):
        return timezone.make_aware(datetime.combine(d, time(hour, 0)))

    def _backdate(self, model, pk_to_dt, field='created_at'):
        """Backdate an auto_now_add field. Groups pks by date to keep query count low."""
        buckets = {}
        for pk, dt in pk_to_dt.items():
            buckets.setdefault(dt, []).append(pk)
        for dt, pks in buckets.items():
            model.objects.filter(pk__in=pks).update(**{field: dt})

    def _slot_dates(self, slot, weeks_back, used):
        """Past dates for a slot that fall on the slot's weekday, oldest first."""
        today = self._today()
        weekday = WEEKDAY_BY_DAY[slot.day]
        days_back_to_weekday = (today.weekday() - weekday) % 7 or 7
        first = today - timedelta(days=days_back_to_weekday)
        dates = []
        for w in range(weeks_back):
            d = first - timedelta(weeks=w)
            if (slot.pk, d) not in used:
                dates.append(d)
        return dates

    def _pick_completed_date(self, slots, used):
        """Random (slot, past date) pair honoring the slot's weekday and uniqueness."""
        random.shuffle(slots)
        for slot in slots:
            weeks_ago = 1 + self._growth_days_ago(7)  # 1..8 weeks, recent-weighted
            candidates = self._slot_dates(slot, 9, used)
            if not candidates:
                continue
            d = candidates[min(weeks_ago - 1, len(candidates) - 1)]
            used.add((slot.pk, d))
            return slot, d
        return None, None

    # ------------------------------------------------------------------ handle

    def handle(self, *args, **options):
        random.seed(SEED)
        Faker.seed(SEED)
        self.fake = Faker()
        self.password_hash = make_password(PASSWORD)
        self.used_slot_dates = set()
        self.summary = []

        self.stdout.write('reset_demo_data: targeted clear + thesis demo reseed (local/dev only)')

        self._clear()
        self._ensure_placeholder_image()
        institutions = self._seed_catalog()
        self._ensure_admins(institutions)
        pools = self._seed_user_pools(institutions)
        personas = self._seed_personas(institutions['cpu.edu.ph'], pools)
        self._seed_subjects_and_preferences(pools, personas)
        self._seed_availability(pools, personas)
        self._seed_bookings_and_ratings(pools, personas)
        self._seed_cluster_scenarios(pools, personas)
        self._seed_load_limit_scenarios(pools, personas)
        self._seed_compensation(pools, personas)
        self._recompute_tutor_aggregates()
        self._seed_operational_queue(institutions)
        self._seed_activity_feed(institutions)
        self._print_summary(personas)

    # ------------------------------------------------------------------ phases

    def _clear(self):
        """Delete demo data; Admin/SuperAdmin users and catalog rows survive."""
        demo_users = User.objects.filter(userprofile__role__in=['Tutee', 'Tutor'])
        deleted, _ = demo_users.delete()  # cascades profiles, tutors, bookings, wallets, ...
        InstitutionCourseCatalog.objects.all().delete()
        PlatformActivity.objects.all().delete()
        InstitutionRequest.objects.all().delete()
        self.stdout.write(f'  cleared: {deleted} rows cascaded from Tutee/Tutor users')

    def _ensure_placeholder_image(self):
        if not default_storage.exists(PLACEHOLDER_IMAGE):
            default_storage.save(PLACEHOLDER_IMAGE, io.BytesIO(PLACEHOLDER_PNG_BYTES))

    def _seed_catalog(self):
        for code, name in STRANDS:
            Strand.objects.update_or_create(strand_code=code, defaults={'strand_name': name})
        for code, name, strand in COURSES:
            Course.objects.update_or_create(
                course_code=code,
                defaults={'course_name': name, 'strand': Strand.objects.get(strand_code=strand)},
            )
        # Drop stray courses from older/manual seeds (e.g. bare STEM/ABM/HUMMS duplicates)
        # so the course picker only shows the defined set. UserProfile.course is SET_NULL and
        # catalog entries CASCADE, so this never deletes users. Pruning before catalog seeding
        # also prevents duplicate alias entries (bare STEM matching SHS-STEM subjects).
        defined_course_codes = [c[0] for c in COURSES]
        pruned_courses, _ = Course.objects.exclude(course_code__in=defined_course_codes).delete()
        if pruned_courses:
            self.stdout.write(f'  pruned {pruned_courses} stray course row(s)')

        subject_rows = []
        for grade in range(1, 7):
            for suffix, base in BASIC_ED_CORE:
                subject_rows.append((f'G{grade}-{suffix}', f'{base} {grade}', f'Grade {grade}', 'ELEMENTARY'))
        for grade in range(7, 11):
            for suffix, base in BASIC_ED_CORE:
                subject_rows.append((f'G{grade}-{suffix}', f'{base} {grade}', f'Grade {grade}', 'JUNIOR_HIGH'))
        for course_code, subs in SHS_SUBJECTS.items():
            for code, name in subs:
                subject_rows.append((code, name, DEPARTMENT_BY_COURSE[course_code], course_code))
        for course_code, years in COLLEGE_SUBJECTS.items():
            for year, subs in years.items():
                for code, name in subs:
                    subject_rows.append((code, name, DEPARTMENT_BY_COURSE[course_code], course_code))

        for code, name, dept, course_code in subject_rows:
            Subjects.objects.update_or_create(
                subject_code=code,
                defaults={'subject_name': name, 'department': dept, 'category': course_code},
            )
        # Legacy catalog rows from older seeds would clutter dropdowns; every row
        # referencing them was already cascade-deleted in the clear phase.
        Subjects.objects.exclude(subject_code__in=[r[0] for r in subject_rows]).delete()

        for pm_code, pm_name in [('CASH', 'Cash Ledger'), ('PAYMONGO', 'PayMongo Online (GCash/Maya)')]:
            PaymentMethod.objects.get_or_create(code=pm_code, defaults={'method_name': pm_name, 'is_active': True})

        institutions = {}
        for inst in INSTITUTIONS:
            obj, _ = PartnerInstitution.objects.update_or_create(
                school_email_domain=inst['domain'],
                defaults={'institution_name': inst['name'], 'is_active': True,
                          'contact_person': inst['contact']},
            )
            institutions[inst['domain']] = obj

        # Drop stray test institutions (e.g. a.com/b.com) so no orphan institution lingers
        # with an empty catalog. Only prune ones with no attached profiles, so a real
        # Admin/SuperAdmin account is never left institution-less by mistake.
        keep_domains = [inst['domain'] for inst in INSTITUTIONS]
        stray_pks = list(
            PartnerInstitution.objects.exclude(school_email_domain__in=keep_domains)
            .filter(userprofile__isnull=True)
            .values_list('pk', flat=True)
        )
        if stray_pks:
            pruned_institutions, _ = PartnerInstitution.objects.filter(pk__in=stray_pks).delete()
            self.stdout.write(f'  pruned {pruned_institutions} stray institution row(s)')

        self._seed_institution_course_catalog(institutions, subject_rows)

        self.summary.append(f'Subjects: {len(subject_rows)} across all tiers')
        self.stdout.write(f'  catalog: {len(subject_rows)} subjects, {len(INSTITUTIONS)} institutions')
        return institutions

    def _seed_institution_course_catalog(self, institutions, subject_rows):
        north = institutions['north.edu.ph']
        subjects_by_code = {subject.subject_code: subject for subject in Subjects.objects.all()}
        courses_by_code = {course.course_code: course for course in Course.objects.all()}
        courses_by_subject_category = {}
        for course_code, course in courses_by_code.items():
            categories = {course_code, *COURSE_CATEGORY_ALIASES.get(course_code, ())}
            for category in categories:
                courses_by_subject_category.setdefault(category, []).append(course)

        rows = []
        for subject_code, _name, _dept, course_code in subject_rows:
            subject = subjects_by_code.get(subject_code)
            matching_courses = courses_by_subject_category.get(course_code, [])
            if not matching_courses or not subject:
                continue

            for institution in institutions.values():
                for course in matching_courses:
                    rows.append(
                        InstitutionCourseCatalog(
                            institution=institution,
                            course=course,
                            subject=subject,
                        )
                    )

        custom_subject, _ = Subjects.objects.update_or_create(
            subject_code='NORTH-AI-LAB',
            defaults={
                'subject_name': 'North AI Lab',
                'department': 'Computer Science',
                'category': 'BSCS',
                'owning_institution': north,
            },
        )
        rows.append(
            InstitutionCourseCatalog(
                institution=north,
                course=courses_by_code['BSCS'],
                subject=custom_subject,
            )
        )

        InstitutionCourseCatalog.objects.bulk_create(rows, ignore_conflicts=True)
        self.summary.append(f'Institution course catalog entries: {len(rows)} seeded')
        self.stdout.write(f'  institution catalogs: {len(rows)} course-subject entries seeded')

    def _ensure_admins(self, institutions):
        for admin in ADMINS:
            user, created = User.objects.get_or_create(
                username=admin['email'],
                defaults={'email': admin['email'], 'first_name': admin['fname'],
                          'last_name': admin['lname'], 'password': self.password_hash},
            )
            UserProfile.objects.get_or_create(
                user=user,
                defaults={'fname': admin['fname'], 'lname': admin['lname'], 'role': 'Admin',
                          'profile_completed': True, 'is_suspended': False,
                          'institution': institutions[admin['domain']]},
            )
            self.stdout.write(f"  admin ready: {admin['email']}{' (created)' if created else ''}")

    def _course_year(self, course_code):
        return random_year_level(course_code)

    def _tier_assignments(self):
        out = []
        for course_code, count in TIER_SPLIT:
            out.extend([course_code] * count)
        assert len(out) == POOL_PER_INSTITUTION
        return out

    def _seed_user_pools(self, institutions):
        """Bulk filler pool: 100 tutees + 100 tutors per institution, tier-mirrored."""
        courses = {c.course_code: c for c in Course.objects.all()}
        reserved_names = {(p['fname'], p['lname']) for p in
                          list(PERSONA_TUTEES.values()) + list(PERSONA_TUTORS.values())}
        now = self._now()
        pools = {}

        for domain, institution in institutions.items():
            tag = domain.split('.', 1)[0]
            users, profiles_meta = [], []
            for role in ('Tutee', 'Tutor'):
                for i, course_code in enumerate(self._tier_assignments()):
                    fname, lname = self.fake.first_name(), self.fake.last_name()
                    while (fname, lname) in reserved_names:
                        fname, lname = self.fake.first_name(), self.fake.last_name()
                    email = f'{role.lower()}.{fname.lower()}.{lname.lower()}.{tag}{i}@{domain}'
                    joined = now - timedelta(days=self._growth_days_ago(),
                                             hours=random.randint(0, 12))
                    users.append(User(username=email, email=email, first_name=fname,
                                      last_name=lname, password=self.password_hash,
                                      date_joined=joined))
                    profiles_meta.append((role, course_code, fname, lname))

            users = User.objects.bulk_create(users)
            profiles = UserProfile.objects.bulk_create([
                UserProfile(user=user, fname=meta[2], lname=meta[3], role=meta[0],
                            course=courses[meta[1]], year_level=self._course_year(meta[1]),
                            bio=self.fake.sentence(nb_words=12), profile_completed=True,
                            institution=institution, is_suspended=False)
                for user, meta in zip(users, profiles_meta)
            ])

            tutee_profiles = [p for p in profiles if p.role == 'Tutee']
            tutor_profiles = [p for p in profiles if p.role == 'Tutor']
            tutors = Tutor.objects.bulk_create([
                Tutor(profile=p,
                      teaching_level='College' if p.course_id in COLLEGE_SUBJECTS else
                      random.choice(['High School', 'Both']),
                      can_online=True,
                      can_f2f=random.random() < 0.5,
                      hourly_rate=random.randint(120, 450),
                      rating_average=0, total_sessions=0)
                for p in tutor_profiles
            ])
            # bulk_create skips the post_save signal that normally creates wallets.
            Wallet.objects.bulk_create([Wallet(tutor=t) for t in tutors])
            self._approve_applications(tutor_profiles, tutee_profiles)

            pools[domain] = {'institution': institution, 'tutees': tutee_profiles,
                             'tutors': tutors, 'courses': courses}
            self.stdout.write(f'  {domain}: {len(tutee_profiles)} tutees, {len(tutors)} tutors')
        return pools

    def _approve_applications(self, tutor_profiles, tutee_profiles):
        """Approved + verified documents, or tutors could never accept bookings
        (can_create_new_booking requires it) and the load-limit demo would be
        blocked by the wrong gate. reviewed_at stays inside the 90-day renewal
        interval so document_renewal_status() reads 'verified'."""
        def reviewed_at(profile):
            joined = profile.user.date_joined
            return min(joined + timedelta(days=random.randint(1, 3)), self._now())

        TutorApplication.objects.bulk_create([
            TutorApplication(profile=p, application_status='approved',
                             reviewed_at=reviewed_at(p), school_id=PLACEHOLDER_IMAGE,
                             enrollment_proof=PLACEHOLDER_IMAGE)
            for p in tutor_profiles
        ])
        TuteeApplication.objects.bulk_create([
            TuteeApplication(profile=p, application_status='approved',
                             reviewed_at=reviewed_at(p), school_id=PLACEHOLDER_IMAGE,
                             enrollment_proof=PLACEHOLDER_IMAGE)
            for p in tutee_profiles
        ])

    def _seed_personas(self, cpu, pools):
        """Fixed-name CPU personas; filler cluster members drawn from the CPU pool."""
        courses = pools['cpu.edu.ph']['courses']
        now = self._now()
        personas = {'tutees': {}, 'tutors': {}}

        for key, spec in PERSONA_TUTEES.items():
            email = f"{spec['fname'].lower()}.{spec['lname'].lower()}@cpu.edu.ph"
            user = User.objects.create(username=email, email=email, first_name=spec['fname'],
                                       last_name=spec['lname'], password=self.password_hash,
                                       date_joined=now - timedelta(days=random.randint(20, 45)))
            profile = UserProfile.objects.create(
                user=user, fname=spec['fname'], lname=spec['lname'], role='Tutee',
                course=courses[spec['course']], year_level=spec['year'],
                bio=spec['story'], profile_completed=True, institution=cpu, is_suspended=False)
            self._approve_applications([], [profile])
            personas['tutees'][key] = profile

        for key, spec in PERSONA_TUTORS.items():
            email = f"{spec['fname'].lower()}.{spec['lname'].lower()}@cpu.edu.ph"
            joined_days = random.randint(3, 7) if key == 'nico' else random.randint(35, 55)
            user = User.objects.create(username=email, email=email, first_name=spec['fname'],
                                       last_name=spec['lname'], password=self.password_hash,
                                       date_joined=now - timedelta(days=joined_days))
            profile = UserProfile.objects.create(
                user=user, fname=spec['fname'], lname=spec['lname'], role='Tutor',
                course=courses[spec['course']], year_level=spec['year'],
                bio=spec['story'], profile_completed=True, institution=cpu, is_suspended=False)
            tutor = Tutor.objects.create(profile=profile, teaching_level=spec['teaching_level'],
                                         can_online=True, can_f2f=True,
                                         hourly_rate=spec['rate'], rating_average=0,
                                         total_sessions=0)
            # Tutor.objects.create fires the wallet signal; no manual Wallet needed.
            self._approve_applications([profile], [])
            personas['tutors'][key] = tutor

        # Cluster members: CPU BSCS/BSIT filler tutees, removed from the generic
        # rating pool so their Top-K Neighbor sets stay exactly as engineered.
        cpu_pool = pools['cpu.edu.ph']
        college_tutees = [p for p in cpu_pool['tutees'] if p.course_id in ('BSCS', 'BSIT')]
        random.shuffle(college_tutees)
        personas['cluster_a'] = [personas['tutees']['carlo']] + college_tutees[:5]
        personas['cluster_b'] = [personas['tutees']['diane']] + college_tutees[5:11]
        cluster_filler = set(p.pk for p in college_tutees[:11])
        cpu_pool['generic_tutees'] = [p for p in cpu_pool['tutees'] if p.pk not in cluster_filler]

        self.stdout.write(f"  personas: {len(personas['tutees'])} tutees, {len(personas['tutors'])} tutors, "
                          f"clusters A={len(personas['cluster_a'])} B={len(personas['cluster_b'])}")
        return personas

    def _subjects_for(self, profile, all_subjects, for_tutor):
        """Tier- and year-appropriate subject codes for a profile."""
        course = profile.course_id
        if course in ('ELEMENTARY', 'JUNIOR_HIGH'):
            grades = range(max(1 if course == 'ELEMENTARY' else 7, profile.year_level - 1),
                           profile.year_level + 1)
            candidates = [s for s in all_subjects
                          if s.category == course and any(f'G{g}-' in s.subject_code for g in grades)]
        elif course in SHS_SUBJECTS:
            candidates = [s for s in all_subjects if s.category == course]
        else:
            # profile.year_level is on the app's unified scale (college = 13-16);
            # COLLEGE_SUBJECTS is keyed by the plain 1-4 college year, so rebase it.
            college_year = profile.year_level - COLLEGE_YEAR_OFFSET
            years = range(1, college_year + 1) if for_tutor else \
                    range(max(1, college_year - 1), min(4, college_year + 1) + 1)
            year_codes = {code for y in years for code, _ in COLLEGE_SUBJECTS[course].get(y, [])}
            candidates = [s for s in all_subjects if s.subject_code in year_codes]
        if for_tutor:
            candidates = [s for s in candidates
                          if s.subject_code not in GAP_SUBJECT_CODES
                          and s.subject_code not in RESERVED_SUBJECT_CODES]
        return candidates

    def _seed_subjects_and_preferences(self, pools, personas):
        all_subjects = list(Subjects.objects.all())
        by_code = {s.subject_code: s for s in all_subjects}

        # ~15% of tutors (incl. Nico) deliberately keep zero history for the
        # empty-state UI. Special-role personas are excluded from that pool.
        zero_pool = set()
        ts_rows, pref_links, pref_rows = [], [], []

        for domain, pool in pools.items():
            tutors = pool['tutors']
            zero_count = int(len(tutors) * ZERO_RATING_SHARE)
            zero_pool.update(t.pk for t in random.sample(tutors, zero_count))

            for tutor in tutors:
                picks = self._subjects_for(tutor.profile, all_subjects, for_tutor=True)
                for s in random.sample(picks, min(len(picks), random.randint(2, 4))):
                    ts_rows.append(TutorSubjects(tutor=tutor, subject=s,
                                                 expertise_level=random.randint(2, 5)))
            gap_added = {'GAS-DR': 0, 'BUS-401': 0}
            for tutee in pool['tutees']:
                picks = self._subjects_for(tutee, all_subjects, for_tutor=False)
                chosen = random.sample(picks, min(len(picks), random.randint(2, 3)))
                # Guarantee demand for the gap subjects: first few matching-tier
                # tutees always want them, so the dashboard indicator has real data.
                gap = {'SHS-GAS': 'GAS-DR', 'BSBA': 'BUS-401'}.get(tutee.course_id)
                if gap and gap_added[gap] < 3:
                    if by_code[gap] not in chosen:
                        chosen.append(by_code[gap])
                    gap_added[gap] += 1
                pref_rows.append((tutee, chosen))

        for key, spec in PERSONA_TUTORS.items():
            tutor = personas['tutors'][key]
            for code, level in spec['subjects']:
                ts_rows.append(TutorSubjects(tutor=tutor, subject=by_code[code],
                                             expertise_level=level))
        for key, spec in PERSONA_TUTEES.items():
            pref_rows.append((personas['tutees'][key], [by_code[c] for c in spec['prefs']]))

        TutorSubjects.objects.bulk_create(ts_rows)
        self.subjects_by_tutor = {}
        for row in ts_rows:
            self.subjects_by_tutor.setdefault(row.tutor_id, []).append(row.subject)
        prefs = Preference.objects.bulk_create([Preference(user=p) for p, _ in pref_rows])
        through = Preference.subjects.through
        for pref, (_, subjects) in zip(prefs, pref_rows):
            pref_links.extend(through(preference_id=pref.pk, subjects_id=s.pk) for s in subjects)
        through.objects.bulk_create(pref_links, ignore_conflicts=True)

        for pool in pools.values():
            pool['zero_pool'] = zero_pool
        self.stdout.write(f'  subjects assigned: {len(ts_rows)} tutor-subjects, {len(prefs)} preferences, '
                          f'{len(zero_pool)} zero-history tutors reserved')

    def _seed_availability(self, pools, personas):
        rows = []

        def build_for(tutor, archetype):
            _, day_pool, day_count, (h_lo, h_hi), block_hours = archetype
            for day in random.sample(day_pool, day_count):
                start = random.randint(h_lo, h_hi)
                cursor = datetime.combine(date.today(), time(start, 0))
                for _ in range(block_hours * 2):
                    rows.append(TutorAvailability(tutor=tutor, day=day,
                                                  time_slot=cursor.time(),
                                                  is_active=True, is_booked=False))
                    cursor += timedelta(minutes=30)

        for pool in pools.values():
            for i, tutor in enumerate(pool['tutors']):
                build_for(tutor, AVAILABILITY_ARCHETYPES[i % len(AVAILABILITY_ARCHETYPES)])
        for tutor in personas['tutors'].values():
            build_for(tutor, AVAILABILITY_ARCHETYPES[0])  # personas get wide schedules

        TutorAvailability.objects.bulk_create(rows)
        self.slots_by_tutor = {}
        for slot in TutorAvailability.objects.all():
            self.slots_by_tutor.setdefault(slot.tutor_id, []).append(slot)
        self.stdout.write(f'  availability: {len(rows)} slots across varied archetypes')

    def _make_booking(self, tutee, tutor, slot, session_date, status, **extra):
        session_mode = extra.pop('session_mode', 'Online' if tutor.can_online else 'F2F')
        subject = extra.pop('subject', None) or random.choice(
            self.subjects_by_tutor.get(tutor.pk) or [None]
        )
        return Booking(student=tutee, tutor=tutor, availability=slot,
                       session_date=session_date,
                       subject=subject,
                       session_mode=session_mode,
                       status=status, session_group_id=uuid4(), booking_request_id=uuid4(),
                       tutee_confirmed=status in ('Confirmed', 'Completed'),
                       tutor_confirmed=status in ('Confirmed', 'Completed'), **extra)

    def _seed_bookings_and_ratings(self, pools, personas):
        """Generic terminal-only pool: Completed / Cancelled / Rejected."""
        excluded = {t.pk for k, t in personas['tutors'].items()
                    if k in ('miguel', 'elena', 'anchor1', 'anchor2', 'nico')}
        bookings, cancelled = [], []

        for domain, pool in pools.items():
            tutees = pool.get('generic_tutees', pool['tutees'])
            candidates = [t for t in pool['tutors']
                          if t.pk not in pool['zero_pool'] and t.pk not in excluded]
            if domain == 'cpu.edu.ph':
                # Grace/Paolo need believable terminal history behind their
                # in-flight load-limit bookings; Isabel gets hers separately.
                candidates += [personas['tutors']['grace'], personas['tutors']['paolo']]
            for tutor in candidates:
                slots = self.slots_by_tutor.get(tutor.pk, [])
                for _ in range(random.randint(2, 10)):
                    slot, d = self._pick_completed_date(list(slots), self.used_slot_dates)
                    if slot is None:
                        break
                    bookings.append(self._make_booking(random.choice(tutees), tutor, slot, d, 'Completed'))
                for _ in range(random.randint(0, 3)):  # terminal failures for a real completion rate
                    slot, d = self._pick_completed_date(list(slots), self.used_slot_dates)
                    if slot is None:
                        break
                    status = random.choice(['Cancelled', 'Rejected'])
                    extra = ({'cancellation_reason': 'Schedule conflict',
                              'cancelled_by_role': random.choice(['tutee', 'tutor'])}
                             if status == 'Cancelled' else {})
                    cancelled.append(self._make_booking(random.choice(tutees), tutor, slot, d, status, **extra))

        created = Booking.objects.bulk_create(bookings + cancelled)
        self._create_payments_and_ratings([b for b in created if b.status == 'Completed'],
                                          [b for b in created if b.status != 'Completed'])
        self.stdout.write(f'  bookings: {len(bookings)} completed, {len(cancelled)} cancelled/rejected')

    def _create_payments_and_ratings(self, completed, terminal_failures, fixed_scores=None):
        methods = list(PaymentMethod.objects.all())
        payments, ratings, booking_dates, rating_dates = [], {}, {}, {}

        for b in completed:
            paid_at = self._aware(b.session_date, hour=19)
            payments.append(Payment(booking=b, method=random.choice(methods),
                                    amount=b.tutor.hourly_rate, payment_status='Paid',
                                    paid_at=paid_at,
                                    transaction_reference=f'TXN-{uuid4().hex[:10].upper()}'))
            booking_dates[b.pk] = self._aware(b.session_date - timedelta(days=random.randint(1, 5)))
            score = (fixed_scores or {}).get(b.pk) or \
                random.choices([1, 2, 3, 4, 5], weights=[2, 5, 20, 40, 33], k=1)[0]
            first_for_tutor = b.tutor_id not in ratings
            if fixed_scores or first_for_tutor or random.random() < 0.85:
                ratings.setdefault(b.tutor_id, []).append(Rating(
                    booking=b, student=b.student, tutor=b.tutor, rating_score=score,
                    comment=self.fake.sentence(nb_words=10)))
                rating_dates[b.pk] = self._aware(b.session_date + timedelta(days=1))

        for b in terminal_failures:
            payments.append(Payment(booking=b, method=random.choice(methods),
                                    amount=b.tutor.hourly_rate,
                                    payment_status='Refunded' if b.status == 'Cancelled' else 'Failed'))
            booking_dates[b.pk] = self._aware(b.session_date - timedelta(days=random.randint(1, 5)))

        Payment.objects.bulk_create(payments)
        flat_ratings = [r for rs in ratings.values() for r in rs]
        created_ratings = Rating.objects.bulk_create(flat_ratings)
        self._backdate(Booking, booking_dates)
        self._backdate(Rating, {r.pk: rating_dates[r.booking_id]
                                for r in created_ratings if r.booking_id in rating_dates})
        return created_ratings

    def _seed_cluster_scenarios(self, pools, personas):
        """Engineered rating clusters. Pearson sim() needs >= 2 shared rated tutors
        with non-identical scores per tutee, so every member rates both anchors.
        The two clusters use INVERTED anchor patterns (A: anchor1 high / anchor2
        low; B: the opposite) — with identical patterns the clusters would be
        indistinguishable, Top-K Neighbors would mix both, and their opposing
        Miguel ratings would average out instead of driving the CF override."""
        t = personas['tutors']
        plan = []  # (tutee, tutor, score)

        for member in personas['cluster_a']:
            plan.append((member, t['anchor1'], random.choice([5, 4])))
            plan.append((member, t['anchor2'], random.choice([1, 2])))
            if member.pk != personas['tutees']['carlo'].pk:
                plan.append((member, t['miguel'], random.choice([5, 5, 4])))
        for member in personas['cluster_b']:
            plan.append((member, t['anchor1'], random.choice([1, 2])))
            plan.append((member, t['anchor2'], random.choice([5, 4])))
            if member.pk != personas['tutees']['diane'].pk:
                plan.append((member, t['elena'], random.choice([5, 5, 4])))
                plan.append((member, t['miguel'], random.choice([2, 1, 2])))

        bookings, scores = [], {}
        for tutee, tutor, score in plan:
            slots = list(self.slots_by_tutor.get(tutor.pk, []))
            slot, d = self._pick_completed_date(slots, self.used_slot_dates)
            if slot is None:
                raise RuntimeError(f'No free slot for cluster booking with {tutor}')
            bookings.append(self._make_booking(tutee, tutor, slot, d, 'Completed'))
        created = Booking.objects.bulk_create(bookings)
        for b, (_, _, score) in zip(created, plan):
            scores[b.pk] = score
        self._create_payments_and_ratings(created, [], fixed_scores=scores)
        self.stdout.write(f'  clusters: {len(plan)} engineered ratings (A={len(personas["cluster_a"])}, '
                          f'B={len(personas["cluster_b"])} members)')

    def _future_slot_dates(self, tutor, count):
        """(slot, future date) pairs on the slot's weekday within the next 3 weeks."""
        today = self._today()
        out = []
        for slot in self.slots_by_tutor.get(tutor.pk, []):
            weekday = WEEKDAY_BY_DAY[slot.day]
            days_ahead = (weekday - today.weekday()) % 7 or 7
            for w in range(3):
                d = today + timedelta(days=days_ahead, weeks=w)
                if (slot.pk, d) not in self.used_slot_dates:
                    out.append((slot, d))
        random.shuffle(out)
        return out[:count]

    def _seed_load_limit_scenarios(self, pools, personas):
        """The plan's one in-flight exception: Grace at 10/10 (blocked), Paolo at 8/10."""
        cpu_tutees = pools['cpu.edu.ph']['generic_tutees']
        bookings = []
        for key, target in (('grace', 10), ('paolo', 8)):
            tutor = personas['tutors'][key]
            pairs = self._future_slot_dates(tutor, target)
            if len(pairs) < target:
                raise RuntimeError(f'Not enough future slots for {key} ({len(pairs)}/{target})')
            for i, (slot, d) in enumerate(pairs):
                self.used_slot_dates.add((slot.pk, d))
                status = 'Awaiting Payment Verification' if i < 2 else 'Confirmed'
                bookings.append(self._make_booking(random.choice(cpu_tutees), tutor, slot, d, status))
        created = Booking.objects.bulk_create(bookings)
        Payment.objects.bulk_create([
            Payment(booking=b, method=PaymentMethod.objects.get(code='PAYMONGO'),
                    amount=b.tutor.hourly_rate, payment_status='Pending')
            for b in created
        ])
        loads = {k: personas['tutors'][k].accepted_session_load() for k in ('grace', 'paolo')}
        self.stdout.write(f"  load limits: Grace {loads['grace']}/10, Paolo {loads['paolo']}/10")

    def _seed_compensation(self, pools, personas):
        """Wallets, transactions, top-ups, and withdrawals that actually reconcile:
        balance = 0.9 * gross + top-ups - processed - pending; pending_amount = pending."""
        isabel = personas['tutors']['isabel']

        # Isabel's heavy history: ~60 completed sessions across the window.
        tutees = pools['cpu.edu.ph']['generic_tutees']
        bookings = []
        for _ in range(60):
            slot, d = self._pick_completed_date(list(self.slots_by_tutor[isabel.pk]),
                                                self.used_slot_dates)
            if slot is None:
                break
            bookings.append(self._make_booking(random.choice(tutees), isabel, slot, d, 'Completed'))
        created = Booking.objects.bulk_create(bookings)
        self._create_payments_and_ratings(created, [])

        # Session credits + commission per paid booking, backdated with the session.
        tx_rows, tx_dates = [], []
        wallets = {w.tutor_id: w for w in Wallet.objects.select_related('tutor')}
        earnings = {}
        paymongo_method = PaymentMethod.objects.get(code='PAYMONGO')
        cash_method = PaymentMethod.objects.get(code='CASH')

        # Isabel is deliberately excluded here: she's the "high-earner" persona with a
        # PHP 55,000 top-up and ~60 completed sessions (below), so a couple of PHP-30-45
        # cash commissions would never make a dent. Miguel gets the visible cash
        # bookings/receipts for the demo; his actual debt is guaranteed below rather than
        # assumed, since he also picks up ~10 payments from _seed_cluster_scenarios with a
        # random PAYMONGO/CASH split that this function has no visibility into in advance.
        cash_demo_specs = [
            ('miguel', 3),
        ]
        cash_bookings = []
        for tutor_key, booking_count in cash_demo_specs:
            tutor = personas['tutors'][tutor_key]
            slots = list(self.slots_by_tutor[tutor.pk])
            for _ in range(booking_count):
                slot, d = self._pick_completed_date(slots, self.used_slot_dates)
                if slot is None:
                    break
                cash_bookings.append(
                    self._make_booking(
                        random.choice(tutees),
                        tutor,
                        slot,
                        d,
                        'Completed',
                        session_mode='F2F',
                        preferred_location='CPU Main Library',
                    )
                )

        created_cash_bookings = Booking.objects.bulk_create(cash_bookings)
        Payment.objects.bulk_create([
            Payment(
                booking=booking,
                method=cash_method,
                amount=booking.tutor.hourly_rate,
                payment_status='Paid',
                paid_at=self._aware(booking.session_date, hour=19),
                receipt_image=PLACEHOLDER_IMAGE,
            )
            for booking in created_cash_bookings
        ])
        self._backdate(
            Booking,
            {
                booking.pk: self._aware(booking.session_date - timedelta(days=random.randint(1, 5)))
                for booking in created_cash_bookings
            },
        )

        for p in Payment.objects.filter(payment_status='Paid').select_related('booking'):
            wallet = wallets[p.booking.tutor_id]
            amount = Decimal(p.amount)
            commission = (amount * COMMISSION_RATE).quantize(Decimal('0.01'))
            dt = self._aware(p.booking.session_date, hour=20)
            if p.method_id == paymongo_method.method_id:
                tutor_share = amount - commission
                tx_rows.append(Transaction(wallet=wallet, transaction_type='session_credit',
                                           amount=tutor_share, description=f'Session credit (booking {p.booking_id})',
                                           reference_id=str(p.booking_id)))
                tx_dates.append(dt)
                earnings[wallet.pk] = earnings.get(wallet.pk, Decimal('0')) + tutor_share
            elif p.method_id == cash_method.method_id:
                tx_rows.append(Transaction(wallet=wallet, transaction_type='commission_deduction',
                                           amount=-commission, description='Platform commission (10%)',
                                           reference_id=str(p.booking_id)))
                tx_dates.append(dt)
                earnings[wallet.pk] = earnings.get(wallet.pk, Decimal('0')) - commission
        created_tx = Transaction.objects.bulk_create(tx_rows)
        self._backdate(Transaction, {t.pk: d for t, d in zip(created_tx, tx_dates)})

        # Guarantee Miguel actually lands negative for the wallet-debt-banner demo. His
        # cluster-rating sessions (_seed_cluster_scenarios) use a random PAYMONGO/CASH split
        # we don't control here, so his running total after the loop above could plausibly
        # still be positive even with his 3 cash sessions counted. Rather than guessing at a
        # session count that "should" work, force it: top up his cash-commission deduction
        # just enough to cross zero, framed as one more settled cash session's commission.
        miguel_wallet = wallets[personas['tutors']['miguel'].pk]
        miguel_earnings = earnings.get(miguel_wallet.pk, Decimal('0'))
        if miguel_earnings >= 0:
            debt_amount = miguel_earnings + Decimal('75.00')
            debt_tx = Transaction.objects.create(
                wallet=miguel_wallet, transaction_type='commission_deduction',
                amount=-debt_amount,
                description='Platform commission (10%) - cash session settlement',
                reference_id=f'DEBT-{miguel_wallet.pk}',
            )
            self._backdate(Transaction, {debt_tx.pk: self._now() - timedelta(days=1)})
            earnings[miguel_wallet.pk] = miguel_earnings - debt_amount

        # Isabel: top-ups justify a near-cap cash-out that session earnings alone couldn't.
        isabel_wallet = wallets[isabel.pk]
        topup = WalletTopUp.objects.create(tutor=isabel, amount=Decimal('55000'), status='paid',
                                           provider='paymongo', provider_reference=f'TOPUP-{uuid4().hex[:8]}',
                                           paid_at=self._now() - timedelta(days=20))
        cash_in = Transaction.objects.create(wallet=isabel_wallet, transaction_type='cash_in',
                                             amount=topup.amount, description='Wallet top-up (PayMongo)',
                                             reference_id=str(topup.pk))
        self._backdate(Transaction, {cash_in.pk: self._now() - timedelta(days=20)})
        earnings[isabel_wallet.pk] = earnings.get(isabel_wallet.pk, Decimal('0')) + topup.amount

        # Withdrawals across every outcome state; Isabel's pending one sits near the cap.
        rated = list(Tutor.objects.exclude(ratings=None)
                     .exclude(pk__in=[p.pk for p in personas['tutors'].values()])
                     .distinct()[:4])
        wd_specs = [
            (isabel, Decimal('12000'), 'processed', ''),
            (isabel, Decimal('48500'), 'pending', ''),
        ] + [
            (rated[0], Decimal('900'), 'processed', ''),
            (rated[1], Decimal('500'), 'rejected', 'Account name mismatch'),
            (rated[2], Decimal('750'), 'failed', 'Receiving institution unavailable'),
            (rated[3], Decimal('400'), 'flagged', 'Manual review: rapid successive requests'),
        ]
        wd_dates = {}
        # Terminal (processed/failed) payouts also log a PlatformActivity, mirroring
        # log_cash_out_activity (views.py), so auto-processed payouts show in the admin feed.
        payout_activity, payout_activity_dates = [], []
        for tutor, amount, status_, reason in wd_specs:
            assert amount <= INSTAPAY_CAP
            wd = WithdrawalRequest.objects.create(
                tutor=tutor, amount=amount, method='gcash',
                receiving_institution_name='GCash', account_number='09170000000',
                account_name=f'{tutor.profile.fname} {tutor.profile.lname}',
                status=status_, failure_reason=reason or None,
                net_amount=amount,
                processed_at=self._now() - timedelta(days=5) if status_ == 'processed' else None)
            wd_dates[wd.pk] = self._now() - timedelta(days=random.randint(2, 15))
            wallet = wallets[tutor.pk]
            if status_ == 'processed':
                Transaction.objects.create(wallet=wallet, transaction_type='withdrawal',
                                           amount=-amount, description='Cash-out (InstaPay)',
                                           reference_id=str(wd.pk))
                earnings[wallet.pk] = earnings.get(wallet.pk, Decimal('0')) - amount
            elif status_ == 'pending':
                wallet.pending_amount = amount
                earnings[wallet.pk] = earnings.get(wallet.pk, Decimal('0')) - amount
            if status_ in ('processed', 'failed'):
                payout_activity.append(PlatformActivity(
                    activity_type=f'withdrawal_{status_}',
                    message=f'Cash-out #{wd.id} for {tutor.profile.fname} {status_}',
                    institution=tutor.profile.institution))
                payout_activity_dates.append(self._now() - timedelta(days=random.randint(1, 6)))
        self._backdate(WithdrawalRequest, wd_dates, field='requested_at')

        created_payout_activity = PlatformActivity.objects.bulk_create(payout_activity)
        self._backdate(PlatformActivity,
                       {a.pk: d for a, d in zip(created_payout_activity, payout_activity_dates)})

        for wallet in wallets.values():
            wallet.balance = earnings.get(wallet.pk, Decimal('0'))
        Wallet.objects.bulk_update(wallets.values(), ['balance', 'pending_amount'])
        self.stdout.write(f'  compensation: {len(created_tx) + 1} transactions, '
                          f'{len(wd_specs)} withdrawals, Isabel balance '
                          f'{earnings.get(isabel_wallet.pk)}, Miguel balance '
                          f'{earnings.get(miguel_wallet.pk)} (must be negative for the debt banner demo)')

    def _recompute_tutor_aggregates(self):
        for tutor in Tutor.objects.all():
            agg = tutor.ratings.all()
            completed = tutor.tutor_bookings.filter(status='Completed').count()
            if agg.exists():
                tutor.rating_average = round(sum(r.rating_score for r in agg) / agg.count(), 2)
            tutor.total_sessions = completed
            tutor.save(update_fields=['rating_average', 'total_sessions'])

    def _seed_operational_queue(self, institutions):
        """Pending applications live on dedicated new applicants, never active users —
        a pending application would block an active tutor from accepting work."""
        now = self._now()
        courses = {c.course_code: c for c in Course.objects.all()}
        specs = [('Tutor', 'cpu.edu.ph', 3), ('Tutor', 'north.edu.ph', 2),
                 ('Tutee', 'cpu.edu.ph', 2), ('Tutee', 'north.edu.ph', 1)]
        for role, domain, count in specs:
            for i in range(count):
                fname, lname = self.fake.first_name(), self.fake.last_name()
                email = f'applicant.{role.lower()}.{fname.lower()}{i}@{domain}'
                user = User.objects.create(username=email, email=email, first_name=fname,
                                           last_name=lname, password=self.password_hash,
                                           date_joined=now - timedelta(days=random.randint(0, 3)))
                profile = UserProfile.objects.create(
                    user=user, fname=fname, lname=lname, role=role,
                    course=courses['BSIT'], year_level=random_year_level('BSIT'),
                    profile_completed=True, institution=institutions[domain], is_suspended=False)
                model = TutorApplication if role == 'Tutor' else TuteeApplication
                model.objects.create(profile=profile, application_status='pending',
                                     school_id=PLACEHOLDER_IMAGE, enrollment_proof=PLACEHOLDER_IMAGE)
        InstitutionRequest.objects.create(
            institution_name='Western Visayas College', school_email_domain='wvc.edu.ph',
            contact_person='Registrar - L. Hervias', contact_email='registrar@wvc.edu.ph',
            note='Requesting partnership for the incoming semester.', status='pending')
        self.stdout.write('  queue: 8 pending applications + 1 institution request')

    def _seed_activity_feed(self, institutions):
        entries, dates = [], []
        samples = [
            ('registration', 'New {role} registered: {name}'),
            ('booking_completed', 'Session completed: {name}'),
            ('tutor_application', 'Tutor application submitted by {name}'),
        ]
        profiles = list(UserProfile.objects.filter(role__in=['Tutee', 'Tutor'])
                        .select_related('institution')[:200])
        for _ in range(36):
            profile = random.choice(profiles)
            activity_type, template = random.choice(samples)
            entries.append(PlatformActivity(
                activity_type=activity_type,
                message=template.format(role=profile.role.lower(),
                                        name=f'{profile.fname} {profile.lname}')[:255],
                institution=profile.institution))
            dates.append(self._now() - timedelta(days=self._growth_days_ago(30),
                                                 hours=random.randint(0, 20)))
        entries.append(PlatformActivity(activity_type='withdrawal_failed',
                                        message='Withdrawal failed: receiving institution unavailable',
                                        institution=institutions['cpu.edu.ph']))
        dates.append(self._now() - timedelta(days=2))
        created = PlatformActivity.objects.bulk_create(entries)
        self._backdate(PlatformActivity, {e.pk: d for e, d in zip(created, dates)})
        self.stdout.write(f'  activity feed: {len(created)} entries')

    def _print_summary(self, personas):
        w = self.stdout.write
        w(self.style.SUCCESS('\nDemo data ready. All demo passwords: ' + PASSWORD))
        w('\n== Logins ==')
        w('  SuperAdmin: (your existing account - untouched)')
        for admin in ADMINS:
            w(f"  Admin ({admin['domain']}): {admin['email']}")
        w('\n== Personas (all @cpu.edu.ph) ==')
        for key, spec in PERSONA_TUTEES.items():
            w(f"  Tutee  {spec['fname']} {spec['lname']:<12} "
              f"{spec['fname'].lower()}.{spec['lname'].lower()}@cpu.edu.ph - {spec['story']}")
        for key, spec in PERSONA_TUTORS.items():
            w(f"  Tutor  {spec['fname']} {spec['lname']:<12} "
              f"{spec['fname'].lower()}.{spec['lname'].lower()}@cpu.edu.ph - {spec['story']}")
        w('\n== Counts ==')
        for label, qs in [
            ('Users', User.objects.all()), ('Tutors', Tutor.objects.all()),
            ('Tutees', UserProfile.objects.filter(role='Tutee')),
            ('Subjects', Subjects.objects.all()), ('Availability slots', TutorAvailability.objects.all()),
            ('Bookings', Booking.objects.all()),
            ('  completed', Booking.objects.filter(status='Completed')),
            ('  in-flight (load-limit demo)', Booking.objects.filter(
                status__in=['Confirmed', 'Awaiting Payment Verification'])),
            ('Ratings', Rating.objects.all()), ('Payments', Payment.objects.all()),
            ('Transactions', Transaction.objects.all()),
            ('Withdrawal requests', WithdrawalRequest.objects.all()),
            ('Platform activity', PlatformActivity.objects.all()),
            ('Pending applications', TutorApplication.objects.filter(application_status='pending')),
        ]:
            w(f'  {label}: {qs.count()}')
        w(self.style.SUCCESS('\nSee docs/artifacts/2026-07-05-demo-data-testing-guide.md '
                             'for per-objective walkthroughs.'))
