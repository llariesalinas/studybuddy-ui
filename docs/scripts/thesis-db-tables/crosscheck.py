# -*- coding: utf-8 -*-
"""Independent check: does the hand-written table data match Django's real models?

Loads the Django app registry (no database connection needed) and compares the concrete
field list of every model against the rows written into the document.
"""
import os
import sys

sys.path.insert(0, r"C:\FIles\Studybuddy\FrontEnd\studybuddy-ui\backend")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# settings.py reads these via os.getenv; values are irrelevant since we never connect.
os.environ.setdefault("DB_NAME", "x")
os.environ.setdefault("DB_USER", "x")
os.environ.setdefault("DB_PASSWORD", "x")
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_PORT", "5432")
os.environ.setdefault("SECRET_KEY", "x")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

import django
django.setup()

from django.apps import apps
from tables_data import BLOCKS

# Map each documented block to the model backing it.
MODEL_FOR = {
    "auth_users (django built in)": ("auth", "User"),
    "token_blacklist_outstandingtoken (SimpleJWT built in)": ("token_blacklist", "OutstandingToken"),
    "token_blacklist_blacklistedtoken (SimpleJWT built in)": ("token_blacklist", "BlacklistedToken"),
    "email_otp_challenge": ("studybuddy", "EmailOTPChallenge"),
    "partner_institution": ("studybuddy", "PartnerInstitution"),
    "institution_request": ("studybuddy", "InstitutionRequest"),
    "user_profile": ("studybuddy", "UserProfile"),
    "strand": ("studybuddy", "Strand"),
    "course": ("studybuddy", "Course"),
    "subjects": ("studybuddy", "Subjects"),
    "tutor": ("studybuddy", "Tutor"),
    "tutor_subjects": ("studybuddy", "TutorSubjects"),
    "preference": ("studybuddy", "Preference"),
    "preference_subjects (Many-to-Many Bridge)": None,  # auto-created through table
    "tutor_availability": ("studybuddy", "TutorAvailability"),
    "tutor_availability_override": ("studybuddy", "TutorAvailabilityOverride"),
    "booking": ("studybuddy", "Booking"),
    "session_check_in": ("studybuddy", "SessionCheckIn"),
    "rating": ("studybuddy", "Rating"),
    "payment_method": ("studybuddy", "PaymentMethod"),
    "payment": ("studybuddy", "Payment"),
    "wallet": ("studybuddy", "Wallet"),
    "transaction": ("studybuddy", "Transaction"),
    "withdrawal_request": ("studybuddy", "WithdrawalRequest"),
    "wallet_top_up": ("studybuddy", "WalletTopUp"),
    "tutor_application": ("studybuddy", "TutorApplication"),
    "tutor_document_renewal_review": ("studybuddy", "TutorDocumentRenewalReview"),
    "tutee_application": ("studybuddy", "TuteeApplication"),
    "tutee_document_renewal_review": ("studybuddy", "TuteeDocumentRenewalReview"),
    "chat_room": ("studybuddy", "ChatRoom"),
    "message": ("studybuddy", "Message"),
    "notification": ("studybuddy", "Notification"),
    "support_ticket": ("studybuddy", "SupportTicket"),
    "platform_activity": ("studybuddy", "PlatformActivity"),
    "email_send_log": ("studybuddy", "EmailSendLog"),
}

problems = []
checked = 0

for block in BLOCKS:
    target = MODEL_FOR.get(block["name"], "MISSING")
    if target == "MISSING":
        problems.append("no model mapping for block %r" % block["name"])
        continue
    if target is None:
        continue  # auto-created M2M through table, no model class

    model = apps.get_model(*target)
    # Concrete columns only: skip reverse relations and M2M (which live in their own table).
    real = [f.name for f in model._meta.get_fields()
            if getattr(f, "concrete", False) and not f.many_to_many]
    documented = [r[0] for r in block["rows"]]

    # Django names the implicit pk "id"; the doc uses the same.
    missing = [f for f in real if f not in documented]
    extra = [f for f in documented if f not in real]

    checked += 1
    status = "OK"
    if missing or extra:
        status = "MISMATCH"
        problems.append((block["name"], "missing from doc: %s" % missing,
                         "in doc but not in model: %s" % extra))
    print("%-45s model=%-30s real=%2d doc=%2d  %s"
          % (block["name"][:45], target[1], len(real), len(documented), status))
    if missing:
        print("      MISSING FROM DOC : %s" % missing)
    if extra:
        print("      NOT IN MODEL     : %s" % extra)

print()
print("models cross-checked: %d" % checked)

# Also confirm we did not miss any concrete model in the studybuddy app.
documented_models = {t[1] for t in MODEL_FOR.values() if t}
app_models = {m.__name__ for m in apps.get_app_config("studybuddy").get_models()}
undocumented = sorted(app_models - documented_models)
print("concrete models in studybuddy app: %d" % len(app_models))
if undocumented:
    problems.append("undocumented models: %s" % undocumented)
    print("UNDOCUMENTED MODELS: %s" % undocumented)
else:
    print("every model in the studybuddy app is documented")

print()
print("RESULT:", "ALL CHECKS PASSED" if not problems else "PROBLEMS FOUND")
for p in problems:
    print("  -", p)
