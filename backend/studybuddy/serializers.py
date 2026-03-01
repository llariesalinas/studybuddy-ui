
from rest_framework import serializers
from .models import Tutor, Subjects, TutorAvailability

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
        fields = ['subject_code', 'subject_name', 'department']


class TutorDetailSerializer(serializers.ModelSerializer):

    fname = serializers.CharField(source='profile.fname')
    lname = serializers.CharField(source='profile.lname')
    bio = serializers.CharField(source='profile.bio', allow_null=True)

    class Meta:
        model = Tutor
        fields = [
            'profile_id',
            'fname',
            'lname',
            'rating_average',
            'hourly_rate',
            'total_sessions',
            'bio'
        ]

class TutorAvailabilitySerializer(serializers.ModelSerializer):
    day = serializers.SerializerMethodField()

    class Meta:
        model = TutorAvailability
        fields = ['id', 'day', 'time_slot', 'is_booked']

    def get_day(self, obj):
        return obj.get_day_display()  # converts 'Mon' to 'Monday', etc.