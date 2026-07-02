---
title: Edge-Case Scan — Findings Summary
date: 2026-06-14
status: In Progress (scan complete A–D; findings not all human-verified; no fixes shipped)
scope: Full A–D scan by Antigravity (27 files), plus a Claude-verified subset of the money/auth core.
auditor: Antigravity (agy) full scan + Claude verification (no code changed, nothing run)
plan: ../plans/2026-06-14-antigravity-edgecase-scan.md
raw_findings: ../2026-06-14-antigravity-edgecase-findings.md
---

# Edge-Case Scan — Findings Summary

## Scan status (reconciled 2026-06-14)

Two artifacts feed this summary; they were inconsistent and are now reconciled:

- **Raw findings** — `docs/2026-06-14-antigravity-edgecase-findings.md` (Antigravity, all
  four passes A–D, 27 files, 55 primary + 7 uncertain findings). This is the full scan output.
- **Verified subset (below)** — Claude independently read the money/auth core and the
  booking/payment paths and confirmed the high-severity findings against real `file:line`
  evidence.

**Why status is "In Progress," not "Done":** the *scan* is complete, but (a) the 55 findings
are not all human-verified, and (b) no code fixes have shipped. Flip to Done only when the
confirmed criticals are fixed (or explicitly deferred) and the rest are triaged.

**Antigravity's accuracy:** spot-checks passed. Its independently-derived criticals match
Claude's findings (A-03/A-04/C-02/U-01/U-02 ≡ F2/F3/F1 below), and its novel high-severity
claims hold up against the code — most notably the centavos bug (see V0), which Claude's
focused pass had missed. Treat the raw findings as credible but still requiring per-item
verification before fixing.

## Verified subset

- **Files read in full by Claude:** `paymongo_money_movement.py`, `permissions.py`, `wallet.js`,
  `api.js`, plus targeted regions of `views.py` (registration, withdrawals, cash-outs, booking
  confirm, online-payment verify, wallet credit).
- **Confirmed:** 1 newly-verified CRITICAL (V0, from Antigravity) + 4 HIGH, 3 MED, 2 LOW (below).
- **No code was changed. Nothing was run.** Line numbers are from the current working tree.

### V0 CRITICAL E3 — cash-out amount sent to PayMongo in pesos, not centavos
- File: `backend/studybuddy/paymongo_money_movement.py:97` (vs `backend/studybuddy/views.py:4201`)
- What: PayMongo's API takes amounts in **centavos**. The online-payment path proves this —
  `initiate_online_payment` sends `amount_cents = int(total_amount * 100)` (views.py:4201). But
  `create_wallet_transaction` sends the raw peso value `'amount': str(amount)` with no ×100, so
  a ₱500 cash-out is transmitted as 500 centavos (₱5) or rejected by provider validation.
- Source: Antigravity A-01/A-02; **verified by Claude** against the divergent checkout path.
- Suggested check: convert to integer centavos in `create_wallet_transaction`, and divide the
  returned `fee`/`net_amount` by 100 in `normalize_wallet_transaction`.

The 8 items below (F1–F9) are Claude's original focused-pass findings, retained as the
verified money/auth core. Several appear in the raw findings under different IDs.

What's solid (checked, no issue): the live `cash_outs` flow uses
`select_for_update()` on the wallet (views.py:4082); booking double-booking is blocked by a
`select_for_update` on `TutorAvailability` plus a conflict check inside the atomic block
(views.py:1967, 2007); `credit_tutor_wallet` is idempotent via a `reference_id` existence
check (views.py:4428); `api.js` 401-refresh coalescing via `refreshPromise` is correct.

---

## HIGH

### F1 HIGH E10 — money deducted, then unhandled provider exception leaves wallet short
- File: `backend/studybuddy/views.py:4124`
- What: In `cash_outs`, the DB `transaction.atomic()` block (4081-4122) **commits first** —
  balance is debited and the `WithdrawalRequest` + `Transaction` rows are written — and only
  *afterwards* does `create_wallet_transaction(...)` call PayMongo. Only `PayMongoCashOutError`
  is caught (4133). A raw `requests` failure (`ConnectionError`, `Timeout`, `JSONDecodeError`
  on a non-JSON 500, etc.) is **not** caught, so it propagates as an unhandled 500.
- Trigger: PayMongo is slow/unreachable, or returns a malformed body, when a tutor cashes out.
- Code:
    ```python
    wallet.balance -= total_deducted
    wallet.save(update_fields=['balance'])
    ...                         # atomic block ends here — committed
    try:
        provider_data = create_wallet_transaction(...)
    except PayMongoCashOutError as exc:   # only this is caught
    ```
