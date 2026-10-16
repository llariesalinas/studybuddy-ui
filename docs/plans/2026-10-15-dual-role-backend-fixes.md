---
title: Dual-role backend fixes
date: 2026-10-15
status: Done
spec: 2026-08-19-dual-role-mode-switch.md
---

# Dual-role backend fixes

## Status & Progress Summary

Implemented and tested locally on 2026-10-16. Imported from pr139-review-plans.patch and refined
before implementation. Changes are uncommitted and ready for review.

## Goal

Resolve the confirmed PR #139 review findings for dual-role backend fixes.

## Approach

Apply the reviewed fixes with regression coverage and preserve established behavior outside the
reported problems. Record implementation refinements and known limitations below.

## Completed steps

1. Carry-over selects the latest approved renewal with a review timestamp and copies its
   documents, reviewer and approval date. Original application documents remain the fallback.
   A newer pending renewal does not override approved documents. Both switch directions are tested.
2. Both ranked dashboard recommendations and the no-preferences fallback exclude the requester.
3. Dashboard cache keys have a new namespace independent of the mutable cached version, so
   deployment invalidates old lists even if the cache already holds a version counter.
4. Regression tests cover both carry-over directions, matching and fallback self-exclusion,
   and cache isolation with an existing version counter.

## Risks

- Already-created target applications are not overwritten. There is no reliable provenance
  marker distinguishing carried applications from independently reviewed submissions, so an
  automatic historical document repair is deferred.
- Cache namespace replacement causes one cold recommendation request per user.

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
