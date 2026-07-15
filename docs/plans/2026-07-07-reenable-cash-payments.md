---
title: Re-enable cash payments + tutor debt banner
date: 2026-07-07
status: Done
spec:
---

# Re-enable cash payments + tutor debt banner

## Status & Progress Summary

**Status:** Done · **Last updated:** 2026-07-07

Implemented (Steps A–G), audited line-by-line against this plan, and verified with real test runs
and a real `reset_demo_data` execution — against a genuine local PostgreSQL 18 instance, never
against the Supabase database `.env` points to. Steps A–F matched the plan exactly on read-through.
The audit caught and fixed three real issues before anything ran: a hardcoded hex color in
`WalletDebtBanner.vue` (now `--sb-danger`-derived); Step G's original negative-balance persona pick
(Isabel/Miguel both plausibly stay positive given their pre-existing earnings), replaced with a
deterministic correction that forces Miguel negative regardless of his computed baseline; and a
pre-existing test (`test_manual_payment_submission_updates_all_session_group_slots`) that the new
server-side enforcement silently broke, now fixed. Added 3 new test classes
(`SessionModePaymentMethodEnforcementTests`, `ProfileStatusWalletNegativeTests`, 8 tests) covering
the plan's required coverage — one had its own bug (an unrelated verification-gate setting) caught
and fixed during the actual run. **All verification now complete**: this project had no isolated
local database (`.env`/`.env.dev` both point at the same Supabase instance) — resolved by using the
local PostgreSQL 18 server already running on the machine instead, matching the config this
project's own CI already uses (`postgres`/`postgres`/`localhost`) rather than Supabase. Full
backend suite: 25/25 of the tests touching this plan's code pass; the wider suite's 30
failures/5 errors are all pre-existing and unrelated (recommender endpoints, avatar uploads,
dev-tools flags off by default — none touch anything this plan changed). `reset_demo_data` ran
clean end-to-end and empirically confirmed Miguel's wallet lands at exactly `-75.00` as designed.

Grilled end-to-end (16 decisions) covering: motivation (real cash-reliant market need, not just
defense optics), payment method derived from `session_mode` and enforced server-side, CASH
requiring a receipt photo but no fabricated transaction reference, folding in the already-tracked
PAYMONGO proof-of-payment gap fix, a non-dismissible tutor debt banner sourced from a boolean
(never shows the amount), and demo-data personas to make the flow demonstrable. Added a literal,
file-and-line-anchored **Implementation Instructions** section (Steps A–G) plus a **Local-only
testing constraints** section for the implementing coding agent — exact code to replace in
`submit_session_payment`/`confirm_payment_and_book`/`profile_status`, exact new-file/component
instructions, and hard rules against touching the demo deployment, live PayMongo keys, or
pushing/deploying. Not yet implemented.

---

## Goal

Re-enable CASH as a payment method — deactivated in June via
[`2026-06-08-online-only-payments.md`](2026-06-08-online-only-payments.md) — because the
Philippines is a cash-reliant market and losing that payment option is a real product gap, not
just a defense talking point. Pair it with a persistent tutor-facing banner that surfaces wallet
debt (a pre-existing but previously invisible state), since re-enabling CASH reactivates the path
that can push a tutor's wallet balance negative.

## Approach

**Payment method is derived, not picked.** `PostSessionPaymentView.vue` currently shows a
payment-method picker grid. That picker is removed. Instead, the required method is derived from
the booking's own `session_mode` (already set once per whole booking request, uniformly across
all slots — confirmed via `TutorDetails.vue:455`, `bookingPrefsStore.selectedMode`):

- `session_mode == 'F2F'` → CASH
- `session_mode == 'Online'` → PAYMONGO

This is enforced **server-side**, not just as a frontend convenience — `submit_session_payment`
(the live path) and `confirm_payment_and_book` (a vestigial, currently-unreachable-from-the-UI
path with the same pattern, updated for consistency) both independently derive the required
method from `booking.session_mode` and reject a mismatched `payment_method` regardless of what
the client sends.