- Suggested check: catch a broader `requests.RequestException` (or `Exception`) around the
  provider call and run it through the same `apply_cash_out_provider_result(..., 'failed')`
  path so the balance is refunded / withdrawal marked failed instead of silently short.

### F2 HIGH E10 — outbound PayMongo HTTP calls have no timeout
- File: `backend/studybuddy/paymongo_money_movement.py:71` and `:114`; also
  `backend/studybuddy/views.py:4346` (`verify_online_payment`)
- What: `requests.get(...)` / `requests.post(...)` are called with **no `timeout=`**. The
  default is to wait forever, so a hung PayMongo socket blocks the worker thread indefinitely.
- Trigger: provider network stall during a cash-out, receiving-institution lookup, or payment
  verification.
- Code:
    ```python
    response = requests.post(
        f'{PAYMONGO_API_BASE_URL}/wallets/{wallet_id}/transactions',
        json={'data': {'attributes': attributes}},
        headers=get_money_movement_headers(),
    )   # no timeout=
    ```
- Suggested check: pass an explicit `timeout=(connect, read)` on every external `requests` call.

### F3 HIGH E5 — cash-out callback processes unauthenticated when secret is unset
- File: `backend/studybuddy/views.py:4152`
- What: `paymongo_cashout_callback` has `@authentication_classes([])` / `@permission_classes([])`.
  If `PAYMONGO_CASHOUT_CALLBACK_SECRET` is configured it verifies a token (good), but when the
  setting is **empty it only logs a warning and proceeds**. With the secret unset in any
  environment, anyone who can reach the URL can POST a body that flips a withdrawal's status
  (e.g. mark a failed cash-out "succeeded", or vice-versa) via `apply_cash_out_provider_result`.
- Trigger: deploy/staging where `PAYMONGO_CASHOUT_CALLBACK_SECRET` was never set.
- Code:
    ```python
    if secret:
        ... constant_time_compare ...
    else:
        logger.warning("... callback received without signature verification ...")
        # falls through and processes the request
    ```
- Suggested check: fail closed — return 403 when the secret is not configured, rather than
  processing an unauthenticated state change to money records.

### F4 HIGH (maintainability / latent bug) — duplicate & dead withdrawal view definitions
- File: `backend/studybuddy/views.py:3910`, `:4032`, `:4043`, `:4146`
- What: `request_withdrawal` is defined as a full implementation at **3910**, redefined as a
  thin wrapper at **4043**, then rebound `request_withdrawal = cash_outs` at **4146**.
  `list_withdrawals` is likewise defined twice (3885 and 4032). The URLconf routes
  `wallet/cash-outs/` and `wallet/withdraw/` to `cash_outs`, so the 3910 implementation is
  **dead code** — yet it carries divergent rules (a hardcoded `< 500` minimum at 3924 and a
  balance check with **no `select_for_update`** at 3917-3938) that contradict the live path's
  `get_cashout_minimum()` + locked wallet. A future edit to "the withdrawal view" could easily
  land on the dead one.
- Trigger: maintenance error — editing the shadowed definition believing it is live.
- Code:
    ```python
    def request_withdrawal(request):   # 3910 — DEAD, hardcoded < 500, no row lock
        ...
    def request_withdrawal(request):   # 4043 — wrapper
        return cash_outs(request)
    request_withdrawal = cash_outs     # 4146 — final rebind
    ```
- Suggested check: delete the dead 3910 `request_withdrawal` and the duplicate 3885
  `list_withdrawals`; keep one definition each. (Confirm no `urls.py` entry points at the dead
  ones first — current routing points only at `cash_outs` / the 4032 `list_withdrawals`.)

---

## MED

### F5 MED E1/E8 — booking confirm crashes (500) on a malformed slot instead of 400
- File: `backend/studybuddy/views.py:1968` and `:2029`
- What: `confirm_payment_and_book` validates `session_date` carefully but reads
  `slot["availability_id"]` and `slot["session_mode"]` with **bracket access**. A slot object
  missing either key raises `KeyError` → unhandled 500, rather than a clean 400.
- Trigger: client (or a malformed/replayed request) posts a slot without `availability_id`.
- Code:
    ```python
    availability = get_object_or_404(
        TutorAvailability.objects.select_for_update(),
        id=slot["availability_id"], tutor=tutor)
    ...
    "session_mode": "F2F" if slot["session_mode"] in [...] else "Online",
    ```
- Suggested check: use `slot.get(...)` with an explicit "Malformed slot" 400, matching the
  surrounding validation style.

