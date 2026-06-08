---
title: Notifications timeout fix — session summary
date: 2026-06-07
plan: ../plans/2026-06-07-notifications-timeout-fix.md
---

# Notifications timeout fix — session summary

## What shipped

All 4 planned tasks completed as specified. No deviations from the plan.

### Frontend (`feature-darkmode-toggle` branch)

**`src/stores/notifications.js`**
- Added `if (loading.value) return false` at the top of `fetchNotifications` — skips the API call entirely if a request is already in flight.
- `fetchNotifications` now returns `true` on success, `false` on error, enabling the component to signal backoff.

**`src/components/NotificationBell.vue`**
- Added `errorTicksRemaining` and `consecutiveErrors` module-level vars.
- `setInterval` callback now skips when `document.hidden` is true (tab not visible).
- On error, backs off exponentially: skips 1 tick → 2 → 4 → 8 (cap), equating to ~30s → 45s → 75s → 135s between attempts. Resets on next success.
- Existing `handleVisibilityChange` re-fetch on tab return left intact.

### Backend

**`backend/studybuddy/models.py` + migration `0051`**
- Added composite index `notif_recipient_date_idx` on `(recipient, -created_at)` to `Notification.Meta`.
- Migration generated (`0051_add_notification_recipient_date_index`) and applied successfully.

**`backend/studybuddy/views.py`**
- Added `.select_related('recipient')` to the `list_notifications` queryset.

## Commits

1. `fix(notifications): skip concurrent fetch if request already in flight`
2. `fix(notifications): skip polling when tab hidden; add exponential backoff on errors`
3. `perf(notifications): add composite index on (recipient, created_at)`
4. `perf(notifications): add select_related to list_notifications queryset`

## Checks run

- Migration applied cleanly: `Applying studybuddy.0051_add_notification_recipient_date_index... OK`
- Build output confirmed unchanged (all chunks same sizes as before).

## Notes

- The concurrent-request guard and hidden-tab skip eliminate the request pile-up immediately. The DB index removes the root cause (slow query). Together these should bring `notifications/` well under the 30s timeout even under load.
- `select_related('recipient')` is defensive — the serializer may not currently access recipient fields, but prevents N+1 if that changes.
