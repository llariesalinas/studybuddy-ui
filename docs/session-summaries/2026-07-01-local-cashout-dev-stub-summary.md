# Local cash-out dev stub (PayMongo Money Movement) — Summary

Plan: [2026-07-01-local-cashout-dev-stub.md](../plans/2026-07-01-local-cashout-dev-stub.md)

## What shipped

Matches the approved plan exactly — all 6 steps, no deviations.

1. `backend/backend/settings.py` — added `PAYMONGO_CASHOUT_MOCK` (default off, parsed from
   `os.getenv`), plus a `logger.warning` if it's ever combined with `DEBUG=false`.
2. `backend/studybuddy/paymongo_money_movement.py` — `create_wallet_transaction` returns a
   simulated `succeeded` transaction when the flag is on, checked before the `wallet_id`
   guard. No `requests.post` call in that branch.
3. `backend/.env.example` — documented `PAYMONGO_CASHOUT_MOCK`; also added the
   previously-missing `PAYMONGO_CASHOUT_CALLBACK_SECRET` line.
4. `backend/studybuddy/tests.py` — new
   `test_cashout_mock_mode_succeeds_without_wallet_id_or_http_call` in `TutorCashOutTests`,
   asserting 201, `status="processed"`, and `mock_post.assert_not_called()`.

## Why

PayMongo test mode has no Money Movement/payouts product, so there's no test `wallet_...` ID
to configure — the only real code path is live PayMongo with a KYB-approved account moving
real money. That made local cash-out completely unrunnable outside the test suite (which
mocks the provider via `override_settings`). The stub is the only way to exercise the running
app end-to-end in dev.

## Checks run

- `python manage.py test studybuddy.tests.TutorCashOutTests studybuddy.tests.WalletCashOutEdgeCaseTests --keepdb` — 21/21 pass.
- `python manage.py test studybuddy --keepdb` (full suite, 176 tests) — 18 failures/errors,
  all pre-existing and unrelated (dashboard recommendations, tutor availability search, dev
  live-session tooling, SuperAdmin analytics, avatar upload — tied to in-progress
  institution-scoping work already uncommitted in `views.py`). Zero failures in any
  cash-out, cash-in, or support-ticket-escalation test.
- `npm run build` — passes.

## To use locally

Add `PAYMONGO_CASHOUT_MOCK=true` to `backend/.env` and restart the backend. Submitting a
cash-out will now return 201 with the withdrawal immediately `processed`, instead of the
502 "PayMongo wallet is not configured." error.
