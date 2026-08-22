---
title: Trusted-device login OTP
date: 2026-08-21
status: In Progress
summary: OTP once per device per 7 idle days instead of on every login, backed by a revocable TrustedDevice token
spec:
---

# Trusted-device login OTP

## Status & Progress Summary

**In Progress — backend done (steps 1-9), frontend outstanding (steps 10-14).**

Design settled with the user on 2026-08-21: 7-day sliding trust, automatic (no checkbox), revoked
by password reset / suspension / user-initiated logout / admin action, same rules for admins. The
one point narrowed beyond what was chosen: automatic logouts (idle timeout, refresh failure) do
*not* revoke trust — only the sidebar logout button does.

`TrustedDevice`, the migration, the four helper functions, and all five call sites (`login/`,
`login/verify-otp/`, `logout_view`, `password_reset_confirm`, the admin PATCH) are in, with 13
passing tests in `TrustedDeviceLoginTests`. Nothing on the frontend consumes `device_token` yet —
`src/stores/auth.js` doesn't send or store it, so every login still OTPs today. Steps 10-14 are
the remaining work.

## Goal

Panel comment: *"Remove the OTP requirement for every single login. (Switch to a standard session
token or only require it for first-time device logins)."*

Today `login/` mints an `EmailOTPChallenge` on every successful password check and only
`login/verify-otp/` returns the JWT payload, so every login costs an email round trip. After this
change, OTP is a **first-time-on-this-device** step whose validity behaves like a token expiry: a
device that verified once stays trusted for 7 days of inactivity, and only an expired or revoked
trust re-challenges.

## Approach

**A real server-side `TrustedDevice` row, not a client-side flag.** On successful OTP verification
the server issues an opaque device token, stores only its HMAC (same `SECRET_KEY`-keyed SHA-256
pattern as `hash_otp_code`), and returns it in the login payload. The client keeps it in
`localStorage` next to the JWTs and replays it on the next `login/`. The server decides; the client
only carries the token. That keeps the trust auditable and revocable, which a "skip OTP"
localStorage boolean would not be.

Decisions taken with the user:

| Decision | Choice | Why |
| --- | --- | --- |
| Trust lifetime | **7 days, sliding** | Each accepted login pushes `expires_at` out 7 days. Tighter than the usual 30 because CPU students share lab machines. |
| Opt-in | **Automatic, no checkbox** | Any successful OTP verification trusts that browser. Zero visual change to `Login.vue`; nothing new to explain to the panel. |
| Revocation | Password reset, suspension, user-initiated logout, admin action | See below. |
| Admin/SuperAdmin accounts | **Same rules** | One code path. The panel's comment was unqualified. |

**Token format:** `"<device_id>.<secret>"` -- a UUID for O(1) lookup plus 32 bytes of
`secrets.token_urlsafe` entropy compared with `constant_time_compare`. Never store the raw secret.

**Logout is narrower than it sounds.** `handleIdleLogout` (`src/stores/auth.js:68`) and the
refresh-failure path (`:157`) call the *same* `logout()` as the sidebar button. If logout revoked
trust literally, a user would be re-challenged after every 10 idle minutes -- worse than today. So
only the **user-initiated** logout (the confirm button in `App.vue:612`) forgets the device; the
router-guard and idle paths leave the trust intact. `App.vue:617` is the single call site that
passes the flag.

**Suspension and admin revocation ride the existing admin PATCH** (`admin_views.py:517`) rather
than a new endpoint: setting `is_suspended: true` revokes that user's devices as a side effect, and
a new `revoke_trusted_devices: true` field in the same PATCH gives the explicit admin action. The
button goes in `SuperAdminUserModal.vue`, which already edits these fields.

`LOGIN_OTP_DISABLED` (the email-outage escape hatch) is untouched and still short-circuits
everything.

## Steps

**Backend**

1. Add `TrustedDevice` to `backend/studybuddy/models.py`: `user` FK (CASCADE,
   `related_name='trusted_devices'`), `device_id` UUID (unique, indexed), `token_hash`
   `CharField(max_length=64)`, `expires_at`, `revoked_at` (nullable), `last_used_at`, `created_at`,
   plus `user_agent` (truncated `CharField`) and `last_ip` for the admin audit line. `Meta.indexes`
   on `['user', 'revoked_at']` and `['expires_at']`, `ordering = ['-last_used_at']`. Make the
   migration.
2. Add `TRUSTED_DEVICE_TTL_SECONDS = 7 * 24 * 60 * 60` to `settings.py` beside
   `LOGIN_OTP_TTL_SECONDS`, with a comment that it is a *sliding* window.
