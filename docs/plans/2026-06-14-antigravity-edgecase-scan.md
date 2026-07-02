---
title: Antigravity Edge-Case Scan — Handoff Brief
date: 2026-06-14
status: Ready to hand off
audience: Antigravity (AGY) — automated agent, treat as junior; needs explicit, narrow instructions
---

# Antigravity Edge-Case Scan — Handoff Brief

## 0. Read this first (rules that never change)

You are scanning the Studybuddy codebase for **edge cases and latent bugs**. You are an
auditor, not a fixer.

**Hard rules:**
1. **DO NOT edit, refactor, fix, or delete any code.** Report only. No `git commit`, no
   file writes except the one report file in Section 6.
2. **DO NOT run the app, migrations, builds, or tests.** This is a static read-only scan.
3. **Work ONE pass at a time** (passes are in Section 4). Finish a pass, write its findings
   to the report, then start the next. Never hold two passes in your head at once.
4. **If a file is longer than ~600 lines, read it in chunks** (e.g. lines 1-600, then
   601-1200). Do not try to load `views.py` (4,719 lines) in one read — you will lose track.
5. **Every finding needs a file path + line number + a one-line reason.** No vague claims.
   If you cannot point to a line, it is not a finding — drop it.
6. **When unsure, mark it `UNCERTAIN` and move on.** Do not guess fixes. Do not invent
   behavior you did not read.
7. **Quote the actual code** for each finding (2-5 lines). If you can't quote it, you didn't
   find it.

**Stack reminder:** Frontend = Vue 3 (`<script setup>`) + Pinia + Vue Router + Axios.
Backend = Django REST Framework + PostgreSQL + SimpleJWT. Timezone is Asia/Manila.

---

## 1. What "edge case" means here (with concrete examples)

An edge case is an input or state the code does not handle, that causes a crash, wrong data,
security hole, or money error. Use THIS checklist on every file. These are the only categories
that count:

