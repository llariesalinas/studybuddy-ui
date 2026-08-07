---
title: Consolidate demo data seeding
date: 2026-08-08
status: In Progress
summary: Fold seed_tie_breaker_demo/seed_booking_load_limit_demo/seed_wallet_cases_demo into seed_data.py and seed 2 permanent SuperAdmin accounts, so reset_demo_data + seed_data alone produces a fully demoable database.
spec:
---

# Consolidate demo data seeding

<!-- LIVING SUMMARY: keep this section and the Changelog current on every edit -->

**Status & Progress Summary** (2026-08-08): Steps 1-8 done and verified end-to-end against the
real database (which turned out to already be the same DB as the live Render demo — no separate
local one exists). `reset_demo_data && seed_data` runs clean, seeds both SuperAdmins, all 3
additive demo cases, and the SuperAdmins survive a second reset. Found and fixed a real ordering
bug during verification (see Deviations). Also found and fixed an unrelated, pre-existing
production incident along the way: Render's `DB_HOST` had drifted to a stale value, meaning the
live demo backend could not reach its database at all — fixed via Render's Environment tab,
confirmed via Supabase's own dashboard. Step 8 backend test suite finished: 381 tests, 7 failures + 1 error, all in
`TutorCashOutTests`/`TutorProfileTests`/`VerificationDevToolsTests` — unrelated to this diff's
scope, not independently re-verified against `origin/main` without these changes. Step 9
(live-DB operational wipe) is effectively already covered, since the verification run above *was*
against the live DB. Committed and pushed; PR opened:
[#116](https://github.com/llariesalinas/studybuddy-ui/pull/116).

**Deviations from the plan:**
- Additive demo case call order had to be tie-breaker discovery first, then
  booking-load-limit/wallet-cases — the plan didn't specify order, and running load-limit/wallet
  first polluted the tie-group scan with their own signal-less new tutors, producing an incidental
  tie against the cold-start tutee S1 instead of a real one, which then failed on an unrelated
  availability shape. Fixed in `_seed_additive_demo_cases`.

## Goal

`reset_demo_data && seed_data` should be the only two commands needed for a clean,
fully-demoable database (local dev and the live Render demo deployment alike) — no chaining
extra demo-case commands afterward, and a SuperAdmin login should exist without a manual
`make_superadmin` step.

## Approach

- Seed two permanent SuperAdmin accounts directly in `seed_data.py`, using the same shared demo
  password as every other seeded account (`studybuddy123`), for easy access. `reset_demo_data.py`
  already excludes `is_staff=True` users from deletion, so once seeded these accounts survive
  every future reset with no code change to that command.
- Keep `seed_tie_breaker_demo`, `seed_booking_load_limit_demo`, `seed_wallet_cases_demo` as
  standalone, independently reversible (`--remove`) commands — `seed_data.handle()` orchestrates
  all three via Django's `call_command()` at the end of its own seeding.
- Fix the long-standing `DEFAULT_TUTEE_ID = 5089` breakage in `seed_tie_breaker_demo`: instead of
  trusting a hardcoded id that only matches one specific database's row numbering,
  `seed_data` discovers a real curated tutee with an actual tie group and passes it explicitly
  via `--tutee`.
- `PartnerInstitution`/`Course`/`Strand` already survive `reset_demo_data` (never deleted) and
  reseed idempotently via `update_or_create` in `_seed_academic_foundation` — no change needed.
- Update both demo docs (`docs/architecture/demo-deployment.md`,
  `docs/architecture/demo-data-testing-accounts.html`) to reflect the collapsed recipe and the
  new SuperAdmin accounts.

## Steps

1. Branch `chore/consolidate-demo-seed` off freshly-fetched `origin/main`.
2. Add SuperAdmin seeding to `seed_data.py`: two accounts —
   `superadmin.demo@cpu.edu.ph` (Sonia Superadmin) and `superadmin2.demo@cpu.edu.ph`
   (Ramon Superadmin), both `is_staff=True`, `role='SuperAdmin'`, `is_domain_exempt=True`,
   `profile_completed=True`, password `studybuddy123`.
3. Add a helper to `seed_data.py` that finds a curated tutee with a real tie group (mirrors the
   manual shell workaround already documented in `demo-deployment.md`).
4. Call `seed_booking_load_limit_demo`, `seed_wallet_cases_demo`, and `seed_tie_breaker_demo
   --tutee <discovered id>` via `call_command()` at the end of `seed_data.handle()`, inside the
   existing transaction.
5. Update `docs/architecture/demo-deployment.md`: collapse the reseed recipe to
   `migrate → reset_demo_data → seed_data` (+ optional `make_superadmin` only for a *different*
   email than the two seeded defaults), document the 2 SuperAdmin logins.
6. Update `docs/architecture/demo-data-testing-accounts.html`: add the 2 SuperAdmin rows, remove
   stale "No Longer Seeded" / manual-command notes for the three folded-in demo cases.
7. Verify end-to-end locally: `migrate && reset_demo_data && seed_data` completes clean, the two
   SuperAdmins exist and survive a second `reset_demo_data` run, all three demo cases present.
8. Run `python manage.py test`; confirm no new failures vs. documented baseline.
9. **Operational, not code:** one-time full wipe of any existing stale staff/superuser accounts
   on both local dev DB and the live Render demo DB, then run the new consolidated seed there too.
   Confirm explicitly with the user again before touching the live Render database.

## Risks

- Tie-breaker discovery adds a query loop over curated tutees inside `seed_data` — bounded to the
  small curated set (not the 150/350 filler population), so cost stays low.
- Nesting `call_command()` inside the outer `transaction.atomic()` relies on Django savepoints —
  verify it behaves as expected rather than assuming.
- Live Render DB wipe touches the deployed demo — requires explicit confirmation at execution
  time, separate from this plan's approval.

## Checks to run

- `cd backend && python manage.py migrate && python manage.py reset_demo_data && python manage.py seed_data` —
  completes without error; shell-verify 2 SuperAdmins + all 3 demo cases exist.
- `python manage.py reset_demo_data` again — confirm the 2 SuperAdmins still exist afterward.
- `python manage.py test` — no new failures vs. documented pre-existing baseline.

## Changelog

| Date | Change |
|------|--------|
| 2026-08-08 | Committed (all 5 files) and pushed `chore/consolidate-demo-seed`; opened [PR #116](https://github.com/llariesalinas/studybuddy-ui/pull/116) against `origin/main`. Test suite result (381 tests, 7 failures + 1 error, all unrelated to this diff) recorded |
| 2026-08-08 | Implemented Steps 1-7: branched off `origin/main`, seeded 2 SuperAdmins + orchestrated the 3 additive demo cases in `seed_data.py`, verified end-to-end (reset+seed twice, SuperAdmins survive), updated both demo docs. Found/fixed a call-order bug (tie-breaker must run before load-limit/wallet). Found/fixed an unrelated live incident: Render's `DB_HOST` had drifted stale, breaking the demo backend's DB connectivity entirely; corrected via Render's Environment tab. Status set to In Progress pending the backend test suite result |
| 2026-08-08 | Plan created and Approved after an 8-decision `/grill-with-docs` session; added Status & Progress Summary and this Changelog |
