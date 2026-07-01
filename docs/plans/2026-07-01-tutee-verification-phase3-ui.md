---
title: Tutee enrollment verification — Phase 3 (UI surfaces)
date: 2026-07-01
status: Draft
spec: 2026-07-01-tutee-verification-overview.md
---

# Phase 3 — UI surfaces

> Part of [Tutee enrollment verification — overview](2026-07-01-tutee-verification-overview.md). Outline
> only — flesh out once Phase 2 lands.

<!-- LIVING SUMMARY: keep this section and the Changelog current on every edit -->
## Status & Progress Summary

**Status: Draft — outline only, not started.** Depends on Phase 2.

## Goal

Give tutees the same submit/resubmit and status-visibility surfaces tutors have, and give admins a unified
view across both roles.

## Approach (outline)

- Generalize `/application-status` (`TutorApplicationStatus.vue`) to serve both roles for submit/resubmit,
  entered via CTA / booking-block (no more global lockout after Phase 2's loosening).
- Add a verification/renewal card to **both** `TuteeProfile.vue` and `TutorProfile.vue`: "Renewed ✓" +
  countdown to next renewal. Use `.sb-card` / `.sb-badge` local patterns + `--sb-*` CSS custom properties
  per `.claude/skills/shadcn-components.md` and `App.vue` — no hardcoded colors.
- Generalize the admin queue (`AdminTutorApplications.vue`) with a tutor/tutee role tab. This phase writes
  `TuteeApplicationSerializer` / `TuteeDocumentRenewalReviewSerializer` (mirroring the tutor ones
  field-for-field against the `TuteeApplication`/`TuteeDocumentRenewalReview` models from Phase 1 —
  deliberately deferred here so they land alongside the views/tests that use them, not unreferenced) and
  new admin list/detail views mirroring `AdminTutorApplicationListView` / `AdminTutorApplicationDetailView`.
- Admin renewal-status visibility (read-only for regular admins): renewal status column + filter
  (`verified`/`due`/`pending`/`rejected`/`lapsed`) across ALL users of both roles with due date — not just
  rows with a pending submission. Regular admins act only through the existing review-a-submission flow;
  no manual "mark verified"/force-expire (those are dev-only SuperAdmin, Phase 4).
- This phase is also where dedup-field resets on renewal approval get wired in (the approval endpoints
  this phase generalizes are where "reset `reminder_*_sent_at` on approval" naturally lives).

## Risks

- Admin queue generalization touches a component with real production usage (tutor reviews happen daily)
  — needs careful regression testing of the existing tutor flow while adding the tutee tab.

## Checks to run

- TBD when detailed — at minimum: existing admin tutor-review flow unaffected; new tutee review flow
  tested end to end; renewal countdown card tested for both roles.

## Changelog

- 2026-07-01: Outline written alongside the overview and Phase 1 detail plan. Not started.
- 2026-07-01: Phase 1 cut its step 10 (Tutee serializers) as premature/unwired; this phase now explicitly
  owns writing `TuteeApplicationSerializer` / `TuteeDocumentRenewalReviewSerializer` itself.
