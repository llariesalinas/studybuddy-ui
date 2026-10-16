---
title: Desktop UI and trust fixes
date: 2026-10-16
status: Done
spec: ../../.impeccable/critique/2026-10-15T23-17-56Z__src.md
---

# Desktop UI and trust fixes

## Intent

Implement approved critique priorities 1–4 and refine desktop presentation across student, tutor
and admin screens. Users should see truthful tutor information, consistent booking consequences,
accessible core controls, and explicit recurring-schedule deletion scope. Preserve StudyBuddy's
identity, existing layouts, useful information density and all unrelated work. Mobile changes,
backend policy changes, deployment and external sends are out of scope.

The user approved the implementation plan with “do it” on 2026-10-16.

## Goal

Correct misleading data and interaction barriers, protect recurring availability deletion, and
deliver coherent desktop hierarchy, form states, spacing and action emphasis with evidence.

## Approach

Use the existing design system and approved mockups. Implement directly without delegation.
Fix factual and interaction defects first, then make focused desktop refinements at the narrowest
shared layer. Use targeted regression tests for meaningful behaviors and bounded browser review.

## Steps

1. Remove fabricated tutor data and unsupported landing claims.
2. Show the configured 12-hour cancellation cutoff and selected booking deadline before confirming.
3. Associate core form labels, add autocomplete and keyboard session links, improve relevant dialog focus.
4. Explain weekly versus date-specific scheduling and confirm recurring deletions.
5. Refine desktop heading/spacing/action hierarchy, form states, wallet balance and routine statuses
   across student/tutor/admin surfaces without changing their layouts or mobile rules.
6. Run targeted and baseline tests, lint and production build; inspect representative desktop screens.
7. Record results, regenerate the plan dashboard and commit focused changes.

## Risks

- Live API access may be unavailable. Use an isolated local visual-review fixture if needed; label
  fixture evidence honestly and never mutate shared demo data or trigger mail.
- The repository has previously recorded frontend failures; run a baseline to distinguish new ones.
- Existing plan-index edits are unrelated and must be preserved and staged separately.
- Do not invent payment policies or change cancellation enforcement.

## Checks to run

- Regression tests for zero/missing tutor data, booking deadline text, accessible core controls,
  keyboard session navigation and confirmation-before-delete.
- Full frontend test suite; compare failures to the pre-change baseline.
- npm run lint and npm run build, inspecting any auto-fix changes for scope.
- Desktop browser review of public, tutee, tutor and admin surfaces, plus keyboard interaction.
- One batched correction and confirmation round at most; no mobile refinement.

## Outcome

Completed critique issues 1–4 and desktop refinement. Tutor profiles preserve real zero values
and missing data, landing claims match supported behavior, and booking consequences use the
shared Manila-time 12-hour cancellation calculation. Core forms have associated labels/autofill,
sessions have native detail links, and relevant dialogs contain and restore keyboard focus.
Recurring slot deletion now explains its weekly scope and requires confirmation; failures and
partially completed batches remain retryable.

Desktop shared typography, forms, filters, tables and controls were refined within existing
layouts. Wallet balance is emphasized, routine unrated sessions use neutral styling, and
redundant headings were removed. No mobile-specific rules or backend behavior were changed.

Verification: 15 new regression tests pass; a focused seven-file run passes 48 tests. Full frontend
suite: 264 pass, one skip, exactly the nine baseline failures. Lint and production build pass.
Browser inspection used actual public pages and isolated local-data fixtures for authenticated
booking, scheduling, wallet, sessions, student dashboard, admin dashboard and support queue.
No shared accounts/data, payments or emails were used. Temporary preview files and server removed.

See [completion summary](../session-summaries/2026-10-16-desktop-ui-and-trust-fixes-summary.md)
for detailed evidence and limits. No new critique score is claimed.
