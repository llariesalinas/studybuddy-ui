---
title: Cash-Out Recent Transactions (Remove Standalone Destinations)
date: 2026-06-29
status: Done
spec: ../specs/2026-06-29-cashout-recent-transactions.md
---

# Cash-Out Recent Transactions Implementation Plan

> **For agentic workers:** Use superpowers:subagent-driven-development to execute task-by-task.

## Status & Progress Summary

**Status:** Done — all 8 tasks implemented, reviewed, and verified.
**Tasks complete:** 8 / 8
**Next:** None. See
[summary](../session-summaries/2026-06-29-cashout-recent-transactions-summary.md) for fixes found
during review (institution-id missing from the match check, bank_name validation/auto-fill, three
extra cleanups in Task 7) and manual-verification results.

## Goal

Collapse "add a payout destination" and "cash out" into one inline cash-out form that surfaces
the tutor's last 4 withdrawals as reusable shortcuts, per
[the spec](../specs/2026-06-29-cashout-recent-transactions.md), without touching the
InstaPay-only cap, fee logic, or institutions catalog.

**Stack:** Vue 3 (Composition API), Pinia, Django REST, Bootstrap 5

## Approach

Build additively, then remove the old destination concept once nothing depends on it:

1. Add the new backend surface (recent-transactions endpoint, inline-fields cash-out contract)
   alongside the existing destination endpoints so the app keeps working mid-build.
2. Switch the frontend (store + `TutorWallet.vue` cash-out modal) onto the new contract and
   remove the standalone Destinations UI.
3. Remove the now-unused destination endpoints, serializer, and `TutorPayoutAccount` model last,
   via its own migration task — kept separate and called out explicitly per the spec's
   destructive-migration caveat.

**Resolved ambiguity — how the "new-destination confirmation" is enforced:** the spec describes
the behavior (confirm before sending to an unrecognized destination) but doesn't say whether the
match check lives client-side or server-side. Backend-enforced is chosen because the spec's
Testing Decisions ask for an *API-level* test of "requires/triggers the confirmation path before
the withdrawal is created" — that's only testable at the API boundary if the API itself enforces
it. Contract: `POST /api/wallet/cash-outs/` gains an optional `confirm_new_destination: bool`
(default `false`). The view computes whether the submitted destination fields
(`destination_type`, `receiving_institution_id`, `account_number`, `account_name`) exactly match
any of the tutor's last 4 `WithdrawalRequest` rows. If there's no match and
`confirm_new_destination` is not `true`, return `409` with
`{"error": "new_destination_confirmation_required"}` and create nothing. Otherwise proceed as
today. The frontend always has the same last-4 list (it fetched it for the shortcuts), runs the
same match client-side first to decide whether to show the confirm step, and only sends
`confirm_new_destination: true` after the tutor confirms — so the common (matching) case never
sees the extra round trip's 409.

**Endpoint for recent transactions:** new `GET /api/wallet/cash-outs/recent/`, registered before
`wallet/cash-outs/<id>/`-style patterns aren't needed since none exist today — `cash_outs` has no
existing id-suffixed route, so `recent/` is unambiguous as a new sibling path. Reuses
`serialize_cash_out`.

## Tasks

### Task 1: Backend — recent cash-outs endpoint

**Files:**
- Modify: `backend/studybuddy/views.py`
- Modify: `backend/studybuddy/urls.py`

- [ ] Add `recent_cash_outs(request)` view near `cash_outs()` in `views.py`: get tutor via
      `get_request_tutor(request)` (404 if none), query
      `WithdrawalRequest.objects.filter(tutor=tutor).order_by('-requested_at')[:4]`, return
      `Response([serialize_cash_out(w) for w in qs])`. No status filtering, no dedup, per spec.
- [ ] Add `path('wallet/cash-outs/recent/', views.recent_cash_outs)` to `urlpatterns` in
      `urls.py`, placed above `path('wallet/cash-outs/', views.cash_outs)` so Django's
      first-match routing can't shadow it (Django matches in declaration order; `recent/` is a
      distinct literal path so order doesn't actually matter here, but keep it above for
      readability).
- [ ] Verify: `python manage.py check` passes with no errors.
- [ ] Commit — `git commit -m "feat: add recent cash-outs endpoint"`

### Task 2: Backend — inline destination fields + new-destination confirmation on cash-out

**Files:**
- Modify: `backend/studybuddy/views.py` (`cash_outs`)

