# Online-only payments + proof of payment summary

Implemented Scope B of the online-only payments plan:
- **Backend Status Flip**: Applied database migration `0055_deactivate_cash_payment.py` to set the `is_active` status of the `CASH` method to `False`, making online payment the only active payment option returned.
- **Frontend Code Purge**: 
  - Deleted the dead/unrouted frontend file `src/views/PaymentScreenTutee.vue`.
  - Removed the `CASH`-specific "I Paid in Person" template box and clean-up icon logics in `src/views/PostSessionPaymentView.vue`.
- **Test / Bug Fixes**:
  - Resolved hardcoded date temporal bugs in `backend/studybuddy/tests.py` that caused chat context tests to fail as the dates elapsed into the past.
  - Added test-checking settings to backend `settings.py` so that Django-Q2 enqueues and runs async tasks synchronously (`sync = True`) during tests. This ensures password reset mail delivery assertions pass cleanly.

Verification:
- Frontend code compiles cleanly: `npm run lint` and `npm run build` both succeeded.
- All 99 Django backend tests executed and passed (`python manage.py test --keepdb`).

## Post-ship verification (2026-06-11)

Running the `verify` skill against this work found that one claim in the original plan
was **false**: the plan's "Backend Validation" bullet said the active `online` payment
method already made receipts/transaction references mandatory. In practice,
`confirm_payment_and_book()` and `submit_session_payment()` only enforce that
requirement when `method.code == 'online'`, and the only active method after this
change is `PAYMONGO` — so that check never fires and proof-of-payment is **not** yet
mandatory.

The CASH-deactivation and frontend-cleanup work described above (Scope B) is verified
correct and complete. The proof-of-payment gap is out of scope for this plan and is
tracked as a new follow-up plan:
[2026-06-11-paymongo-proof-of-payment-validation.md](../plans/2026-06-11-paymongo-proof-of-payment-validation.md)
(status: Draft). The original plan's Approach/Risks sections and Status & Progress
Summary have been updated to document this gap.
