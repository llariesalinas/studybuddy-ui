---
title: Algorithm weights preview fixes
date: 2026-10-15
status: Done
spec: 2026-08-19-dynamic-algorithm-weights.md
---

# Algorithm weights preview fixes

## Status & Progress Summary

Implemented and tested locally on 2026-10-16. Imported from pr139-review-plans.patch and refined
before implementation. Changes are uncommitted and ready for review.

## Goal

Resolve the confirmed PR #139 review findings for algorithm weights preview fixes.

## Approach

Apply the reviewed fixes with regression coverage and preserve established behavior outside the
reported problems. Record implementation refinements and known limitations below.

## Completed steps

1. Preview and baseline requests carry sequence counters and a tutee id. Obsolete responses
   and errors are ignored; only the current preview clears the loading state.
2. Input changes invalidate pending responses immediately, before the debounce delay. Selection
   changes clear rows and baseline and start independent current requests. Unmount invalidates
   requests and cancels the timer. Obsolete scheduled calls cannot restart the loading state.
3. Saving refreshes both baseline and preview. Regression tests cover a pending debounce at Save.
4. Preview and Save share a raw stored-value/default merge and zero-sum override validation.
   Normalization happens after merging, preserving partial-update parity.
5. load_weights retains its previous fallback for unusable stored groups. Existing normalization
   tests verify defaults, missing rows, unknown keys, zero-sum fallback and raw normalization.
6. Deferred-response tests cover old tutee responses, baseline order, obsolete errors, slider
   changes during debounce, and Save. Backend tests verify partial raw-value parity and zero-sum
   rejection.

## Risks

- Existing settings send complete groups, so partial-update parity primarily protects API callers.
- Invalid stored groups retain the existing default fallback; new all-zero overrides return 400.

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
