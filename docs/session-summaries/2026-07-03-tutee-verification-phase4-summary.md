---
title: Tutee enrollment verification — Phase 4 (email & dev tools) — session summary
date: 2026-07-03
plan: ../plans/2026-07-01-tutee-verification-phase4-email-devtools.md
status: Done
---

# Tutee Enrollment Verification — Phase 4 — Summary

## What shipped

The final phase of the tutee enrollment verification effort (all 4 phases now Done), plus two small
fixes bundled in after an audit. Six sections, all implemented, tested, and browser-verified:

1. **Generalized verification emails.** `send_application_received_email`/`approved`/`rejected` now
   take a `role_label` kwarg (defaults to `'tutor'`, byte-identical for existing call sites). New
   `send_document_renewal_result_email` covers renewal approve/reject for both roles. Wired into
   every previously-silent path: tutee initial submission, tutee resubmission, and all four admin
   `.patch` views (tutor/tutee application decisions, tutor/tutee renewal decisions).
2. **Opportunistic renewal reminders.** `get_document_review_context` now sends a 7-day or 1-day
   reminder email (whichever window applies, 1-day checked first) from the existing read path
   (`profile_status`/login), dedup-gated by `reminder_7day_sent_at`/`reminder_1day_sent_at`. New
   `mailer.enqueue_document_renewal_reminder` + async task + email templates.
3. **SuperAdmin dev tools.** New `AdminUserVerificationDevToolsView` — force-send any status/reminder
   email, or force-expire a renewal — gated by `VERIFICATION_DEV_TOOLS_ENABLED` (403 before any query
   when off). `SuperAdminUserModal.vue` got a "Verification Dev Tools" button group in its Actions tab.
4. **Pending-status display fix** (bundled). `TutorApplicationStatus.vue`'s pending views now show
   the submitted School ID / Enrollment Proof links and motivation text — data the API already
   returned but the template was discarding.
5. **`TutorDetails.vue` verified badge fix** (bundled). The public tutor-browsing page's "Verified"
   badge was unconditional (always showing); now gated on a new `TutorDetailSerializer.is_verified`
   field (`application_status == 'approved' and document_renewal_status() == 'verified'`).

## How this started

The user reported "the institutional admin doesn't have a manage tutee request screen." Investigation
(via `/grill-with-docs`) found this was **not a missing feature** — Phase 3 had already shipped a
working admin queue for tutee applications; the empty table the user saw was just an empty dev
database (no tutee had submitted documents yet). Confirmed once the user submitted a real
application and it appeared correctly in the admin queue.

The user then asked for a broader audit of the whole verification flow (frontend vs. backend vs.
tests, plus notifications/emails), which surfaced the two real gaps bundled into this phase (items 4
and 5 above) alongside the already-drafted, already-fully-speced Phase 4 email/dev-tools scope.

## Deviations from the plan

- **A third `get_document_review_context` call site.** The plan's own risk section flagged "two call
  sites... both must be updated together" — there were actually three (`create_tutee_document_renewal_submission`
  was missed). Found and fixed during implementation, not left latent.
- **A real regression during full-suite verification.** A pre-existing test
  (`ApplicationVerificationSharedBaseTests.test_generalized_document_review_context_matches_tutor_shape`)
  called the function with the old 1-arg signature. Fixed by passing `role_label` at that call site.
- **Self-review findings applied before finalizing:** moved a per-branch local `from . import mailer`
  in the dev-tools view to a module-level import; added a 400 guard on the `send_rejected` dev action
  when the application has no `rejection_reason` set (previously would have silently emailed an empty
  reason), with a new regression test.

## Checks run

- **Backend:** 32 new tests across 6 test classes, all green (TDD throughout). Full suite: 238 tests,
  14 failures + 3 errors — one error was the regression above (fixed); the remaining 13 failures + 2
  errors were verified pre-existing and unrelated by isolating and re-running each individually
  (recommendation-matching ID-set mismatches, a `PaymentMethod` unique-constraint fixture collision, a
  301-vs-200 dashboard-stats redirect, avatar-upload 400s) — none touch a file this phase changed, and
  each reproduces identically in complete isolation from this diff.
- `python manage.py makemigrations --check --dry-run`: clean (one migration generated,
  `0066_alter_emailsendlog_purpose`, state-only per the plan's own expectation).
- **Frontend:** `npm run lint` clean in touched files (the 18-error baseline is entirely a stale copy
  of `TutorDetails.vue` inside an unrelated `.claude/worktrees/perf-debug/` checkout). `npm run build`
  clean. `npx vitest run`: 54/54 passing.
- **Browser verification** (real accounts created and cleaned up afterward): submitted a real tutee
  application via the actual API (exercising the email wiring live); confirmed the pending-status page
  renders document links + motivation text; confirmed the `TutorDetails.vue` badge shows for an
  approved+verified tutor and disappears when flipped to pending; confirmed the SuperAdmin dev-tools
  buttons render and correctly 403 with the flag off. Renewal reminders (time-window-gated,
  opportunistic) verified via unit tests rather than a live 90-day wait, consistent with how prior
  phases verified similar time-gated logic.

## Not done / follow-ups

- Nothing deferred within this phase's scope — all 6 sections shipped.
- Not pushed or committed as part of this session (per project convention: confirm before commit/push).
