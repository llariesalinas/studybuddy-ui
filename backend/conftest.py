# Sets required env vars before pytest-django loads settings.
import os

os.environ.setdefault("SECRET_KEY", "django-insecure-test-only-key")
os.environ.setdefault("PAYMONGO_SECRET_KEY", "sk_test_placeholder")
os.environ.setdefault("DEBUG", "true")
