# Session Summary: Real email provider (shipped on Gmail SMTP)

**Date:** 2026-06-06
**Plan:** [2026-06-06-resend-email-integration.md](../plans/2026-06-06-resend-email-integration.md)
**Branch:** feature-darkmode-toggle

## What shipped

Replaced the dev-only Django console email backend with a real, config-driven email system.
Outbound mail still flows through Django's `send_mail()` in the three helpers in
`backend/studybuddy/views.py` — only the transport underneath changed.

**Active provider: Gmail SMTP** (not Resend). We started toward Resend (and `django-anymail`
is installed and wired), but Resend's only no-DNS sender (`onboarding@resend.dev`) can only
deliver to the Resend account owner, and a real Resend sender needs an owned + verified
domain — which we don't have yet. So for now we send via **Gmail SMTP** (no domain, free,
~500/day). Resend stays configured as a **one-line `.env` switch** for later.

### Transport selection ladder (in `settings.py`)
**Resend (if `RESEND_API_KEY` set) → SMTP → console (DEBUG only).** Switching providers is
config-only — no code changes.

### Changes
- `backend/requirements.txt` — added `django-anymail==15.0` (installed in `backend/venv`).
- `backend/backend/settings.py` — added `"anymail"` to `INSTALLED_APPS`; added
  `RESEND_API_KEY`/`ANYMAIL` config and the transport ladder (email block ~line 199).
- `backend/.env` (gitignored) — **Gmail SMTP active**: dedicated account
  `tutoringstuddybuddy@gmail.com`, App Password set, `DEFAULT_FROM_EMAIL=StudyBuddy <…@gmail.com>`.
  Resend key is **commented out, not deleted**, for the future switch.
- `backend/.env.example` — documented the transport options.
- Docs: plan doc + this summary + index row in `docs/plans/README.md`.

## Decisions
- **Gmail SMTP now** — no domain required; quickest path to actually delivering mail.
- **Resend kept as the upgrade path** — `django-anymail` installed/configured so re-enabling
  is one `.env` line once a domain is verified (SPF/DKIM).
- **Plain-text emails kept** (no HTML templates this round).

## What triggers email (live now)
- Login OTP → `POST /login/` and `POST /login/resend-otp/`
- Password reset link → `POST /password-reset/request/`
- Password-changed notice → `POST /password-reset/confirm/`

> OTP send is on the **login critical path**: if it fails, `POST /login/` returns 500 and login
> is blocked. Password-reset sends fail silently (logged only). Watch Gmail rate limits.

## Checks run
- `pip install django-anymail` → 15.0; `import anymail.backends.resend` OK. ✅
- `manage.py check` → no issues. ✅
- Backend selection verified for each env: blank key → console; SMTP vars set → SMTP;
  key set → `anymail.backends.resend.EmailBackend`. ✅
- Gmail SMTP **auth** check (`get_connection().open()`) → "SMTP AUTH OK" (no email sent). ✅

## Remaining / next steps
- **Live delivery test not yet run** — send a real email (e.g. the Forgot Password flow) and
  confirm it lands (may hit spam first time on a fresh Gmail sender).
- Nothing committed to git yet.
- App-wide production blockers (separate from email): `DEBUG=true`, `SECRET_KEY` is the
  insecure placeholder, PayMongo on test keys.

## Switching to Resend later
1. Verify a domain in Resend (SPF/DKIM DNS records).
2. In `backend/.env`: uncomment `RESEND_API_KEY=…` and set `DEFAULT_FROM_EMAIL` to the domain.
3. No code changes — the ladder auto-prefers Resend once the key is present.
