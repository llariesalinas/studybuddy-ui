---
title: Notifications timeout fix
date: 2026-06-07
status: Done
spec:
---

# Notifications timeout fix

## Status & Progress Summary

**Status:** Done — all 4 tasks shipped and committed.

**Progress:** 4 of 4 tasks complete.

---

## Goal

Eliminate the 30s Axios timeout error on `GET /notifications/` caused by concurrent request pile-up on the frontend and a slow unindexed query on the backend.

## Approach

Two-pronged fix:
- **Frontend**: add a concurrent-request guard to the Pinia store so only one in-flight request runs at a time; make the `setInterval` in `NotificationBell.vue` skip ticks when the tab is hidden and back off exponentially after errors.
- **Backend**: add a composite DB index on `(recipient, created_at DESC)` to eliminate the filesort, and add `select_related('recipient')` to the queryset as a defensive N+1 prevention.

## Steps

1. Add `if (loading.value) return false` guard to `fetchNotifications` in `src/stores/notifications.js`; return `true`/`false` for success signalling.
2. Add `errorTicksRemaining` and `consecutiveErrors` tracking vars to `NotificationBell.vue`; replace the `setInterval` callback with a smart version that skips hidden-tab ticks and backs off 1→2→4→8 ticks on consecutive errors.
3. Add `models.Index(fields=['recipient', '-created_at'], name='notif_recipient_date_idx')` to `Notification.Meta` in `backend/studybuddy/models.py`; generate and apply migration `0051`.
4. Add `.select_related('recipient')` to the queryset in `list_notifications` in `backend/studybuddy/views.py`.

## Risks

- Backoff resets to zero on any success — if errors are intermittent rather than sustained the backoff won't accumulate much, but this is the desired behavior.
- `select_related('recipient')` fetches the UserProfile row even if the serializer doesn't use it; the join cost is negligible but worth revisiting if the payload is later trimmed.

## Checks to run

- Open app in Chrome DevTools → Network tab, filter to `notifications/`, click the bell rapidly — only one pending request should appear at a time.
- Response time should drop to sub-100ms on a local DB after the index is applied.
- Restart Django dev server after migration to confirm `0051` applied cleanly.

---

## Changelog

- **2026-06-07** — Plan created and executed in full. All 4 tasks committed on `feature-darkmode-toggle`.
