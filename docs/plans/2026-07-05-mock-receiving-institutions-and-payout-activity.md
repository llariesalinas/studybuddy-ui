---
title: Mock receiving institutions + auto-processed payout activity
date: 2026-07-05
status: Done
spec:
---

# Mock receiving institutions + auto-processed payout activity

## Status & Progress Summary

**Status: Done.** All steps implemented on `feat/demo-data-reset`: `MOCK_RECEIVING_INSTITUTIONS`
constant + mock branch in `list_receiving_institutions`, `withdrawal_processed` choice + migration
`0069`, `log_cash_out_activity` logging at the resolution chokepoint, and 2 new tests. The 3
mock-related cash-out tests pass; the 2 failures in `TutorCashOutTests` are pre-existing
(confirmed by stashing all changes and re-running against HEAD — provider-fee normalization and
callback-auth, both unrelated). See
[session summary](../session-summaries/2026-07-05-mock-receiving-institutions-and-payout-activity-summary.md).

## Goal

Let the full tutor cash-out flow run end-to-end in local dev / the thesis demo without touching
live PayMongo, and make an auto-processed payout visible in the admin activity feed.

Two gaps remain after the prior dev stub:

1. The prior plan mocked `create_wallet_transaction` (the payout call) but **not**
   `list_receiving_institutions` (the bank/e-wallet dropdown that loads *before* it). So the
   dropdown still hits live PayMongo and the tutor can't reach the cash-out button.
2. An auto-processed cash-out (real *or* mock) resolves straight to `processed` via `cash_outs`
   and never passes through `AdminWithdrawalDetailView`, so it writes **no** `PlatformActivity`.
   The payout is invisible in the admin activity feed.

## Approach

- **Reuse the existing `PAYMONGO_CASHOUT_MOCK` flag** — no new setting. Mirror the pattern already
  used in `create_wallet_transaction`: a mock branch at the top of `list_receiving_institutions`
  that returns hardcoded data before any `requests.get`.
- **Hardcoded institution list as a module constant** in `paymongo_money_movement.py`, next to
  `INSTAPAY_PROVIDER`. Dev-only demo data; a separate module is over-structuring for ~12 entries
  that get deleted once KYB-approved.
- **Realistic curated list (~12)** whose `name` values match keys in
  `src/data/receivingInstitutionLogos.js`, so logos render in the demo. PayMongo JSON:API shape
  (`{'data': [{'id', 'type': 'receiving_institution', 'attributes': {'name', 'code'}}]}`) so the
  frontend's `institutionAttributes`/`institutionName` readers (`TutorWallet.vue:483-491`) work
  unchanged.
- **Activity logging at the resolution chokepoint** `apply_cash_out_provider_result`
  (`views.py:4469`): log `withdrawal_processed` on the `succeeded` branch and `withdrawal_failed`
  on the `failed` branch, with `institution=withdrawal.tutor.profile.institution`. One chokepoint
  covers sync mock, sync live, and the async callback path.
- **Declare the `withdrawal_processed` choice** in `PlatformActivity.ACTIVITY_TYPES`. The admin
  path (`admin_views.py:359`) already writes this value even though it isn't declared; adding it
  closes that latent gap and reuses one value across both call sites.
- **Keep it minimal — this is a mock.** In mock mode the payout always succeeds synchronously; no
  callbacks fire. Deliberately **not** in scope: an idempotency guard on
  `apply_cash_out_provider_result` for the (real-only, async) double-callback double-log race.
  Cosmetic and impossible in mock mode.

## Steps

1. **Institution constant** (`backend/studybuddy/paymongo_money_movement.py`): add a module-level
   `MOCK_RECEIVING_INSTITUTIONS` (~12 entries: GCash, Maya, BDO Unibank, BPI, Metrobank, Landbank,
   PNB, RCBC, Security Bank, Chinabank, UnionBank, EastWest) as a `{'data': [...]}` payload in
   PayMongo JSON:API shape. Names must match `receivingInstitutionLogos.js` keys.
