---
title: Tutee enrollment verification — Phase 2 (booking gate & forward-only)
date: 2026-07-01
status: Draft
spec: 2026-07-01-tutee-verification-overview.md
---

# Phase 2 — Booking gate & forward-only enforcement

> Part of [Tutee enrollment verification — overview](2026-07-01-tutee-verification-overview.md). Outline
> only — flesh out once Phase 1 is Done and its abstract-base shape is confirmed stable (may reshape this).

<!-- LIVING SUMMARY: keep this section and the Changelog current on every edit -->
## Status & Progress Summary

**Status: Draft — outline only, not started.** Depends on Phase 1.

## Goal

Enforce document verification at the point of new work (booking creation for tutees, accepting a booking
request for tutors) instead of a global lockout, for both roles, with an existing-tutee grace period.

## Approach (outline)

- Loosen `src/router/index.js` (`needsTutorApplicationAttention`, ~line 296-302): today it globally
  redirects any renewal-due tutor to `/application-status`. Change to forward-only — only redirect away
  from booking/accept-request surfaces, not the whole app.
- Mirror the same guard shape for tutees, driven by the Phase 1 generalized helper.
- Server-side enforcement (source of truth, route guard is UX only): a shared `can_book`-style check at
  `POST bookings/confirm/` (tutee booking creation) and the tutor accept-booking-request endpoint.
- New (never-approved) `pending` tutors stay hard-blocked at login, unchanged. New tutees register free,
  gated only at first booking.
- Existing tutees: one-time global 30-day grace period before enforcement kicks in — new setting
  (`TUTEE_VERIFICATION_GRACE_PERIOD_DAYS = 30`). Open decision to make in this phase: cutover date as a
  settings constant vs. a DB field.
- In-flight bookings when someone lapses: untouched (lapse blocks only new work).

## Risks

- This *loosens* current tutor behavior — a real behavior change for existing users, not just an addition.
  Needs explicit regression tests against current tutor-lockout tests before shipping.
- Two enforcement points (guard + server) must stay in sync; keep the server check as the single source of
  truth and have the guard call the same logic/shape.

## Checks to run

- TBD when this phase is detailed — at minimum: existing tutor lockout tests updated to assert
  forward-only behavior; new tests for tutee booking-gate; grace-period cutover tested with a frozen clock.

## Changelog

- 2026-07-01: Outline written alongside the overview and Phase 1 detail plan. Not started.