- [ ] Change the POST branch of `cash_outs()` to read destination fields directly from the
      request body instead of resolving `payout_account_id`:
      `destination_type`, `receiving_institution_id`, `receiving_institution_name`,
      `receiving_institution_code` (optional), `account_number`, `account_name`, `bank_name`
      (optional), plus existing `amount` and a new optional `note`.
- [ ] Validate required fields present (`destination_type` in `('gcash', 'bank')`,
      `account_number`, `account_name`, `receiving_institution_id`/`name`) — 400 with a clear
      message if missing, following the existing validation-message style in this view.
- [ ] Add the match check: fetch the tutor's last 4 `WithdrawalRequest` rows, compare
      `(destination_type/method, receiving_institution_id, account_number, account_name)`
      against the submitted fields. If no row matches and
      `request.data.get('confirm_new_destination') is not True`, return
      `Response({"error": "new_destination_confirmation_required"}, status=409)` without
      creating anything.
- [ ] Keep all existing amount/balance/cap validation (`get_cashout_minimum`,
      `get_cashout_maximum`, balance check) unchanged.
- [ ] Build the `WithdrawalRequest` directly from the submitted fields (method=destination_type,
      account_number, account_name, bank_name) instead of from a `payout_account` lookup; stop
      setting `payout_account` on the new row. Store `note` on the existing free-text field if
      one already fits (check `description`/similar on `Transaction`, not `WithdrawalRequest` —
      if `WithdrawalRequest` has no note-shaped field, add `note = models.TextField(blank=True,
      default='')` via a small additive migration in this task).
- [ ] Update `serialize_cash_out()` to include `note` in its output.
- [ ] Verify: `python manage.py check` passes; manually trace one happy-path request mentally
      against the diff (no test run yet — Task 3 adds the tests for this).
- [ ] Commit — `git commit -m "feat: accept inline destination fields and new-destination confirmation on cash-out"`

### Task 3: Backend — tests

**Files:**
- Modify: `backend/studybuddy/tests.py`

