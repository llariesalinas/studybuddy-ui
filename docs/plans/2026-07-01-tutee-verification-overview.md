---
title: Tutee enrollment verification — overview
date: 2026-07-01
status: Done
spec: ../session-summaries/2026-07-01-tutee-verification-handoff.md
---

# Tutee enrollment verification — overview

> Handoff: see [`docs/session-summaries/2026-07-01-tutee-verification-handoff.md`](../session-summaries/2026-07-01-tutee-verification-handoff.md)
> for the full grilled design (17 decisions, all locked) this plan set was written from. This overview
> and its 4 phase files are the durable record going forward; the handoff doc can be treated as
> historical once all 4 phases are Done.

<!-- LIVING SUMMARY: keep this section and the Changelog current on every edit -->
## Status & Progress Summary

**Status: Done — all 4 phases implemented, tested, and verified. Phase 4 (scope expanded via grilling on
2026-07-03 to also cover two small display/badge fixes found during that session) shipped 2026-07-03.**

- [x] Phase 1 — Model & backend foundation ([plan](2026-07-01-tutee-verification-phase1-model.md))
- [x] Phase 2 — Booking gate & forward-only enforcement ([plan](2026-07-01-tutee-verification-phase2-gate.md))
- [x] Phase 3 — UI surfaces ([plan](2026-07-01-tutee-verification-phase3-ui.md))
- [x] Phase 4 — Email & dev tools ([plan](2026-07-01-tutee-verification-phase4-email-devtools.md))

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
- 2026-07-01: Phase 1 implemented and verified (abstract base models, `TuteeApplication`/
  `TuteeDocumentRenewalReview`, schema-neutral migration, generalized helper, full backend suite run with
  only pre-existing/unrelated failures). Status moved to In Progress; Phase 2 awaits explicit go-ahead.
- 2026-07-02: Phase 2 implemented and verified (server-side `can_create_new_booking` gate wired into both
  booking-creation and accept-request endpoints, tutor router lockout narrowed to forward-only, grace-period
  cutover as an env-driven settings constant). Tutee-side route guard deliberately deferred to Phase 3 (see
  Phase 2's own changelog for why). Browser-verified the loosening end to end. Phase 3 awaits explicit
  go-ahead.
- 2026-07-02: Phase 3 implemented, tested, and browser-verified end to end (generalized `/application-status`
  for both roles, renewal cards on both profile views via a new shared `VerificationStatusCard.vue`, tutee
  admin review queue with a role tab, the tutee-side route guard gap Phase 2 deferred is now closed). Found
  and fixed a real gap during verification: tutees have no application at signup (unlike tutors), so the
  status page needed a genuine initial-submission path, not just resubmission — `tutee_application_resubmit`
  now creates on first submit. User pre-approved proceeding directly to Phase 4 next.
- 2026-07-03: A `/grill-with-docs` session (starting from an "admin has no manage-tutee-request screen"
  report that turned out to be Phase 3 working as designed against an empty dev DB) audited the full
  verification flow's frontend/backend/email coverage and found two small real gaps beyond Phase 4's
  original scope: the pending-status page doesn't render document/motivation data it already fetches, and
  `TutorDetails.vue`'s public "Verified" badge is unconditional. Both bundled into the Phase 4 plan file
  (see its own Changelog for the locked design decisions) rather than split into new phase files. Phase 4
  moved from Draft to Approved; still not implemented.
- 2026-07-03: Phase 4 implemented, tested, and browser-verified (see its own Changelog for full detail):
  generalized emails wired into every previously-silent tutor/tutee application and renewal decision path,
  opportunistic 7-day/1-day renewal reminders, SuperAdmin dev tools, plus the two bundled fixes (pending-
  status document display, binary `TutorDetails.vue` verified badge). 32 new backend tests green; one real
  regression found and fixed during full-suite verification (a pre-existing test using the old
  `get_document_review_context` signature); all other full-suite failures verified pre-existing and
  unrelated via isolated re-runs. All 4 phases of this plan are now Done.
