import uuid

from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


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


class PartnerInstitution(models.Model):
    institution_name = models.CharField(max_length=255)
    school_email_domain = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    contact_person = models.CharField(max_length=255, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['institution_name']

    def __str__(self):
        return f"{self.institution_name} ({self.school_email_domain})"



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
    is_suspended = models.BooleanField(default=False)

    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        blank=True,
        null=True
    )

    institution = models.ForeignKey(
        PartnerInstitution,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    is_domain_exempt = models.BooleanField(default=False)

    ROLE_CHOICES = [
        ('Tutee', 'Tutee'),
        ('Tutor', 'Tutor'),
        ('Admin', 'Admin'),
        ('SuperAdmin', 'SuperAdmin'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.fname} {self.lname}"


class EmailOTPChallenge(models.Model):
    PURPOSE_LOGIN = 'login'
    PURPOSE_CHOICES = [
        (PURPOSE_LOGIN, 'Login'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_otp_challenges')
    challenge_id = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES, default=PURPOSE_LOGIN)
    code_hash = models.CharField(max_length=64)
    expires_at = models.DateTimeField()
    consumed_at = models.DateTimeField(null=True, blank=True)
    attempt_count = models.PositiveSmallIntegerField(default=0)
    resend_count = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'purpose', 'created_at']),
            models.Index(fields=['expires_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.purpose} OTP for user {self.user_id}"


class EmailSendLog(models.Model):
    """Audit row written for every outbound email attempt.

    Backs two features: the per-recipient send cap (counting recent rows) and
    failure visibility (a queryable history of what was sent and what failed).
    """
    PURPOSE_LOGIN_OTP = 'login_otp'
    PURPOSE_PASSWORD_RESET = 'password_reset'
    PURPOSE_PASSWORD_CHANGED = 'password_changed'
    PURPOSE_CHOICES = [
        (PURPOSE_LOGIN_OTP, 'Login OTP'),
        (PURPOSE_PASSWORD_RESET, 'Password reset'),
        (PURPOSE_PASSWORD_CHANGED, 'Password changed'),
    ]

    STATUS_SENT = 'sent'
    STATUS_FAILED = 'failed'
    STATUS_CHOICES = [
        (STATUS_SENT, 'Sent'),
        (STATUS_FAILED, 'Failed'),
    ]

    recipient = models.EmailField()
    purpose = models.CharField(max_length=32, choices=PURPOSE_CHOICES)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES)
    error = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['recipient', 'purpose', 'created_at']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.purpose} -> {self.recipient} [{self.status}]"


#TUTOR TABLE
class Tutor(models.Model):

    RESPONSE_TIME_CHOICES = [
        ('within_1_hour', 'Within 1 hour'),
        ('within_few_hours', 'Within a few hours'),
        ('within_a_day', 'Within a day'),
    ]

    RESPONSE_TIME_LABELS = {
        'within_1_hour': 'within 1 hour',
        'within_few_hours': 'within a few hours',
        'within_a_day': 'within a day',
    }

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

    response_time = models.CharField(
        max_length=30,
        choices=RESPONSE_TIME_CHOICES,
        null=True,
        blank=True
    )

    response_time_label = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )

    pinned_review = models.ForeignKey(
        'Rating',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pinned_by_tutor'
    )

    total_sessions = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.response_time_label = self.RESPONSE_TIME_LABELS.get(self.response_time)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Tutor: {self.profile.fname} {self.profile.lname}"

class TutorApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    profile = models.OneToOneField(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='tutor_application'
    )

    # Required Documents Only
    school_id = models.ImageField(upload_to='tutor_applications/school_ids/')
    enrollment_proof = models.FileField(upload_to='tutor_applications/enrollment_proofs/')

    # Optional Motivation
    reason_to_tutor = models.TextField(
        blank=True,
        help_text="Why do you want to become a tutor?"
    )

    # Screening Status
    application_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    # Admin Feedback
    rejection_reason = models.TextField(blank=True, default='')
    reviewed_by = models.ForeignKey(
        UserProfile, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='reviewed_applications'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)

    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Application: {self.profile.fname} {self.profile.lname} ({self.application_status})"

