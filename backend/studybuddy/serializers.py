from rest_framework import serializers
from .models import Notification, Preference, Rating, Subjects, Tutor, TutorApplication, TutorAvailability, TutorAvailabilityOverride, TutorDocumentRenewalReview, TuteeApplication, TuteeDocumentRenewalReview, WithdrawalRequest, UserProfile, PartnerInstitution, PlatformActivity, Wallet

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
    institution_name = serializers.CharField(source='institution.institution_name', read_only=True)
    wallet_balance = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            'id',
            'email',
            'fname',
            'lname',
            'full_name',
            'role',
            'institution_name',
            'profile_completed',
            'is_suspended',
            'wallet_balance',
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
            'subjects',
            'response_time',
            'response_time_label',
            'pinned_review_id',
            'pinned_review'
        ]

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
    review_type = serializers.SerializerMethodField()
    applicant_name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    institution_name = serializers.SerializerMethodField()
    school_id_url = serializers.SerializerMethodField()
    enrollment_proof_url = serializers.SerializerMethodField()
    document_renewal_status = serializers.SerializerMethodField()
    document_renewal_due_at = serializers.SerializerMethodField()
    can_submit_document_renewal = serializers.SerializerMethodField()
    latest_document_renewal_id = serializers.SerializerMethodField()
    latest_document_renewal_rejection_reason = serializers.SerializerMethodField()
    latest_document_renewal_submitted_at = serializers.SerializerMethodField()
    latest_document_renewal_reviewed_at = serializers.SerializerMethodField()
    latest_document_renewal_school_id_url = serializers.SerializerMethodField()
    latest_document_renewal_enrollment_proof_url = serializers.SerializerMethodField()

    class Meta:
        model = TutorApplication
        fields = [
            'id', 'review_type', 'applicant_name', 'email', 'institution_name',
            'reason_to_tutor', 'application_status',
            'school_id_url', 'enrollment_proof_url',
            'rejection_reason', 'submitted_at', 'reviewed_at',
            'document_renewal_status', 'document_renewal_due_at',
            'can_submit_document_renewal', 'latest_document_renewal_id',
            'latest_document_renewal_rejection_reason',
            'latest_document_renewal_submitted_at',
            'latest_document_renewal_reviewed_at',
            'latest_document_renewal_school_id_url',
            'latest_document_renewal_enrollment_proof_url',
        ]

    def get_review_type(self, obj):
        renewal = obj.latest_document_renewal_review()
        if obj.application_status == 'approved' and renewal and renewal.status in ['pending', 'rejected']:
            return 'document_renewal'
        return 'initial'

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

    def get_document_renewal_status(self, obj):
        return obj.document_renewal_status()

    def get_document_renewal_due_at(self, obj):
        due_at = obj.document_renewal_due_at()
        return due_at.isoformat() if due_at else None

    def get_can_submit_document_renewal(self, obj):
        return obj.can_submit_document_renewal()

    def get_latest_document_renewal_id(self, obj):
        renewal = obj.latest_document_renewal_review()
        return renewal.id if renewal else None

    def get_latest_document_renewal_rejection_reason(self, obj):
        renewal = obj.latest_document_renewal_review()
        if renewal and renewal.status == 'rejected':
            return renewal.rejection_reason
        return ''

    def get_latest_document_renewal_submitted_at(self, obj):
        renewal = obj.latest_document_renewal_review()
        return renewal.submitted_at.isoformat() if renewal else None

    def get_latest_document_renewal_reviewed_at(self, obj):
        renewal = obj.latest_document_renewal_review()
        return renewal.reviewed_at.isoformat() if renewal and renewal.reviewed_at else None

    def get_latest_document_renewal_school_id_url(self, obj):
        renewal = obj.latest_document_renewal_review()
        request = self.context.get('request')
        if not renewal or not renewal.school_id:
            return None
        if request:
            return request.build_absolute_uri(renewal.school_id.url)
        return renewal.school_id.url

    def get_latest_document_renewal_enrollment_proof_url(self, obj):
        renewal = obj.latest_document_renewal_review()
        request = self.context.get('request')
        if not renewal or not renewal.enrollment_proof:
            return None
        if request:
            return request.build_absolute_uri(renewal.enrollment_proof.url)
        return renewal.enrollment_proof.url


class TutorDocumentRenewalReviewSerializer(serializers.ModelSerializer):
    review_type = serializers.SerializerMethodField()
    applicant_name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    institution_name = serializers.SerializerMethodField()
    application_status = serializers.CharField(source='status')
    school_id_url = serializers.SerializerMethodField()
    enrollment_proof_url = serializers.SerializerMethodField()

    class Meta:
        model = TutorDocumentRenewalReview
        fields = [
            'id', 'review_type', 'applicant_name', 'email', 'institution_name',
            'reason_to_tutor', 'application_status',
            'school_id_url', 'enrollment_proof_url',
            'rejection_reason', 'submitted_at', 'reviewed_at'
        ]

    def get_review_type(self, obj):
        return 'document_renewal'

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


