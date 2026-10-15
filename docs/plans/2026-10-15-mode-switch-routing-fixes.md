---
title: Mode-switch routing fixes
date: 2026-10-15
status: Done
spec: 2026-08-19-dual-role-mode-switch.md
---

# Mode-switch routing fixes

## Status & Progress Summary

Implemented and tested locally on 2026-10-16. Imported from pr139-review-plans.patch and refined
before implementation. Changes are uncommitted and ready for review.

## Goal

Resolve the confirmed PR #139 review findings for mode-switch routing fixes.

## Approach

Apply the reviewed fixes with regression coverage and preserve established behavior outside the
reported problems. Record implementation refinements and known limitations below.

## Completed steps

1. Replaced the router's capability-based onboarding gate with durable setup completion.
   `UserProfile.tutor_setup_completed_at` is backfilled for established tutors in migration 0087.
   Submitted verification plus configured tutor setup records completion; carried verification
   alone does not. Completion survives subject removal. Explicit verification skip retains its
   existing behavior. Pending applications keep their existing application-status flow; this
   change does not introduce a new approval gate.
2. Auto-switch now reloads the profile and redirects through the guard again, so onboarding
   and commission terms run against the destination mode.
3. Undo restores a compatible home route and expires on subsequent navigation.
4. Remote role refresh reloads the profile before incrementing a revision watched by App.vue.
   The watcher moves incompatible routes to the new mode's home without automatically switching
   back. Shared routes stay open.
5. After a detected remote change, automatic mode switches ask for confirmation. Cancellation
   retains the current mode. A successful local switch clears that flag.
6. Router and auth regression tests cover completion with no subjects, carried verification,
   automatic gates, Undo, remote profile reload ordering, shared routes and confirmation.

## Risks

- Active mode remains account-wide. Until token refresh detects a remote switch, server requests
  can still encounter the other device's mode. Per-device mode is deferred.
- Historical completion is inferred from an existing tutor rate and submitted application (or
  explicit skip); no previous dedicated completion marker existed.
- Includes migration 0087; migrate the development database before manual checks.

## Verification

- npm run lint and npm run build pass.
- Focused frontend regression files: 29/29 pass.
- Focused backend classes plus migration regression: 95/95 pass on isolated local PostgreSQL.
- Full frontend: 249 pass, 1 skip, 9 existing failures. Original commit: 232 pass, 1 skip,
  the same 9 failures.
- Full backend: 555 pass, 1 existing chat grace-cutoff failure. Original commit: 540 pass,
  the same failure. No new failures.
- makemigrations --check --dry-run reports no changes.
- Manual two-browser review is left for the user; no production or remote database changes.

See [completion and manual checks](../session-summaries/2026-10-16-pr139-review-fixes.md).
