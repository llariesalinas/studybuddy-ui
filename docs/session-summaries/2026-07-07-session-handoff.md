# Session handoff — 2026-07-07

**Branch:** `feat/demo-data-reset`, **3 commits ahead of `origin/feat/demo-data-reset`, not pushed.**

## Where things stand

Everything described below is **committed locally** but **not pushed**. The user said they'll verify everything locally first, then push. Do not push without an explicit go-ahead when this session resumes.

```
2102caf feat: re-enable cash payments, fix seed data year_level scale, redesign onboarding guided rail
1e099e5 chore: add StudyBuddy logo concept mockups
03fad77 docs: add pre-oral defense Q&A and booking concurrency architecture doc
142ca8f fix: rename admin nav to Applications and capitalize StudyBuddy brand   <- last pushed commit
```

## What shipped in this session

### 1. Pre-oral defense Q&A document
[docs/architecture/pre-oral-defense-qa.html](../architecture/pre-oral-defense-qa.html) — a Q&A doc for the user's thesis pre-oral defense, grounded in the actual codebase (not the proposal), covering the 5 thesis objectives, a Student Safety section, general system Q&A, and a "Before you walk in" callout with known gotchas (e.g. a 10%/16% commission-rate inconsistency in unrelated code, a stale planning doc, decorative placeholder chart bars). Later updated to reflect the cash-payments work (below) and to add a Q&A about why location is a plain text field instead of a paid map API (cost).

### 2. `docs/architecture/booking-realtime-and-concurrency.md`
Pre-existing doc (not authored this session) explaining the two-layer mechanism that actually prevents double-booking: `select_for_update()` row locking (fires first) + a DB `UniqueConstraint` (backstop). Chat is the only real-time channel (WebSocket); everything else is pull-based. Referenced from the defense doc.

### 3. Re-enable cash payments + tutor debt banner (the main feature work)
Plan: [docs/plans/2026-07-07-reenable-cash-payments.md](../plans/2026-07-07-reenable-cash-payments.md) · Summary: [docs/session-summaries/2026-07-07-reenable-cash-payments-summary.md](2026-07-07-reenable-cash-payments-summary.md)

- CASH reactivated as a `PaymentMethod` (migration `0070_reactivate_cash_payment.py`).
- Payment method is now **derived from the booking's `session_mode`** (F2F -> CASH, Online -> PAYMONGO), not user-picked, and **enforced server-side** in both `submit_session_payment` and `confirm_payment_and_book`. Folded in a fix for an adjacent, previously-tracked bug where the proof-of-payment check looked for `'online'` instead of the actually-active `'PAYMONGO'` code.
- CASH requires a receipt photo only (no fabricated transaction reference).
- New `src/components/WalletDebtBanner.vue`: global, **non-dismissible while a tutor's wallet balance is negative**, sourced from a boolean-only `wallet_negative` field on `profile_status` (never exposes the amount), styled with `--sb-danger`, links to the Wallet page.
- `reset_demo_data.py` seeds CASH-paid F2F sessions with receipt images and **deterministically forces Miguel's wallet to exactly -75.00** (not left to chance) so the debt banner is actually demoable.
- Added 3 new backend test classes (`SessionModePaymentMethodEnforcementTests`, `ProfileStatusWalletNegativeTests`, 8 tests) and fixed one pre-existing test the new enforcement silently broke.

### 4. Seed data year_level scale fix (pre-existing Codex work, audited and extended this session)
Plan: [docs/plans/2026-07-07-seed-data-year-level-scale-fix.md](../plans/2026-07-07-seed-data-year-level-scale-fix.md)

New shared module `backend/studybuddy/management/commands/_year_level_scale.py` (`YEAR_RANGE_BY_COURSE`, `random_year_level()`, `COLLEGE_YEAR_OFFSET`) so the "college years are 13-16 on the unified scale" convention lives in one place instead of being duplicated across `reset_demo_data.py` and `seed_data.py`.

