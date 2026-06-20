from rest_framework import serializers
from .models import (
    AdminAccountRequest,
    InstitutionRequest,
    Notification,
    PartnerInstitution,
    PlatformActivity,
    Preference,
    Rating,
    Subjects,
    Tutor,
    TutorApplication,
    TutorAvailability,
    TutorAvailabilityOverride,
    UserProfile,
    Wallet,
    WithdrawalRequest,
)

# Create Serializers here.

class PlatformActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = PlatformActivity
        fields = ['id', 'activity_type', 'message', 'created_at']

class AdminWithdrawalSerializer(serializers.ModelSerializer):
    tutor_name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()

    class Meta:
        model = WithdrawalRequest
        fields = [
            'id',
            'tutor',
            'tutor_name',
            'email',
            'amount',
            'method',
            'account_number',
            'account_name',
            'bank_name',
            'status',
            'failure_reason',
            'provider',
            'provider_wallet_transaction_id',
            'provider_reference_number',
            'provider_status',
            'provider_error_code',
            'provider_error_message',
            'provider_fee',
            'net_amount',
            'rail',
            'callback_received_at',
            'requested_at',
            'processed_at'
        ]

    def get_tutor_name(self, obj):
        return f"{obj.tutor.profile.fname} {obj.tutor.profile.lname}"

    def get_email(self, obj):
        return obj.tutor.profile.user.email

class AdminUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email')
    full_name = serializers.SerializerMethodField()
    institution = serializers.PrimaryKeyRelatedField(read_only=True)
    institution_name = serializers.CharField(source='institution.institution_name', read_only=True)
    wallet_balance = serializers.SerializerMethodField()
    profile_picture_url = serializers.SerializerMethodField()
    tutor_sessions_completed = serializers.SerializerMethodField()
    tutor_avg_rating = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            'id',
            'email',
            'fname',
            'lname',
            'full_name',
            'role',
            'institution',
            'institution_name',
            'profile_completed',
            'is_domain_exempt',
            'is_suspended',
            'wallet_balance',
            'profile_picture_url',
            'tutor_sessions_completed',
            'tutor_avg_rating',
            'created_at'
        ]

    def get_full_name(self, obj):
        return f"{obj.fname} {obj.lname}"

    def get_wallet_balance(self, obj):
        if obj.role == 'Tutor':
            try:
                return float(obj.tutor.wallet.balance)
            except Exception:
                return 0.0
        return None

    def get_profile_picture_url(self, obj):
        request = self.context.get('request')
        if obj.profile_picture and request:
            return request.build_absolute_uri(obj.profile_picture.url)
        return obj.profile_picture.url if obj.profile_picture else None

    def get_tutor_sessions_completed(self, obj):
        if obj.role != 'Tutor':
            return None
        try:
            return obj.tutor.total_sessions
        except Exception:
            return 0

    def get_tutor_avg_rating(self, obj):
        if obj.role != 'Tutor':
            return None
        try:
            return obj.tutor.rating_average
        except Exception:
            return 0

class PartnerInstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartnerInstitution
        fields = [
            'id',
            'institution_name',
            'school_email_domain',
            'is_active',
            'contact_person',
            'date_added'
        ]


class InstitutionRequestSerializer(serializers.ModelSerializer):
    reviewed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = InstitutionRequest
        fields = [
            'id',
            'institution_name',
            'school_email_domain',
            'contact_person',
            'contact_email',
            'note',
            'status',
            'reviewed_by',
            'reviewed_by_name',
            'created_at',
            'reviewed_at',
        ]
        read_only_fields = ['reviewed_by', 'reviewed_by_name', 'created_at', 'reviewed_at']

    def get_reviewed_by_name(self, obj):
        if not obj.reviewed_by:
            return None
        full_name = obj.reviewed_by.get_full_name()
        return full_name or obj.reviewed_by.email or obj.reviewed_by.username