### F6 MED E9 — wallet store fetches swallow/propagate errors with no UI handling
- File: `src/stores/wallet.js:42` (`fetchWallet` — `try`/`finally`, no `catch`), and
  `:55`/`:60`/`:65` (`fetchTransactions`, `fetchWithdrawals`, `fetchPayoutAccounts` — no
  try at all)
- What: A failed `api.get('wallet/...')` produces an unhandled promise rejection. `fetchWallet`
  clears `loading` but re-throws; the others reject silently. Depending on the caller, the
  wallet UI can hang or show stale data with no error surfaced (contrast `requestWithdrawal`
  at :90, which does handle errors).
- Trigger: wallet endpoint returns 5xx / network drop while the wallet view is loading.
- Code:
    ```js
    async function fetchTransactions() {
      const { data } = await api.get('wallet/transactions/')
      transactions.value = data
    }   // no catch
    ```
- Suggested check: surface fetch failures (toast / error state) the way `requestWithdrawal`
  already does, so a wallet load failure is visible rather than a silent hang.

### F7 MED E1 — `credit_tutor_wallet` assumes `payment.amount` is non-null
- File: `backend/studybuddy/views.py:4432`
- What: `total_amount = payment.amount` then `commission = total_amount * COMMISSION_RATE`.
  If `payment.amount` is `None` (a payment row created before the amount was set), this raises
  `TypeError` on the multiply, inside the crediting path.
- Trigger: a `Paid` payment whose `amount` was never populated.
- Code:
    ```python
    total_amount = payment.amount
    commission = total_amount * COMMISSION_RATE
    ```
- Suggested check: guard `if payment.amount is None: return` alongside the existing
  `payment_status != 'Paid'` guard at 4424. (UNCERTAIN — depends on whether the schema makes
  `amount` non-null; verify the model field.)

---

## LOW

### F8 LOW E10 — receiving-institutions lookup also un-timed and bubbles 502 only for PayMongo errors
- File: `backend/studybuddy/views.py:3952` → `paymongo_money_movement.py:70`
- What: same missing-`timeout` family as F2 (logged separately because it's a read path, lower
  blast radius). `receiving_institutions` only translates `PayMongoCashOutError`; a raw
  `requests` exception would 500.
- Suggested check: covered by fixing F2 + wrapping the call like F1.

### F9 LOW E5 — `wallet_transactions` (3856) returns 403 for non-tutors but has no duplicate-safe naming
- File: `backend/studybuddy/views.py:3856`
- What: Not a security hole — the role gate is present (`Tutor.DoesNotExist → 403`). Flagged
  only as part of the F4 duplication cluster: several wallet views in this region share
  near-identical tutor-lookup preambles that have drifted (`Tutor.objects.get(...)` vs the
  helper `get_request_tutor(request)` used by the newer 4032/4049 views). Consistency risk, not
  a live bug.
- Suggested check: standardize all wallet/withdrawal views on `get_request_tutor`.

---

## Coverage (now scanned)

The areas this section previously listed as "not yet scanned" were covered by the Antigravity
A–D pass — see `docs/2026-06-14-antigravity-edgecase-findings.md`:
- Full `views.py` endpoints (Pass C: C-01…C-16) — registration role check, cash-out, payment,
  support tickets, profile setup, query-param parsing.
- `admin_views.py` withdrawal state machine + locking (C-05, C-06).
- `recommender/` (Pass D: D-01…D-05) — `hybrid.py` cold-start, `cbf.py` course/level matching,
  `CF.py` ZeroDivision on empty ratings.
- `chat/consumers.py`, `chat/services.py` (Pass D: D-06…D-12) — websocket JSON/auth, disconnect,
  duplicate-room race, timezone.
- Frontend booking views and stores (Pass B: B-01…B-12) — `TutorDetails.vue`, `InitialBooking.vue`,
  `FindTutors.vue`, `activeSession.js`, plus the booking stores in UNCERTAIN (U-03, U-04).

## Next steps before this can be marked Done

1. **Triage the 55 raw findings** — confirm each `file:line`, drop duplicates/false positives.
   (Antigravity's accuracy spot-checked well, but per-item verification is still required.)
2. **Fix the confirmed criticals first:** V0 (centavos), F1/C-02 (cash-out reversal),
   F3/U-02 (callback fails open), C-01 (registration role), C-07/C-09 (null crashes).
3. **Verify the UNCERTAIN items** (U-01…U-07) against the schema/callers before acting.
4. Then flip plan status to **Done** and note in the index row.