class Wallet(models.Model):
    tutor = models.OneToOneField(Tutor, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    pending_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Wallet - {self.tutor.profile.fname} (₱{self.balance})"

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('session_credit', 'Session Credit'),
        ('withdrawal', 'Withdrawal'),
        ('withdrawal_reversal', 'Withdrawal Reversal'),
        ('cashout_fee', 'Cash-Out Provider Fee'),
        ('cashout_fee_reversal', 'Cash-Out Provider Fee Reversal'),
        ('commission_deduction', 'Commission Deduction'),
    ]

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=30, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    reference_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

class TutorPayoutAccount(models.Model):
    DESTINATION_TYPES = [
        ('gcash', 'GCash'),
        ('bank', 'Bank Transfer'),
    ]

    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE, related_name='payout_accounts')
    destination_type = models.CharField(max_length=10, choices=DESTINATION_TYPES)
    receiving_institution_id = models.CharField(max_length=100)
    receiving_institution_name = models.CharField(max_length=150)
    receiving_institution_code = models.CharField(max_length=50, blank=True)
    provider = models.CharField(max_length=20, blank=True, default='')
    account_number = models.CharField(max_length=50)
    account_name = models.CharField(max_length=100)
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_active', '-updated_at']

    def __str__(self):
        return f"{self.tutor.profile.fname} - {self.receiving_institution_name}"

class WithdrawalRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processed', 'Processed'),
        ('rejected', 'Rejected'),
        ('failed', 'Failed'),
        ('flagged', 'Flagged'),
    ]
    METHOD_CHOICES = [
        ('gcash', 'GCash'),
        ('bank', 'Bank Transfer'),
    ]

    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    payout_account = models.ForeignKey(
        TutorPayoutAccount,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cash_outs'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=10, choices=METHOD_CHOICES)
    account_number = models.CharField(max_length=50)
    account_name = models.CharField(max_length=100)
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    failure_reason = models.TextField(blank=True, null=True)
    provider = models.CharField(max_length=30, blank=True, default='')
    provider_wallet_transaction_id = models.CharField(max_length=120, blank=True, default='')
    provider_reference_number = models.CharField(max_length=120, blank=True, default='')
    provider_status = models.CharField(max_length=30, blank=True, default='')
    provider_error_code = models.CharField(max_length=120, blank=True, default='')
    provider_error_message = models.TextField(blank=True, default='')
    provider_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    rail = models.CharField(max_length=20, blank=True, default='')
    callback_received_at = models.DateTimeField(null=True, blank=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

class PlatformActivity(models.Model):
    ACTIVITY_TYPES = [
        ('registration', 'New User Registration'),
        ('booking_completed', 'Session Completed'),
        ('institution_added', 'New Institution Request'),
        ('withdrawal_failed', 'Withdrawal Failure'),
        ('admin_action', 'Admin Action'),
        ('tutor_application', 'Tutor Application'),
    ]

    activity_type = models.CharField(max_length=30, choices=ACTIVITY_TYPES)
    message = models.CharField(max_length=255)
    institution = models.ForeignKey(
        'PartnerInstitution',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='activities'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Platform Activities"

    def __str__(self):
        return f"{self.activity_type} - {self.created_at}"

@receiver(post_save, sender=Tutor)
def create_tutor_wallet(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.get_or_create(tutor=instance)

#Subjects Table
class Subjects(models.Model):
    subject_code = models.CharField(max_length=20, primary_key=True)
    subject_name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    category = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.subject_code} - {self.subject_name}"

#Tutor Subjects Table

class TutorSubjects(models.Model):
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subjects, on_delete=models.CASCADE)

    expertise_level = models.IntegerField()  # e.g., Beginner, Intermediate, Advanced
    description = models.TextField(blank=True, default='')

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
        indexes = [
            models.Index(fields=['day', 'time_slot', 'is_active']),
        ]
        unique_together = ('tutor', 'day', 'time_slot')

    def __str__(self):
        return f"{self.tutor.profile.fname} - {self.day} {self.time_slot}"


class TutorAvailabilityOverride(models.Model):
    tutor = models.ForeignKey(
        Tutor,
        on_delete=models.CASCADE,
        related_name='availability_overrides'
    )
    override_date = models.DateField()
    availability = models.ForeignKey(
        TutorAvailability,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='date_overrides'
    )
    is_full_day = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['tutor', 'override_date'],
                condition=Q(is_full_day=True),
                name='unique_full_day_override_per_tutor_date'
            ),
            models.UniqueConstraint(
                fields=['tutor', 'override_date', 'availability'],
                condition=Q(is_full_day=False),
                name='unique_slot_override_per_tutor_date_slot'
            ),
        ]

    def __str__(self):
        if self.is_full_day:
            return f"{self.tutor.profile.fname} full-day override on {self.override_date}"
        return f"{self.tutor.profile.fname} override on {self.override_date} for {self.availability_id}"

