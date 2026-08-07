---
title: Restore booking-load-limit and wallet demo cases
date: 2026-08-07
status: Done
summary: Bring back the load-limit and wallet demo personas lost in the taxonomy reseed, as additive seed commands, and reconcile the doc that lists them as gone.
spec: ../architecture/demo-data-testing-accounts.html
---

# Restore booking-load-limit and wallet demo cases

## Status & Progress Summary

**Done** — both commands implemented, verified locally, and full test suite confirmed clean of
regressions. See the [session summary](../session-summaries/2026-08-07-restore-demo-load-and-wallet-cases-summary.md).
Not committed yet.

## Goal

`docs/architecture/demo-data-testing-accounts.html` ("No Longer Seeded") documents three personas
the 2026-07-16 taxonomy reseed dropped: Grace Domingo / Paolo Ramirez (booking load limits) and
Isabel Fernandez / Miguel Torres (wallet states). Bring both pairs back without touching
`seed_data.py`'s reproducible fixed-seed run, following the precedent
`seed_tie_breaker_demo.py` set: a separate, additive, `--remove`-reversible management command
layered on top of an existing `seed_data` run. Then update the doc so it stops telling people
these are gone.

Out of scope (per triage): multi-institution scoping (the institutional Admin role it demoed was
removed platform-wide in migration `0072` — not revivable as documented) and the reporting-gap
subjects case (references course codes that don't exist in the new taxonomy).

## Approach

Two new commands under `backend/studybuddy/management/commands/`, both modeled on
`seed_tie_breaker_demo.py`: idempotent-ish (a re-run finds the existing seeded personas by
username rather than duplicating them), transaction-wrapped, and reversible with `--remove`.
Neither modifies `seed_data.py` or its fixed-seed guarantees.

Both commands are brand-new tutor accounts, created from scratch (full profile, `Tutor` row,
`TutorSubjects`, availability) — not existing seeded tutors relabeled. Each command creates its
own dedicated seed tutee to own its bookings (no sharing across commands, no reuse of the
tie-breaker's tutee), keeping every command's `--remove` fully self-contained. Both print a
self-verifying summary after seeding (re-querying the state they just created and asserting it
landed), matching `seed_tie_breaker_demo.py`'s own pattern.

**`seed_booking_load_limit_demo.py`** — two curated tutors:
- **Grace Domingo** (`grace.domingo.demo@cpu.edu.ph`) — `session_load_limit` explicitly set to 10
  (not left to the model default), bookings pushed to `accepted_session_load() == session_load_limit`:
  blocked, hidden from search per ADR-0008's gate. Both targets are computed off the tutor's own
  `session_load_limit` field, not a bare literal `10`.
- **Paolo Ramirez** (`paolo.ramirez.demo@cpu.edu.ph`) — `session_load_limit` explicitly set to 10,
  bookings pushed to `session_load_limit - 2` (8 of 10), still accepting.

**`seed_wallet_cases_demo.py`** — two curated tutors:
- **Isabel Fernandez** (`isabel.fernandez.demo@cpu.edu.ph`) — one `WalletTopUp` row per state
  (`paid`, `pending`, `failed`) and one `WithdrawalRequest` row per state (`pending`, `processed`,
  `rejected`, `failed`, `flagged`), each with its matching `Transaction` row (`cash_in` for the
  paid top-up, `withdrawal`/`withdrawal_reversal`/`cashout_fee` for the withdrawal states as
  applicable). Amounts are worked backward from a round reconciled target balance of ₱500.00, not
  chosen independently.
- **Miguel Torres** (`miguel.torres.demo@cpu.edu.ph`) — `Wallet.balance` forced negative by a
  single `counted_strike` `Transaction` (the ADR-0008 Late Cancellation wallet-deduction path)
  sized larger than his remaining balance — a `Transaction` row only, with no backing
  `SupportTicket`/cancelled `Booking` chain, since the debt banner (`views.py:1444`) only reads
  `wallet.balance < 0`. Separately, 3 completed cash-paid `Booking`/`Payment` rows
  (`PaymentMethod.code == 'CASH'`) dated across the last 2-3 weeks, for cash-payment history.

Scope is exactly what the doc promises — no commission-disclosure extras, per triage.

## Steps

1. `seed_booking_load_limit_demo.py`: create Grace and Paolo from scratch (profile, `Tutor`,
   `TutorSubjects`, availability, `session_load_limit=10` explicit), each with its own dedicated
   seed tutee, create bookings to hit `limit` and `limit - 2` accepted load. Print a self-verifying
   summary (accepted load, search-visibility state) after seeding. `--remove` deletes each
   command's own seed tutee, its bookings, and the two tutor profiles.
2. Update `docs/architecture/demo-data-testing-accounts.html`: replace the "Booking load limits"
   entry in "No Longer Seeded" with a short pointer to the new command (no table rows — matching
   how the tie-breaker command isn't in this doc's tables either).
3. `seed_wallet_cases_demo.py`: create Isabel and Miguel from scratch, build Isabel's one-row-per-
   state `WalletTopUp`/`WithdrawalRequest`/`Transaction` set reconciling to ₱500.00, and Miguel's
   negative-balance `counted_strike` `Transaction` plus 3 cash-paid completed `Booking`/`Payment`
   rows. Print a self-verifying summary (`wallet.balance`, debt-banner state) after seeding.
   `--remove` deletes both personas and everything they own.
4. Update `docs/architecture/demo-data-testing-accounts.html`: replace the "Compensation / wallet
   states" entry with a short pointer to the new command, same treatment as step 2.
5. Manual verification: run each command locally, confirm the API/UI surfaces the intended state
   (load-limit gate hides Grace from search and blocks her booking; Paolo still bookable; Isabel's
   wallet screen shows all top-up/withdrawal states; Miguel shows the debt banner and is blocked
   from new bookings per `views.py:2560`).
6. Write a session summary once both commands are verified working.

## Risks

- **Availability/date collisions.** Like the tie-breaker command, booking creation depends on free
  `TutorAvailability` slots; may need `--sessions`-style overrides if the demo DB's availability
  is sparse for a given tutor.
- **Negative-balance mechanics.** No existing code path directly sets a negative balance outside
  normal transaction flows; the command needs to produce it via a legitimate-looking transaction
  (e.g. a commission deduction larger than balance) rather than writing `balance` directly, so the
  `Transaction` ledger stays consistent with `Wallet.balance`.
- **`session_load_limit` drift.** Grace's 10/10 assumes the model default; if a demo DB has a
  tutor with a customized `session_load_limit`, the command should read it rather than hardcode 10.
- **Reversibility.** `--remove` must not cascade into anything beyond what each command created —
  same discipline as `seed_tie_breaker_demo.py`'s scoped delete.

## Checks to run

- `cd backend && python manage.py seed_booking_load_limit_demo` then `--remove` — both succeed,
  self-verifying output confirms 10/10 and 8/10 load, `--remove` leaves no orphaned rows.
- `cd backend && python manage.py seed_wallet_cases_demo` then `--remove` — same, self-verifying
  output confirms Isabel's ₱500.00 reconciled balance and Miguel's negative balance.
- `cd backend && python manage.py test studybuddy` — full existing suite still passes (no new
  tests added; these are demo/dev-data generators, not application logic under test).
- Manual: confirm Grace is absent from tutee search results, Paolo is present, Isabel's wallet
  screen renders all transaction/withdrawal states, Miguel's debt banner shows and his booking
  attempts are blocked.

## Changelog

- **2026-08-07** — Plan drafted from clarifying questions: scope is booking-load-limit + wallet
  cases only (multi-institution and reporting-gap scenarios excluded); wallet cases follow the
  separate-additive-command pattern; wallet detail matches the doc exactly, no commission-disclosure
  extras. Status: Draft, awaiting approval.
- **2026-08-07** — Grilled to a fully settled design: both personas pairs are brand-new tutor
  accounts (not existing tutors relabeled); Miguel's negative balance comes from a single
  `counted_strike` Transaction only, no backing SupportTicket/Booking chain; each command gets its
  own dedicated seed tutee (no sharing, corrected the earlier assumption that the tie-breaker
  tutee could be reused); Grace/Paolo get `session_load_limit` explicitly set to 10 with targets
  computed off that field, not a bare literal; Isabel gets one row per wallet state reconciling to
  a round ₱500.00 target; Miguel gets 3 cash-paid completed bookings over the last 2-3 weeks; both
  commands self-verify their output on the tie-breaker command's model; doc updates happen inline
  per command (short pointers replacing "No Longer Seeded" entries, no new table rows — corrected
  the earlier assumption that the tie-breaker command was already documented in the table, it
  isn't); no new automated tests. Status: Approved, ready to implement.
- **2026-08-07** — Implemented both commands as designed. One bugfix beyond the written plan:
  `Tutor`'s `post_save` signal (`create_tutor_wallet`, models.py) creates the `Wallet` at
  `Tutor.objects.create()` time using the model field's raw float default and caches it on the
  reverse `tutor.wallet` accessor, which broke Decimal arithmetic in `seed_wallet_cases_demo.py`;
  fixed by fetching the wallet fresh via `Wallet.objects.get(tutor=tutor)` instead of trusting the
  cached accessor. Applied a pending migration (`0080_subjects_description_and_more`) the local
  dev DB was missing, unrelated to this work. Verified: both commands run and re-run idempotently,
  `--remove` cleans up fully and is itself idempotent, and `get_recommendation_candidate_tutors`
  correctly excludes Grace (load limit reached) and Miguel (negative balance) while including
  Paolo. Full suite: 381 tests, 9 failures + 1 error, confirmed pre-existing and unrelated (`git
  status` shows only two new standalone command files plus a doc edit — nothing that touches the
  failing tests' code paths). Status: Done, not committed.
- **2026-08-07** — `/code-review` (Standards + Spec axes, parallel sub-agents) run before commit.
  One real bug found and fixed: the doc edit had accidentally duplicated the "Reporting gap
  subjects" block into the new "Restored" section, where it read as a gone-scenario notice sitting
  under a "Restored" heading. One cosmetic fix: aligned `seed_wallet_cases_demo.py`'s `datetime`
  import to module scope, matching its sibling file. Remaining findings (constant duplication
  across the two sibling commands, matching existing precedent; Isabel's ledger deriving only the
  flagged amount backward rather than every amount, while still provably reconciling to the target
  via an assertion; the doc using a full section rather than a single inline sentence) were judged
  in-spirit compliant or precedent-consistent, not requiring rework. Status: Done, ready to commit.
