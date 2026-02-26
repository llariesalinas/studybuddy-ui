
from rest_framework import serializers
from .models import Tutor, Subjects

# Create Serializers here.

class TutorSearchSerializer(serializers.ModelSerializer):
   fname = serializers.CharField(source='profile.fname')
   lname = serializers.CharField(source='profile.lname')

   class Meta:
       model = Tutor
       fields = ['id','fname', 'lname']

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subjects
        fields = ['subject_code', 'subject_name', 'department']