class Booking(models.Model):

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Awaiting Payment Verification', 'Awaiting Payment Verification'),
        ('Completed', 'Completed'),
        ('Rejected', 'Rejected'),
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

    preferred_location = models.CharField(max_length=255, null=True, blank=True)

    session_group_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
        default=None
    )
    booking_request_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
        default=None
    )

    status = models.CharField(
        max_length=40,
        choices=STATUS_CHOICES,
        default="Pending"
    )
    cancellation_reason = models.TextField(blank=True, default='')
    cancelled_by_role = models.CharField(
        max_length=10,
        blank=True,
        default='',
        choices=[('tutee', 'Tutee'), ('tutor', 'Tutor')],
    )
    tutee_confirmed = models.BooleanField(default=False)
    tutor_confirmed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['session_date', 'availability', 'status']),
            # Hot dashboard/bookings queries filter on the owner FK + status and
            # order by session_date (student_dashboard, list_bookings, tutor_dashboard).
            models.Index(fields=['student', 'status', 'session_date']),
            models.Index(fields=['tutor', 'status', 'session_date']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['availability', 'session_date'],
                condition=Q(status__in=[
                    'Pending',
                    'Confirmed',
                    'Awaiting Payment Verification',
                    'Completed',
                ]),
                name='unique_active_booking_per_slot_date',
            ),
        ]

class PaymentMethod(models.Model):

    METHOD_CODES = [
        ('CASH', 'Cash'),
        ('GCASH', 'GCash'),
        ('BANK', 'Bank Transfer'),
        ('online', 'Online Payment'),
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

    receipt_image = models.ImageField(
        upload_to='payment_receipts/',
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


class Notification(models.Model):

    recipient = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='notifications'
    )

    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', '-created_at'], name='notif_recipient_date_idx'),
        ]

    def __str__(self):
        return f"Notification for {self.recipient} - {'Read' if self.is_read else 'Unread'}"

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

# Import chat models to register them with the studybuddy app
from .chat.models import ChatRoom, Message

class SupportTicket(models.Model):
    CATEGORY_CHOICES = [
        ('Payment', 'Payment Issue'),
        ('Booking', 'Booking/No-show'),
        ('Technical', 'Technical Problem'),
        ('Dispute', 'Tutee/Tutor Dispute'),
        ('Other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('In_Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
    ]

    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="support_tickets")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    subject = models.CharField(max_length=150)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Open")

    booking = models.ForeignKey('Booking', on_delete=models.SET_NULL, null=True, blank=True)
    transaction = models.ForeignKey('Transaction', on_delete=models.SET_NULL, null=True, blank=True)

    chatroom = models.OneToOneField('ChatRoom', on_delete=models.SET_NULL, null=True, related_name='ticket')

    assigned_agent = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Ticket #{self.id} - {self.subject} ({self.status})"
