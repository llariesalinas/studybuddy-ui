---
title: Tutee enrollment verification — Phase 4 (email & dev tools)
date: 2026-07-01
status: Draft
spec: 2026-07-01-tutee-verification-overview.md
---

# Phase 4 — Email & dev tools

> Part of [Tutee enrollment verification — overview](2026-07-01-tutee-verification-overview.md). Phase 3 is
> Done; see the session handoff at
> [`docs/session-summaries/2026-07-02-tutee-verification-phase4-handoff.md`](../session-summaries/2026-07-02-tutee-verification-phase4-handoff.md)
> for environment gotchas.

<!-- LIVING SUMMARY: keep this section and the Changelog current on every edit -->
## Status & Progress Summary

**Status: Draft — fleshed out, awaiting go-ahead to implement.** Design locked, no open decisions. Codebase
verified against current `HEAD` (post-Phase-3) on 2026-07-02: every file/line reference below was read
directly, not assumed from the outline.

## Goal

Notify users of verification events and renewal deadlines for both roles, and give SuperAdmins a way to
demo lapse/reminders without waiting out the real 90-day/30-day windows.

## Approach

### 1. Generalize event-driven emails (`email_utils.py`)

Current state: three tutor-worded functions, each taking only `profile` (`send_application_received_email`
at `email_utils.py:33`, `send_application_approved_email:57`, `send_application_rejected_email:83`). No
function exists for renewal-review results at all.

- Add `role_label='tutor'` kwarg to all three existing functions. Default preserves every current call site
  byte-identical. Subject/body text swaps `"Tutor"` → `role_label.capitalize()` (e.g. `"Your StudyBuddy
  {role_label.capitalize()} Application"`); the rejected email's `status_url` and approved email's
  `login_url` stay role-agnostic (`/application-status`, `/login` — both routes already serve either role
  post-Phase-3).
