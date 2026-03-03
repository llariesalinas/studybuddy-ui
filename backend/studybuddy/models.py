from django.db import models
from django.contrib.auth.models import User ### allows the use of auth user model for authentication and user management


# Create your models here.

class Strand(models.Model):

    strand_code = models.CharField(max_length=10, primary_key=True)
    strand_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.strand_code} - {self.strand_name}"
    
class Course(models.Model):

    course_code = models.CharField(max_length=20, primary_key=True)
    course_name = models.CharField(max_length=100)

    strand = models.ForeignKey(
        Strand,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.course_code} - {self.course_name}"



class UserProfile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    fname = models.CharField(max_length=100)
    mname = models.CharField(max_length=100, blank=True)
    lname = models.CharField(max_length=100)

    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    year_level = models.IntegerField(null=True, blank=True)

    bio = models.TextField(blank=True, null=True)

    profile_completed = models.BooleanField(default=False)

    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        blank=True,
        null=True
    )

    ROLE_CHOICES = [
        ('Tutee', 'Tutee'),
        ('Tutor', 'Tutor'),
        ('Admin', 'Admin'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.fname} {self.lname}"

    ROLE_CHOICES = [
        ('Tutee', 'Tutee'),
        ('Tutor', 'Tutor'),
        ('Admin', 'Admin'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)  # Tutee, Tutor, Admin
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.fname} {self.lname}"
    
#TUTOR TABLE
class Tutor(models.Model):

    profile = models.OneToOneField(
        UserProfile,
        on_delete=models.CASCADE,
        primary_key=True
    )

    # Tutor setup fields (filled later)
    teaching_level = models.CharField(max_length=100, null=True, blank=True)

    can_online = models.BooleanField(default=True)
    can_f2f = models.BooleanField(default=False)

    rating_average = models.FloatField(default=0)

    hourly_rate = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True
    )

    total_sessions = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Tutor: {self.profile.fname} {self.profile.lname}"

#Subjects Table 
class Subjects(models.Model):
    subject_code = models.CharField(max_length=20, primary_key=True)
    subject_name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.subject_code} - {self.subject_name}"
    
#Tutor Subjects Table

class TutorSubjects(models.Model):
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subjects, on_delete=models.CASCADE)
    
    expertise_level = models.IntegerField()  # e.g., Beginner, Intermediate, Advanced

    def __str__(self):
        return f"{self.tutor.profile.fname} {self.tutor.profile.lname} - {self.subject.subject_code}"


class TutorAvailability(models.Model):

    DAY_CHOICES = [
        ('Mon', 'Monday'),
        ('Tue', 'Tuesday'),
        ('Wed', 'Wednesday'),
        ('Thu', 'Thursday'),
        ('Fri', 'Friday'),
        ('Sat', 'Saturday'),
        ('Sun', 'Sunday'),
    ]

    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    day = models.CharField(max_length=3, choices=DAY_CHOICES)
    time_slot = models.TimeField()
    is_active = models.BooleanField(default=False)   # tutor toggles this
    is_booked = models.BooleanField(default=False)   # system controls this

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('tutor', 'day', 'time_slot')

    def __str__(self):
        return f"{self.tutor.profile.fname} - {self.day} {self.time_slot}"
    
class Booking(models.Model):

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    student = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="student_bookings"
    )

    tutor = models.ForeignKey(
        Tutor,
        on_delete=models.CASCADE,
        related_name="tutor_bookings"
    )

    availability = models.ForeignKey(
        TutorAvailability,
        on_delete=models.CASCADE,
        related_name="bookings"
    )

    session_date = models.DateField()

    session_mode = models.CharField(
        max_length=10,
        choices=[('Online', 'Online'), ('F2F', 'Face-to-Face')]
    )

    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default="Pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('availability', 'session_date')

class PaymentMethod(models.Model):

    METHOD_CODES = [
        ('CASH', 'Cash'),
        ('GCASH', 'GCash'),
        ('BANK', 'Bank Transfer'),
    ]

    method_id = models.AutoField(primary_key=True)

    code = models.CharField(             
        max_length=20,
        choices=METHOD_CODES,
        unique=True,
    )

    method_name = models.CharField(max_length=50)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.method_name} ({self.code})"

class Payment(models.Model):

    PAYMENT_STATUS = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Failed', 'Failed'),
        ('Refunded', 'Refunded'),
    ]

    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name="payment"
    )

    method = models.ForeignKey(        # ✅ FK to PAYMENT_METHODS
        PaymentMethod,
        on_delete=models.SET_NULL,
        null=True,
        related_name="payments"
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    payment_status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS,
        default='Pending'
    )

    transaction_reference = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    paid_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Booking {self.booking.id} - {self.payment_status}"
    
class Rating(models.Model):

    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name="rating"
    )

    student = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE
    )

    tutor = models.ForeignKey(
        Tutor,
        on_delete=models.CASCADE,
        related_name="ratings"
    )

    rating_score = models.IntegerField()  # 1–5

    comment = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.rating_score} ⭐ for {self.tutor.profile.fname}"
    
class Preference(models.Model):

    MODE_CHOICES = [
        ('Online', 'Online'),
        ('F2F', 'Face-to-Face'),
    ]

    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE)

    subjects = models.ManyToManyField(Subjects)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Preferences for {self.user.fname}"
    



    
