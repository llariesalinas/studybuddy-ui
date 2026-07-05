# StudyBuddy Wallet Cash-In and Cash-Out Testing Guide

Use this guide to test tutor wallet top-ups and withdrawals in StudyBuddy.

## Scope

This covers the tutor wallet flow at `/tch-wallet`:

- Cash In: tutor adds wallet funds through a PayMongo Checkout Session.
- Cash Out: tutor withdraws wallet balance to a saved GCash or bank destination through PayMongo Money Movement.
- Wallet ledger: balance, recent transactions, payout destinations, and cash-out history.

## Prerequisites

1. Run the backend with payment environment variables configured.

   Required for both cash-in and online checkout:

   ```env
   PAYMONGO_SECRET_KEY=sk_test_...
   FRONTEND_URL=http://localhost:5173
   ```

   Required for cash-out:

   ```env
   PAYMONGO_WALLET_ID=wallet_...
   PAYMONGO_CASHOUT_CALLBACK_URL=https://your-api.example.com/api/wallet/paymongo/callback/
   PAYMONGO_CASHOUT_CALLBACK_SECRET=shared-secret
   CASHOUT_PROVIDER_FEE_PHP=10
   CASHOUT_MIN_PHP=500
   ```

   Production startup now expects the callback secret to be present. Keep
   `PAYMONGO_CASHOUT_MOCK=true` limited to local `DEBUG` runs only.

2. Use a tutor account. The wallet endpoints return `403 Not a tutor` for non-tutor users.

3. For local manual testing, run the frontend at `http://localhost:5173` and open `/tch-wallet`.

4. In development mode only, the wallet page exposes Dev Tools:

   - `Add Test Funds` calls `POST /api/dev/wallet/add/`.
   - `Remove Funds` calls `POST /api/dev/wallet/remove/`.

   These are useful for preparing cash-out balances without completing real sessions.

## Cash In Test

### UI Flow

1. Sign in as a tutor.
2. Go to `/tch-wallet`.
3. Click `Cash In`.
4. Enter an amount greater than `0`.
5. Click `Continue to Payment`.
6. Confirm the app redirects to PayMongo Checkout.
7. Complete or cancel the checkout in PayMongo test mode.
8. On success, PayMongo redirects back to:

   ```text
   /tch-wallet?cashin=success&id=<topup_id>
   ```

9. The wallet page automatically calls verify for that top-up and clears the query string.

### Expected Success Result

After successful verification:

- Wallet balance increases by the top-up amount.
- A `WalletTopUp` row moves to `status='paid'`.
- `paid_at` is set.
- A positive `Transaction` is created:

  ```text
  transaction_type = cash_in
  amount = +<top-up amount>
  reference_id = TOPUP-<topup_id>
  description = Wallet Top-Up TOPUP-<topup_id>
  ```

- Recent Activity shows a positive wallet top-up row.

### Expected Cancel Result

If PayMongo redirects to:

```text
/tch-wallet?cashin=cancelled&id=<topup_id>
```

The UI shows a cancellation toast. The wallet should not be credited.

### API Flow

Initiate:

```http
POST /api/wallet/cash-in/
Content-Type: application/json

{ "amount": "100.00" }
```

Expected response:

```json
{
  "checkout_url": "https://checkout.paymongo.com/...",
  "id": 123
}
```

Verify:

```http
POST /api/wallet/cash-in/123/verify/
```

Expected paid response includes the top-up status and current balance:

```json
{
  "id": 123,
  "amount": 100.0,
  "status": "paid",
  "provider": "paymongo",
  "provider_reference": "cs_...",
  "balance": 100.0
}
```

### Cash-In Negative Cases

Test these:

- Amount is `0`, negative, blank, or non-numeric: expect `400 Enter a valid cash-in amount.`
- PayMongo does not return `checkout_url`: top-up becomes `failed`, endpoint returns `502`.
- Verify before paying: expect `400 Payment not completed yet.`
- Verify the same paid top-up twice: balance should not double-credit; there should only be one `TOPUP-<id>` transaction.
- Verify as another tutor: expect not found or unauthorized behavior because top-ups are scoped to the current tutor.

## Cash Out Test

### UI Flow

1. Sign in as a tutor.
2. Go to `/tch-wallet`.
3. Make sure the wallet balance can cover:

   ```text
   cash-out amount + provider fee
   ```

   Default fee is `PHP 10`.

4. Add a payout destination if none exists:

   - Click `Add New Destination`.
   - Choose rail: `InstaPay` or `PESONet`.
   - Choose type: `GCash` or `Bank`.
   - Select a receiving institution.
   - Enter account number and account name.
   - Save destination.

