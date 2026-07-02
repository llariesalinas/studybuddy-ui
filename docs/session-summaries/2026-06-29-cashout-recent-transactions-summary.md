---
title: Cash-Out Recent Transactions (Remove Standalone Destinations) — Summary
date: 2026-06-29
plan: ../plans/2026-06-29-cashout-recent-transactions.md
spec: ../specs/2026-06-29-cashout-recent-transactions.md
---

# Summary

Implemented all 8 tasks from the plan via subagent-driven-development, on branch
`feature-cashout-recent-transactions`. Three task-review rounds caught real bugs before merge;
all were fixed and re-reviewed clean.

## Backend

- Added `GET /api/wallet/cash-outs/recent/` — returns the tutor's last 4 withdrawals,
  most-recent-first, no status filtering or dedup.
- `POST /api/wallet/cash-outs/` now accepts destination fields directly in the request body
  (`destination_type`, `receiving_institution_id/_name/_code`, `account_number`, `account_name`,
  `bank_name`, optional `note`) instead of a `payout_account_id` lookup.
- **New-destination confirmation contract** (designed during planning, not literally specified in
  the PRD): the endpoint compares the submitted destination against the tutor's last 4
  withdrawals on `method`, `receiving_institution_id`, `account_number`, `account_name`. If none
  match and the tutor has prior history, it returns `409
  {"error": "new_destination_confirmation_required"}` without creating anything, unless
  `confirm_new_destination: true` is sent. A tutor with zero prior withdrawals never triggers this
  check (nothing to compare against).
- Added `note`, `receiving_institution_id`, `receiving_institution_name`,
  `receiving_institution_code` fields to `WithdrawalRequest` (two small additive migrations,
  `0061` and `0062`).
- Removed `TutorPayoutAccount` model, `payout_destinations()` view, its URL routes, its
  serializer, and its `admin.py` registration — via a destructive migration (`0063`), run against
  the local dev database with explicit user go-ahead at execution time.
- Extended `TutorCashOutTests` / `WalletCashOutEdgeCaseTests` (the existing highest test seam)
  rather than adding a new test class; net 19 tests in those two classes after the dust settled
  (some old `payout_account_id`-specific tests were replaced with equivalent inline-field tests).

## Frontend

- `src/stores/wallet.js`: added `recentCashOuts` state + `fetchRecentCashOuts()`; changed
  `requestWithdrawal()` to send the new inline-field body and let errors (including the 409)
  propagate as rejected promises instead of returning `{success, error}`; removed
  `payoutAccounts`, `fetchPayoutAccounts`, `savePayoutAccount`, `deactivatePayoutAccount`.
- `src/views/TutorWallet.vue`: removed the standalone "Destinations" card and the "Add
  Destination" modal entirely. The cash-out modal is now the single form — destination type,
  receiving institution, account number, account name, bank name (shown for `bank` only), amount,
  optional note. It shows up to 4 recent-transaction shortcut cards; tapping one pre-fills
  destination fields (not amount or note), and every field remains editable afterward. A
  client-side match check mirrors the backend's: matching destinations submit directly, mismatches
  show an in-modal confirmation step (destination + amount summary, Edit / Confirm & Send) before
  the request is sent with `confirm_new_destination: true`. A race-condition fallback shows the
  same confirmation step if the server still returns the 409 after a client-side "match" verdict.

## Deviations from plan / fixes found in review

- **`bank_name` auto-fill** (Task 5 fix): the first pass left `bank_name` unvalidated and not
  shown in the confirmation summary, and didn't auto-populate it from the selected institution
  like the old flow did. Fixed: validated when `destination_type === 'bank'`, shown in the
  confirm-step summary, and auto-filled from the institution (tracked via a `bankNameAutoFilled`
  ref so it doesn't clobber a manually-typed value or a value copied from a shortcut).
- **Match check missing `receiving_institution_id`** (Tasks 2/3 fix): the first pass only compared
  `method`/`account_number`/`account_name`, because `WithdrawalRequest` had no institution-id
  field to compare against — meaning a same-account-number-different-institution destination would
  have wrongly skipped confirmation. Fixed by adding the three institution fields to the model and
  including `receiving_institution_id` in the match check, with a regression test proving it.
- **Status code on the new `recent_cash_outs()` endpoint**: the original brief said 404 for a
  non-tutor caller; fixed to 403 to match every sibling wallet view's convention.
- **Three things found and fixed in Task 7 that the brief's grep didn't catch**: `admin.py` still
  registered `TutorPayoutAccount`; `serialize_cash_out()` had a stray `payout_account_id` field
  that would have thrown `AttributeError` post-migration; one existing test exercised the dead
  destination endpoints by URL string (not caught by a keyword grep) and was removed as obsolete.

## Manual verification

Verified live against the running app (Daniel Tan, a tutor with 2 legacy withdrawals, and Dave
Tutor, a fresh tutor with none): Destinations UI is gone everywhere; recent shortcuts render
correctly (most-recent-first, blank for the zero-history tutor); shortcut selection pre-fills
destination fields while leaving amount/note untouched and every field editable; a mismatched
destination triggers the confirmation step with a correct summary, and `confirm_new_destination`
gets it through; a matching destination skips the step entirely; the ₱50,000 cap and PHP 10 fee
are unchanged. The only failures hit during manual testing were "PayMongo wallet is not
configured" — a pre-existing local-dev environment limitation, not a defect in this feature.

## Checks run

- `python manage.py test studybuddy` — 170 tests, 14 failures + 2 errors, all in
  dashboard-recommendation / admin-analytics / avatar-upload areas (pre-existing, confirmed
  unrelated to this branch's changes — none touch cash-out/wallet/withdrawal code).
- `npm run lint` — 20 pre-existing errors in unrelated files, none introduced by this branch.
- `npm run build` — clean.
- `python manage.py check` — clean.