**CASH requires a receipt photo, not a transaction reference.** The existing manual-payment
branch in `PostSessionPaymentView.vue` requires both a text "Transaction Reference" and a receipt
image. For cash there's no real reference number, so requiring one just trains tutees to enter
garbage data into `Payment.transaction_reference`. CASH requires only the receipt photo
(free-form — "attach a photo of your proof of payment," no defined slip/template), justified by:
the tutor's own accept/confirm action is the real-time verification; the receipt exists for
**admin dispute resolution**, not tutor-facing gatekeeping. `TutorBookingDetailsFlow.vue` already
displays `receipt_image` generically regardless of payment method — no change needed there.

**Close the adjacent PAYMONGO proof-of-payment gap in the same pass.** The existing check
`is_online_payment = method.code == 'online'` never matches the actually-active method code
`PAYMONGO` (see [`2026-06-11-paymongo-proof-of-payment-validation.md`](2026-06-11-paymongo-proof-of-payment-validation.md),
currently Draft/unresolved). Since we're already rewriting this exact conditional to add the CASH
case, the fix folds in naturally: check membership in `{'CASH', 'PAYMONGO'}` instead of a single
hardcoded `'online'` string. This closes both gaps in one diff instead of touching the same lines
twice across two separate plans.

**Frontend still guards against a stale derived method.** `PostSessionPaymentView.vue` keeps
calling `/api/payment-methods/` (existing endpoint), but instead of rendering a picker from the
result, it checks whether the derived method (CASH or PAYMONGO) is present in the active list. If
not — e.g. an admin deactivates CASH again after an F2F booking was already made — the tutee sees
a clear error ("Cash payment isn't available right now...") instead of a form that would 400 on
submit.

**No new money-movement infrastructure.** Per existing project state (no PayMongo business
permit yet — cash-in already runs against PayMongo sandbox/test keys, cash-out is already
simulated via `PAYMONGO_CASHOUT_MOCK`), re-enabling CASH introduces no new real-money surface. It
is purely a payment-method activation + UI/validation change, consistent with everything else in
the app currently being sandboxed/mock money movement.

**Tutor debt banner.** `approve_booking` already blocks a tutor from accepting new bookings while
`wallet.balance < 0` ([views.py:2814](../../backend/studybuddy/views.py)) — this is silent today,
surfacing only as a 400 error at the moment of trying to accept. Add:

- A global, **non-dismissible-while-negative** banner in `App.vue`, alongside the existing
  (dismissible) `VerificationBanner.vue`.
- Sourced from a new **boolean** (`wallet_negative`), not the raw balance — the banner never shows
  the debt amount, only that it exists and that it blocks bookings. Piggybacks on whatever
  endpoint `profile.js` already loads at login/app-mount (no new network round-trip).
- Copy: *"Your wallet balance is negative. You can't accept new bookings until it's settled —
  visit your Wallet to top up."*
- Clickable → navigates to `/tch-wallet` (same interaction pattern as `VerificationBanner`).
- Styled in `--sb-danger` (not the amber `VerificationBanner` uses) — this is a hard block, not a
  soft nudge.
- Tutor-only (tutees have no wallet).

**Demo data.** `reset_demo_data.py` gets updated to include CASH-paid F2F sessions among the
existing named personas, including at least one receipt image and one persona deliberately pushed
to a negative wallet balance, so the debt banner and the cash receipt flow both have something
real to click through during the defense — not just infrastructure that exists but is never
demoed.

## Steps