Extend `TutorCashOutTests` and `WalletCashOutEdgeCaseTests` (do not create a new test class —
this is the existing highest seam per the spec's Testing Decisions).

- [ ] Update existing tests in both classes that build requests via `create_account()` +
      `payout_account_id` to instead POST inline destination fields directly, since the old
      contract no longer exists after Task 2. Keep their original assertions (balance/fee
      deduction, provider mocking, etc.) intact — only the request-construction changes.
- [ ] Add `test_cashout_with_inline_destination_fields_succeeds`: POST with inline fields (no
      `payout_account_id`), assert 201/200, assert wallet balance deducted by amount+fee as
      before, assert the created `WithdrawalRequest` stores the submitted destination fields.
- [ ] Add `test_recent_cash_outs_returns_last_four_most_recent_first`: create 6 withdrawals
      (mix of statuses), GET `/api/wallet/cash-outs/recent/`, assert exactly 4 returned, ordered
      most-recent-first, no status filtering applied.
- [ ] Add `test_cashout_new_destination_requires_confirmation`: create one prior withdrawal to a
      known destination, POST a cash-out with *different* destination fields and no
      `confirm_new_destination` — assert 409, assert no new `WithdrawalRequest` row was created.
      Then retry the same payload with `confirm_new_destination: true` — assert success.
- [ ] Add `test_cashout_matching_recent_destination_skips_confirmation`: POST a cash-out whose
      destination fields exactly match a prior withdrawal, with no `confirm_new_destination` —
      assert success (no 409).
- [ ] Add `test_payout_destinations_endpoints_removed`: GET/POST
      `/api/wallet/payout-destinations/` return 404. (This test will only pass after Task 7
      removes the routes — write it now, expect it to fail/be skipped until then, or add it in
      Task 7 instead if that reads cleaner; note in the task either way.)
- [ ] Run: `python manage.py test studybuddy.tests.TutorCashOutTests studybuddy.tests.WalletCashOutEdgeCaseTests` —
      all pass except the not-yet-applicable removal test (see above).
- [ ] Commit — `git commit -m "test: cover inline cash-out fields, recent transactions, and new-destination confirmation"`

### Task 4: Frontend — wallet store onto the new contract

**Files:**
- Modify: `src/stores/wallet.js`

- [ ] Add `recentCashOuts` state (array) and `fetchRecentCashOuts()` action: GET
      `/api/wallet/cash-outs/recent/` via `src/services/api/api.js`, set `recentCashOuts`.
- [ ] Change `requestWithdrawal(payload)` to send the new body shape: `{amount, destination_type,
      receiving_institution_id, receiving_institution_name, receiving_institution_code,
      account_number, account_name, bank_name, note, confirm_new_destination}` instead of
      `{amount, payout_account_id}`. Let it propagate the 409
      (`new_destination_confirmation_required`) response as-is — the caller (modal component)
      decides what to do with it.
- [ ] Remove `payoutAccounts` state and the `fetchPayoutAccounts`, `savePayoutAccount`,
      `deactivatePayoutAccount` actions — nothing will reference them after Task 5.
- [ ] Verify: `npm run lint` passes (catches now-unused imports/exports if any).
- [ ] Commit — `git commit -m "feat: switch wallet store to inline cash-out fields and recent transactions"`

### Task 5: Frontend — rebuild the cash-out modal, remove the Destinations UI

**Files:**
- Modify: `src/views/TutorWallet.vue`

This is the largest task — keep it focused on this one view file.

- [ ] Remove the Destinations section/card (existing lines ~143-205: list, logos, status pills,
      "Add New Destination" button, deactivate action) and the entire Add Destination modal
      (existing lines ~274-332). No replacement management surface, per spec.
- [ ] Rebuild the cash-out modal (existing lines ~334-405) as the single form: destination type
      (GCash/Bank) inline, receiving institution picker (reuse the existing `SbSelectModal`
      pattern + `getReceivingInstitutionLogoUrl()` that the old Add Destination modal used —
      same catalog store, same logos), account number, account name, bank name (shown only when
      destination type is `bank`), amount, optional note — all always editable.
- [ ] On modal open, call `walletStore.fetchRecentCashOuts()`. Render the last 4 as tappable
      shortcut chips/cards (institution name + masked account number + date) above the form.
- [ ] Selecting a shortcut copies `destination_type`, `receiving_institution_id/name/code`,
      `account_number`, `account_name` into the form fields. Leave `amount` and `note` blank.
      Every field stays editable afterward (no read-only state introduced).
- [ ] Before submit: compute the same match-against-recent-4 check client-side (same fields as
      the backend check in Task 2) using `walletStore.recentCashOuts`. If no match, show a
      confirmation step (inline summary of destination + amount, "Confirm & Send" /
      "Edit" actions) before calling `requestWithdrawal` with `confirm_new_destination: true`.
      If it matches, submit directly without the extra step.
- [ ] Handle the (should-be-rare, race-condition) case where the backend still returns 409 after
      a client-side "matches" verdict — surface the same confirmation step rather than a raw
      error, then resubmit with `confirm_new_destination: true` on confirm.
- [ ] Keep all existing min/max/fee/balance validation and summary display (existing
      `cashoutError`, `cashoutProviderFee`, cap messaging) unchanged — this feature doesn't touch
      that logic.
- [ ] Verify: `npm run lint` and `npm run build` both pass.
- [ ] Commit — `git commit -m "feat: collapse cash-out destination entry into the cash-out modal"`

### Task 6: Manual verification pass (no new frontend automated test, per spec)

**Files:** none — verification only, using `mcp__Claude_Preview__*` tools per project workflow.

- [ ] Start the dev server (frontend) and Django dev server (backend) if not already running.
- [ ] As a seeded tutor with no prior withdrawals: open the cash-out modal, confirm it shows a
      blank form with no recent-transaction shortcuts, and a cash-out completes (mock/sandbox
      provider) without any destination-confirmation step (first-time has nothing to mismatch
      against, depends on Task 2's logic for "no recent rows" — confirm it doesn't false-trigger
      confirmation when there's simply no history; adjust Task 2's match logic to treat "no
      recent transactions at all" as needing-no-confirmation if it doesn't already, since there's
      nothing to confirm against).
- [ ] As a seeded tutor with prior withdrawals: open the modal, confirm the last 4 show as
      shortcuts most-recent-first, tap one, confirm destination fields prefill and amount/note
      stay blank, confirm all fields remain editable, submit with matching fields and confirm no
      extra confirmation step appears.
- [ ] Same tutor: manually edit a prefilled account number to something not in history, submit,
      confirm the new-destination confirmation step appears before the request actually sends.
- [ ] Confirm the wallet view no longer shows any "Destinations" section anywhere.
- [ ] Confirm the ₱50,000 cap and fee display still work exactly as before (e.g. attempt
      ₱50,000.01, confirm rejection message unchanged).
- [ ] Report results (pass/fail per bullet) — do not mark this task done without having actually
      run the server and observed behavior.

### Task 7: Backend — remove destination endpoints, serializer, and model (destructive)

**Files:**
- Modify: `backend/studybuddy/views.py`
- Modify: `backend/studybuddy/urls.py`
- Modify: `backend/studybuddy/models.py`
- Create: `backend/studybuddy/migrations/00XX_remove_tutorpayoutaccount.py`

**Do not run this task's migration against any environment containing real tutor data without a
separate, explicit go/no-go from the user at execution time** — this matches the spec's
destructive-migration caveat. Running it against a local/dev/test database with only seeded or
test data is fine and expected as part of this task.

- [ ] Remove `payout_destinations()` view and `serialize_payout_account()` from `views.py`.
- [ ] Remove the two `wallet/payout-destinations/...` `path()` entries from `urls.py`.
- [ ] Remove the `payout_account` field from `WithdrawalRequest` and remove the
      `TutorPayoutAccount` model entirely from `models.py`.
- [ ] Generate the migration: `python manage.py makemigrations studybuddy -n
      remove_tutorpayoutaccount`. Confirm the generated migration drops the
      `WithdrawalRequest.payout_account` field and the `TutorPayoutAccount` table.
- [ ] If not already added in Task 3, add `test_payout_destinations_endpoints_removed`
      asserting 404 on the removed routes; if it was added in Task 3 as expected-failing, confirm
      it now passes.
- [ ] Confirm `python manage.py check` passes and no remaining code references
      `TutorPayoutAccount` or `payout_account` (`grep -rn "TutorPayoutAccount\|payout_account"
      backend/studybuddy --include=*.py` should only show the migration files).
- [ ] Run the migration locally: `python manage.py migrate`.
- [ ] Run the full backend cash-out test suite again to confirm nothing regressed:
      `python manage.py test studybuddy.tests.TutorCashOutTests studybuddy.tests.WalletCashOutEdgeCaseTests`.
- [ ] Commit — `git commit -m "chore: remove TutorPayoutAccount model and destination endpoints"`

### Task 8: Final checks and plan close-out

**Files:** `docs/plans/2026-06-29-cashout-recent-transactions.md`, `docs/plans/README.md`,
`docs/session-summaries/2026-06-29-cashout-recent-transactions-summary.md` (new)

- [ ] Run `npm run lint`, `npm run build`, `python manage.py test` (full suite) one more time at
      the tip of the branch — confirm all pass.
- [ ] Write the session summary covering what shipped vs. this plan, noting the
      `confirm_new_destination` contract as the one designed-not-specified decision.
- [ ] Update this plan's frontmatter `status` to `Done` and update the Status & Progress Summary
      section above.
- [ ] Add a row to `docs/plans/README.md` and a changelog entry.
- [ ] Regenerate `docs/plans/index.html` per the dashboard spec.

## Risks

- **`confirm_new_destination` contract is a plan-level design decision, not literally specified**
  in the PRD — flagged above; worth a quick confirmation from the user before Task 2 starts.
- **Destructive migration (Task 7)** — irreversible table drop; explicitly gated, see Task 7.
- **Existing tests construct requests via `payout_account_id`** — Task 2 breaks them until
  Task 3 updates them in the same work session; keep Tasks 2 and 3 close together, don't ship
  Task 2 alone.
- **First-time tutor (no withdrawal history) edge case** for the confirmation check — must not
  false-trigger "new destination" confirmation when there's simply no history to compare
  against; called out explicitly in Task 6.

## Checks to run

- `python manage.py test studybuddy.tests.TutorCashOutTests studybuddy.tests.WalletCashOutEdgeCaseTests`
- `python manage.py check`
- `npm run lint`
- `npm run build`
- Manual verification per Task 6

## Changelog

| Date | Change |
|------|--------|
| 2026-06-29 | Initial plan drafted from the spec, with code research from a direct Explore-agent pass (graphify graph was stale and skipped per user choice). 8 tasks: additive backend → frontend cutover → manual verification → destructive cleanup → close-out. |
| 2026-06-29 | All 8 tasks implemented via subagent-driven-development and reviewed clean; status set to Done. See [summary](../session-summaries/2026-06-29-cashout-recent-transactions-summary.md). |
