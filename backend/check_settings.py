import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

key = getattr(settings, 'PAYMONGO_SECRET_KEY', None)

if key == 'sk_test_placeholder' or key is None:
    print("❌ ERROR: Secret key is still using the placeholder or is missing.")
else:
    # Print only the first few characters for security
    print(f"✅ SUCCESS: Secret key is being read! (Starts with: {key[:7]}...)")
