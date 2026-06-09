---
title: Online-only payments + mandatory proof of payment
date: 2026-06-08
status: Approved
spec:
---

# Online-only payments + mandatory proof of payment

## Goal

Disable the cash payment option (online payment only) and require a proof-of-payment
(receipt image + transaction reference) for every payment, not just online ones.

## Approach

This is mostly "turn on what's already there" rather than new plumbing:
- `Payment.receipt_image` (`backend/studybuddy/models.py` ~line 646) is already an
  `ImageField`.
- `PaymentMethod.is_active` already exists and the `/payment-methods/` endpoint
  (`views.py` ~line 3380) already filters on it — soft-disabling CASH needs no schema
  migration, just flipping the flag.
- `PaymentScreenTutee.vue` already renders a receipt-upload UI for online methods.

Decision: soft-disable CASH (`is_active = False`) rather than remove it from the DB —
this avoids a data migration and keeps historical bookings/payments referencing a valid
`PaymentMethod` row intact.

## Steps

1. Backend: set the `CASH` `PaymentMethod` row's `is_active = False`.
2. Backend: in `confirm_payment_and_book()` (`views.py` ~line 1909) and
   `submit_session_payment()` (~line 2689), remove the "only require receipt for online
   methods" branch — once CASH is gone every active method is online, so
   `receipt_image` + `transaction_reference` become unconditionally required.
3. Frontend: in `PaymentScreenTutee.vue`, remove the CASH-specific icon branch
   (~line 216) and make the receipt-upload section unconditional instead of gated on
   `method.code === 'online'`.
4. Frontend: in `PostSessionPaymentView.vue`, remove the "I Paid in Person" CASH flow
   (~lines 71–81).
5. Smoke-check `TutorPaymentScreen.vue`'s verification flow still works now that every
   payment always carries a receipt.

## Risks

- Existing bookings already created with CASH selected (status Pending/Awaiting) —
  grandfather them through as-is rather than retroactively demanding a receipt for
  payments that predate this change.
- Confirm `is_active` filtering is applied everywhere a payment method can be selected,
  not just the main listing endpoint.

## Checks to run

- `/payment-methods/` no longer returns CASH in its response.
- Walk a booking through selection → payment → tutor verification using a non-cash
  method, end to end, in the dev server (`npm run dev`).
- Confirm the backend now rejects a payment submission missing `receipt_image` or
  `transaction_reference` (try submitting without them).
- `npm run lint` and `npm run build` pass after the frontend changes.
