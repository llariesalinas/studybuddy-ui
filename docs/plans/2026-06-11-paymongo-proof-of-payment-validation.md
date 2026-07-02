---
title: PayMongo proof-of-payment validation
date: 2026-06-11
status: Draft        # Draft | Approved | In Progress | Done
spec: 2026-06-08-online-only-payments.md
---

# PayMongo proof-of-payment validation

<!-- LIVING SUMMARY: keep this section and the Changelog at the bottom current on every
     edit to this plan. Update on each phase completion, decision, or scope change. -->

## Status & Progress Summary

**Status:** Draft · **Last updated:** 2026-06-11

Not started. Created as a follow-up to
[Online-only payments + mandatory proof of payment](2026-06-08-online-only-payments.md)
after verification found its "Backend Validation" claim was false. Path A vs Path B
(see Approach) is not yet decided — that decision is Step 1-3 of this plan.

---

## Goal

Close the gap left by [Online-only payments + mandatory proof of payment](2026-06-08-online-only-payments.md):
make `PAYMONGO` payments actually carry verifiable proof (receipt image and/or
transaction reference). Today the relevant checks in `confirm_payment_and_book()` and
`submit_session_payment()` (`backend/studybuddy/views.py`, ~lines 1909 and 2689) gate
the requirement on `method.code == 'online'`, but the only active payment method is now
`PAYMONGO`, so the check never fires and proof-of-payment is not enforced.

## Approach

Two candidate paths — pick one after investigation (Step 1):

- **Path A — PayMongo webhook is the source of truth.** The PayMongo webhook handler
  (`views.py`, ~lines 4127-4148) already sets `Payment.transaction_reference` from the
  PayMongo API response on successful checkout. If this fires reliably for all PAYMONGO
  bookings, proof-of-payment is effectively already guaranteed by the payment provider,
  and the manual receipt-upload UI/endpoint becomes dead code that should be removed
  (`PostSessionPaymentView.vue`'s manual-method branch and the corresponding manual
  submit path in `submit_session_payment`).
- **Path B — Keep a manual fallback, fix the check.** If a manual proof-of-payment path
  is still needed (e.g. webhook delivery isn't guaranteed), update the
  `is_online_payment` condition in both `confirm_payment_and_book()` and
  `submit_session_payment()` to recognize `PAYMONGO` (or any active non-CASH method) so
  the receipt image + transaction reference become genuinely mandatory.

## Steps

1. **Investigate reachability**: confirm whether the manual receipt-upload branch in
   `PostSessionPaymentView.vue` / `submit_session_payment` can still be reached now that
   `/api/payment-methods/` only returns `PAYMONGO`.
2. **Confirm webhook reliability**: verify the PayMongo webhook reliably populates
   `Payment.transaction_reference` for completed checkouts (test data + logs).
3. **Decide Path A vs Path B** based on findings from steps 1-2.
4. **Implement** the chosen path:
   - Path A: remove the dead manual receipt-upload branch and endpoint.
   - Path B: update the `is_online_payment` checks to match `PAYMONGO`.
5. **Update the original plan**: mark the gap in
   [2026-06-08-online-only-payments.md](2026-06-08-online-only-payments.md) Risks/Status
   as resolved, with a Changelog entry.
6. **Validate**: run backend tests and a manual PAYMONGO checkout walkthrough confirming
   `Payment.transaction_reference` (and/or receipt image) is populated as expected.

## Risks

- Changing `is_online_payment` could affect future payment method codes if not scoped
  carefully (e.g. should match "any active non-CASH method", not just `PAYMONGO`
  literally).
- If Path A is chosen, confirm no in-flight or recent bookings rely on the manual
  receipt-upload path before removing it.

## Checks to run

- `python manage.py test` (backend).
- Manual PAYMONGO checkout walkthrough confirming `Payment.transaction_reference` is
  populated and `confirm_payment_and_book()` / `submit_session_payment()` enforce it.
- `npm run lint` and `npm run build` if frontend files are touched.

## Changelog

- **2026-06-11**: Plan created (Draft) as a follow-up to
  [2026-06-08-online-only-payments.md](2026-06-08-online-only-payments.md), to track
  closing the proof-of-payment gap found during verification.