class AdminAccountRequestSerializer(serializers.ModelSerializer):
    requesting_admin_name = serializers.SerializerMethodField()
    institution_name = serializers.CharField(source='institution.institution_name', read_only=True)
    target_user_name = serializers.SerializerMethodField()
    target_user_email = serializers.EmailField(source='target_user.user.email', read_only=True)

    class Meta:
        model = AdminAccountRequest
        fields = [
            'id',
            'requesting_admin',
            'requesting_admin_name',
            'institution',
            'institution_name',
            'target_user',
            'target_user_name',
            'target_user_email',
            'note',
            'status',
            'created_at',
            'reviewed_at',
        ]
        read_only_fields = [
            'requesting_admin',
            'requesting_admin_name',
            'institution_name',
            'target_user_name',
            'target_user_email',
            'created_at',
            'reviewed_at',
        ]

    def get_requesting_admin_name(self, obj):
        return f"{obj.requesting_admin.fname} {obj.requesting_admin.lname}".strip()

    def get_target_user_name(self, obj):
        if not obj.target_user:
            return None
        return f"{obj.target_user.fname} {obj.target_user.lname}".strip()

class TutorSearchSerializer(serializers.ModelSerializer):

    fname = serializers.CharField(source='profile.fname')
    lname = serializers.CharField(source='profile.lname')

    class Meta:
        model = Tutor
        fields = [
            'profile_id',
            'fname',
            'lname',
            'rating_average',
            'hourly_rate',
            'total_sessions'
        ]

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subjects
        fields = ['subject_code', 'subject_name', 'department', 'category']


class PinnedReviewSerializer(serializers.ModelSerializer):

    student_name = serializers.SerializerMethodField()

    class Meta:
        model = Rating
        fields = ['id', 'rating_score', 'comment', 'student_name', 'created_at']

    def get_student_name(self, obj):
        return f"{obj.student.fname} {obj.student.lname}".strip()


class TutorDetailSerializer(serializers.ModelSerializer):

    fname = serializers.CharField(source='profile.fname')
    lname = serializers.CharField(source='profile.lname')
    bio = serializers.CharField(source='profile.bio', allow_null=True)
    subjects = serializers.SerializerMethodField()
    profile_picture_url = serializers.SerializerMethodField()
    response_time_label = serializers.CharField(read_only=True)
    pinned_review_id = serializers.IntegerField(read_only=True)
    pinned_review = PinnedReviewSerializer(read_only=True)

    class Meta:
        model = Tutor
        fields = [
            'profile_id',
            'fname',
            'lname',
            'rating_average',
            'hourly_rate',
            'total_sessions',
            'bio',
            'profile_picture_url',
            'subjects',
            'response_time',
            'response_time_label',
            'pinned_review_id',
            'pinned_review'
        ]

    def get_profile_picture_url(self, obj):
        request = self.context.get('request')
        if obj.profile.profile_picture and request:
            return request.build_absolute_uri(obj.profile.profile_picture.url)
        return None

    def get_subjects(self, obj):
        tutor_subjects = obj.tutorsubjects_set.select_related('subject').all()

        return [
            {
                'subject_code': tutor_subject.subject.subject_code,
                'subject_name': tutor_subject.subject.subject_name,
                'description': tutor_subject.description or ''
            }
            for tutor_subject in tutor_subjects
        ]


