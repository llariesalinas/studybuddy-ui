---
title: Local cash-out dev stub (PayMongo Money Movement)
date: 2026-07-01
status: Done
spec:
---

# Local cash-out dev stub (PayMongo Money Movement)

## Status & Progress Summary

**Status: Done.** All 6 steps implemented as planned: `PAYMONGO_CASHOUT_MOCK` setting, the
stub branch in `create_wallet_transaction`, env docs, and a regression test. Verified with
the targeted cash-out test classes, the full backend suite (176 tests — 18 pre-existing
failures elsewhere, none in cash-out/cash-in/support-ticket code), and `npm run build`. See
[session summary](../session-summaries/2026-07-01-local-cashout-dev-stub-summary.md).

## Goal

Let a tutor complete a cash-out in the locally running app. PayMongo test mode has no
Money Movement / payouts product, so there is no test `wallet_...` ID to configure — the
live API path is the only real one, and it needs a KYB-approved account moving real money.
This makes cash-out unrunnable in local dev today: `create_wallet_transaction` either hits
live PayMongo or trips the "PayMongo wallet is not configured." guard.

## Root cause (diagnosed)

Config gap, surfaced by a missing dev seam — not a logic bug:

1. `PAYMONGO_WALLET_ID` (and the two callback vars) are unset in `backend/.env`, so
   `settings.PAYMONGO_WALLET_ID` defaults to `""` (`settings.py:332`).
2. `cash_outs` calls `create_wallet_transaction(settings.PAYMONGO_WALLET_ID, ...)`
   (`views.py:4280`).
3. Falsy `wallet_id` trips the guard at `paymongo_money_movement.py:98`, raising
   `PayMongoCashOutError('PayMongo wallet is not configured.')`.
4. Caught at `views.py:4286`: withdrawal marked `failed`, balance reversed via
   `reverse_failed_cash_out` (`views.py:4033`), HTTP 502 with `provider_error_message`.

The test suite passes because it overrides `PAYMONGO_WALLET_ID="wallet_test"` and mocks the
provider (`tests.py:1623`, `tests.py:1916`), so the guard and the live call are never hit.

## Approach

Add an opt-in dev stub inside the single external-call chokepoint
(`create_wallet_transaction`), gated by a new `PAYMONGO_CASHOUT_MOCK` setting that defaults
**off**. Chosen (over a live account) because test mode offers no payouts product, so a stub
is the only way to exercise the running app locally. Simulated outcome resolves as **instant
success** — the stub returns a `succeeded` transaction so the withdrawal goes straight to
`processed`, with no public callback URL required.

Keep the branch in `paymongo_money_movement.py` only; `views.py` is untouched, so the real
provider contract, fee handling, and reversal logic stay exactly as in production.

## Steps

1. **Settings** (`backend/backend/settings.py`, near line 336): add
   `PAYMONGO_CASHOUT_MOCK = os.getenv("PAYMONGO_CASHOUT_MOCK", "false").lower() in ("1", "true", "yes")`.
2. **Stub** (`backend/studybuddy/paymongo_money_movement.py`): at the top of
   `create_wallet_transaction`, **before** the `wallet_id` guard, if
   `settings.PAYMONGO_CASHOUT_MOCK` is truthy, return a simulated payload matching
   `normalize_wallet_transaction`'s shape:
   - `id`: `f"mock_wtx_{withdrawal_id}"`
   - `status`: `"succeeded"`
   - `provider`: `INSTAPAY_PROVIDER`
   - `reference_number`: `f"MOCK-{withdrawal_id}"`
   - `provider_error_code` / `provider_error_message`: `""`
   - `fee`: `Decimal("0.00")`, `net_amount`: the passed `amount`
   - `raw`: `{"mock": True}`
   Do not call `requests.post` in this branch.
3. **Safety warning**: if `PAYMONGO_CASHOUT_MOCK` is true while `DEBUG` is false, log a
   `logger.warning` (at startup or first use) so it can never run silently in production.
4. **Env docs**: add `PAYMONGO_CASHOUT_MOCK=true` (with a "dev only" comment) to
   `backend/.env.example`; also add the currently-missing
   `PAYMONGO_CASHOUT_CALLBACK_SECRET` line there for completeness.
5. **Local `.env`**: set `PAYMONGO_CASHOUT_MOCK=true`, restart the backend.
6. **Test**: add a test asserting that with `PAYMONGO_CASHOUT_MOCK=True` and an empty
   `PAYMONGO_WALLET_ID`, a cash-out returns 201 and the withdrawal reaches `processed`
   without any outbound HTTP (patch/assert `requests.post` is not called).

## Risks

- **Prod leakage**: someone sets `PAYMONGO_CASHOUT_MOCK=true` in production and cash-outs
  silently succeed without moving money. Mitigated by default-off + the DEBUG-false warning
  in step 3; consider a hard refuse if that risk is unacceptable.
- **Shape drift**: the simulated dict must match `normalize_wallet_transaction` output, or
  `update_cash_out_provider_fields` may misread it. The step-6 test locks this down.
- **Fee accounting**: `provider_fee` is deducted in `cash_outs` before the provider call and
  is independent of the stub's `fee`; returning `fee=0` from the stub is correct and does not
  double-count.

## Checks to run

- `cd backend && python manage.py test studybuddy.tests.TutorCashOutTests studybuddy.tests.WalletCashOutEdgeCaseTests --keepdb` — all pass, including the new mock test.
- Manual: `PAYMONGO_CASHOUT_MOCK=true`, restart backend, submit a cash-out in the app →
  withdrawal shows `processed`, balance debited once, no 502.
- `npm run build` — passes (no frontend changes, but confirms nothing regressed).

## Changelog

- 2026-07-01: Plan created and approved. Diagnosed the blocker as a config gap + missing dev
  seam (PayMongo test mode has no Money Movement product); decided on an opt-in
  `PAYMONGO_CASHOUT_MOCK` stub resolving to instant success.
- 2026-07-01: Implemented all 6 steps. Verified with targeted cash-out tests, the full
  backend suite, and `npm run build`. Marked Done; wrote session summary.
