# Build 03: PayMongo Dashboard Reference

## Summary

Improved PayMongo test dashboard traceability by adding a StudyBuddy booking reference to the actual PayMongo checkout payload.

## Changes

- Added a generated reference code: `SB-BK-<booking id>`.
- Added the reference to the PayMongo checkout description.
- Added the reference to the line item name.
- Added the reference to the line item description.

## Test Cases

- Checkout payload includes the `SB-BK-<booking id>` reference.
- Checkout line item name is `StudyBuddy SB-BK-<booking id>`.
- Existing PayMongo initiation tests still pass.

## Validation

- `python manage.py test studybuddy.tests.OnlinePaymentInitiationTests -v 2 --keepdb`
- `git diff --check -- backend\studybuddy\views.py backend\studybuddy\tests.py`

## Manual Validation

- Create a PayMongo test checkout.
- Open the PayMongo test dashboard using the same `sk_test_...` account.
- Search or inspect checkout/payment records for `SB-BK-<booking id>`.

