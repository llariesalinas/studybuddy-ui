# Build 04: Payment Method Deduplication

## Summary

Fixed duplicate online payment buttons on the tutee payment screen. The database can contain legacy active online methods such as `ONLINE` or `online` alongside the newer `PAYMONGO` method, so the payment-method API now returns a canonical list.

## Changes

- Updated `payment_methods` in `backend/studybuddy/views.py`.
- If active `PAYMONGO` exists, legacy `ONLINE` / `online` methods are hidden from the API response.
- Kept `CASH` visible.
- Kept PayMongo visible as `Pay Online (GCash / Card)`.
- No frontend rendering change was needed because the API now returns clean data.

## Test Cases

- Creates active `CASH`, `ONLINE`, `online`, and `PAYMONGO` rows.
- Confirms `/api/payment-methods/` returns only `CASH` and `PAYMONGO`.
- Confirms PayMongo checkout initiation and verification tests still pass.

## Validation

- `python manage.py test studybuddy.tests.PaymentMethodTests studybuddy.tests.OnlinePaymentInitiationTests -v 2 --keepdb`
- `python manage.py test studybuddy.tests -v 2 --keepdb`
- `npx eslint src/views/PostSessionPaymentView.vue --cache`
- `npx oxlint src/views/PostSessionPaymentView.vue`
- `git diff --check`