3. In `views.py`, next to the OTP helpers (~line 654), add `hash_device_token`,
   `issue_trusted_device(user, request)`, `consume_trusted_device(user, raw_token, request)`
   (validates, slides `expires_at`, stamps `last_used_at`/`last_ip`, returns bool), and
   `revoke_trusted_devices(user, device_id=None)`.
4. `login/`: after the suspension and domain checks pass and before
   `create_login_otp_challenge`, if `request.data['device_token']` is accepted by
   `consume_trusted_device`, return `build_login_response_payload(user, profile)` directly.
   On the suspension 403, revoke that user's devices first.
5. `login/verify-otp/`: on success, call `issue_trusted_device` and add `device_token` to the
   response payload (add it in the view, not inside `build_login_response_payload`, which other
   callers reuse).
6. `logout_view`: accept an optional `device_token` and revoke that single device.
7. `password_reset_confirm`: call `revoke_trusted_devices(user)` next to the existing
   `blacklist_user_refresh_tokens(user)` at `views.py:1697`.
8. `admin_views.py` user PATCH: revoke on `is_suspended: true`, and handle a new
   `revoke_trusted_devices: true` field (log it in `changed_fields` like its neighbours).
9. Tests in `backend/studybuddy/tests.py`: OTP still required with no token; second login with the
   issued token skips OTP; expired token re-challenges; revoked token re-challenges; another user's
   token is rejected; sliding renewal pushes `expires_at`; suspension revokes.

**Frontend**

10. `src/config.js`: no new TTL constant (the expiry is the server's), but add the
    `DEVICE_TOKEN_STORAGE_KEY` name alongside the other auth constants rather than inlining the
    string.
11. `src/stores/auth.js`: read/write the device token in `localStorage`; send it in the `login/`
    POST body; store `responseData.device_token` in `completeLogin` when present; give `logout` a
    `{ forgetDevice = false }` option that posts the token and clears it, and *never* clear it on
    the idle/refresh-failure paths.
12. `src/App.vue:612`: call `authStore.logout({ forgetDevice: true })`.
13. `src/components/SuperAdminUserModal.vue`: a "Sign out all devices" action that PATCHes
    `revoke_trusted_devices: true`, matching the modal's existing control patterns.
14. `src/stores/auth.test.js` (or a new one): device token is sent on login, persisted from
    verify-otp, kept on idle logout, cleared on user logout.

## Risks

- **Silent security regression.** A stolen `localStorage` token is a 7-day bypass of the second
  factor. Mitigated by hashing at rest, per-device revocation, and revoking on password reset -- but
  it is a real, deliberate trade the panel asked for. Say so in the defense, don't hide it.
- **Sliding expiry never expiring.** A daily user is trusted forever. That is the intent, but it
  means the OTP is effectively a one-time enrolment for active users; confirm that reads as
  acceptable to the panel.
- **Shared lab machines.** Automatic trust with no checkbox means a student who logs in on a lab PC
  leaves a trusted device behind. The user-initiated logout revoking trust is what covers this,
  which is exactly why the narrower logout reading above matters.
- **Existing sessions.** No migration path needed -- nobody has a device token, so the first login
  after deploy still OTPs. Correct by construction.
- **`LOGIN_OTP_DISABLED` interaction.** When email delivery is off, `login/` returns the payload
  before any device logic runs, so no device is ever enrolled during an outage. Acceptable; note it
  so nobody debugs it later as a bug.

## Checks to run

- `cd backend && python manage.py makemigrations --check --dry-run` -- clean once step 1's migration
  is committed.
- `cd backend && python manage.py test studybuddy` -- all pass, including the new trusted-device
  tests.
- `npm run test` -- auth store tests pass.
- `npm run lint` and `npm run build` -- clean.
- Manual: log in (OTP), close and reopen the tab, log in again -- no OTP. Then log out via the
  sidebar button and log in -- OTP returns.

## Changelog

- **2026-08-22** — Steps 1-9 (backend) implemented: `TrustedDevice` model and migration, the
  `trusted_devices.py` helper module, and all five call sites. Added `TrustedDeviceLoginTests`
  (13 tests). Fixed an unrelated test-infra bug found along the way: `LoginRateThrottle` reads its
  rate from `DEFAULT_THROTTLE_RATES` once at import time, so `override_settings(REST_FRAMEWORK=…)`
  never reaches it — the tests now patch `LoginRateThrottle.THROTTLE_RATES` directly instead.
  Status: In Progress (frontend steps 10-14 outstanding).
- **2026-08-21** — Plan created from the OTP design session. Recorded the four decisions (7-day
  sliding TTL, automatic trust with no checkbox, four revocation triggers, no admin exemption) and
  the narrowed reading of "logout revokes trust" that keeps idle/refresh-failure logouts from
  re-challenging every 10 minutes. Status: Draft.

