# Handoff - Algorithm Demo Live Rating Edit

**Date:** 2026-07-08  
**Branch:** `feat/demo-data-reset`  
**Source plan:** [docs/plans/2026-07-08-algorithm-demo-live-rating-edit-codex-handoff.md](../plans/2026-07-08-algorithm-demo-live-rating-edit-codex-handoff.md)

## What was completed

Task 1 was already present before this session and was verified in code:
- `backend/studybuddy/views.py` already contains `algorithm_demo_update_rating`
- `backend/studybuddy/urls.py` already contains `path('dev/algorithm-demo/rating/', views.algorithm_demo_update_rating)`

This session implemented Tasks 2-5:

### Backend tests

Updated [backend/studybuddy/tests.py](../../backend/studybuddy/tests.py) to add 5 new endpoint tests in `AlgorithmDemoToolTests`:
- `test_algorithm_demo_update_rating_changes_score`
- `test_algorithm_demo_update_rating_recomputes_tutor_average`
- `test_algorithm_demo_update_rating_rejects_out_of_range_score`
- `test_algorithm_demo_update_rating_404_when_no_rating_exists`
- `test_algorithm_demo_update_rating_requires_superadmin`

Also added small local test helpers/fixtures inside that class:
- `self.availability`
- `_create_rating(...)`

### Frontend API helper

Updated [src/services/api/algorithmDemo.js](../../src/services/api/algorithmDemo.js):
- added `updateAlgorithmDemoRating(studentId, tutorId, ratingScore)`

### Editable neighbor UI

Updated [src/components/algorithm-demo/AlgorithmDemoBreakdown.vue](../../src/components/algorithm-demo/AlgorithmDemoBreakdown.vue):
- imports `updateAlgorithmDemoRating`
- emits `rating-updated`
- adds per-neighbor draft/saving/error state
- replaces static neighbor text with editable number inputs + Save buttons
- shows inline error text on save failure
- preserves/reset local neighbor UI state correctly when the selected row changes

### Refetch after save

Updated [src/components/algorithm-demo/AlgorithmDemoPairPicker.vue](../../src/components/algorithm-demo/AlgorithmDemoPairPicker.vue):
- extracted recommendation fetch into `refetchRows()`
- added `onRatingUpdated()`
- wired `@rating-updated="onRatingUpdated"` into `AlgorithmDemoBreakdown`

## Verification already done

### Backend tests

Focused run of the 5 new tests passed:

```powershell
venv\Scripts\python.exe manage.py test --keepdb \
  studybuddy.tests.AlgorithmDemoToolTests.test_algorithm_demo_update_rating_changes_score \
  studybuddy.tests.AlgorithmDemoToolTests.test_algorithm_demo_update_rating_recomputes_tutor_average \
  studybuddy.tests.AlgorithmDemoToolTests.test_algorithm_demo_update_rating_rejects_out_of_range_score \
  studybuddy.tests.AlgorithmDemoToolTests.test_algorithm_demo_update_rating_404_when_no_rating_exists \
  studybuddy.tests.AlgorithmDemoToolTests.test_algorithm_demo_update_rating_requires_superadmin
```

Result: `Ran 5 tests ... OK`

Notes:
- A first attempt to run the whole `AlgorithmDemoToolTests` class surfaced **pre-existing unrelated failures** in older recommendation tests in that class.
- The new tests initially failed because they used `self.tutor.id`; this repo's `Tutor` is keyed by `profile_id`, so the tests were corrected to use `self.tutor.pk`.

### Frontend verification

Focused lint on the changed files passed:

```powershell
.\node_modules\.bin\oxlint.cmd src/services/api/algorithmDemo.js src/components/algorithm-demo/AlgorithmDemoBreakdown.vue src/components/algorithm-demo/AlgorithmDemoPairPicker.vue
.\node_modules\.bin\eslint.cmd src/services/api/algorithmDemo.js src/components/algorithm-demo/AlgorithmDemoBreakdown.vue src/components/algorithm-demo/AlgorithmDemoPairPicker.vue
```

`npm run build` also passed.

Full `npm run lint` is still blocked by a **pre-existing unrelated** error in [src/router/index.js](../../src/router/index.js):
- unused `from` parameter in `router.beforeEach(async (to, from) => { ... })`

### Manual live verification

Manual browser verification was performed successfully against the local app:

1. Logged into the local app as `superadmin@studybuddy.test`
2. Reset that local account's password to `studybuddy123` for testing
3. Opened `/superadmin/algorithm-demo`
4. Selected `Diane Cruz`
5. Verified the Compare Pair flow and inline editable neighbor controls
6. Confirmed the Save button enters a `Saving...` state
7. Confirmed a successful save triggers a refetch and updates the displayed scores live
8. Verified Elena's score changed after lowering a neighbor rating further:
   - Elena hybrid score observed at `0.739` before the second manual edit
   - after lowering another neighbor rating to `1`, Elena updated to `0.712`
   - the tutor picker label also updated to `Elena Bautista (score 0.71)`
9. Switched to `Miguel Torres` for the same tutee and confirmed a different unaffected breakdown:
   - observed `Miguel Torres (score 0.77)`
   - observed hybrid `0.770`
10. Verified the flag-off gate separately by running a second backend on `8001` with `ALGORITHM_DEMO_TOOLS_ENABLED=false` and issuing a direct authenticated PATCH:
   - response: `{"error":"Algorithm demo tools are disabled."}`

Important nuance:
- During browser testing, the first inline save attempt hit stale local backend state because an older process was still bound to `8000`.
- After restarting the correct backend on `8000`, the flow behaved as expected.

## What is still not done

### 1. No task commits were created

The handoff plan asked for per-task commits after Tasks 2-5. Those commits were **not** made in this session.

Current uncommitted working tree:
- `backend/studybuddy/tests.py`
- `src/components/algorithm-demo/AlgorithmDemoBreakdown.vue`
- `src/components/algorithm-demo/AlgorithmDemoPairPicker.vue`
- `src/services/api/algorithmDemo.js`

### 2. Final demo-data reset was not completed

The final cleanup step from Task 6 was started, but not completed.

Attempted command:

```powershell
venv\Scripts\python.exe manage.py reset_demo_data --noinput
```

Result:
- failed immediately because `reset_demo_data` does **not** support `--noinput`
- no cleanup reseed was performed by that command

### 3. The repo handoff was not yet written before this file

This file is that missing handoff.

## Current runtime state at handoff

As of this handoff, local dev processes are still running:

- frontend Vite server on `127.0.0.1:5173`
- backend dev server on `127.0.0.1:8000`
- second backend dev server on `127.0.0.1:8001` for the flag-off `403` verification

The browser session used for manual verification was left active during the interrupted session.

## Exact next steps

1. Decide whether to keep or stop the running local servers on `5173`, `8000`, and `8001`.
2. Run the real demo reset command **without** `--noinput` from [backend](../../backend/):

```powershell
venv\Scripts\python.exe manage.py reset_demo_data
```

3. Confirm the reseed completes successfully.
4. Optionally do one quick post-reset spot check in the UI:
   - `Diane Cruz`
   - `Elena Bautista`
   - confirm the baseline seeded score is back to the original demo state
5. If the user wants the plan followed exactly, create the missing commits:
   - tests
   - API helper
   - breakdown UI
   - pair picker refetch wiring
6. If desired, write the final session summary version and update plan status/tracker docs.

## Manual verification guide

If someone needs to rerun the remaining manual verification from scratch:

1. Start backend on `8000` with `ALGORITHM_DEMO_TOOLS_ENABLED=true`.
2. Start frontend on `5173`.
3. Log in as a SuperAdmin.
4. Navigate to `/superadmin/algorithm-demo`.
5. Switch to `Compare Pair`.
6. Pick tutee `Diane Cruz`.
7. Pick tutor `Elena Bautista`.
8. Confirm neighbor rows show:
   - number inputs
   - Save buttons
9. Change one neighbor rating to `1`.
10. Click `Save`.
11. Confirm:
   - button briefly shows `Saving...`
   - no page reload
   - CF/hybrid breakdown updates
   - tutor picker score updates too
12. Switch tutor to `Miguel Torres`.
13. Confirm Miguel's breakdown is still different and not overwritten by Elena's edit.
14. For the gate check, run a second backend with the flag off on `8001` and confirm direct PATCH returns `403` JSON.

## Deviations from the original task handoff

- The original handoff asked for `npm run lint` clean. Full repo lint is still blocked by a pre-existing unrelated router lint issue, but the edited files themselves lint clean and the app builds.
- The original handoff asked for commits after each task. Those commits were not created.
- The original handoff asked to re-run `reset_demo_data` afterward. That was attempted with the wrong flag and therefore did not complete.