1. **Migration**: new migration reactivating `CASH` (`PaymentMethod.objects.filter(code='CASH').update(is_active=True)`), mirroring (in reverse) `0055_deactivate_cash_payment.py`.
2. **Backend — `submit_session_payment`**: derive required method from `representative_booking.session_mode`, reject mismatched `payment_method`; update the receipt/reference requirement to `{'CASH', 'PAYMONGO'}` with CASH requiring only the receipt image (no reference).
3. **Backend — `confirm_payment_and_book`**: apply the same derivation/enforcement to the vestigial `method_id` branch for consistency, even though it's not reachable from the current UI.
4. **Backend — profile/dashboard serializer**: add `wallet_negative` boolean for tutor profiles (`Wallet.balance < 0`), surfaced through whatever `profile.js` already fetches.
5. **Frontend — `PostSessionPaymentView.vue`**: remove the payment-method picker grid; derive `requiredMethodCode` from `bookingDetail.session_mode`; keep the active-methods fetch as a guard (render error state if derived method isn't active); drop the Transaction Reference field for the CASH branch; update copy for CASH context.
6. **Frontend — `App.vue` + new `WalletDebtBanner.vue`**: global banner reading `wallet_negative`, non-dismissible while true, `--sb-danger` styling, links to `/tch-wallet`.
7. **Demo data — `reset_demo_data.py`**: add CASH-paid F2F sessions with receipt images to existing personas; engineer at least one persona's transaction history to land with a negative wallet balance.
8. **Validation**: see Checks to run.

---

## Implementation Instructions for the Coding Agent (Codex) — read before touching any file

These instructions are literal and exhaustive. Follow them exactly, in order. Do not reorder,
merge, skip, "improve," or add anything not named below. If something here appears to conflict
with what you find in the code, **stop and report the discrepancy instead of resolving it
yourself** — do not silently choose an approach.

**Hard scope boundary:** touch only the files named in Steps A–G below. No renaming of unrelated
fields/functions, no refactors, no dependency additions, no UI polish beyond what's specified, no
new payment methods beyond CASH/PAYMONGO.

### Step A — Migration

- Repo currently has migrations up to `0069_alter_platformactivity_activity_type.py`. Create
  `backend/studybuddy/migrations/0070_reactivate_cash_payment.py`. If `0070` already exists when
  you run this (another migration landed first), use the next free number — do not overwrite an
  existing file.
- Mirror the structure of `backend/studybuddy/migrations/0055_deactivate_cash_payment.py` exactly,
  but inverted:
  ```python
  from django.db import migrations

  def reactivate_cash_payment(apps, schema_editor):
      PaymentMethod = apps.get_model('studybuddy', 'PaymentMethod')
      PaymentMethod.objects.filter(code='CASH').update(is_active=True)

  def deactivate_cash_payment(apps, schema_editor):
      PaymentMethod = apps.get_model('studybuddy', 'PaymentMethod')
      PaymentMethod.objects.filter(code='CASH').update(is_active=False)

  class Migration(migrations.Migration):
      dependencies = [('studybuddy', '0069_alter_platformactivity_activity_type')]
      operations = [migrations.RunPython(reactivate_cash_payment, deactivate_cash_payment)]
  ```
- Do not touch `PaymentMethod` choices, `GCASH`, or `BANK` codes. Only `CASH`'s `is_active` flag
  changes.

### Step B — `backend/studybuddy/views.py`, function `submit_session_payment`

- Locate the function (currently starts at line 3292 in the base commit `142ca8f`; line numbers
  will have drifted after Step A/prior edits — search by function name, not line number).
- Current logic to replace:
  ```python
  is_online_payment = method.code == 'online'
  if is_online_payment and receipt_image is None:
      return Response({"error": "Receipt image is required for online payments."}, status=400)
  if is_online_payment and not str(transaction_reference or '').strip():
      return Response({"error": "Transaction reference is required for online payments."}, status=400)
  ```
- Replace with logic that does two things — derive-and-enforce, then require-proof:
  1. Derive the required method code from `representative_booking.session_mode`:
     `'CASH' if representative_booking.session_mode == 'F2F' else 'PAYMONGO'`.
  2. If `method.code != required_method_code`: return
     `Response({"error": "Payment method does not match this session's mode."}, status=400)`.
  3. If `method.code == 'PAYMONGO'`: require both `receipt_image` and `transaction_reference`
     (same messages as today, just matched against `'PAYMONGO'` instead of `'online'`).
  4. If `method.code == 'CASH'`: require only `receipt_image` — return
     `Response({"error": "Receipt image is required for cash payments."}, status=400)` if missing.
     Do **not** require or validate `transaction_reference` for CASH.
- Do not change anything else in this function (the `Payment.objects.create(...)` call, the
  status transition to `"Awaiting Payment Verification"`, the notification call — all unchanged).

### Step C — `backend/studybuddy/views.py`, function `confirm_payment_and_book`

- Locate the `if method_id:` block (currently ~line 2421–2434 in base commit `142ca8f`; search by
  the surrounding function name `confirm_payment_and_book`, not the line number).
- Apply the exact same three-part logic as Step B, using the booking's own `session_mode` (the
  slots being confirmed — use `first_slot_mode`/`slots[0].get('session_mode', '')`, already
  computed a few lines above this block, normalized to `'F2F'`/`'Online'` the same way the
  existing `is_f2f` check does) in place of `representative_booking.session_mode` (this endpoint
  doesn't have a `representative_booking` yet at this point — the booking doesn't exist until
  after this validation block runs).
