---
title: Async email worker reliability
date: 2026-08-12
status: In Progress
summary: Django-Q emails (password reset, verification approval, booking confirmed, renewal reminders/results) queue but never send because no process has ever consumed the queue, in dev or prod; make password reset synchronous and drain the rest via a Render cron job.
spec:
---

# Async email worker reliability

## Status/Progress Summary

In Progress as of 2026-08-12. Steps 1-2 done. Step 1 (sync password reset): implemented and
tested — `mailer.send_password_reset` mirrors `send_login_otp` (sync, rate-capped, raises
`EmailRateLimitError`), `send_password_reset_email_task` and `enqueue_password_reset` are
deleted, `views.password_reset_request` calls the sync function directly and stays on the
generic response even when rate-limited (no enumeration regression). 4 new tests added; full
suite (452 tests) has only 4 pre-existing, unrelated failures (test-data pollution from
repeated `--keepdb` runs, not this diff). Step 2 (local dev doc note): `AGENTS.md`'s command
table now documents the `qcluster` requirement. Step 4 (backlog purge) still to do; step 3
(Render Cron Job) is a manual dashboard action for the user — the plan's Steps section has
the exact command and schedule to set up when ready.

## Goal

Stop async emails from silently vanishing. Right now every email routed through
`mailer.enqueue_*` / `email_utils.enqueue_*` (password reset, password-changed notice,
verification approved/rejected, document renewal result/reminder, booking confirmed) is
written to the Django-Q ORM queue and never delivered, because nothing runs
`python manage.py qcluster` to consume it — not locally, not on Render. Confirmed directly
against the dev DB's `django_q.OrmQ` table: 19 tasks stuck, including a password-reset email
to a real account that's been sitting for 44 days (its token is almost certainly expired by
now) and two more from 16 minutes ago from live testing today.

Production runs as a single Render web service with no worker process, so this is very
likely happening in prod too, not just locally — the risk was called out explicitly in
`docs/plans/2026-06-06-email-async-hardening.md` ("Production: supervise qcluster") but that
supervision step was never actually built.

## Approach

Two independent fixes, decided together:

1. **Password reset becomes synchronous**, mirroring the login-OTP pattern already in
   `mailer.send_login_otp` / `views.create_login_otp_challenge`. It's already rate-capped
   (`is_send_allowed`), low-frequency, and the user is actively waiting on it — same profile
   as OTP. This removes password reset's dependency on a worker ever running, for the one
   flow where a silent drop is most damaging (locked-out user, no other recovery path).

2. **Everything else stays async, but the queue gets an actual consumer**: a Render Cron Job
   running `python manage.py qcluster --run-once` on a short interval (every 2-5 minutes)
   drains whatever's queued, then exits. Chosen over a permanently-running Background Worker
   service because this app's mail volume doesn't need near-instant delivery for
   approval/booking/renewal notices, and a cron job is a fraction of the cost of a second
   always-on paid instance. Locally, the equivalent is just remembering to run
   `python manage.py qcluster` alongside `runserver` — documented so it isn't invisible.

Not in scope for this pass: a monitoring/alerting layer that would have caught this sooner
(e.g. surfacing `OrmQ` backlog age somewhere in the SuperAdmin dashboard). Worth a follow-up
plan once this fix ships, so a stuck worker becomes visible instead of silent again.

## Steps

1. **Sync password reset**
   - Add `mailer.send_password_reset(user)` (sync), modeled on `send_login_otp`: checks
     `EMAIL_DELIVERY_DISABLED`, checks `is_send_allowed` and raises `EmailRateLimitError` if
     capped, renders + `_deliver()`s directly, no `async_task`.
   - Update `views.password_reset_request` to call it directly instead of
     `mailer.enqueue_password_reset(user)`, catching `EmailRateLimitError` the same way
     `create_login_otp_challenge`'s caller does, but keep the response body generic
     (`PASSWORD_RESET_GENERIC_MESSAGE`) either way — the existing enumeration protection
     (never revealing whether the email exists) must not regress just because we're now
     rate-limit-aware in the request path.
   - Remove `send_password_reset_email_task` and `enqueue_password_reset` once nothing calls
     them, or leave them dead-code-free by deleting outright (repo convention favors deleting
     over leaving unused code around).
   - `password_changed` notice (sent after a successful reset) stays async — it's a
     nice-to-have security notice, not blocking, no reason to add SMTP latency to the
     already-completed reset request.

2. **Local dev workflow doc**
   - Add a note to `.claude/CLAUDE.md` (or wherever the dev-commands table lives) that
     `python manage.py qcluster` must run alongside `runserver` for async email
     (verification approval/rejection, renewal reminder/result, booking confirmed,
     password-changed notice) to actually send. State plainly what happens if it's not
     running: tasks queue silently in `django_q.OrmQ`, no error surfaces anywhere.

3. **Render Cron Job (user action — no IaC in this repo, so the Render dashboard is the
   source of truth; this plan doc records the config for reference)**
   - Command: `python manage.py qcluster --run-once`
   - Schedule: every 2-5 minutes (exact cadence is a product call, not a technical one —
     shorter is fresher delivery, longer is fewer Render cron invocations)
   - Env: identical to the web service (DB creds, SMTP creds, `DJANGO_SETTINGS_MODULE`) —
     `--run-once` still needs a full app boot.
   - Verify after setup: trigger a booking confirmation or admin approval, watch `OrmQ`
     backlog drop to 0 within one cron interval.

