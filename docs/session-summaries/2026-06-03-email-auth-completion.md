# StudyBuddy Email Auth Completion - 2026-06-03

## Summary

Implemented the email-backed auth feature for StudyBuddy:

- Provider-agnostic SMTP settings for real email delivery.
- Password reset request and confirm flow.
- Email OTP login step before issuing JWT tokens.
- Vue auth pages for forgot password, reset password, and OTP verification.
- Local development fallback that prints emails to Django logs, plus a DEBUG-only OTP display on the login screen.

Important: local development still does not send to a real inbox unless SMTP env vars are configured in `backend/.env`.

## Backend Changes

- Added email settings in `backend/backend/settings.py`:
  - `EMAIL_HOST`
  - `EMAIL_PORT`
  - `EMAIL_HOST_USER`
  - `EMAIL_HOST_PASSWORD`
  - `EMAIL_USE_TLS`
  - `DEFAULT_FROM_EMAIL`
  - `EMAIL_TIMEOUT`
  - `PASSWORD_RESET_TIMEOUT`
  - `LOGIN_OTP_TTL_SECONDS`
  - `LOGIN_OTP_MAX_ATTEMPTS`

- Added `EmailOTPChallenge` in `backend/studybuddy/models.py` with migration `0047_emailotpchallenge.py`.
- Added auth endpoints in `backend/studybuddy/urls.py`:
  - `POST /api/password-reset/request/`
  - `POST /api/password-reset/confirm/`
  - `POST /api/login/verify-otp/`
  - `POST /api/login/resend-otp/`

- Updated `login_view` in `backend/studybuddy/views.py` so valid username/password starts an OTP challenge instead of immediately returning JWTs.
- Added HMAC hashing for OTP codes. Plain OTP values are not stored in the database.
- Added refresh-token blacklisting after password reset.
- Added DEBUG-only `debug_code` in OTP responses to make local testing reliable before SMTP is configured.

## Frontend Changes

- Added routes in `src/router/index.js`:
  - `/forgot-password`
  - `/reset-password/:uid/:token`
  - `/password-reset/confirm` for older query-string reset links.

- Added pages:
  - `src/views/ForgotPassword.vue`
  - `src/views/ResetPassword.vue`

- Updated `src/views/Login.vue`:
  - Handles OTP step after password submission.
  - Supports resend OTP.
  - Shows DEBUG-only development code when backend sends `debug_code`.
  - Links the Forgot? action to `/forgot-password`.

- Updated `src/stores/auth.js` to support both OTP challenge responses and completed JWT login responses.
- Updated `src/services/api/api.js` public endpoint allowlist for auth endpoints.
- Updated `index.html` with `no-referrer` behavior for safer reset-link handling.

## Email Delivery Behavior

Current local behavior:

- `backend/.env` has `DEBUG=true`.
- No SMTP settings are configured.
- Django uses `django.core.mail.backends.console.EmailBackend`.
- Emails are printed to `backend/django-dev.out.log`, not sent to a real inbox.

To check local console emails from CMD:

```bat
type backend\django-dev.out.log
findstr /C:"verification code" backend\django-dev.out.log
findstr /C:"reset-password" backend\django-dev.out.log
```

To enable real email delivery, add SMTP settings to `backend/.env`, for example with Resend:

```env
EMAIL_HOST=smtp.resend.com
EMAIL_PORT=587
EMAIL_HOST_USER=resend
EMAIL_HOST_PASSWORD=<resend_api_key>
EMAIL_USE_TLS=true
DEFAULT_FROM_EMAIL=StudyBuddy <onboarding@resend.dev>
EMAIL_TIMEOUT=10
```

Then restart the Django backend.

## Additional Fixes Made During Testing

- Added missing `ForgotPassword.vue` and `ResetPassword.vue` files after Vite failed to resolve the new router imports.
- Added forgot/reset routes to the public layout guard in `App.vue` so the rating reminder and app chrome do not appear on auth pages.
- Applied migration `studybuddy.0047_emailotpchallenge` locally so OTP challenge persistence works.
- Started Django on `127.0.0.1:8000` so the Vite `/api` proxy no longer returns backend-proxy 500s.
- Fixed reset email links to point to `/reset-password/<uid>/<token>`.
- Changed reset email text so the reset URL appears on its own line and is easier to copy from console logs.
- Fixed logout modal errors by replacing Bootstrap JS modal control with a Vue-controlled logout confirmation.
- Added DEBUG-only OTP display on the login page because console logs can contain old codes and are awkward to search.

## Verification

Backend:

```bat
cd backend
venv\Scripts\python.exe manage.py migrate studybuddy
venv\Scripts\python.exe manage.py test studybuddy.tests.EmailAuthTests --keepdb
```

Frontend targeted checks run:

```bat
npx eslint src/App.vue
npx eslint src/views/Login.vue src/stores/auth.js
npx eslint src/App.vue src/views/ResetPassword.vue src/router/index.js
```

Live endpoint verified through Vite proxy:

```text
POST http://localhost:5173/api/password-reset/request/ -> 200
```

Full `npm run build` was attempted earlier but could not be fully rerun after the last small patches because the elevated build run was declined.

## Known Follow-Ups

- Configure a real SMTP provider before expecting emails to arrive in inboxes.
- For production, use a verified sender/domain instead of `onboarding@resend.dev`.
- Consider invalidating older unconsumed OTP challenges when a new login challenge is issued.
- Consider adding `EMAIL_USE_SSL` support for SMTP providers that require port `465`.
- Commit the finished email-auth feature once the current working tree is reviewed.
