from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from faker import Faker
from studybuddy.models import (
    Strand, Course, PartnerInstitution, Subjects,
    UserProfile, Tutor, TutorSubjects, TutorAvailability,
    Booking, Payment, PaymentMethod, Rating, Preference
)
import datetime
import random
from uuid import uuid4

fake = Faker()

class Command(BaseCommand):
    help = 'Seeds the database with explicit, cascading, and rich academic parameters for thesis evaluation'

    def handle(self, *args, **options):
        self.stdout.write("Starting seeding process...")

        # 1. Seed Strands (The Foundations)
        strands_data = [
            {'code': 'STEM', 'name': 'Science, Technology, Engineering, and Mathematics'},
            {'code': 'ABM', 'name': 'Accountancy, Business, and Management'},
            {'code': 'HUMSS', 'name': 'Humanities and Social Sciences'},
            {'code': 'GAS', 'name': 'General Academic Strand'},
            {'code': 'ELEM', 'name': 'Elementary Education Base'},
            {'code': 'JHS', 'name': 'Junior High School Base'},
        ]

        for s in strands_data:
            obj, created = Strand.objects.update_or_create(
                strand_code=s['code'],
                defaults={'strand_name': s['name']}
            )
            status = "Created" if created else "Updated"
            self.stdout.write(f"  - Strand {s['code']}: {status}")

        # 2. Seed Partner Institutions (Crucial to prevent dropdown registration crashes)
        inst_obj, created = PartnerInstitution.objects.update_or_create(
            school_email_domain='cpu.edu.ph',
            defaults={
                'institution_name': 'Central Philippine University',
                'is_active': True,
                'contact_person': 'Office of the Registrar / CCS Dean'
            }
        )
        self.stdout.write(f"  - Institution {inst_obj.school_email_domain}: {'Created' if created else 'Updated'}")

        # 3. Seed Comprehensive Academic Program Course Blocks
        # For Elementary and JHS, we introduce virtual course containers so the cascading frontend dropdown works universally
        courses_data = [
            {'code': 'ELEMENTARY', 'name': 'Elementary Curriculum (Grades 1-6)', 'strand': 'ELEM'},
            {'code': 'JUNIOR_HIGH', 'name': 'Junior High Curriculum (Grades 7-10)', 'strand': 'JHS'},
            {'code': 'SHS-STEM', 'name': 'Senior High - STEM Track', 'strand': 'STEM'},
            {'code': 'SHS-ABM', 'name': 'Senior High - ABM Track', 'strand': 'ABM'},
            {'code': 'SHS-HUMSS', 'name': 'Senior High - HUMSS Track', 'strand': 'HUMSS'},
            {'code': 'SHS-GAS', 'name': 'Senior High - GAS Track', 'strand': 'GAS'},
            {'code': 'BSCS', 'name': 'BS Computer Science (CPU-CCS)', 'strand': 'STEM'},
            {'code': 'BSIT', 'name': 'BS Information Technology (CPU-CCS)', 'strand': 'STEM'},
            {'code': 'BSBA', 'name': 'BS Business Administration (CPU-CBA)', 'strand': 'ABM'},
        ]

        for c in courses_data:
            strand_obj = Strand.objects.get(strand_code=c['strand'])
            obj, created = Course.objects.update_or_create(
                course_code=c['code'],
                defaults={
                    'course_name': c['name'],
                    'strand': strand_obj
                }
            )
            self.stdout.write(f"  - Course Container {c['code']}: {'Created' if created else 'Updated'}")

        # 4. Seed Subjects with Explicit Course Constraints
        # CRITICAL REFINEMENT: Links every single subject row directly to a matching parent course model code target
        subjects_data = [
            # --- ELEMENTARY SUBSET (Grades 1-6) ---
            {'code': 'G1-ENG',  'name': 'English 1 (Primary Literacy)', 'dept': 'Grade 1', 'course': 'ELEMENTARY'},
            {'code': 'G1-MTH',  'name': 'Mathematics 1 (Basic Arithmetic)', 'dept': 'Grade 1', 'course': 'ELEMENTARY'},
            {'code': 'G1-FIL',  'name': 'Filipino 1 (Wika)', 'dept': 'Grade 1', 'course': 'ELEMENTARY'},
            {'code': 'G2-SCI',  'name': 'Science 2 (The Living World)', 'dept': 'Grade 2', 'course': 'ELEMENTARY'},
            {'code': 'G3-MTH',  'name': 'Mathematics 3 (Fractions & Multipliers)', 'dept': 'Grade 3', 'course': 'ELEMENTARY'},
            {'code': 'G4-ENG',  'name': 'English 4 (Grammar & Syntax)', 'dept': 'Grade 4', 'course': 'ELEMENTARY'},
            {'code': 'G5-SCI',  'name': 'Science 5 (Environmental Ecology)', 'dept': 'Grade 5', 'course': 'ELEMENTARY'},
            {'code': 'G6-EPP',  'name': 'EPP 6 (Home Economics & ICT Basics)', 'dept': 'Grade 6', 'course': 'ELEMENTARY'},

            # --- JUNIOR HIGH SUBSET (Grades 7-10) ---
            {'code': 'G7-ENG',  'name': 'English 7 (Philippine Literature)', 'dept': 'Grade 7', 'course': 'JUNIOR_HIGH'},
            {'code': 'G7-MTH',  'name': 'Mathematics 7 (Algebra & Set Theory)', 'dept': 'Grade 7', 'course': 'JUNIOR_HIGH'},
            {'code': 'G7-SCI',  'name': 'Integrated Science 7', 'dept': 'Grade 7', 'course': 'JUNIOR_HIGH'},
            {'code': 'G8-FIL',  'name': 'Filipino 8 (Florante at Laura)', 'dept': 'Grade 8', 'course': 'JUNIOR_HIGH'},
            {'code': 'G8-MTH',  'name': 'Mathematics 8 (Geometry Structures)', 'dept': 'Grade 8', 'course': 'JUNIOR_HIGH'},
            {'code': 'G9-CHM',  'name': 'Chemistry 9 (Atomic Logic Matrices)', 'dept': 'Grade 9', 'course': 'JUNIOR_HIGH'},
            {'code': 'G9-AP',   'name': 'Araling Panlipunan 9 (Ekonomiks)', 'dept': 'Grade 9', 'course': 'JUNIOR_HIGH'},
            {'code': 'G10-PHY', 'name': 'Physics 10 (Mechanics & Waves)', 'dept': 'Grade 10', 'course': 'JUNIOR_HIGH'},

            # --- SENIOR HIGH TRACKS (STEM, ABM, HUMSS, GAS) ---
            {'code': 'STEM-PC', 'name': 'Pre-Calculus (Trigonometry & Conic Sections)', 'dept': 'STEM', 'course': 'SHS-STEM'},
            {'code': 'STEM-BC', 'name': 'Basic Calculus (Limits & Derivatives)', 'dept': 'STEM', 'course': 'SHS-STEM'},
            {'code': 'STEM-GP', 'name': 'General Physics 1 (Vectors & Mechanics)', 'dept': 'STEM', 'course': 'SHS-STEM'},
            {'code': 'ABM-FAB', 'name': 'Fundamentals of Accountancy & Business 1', 'dept': 'ABM', 'course': 'SHS-ABM'},
            {'code': 'ABM-BM',  'name': 'Business Mathematics', 'dept': 'ABM', 'course': 'SHS-ABM'},
            {'code': 'HUM-CW',  'name': 'Creative Writing / Malikhaing Pagsulat', 'dept': 'HUMSS', 'course': 'SHS-HUMSS'},
            {'code': 'HUM-DI',  'name': 'Disciplines & Ideas in the Social Sciences', 'dept': 'HUMSS', 'course': 'SHS-HUMSS'},
            {'code': 'GAS-RS',  'name': 'Practical Research 1 (Qualitative Logic)', 'dept': 'GAS', 'course': 'SHS-GAS'},

            # --- CPU COLLEGE COURSES: BS COMPUTER SCIENCE (BSCS) ---
            {'code': 'CS-111',  'name': 'CS 111 - Introduction to Computing', 'dept': 'Computer Science', 'course': 'BSCS'},
            {'code': 'CS-112',  'name': 'CS 112 - Computer Programming 1 (Procedural C++)', 'dept': 'Computer Science', 'course': 'BSCS'},
            {'code': 'CS-121',  'name': 'CS 121 - Computer Programming 2 (Advanced Syntax Flow)', 'dept': 'Computer Science', 'course': 'BSCS'},
            {'code': 'CS-211',  'name': 'CS 211 - Data Structures and Algorithms', 'dept': 'Computer Science', 'course': 'BSCS'},
            {'code': 'CS-212',  'name': 'CS 212 - Discrete Structures 1 (Logic matrices)', 'dept': 'Computer Science', 'course': 'BSCS'},
            {'code': 'CS-311',  'name': 'CS 311 - Information Management & Advanced SQL', 'dept': 'Computer Science', 'course': 'BSCS'},
            {'code': 'CS-321',  'name': 'CS 321 - Design and Analysis of Algorithms', 'dept': 'Computer Science', 'course': 'BSCS'},
            {'code': 'CS-412',  'name': 'CS 412 - Artificial Intelligence & Intelligent Agents', 'dept': 'Computer Science', 'course': 'BSCS'},

            # --- CPU COLLEGE COURSES: BS INFORMATION TECHNOLOGY (BSIT) ---
            {'code': 'IT-111',  'name': 'IT 111 - Introduction to Computing Technology', 'dept': 'Information Technology', 'course': 'BSIT'},
            {'code': 'IT-212',  'name': 'IT 212 - Web Systems and Technologies 1', 'dept': 'Information Technology', 'course': 'BSIT'},
            {'code': 'IT-221',  'name': 'IT 221 - Database Management Systems 1', 'dept': 'Information Technology', 'course': 'BSIT'},
            {'code': 'IT-222',  'name': 'IT 222 - Networking 1 (Routing & Switching)', 'dept': 'Information Technology', 'course': 'BSIT'},
            {'code': 'IT-312',  'name': 'IT 312 - Web Systems 2 (Vue & Full-Stack Architectures)', 'dept': 'Information Technology', 'course': 'BSIT'},
            {'code': 'IT-313',  'name': 'IT 313 - Information Assurance and Security 1', 'dept': 'Information Technology', 'course': 'BSIT'},

            # --- CPU COLLEGE COURSES: BS BUSINESS ADMINISTRATION (BSBA) ---
            {'code': 'BUS-101', 'name': 'BUS 101 - Principles of Business Management', 'dept': 'Business', 'course': 'BSBA'},
            {'code': 'BUS-201', 'name': 'BUS 201 - Marketing Management & Consumer Analysis', 'dept': 'Business', 'course': 'BSBA'},
            {'code': 'ACC-101', 'name': 'ACC 101 - Accounting Principles and Financial Records', 'dept': 'Accountancy', 'course': 'BSBA'},
        ]

        for s in subjects_data:
            obj, created = Subjects.objects.update_or_create(
                subject_code=s['code'],
                defaults={
                    'subject_name': s['name'],
                    'department': s['dept'],
                }
            )
            self.stdout.write(f"  - Subject {s['code']}: {'Created' if created else 'Updated'}")
            
        # 5. Seed Users + UserProfiles with Bounded Security Rules
        cpu = PartnerInstitution.objects.get(school_email_domain='cpu.edu.ph')
        courses = list(Course.objects.all())
        year_levels_pool = [1, 2, 3, 4]

        TUTEE_COUNT = 20
        TUTOR_COUNT = 10

        tutee_profiles = []
        tutor_profiles = []

        for i in range(TUTEE_COUNT):
            fname = fake.first_name()
            lname = fake.last_name()
            email = f"{fname.lower()}.{lname.lower()}{i}@cpu.edu.ph"

            user, created = User.objects.get_or_create(
                username=email,
                defaults={'email': email, 'first_name': fname, 'last_name': lname}
            )
            if created:
                user.set_password('studybuddy123')
                user.save()

            profile, _ = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'fname': fname,
                    'lname': lname,
                    'role': 'Tutee',
                    'course': fake.random_element(courses),
                    'year_level': fake.random_element(year_levels_pool),
                    'bio': fake.sentence(nb_words=12),
                    'profile_completed': True,
                    'institution': cpu,
                    'is_suspended': False, # Resolves PostgreSQL row level constraints block
                }
            )
            tutee_profiles.append(profile)
            self.stdout.write(f"  - Seeded Student Profile: {fname} {lname}")

        for i in range(TUTOR_COUNT):
            fname = fake.first_name()
            lname = fake.last_name()
            email = f"tutor.{fname.lower()}.{lname.lower()}{i}@cpu.edu.ph"

            user, created = User.objects.get_or_create(
                username=email,
                defaults={'email': email, 'first_name': fname, 'last_name': lname}
            )
            if created:
                user.set_password('studybuddy123')
                user.save()

            profile, _ = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'fname': fname,
                    'lname': lname,
                    'role': 'Tutor',
                    'course': fake.random_element(courses),
                    'year_level': fake.random_element(year_levels_pool),
                    'bio': fake.sentence(nb_words=12),
                    'profile_completed': True,
                    'institution': cpu,
                    'is_suspended': False,
                }
            )
            tutor_profiles.append(profile)
            self.stdout.write(f"  - Seeded Tutor User: {fname} {lname}")

        # 6. Seed Tutor Records loaded with feature vectors for algorithm processing
        tutors = []
        for profile in tutor_profiles:
            tutor, _ = Tutor.objects.get_or_create(
                profile=profile,
                defaults={
                    'teaching_level': fake.random_element(['College', 'High School', 'Both']),
                    'can_online': fake.boolean(chance_of_getting_true=70),
                    'can_f2f': fake.boolean(chance_of_getting_true=50),
                    'hourly_rate': fake.random_int(min=120, max=450),
                    'rating_average': 0,
                    'total_sessions': 0,
                }
            )
            tutors.append(tutor)
            self.stdout.write(f"  - Tutor record generated: {profile.fname} {profile.lname}")
            
        # 7. Seed TutorSubjects
        all_seeded_subjects = list(Subjects.objects.all())

        for tutor in tutors:
            assigned = fake.random_elements(all_seeded_subjects, length=fake.random_int(min=2, max=4), unique=True)
            for subject in assigned:
                TutorSubjects.objects.get_or_create(
                    tutor=tutor,
                    subject=subject,
                    defaults={'expertise_level': fake.random_int(min=1, max=3)}
                )
            self.stdout.write(f"  - Subjects assigned to {tutor.profile.fname}: {[s.subject_code for s in assigned]}")

        # 8. Seed TutorAvailability (contiguous 30-min blocks so multi-slot searches match)
        DAY_CHOICES = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

        def build_contiguous_slots(start_hour, block_hours):
            slots = []
            current = datetime.datetime.combine(
                datetime.date.today(), datetime.time(start_hour, 0)
            )
            end = current + datetime.timedelta(hours=block_hours)
            while current < end:
                slots.append(current.time())
                current += datetime.timedelta(minutes=30)
            return slots

        availability_pool = []

        for tutor in tutors:
            assigned_days = fake.random_elements(DAY_CHOICES, length=3, unique=True)
            for day in assigned_days:
                start_hour = fake.random_int(min=8, max=13)   # block starts 8am-1pm
                block_hours = fake.random_int(min=4, max=6)    # 4-6 hour contiguous block
                for time_slot in build_contiguous_slots(start_hour, block_hours):
                    slot, created = TutorAvailability.objects.get_or_create(
                        tutor=tutor,
                        day=day,
                        time_slot=time_slot,
                        defaults={'is_active': True, 'is_booked': False}
                    )
                    availability_pool.append(slot)
                    
        # 9. Seed PaymentMethods
        payment_methods_data = [
            {'code': 'CASH', 'name': 'Cash Ledger'},
            {'code': 'online', 'name': 'PayMongo Online Framework (GCash/Maya)'},
        ]

        for pm in payment_methods_data:
            obj, created = PaymentMethod.objects.get_or_create(
                code=pm['code'],
                defaults={'method_name': pm['name'], 'is_active': True}
            )
            self.stdout.write(f"  - PaymentMethod {pm['code']}: {'Created' if created else 'Exists'}")

        payment_methods = list(PaymentMethod.objects.all())
        
        # 10. Seed Bookings + Payments
        from datetime import date, timedelta

        BOOKING_COUNT = 40
        bookings_created = []

        for _ in range(BOOKING_COUNT):
            tutee = fake.random_element(tutee_profiles)
            tutor = fake.random_element(tutors)

            tutor_slots = [s for s in availability_pool if s.tutor == tutor]
            if not tutor_slots:
                continue

            slot = fake.random_element(tutor_slots)
            session_date = date.today() - timedelta(days=fake.random_int(min=1, max=90))

            status_choice = random.choices(
                ['Completed', 'Confirmed', 'Pending', 'Cancelled'],
                weights=[60, 20, 15, 5],
                k=1
            )[0]

            if Booking.objects.filter(availability=slot, session_date=session_date).exists():
                continue

            session_mode = 'Online' if tutor.can_online else 'F2F'

            booking = Booking.objects.create(
                student=tutee,
                tutor=tutor,
                availability=slot,
                session_date=session_date,
                session_mode=session_mode,
                status=status_choice,
                tutee_confirmed=True,
                tutor_confirmed=True,
                session_group_id=uuid4(),
                booking_request_id=uuid4()
            )
            bookings_created.append(booking)

            payment_status = 'Paid' if status_choice == 'Completed' else 'Pending'
            Payment.objects.create(
                booking=booking,
                method=fake.random_element(payment_methods),
                amount=tutor.hourly_rate,
                payment_status=payment_status,
                transaction_reference=f"TXN-{uuid4().hex[:10].upper()}"
            )

        self.stdout.write(f"  - Bookings generated cleanly: {len(bookings_created)}")
        
        # 11. Seed Ratings (bell curve model variables to test recommender matrix weights)
        completed_bookings = [b for b in bookings_created if b.status == 'Completed']
        ratings_created = 0

        for booking in completed_bookings:
            score = random.choices(
                [1, 2, 3, 4, 5],
                weights=[2, 5, 20, 40, 33],
                k=1
            )[0]

            Rating.objects.create(
                booking=booking,
                student=booking.student,
                tutor=booking.tutor,
                rating_score=score,
                comment=fake.sentence(nb_words=10) if score >= 3 else 'Session fulfilled metrics structural baseline.',
            )
            ratings_created += 1

        self.stdout.write(f"  - Ratings calculated: {ratings_created}")

        # 12. Recompute and aggregate mathematical vector properties for the Recommender Engine
        for tutor in tutors:
            tutor_ratings = Rating.objects.filter(tutor=tutor)
            completed = Booking.objects.filter(tutor=tutor, status='Completed').count()

            if tutor_ratings.exists():
                avg = sum(r.rating_score for r in tutor_ratings) / tutor_ratings.count()
                tutor.rating_average = round(avg, 2)

            tutor.total_sessions = completed
            tutor.save()
            self.stdout.write(f"  - Aggregated {tutor.profile.fname}: {tutor.rating_average} avg rating / {tutor.total_sessions} sessions")
            
        # 13. Seed User Preference Maps
        for tutee in tutee_profiles:
            pref, created = Preference.objects.get_or_create(user=tutee)
            preferred_subjects = fake.random_elements(all_seeded_subjects, length=fake.random_int(min=2, max=3), unique=True)
            pref.subjects.set(preferred_subjects)
            pref.save()

        self.stdout.write(f"  - Preference bounds initialized for {len(tutee_profiles)} student accounts.")
        self.stdout.write(self.style.SUCCESS("Seeding complete. Database ready for evaluation."))