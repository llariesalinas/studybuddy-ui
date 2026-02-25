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
    role = models.CharField(max_length=20)  # Tutee, Tutor, Admin
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.fname} {self.lname}"