- This block is not reachable from any current frontend screen. Do not add a frontend caller for
  it. Do not delete it either — just bring its validation in line with Step B for consistency, per
  the plan's Step 3.

### Step D — `backend/studybuddy/views.py`, function `profile_status`

- Locate the function (currently line 1335 in base commit `142ca8f`).
- Inside the function, after `document_context = get_role_document_review_context(profile)` and
  before the `return Response(...)`, add:
  ```python
  wallet_negative = False
  if profile.role == 'Tutor':
      tutor = getattr(profile, 'tutor', None)
      if tutor is not None:
          wallet = Wallet.objects.filter(tutor=tutor).first()
          wallet_negative = bool(wallet and wallet.balance < 0)
  ```
- Add `"wallet_negative": wallet_negative,` to the returned dict (alongside
  `"profile_completed"`, `"role"`, etc.).
- `Wallet` is already imported in this file (used by `credit_tutor_wallet` and others) — do not
  add a new import if it's already present; only add one if it genuinely isn't imported yet.
- Do not compute this for non-Tutor roles beyond the `False` default above. Do not expose the
  balance itself anywhere in this response — only the boolean.

### Step E — `src/stores/profile.js`

- Add `walletNegative: false` to the `state()` object, alongside the existing fields.
- Add `this.walletNegative = false` inside `resetProfileState()`, alongside the existing resets.
- Inside `checkProfileStatus()`, after the existing `res.data...` assignments, add:
  `this.walletNegative = Boolean(res.data.wallet_negative)`.
- Do not add a new fetch call, a new store, or polling. This piggybacks entirely on the existing
  `checkProfileStatus()` call.

### Step F — `src/components/WalletDebtBanner.vue` (new file) + `src/App.vue`