### 5. Onboarding guided-rail redesign (pre-existing Codex work, not authored this session)
Plan: [docs/plans/2026-07-07-onboarding-guided-rail-redesign.md](../plans/2026-07-07-onboarding-guided-rail-redesign.md) — `PreferenceSetup.vue` redesign, template/CSS only; `SbStepBar.vue` deleted.

### 6. Logo concept mockups
`docs/design/2026-07-07-studybuddy-logo-concepts-mockups/index.html` + `src/assets/logo-studybuddy-s-v1.png` — unrelated design exploration, committed as-is per the user's "commit everything" instruction. Not otherwise discussed in this session.

## Important environment discovery: no isolated local database

`backend/.env` and `backend/.env.dev` are **identical**, both pointing at the same Supabase-hosted Postgres instance — this project had no separate local database for dev/testing. This was discovered while trying to run tests for the cash-payments work, since the plan I wrote had wrongly assumed a local DB already existed.

**Resolved by using the local PostgreSQL 18 server already installed and running on the machine** (`localhost:5432`), matching this project's own CI config (`postgres`/`postgres`/`localhost`) rather than Supabase. Credentials the user provided: username `postgres`, password `sysadmin2003`. `.env` itself was never modified — DB connection env vars are passed inline per-command.

**Commands used (from `backend/`):**
```bash
# Migrate
DB_HOST=localhost DB_PORT=5432 DB_USER=postgres DB_PASSWORD=sysadmin2003 DB_NAME=postgres ./venv/Scripts/python.exe manage.py migrate

# Clear + reseed demo data (includes the CASH/debt-banner demo scenario)
DB_HOST=localhost DB_PORT=5432 DB_USER=postgres DB_PASSWORD=sysadmin2003 DB_NAME=postgres ./venv/Scripts/python.exe manage.py reset_demo_data

# Run the dev server
DB_HOST=localhost DB_PORT=5432 DB_USER=postgres DB_PASSWORD=sysadmin2003 DB_NAME=postgres ./venv/Scripts/python.exe manage.py runserver

# Run tests (creates/destroys its own disposable test_postgres DB on the same local server)
DB_HOST=localhost DB_PORT=5432 DB_USER=postgres DB_PASSWORD=sysadmin2003 DB_NAME=postgres ./venv/Scripts/python.exe manage.py test --noinput --keepdb
```

**As of this handoff, the local backend dev server is NOT running** — only `migrate`, `reset_demo_data`, and test runs were executed; nothing was left listening on port 8000. Confirmed the local `postgres` database currently has the full demo dataset seeded (421 users, Miguel's wallet at -75.00, etc.) from the last `reset_demo_data` run.

## Verification already done in this session

- 8 new tests + the fixed pre-existing test: all pass (25/25 relevant to this work).
- Full backend suite (matching CI's clean env, `.env` temporarily moved aside and restored): 278 tests, 30 failures + 5 errors — all confirmed pre-existing and unrelated (recommender endpoints, avatar uploads, institution catalog, dev-tools flags off by default in both this run and CI). None touch anything changed this session.
- `reset_demo_data` ran end-to-end against local Postgres; log line confirmed: `Miguel balance -75.00 (must be negative for the debt banner demo)`.
- `npm run lint` and `npm run build`: clean.

## What's NOT done / pending

- **The user is verifying everything locally themselves right now** (had asked how to clear/reseed and whether the backend was running). No frontend manual click-through of the debt banner / cash receipt flow has been done by either of us yet in a browser.
- **Nothing has been pushed.** Confirm explicitly with the user before pushing `feat/demo-data-reset`.
- The plans README (`docs/plans/README.md`) and `docs/plans/index.html` were updated to reflect Done status for the cash-payments plan — already committed, no action needed unless new work starts.

## Known non-blocking observations (don't re-litigate, just be aware)

- Isabel (a different demo persona) also happened to land with a negative balance in the last `reset_demo_data` run (-505.00), purely by chance from pre-existing `random.choice(methods)` logic unrelated to this session's changes — not a bug, not something this session is responsible for fixing.
- There's a pre-existing, unrelated 10%/16% commission-rate inconsistency flagged in the defense doc's "Before you walk in" callout — worth the user reconciling before their actual defense, but out of scope for code changes here.
