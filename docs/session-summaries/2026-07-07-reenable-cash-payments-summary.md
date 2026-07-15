# Re-enable cash payments + tutor debt banner — Summary

**Plan:** [2026-07-07-reenable-cash-payments.md](../plans/2026-07-07-reenable-cash-payments.md)
**Status:** Done

## What shipped

- **CASH reactivated** as a `PaymentMethod` (migration `0070_reactivate_cash_payment.py`, reversing `0055`).
- **Payment method is derived from the booking's `session_mode`**, not user-picked — F2F → CASH, Online → PAYMONGO — enforced **server-side** in both `submit_session_payment` (live path) and `confirm_payment_and_book` (vestigial path, brought in line for consistency). A mismatched method is rejected with 400 regardless of what the client sends.
- **CASH requires a receipt photo only** — no fabricated transaction reference. `PostSessionPaymentView.vue`'s payment-method picker was removed; the screen now shows the correct form directly based on the derived method, with a guard against a stale/deactivated method.
- **Folded in the adjacent PAYMONGO proof-of-payment gap** (tracked separately since 2026-06-11) in the same pass — the validation now checks `{'CASH', 'PAYMONGO'}` instead of a dead `'online'` string.
- **New tutor debt banner** (`WalletDebtBanner.vue`): global, non-dismissible while `Wallet.balance < 0`, sourced from a new boolean-only `wallet_negative` field on `profile_status` (never exposes the amount), styled with `--sb-danger`, links to the Wallet page. Makes visible a block (`approve_booking`'s existing 400 on negative balance) that was previously silent.
- **Demo data**: `reset_demo_data.py` now seeds CASH-paid F2F sessions with receipt images, and deterministically forces one persona (Miguel) to a negative wallet balance so the debt banner is actually demoable.

## What the audit caught and fixed (before any of the above shipped as "done")

1. A hardcoded hex color in `WalletDebtBanner.vue` — now derived from `--sb-danger`.
2. Step G's original negative-balance persona pick was broken: Isabel's ₱55,000 top-up and Miguel's ~10 additional cluster-rating-scenario payments (random PAYMONGO/CASH split, pre-existing code) made both plausibly land positive despite the seeded CASH sessions. Replaced session-count guesswork with a deterministic correction that forces Miguel to exactly `-75.00` regardless of his actual computed baseline.
3. The new server-side enforcement silently broke a pre-existing test (`test_manual_payment_submission_updates_all_session_group_slots`, which submitted CASH for an Online-mode booking) — fixed to use an F2F booking with a receipt upload.
4. Added 3 new test classes (`SessionModePaymentMethodEnforcementTests`, `ProfileStatusWalletNegativeTests`, 8 tests) covering the plan's required coverage, none of which existed. One of these had its own bug during the real run (missing `@override_settings` to isolate an unrelated verification-gate setting) — found and fixed.

## Verification

This project had no isolated local database — `.env` and `.env.dev` both pointed at the same Supabase instance. Resolved by using the local PostgreSQL 18 server already running on the machine, matching this project's own CI config (`postgres`/`postgres`/`localhost`) rather than Supabase. `.env` was never modified; DB connection variables were passed inline per-command only.

- The 8 new tests: 8/8 pass (after fixing the one test bug found above).
- The 17 tests in the class containing the fixed pre-existing test: 17/17 pass.
- Full backend suite (matching CI's clean environment exactly): 278 tests, 30 failures + 5 errors — all pre-existing and unrelated to this plan (recommender endpoints, avatar uploads, institution catalog, dev-tools endpoints gated by flags off by default in both this run and CI). None touch `submit_session_payment`, `confirm_payment_and_book`, `profile_status`, or `reset_demo_data`.
- `manage.py migrate` then `manage.py reset_demo_data` ran end-to-end against the local database and empirically confirmed the log line: `Miguel balance -75.00 (must be negative for the debt banner demo)`.
- `npm run lint` and `npm run build`: clean (4 pre-existing lint errors in unrelated files).

## Deviations from the original plan

- The plan's "local-only testing constraints" section assumed a local database already existed for this project. It didn't — `.env`/`.env.dev` were identical, both pointing at Supabase. Resolved by setting up and using the local PostgreSQL 18 server already installed on the machine instead, which is also what this project's own CI already does.
- `reset_demo_data.py`'s seeded `PaymentMethod` code was renamed from `'online'` to `'PAYMONGO'` (not explicitly listed in Step G) — necessary, since the new derivation logic checks for `'PAYMONGO'` and the old seeded code would have left every online-mode demo session unable to find a matching active method.
