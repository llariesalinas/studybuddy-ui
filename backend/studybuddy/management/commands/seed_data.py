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

fake = Faker()

class Command(BaseCommand):
    help = 'Seeds the database with initial CPU Strands, Courses, and Institutions'

    def handle(self, *args, **options):
        self.stdout.write("🌱 Starting the seeding process...")

        # 1. Seed Strands (The Foundations)
        strands_data = [
            {'code': 'STEM', 'name': 'Science, Technology, Engineering, and Mathematics'},
            {'code': 'ABM', 'name': 'Accountancy, Business, and Management'},
            {'code': 'HUMSS', 'name': 'Humanities and Social Sciences'},
            {'code': 'GAS', 'name': 'General Academic Strand'},
        ]

        for s in strands_data:
            obj, created = Strand.objects.update_or_create(
                strand_code=s['code'],
                defaults={'strand_name': s['name']}
            )
            status = "Created" if created else "Updated"
            self.stdout.write(f"  - Strand {s['code']}: {status}")

        # 2. Seed Partner Institutions
        inst_obj, created = PartnerInstitution.objects.update_or_create(
            school_email_domain='cpu.edu.ph',
            defaults={
                'institution_name': 'Central Philippine University',
                'is_active': True,
                'contact_person': 'Admin'
            }
        )
        self.stdout.write(f"  - Institution {inst_obj.school_email_domain}: {'Created' if created else 'Updated'}")

        # 3. Seed College Courses (Example subset)
        courses_data = [
            {'code': 'BSCS', 'name': 'BS Computer Science', 'strand': 'STEM'},
            {'code': 'BSIT', 'name': 'BS Information Technology', 'strand': 'STEM'},
            {'code': 'BSBA', 'name': 'BS Business Administration', 'strand': 'ABM'},
        ]

        for c in courses_data:
            # We fetch the strand object to link it
            strand_obj = Strand.objects.get(strand_code=c['strand'])
            obj, created = Course.objects.update_or_create(
                course_code=c['code'],
                defaults={
                    'course_name': c['name'],
                    'strand': strand_obj
                }
            )
            self.stdout.write(f"  - Course {c['code']}: {'Created' if created else 'Updated'}")
        # 4. Seed Subjects
        subjects_data = [
            {'code': 'CS101', 'name': 'Introduction to Computing', 'dept': 'Computer Science'},
            {'code': 'CS201', 'name': 'Data Structures and Algorithms', 'dept': 'Computer Science'},
            {'code': 'CS301', 'name': 'Database Management Systems', 'dept': 'Computer Science'},
            {'code': 'CS401', 'name': 'Machine Learning', 'dept': 'Computer Science'},
            {'code': 'MATH101', 'name': 'Calculus I', 'dept': 'Mathematics'},
            {'code': 'MATH201', 'name': 'Linear Algebra', 'dept': 'Mathematics'},
            {'code': 'MATH301', 'name': 'Statistics and Probability', 'dept': 'Mathematics'},
            {'code': 'ENG101', 'name': 'Technical Writing', 'dept': 'English'},
            {'code': 'IT201', 'name': 'Web Development', 'dept': 'Information Technology'},
            {'code': 'IT301', 'name': 'Network Administration', 'dept': 'Information Technology'},
        ]

        for s in subjects_data:
            obj, created = Subjects.objects.update_or_create(
                subject_code=s['code'],
                defaults={
                    'subject_name': s['name'],
                    'department': s['dept']
                }
            )
            self.stdout.write(f"  - Subject {s['code']}: {'Created' if created else 'Updated'}")
            
        # 5. Seed Users + UserProfiles
        cpu = PartnerInstitution.objects.get(school_email_domain='cpu.edu.ph')
        courses = list(Course.objects.all())
        year_levels = [1, 2, 3, 4]

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
                    'year_level': fake.random_element(year_levels),
                    'bio': fake.sentence(nb_words=12),
                    'profile_completed': True,
                    'institution': cpu,
                }
            )
            tutee_profiles.append(profile)
            self.stdout.write(f"  - Tutee: {fname} {lname}")

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
                    'year_level': fake.random_element(year_levels),
                    'bio': fake.sentence(nb_words=12),
                    'profile_completed': True,
                    'institution': cpu,
                }
            )
            tutor_profiles.append(profile)
            self.stdout.write(f"  - Tutor profile: {fname} {lname}")

        # 6. Seed Tutor records
        tutors = []
        for profile in tutor_profiles:
            tutor, _ = Tutor.objects.get_or_create(
                profile=profile,
                defaults={
                    'teaching_level': fake.random_element(['College', 'High School', 'Both']),
                    'can_online': fake.boolean(chance_of_getting_true=70),
                    'can_f2f': fake.boolean(chance_of_getting_true=50),
                    'hourly_rate': fake.random_int(min=100, max=500),
                    'rating_average': 0,
                    'total_sessions': 0,
                }
            )
            tutors.append(tutor)
            self.stdout.write(f"  - Tutor record: {profile.fname} {profile.lname}")
            
        # 7. Seed TutorSubjects
        from studybuddy.models import TutorSubjects

        subjects = list(Subjects.objects.all())

        for tutor in tutors:
            assigned = fake.random_elements(subjects, length=fake.random_int(min=2, max=4), unique=True)
            for subject in assigned:
                TutorSubjects.objects.get_or_create(
                    tutor=tutor,
                    subject=subject,
                    defaults={'expertise_level': fake.random_int(min=1, max=3)}
                )
            self.stdout.write(f"  - Subjects assigned to {tutor.profile.fname}: {[s.subject_code for s in assigned]}")

        # 8. Seed TutorAvailability
        from studybuddy.models import TutorAvailability
        import datetime

        DAY_CHOICES = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
        TIME_SLOTS = [
            datetime.time(8, 0),
            datetime.time(10, 0),
            datetime.time(13, 0),
            datetime.time(15, 0),
            datetime.time(17, 0),
        ]

        availability_pool = []

        for tutor in tutors:
            assigned_days = fake.random_elements(DAY_CHOICES, length=3, unique=True)
            for day in assigned_days:
                for time_slot in fake.random_elements(TIME_SLOTS, length=2, unique=True):
                    slot, created = TutorAvailability.objects.get_or_create(
                        tutor=tutor,
                        day=day,
                        time_slot=time_slot,
                        defaults={'is_active': True, 'is_booked': False}
                    )
                    availability_pool.append(slot)
                    
        # 9. Seed PaymentMethods
        payment_methods_data = [
            {'code': 'CASH', 'name': 'Cash'},
            {'code': 'ONLINE', 'name': 'Online Payment'},
        ]

        for pm in payment_methods_data:
            obj, created = PaymentMethod.objects.get_or_create(
                code=pm['code'],
                defaults={'method_name': pm['name'], 'is_active': True}
            )
            self.stdout.write(f"  - PaymentMethod {pm['code']}: {'Created' if created else 'Exists'}")

        payment_methods = list(PaymentMethod.objects.all())
        
        # 10. Seed Bookings + Payments
        import random
        from datetime import date, timedelta

        BOOKING_COUNT = 40
        bookings_created = []

        for _ in range(BOOKING_COUNT):
            tutee = fake.random_element(tutee_profiles)
            tutor = fake.random_element(tutors)

            # Pick a random availability slot belonging to this tutor
            tutor_slots = [s for s in availability_pool if s.tutor == tutor]
            if not tutor_slots:
                continue

            slot = fake.random_element(tutor_slots)

            # Random session date in the past 90 days
            session_date = date.today() - timedelta(days=fake.random_int(min=1, max=90))

            # Weighted status — Completed appears most often
            status = random.choices(
                ['Completed', 'Confirmed', 'Pending', 'Cancelled'],
                weights=[60, 20, 15, 5],
                k=1
            )[0]

            # Skip if this slot + date combo already exists (unique_together constraint)
            if Booking.objects.filter(availability=slot, session_date=session_date).exists():
                continue

            session_mode = 'Online' if tutor.can_online else 'F2F'

            booking = Booking.objects.create(
                student=tutee,
                tutor=tutor,
                availability=slot,
                session_date=session_date,
                session_mode=session_mode,
                status=status,
                tutee_confirmed=True,
                tutor_confirmed=True,
            )
            bookings_created.append(booking)

            # Create a Payment for every booking
            payment_status = 'Paid' if status == 'Completed' else 'Pending'
            Payment.objects.create(
                booking=booking,
                method=fake.random_element(payment_methods),
                amount=tutor.hourly_rate,
                payment_status=payment_status,
            )

        self.stdout.write(f"  - Bookings created: {len(bookings_created)}")
        
        # 11. Seed Ratings (bell curve, only for Completed bookings)
        completed_bookings = [b for b in bookings_created if b.status == 'Completed']
        ratings_created = 0

        for booking in completed_bookings:
            # Bell curve: 4-star most common, 1-star very rare
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
                comment=fake.sentence(nb_words=10) if score >= 3 else '',
            )
            ratings_created += 1

        self.stdout.write(f"  - Ratings created: {ratings_created}")

        # 12. Update each tutor's rating_average and total_sessions
        for tutor in tutors:
            tutor_ratings = Rating.objects.filter(tutor=tutor)
            completed = Booking.objects.filter(tutor=tutor, status='Completed').count()

            if tutor_ratings.exists():
                avg = sum(r.rating_score for r in tutor_ratings) / tutor_ratings.count()
                tutor.rating_average = round(avg, 2)

            tutor.total_sessions = completed
            tutor.save()
            self.stdout.write(f"  - Updated {tutor.profile.fname}: {tutor.rating_average}⭐ / {tutor.total_sessions} sessions")
            
        # 13. Seed Preferences
        for tutee in tutee_profiles:
            pref, created = Preference.objects.get_or_create(user=tutee)
            preferred_subjects = fake.random_elements(subjects, length=fake.random_int(min=2, max=3), unique=True)
            pref.subjects.set(preferred_subjects)
            pref.save()

        self.stdout.write(f"  - Preferences seeded for {len(tutee_profiles)} tutees")

        self.stdout.write(f"  - Total availability slots created: {len(availability_pool)}")
        self.stdout.write(self.style.SUCCESS("✅ Database successfully seeded!"))