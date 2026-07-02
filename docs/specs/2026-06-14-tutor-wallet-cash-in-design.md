---
title: Tutor Wallet Cash-In (Top-Up)
date: 2026-06-14
status: Approved
feature-slug: tutor-wallet-cash-in
roles: tutor
---

# Tutor Wallet Cash-In (Top-Up) — Design Spec

## Goal

Let a tutor load (deposit) money into their StudyBuddy wallet via PayMongo Checkout. The
primary purpose is to **settle platform commission owed from CASH sessions**, which currently
drives the wallet `balance` negative (the CASH-session commission deduction at
`backend/studybuddy/views.py:4455` has no floor). A successful cash-in credits the wallet,
moving a negative balance toward zero (or positive).

## Decisions (locked)

- **Purpose:** settle owed commission. Funds raise a negative `balance`.
- **Amount cap:** none. A tutor may load any positive amount; any excess above what they owe
  remains a positive, withdrawable balance.
- **Payment rail:** reuse the existing PayMongo **Checkout Session** flow (the same mechanism
  as booking online payments in `initiate_online_payment` / `verify_online_payment`), plus a
  dedicated record modeled on `WithdrawalRequest`.
- **Crediting trigger:** client-verified on redirect return (polling), **not** a webhook.

## Known tradeoff (accepted)

With no cap, the wallet becomes a money pass-through: a tutor can load funds via card and then
cash them out. This carries laundering / card-fee-arbitrage risk. Accepted for now per product
decision; revisit if abuse appears (a future cap at "owed amount + buffer" is the mitigation).

## Data model

### New model: `WalletTopUp` (`backend/studybuddy/models.py`)

Parallels `WithdrawalRequest`.

| Field | Type | Notes |
|---|---|---|
| `tutor` | `ForeignKey(Tutor, on_delete=CASCADE, related_name='top_ups')` | owner |
| `amount` | `DecimalField(max_digits=10, decimal_places=2)` | positive PHP |
| `status` | `CharField(max_length=20, choices=STATUS, default='pending')` | `pending` / `paid` / `failed` |
| `provider` | `CharField(max_length=20, default='paymongo')` | |
| `provider_reference` | `CharField(max_length=100, blank=True)` | PayMongo checkout session id |
| `created_at` | `DateTimeField(auto_now_add=True)` | |
| `paid_at` | `DateTimeField(null=True, blank=True)` | set on successful verify |

`STATUS = [('pending','Pending'), ('paid','Paid'), ('failed','Failed')]`

### Modified: `Transaction.TRANSACTION_TYPES` (`backend/studybuddy/models.py:293`)

Add one choice:

```python
('cash_in', 'Wallet Top-Up'),
```