class TuteeApplicationSerializer(serializers.ModelSerializer):
    review_type = serializers.SerializerMethodField()
    applicant_name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    institution_name = serializers.SerializerMethodField()
    school_id_url = serializers.SerializerMethodField()
    enrollment_proof_url = serializers.SerializerMethodField()
    document_renewal_status = serializers.SerializerMethodField()
    document_renewal_due_at = serializers.SerializerMethodField()
    can_submit_document_renewal = serializers.SerializerMethodField()
    latest_document_renewal_id = serializers.SerializerMethodField()
    latest_document_renewal_rejection_reason = serializers.SerializerMethodField()
    latest_document_renewal_submitted_at = serializers.SerializerMethodField()
    latest_document_renewal_reviewed_at = serializers.SerializerMethodField()
    latest_document_renewal_school_id_url = serializers.SerializerMethodField()
    latest_document_renewal_enrollment_proof_url = serializers.SerializerMethodField()

    class Meta:
        model = TuteeApplication
        fields = [
            'id', 'review_type', 'applicant_name', 'email', 'institution_name',
            'reason_to_tutor', 'application_status',
            'school_id_url', 'enrollment_proof_url',
            'rejection_reason', 'submitted_at', 'reviewed_at',
            'document_renewal_status', 'document_renewal_due_at',
            'can_submit_document_renewal', 'latest_document_renewal_id',
            'latest_document_renewal_rejection_reason',
            'latest_document_renewal_submitted_at',
            'latest_document_renewal_reviewed_at',
            'latest_document_renewal_school_id_url',
            'latest_document_renewal_enrollment_proof_url',
        ]

    def get_review_type(self, obj):
        renewal = obj.latest_document_renewal_review()
        if obj.application_status == 'approved' and renewal and renewal.status in ['pending', 'rejected']:
            return 'document_renewal'
        return 'initial'

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

    def get_document_renewal_status(self, obj):
        return obj.document_renewal_status()

    def get_document_renewal_due_at(self, obj):
        due_at = obj.document_renewal_due_at()
        return due_at.isoformat() if due_at else None

    def get_can_submit_document_renewal(self, obj):
        return obj.can_submit_document_renewal()

    def get_latest_document_renewal_id(self, obj):
        renewal = obj.latest_document_renewal_review()
        return renewal.id if renewal else None

    def get_latest_document_renewal_rejection_reason(self, obj):
        renewal = obj.latest_document_renewal_review()
        if renewal and renewal.status == 'rejected':
            return renewal.rejection_reason
        return ''

    def get_latest_document_renewal_submitted_at(self, obj):
        renewal = obj.latest_document_renewal_review()
        return renewal.submitted_at.isoformat() if renewal else None

    def get_latest_document_renewal_reviewed_at(self, obj):
        renewal = obj.latest_document_renewal_review()
        return renewal.reviewed_at.isoformat() if renewal and renewal.reviewed_at else None

    def get_latest_document_renewal_school_id_url(self, obj):
        renewal = obj.latest_document_renewal_review()
        request = self.context.get('request')
        if not renewal or not renewal.school_id:
            return None
        if request:
            return request.build_absolute_uri(renewal.school_id.url)
        return renewal.school_id.url

    def get_latest_document_renewal_enrollment_proof_url(self, obj):
        renewal = obj.latest_document_renewal_review()
        request = self.context.get('request')
        if not renewal or not renewal.enrollment_proof:
            return None
        if request:
            return request.build_absolute_uri(renewal.enrollment_proof.url)
        return renewal.enrollment_proof.url


class TuteeDocumentRenewalReviewSerializer(serializers.ModelSerializer):
    review_type = serializers.SerializerMethodField()
    applicant_name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    institution_name = serializers.SerializerMethodField()
    application_status = serializers.CharField(source='status')
    school_id_url = serializers.SerializerMethodField()
    enrollment_proof_url = serializers.SerializerMethodField()

    class Meta:
        model = TuteeDocumentRenewalReview
        fields = [
            'id', 'review_type', 'applicant_name', 'email', 'institution_name',
            'reason_to_tutor', 'application_status',
            'school_id_url', 'enrollment_proof_url',
            'rejection_reason', 'submitted_at', 'reviewed_at'
        ]

    def get_review_type(self, obj):
        return 'document_renewal'

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
