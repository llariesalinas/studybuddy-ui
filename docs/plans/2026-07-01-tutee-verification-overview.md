---
title: Tutee enrollment verification — overview
date: 2026-07-01
status: Approved
spec: ../session-summaries/2026-07-01-tutee-verification-handoff.md
---

# Tutee enrollment verification — overview

> Handoff: see [`docs/session-summaries/2026-07-01-tutee-verification-handoff.md`](../session-summaries/2026-07-01-tutee-verification-handoff.md)
> for the full grilled design (17 decisions, all locked) this plan set was written from. This overview
> and its 4 phase files are the durable record going forward; the handoff doc can be treated as
> historical once all 4 phases are Done.

<!-- LIVING SUMMARY: keep this section and the Changelog current on every edit -->
## Status & Progress Summary

**Status: Approved — design locked, phase files written. Phase 1 is next.**

- [ ] Phase 1 — Model & backend foundation ([plan](2026-07-01-tutee-verification-phase1-model.md))
- [ ] Phase 2 — Booking gate & forward-only enforcement ([plan](2026-07-01-tutee-verification-phase2-gate.md))
- [ ] Phase 3 — UI surfaces ([plan](2026-07-01-tutee-verification-phase3-ui.md))
- [ ] Phase 4 — Email & dev tools ([plan](2026-07-01-tutee-verification-phase4-email-devtools.md))

Execute one phase at a time; do not start the next phase without explicit go-ahead, per this project's
"one plan file per phase" convention. Each phase is independently testable and leaves the app working.

## Goal

Extend the existing tutor document-verification/renewal system to tutees, so both roles prove enrollment
(school ID + proof of enrollment) and re-verify on a 90-day cycle, gated at booking time rather than
globally — without duplicating the tutor logic.

## Approach

Framing throughout: **"tutees and tutors are both students"** — maximize shared code, mirror the tutor
flow, apply rules symmetrically. Concretely:

- A shared **abstract Django base model** carries the document fields, status, and renewal-cadence logic
  (`document_renewal_status()`, `can_submit_document_renewal()`, `latest_approved_document_review_at()`).
  `TutorApplication` is refactored onto it; a new `TuteeApplication` inherits the same base. Separate
  tables, one source of logic — chosen over renaming `TutorApplication` into a shared concrete model (too
  risky against the freshly-shipped renewal-review commit `66c1441`) and over full duplication (drift risk,
  the exact bug class just fixed with `MAX_UPLOAD_SIZE`).
- Enforcement is **forward-only** for both roles: a lapsed/unverified user keeps existing bookings, wallet,
  and dashboard access. Only *new* booking creation (tutee) / accepting new booking requests (tutor) is
  blocked. This *loosens* today's tutor behavior (currently a full-app lockout via the router guard).
- Enforced in two places (defense in depth, one shared source-of-truth check): the frontend route guard
  (redirect to `/application-status` only from booking/accept surfaces) and a server-side check at the
  booking-create and tutor accept-request endpoints.
- New tutees register free and are gated at first booking (not at signup) — consistent with the
  booking-time gate.
- 90-day renewal cadence, anchored to `latest_approved_document_review_at()`. Existing tutees get a
  one-time, global 30-day grace period before enforcement kicks in.
- UI: generalize `/application-status`, add a verification/renewal card to both profile views, generalize
  the admin queue with a role tab and a read-only renewal-status column/filter for regular admins.
- Email: generalize the existing received/approved/rejected emails to take role/label; add opportunistic
  (no-scheduler) 7-day/1-day renewal reminders piggybacked on the existing profile-status read path.
- Dev-only SuperAdmin tooling (backend-gated, not just UI-hidden): force-send any status email, force-expire
  a user's verification — the mechanism for demoing lapse/reminders since the real windows are 90/30 days.

## Risks

- The abstract-base refactor of `TutorApplication` is the riskiest step — must be verified schema-neutral
  (Phase 1's own risk section covers this in detail).
- Loosening the tutor lockout to forward-only is a **behavior change for existing tutors**, not just an
  addition — must be validated against current tutor tests before Phase 2 ships.
- Reminder emails are opportunistic (no scheduler) — a user who never logs in during their reminder window
  won't be reminded until they return. Accepted tradeoff (they're not booking anyway under forward-only).

## Checks to run

- Each phase's own `Checks to run` section (see phase files).
- End to end, once all 4 phases ship: a tutee can register, get gated at first booking, submit documents,
  get approved by an admin, and see a renewal countdown; the same for a tutor including the loosened
  forward-only lockout; dev-only force-expire and force-send-email work for a SuperAdmin and are rejected
  server-side for a regular admin.

## Changelog

- 2026-07-01: Overview and all 4 phase plan files written from the locked design in the handoff doc.
  Status set to Approved (design already signed off via grilling; nothing left to decide at this level).