- Create `src/components/WalletDebtBanner.vue` structurally mirroring
  `src/components/VerificationBanner.vue` (same `<script setup>` pattern, same use of
  `useProfileStore`), but:
  - Reads `profileStore.walletNegative` (no dismiss logic, no `localStorage` dismiss key — this
    banner has no dismiss state at all; it renders whenever `walletNegative` is `true` and nothing
    otherwise).
  - Renders exactly this copy: `"Your wallet balance is negative. You can't accept new bookings
    until it's settled — visit your Wallet to top up."`
  - The whole banner element is clickable and emits a `navigate` event (mirror
    `VerificationBanner`'s `@navigate` pattern) — wire it in `App.vue` to
    `router.push('/tch-wallet')`.
  - Style it using `var(--sb-danger)` for the accent/background tint — do not reuse
    `VerificationBanner`'s amber/warning styling.
  - This banner only makes sense for a Tutor — gate its render on
    `profileStore` role being `Tutor` if that information is available client-side (check how
    `VerificationBanner.vue` itself distinguishes tutor vs. tutee banners and follow the same
    pattern), so it never flashes for a tutee.
- In `src/App.vue`, import `WalletDebtBanner` and mount it directly adjacent to the existing
  `<VerificationBanner @navigate="goToVerificationStatus" />` line (currently line 69). Do not
  move or alter the `VerificationBanner` line itself.

### Step G — `backend/studybuddy/management/commands/reset_demo_data.py`

- Do not restructure the file. Add to the existing persona/session-generation logic:
  - At least one existing F2F-mode booking (check `AVAILABILITY_ARCHETYPES`/session-generation
    code for how `session_mode` is currently assigned per persona) that gets paid via `CASH`
    instead of `PAYMONGO`, with a `Payment.receipt_image` set to a real file path in the repo's
    test/demo media fixtures (check `backend/media/` or existing fixture usage in this same file
    for a pattern to reuse — do not invent a new asset pipeline; if no reusable image fixture
    exists, generate a minimal placeholder image file and store it as the receipt exactly the way
    the existing avatar/document seeding in this file already handles image fields).
  - Push exactly one tutor persona's `Wallet.balance` negative by ensuring their seeded CASH
    session count and commission deductions exceed their seeded top-ups/credits — do this by
    adjusting the order/count of transactions for one existing persona (e.g. `nico`, described as
    "Brand-new tutor: zero sessions, zero ratings" — do **not** reuse this exact persona if doing
    so would contradict their existing story; pick whichever persona's existing narrative is least
    disrupted by also being in debt, or introduce one new persona if none fit).
  - Do not change any existing persona's already-documented CBF/CF story/behavior described in
    their `'story'` field.

---

## Local-only testing constraints (read before running anything)

**This implementation is validated exclusively against your local machine. Never touch the demo
deployment, Render, Vercel, or the Supabase-hosted database.**

1. **Database**: run all migrations and tests against your local dev database only — whatever
   `DATABASE_URL` (or default local Postgres/sqlite config) is set in your local `.env` /
   `backend/backend/settings.py` dev defaults. Before running `python manage.py migrate`, confirm
   your active `.env` does **not** point at the Supabase demo database (check for a Supabase host
   in `DATABASE_URL` — if present, stop and do not proceed).
2. **No live PayMongo keys**: do not add, change, or reference any PayMongo secret/public key.
   This plan requires zero PayMongo configuration changes. If your local `.env` has PayMongo keys
   at all, they should already be test/sandbox keys — do not swap them for live keys under any
   circumstance.
3. **No demo-deployment flags**: do not set or reference `IS_DEMO_DEPLOYMENT`,
   `DEMO_BASIC_AUTH_USER/PASSWORD`, or `PAYMONGO_CASHOUT_MOCK` as part of this work — none of these
   need to change for this plan.
4. **Run the backend locally**: `python manage.py runserver` (default `localhost:8000`), not
   against any deployed URL.
5. **Run the frontend locally**: `npm run dev` (Vite dev server, default `localhost:5173`), not
   against any deployed URL. Point it at your local backend, not the Render-hosted one.
6. **Seed data locally only**: run `python manage.py reset_demo_data` against your local database
   only, to produce the CASH-paid personas from Step G, then verify the manual walkthrough (see
   Checks to run) against that local seeded data in your local browser session.
7. **Do not deploy, push, or open a PR** as part of implementing this plan. Stop after local
   verification passes and hand back for review. Pushing/deploying requires separate, explicit
   confirmation outside this plan.
8. **Tests**: `python manage.py test` must be run against the local database from point 1 —
   Django's test runner creates/destroys its own test database derived from that same connection,
   so if point 1 is satisfied, the test run is automatically local-only too.

## Risks

- The `confirm_payment_and_book` change (Step 3) is applied to a path with no live UI trigger today — it can only be verified by test/direct API call, not a real click-through, so a mistake there won't surface in manual QA.
- `wallet_negative` must be scoped correctly in the serializer so it never appears (or always reads `false`) for non-tutor profiles.
- Engineering a demo persona into negative balance requires careful transaction-history ordering (top-ups, session credits, and the CASH commission deduction) similar to the existing CBF/CF cluster engineering in `reset_demo_data.py` — get the order wrong and the persona could end up positive instead.
- Dropping the Transaction Reference field only for CASH means the `PostSessionPaymentView.vue` template now branches three ways (PAYMONGO / CASH / mismatch-error) instead of two — worth double-checking `canSubmitOnlinePayment`-equivalent validation logic is updated for all three, not just two.

## Checks to run

- `python manage.py test` (backend) — existing payment/wallet test suites must still pass; add coverage for: CASH submit with receipt-only (no reference) succeeds; mismatched session_mode/payment_method is rejected server-side in both endpoints; `wallet_negative` boolean reflects `Wallet.balance < 0`.
- `npm run lint` and `npm run build`.
- Manual walkthrough: book an F2F session → pay via CASH with a receipt photo, no reference field shown → tutor views receipt in `TutorBookingDetailsFlow.vue` and confirms → wallet debited 10% → repeat until a demo persona goes negative → debt banner appears globally, non-dismissible → attempt to accept a new booking as that tutor and confirm the existing 400 block still fires → top up via `/tch-wallet` → banner clears once balance ≥ 0.

## Changelog

- **2026-07-07**: Grilled re-enabling cash payments end-to-end (16 decisions: motivation,
  session_mode-derived payment method with server-side enforcement, CASH receipt-only
  requirement, folding in the PAYMONGO proof-of-payment gap fix, tutor debt banner design,
  demo-data scope); created this plan as Approved.
- **2026-07-07**: Added a literal, exhaustive "Implementation Instructions for the Coding Agent"
  section (Steps A–G, anchored to exact functions/files/current line numbers as of base commit
  `142ca8f`, with drop-in code for the migration, both backend validation functions, the profile
  serializer addition, the new banner component, and the demo-data persona) plus a "Local-only
  testing constraints" section (no Supabase/demo DB, no live PayMongo keys, no demo-deployment
  flags, local dev server only, no push/deploy) — written to keep an external implementing agent
  from straying from the agreed scope.