2. **Mock branch** (`list_receiving_institutions`): at the top, if
   `getattr(settings, 'PAYMONGO_CASHOUT_MOCK', False)`, return `MOCK_RECEIVING_INSTITUTIONS`
   before any `requests.get`. Mirror the `create_wallet_transaction` mock branch style.
3. **Model choice** (`backend/studybuddy/models.py`): add
   `('withdrawal_processed', 'Withdrawal Processed')` to `PlatformActivity.ACTIVITY_TYPES`.
   Generate the (trivial, no-data) migration.
4. **Activity logging** (`backend/studybuddy/views.py`, `apply_cash_out_provider_result`): on the
   `processed` branch create a `PlatformActivity(activity_type='withdrawal_processed', ...)`; on
   the `failed` branch create `activity_type='withdrawal_failed'`. Use
   `withdrawal.tutor.profile.institution` and a short message including the withdrawal id and tutor
   name. Do not log on the non-terminal (`pending`/`processing`) case.
5. **Tests** (`backend/studybuddy/tests.py`):
   - With `PAYMONGO_CASHOUT_MOCK=True`, `list_receiving_institutions` returns the fake list and
     makes no outbound HTTP (patch/assert `requests.get` not called).
   - An auto-processed cash-out writes exactly one `PlatformActivity` with
     `activity_type='withdrawal_processed'` scoped to the tutor's institution.
6. **Manual check**: `PAYMONGO_CASHOUT_MOCK=true`, restart backend, open the cash-out form →
   dropdown populates with logos, submit → withdrawal `processed`, and the entry appears in the
   admin activity feed.

## Risks

- **Name mismatch → missing logos.** If a mock institution `name` doesn't match a
  `receivingInstitutionLogos.js` key, it silently falls back to the generic icon. Mitigate by
  copying names verbatim from that file.
- **Shape drift.** The mock `data` items must match what `receiving_institutions` view returns
  (`provider_response.get('data', ...)`) and what the frontend reads. Locked by the step-5 test
  and by copying the JSON:API shape.
- **Prod leakage** (inherited): `PAYMONGO_CASHOUT_MOCK=true` in production would fake payouts and
  now also write feed entries. Already mitigated by default-off + the DEBUG-false warning from the
  prior plan.
- **Double-log on real async callback** (out of scope): a real sync-failure-then-callback could
  write two feed entries. Impossible in mock mode; deferred.

## Checks to run

- `cd backend && python manage.py makemigrations studybuddy` — one migration for the new choice,
  no data operations.
- `cd backend && python manage.py test studybuddy.tests.TutorCashOutTests studybuddy.tests.WalletCashOutEdgeCaseTests --keepdb` — all pass, including the two new tests.
- Manual (step 6) — dropdown populates with logos, cash-out reaches `processed`, activity feed
  shows the entry.
- `npm run build` — passes (no frontend changes, confirms nothing regressed).

## Changelog

- 2026-07-05: Plan created and approved after a grilling session. Scope: mock
  `list_receiving_institutions` under the existing `PAYMONGO_CASHOUT_MOCK` flag (curated ~12
  logo-matched institutions), plus activity-feed logging for auto-processed/failed cash-outs and a
  declared `withdrawal_processed` choice. Explicitly excluded an idempotency refactor as out of
  scope for a mock.
- 2026-07-05: Implemented all steps and marked Done. Added `MOCK_RECEIVING_INSTITUTIONS` + mock
  branch, the `withdrawal_processed` choice (migration `0069`), `log_cash_out_activity` at the
  resolution chokepoint, and 2 tests. 3 mock cash-out tests pass; verified the 2 remaining
  `TutorCashOutTests` failures are pre-existing (stashed all changes, re-ran against HEAD, both
  still failed). Wrote session summary.
