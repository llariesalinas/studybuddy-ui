# Build 01: PayMongo Checkout Initiation

## Summary

Fixed the first PayMongo checkout failure where the backend treated non-`201` PayMongo responses as failed checkout creation. PayMongo can return `200 OK` for a successful checkout session, so the endpoint now accepts both `200` and `201`.

## Changes

- Updated `initiate_online_payment` in `backend/studybuddy/views.py`.
- Accepted PayMongo success responses with status `200` or `201`.
- Added defensive validation for `data.attributes.checkout_url`.
- Improved provider error handling for PayMongo `400` and `401` responses.
- Kept sensitive data out of logs and responses.
- Changed payment amount math to use `Decimal`.
- Ensured local `Payment` records are created or updated only after a checkout URL exists.

## Test Cases

- PayMongo `200 OK` with checkout URL returns `payment_url`.
- PayMongo `201 Created` with checkout URL returns `payment_url`.
- PayMongo `400` returns the provider validation message.
- PayMongo `401` returns a secret-key/configuration error.
- PayMongo success without `checkout_url` returns a controlled backend error.
- Successful checkout stores pending `Payment` details.

## Validation

- `python manage.py test studybuddy.tests.OnlinePaymentInitiationTests -v 2 --keepdb`
- `python manage.py test studybuddy.tests.ChatFeatureTests studybuddy.tests.OnlinePaymentInitiationTests -v 2 --keepdb`
- `python manage.py test studybuddy.tests -v 2 --keepdb`
- `git diff --check -- backend\studybuddy\views.py backend\studybuddy\tests.py`

