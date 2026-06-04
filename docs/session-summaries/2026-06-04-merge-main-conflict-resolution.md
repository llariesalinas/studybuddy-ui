# Merge `main` into `feature-darkmode-toggle` — conflict resolution

**Date:** 2026-06-04
**Branch:** `feature-darkmode-toggle`
**Status:** Completed, pushed

## Summary

Merged the latest `origin/main` (admin side PR #83, dark mode PR #82) into the
feature branch and resolved 28 conflicts across 22 files. The merge was initially
pushed with leftover conflict markers (frontend build passed, so broken backend
Python slipped through); a follow-up pass found and fixed every remaining marker,
recovered admin content that was wrongly dropped, and reconciled the migration
history on the dev database.

## Conflict resolution strategy

- **Chat backend** (`chat/models.py`, `serializers.py`, `services.py`, `views.py`) —
  kept our performance work (cursor pagination, `get_current_booking_contexts`
  batching, `unread_map` / `current_booking_map`, `skip_partner_context`, the
  `_CURRENT_BOOKING_UNSET` memoization, null-safe sender fallback) **and** merged in
  admin's `room_type` field, `ticket_status`, and nullable `Message.sender`.
- **`App.vue`** — kept our logout modal + aurora CSS; added admin's `SupportModal`
  integration, sidebar Help button, and Support Desk header copy.
- **`Chat.vue`** — kept our infinite scroll + loading states; added admin's support
  room context panel, resolved-ticket banner, and system-message styling.
- **`TuteeSessionDetailsFlow.vue`** — kept our cancellation guards; added admin's
  `SupportModal` state.
- **`vite.config.js` / `settings.py`** — kept our esbuild console-drop, `allowedHosts`,
  and `env_bool` email config.

## Content wrongly dropped by `--ours`, then recovered

Taking our side wholesale on `views.py` and `AdminDashboard.vue` silently discarded
admin PR #83 additions that the auto-merged `urls.py` still referenced, which crashed
`manage.py` with `AttributeError: module 'studybuddy.views' has no attribute
'admin_list_tickets'`.

- Re-added 5 support-ticket endpoints to `studybuddy/views.py`:
  `create_support_ticket`, `admin_claim_ticket`, `list_my_tickets`,
  `admin_list_tickets`, `admin_resolve_ticket`, plus the `IntegrityError` import.
- Re-added the "Support Desk" quick-action card to `AdminDashboard.vue`.
- Verified `chat.js` and `TutorWallet.vue` (also `--ours`) dropped nothing — main's
  differences there were superseded styling.

## Migration renumbering & dev-DB reconciliation

Our `0046_booking_cancellation_reason_and_more` and `0047_emailotpchallenge` collided
with admin PR #83's `0046_supportticket_chatroom_room_type_and_more` and
`0047_alter_message_sender_and_more`. Ours were renamed **`0046/0047 → 0048/0049`**
with their dependency chains rewired onto admin's `0047`.

The dev database already physically had the `cancellation_reason` / `cancelled_by_role`
columns and the `EmailOTPChallenge` table (from the pre-rename migrations), so applying
`0048/0049` failed with `DuplicateColumn`. Reconciled by:

- `python manage.py migrate studybuddy 0049 --fake` (schema already present)
- Deleting the two orphan `django_migrations` records under the old `0046/0047` names.

> **Reviewer / teammate note:** If you pull this branch onto an existing dev DB that
> already ran the old `0046/0047`, fake-apply the renamed migrations:
> `python manage.py migrate studybuddy 0049 --fake`. A clean DB applies all of
> `0046`–`0049` normally.

## Verification

- `npm run build` — passed.
- `python manage.py check` — no issues.
- `python manage.py migrate --check` / `showmigrations studybuddy` — `0046`–`0049`
  all applied, history clean.
- No conflict markers remain in tracked source (`<<<<<<<` / `>>>>>>>` swept from
  `*.py`, `*.vue`, `*.js`, excluding `venv/`).
