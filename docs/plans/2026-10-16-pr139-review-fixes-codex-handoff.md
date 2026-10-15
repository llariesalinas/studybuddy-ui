---
title: Codex Handoff — Verify the PR #139 Review Fixes
date: 2026-10-16
status: Approved
summary: Apply migrations 0087/0088 to the dev database, re-run both test suites with the real environment, and walk the eight-step manual checklist for commit 94bf7f1.
---

# Codex Handoff — Verify the PR #139 Review Fixes

## Status & Progress Summary

**Status:** Ready for Codex. The code is done and pushed. This handoff covers only verification
work that needs access the Claude cloud session did not have: the real `.env`, the dev database
and a browser.
**Next step:** Give this document to Codex. Work through Tasks 1–5 in order, then report back as
described at the end. **Do not change application code** unless a task below finds a regression
caused by `94bf7f1`. If it does, stop and report before fixing.

---

## Context

- Repo: `llariesalinas/studybuddy-ui`. Vue 3 + Pinia frontend in `src/`, Django backend in
  `backend/`.
- Branch: `claude/beautiful-archimedes-8fu8tm`. Head: `94bf7f1`
  (`fix: address PR 139 routing and data integrity findings`). Base: `045cfe0` (the PR #139 merge).
- What changed: see `docs/session-summaries/2026-10-16-pr139-review-fixes.md`. It covers
  mode-switch routing, verification carry-over, self-exclusion from recommendations, subject
  category integrity, weights preview sequencing and trusted-device row cleanup. It also adds two
  migrations:
  - `0087_review_integrity`: adds `tutor_setup_completed_at`, backfills configured tutors and
    merges duplicate system categories.
  - `0088_unique_system_subject_category`: adds the conditional unique constraint. It is a
    separate migration because PostgreSQL rejects the index while deferred FK events from the
    merge are pending.
- Plans: the four `docs/plans/2026-10-15-*.md` files, all marked Done.

## What the Claude session already checked (2026-10-16, no `.env`)

The Claude session ran these checks against a local PostgreSQL 16 server with `DEBUG=true`,
placeholder `SECRET_KEY` and `PAYMONGO_SECRET_KEY`, and no other env vars:

| Check | `94bf7f1` | Base `045cfe0` |
| --- | --- | --- |
| `oxlint src/` / `eslint src/` | Clean | — |
| `vite build` | Pass | — |
| `npx vitest run` | 247 pass, 1 skip, 11 fail | Same 11 fail |
| `python manage.py test` | 556 run, 8 fail | Same 8 fail |

Every failure also fails on the base commit, so none comes from `94bf7f1`. The commit's own
summary reports fewer failures, and the gap is expected:

- **Backend, 7 of 8:** `DevLiveSessionTests` (5) and `DevWalletFundsTests` (2) return 404 because
  `BOOKING_DEV_TOOLS_ENABLED` defaults to false (`backend/backend/settings.py:338`). With the real
  `.env` they should pass. The 8th, `ChatFeatureTests.test_location_update_rejected_inside_grace_cutoff`
  (200 instead of 400), is the known pre-existing failure.
- **Frontend, 2 of 11:** `useOrbitStripComposable.test.js` ("derives the explicit session's own
  phase…") and `activeSession.test.js` ("recognizes a forced live booking…") failed here but are
  not in the commit summary's list of 9. Both also fail on base. They are probably sensitive to
  the clock or timezone (the container runs in UTC, while the app assumes Manila time). The other
  9 (6 `BookingTimeRangePicker`, 3 `tokens.test.js`) are the known pre-existing ones.

---

## Tasks

### Task 1: Check out and install

```
git fetch origin claude/beautiful-archimedes-8fu8tm
git checkout claude/beautiful-archimedes-8fu8tm   # confirm HEAD is 94bf7f1 or later
npm ci
cd backend && pip install -r requirements.txt
```

### Task 2: Apply migrations to the dev database only

1. Confirm which database `.env` points at. **If it is production or the shared demo database, stop
   and ask the user first.** Applying the migrations merges category rows and backfills a column,
   and that is hard to undo.
2. Take a dump of the dev database first (`pg_dump`), so the migration can be rolled back.
3. Run `python manage.py showmigrations studybuddy`, then `python manage.py migrate`. Confirm that
   0087 and 0088 apply cleanly.
4. Spot-check the results:
   - There is exactly one `SubjectCategory` row with the system flag.
   - Existing tutors who already have rates or subjects have a non-null `tutor_setup_completed_at`.
5. Run `python manage.py makemigrations --check --dry-run`. It should report no changes.

### Task 3: Re-run the full suites with the real environment

- Backend: `cd backend && python manage.py test`, with `BOOKING_DEV_TOOLS_ENABLED=true`. Expect only
  the `ChatFeatureTests` grace-cutoff failure. Any other failure is a finding. Confirm it also fails
  on `045cfe0` before attributing it.
- Frontend: `npm run lint` (note that this auto-fixes; check `git status` afterwards and do not
  commit lint churn), `npm run build`, then `npx vitest run`. Expect at most the 11 failures listed
  above. Run the two clock-sensitive tests once more with `TZ=Asia/Manila` and record whether they
  pass.

### Task 4: Manual checklist in the browser

Start `python manage.py runserver`, `python manage.py qcluster` and `npm run dev`. Then walk the
eight steps under "Manual review checklist" in
`docs/session-summaries/2026-10-16-pr139-review-fixes.md`. They cover:

1. An established tutor removes their last subject and keeps dashboard access.
2. A first-time tutee-to-tutor switch still requires rate and subject setup.
3. A tutor deep link from Tutee mode opens the commission terms gate.
4. Undo after a deep-link switch, and Undo expiring after a navigation.
5. A two-session remote switch refreshes the profile, and a later deep link asks first.
6. An empty category shows in tutor proposals; renaming the system category is rejected.
7. A category created in the review panel appears without a reload.
8. Throttled weights preview shows only the current tutee; Save during preview settles.

Record pass or fail per step, with a screenshot for any failure. Step 8 needs algorithm tools
enabled and network throttling in devtools.

### Task 5: Leave the pre-existing failures alone

Do not fix the pre-existing failures on this branch. If you can explain one quickly (for example,
the clock-sensitive frontend tests), write down the cause and a proposed fix in your report.

---

## Report back

Reply with:

- The database you migrated (name or host only, **no credentials**) and the result of the
  Task 2 spot checks.
- Backend and frontend test counts, with any failure beyond the expected set and whether it
  reproduces on `045cfe0`.
- Pass or fail for each of the 8 manual steps, with screenshots for failures.
- Any regression traced to `94bf7f1`, with file and line. Do not fix it yet.

When everything passes, update this file's `status` to `Done` and add a row to
`docs/plans/README.md`.