| # | Category | What to look for | Studybuddy example |
|---|----------|------------------|--------------------|
| E1 | **Null / undefined / missing** | `.field` on something that may be null; `obj.a.b` chains; missing dict keys (`request.data['x']` vs `.get('x')`) | `booking.tutor.user.email` when a booking has no tutor |
| E2 | **Empty collections** | `[0]` on a possibly-empty list/array; `.first()` then using it; `reduce`/`sum` over empty | recommender returns `[]`, code does `results[0]` |
| E3 | **Number / money** | division by zero; float money math; negative amounts; rounding; rate × hours | wallet balance going negative; `amount / count` |
| E4 | **Date / time / timezone** | naive vs aware datetime; UTC vs Manila; slot overlap; past-date bookings; DST | booking time in the past; double-booked slot |
| E5 | **Auth / permission** | endpoint missing permission check; role check (tutor vs tutee vs admin) missing; IDOR (user A reads user B's data by id) | tutee hitting a tutor-only endpoint; reading another user's booking by `pk` |
| E6 | **State machine** | invalid status transition; acting on already-cancelled/completed/paid records; double-submit | confirming an already-rejected booking; paying twice |
| E7 | **Concurrency / double-action** | no idempotency on POST; double-click submit; race on balance | two booking confirms with same `request_id`; double withdrawal |
| E8 | **Input validation** | unbounded string; wrong type; out-of-range; unvalidated query params; SQL/`filter` on raw input | negative `hourly_rate`; `page=-1`; huge file upload |
| E9 | **Error handling** | bare `except:`; swallowed errors; API call with no failure branch; `await` with no catch | axios call in a `.vue` with no `catch`, UI stuck loading |
| E10 | **External calls** | PayMongo / email / websocket failure paths; partial success; no retry/timeout | payment provider returns error mid-flow, DB already updated |

If something doesn't fit E1-E10, it is **not** in scope. Skip it.

---

## 2. Risk-ranked file map (scan in this order)

Highest risk first — money, auth, and the booking flow are where edge cases hurt most.

### TIER 1 — money & auth (scan most carefully)
- `backend/studybuddy/paymongo_money_movement.py` (132 lines) — payment provider calls (E3, E10, E6)
- `backend/studybuddy/permissions.py` — every permission class (E5)
- `src/stores/wallet.js` — balance, withdrawals (E3, E6, E7)
- `src/views/TutorWallet.vue`, `src/views/AdminWithdrawals.vue` — withdrawal UI (E3, E6)
- `src/stores/auth.js` (266 lines) — JWT refresh, logout, token state (E5, E7, E9)
- `src/services/api/api.js` (115 lines) — 401 handling, `refreshPromise` coalescing (E7, E9)

### TIER 2 — booking flow (the core product path)
- `src/views/TutorDetails.vue` (1,364 lines — READ IN 3 CHUNKS) — owns `POST bookings/confirm/` (E4, E6, E7)
- `src/views/InitialBooking.vue`, `src/views/FindTutors.vue` — steps 1-2 (E1, E2, E8)
- `src/stores/initialbookingprefs.js`, `findTutors.js`, `bookedSessionDetails.js`,
  `tuteePaymentDetails.js` — booking state split across 4 stores (E1, E6)
- `src/components/BookingDatePicker.vue`, `BookingTimePicker.vue` — slot selection (E4)
- `src/components/SessionCheckInModal.vue`, `src/stores/activeSession.js` — check-in (E6)

### TIER 3 — backend endpoints (biggest surface)
- `backend/studybuddy/views.py` (4,719 lines, 138 functions — READ IN 8 CHUNKS OF ~600 LINES)
  Focus on every `@api_view` function: check E5 (permission) and E1/E8 (input) on each.
- `backend/studybuddy/serializers.py` (327 lines) — validation gaps (E8)
- `backend/studybuddy/admin_views.py` (483 lines) — admin endpoints, must be admin-gated (E5)
- `backend/studybuddy/models.py` (814 lines) — constraints, defaults, `save()` overrides (E3, E6)

### TIER 4 — recommender & chat
- `backend/studybuddy/recommender/hybrid.py`, `cbf.py`, `CF.py` — `cf_score/5` div, empty data (E2, E3)
- `backend/studybuddy/chat/consumers.py`, `services.py` — websocket auth & message handling (E5, E9)

---

## 3. Exact procedure for each file

For every file in a pass, do exactly this:

1. Read the file (in chunks if >600 lines).
2. Walk the **E1-E10 checklist** (Section 1) against it. One pass per category is fine.
3. For each issue found, write a finding using the template in Section 5.
4. Move to the next file. Do not fix anything. Do not re-read files from earlier passes.

**Backend-specific moves:**
- For each `@api_view` function in `views.py`: ask "what permission class guards this?" If you
  can't find one, that's an **E5 HIGH** finding.
- For each `request.data[...]` (bracket access): that crashes on missing key — **E1**. `.get()` is safer.
- For each `.objects.get(...)`: missing object raises `DoesNotExist` — is it wrapped? If not, **E9**.
- For each `[0]` / `.first()` followed by attribute access: **E2**.

**Frontend-specific moves:**
- For each `await api...(...)` or `axios` call in a `.vue`/store: is there a `try/catch` or
  `.catch`? If not — **E9** (UI can hang on error).
- For each `v-for` / list render that indexes `[0]` or assumes non-empty: **E2**.
- For each optional-chain-worthy access (`a.b.c`) without `?.`: **E1**.
- For each submit button: is there a disabled/in-flight guard against double-click? If not — **E7**.

---

## 4. The passes (do them in this order, one at a time)

- **Pass A — Money & Auth (Tier 1).** ~6 files. Highest priority. Output section "A".
- **Pass B — Booking Flow (Tier 2).** ~10 files. Output section "B".
- **Pass C — Backend Endpoints (Tier 3).** Big. `views.py` in 8 chunks. Output section "C".
- **Pass D — Recommender & Chat (Tier 4).** ~5 files. Output section "D".

After EACH pass: append that pass's findings to the report file (Section 6), then continue.
Do not wait until the end to write — write incrementally so nothing is lost.

---

## 5. Finding template (use exactly this format)

```
### [ID] [SEVERITY] [CATEGORY] — short title
- File: path/to/file.ext:LINE
- What: one sentence on the bug / unhandled case
- Trigger: the specific input or state that breaks it
- Code:
    <2-5 lines quoted from the file>
- Suggested check: one sentence — what guard is missing (NOT a code fix, just the idea)
```

- **ID**: `A1`, `A2`, ... `B1`, ... sequential per pass.
- **SEVERITY**: `HIGH` (money loss / auth bypass / crash on common path), `MED` (crash on
  uncommon path / wrong data), `LOW` (cosmetic / unlikely input).
- **CATEGORY**: one of E1-E10.

Example of a good finding:
```
### A3 HIGH E5 — withdrawal endpoint missing role check
- File: backend/studybuddy/views.py:2841
- What: any authenticated user can POST a withdrawal, not just the wallet owner / tutor
- Trigger: a tutee calls POST /wallet/withdraw/ with a tutor's wallet id
- Code:
    @api_view(['POST'])
    def request_withdrawal(request):
        wallet = Wallet.objects.get(id=request.data['wallet_id'])
        ...
- Suggested check: verify wallet.user == request.user before creating the request
```

---

## 6. Report output

Write ALL findings to a single new file:

```
docs/2026-06-14-antigravity-edgecase-findings.md
```

Structure:
```
# Antigravity Edge-Case Findings — 2026-06-14

## Summary
- Files scanned: N
- Findings: X HIGH, Y MED, Z LOW
- Passes completed: A / B / C / D

## Pass A — Money & Auth
<findings>

## Pass B — Booking Flow
<findings>

## Pass C — Backend Endpoints
<findings>

## Pass D — Recommender & Chat
<findings>

## UNCERTAIN (need a human to look)
<anything you couldn't confirm>
```

Do not write anywhere else. Do not modify source files.

---

## 7. Definition of done

- [ ] All four passes (A-D) completed.
- [ ] Every Tier 1 and Tier 2 file read in full (chunked where needed).
- [ ] Every finding has file:line, a quoted snippet, severity, and an E-category.
- [ ] Report saved at `docs/2026-06-14-antigravity-edgecase-findings.md`.
- [ ] No source files changed (`git status` shows only the new report file).
- [ ] Anything ambiguous is in the UNCERTAIN section, not guessed.

## 8. What NOT to do (common ways this goes wrong)
- Do not propose code fixes — only name the missing guard.
- Do not report style/formatting/naming — out of scope.
- Do not report a "finding" without a line number.
- Do not load giant files in one read — chunk them.
- Do not skip Tier 1 to do easy frontend files first — money and auth come first.
- Do not run, build, test, migrate, or commit anything.
