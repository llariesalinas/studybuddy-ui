# Plan: Replace Django console email backend with a real email provider

> Outcome: shipped on **Gmail SMTP** (no domain needed); Resend is wired up as the
> documented one-line upgrade once a domain is verified.

**Date:** 2026-06-06
**Branch:** feature-darkmode-toggle
**Spec:** Inline in this document
**Status:** Done

---

## Context

The StudyBuddy backend (`backend/`, Django 6.0.2) only sent real email in development as
text printed to the Django console (`console.EmailBackend`). A working SMTP fallback existed
in `settings.py`, but no real provider was wired up, so no email actually left the machine.
We want a proper email system that actually delivers OTP and password-reset emails.

All outbound mail already flows through Django's `send_mail()` in three helpers in
`backend/studybuddy/views.py`, so this is a **transport/config change, not a rewrite**.
We built a config-driven transport ladder (`django-anymail` installed for Resend support)
that keeps `send_mail()` working unchanged regardless of provider.

> **Final outcome: Gmail SMTP is the active provider, not Resend.** Resend's only no-DNS
> sender (`onboarding@resend.dev`) can only deliver to the Resend account owner, and a real
> Resend domain requires owning + verifying a domain — which we don't have yet. So for now
> we use **Gmail SMTP** (no domain needed, free, ~500 emails/day). Resend stays wired up and
> is a **one-line `.env` switch** once a domain is available. See "Final state" below.

**Decisions (confirmed with user):**
- Provider for now: **Gmail SMTP** (no domain required). Resend is the documented upgrade path.
- Integration kept flexible via the **Resend → SMTP → console** selection ladder, so switching
  providers is config-only — no code changes.
- Content: **keep existing plain-text messages** (no HTML templates this round).
- `django-anymail` is installed and configured so re-enabling Resend later needs no new code.

## What actually sends email (scope)

Only three functions, all in `backend/studybuddy/views.py`, all using `send_mail(..., from_email=None)`:
- `send_login_otp_email` — login 2FA code
- `send_password_reset_email` — reset link
- `send_password_changed_email` — confirmation

No changes were made to these — they work as-is once the backend is swapped.
(Booking/payment/support "notifications" are in-app, not email — out of scope.)

## Approach

Anymail becomes the email backend whenever a `RESEND_API_KEY` is present, slotted into the
existing console/SMTP selection logic in `settings.py` so console (no config) and SMTP
(legacy) still work as fallbacks. No changes to the `send_mail` call sites.

## Steps

1. Save this plan; add a row to `docs/plans/README.md`.
2. `backend/requirements.txt`: add `django-anymail`. Install into `backend/venv`.
3. `backend/backend/settings.py` `INSTALLED_APPS`: add `"anymail"`.
4. `backend/backend/settings.py` email block: add `RESEND_API_KEY` + `ANYMAIL`, prefer the
   `anymail.backends.resend.EmailBackend` when the key + `DEFAULT_FROM_EMAIL` are set;
   keep SMTP and console as fallbacks.
5. `backend/.env.example` (placeholder) and `backend/.env` (real key, gitignored): add
   `RESEND_API_KEY` and set `DEFAULT_FROM_EMAIL=StudyBuddy <onboarding@resend.dev>`.
6. External (user): create Resend account, generate API key, paste into `backend/.env`.

## Risks

- **Test-sender limitation:** `onboarding@resend.dev` only delivers to the Resend account
  owner's own verified email until a custom domain is verified (SPF/DKIM) — production follow-up.
- **Synchronous sending:** `send_mail()` runs inline (no Celery); fine for current volume.
- **Secret handling:** API key lives only in `.env`, never committed or in `.env.example`.
- **Version pin:** confirm the installed `django-anymail` actually ships the Resend backend.

## Checks to run

1. `pip install django-anymail` succeeds; `python -c "import anymail.backends.resend"` imports.
2. `python manage.py check` passes with `anymail` in `INSTALLED_APPS`.
3. No-key fallback: key unset + `DEBUG=true` → mail still prints to console.
4. Backend selection resolves correctly per env (Resend vs SMTP vs console).
5. SMTP auth check: `get_connection().open()` succeeds against Gmail.
6. End-to-end (pending): Forgot Password (`POST /password-reset/request/`) delivers a real email.

## Final state (what actually shipped)

**Active provider: Gmail SMTP** — chosen over Resend because we have no domain to verify yet,
and Resend's no-DNS sandbox sender only reaches the account owner.

- Dedicated Gmail account `tutoringstuddybuddy@gmail.com` sends as `StudyBuddy <…@gmail.com>`,
  authenticated with a Gmail **App Password** (requires 2-Step Verification on the account).
- Limits/caveats: free Gmail caps ~500 emails/day; first emails may land in spam (fresh sender,
  no custom-domain DKIM).
- `settings.py` transport ladder: **Resend (if `RESEND_API_KEY` set) → SMTP → console (DEBUG)**.
  Gmail SMTP is used because `RESEND_API_KEY` is left blank/commented in `.env`.
- The Resend key is **commented out, not deleted**, in `backend/.env`.

**OTP send is on the login critical path:** if the OTP email fails, `POST /login/` returns 500
and login is blocked. Password-reset sends fail silently (logged only). Watch Gmail rate limits.

### Switching to Resend later (when a domain is owned)
1. Verify a domain in Resend (add SPF/DKIM DNS records).
2. In `backend/.env`: uncomment `RESEND_API_KEY=…` and set `DEFAULT_FROM_EMAIL` to the domain
   address (e.g. `StudyBuddy <no-reply@yourdomain.com>`).
3. No code changes — the ladder auto-prefers Resend once the key is present.