A successful cash-in writes a `Transaction` with `transaction_type='cash_in'`, positive
`amount`, and `reference_id=f"TOPUP-{topup.id}"` (idempotency key — mirrors
`credit_tutor_wallet`'s `reference_id` existence guard at `views.py:4428`).

### `Wallet` — unchanged

`balance` already permits negatives; a cash-in just increments it.

## API

Both endpoints are tutor-only, resolved with the existing `get_request_tutor(request)` helper
(returns 403 for non-tutors), and registered in `backend/studybuddy/urls.py`.

### `POST wallet/cash-in/` — initiate

Request body: `{ "amount": <number> }`

1. `tutor = get_request_tutor(request)`; 403 if `None`.
2. `amount = parse_money_amount(request.data.get('amount'))`; 400 `"Enter a valid cash-in amount."`
   if `None` (this rejects non-numeric, zero, and negative — reusing `views.py:3694`).
3. Create `WalletTopUp(tutor=tutor, amount=amount, status='pending', provider='paymongo')`.
4. Build a PayMongo Checkout Session:
   - **`amount_cents = int(amount * decimal.Decimal("100"))`** — convert to centavos.
     (Explicitly avoids the cash-out V0 bug where pesos were sent raw.)
   - `line_items`: one item, `currency: "PHP"`, `amount: amount_cents`,
     name/description `f"StudyBuddy Wallet Top-Up TOPUP-{topup.id}"`.
   - `payment_method_types`: `["gcash", "card", "paymaya"]` (match booking checkout).
   - `success_url`: `f"{settings.FRONTEND_URL}/tch-wallet?cashin=success&id={topup.id}"`
   - `cancel_url`: `f"{settings.FRONTEND_URL}/tch-wallet?cashin=cancelled&id={topup.id}"`
   - Headers from `get_paymongo_auth_headers()` (`views.py:3564`).
5. On PayMongo `200/201`: store `topup.provider_reference = res_data['data']['id']`, save,
   and return `{ "checkout_url": <url>, "id": topup.id }` (extract `checkout_url` the same way
   `initiate_online_payment` does at `views.py:4244`).
6. On PayMongo error / missing `checkout_url`: mark `topup.status='failed'`, save, return
   `502` with `{ "error": <provider message> }`. Wrap the `requests.post` in try/except for
   `requests.RequestException` (do not repeat the unhandled-exception gap from the scan).
   Pass an explicit `timeout` on the request.

### `POST wallet/cash-in/<int:topup_id>/verify/` — confirm & credit

1. `tutor = get_request_tutor(request)`; 403 if `None`.
2. `topup = get_object_or_404(WalletTopUp, id=topup_id, tutor=tutor)`.
3. If `topup.status == 'paid'`: return the current serialized topup (idempotent no-op).
4. If no `provider_reference`: 400 `"No PayMongo checkout for this top-up."`
5. `GET https://api.paymongo.com/v1/checkout_sessions/{provider_reference}` with
   `get_paymongo_auth_headers()` and an explicit `timeout`. Non-200 → `502`.
6. If `not is_paymongo_checkout_paid(res_data)` (`views.py:3615`): return `400`
   `{ "error": "Payment not completed yet." }`.
7. If paid — inside one `transaction.atomic()` with `select_for_update()` on the wallet:
   - Re-check `topup.status != 'paid'` (guard against concurrent verify).
   - `topup.status = 'paid'`; `topup.paid_at = now()`; save.
   - Guard idempotency: if a `Transaction` with `reference_id=f"TOPUP-{topup.id}"` exists, skip
     the credit.
   - Else `wallet.balance += topup.amount`; save; create the `cash_in` `Transaction`.
8. Return serialized topup + new balance.

### Serializer helper

`serialize_cash_in(topup)` → `{ id, amount (float), status, provider, provider_reference,
created_at, paid_at }`. Lives beside `serialize_cash_out`.

## Frontend

### `src/stores/wallet.js` (modify)

Add two actions using the authenticated `api` instance:

```js
async function initiateCashIn(amount) {
  const { data } = await api.post('wallet/cash-in/', { amount })
  return data            // { checkout_url, id }
}

async function verifyCashIn(id) {
  const { data } = await api.post(`wallet/cash-in/${id}/verify/`)
  await fetchWallet()
  await fetchTransactions()
  return data
}
```

Export both from the store's return object.

### `src/components/CashInModal.vue` (new)

- Props: `modelValue` (open boolean) or use a parent `v-if`; emits `close`.
- A single numeric amount input (`type="number"`, `min` step `0.01`) bound to a local ref.
- Validation: positive amount required; disable the submit button while a request is in flight
  (avoid the double-submit class of bug the scan flagged).
- On submit: `const { checkout_url } = await walletStore.initiateCashIn(amount)`, then
  `window.location.href = checkout_url`. Show a toast on failure (`useToastStore`).
- Styling: `.sb-card`, `.sb-btn-pill`, `.text-sb-primary` / `.bg-sb-primary`, `.border-sb` —
  no hardcoded hex (see `.claude/CLAUDE.md` styling rules).

### `src/views/TutorWallet.vue` (modify)

- Add a **"Cash In"** button near the existing cash-out action; clicking opens `CashInModal`.
- On mount (`onMounted`), handle the PayMongo redirect return, mirroring
  `TuteeSessionDetailsFlow.vue:404`:

```js
if (route.query.cashin === 'success' && route.query.id) {
  try {
    await walletStore.verifyCashIn(route.query.id)
    toast.push('Wallet topped up successfully.', 'success')
  } catch {
    toast.push('We could not confirm your top-up. Refresh to check your balance.', 'error')
  } finally {
    router.replace({ query: {} })   // clear query params
  }
} else if (route.query.cashin === 'cancelled') {
  toast.push('Cash-in cancelled.', 'info')
  router.replace({ query: {} })
}
```

## Out of scope (YAGNI)

- PayMongo webhook (client-verify only, like the booking flow).
- Amount cap / owed-amount enforcement.
- Admin UI for viewing top-ups.
- Tutee cash-in (tutees pay per-booking, not via a wallet).
- Refunds / reversing a completed top-up.

## Success criteria

1. A tutor with a negative wallet balance opens "Cash In", enters an amount, and is sent to
   PayMongo Checkout.
2. After paying (sandbox), they are redirected back to `/tch-wallet`; the balance increases by
   the amount and a "Wallet Top-Up" transaction appears in history.
3. Re-running verify (or refreshing the redirect URL) does **not** double-credit.
4. A non-tutor calling the endpoints gets 403; an invalid amount gets 400.
5. `python manage.py test` and `npm run build` pass.

## Checks to run

- Backend: `python manage.py makemigrations && python manage.py migrate`,
  `python manage.py test studybuddy`
- Frontend: `npm run lint`, `npm run build`
