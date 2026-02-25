from django.db import models
from django.contrib.auth.models import User ### allows the use of auth user model for authentication and user management


# Create your models here.

 
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fname = models.CharField(max_length=100)
    mname = models.CharField(max_length=100, blank=True)
    lname = models.CharField(max_length=100)
    course = models.CharField(max_length=100, blank=True)
    year_level = models.IntegerField(null=True, blank=True)

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

    teaching_level = models.CharField(max_length=100)
    can_online = models.BooleanField(default=True)
    can_f2f = models.BooleanField(default=False)

    rating_average = models.FloatField(default=0)
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2)
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