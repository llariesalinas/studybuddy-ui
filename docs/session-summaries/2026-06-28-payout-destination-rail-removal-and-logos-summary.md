---
title: Payout Destination Rail Removal and Receiving Institution Logos — Summary
date: 2026-06-28
plan: ../plans/2026-06-28-payout-destination-rail-removal-and-logos.md
---

# Summary

Implemented both slices from the plan in a single pass (user opted for "both slices" over
splitting into sub-issues first).

## Rail removal

- Deleted `get_required_cashout_rail`, the `TutorPayoutAccount.provider` rail lock-in field, and
  the `WithdrawalRequest.rail` field, via migration `0060_remove_cashout_rail_fields`.
- Added `CASHOUT_MAX_PHP` (default `50000`) as a named setting, mirroring the existing
  `CASHOUT_MIN_PHP` pattern, with `get_cashout_maximum()` in `views.py`. The cash-out endpoint now
  rejects amounts above this cap with an amount-based error message instead of a rail-mismatch
  error, and the value is returned from `wallet_status` so the frontend doesn't hardcode it.
- `create_wallet_transaction` and `list_receiving_institutions` (in `paymongo_money_movement.py`)
  no longer take a rail/provider argument — they always use InstaPay via a module constant.
  `/api/wallet/receiving-institutions/` no longer accepts or validates a `provider` query param.
- Frontend: removed the Rail select from the "Add Destination" modal, the rail summary row from
  the cash-out modal, and the rail column from `AdminWithdrawals.vue`'s table and detail view.
  `catalog.js`'s `fetchReceivingInstitutions` dropped its provider parameter and now stores a flat
  list instead of a per-provider map (updated `catalog.test.js` to match). The cash-out form now
  shows the live min/max from the wallet store and blocks submission above the cap client-side.
- Rewrote `test_cashout_rejects_rail_mismatch` as
  `test_cashout_same_destination_works_across_different_amounts`, and added
  `test_cashout_allows_exact_cap_amount` / `test_cashout_rejects_amount_above_cap` for the
  boundary. All 11 cash-out tests pass.

## Receiving Institution logos

- Added `src/data/receivingInstitutionLogos.js`: a name-keyed domain mapping plus the pure
  `getReceivingInstitutionLogoUrl(institution, token)` resolver, with a small test file.
- **Deviation from the plan as written**: the plan asked for full coverage of PayMongo's ~90
  InstaPay institutions, keyed by PayMongo's institution id/code. Live lookup of PayMongo's actual
  institution list wasn't available in this session (PayMongo's public docs pages returned 404 on
  fetch), and PayMongo's institution `id` is an opaque per-account value, not a stable code, so the
  mapping is keyed by normalized institution **name** instead. Coverage is ~35 major PH banks and
  e-wallets (BDO, BPI, Metrobank, GCash, Maya, UnionBank, Landbank, etc.), not the full ~90 — this
  is called out in a comment in the data file. The fallback-to-generic-icon behavior the plan
  specifies makes this safe to extend incrementally; it is not a correctness gap, just smaller
  initial coverage than spec'd.
- Added optional `icon` support to `SbSelectModal.vue`'s option rendering (a small, backward
  compatible addition — falls back to no icon when omitted) so the Receiving Institution picker
  in the "Add Destination" modal shows institution logos, with `@error` hiding a broken image.
- The saved Payout Destinations list in `TutorWallet.vue` renders the resolved logo with a
  fallback to the existing generic bank/phone icon, tracked per-account via an `@error` handler so
  a broken image is never shown.
- Added `VITE_LOGO_DEV_TOKEN` / `LOGO_DEV_TOKEN` in `src/config.js` for the optional publishable
  key; the app works with or without it set.

## Checks run

- `python manage.py test studybuddy.tests.TutorCashOutTests studybuddy.tests.WalletCashOutEdgeCaseTests --keepdb` — 11/11 passed
- `python manage.py test studybuddy --keepdb` (full backend suite) — passed
- `npx vitest run` (full frontend suite, 40 tests across all files) — passed
- `npm run build` — succeeded
- `npm run lint` — pre-existing unrelated issues only (stale `.claude/worktrees/perf-debug/` copy
  and untracked scratch scripts); no issues in any file this change touched

## Deviations from the plan

- Implemented both slices together instead of running `/to-issues` to split first, per explicit
  user choice.
- Receiving-institution logo mapping has ~35 entries keyed by name, not ~90 keyed by PayMongo id —
  see above.
