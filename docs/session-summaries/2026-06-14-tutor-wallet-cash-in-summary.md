---
title: Tutor Wallet Cash-In (Top-Up) — Session Summary
date: 2026-06-14
plan: ../plans/2026-06-14-tutor-wallet-cash-in.md
spec: ../specs/2026-06-14-tutor-wallet-cash-in-design.md
status: Done
---

# Tutor Wallet Cash-In (Top-Up) — Session Summary

## What shipped

A tutor can load money into their StudyBuddy wallet via PayMongo Checkout (primarily to settle
platform commission owed from CASH sessions, which drives the balance negative). Crediting is
client-verified on redirect return, mirroring the existing booking online-payment flow.

### Backend
- **`WalletTopUp` model** (`backend/studybuddy/models.py`) — parallels `WithdrawalRequest`
  (`tutor`, `amount`, `status` pending/paid/failed, `provider`, `provider_reference`, `created_at`,
  `paid_at`). Migration `0058_alter_transaction_transaction_type_wallettopup`.
- **`cash_in` transaction type** added to `Transaction.TRANSACTION_TYPES`.
- **`initiate_cash_in`** (`POST wallet/cash-in/`) — tutor-only; validates amount via
  `parse_money_amount`; creates a `WalletTopUp`; builds a PayMongo Checkout Session with the amount
  converted to **centavos**; wraps the request in try/except for `requests.RequestException` with an
  explicit timeout; marks the top-up `failed` on any provider error; returns `{ checkout_url, id }`.
- **`verify_cash_in`** (`POST wallet/cash-in/<id>/verify/`) — tutor-only; idempotent. Confirms the
  checkout is paid via `is_paymongo_checkout_paid`, then inside `transaction.atomic()` +
  `select_for_update()` flips the top-up to `paid`, credits the wallet, and writes a `cash_in`
  `Transaction` keyed on `TOPUP-{id}` (double-guarded against double-crediting).
- **`serialize_cash_in`** helper beside `serialize_cash_out`.
- Routes registered in `backend/studybuddy/urls.py`.

### Frontend
- **`src/stores/wallet.js`** — `initiateCashIn(amount)` and `verifyCashIn(id)` actions
  (verify re-fetches wallet + transactions).
- **`src/components/CashInModal.vue`** (new) — numeric amount input, in-flight disabling, toast on
  failure, redirects to PayMongo via `window.location.href`. Styled with `sb-` / CSS-variable
  tokens (no hardcoded brand colors).
- **`src/views/TutorWallet.vue`** — "Cash In" button on the balance card, mounts the modal, handles
  the `?cashin=success|cancelled&id=` redirect return in `onMounted`, and adds `cash_in` to the
  transaction icon/tone maps.

## Deviations from the plan
- The Task 2 and Task 3 backend tests were written together in one pass (one `TutorCashInTests`
  class) rather than strictly task-by-task. All other steps followed the plan.
- Added a small post-plan consistency tweak: the idempotent `verify_cash_in` early-return (when a
  top-up is already `paid`) now also returns `balance`, matching the credit path's response shape.

## Checks run
- `python manage.py makemigrations studybuddy` + `migrate` — migration 0058 created and applied.
- `python manage.py test studybuddy` — **111/111 pass** (includes 6 new `TutorCashInTests`).
- `npx eslint` on changed frontend files — clean.
- `npm run build` — succeeds.

## Follow-ups / notes
- `settings.FRONTEND_URL` must be set for the redirect URLs to resolve (already used by the booking
  payment flow).
- Money pass-through (no amount cap) is an accepted product tradeoff documented in the spec; the
  future mitigation is a cap at "owed amount + buffer".
- Not done (YAGNI per spec): PayMongo webhook, amount cap, admin UI for top-ups, tutee cash-in,
  refunds. End-to-end sandbox payment was not exercised in this session (no live PayMongo run).
