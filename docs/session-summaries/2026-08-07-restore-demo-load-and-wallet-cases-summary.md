---
title: Restore booking-load-limit and wallet demo cases -- summary
date: 2026-08-07
plan: ../plans/2026-08-07-restore-demo-load-and-wallet-cases.md
---

# Restore booking-load-limit and wallet demo cases -- summary

## What shipped

Two new, additive, reversible Django management commands, following the
`seed_tie_breaker_demo.py` precedent, plus a doc update:

- **`backend/studybuddy/management/commands/seed_booking_load_limit_demo.py`** -- creates Grace
  Domingo (brand-new tutor, `session_load_limit=10`, 10/10 accepted sessions -- blocked, hidden
  from search) and Paolo Ramirez (8/10 -- still accepting). Both share one dedicated seed tutee
  to own their bookings. `--remove` deletes all three profiles and everything that cascades from
  them.
- **`backend/studybuddy/management/commands/seed_wallet_cases_demo.py`** -- creates Isabel
  Fernandez (one `WalletTopUp` row per state -- paid/pending/failed -- and one `WithdrawalRequest`
  row per state -- pending/processed/rejected/failed/flagged -- with the matching `Transaction`
  rows the real `request_withdrawal`/`cash_outs`/`admin_resolve_ticket` code paths would have
  written, reconciling to a round ₱500.00 balance) and Miguel Torres (a forced-negative wallet via
  a single `counted_strike` `Transaction`, using the real `COUNTED_STRIKE_WALLET_DEDUCTION`
  constant, plus 3 completed cash-paid `Booking`/`Payment` rows dated over the last 3 weeks).
  `--remove` deletes both tutors and the seed tutee.
- **`docs/architecture/demo-data-testing-accounts.html`** -- the "Booking load limits" and
  "Compensation / wallet states" entries moved out of "No Longer Seeded" into a new "Restored via
  opt-in seed commands" section, pointing at the two commands above. No table rows added (matches
  how the tie-breaker command isn't in this doc's tables either -- confirmed during the design
  session, correcting an earlier assumption that it was).

Design was settled via a `/grill-with-docs` session before any code was written; the full decision
trail is in the [plan's Changelog](../plans/2026-08-07-restore-demo-load-and-wallet-cases.md).

## Deviations from the plan

One bugfix not anticipated in the plan: `Tutor`'s `post_save` signal (`create_tutor_wallet`,
`models.py`) creates the `Wallet` at `Tutor.objects.create()` time using the `DecimalField`'s raw
float default (`default=0.00`, a Python float literal) and caches it on the reverse `tutor.wallet`
accessor via Django's one-to-one cache-population behavior. Reading `tutor.wallet` later returned
that cached float-typed instance, which raised `TypeError` on the first Decimal transaction credit.
Fixed by fetching the wallet fresh via `Wallet.objects.get(tutor=tutor)` in `seed_wallet_cases_demo.py`
instead of trusting the cached accessor -- `seed_data.py`'s `_make_wallet` sidesteps the same
footgun by passing an explicit `Decimal('0.00')`, but that route wasn't available here since the
signal creates the wallet before this command's code runs.

Also applied a pending migration (`0080_subjects_description_and_more`) the local dev database was
missing -- unrelated to this work, needed to run anything against that database at all.

## Checks run

- `seed_booking_load_limit_demo` then re-run (idempotent, no duplication) then `--remove` then
  `--remove` again (idempotent no-op) -- all as expected. `get_recommendation_candidate_tutors`
  confirmed Grace excluded, Paolo included.
- `seed_wallet_cases_demo` then re-run (idempotent) then `--remove` then `--remove` again --
  all as expected. Self-verifying output confirmed Isabel's balance landed on exactly ₱500.00 and
  Miguel's on exactly -₱50.00. `get_recommendation_candidate_tutors` confirmed Miguel excluded
  (negative balance).
- `cd backend && python manage.py test studybuddy --keepdb` -- 381 tests, 9 failures + 1 error.
  Confirmed pre-existing and unrelated: `git status` shows only the two new standalone command
  files (never imported by `tests.py` or anything else) plus the doc edit -- nothing that touches
  the failing tests' code paths (avatar upload, cash-out provider-fee normalization, verification
  dev-tools flag gating, session check-in). Consistent with the tie-breaker session's own
  documented finding of pre-existing failures in this same suite.
- Manual: confirmed via `get_recommendation_candidate_tutors` (not just the commands' own
  self-reported summaries) that the Session Load Limit and negative-wallet-balance search gates
  actually exclude/include the right tutors.

## Not done

- No automated tests added for either command, per the design decision (demo/dev-data generators,
  not application logic under test).
- Not committed to the branch yet, and not pushed.