class TutorProfileSerializer(serializers.ModelSerializer):

    fname = serializers.CharField(source='profile.fname', read_only=True)
    lname = serializers.CharField(source='profile.lname', read_only=True)
    email = serializers.CharField(source='profile.user.email', read_only=True)
    course = serializers.SerializerMethodField()
    year_level = serializers.IntegerField(source='profile.year_level', read_only=True, allow_null=True)
    bio = serializers.CharField(source='profile.bio', read_only=True, allow_null=True)
    profile_picture_url = serializers.SerializerMethodField()
    response_time_label = serializers.CharField(read_only=True)
    pinned_review_id = serializers.IntegerField(read_only=True)
    pinned_review = PinnedReviewSerializer(read_only=True)

    class Meta:
        model = Tutor
        fields = [
            'fname',
            'lname',
            'email',
            'course',
            'year_level',
            'bio',
            'profile_picture_url',
            'hourly_rate',
            'teaching_level',
            'can_online',
            'can_f2f',
            'rating_average',
            'total_sessions',
            'response_time',
            'response_time_label',
            'pinned_review_id',
            'pinned_review'
        ]

    def get_course(self, obj):
        return obj.profile.course.course_code if obj.profile.course else None

    def get_profile_picture_url(self, obj):
        request = self.context.get('request')
        if obj.profile.profile_picture and request:
            return request.build_absolute_uri(obj.profile.profile_picture.url)
        return None


class TutorProfileUpdateSerializer(serializers.ModelSerializer):

    response_time_label = serializers.CharField(read_only=True)
    pinned_review_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Tutor
        fields = [
            'hourly_rate',
            'teaching_level',
            'can_online',
            'can_f2f',
            'response_time',
            'response_time_label',
            'pinned_review',
            'pinned_review_id'
        ]

    def validate_pinned_review(self, value):
        tutor = self.instance

        if value is not None and value.tutor_id != tutor.profile_id:
            raise serializers.ValidationError('Pinned review must belong to this tutor.')

        return value

class TutorAvailabilitySerializer(serializers.ModelSerializer):
    day = serializers.SerializerMethodField()

    class Meta:
        model = TutorAvailability
        fields = ['id', 'day', 'time_slot', 'is_booked']

    def get_day(self, obj):
        return obj.get_day_display()  # converts 'Mon' to 'Monday', etc.
    

class PreferenceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Preference
        fields = ['subjects']


class TutorAvailabilityOverrideSerializer(serializers.ModelSerializer):
    availability_id = serializers.IntegerField(source='availability.id', read_only=True)
    time_slot = serializers.SerializerMethodField()
    day = serializers.SerializerMethodField()

    class Meta:
        model = TutorAvailabilityOverride
        fields = [
            'id',
            'override_date',
            'is_full_day',
            'availability_id',
            'day',
            'time_slot',
        ]

    def get_time_slot(self, obj):
        if obj.availability is None:
            return None
        return obj.availability.time_slot.strftime('%H:%M')

    def get_day(self, obj):
        if obj.availability is None:
            return None
        return obj.availability.day


class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = ['id', 'message', 'is_read', 'created_at']


class TutorApplicationSerializer(serializers.ModelSerializer):
    applicant_name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    institution_name = serializers.SerializerMethodField()
    school_id_url = serializers.SerializerMethodField()
    enrollment_proof_url = serializers.SerializerMethodField()

    class Meta:
        model = TutorApplication
        fields = [
            'id', 'applicant_name', 'email', 'institution_name',
            'reason_to_tutor', 'application_status',
            'school_id_url', 'enrollment_proof_url',
            'rejection_reason', 'submitted_at', 'reviewed_at'
        ]

    def get_applicant_name(self, obj):
        return f"{obj.profile.fname} {obj.profile.lname}"

    def get_email(self, obj):
        return obj.profile.user.email

    def get_institution_name(self, obj):
        return obj.profile.institution.institution_name if obj.profile.institution else "N/A"

    def get_school_id_url(self, obj):
        request = self.context.get('request')
        if obj.school_id and request:
            return request.build_absolute_uri(obj.school_id.url)
        return obj.school_id.url if obj.school_id else None

    def get_enrollment_proof_url(self, obj):
        request = self.context.get('request')
        if obj.enrollment_proof and request:
            return request.build_absolute_uri(obj.enrollment_proof.url)
        return obj.enrollment_proof.url if obj.enrollment_proof else None