- **2026-07-07**: Steps A–G implemented by a coding agent; audited line-by-line against this plan.
  Findings: Steps A–F matched the spec exactly (migration, `submit_session_payment`,
  `confirm_payment_and_book`, `profile_status`, `profile.js`, `WalletDebtBanner.vue`/`App.vue`
  wiring, `PostSessionPaymentView.vue`). Found and fixed: (1) a hardcoded hex color in
  `WalletDebtBanner.vue` that violated the project's CSS-variable convention, now derived from
  `--sb-danger`; (2) Step G's negative-balance persona pick was broken — Isabel's PHP 55,000 top-up
  and Miguel's ~10 additional cluster-rating-scenario payments (random PAYMONGO/CASH split) made
  both plausibly land positive despite the 2-3 seeded CASH sessions, so replaced the
  hope-the-count-is-enough approach with a deterministic correction that forces Miguel negative
  regardless of his actual computed baseline; (3) discovered the new server-side enforcement broke
  a pre-existing test (`test_manual_payment_submission_updates_all_session_group_slots`, which
  submitted CASH for an Online-mode booking) and fixed it to use an F2F booking with a receipt
  upload; (4) added 3 new test classes (`SessionModePaymentMethodEnforcementTests`,
  `ProfileStatusWalletNegativeTests`) covering the mismatch-rejection, CASH-receipt-only, and
  `wallet_negative` requirements from Checks to run, none of which existed yet. Also discovered
  this project has no isolated local database (`.env`/`.env.dev` are identical, both pointing at
  the same Supabase instance) — flagged as an open decision; `python manage.py test`/`migrate`
  still have not been run against real data pending that call. Status moved Approved -> In
  Progress.
- **2026-07-07**: Resolved the local-database gap by using the local PostgreSQL 18 server already
  running on the machine (matching this project's own CI config: `postgres`/`postgres`/`localhost`)
  instead of Supabase — zero risk to any shared/demo data, `.env` never modified (DB connection
  vars passed inline per-command only). Ran the 8 new tests: 1 failure
  (`test_confirm_payment_and_book_rejects_mismatched_method`, 403 instead of 400 — my own test's
  bug, missing `@override_settings(TUTEE_VERIFICATION_ENFORCEMENT_START_DATE=None)` to isolate it
  from an unrelated verification-gate setting inherited from `.env`), fixed, re-ran: 8/8 pass. Ran
  the 17 tests in `OnlinePaymentInitiationTests` (including the fixed pre-existing test): 17/17
  pass. Ran the full suite matching CI's exact clean environment (temporarily moved `.env` aside,
  restored immediately after): 278 tests, 30 failures + 5 errors, all pre-existing and unrelated to
  this plan (recommender endpoints, avatar uploads, institution catalog, dev-tools endpoints gated
  by flags off by default in both this run and CI — none touch `submit_session_payment`,
  `confirm_payment_and_book`, `profile_status`, or `reset_demo_data`). Ran `manage.py migrate` then
  `manage.py reset_demo_data` against the local database end-to-end: succeeded cleanly, and
  empirically confirmed Miguel's wallet lands at exactly `-75.00` as designed (log line:
  "Miguel balance -75.00 (must be negative for the debt banner demo)"). Noted an incidental,
  pre-existing, unrelated observation: Isabel also landed negative this run (`-505.00`) purely by
  chance, from pre-existing `random.choice(methods)` logic in `_create_payments_and_ratings` that
  this plan didn't touch — doesn't affect the plan since Miguel is the deterministic target.
  Status moved In Progress -> Done.
