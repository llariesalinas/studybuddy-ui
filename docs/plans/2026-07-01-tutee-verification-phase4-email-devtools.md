---
title: Tutee enrollment verification — Phase 4 (email & dev tools)
date: 2026-07-01
status: Draft
spec: 2026-07-01-tutee-verification-overview.md
---

# Phase 4 — Email & dev tools

> Part of [Tutee enrollment verification — overview](2026-07-01-tutee-verification-overview.md). Outline
> only — flesh out once Phase 3 lands.

<!-- LIVING SUMMARY: keep this section and the Changelog current on every edit -->
## Status & Progress Summary

**Status: Draft — outline only, not started.** Depends on Phase 3.

## Goal

Notify users of verification events and renewal deadlines for both roles, and give SuperAdmins a way to
demo lapse/reminders without waiting out the real 90-day/30-day windows.

## Approach (outline)

- Generalize `send_application_*_email` functions (`email_utils.py`) to take the application object +
  role/label. This also fixes a real gap found in `66c1441`: `AdminTutorDocumentRenewalDetailView.patch`
  (`admin_views.py:531`) currently sends **no email** on renewal approve/reject.
- Event-driven emails: received, approved, rejected (3 states), for both roles.
- Reminders: 7-day + 1-day before renewal due, via **opportunistic check, no scheduler** — piggyback on the
  profile-status read path that already computes `document_renewal_status()` (the Phase 1 generalized
  helper): when status is read and the user is inside a reminder window and the matching Phase 1 dedup
  field (`reminder_7day_sent_at` / `reminder_1day_sent_at`) is null, enqueue via the existing `async_task`
  path (`mailer.py`) and stamp the field. Accepted tradeoff: a user who never logs in during their window
  isn't reminded until they return.
- Dev-only SuperAdmin tooling on the per-user detail offcanvas in `SuperAdminUsers.vue` (`selectedUser`,
  `openDetail`, precedent action `toggleSuspension` at line 173): buttons to send each email (received/
  approved/rejected/7-day/1-day) to that user, and force-expire that user's verification. Gated **server-
  side**, not just UI-hidden (e.g. `DEBUG`-derived or a dedicated flag mirrored to backend) — the endpoint
  itself must reject when the flag is off, since it sends real, possibly-false status emails to real users.

## Risks

- Force-send-email and force-expire are real side-effecting admin actions (send actual email, alter a
  real user's verification state) — must be unreachable in production even if someone guesses the URL.

## Checks to run

- TBD when detailed — at minimum: email generalization tested for both roles; opportunistic reminder tested
  with a frozen clock and dedup-field assertions (no double-send); dev-tools endpoint tested to 403 when
  the gate flag is off, even for a SuperAdmin-authenticated request.

## Changelog

- 2026-07-01: Outline written alongside the overview and Phase 1 detail plan. Not started.