- Add a new function `send_document_renewal_result_email(profile, role_label, new_status, reason='')` in
  the same file, same synchronous `_get_smtp_connection()` + `send_mail` pattern as the other three.
  `new_status` is `'approved'` or `'rejected'`; message body branches on it (approved: renewal accepted,
  verification current again; rejected: reason shown, resubmit via `/application-status`, mirroring
  `send_application_rejected_email`'s wording).

### 2. Wire event-driven emails into existing call sites

No-op for tutor call sites (default `role_label='tutor'` keeps them unchanged) except where noted:

- `views.py:885` (tutor registration) — unchanged.
- `views.py:4597` (tutor resubmit) — unchanged.
- `views.py` tutee-application `created` branch (currently `views.py:4718-4724`, no email) — add
  `send_application_received_email(request.user.userprofile, role_label='tutee')` after the
  `PlatformActivity.objects.create(...)` call, wrapped in the same `try/except: logger.exception(...)`
  pattern used at `views.py:4595-4599`.
- `views.py` tutee resubmit branch (currently `views.py:4750-4757`, has an explicit "deliberately not sent
  yet" comment) — replace the comment with the same call.
- `admin_views.py:504-511` (`AdminTutorApplicationDetailView.patch`) — pass `role_label='tutor'` explicitly
  (no behavior change; makes the call site self-documenting once the tutee twin exists).
- `admin_views.py:654-655` (`AdminTuteeApplicationDetailView.patch`, currently a comment, no email) —
  replace with the same `send_application_approved_email` / `send_application_rejected_email` calls,
  `role_label='tutee'`, same `try/except: logger.exception(...)` wrapper as the tutor view.
- `admin_views.py:563-567` (`AdminTutorDocumentRenewalDetailView.patch`, after the reminder-field reset on
  approval) — add `send_document_renewal_result_email(renewal.profile, 'tutor', new_status,
  rejection_reason)` inside a `try/except`, called for **both** `approved` and `rejected` (move it after the
  `if new_status == 'approved':` block so it fires on both branches).
- `admin_views.py:707-710` (`AdminTuteeDocumentRenewalDetailView.patch`) — same, `role_label='tutee'`.

### 3. Opportunistic renewal reminders

Hook: `get_document_review_context(application)` at `views.py:156-185` is the single function both
`get_tutor_document_review_context` (`views.py:188-197`) and `get_role_document_review_context`'s tutee
branch (`views.py:200-214`) call — and it already computes `document_renewal_status` and `due_at`. It's
invoked from both `profile_status` (`views.py:915-925`, called on the frontend's periodic/route-guard reads)
and the login response (`views.py:137`), which together satisfy "opportunistic, no scheduler."

- Change `get_document_review_context`'s signature to `get_document_review_context(application, role_label)`
  and update its two call sites to pass `'tutor'` / `'tutee'` respectively (`profile.role.lower()` would
  also work but the two call sites already know their own role, so pass the literal).
- Add a module-level helper `_maybe_send_renewal_reminder(application, role_label)`, called from the end of
  `get_document_review_context` only when `document_renewal_status == 'verified'` and `due_at` is not None
  (skip for `due`/`pending`/`rejected` — those states have their own UI banner, not a reminder):
  ```
  now = timezone.now()
  if due_at - timedelta(days=1) <= now < due_at and application.reminder_1day_sent_at is None:
      mailer.enqueue_document_renewal_reminder(application.profile, role_label, 1, due_at)
      application.reminder_1day_sent_at = now
      application.save(update_fields=['reminder_1day_sent_at'])
  elif due_at - timedelta(days=7) <= now < due_at - timedelta(days=1) and application.reminder_7day_sent_at is None:
      mailer.enqueue_document_renewal_reminder(application.profile, role_label, 7, due_at)
      application.reminder_7day_sent_at = now
      application.save(update_fields=['reminder_7day_sent_at'])
  ```
  Only one reminder fires per call (1-day checked first since it's the narrower/more urgent window).
- `mailer.py`: add `enqueue_document_renewal_reminder(profile, role_label, days_remaining, due_at)` (no send
  cap — precedent is `enqueue_password_changed:184-187`, uncapped because it's a one-per-window event driven
  by dedup fields, not user-triggerable spam) that calls
  `async_task("studybuddy.mailer.send_document_renewal_reminder_email_task", profile.user.id, role_label,
  days_remaining, due_at.isoformat())`, and the task function
  `send_document_renewal_reminder_email_task(user_id, role_label, days_remaining, due_at_iso)` following the
  `send_password_changed_email_task:158-169` shape (re-fetch user, `_render`, `_deliver`).
- New templates `templates/email/document_renewal_reminder.txt` + `.html` (single template, `days_remaining`
  and `due_at` in context — no separate 7-day/1-day templates), extending `base.html` like the existing
  templates.
- `models.py:139-146` (`EmailSendLog.PURPOSE_CHOICES`) — add
  `PURPOSE_DOCUMENT_RENEWAL_REMINDER = 'document_renewal_reminder'`. This is a Django migration
  (state-only, no schema change — same shape as `0059_alter_platformactivity_activity_type.py`).
- **Accepted race condition**: two concurrent `profile_status` reads inside the same window could both
  read the dedup field as `None` before either write lands (no `select_for_update` on this read-mostly
  path). Worst case is one duplicate reminder email, never a lost one — consistent with the outline's
  existing "no scheduler" tradeoff. Not worth locking a GET-triggered side effect for.

### 4. SuperAdmin dev tools

- `settings.py` — add `VERIFICATION_DEV_TOOLS_ENABLED = env_bool('VERIFICATION_DEV_TOOLS_ENABLED', False)`
  near the other `env_bool` flags (pattern at `settings.py:22-23`, e.g. `DEBUG` at line 35). Default `False`
  so it's inert unless explicitly opted into in a dev `.env`.
- New view in `admin_views.py`: `AdminUserVerificationDevToolsView(BaseAdminView)`,
  `permission_classes = [permissions.IsAuthenticated, IsSuperAdminUser]`, `post(self, request, pk)`:
  1. `if not settings.VERIFICATION_DEV_TOOLS_ENABLED: return Response(..., status=403)` — checked **first**,
     before any query, so it 403s even for a valid SuperAdmin token when the flag is off in that
     environment (the outline's non-negotiable: unreachable in prod regardless of who's asking).
  2. Look up `UserProfile` by `pk`; 404 if missing, 400 if `role not in ('Tutor', 'Tutee')`.
  3. `action = request.data.get('action')`, one of `send_received` / `send_approved` / `send_rejected` /
     `send_reminder_7day` / `send_reminder_1day` / `force_expire`; 400 on anything else.
  4. `send_*` actions call the Section 1/3 email functions directly and synchronously (immediate feedback
     for a manual admin action, unlike the real async reminder path) using
     `role_label = profile.role.lower()` and the profile's real application object (via
     `get_verification_application(profile)`, already defined at `views.py:238-243` — reuse it, don't
     reimplement); 404 if the profile has no application yet (nothing to email about).
  5. `force_expire`: import and reuse the shared state helper from
     `backend/studybuddy/_verification_dev.py` created by
     [Verification dev tools](2026-07-02-verification-dev-tools.md). The helper owns the renewal-clock
     backdating / exact-state behavior so SuperAdmin tools and the self-service profile panel do not
     drift. Wrap the admin action in `@transaction.atomic` like the other admin patch views.
  6. Log a `PlatformActivity` row (`activity_type='admin_action'`) for every dev-tool action, same as every
     other admin mutation in this file — dev tools shouldn't be invisible in the audit trail.
- `urls.py` — add `path('admin/users/<int:pk>/verification-dev-tools/',
  AdminUserVerificationDevToolsView.as_view())` next to the other `admin/users/` routes (~`urls.py:52-53`).
- Frontend: `src/stores/superadmin.js` — add `sendVerificationDevAction(userId, action)` calling
  `api.post(`/admin/users/${userId}/verification-dev-tools/`, { action })`, same shape as
  `updateUserStatus:77-79`.
- `SuperAdminUsers.vue` — add a dev-tools button group to the offcanvas (near `toggleSuspension` at
  line 173), visible only when `selectedUser.role` is `'Tutor'` or `'Tutee'`. **Scope decision:** buttons
  are shown unconditionally (not hidden behind a second "is this enabled" fetch) — adding a
  flag-visibility endpoint would be new attack-surface for no real gain, since the *server* gate is what
  matters per the outline ("gated server-side, not just UI-hidden"). A disabled-environment click just
  surfaces the 403 as a toast error via the existing `toastStore.push(..., 'error')` pattern
  (`toggleSuspension:247-249`). This is the one place the outline's phrasing is interpreted rather than
  quoted verbatim — flagging it in case the reviewer wants an explicit visibility gate instead.

## Risks

- Force-send-email and force-expire are real side-effecting admin actions (send actual email, alter a real
  user's verification state) — mitigated by the server-side flag check happening before any other logic in
  the view, defaulting to `False`.
- The reminder dedup race (Section 3) can double-send at most once per window; accepted, not fixed.
- `get_document_review_context`'s signature change (Section 3) has two call sites in the same file
  (`views.py:197`, `:212`) — both must be updated together or the module fails to import.

## Checks to run

- New backend tests (mirroring existing patterns in `backend/studybuddy/tests.py`):
  - `email_utils` functions: default `role_label='tutor'` produces byte-identical text to today;
    `role_label='tutee'` swaps wording; new `send_document_renewal_result_email` covers both
    approved/rejected branches.
  - `AdminTuteeApplicationDetailView.patch` and `AdminTutor/TuteeDocumentRenewalDetailView.patch`: assert
    the right email function is called (mock/patch) on approve and on reject.
  - Tutee first-submission and resubmission paths: assert `send_application_received_email` called with
    `role_label='tutee'`.
  - Reminder trigger: using `@override_settings` / backdated `reviewed_at` fixtures to land inside each
    window, assert the task is enqueued and the matching dedup field is stamped; assert calling
    `get_document_review_context` again in the same window does **not** re-enqueue (dedup field already
    set); assert no reminder fires outside `verified` status.
  - Dev-tools endpoint: 403 when `VERIFICATION_DEV_TOOLS_ENABLED` is unset/`False` even for an authenticated
    SuperAdmin; 403 for a non-SuperAdmin Admin even with the flag on; 400 for an invalid `action`; with the
    flag on via `@override_settings(VERIFICATION_DEV_TOOLS_ENABLED=True)`, each `send_*` action calls the
    right email function and `force_expire` flips `document_renewal_status()` to `'due'` and clears both
    dedup fields.
- `python manage.py makemigrations --check` clean after the `EmailSendLog.PURPOSE_CHOICES` change.
- Full backend suite (`python manage.py test`, backgrounded per the handoff's gotcha #5) — must match the
  existing 11-failure/error baseline, no new regressions.
- Browser-verify `SuperAdminUsers.vue`: with `VERIFICATION_DEV_TOOLS_ENABLED=True` locally, trigger each
  send action against a seeded dev account and confirm a success toast + a real console-backend email log
  line; trigger `force_expire` on a test tutor/tutee and confirm their own `/application-status` page shows
  `due` afterward.
- `/code-review` (8-angle finder + verify, same as every prior phase).

## Changelog

- 2026-07-01: Outline written alongside the overview and Phase 1 detail plan. Not started.
- 2026-07-02: Phase 3 shipped and committed (`cbc67e8`), unblocking this phase. Session ended before
  fleshing this phase out — linked a handoff doc
  (`docs/session-summaries/2026-07-02-tutee-verification-phase4-handoff.md`) capturing environment gotchas
  and full context for whoever picks this up next. Still Draft/outline; not started.
- 2026-07-02: Fleshed out into full detail against current `HEAD` (post-Phase-3) — every referenced
  file/line/function was read directly, not assumed. Locked one new scope decision not in the original
  outline: dev-tools buttons are always visible to SuperAdmins in the UI (no separate flag-visibility
  fetch), relying entirely on the server-side 403 gate — called out explicitly above for review. Still
  Draft; awaiting go-ahead to implement via TDD.
