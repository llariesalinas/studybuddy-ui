from rest_framework import serializers
from .models import Preference, Rating, Subjects, Tutor, TutorAvailability

# Create Serializers here.

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
        return list(
            obj.tutorsubjects_set.select_related('subject').values_list('subject__subject_name', flat=True)
        )


class TutorProfileSerializer(serializers.ModelSerializer):

    fname = serializers.CharField(source='profile.fname', read_only=True)
    lname = serializers.CharField(source='profile.lname', read_only=True)
    email = serializers.CharField(source='profile.user.email', read_only=True)
    course = serializers.SerializerMethodField()
    year_level = serializers.IntegerField(source='profile.year_level', read_only=True, allow_null=True)
    bio = serializers.CharField(source='profile.bio', read_only=True, allow_null=True)
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
