# SuperAdmin tutor/tutee stats, schedule & bookings — session summary

Plan: `docs/plans/2026-07-13-superadmin-tutor-tutee-stats.md` · Brief: `docs/briefs/2026-07-13-superadmin-tutor-tutee-stats.md`

## What shipped

Exactly what the spec described, no scope changes:

- Backend: `GET admin/users/<pk>/bookings/`, `.../availability/`, `.../stats/`, each with a
  matching `.../export/` CSV endpoint, all under the existing `IsSuperAdminUser` permission
  pattern in `admin_views.py`. No schema changes — everything computed live from `Booking`,
  `Rating`, `TutorSubjects`, `TutorAvailability`.
- Frontend: `SuperAdminUserModal.vue` gained Schedule (tutor-only weekly availability grid) and
  Bookings (paginated, date-filtered history) tabs, plus expanded Profile stats (rating
  distribution, recent reviews, subjects, split cancellations, top-3 counterparts). Each tab has
  its own CSV export button. Data loads lazily per tab and is cached per modal session.
- `src/stores/superadmin.js` gained six new actions (three fetch, three CSV export) following the
  existing `api.get(...)`/blob-download patterns already in that file.

## Deviations from plan

None — the brief was followed as written. Codex's own logged deviations (full Django suite not
run to completion during its session; aggregate `npm run lint` blocked by a pre-existing unrelated
issue) were reproduced and confirmed harmless during independent review.

## Fix rounds

None dispatched back to Codex. Two defects were found during independent verification and fixed
directly (cheaper than a round trip):

1. **Missing `formatTime`/`formatDateShort`.** The template called both in four places (Schedule
   grid, Bookings table) but neither was defined or imported anywhere in the file — this would
   have thrown at runtime the moment either new tab rendered. Added both as local helpers.
2. **Colliding export loading-state key.** The new `exportUserCsv` store helper reused the
   pre-existing `loading.value.export`/`error.value.export` keys, which are already bound to the
   unrelated "Export Users"/"Export Analytics" buttons on `SuperAdminUsers.vue` and
   `SuperAdminReports.vue`. Triggering any of the three new per-tab exports would have spuriously
   disabled/errored those other pages' buttons. Gave the new helper its own `userExport` key.

Neither defect was caught by the automated checks Codex ran (`npm run build`, ESLint, the Django
test suite) — both are the kind of cross-cutting/runtime issue that only surfaces by reading the
diff and reasoning about what else touches the same state, which is exactly what this review step
is for.

## Checks run

- `python manage.py test studybuddy.tests.SuperAdminUserDetailApiTests --keepdb` — 9/9 pass
  (reran independently after the fixes; matches Codex's logged evidence).
- `python manage.py test studybuddy.tests --keepdb` (full suite, 298 tests) — 28 failures + 5
  errors, all pre-existing and unrelated (payment/cash-out mocking, avatar upload, verification
  dev-tools env-var defaults). Confirmed pre-existing by reproducing the two most suspicious
  failures (`VerificationDevToolsTests`, `VerificationDevToolsAdminEndpointTests`) against the
  pre-Codex baseline via `git stash`. None of the 9 new tests appear among the failures.
- `npm run build` — green, 320 modules, no errors.
- `npm run lint:eslint -- --no-fix` — clean.
- `npm run lint` (aggregate oxlint+eslint) — blocked by pre-existing unrelated `no-undef` errors in
  `make_algo_pptx.cjs`/`make_algo_pptx.js`, neither touched by this change.

## Commits

1. `feat: add admin endpoints for user bookings, tutor schedule, and stats` (backend)
2. `feat: add Schedule and Bookings tabs to SuperAdminUserModal` (frontend, includes both fixes)
3. Docs bookkeeping (this summary, brief, plan status → Done, dashboard regeneration)

## What's next

Per the standard flow, a final whole-branch `/code-review` against the spec is the remaining gate
before this is considered fully closed out — not skipped here, just not yet run.
