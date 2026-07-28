---
title: Plan-vs-code implementation audit — session summary
date: 2026-07-17
plan: n/a (ad hoc audit, not a feature plan)
status: Done
---

# Summary

Audited every plan in `docs/plans/` with a non-"Done" frontmatter status (7 In Progress, 10
Approved — the 53 already marked "Done" were treated as pre-verified) against the actual
codebase, to find plans whose status had gone stale. Originally scoped as a handoff brief for
Antigravity (`docs/plans/2026-07-17-antigravity-plan-implementation-audit.md`, still on disk but
unused), then done directly instead via two background forks plus manual verification of every
claimed finding before editing anything.

## What was found

Of the 17 audited plans:

**3 corrected: "In Progress" → "Done"** (the plan body already said Done, the frontmatter was
never updated):
- `2026-06-21-admin-dashboard-redesign.md`
- `2026-06-21-tutor-profile-realtime-image-compression.md`

**1 left "In Progress" correctly** — `2026-06-14-ongoing-booking-live-status.md`: code-complete
but a manual live-flow smoke test is explicitly still unchecked. (The first audit pass
mis-classified this one as done; caught on manual re-check before editing.)

**1 left "In Progress" correctly** — `2026-07-12-admin-role-consolidation.md`: session summary
confirms only 1 of 8 tickets shipped (Admin role dropped from `ROLE_CHOICES`); the rest were
handed to Codex and haven't landed.

**3 left "In Progress" as genuinely ongoing** (real partial work, no evidence of staleness):
`2026-07-15-instant-booking.md`, `2026-07-05-demo-deployment-plan.md`,
`2026-07-08-algorithm-demo-live-rating-edit.md`.

**7 corrected: "Approved" → "Done"** (implemented, but the frontmatter said Approved — several
plan bodies even explicitly said "not yet implemented" or "no code written yet," contradicting
their own later completion):
- `2026-07-02-verification-dev-tools.md`
- `2026-07-07-face-to-face-campus-location-modal.md`
- `2026-07-06-proactive-verification-ui-gates.md`
- `2026-06-15-chat-banner-card-redesign.md`
- `2026-06-15-tutor-details-slot-clarity.md`
- `2026-06-08-superadmin-institution-hierarchy.md`
- `2026-06-06-frontend-chat-caching.md`

**2 left "Approved" — genuinely partial/unresolved, not corrected:**
- `2026-06-17-superadmin-redesign.md` — plan's own task tracker has all 7 tasks unchecked; some
  overlapping code exists (`InstitutionRequestView`) but the plan's specific `AdminAccountRequest`
  model was never added. Needs a human decision on scope, not a status flip.
- `2026-07-08-tutor-verification-relocation.md` — overlaps the later Done plan
  `2026-07-13-tutor-onboarding-verification-redesign.md`, which may have covered the same ground
  differently. Needs a human to reconcile which plan actually shipped the behavior before either
  is re-labeled.

**1 left "Approved" — confirmed not started (label was already accurate):**
- `2026-07-01-tutor-application-bugfix-tests.md`

## Process note

The first audit pass (background fork) had one false positive — it called
`2026-06-14-ongoing-booking-live-status.md` done based on "all build tasks checked" without
noticing the plan's own unchecked manual-QA line. Caught by reading the plan file directly before
editing rather than trusting the fork's summary outright. Every status flip in this session was
verified against either (a) the plan's own body text explicitly saying "Implemented"/"Done", or
(b) direct `grep`/`Read` confirmation of the described file/endpoint/field in the current
codebase — not from fork output alone.

## Checks run

None (read-only investigation; the only writes were to plan frontmatter/changelogs and
regenerating `docs/plans/index.html` via `docs/plans/build-plans-index.ps1`).