4. **Backlog cleanup on the current stuck 19**
   - Purge the 2 permanently-corrupt rows (signature mismatch, undecodable — dead weight
     regardless of a worker running).
   - Purge the password-reset tasks (id 6, and the two from today) once step 1 ships — they're
     superseded by the sync path, and the 44-day-old one's token is stale enough that sending
     it now would be confusing rather than useful.
   - Let the remaining ~14 (booking-confirmed, application-approved, renewal-result) drain
     naturally once the cron job is live; they're idempotent notifications, no harm in a
     late-but-correct delivery.

## Risks

- **Sync password reset adds a live SMTP round-trip to that request's critical path** — same
  tradeoff already accepted for login OTP. A slow/broken SMTP provider makes password-reset
  requests hang or time out instead of silently queuing. Mitigate the same way OTP does:
  short timeout + limited retries (`EMAIL_SYNC_TIMEOUT` / `EMAIL_SYNC_MAX_ATTEMPTS`), fail
  honestly rather than hang.
- **Render Cron Jobs need the full app environment** (DB + SMTP credentials) configured
  identically to the web service; this is a manual dashboard step, not something committed to
  the repo, so it can drift out of sync with the web service's env over time with no
  automated check.
- **Cron interval means non-zero delivery latency** (up to the interval length) for
  everything still async — acceptable for this app's volume, but worth knowing if a future
  flow expects near-real-time delivery.
- **No render.yaml / IaC** in this repo — the cron job's existence and schedule live only in
  Render's dashboard. If the repo is ever migrated or the dashboard config is lost, this plan
  doc is the only record of what to recreate.
- **Purging queued tasks is destructive** — double-check the id list against the live `OrmQ`
  table at execution time rather than trusting the ids recorded here, since more tasks will
  have queued between writing this plan and acting on it.

## Checks to run

- `python manage.py test studybuddy.tests.EmailAuthTests studybuddy.tests.EmailUtilsRoleLabelTests studybuddy.tests.EmailDeliveryDisabledTests` —
  full green, including updated coverage for the now-sync password reset path (rate-limit
  case, delivery-disabled case).
- Manually trigger `password-reset/request/` locally with `qcluster` **not** running and
  confirm the email arrives anyway — proves the sync path no longer depends on the worker.
- Run `python manage.py qcluster --run-once` locally against a manually-queued
  `send_booking_confirmed_email_task` and confirm it drains and the email sends.
- Post-deploy (user action): confirm the Render Cron Job fires on schedule and `OrmQ`
  backlog trends to (and stays at) 0 between runs.

## Changelog

- **2026-08-12** — Plan created. Diagnosed root cause while investigating a "password reset
  doesn't send an email" report (same underlying cause as an earlier "verification approved
  doesn't send an email" fix): confirmed via `django_q.OrmQ` that 19 tasks are permanently
  stuck across every async email type, because no `qcluster` worker has ever run against
  this DB, in dev or prod. User chose Render Cron Job (`qcluster --run-once`) over an
  always-on worker service for cost reasons, and chose to make password reset synchronous
  (mirroring login OTP) rather than leave it dependent on the worker.
- **2026-08-12 (cont.)** — Implemented step 1. `mailer.send_password_reset` added (sync,
  rate-capped via the existing `is_send_allowed`/`EmailRateLimitError` machinery, same
  `EMAIL_SYNC_TIMEOUT`/`EMAIL_SYNC_MAX_ATTEMPTS` as OTP); `send_password_reset_email_task` and
  `enqueue_password_reset` deleted outright rather than left as dead code.
  `views.password_reset_request` now calls the sync function and catches
  `EmailRateLimitError` to keep the response generic even when capped, preserving the
  existing no-enumeration guarantee (a distinct response on rate-limit would have let an
  attacker distinguish a real, capped account from an unknown one). Added
  `test_password_reset_suppressed_when_disabled` / `_delivered_when_enabled` (mirroring the
  existing OTP pair) and `test_password_reset_send_raises_rate_limit_error_when_capped` /
  `test_password_reset_request_stays_generic_when_capped`. All 33 tests across
  `EmailAuthTests`, `EmailDeliveryDisabledTests`, `VerificationEmailWiringTests`,
  `RenewalReminderTests`, `EmailUtilsRoleLabelTests` pass. Full suite: 452 tests, 4 failures
  (1 fail + 3 errors), none touching `mailer.py`/`views.py`/email code — `SupportTicket`
  strike-window/wallet-deduction/tutee-search-pagination tests, with symptoms (duplicate
  `migration-tutee@cpu.edu` username, extra `SupportTicket`/tutee rows) consistent with
  `--keepdb` data pollution from the many repeated runs against the same DB today rather than
  a regression — matches the same "pre-existing, unrelated" 4-failure pattern already
  recorded in `docs/plans/README.md` from an earlier session. Step 1 done. Step 2 done:
  `AGENTS.md`'s command table now documents that `qcluster` must run alongside `runserver`
  for async email, and what silently breaks without it. Steps 3 (Render Cron Job) and 4
  (backlog purge) remain — both need the user, not something this session can do.
