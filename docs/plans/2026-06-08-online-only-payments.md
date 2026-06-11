---
title: Online-only payments + mandatory proof of payment
date: 2026-06-08
status: Done
spec:
---

# Online-only payments + mandatory proof of payment

<!-- LIVING SUMMARY: keep this section and the Changelog at the bottom current on every
     edit to this plan. Update on each phase completion, decision, or scope change. -->

## Status & Progress Summary

**Status:** Done · **Last updated:** 2026-06-11

Scope B shipped and verified: migration `0055_deactivate_cash_payment.py` deactivates the
`CASH` `PaymentMethod`, `/api/payment-methods/` now returns only `PAYMONGO`,
`PaymentScreenTutee.vue` was deleted (zero references), and the CASH "I Paid in Person"
path was removed from `PostSessionPaymentView.vue`.

**Verified gap (2026-06-11):** The original "Backend Validation" claim was incorrect.
`confirm_payment_and_book()` and `submit_session_payment()` only require a receipt image
and transaction reference when `method.code == 'online'`, which the active `PAYMONGO`
method never matches — so proof-of-payment is **not** actually mandatory yet. This is
out of scope for this plan and tracked separately in
[PayMongo proof-of-payment validation](2026-06-11-paymongo-proof-of-payment-validation.md).

---

## Goal

Disable the cash payment option (online payment only) and clean up dead/unreachable cash payment paths in the frontend code.

## Approach

- **Backend Status Flip**: Soft-disable the `CASH` `PaymentMethod` (`is_active = False`) via a new Django database migration. This avoids data deletion and keeps historical bookings/payments intact.
- **Frontend Code Purge (Scope B)**:
  - Remove the dead, unrouted frontend file `src/views/PaymentScreenTutee.vue`.
  - Remove the CASH-specific "I Paid in Person" handler and markup block from `src/views/PostSessionPaymentView.vue`.
- **Backend Validation (gap, not addressed by this plan)**: Verified during review that `confirm_payment_and_book()` (`views.py` ~line 1909) and `submit_session_payment()` (~line 2689) gate the receipt/transaction-reference requirement on `method.code == 'online'`. The only active method after this change is `PAYMONGO`, so that check never fires — proof-of-payment is **not** actually mandatory yet. Tracked separately in [PayMongo proof-of-payment validation](2026-06-11-paymongo-proof-of-payment-validation.md).

## Steps

1. **Backend**: Create and run a new Django migration in `backend/studybuddy/migrations` to update `PaymentMethod` with `code='CASH'` to have `is_active = False`.
2. **Frontend (Delete Dead File)**: Delete the unused file `src/views/PaymentScreenTutee.vue`.
3. **Frontend (Clean Active View)**: Edit `src/views/PostSessionPaymentView.vue` to remove the template block and selection logic for `CASH` (`selectedMethod?.code === 'CASH'`).
4. **Validation**: Run existing tests and perform build checks (`npm run lint`, `npm run build`, and backend tests).

## Risks

- Grandfathered bookings that used CASH can still display historical records properly since the `PaymentMethod` row is kept (soft-disabled, not deleted).
- **Proof-of-payment is not yet enforced for `PAYMONGO`** (see Status & Progress Summary above). `is_online_payment` checks in `confirm_payment_and_book()` and `submit_session_payment()` key off `method.code == 'online'`, which never matches `PAYMONGO`, so the receipt/transaction-reference requirement is dead code for the only active payment method.

## Checks to run

- Django backend tests run and pass (`python manage.py test`).
- Tutee API endpoint `/api/payment-methods/` no longer returns the `CASH` option.
- Frontend builds and lint checks pass cleanly.

## Changelog

- **2026-06-11**: Verification (`verify` skill) found the "Backend Validation" claim in
  the Approach section was factually wrong — corrected it to document the gap. Added a
  Risks bullet for the same gap. Added this Status & Progress Summary / Changelog
  structure. Created follow-up plan
  [2026-06-11-paymongo-proof-of-payment-validation.md](2026-06-11-paymongo-proof-of-payment-validation.md)
  to track closing the gap. Status remains **Done** — Scope B (this plan's actual scope)
  shipped and verified correctly; the proof-of-payment gap is a separate, follow-up
  effort.