5. Click `Cash Out`.
6. Select a saved active destination.
7. Enter amount.
8. Confirm the summary:

   - You receive: requested amount.
   - Provider fee: configured fee.
   - Total deducted: amount plus provider fee.
   - Rail: `instapay` for amounts up to `PHP 50,000`, `pesonet` above `PHP 50,000`.

9. Click `Confirm Cash Out`.

### Expected Success Result

Immediately after a valid cash-out request:

- Wallet balance decreases by:

  ```text
  requested amount + provider fee
  ```

- A `WithdrawalRequest` is created with `status='pending'`.
- A negative `withdrawal` transaction is created with reference `WD-<withdrawal_id>`.
- If provider fee is greater than zero, a negative `cashout_fee` transaction is created with reference `WD-<withdrawal_id>-FEE`.
- The app calls PayMongo Money Movement.

If PayMongo returns provider status `succeeded`:

- Withdrawal status becomes `processed`.
- `processed_at` is set.
- Cash-Out History shows the provider reference number when available.

If PayMongo returns provider status `failed`, or the request throws a PayMongo cash-out error:

- Withdrawal status becomes `failed`.
- Failure reason is stored from the provider error where possible.
- The wallet is reversed through ledger entries:

  ```text
  withdrawal_reversal: +requested amount, reference WD-<id>-REV
  cashout_fee_reversal: +provider fee, reference WD-<id>-FEE-REV
  ```

### API Flow

List wallet status:

```http
GET /api/wallet/
```

List payout destinations:

```http
GET /api/wallet/payout-destinations/
```

Add payout destination:

```http
POST /api/wallet/payout-destinations/
Content-Type: application/json

{
  "destination_type": "gcash",
  "provider": "instapay",
  "receiving_institution_id": "provider-institution-id",
  "receiving_institution_name": "GCash",
  "receiving_institution_code": "gcash",
  "account_number": "09171234567",
  "account_name": "Test Tutor",
  "bank_name": ""
}
```

Request cash-out:

```http
POST /api/wallet/cash-outs/
Content-Type: application/json

{
  "amount": "500.00",
  "payout_account_id": 1
}
```

Expected response:

```json
{
  "id": 456,
  "amount": 500.0,
  "status": "pending",
  "provider": "paymongo",
  "provider_fee": 10.0,
  "net_amount": 500.0,
  "rail": "instapay",
  "payout_account_id": 1
}
```

PayMongo callback:

```http
POST /api/wallet/paymongo/callback/?token=<PAYMONGO_CASHOUT_CALLBACK_SECRET>
```

The callback payload must contain the PayMongo wallet transaction id. The backend matches it against `provider_wallet_transaction_id` and applies `succeeded` or `failed`.

### Cash-Out Negative Cases

Test these:

- No payout destination: UI blocks cash-out.
- Inactive destination: backend only accepts active destinations.
- Amount below `CASHOUT_MIN_PHP`: expect `400 Minimum cash-out is PHP <min>.`
- Balance cannot cover amount plus fee: expect `400 Insufficient balance for cash-out amount plus provider fee.`
- Destination rail mismatch:
  - amount `<= 50000` requires `instapay`
  - amount `> 50000` requires `pesonet`
- Missing or wrong `PAYMONGO_WALLET_ID`: expect provider failure and reversal.
- PayMongo callback missing or wrong secret token: expect `403 Unauthorized`.
- PayMongo callback with failed provider status: withdrawal becomes `failed` and balance is reversed.

## Quick Manual Test Script

Use this sequence for a practical smoke test:

1. Log in as a tutor.
2. Open `/tch-wallet`.
3. In dev mode, click `Add Test Funds` with `1000`.
4. Confirm balance increases and a dev credit appears in Recent Activity.
5. Add an InstaPay GCash payout destination.
6. Cash out `500`.
7. Confirm balance decreases by `510` if the provider fee is `10`.
8. Confirm Cash-Out History has a new row.
9. Refresh the wallet.
10. Check Recent Activity contains:

    ```text
    withdrawal      -500
    cashout_fee     -10
    ```

11. Cash in `100`.
12. Complete PayMongo Checkout.
13. Confirm balance increases by `100`.
14. Check Recent Activity contains:

    ```text
    cash_in         +100
    ```

## Source Map

- Frontend wallet screen: `src/views/TutorWallet.vue`
- Cash-in modal: `src/components/CashInModal.vue`
- Wallet store: `src/stores/wallet.js`
- Wallet routes: `backend/studybuddy/urls.py`
- Wallet views: `backend/studybuddy/views.py`
- PayMongo Money Movement helper: `backend/studybuddy/paymongo_money_movement.py`
- Admin withdrawal review: `backend/studybuddy/admin_views.py`
