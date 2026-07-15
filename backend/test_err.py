import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()
from studybuddy.models import User, UserProfile

u = User(username='test_err')
try:
    p = u.userprofile
except UserProfile.DoesNotExist:
    print('Caught UserProfile.DoesNotExist')
except Exception as e:
    print('Failed:', type(e))
