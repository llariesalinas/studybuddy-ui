# Codex Handoff — Algorithm Demo Live Rating Edit

## Status & Progress Summary
**Status:** Ready for Codex execution. Task 1 (backend PATCH endpoint) is already implemented and committed. Tasks 2–6 are not started.
**Next step:** Give this document to Codex CLI. Skip Task 1 (already done — see note below), execute Tasks 2–6 in order, committing after each. Report back per the "Report back" section at the end.

**Note on Task 1:** the `algorithm_demo_update_rating` view and its `dev/algorithm-demo/rating/` route already exist in `backend/studybuddy/views.py` / `backend/studybuddy/urls.py`, committed as `feat: add staff-only endpoint to edit algorithm demo ratings`. Verify it matches Task 1's code below before moving on (it should — it was transcribed from this same plan), then start execution at Task 2.

---

## Context

Repo root: `C:\FIles\Studybuddy\FrontEnd\studybuddy-ui`
Stack: Vue 3 (Composition API) + Pinia frontend, Django REST backend. Backend lives in `backend/`, frontend in `src/`.
Current branch: `feat/demo-data-reset` (not main — fine to keep committing here unless told otherwise).

This project has a SuperAdmin-only "Algorithm Demo" page at `/superadmin/algorithm-demo` that replays a real hybrid tutor recommender (CBF + CF) against seeded thesis-defense data, so a presenter can show how the algorithm ranks tutors for a given tutee. It has two tabs: Ranked List and Compare Pair. Compare Pair shows, for a chosen tutee/tutor pair, an animated breakdown of the CBF sub-scores, the CF (collaborative filtering) score, and the final Hybrid Score, including a list of the tutee's "Top-K Neighbors" (similar students) who contributed to the CF score, each shown with their name, similarity, and their own rating of that tutor.

**The feature being added:** let a SuperAdmin edit one of those neighbor ratings directly on the Compare Pair page (instead of going to Django admin in a separate tab), and see the CF/Hybrid numbers recompute and re-animate live. This is a dev/demo-only feature — it's gated behind the same `ALGORITHM_DEMO_TOOLS_ENABLED` Django setting and `IsSuperAdminUser` permission the rest of the page already uses.

**Full design rationale** (read if anything below is unclear, but the task steps here are self-contained and should not require it): `docs/specs/2026-07-08-algorithm-demo-live-rating-edit-design.md`

**Full task plan this handoff is transcribed from** (same content, kept in sync — treat this handoff file as the one to execute from): `docs/plans/2026-07-08-algorithm-demo-live-rating-edit.md`

---

## Relevant existing files (read before editing)

- `backend/studybuddy/views.py` — search for `algorithm_demo_search_tutees` and `algorithm_demo_recommend` (near line 389–421). These are the two existing staff-only endpoints for this page. Your new endpoint goes directly after `algorithm_demo_recommend`, following the exact same pattern: `@api_view([...])`, `@permission_classes([IsAuthenticated, IsSuperAdminUser])`, and `if not settings.ALGORITHM_DEMO_TOOLS_ENABLED: return Response({"error": "..."}, status=403)` as the first line of the function body.
- `backend/studybuddy/views.py` — search for `def update_tutor_rating_average(tutor):` (near line 991). Reuse this existing helper; do not duplicate its logic.
- `backend/studybuddy/urls.py` — search for `dev/algorithm-demo/` (near line 164–165) to find where the two existing routes are registered.
- `backend/studybuddy/models.py` — search for `class Rating(models.Model):` (near line 1066) to confirm field names (`student`, `tutor`, `rating_score`).
- `src/services/api/algorithmDemo.js` — the existing API helper file for this feature; follow its existing export style exactly.
- `src/components/algorithm-demo/AlgorithmDemoBreakdown.vue` — search for the `neighbor-list` div (around line 118–124) — this is the static text block you're making editable.
- `src/components/algorithm-demo/AlgorithmDemoPairPicker.vue` — the parent component that fetches recommendation data and passes `:row` to `AlgorithmDemoBreakdown`. Search for `onTuteeChange` (around line 42–61).

---

## Task 1 — Backend: new PATCH endpoint to edit a rating

**Files:**
- Modify: `backend/studybuddy/views.py`
- Modify: `backend/studybuddy/urls.py`

Steps:
1. In `backend/studybuddy/views.py`, immediately after the existing `algorithm_demo_recommend` view, add:
   ```python
   @api_view(['PATCH'])
   @permission_classes([IsAuthenticated, IsSuperAdminUser])
   def algorithm_demo_update_rating(request):
       if not settings.ALGORITHM_DEMO_TOOLS_ENABLED:
           return Response({"error": "Algorithm demo tools are disabled."}, status=403)

       student_id = request.data.get('student_id')
       tutor_id = request.data.get('tutor_id')
       try:
           rating_score = int(request.data.get('rating_score'))
       except (TypeError, ValueError):
           return Response({"error": "A valid rating_score is required."}, status=400)
       if rating_score < 1 or rating_score > 5:
           return Response({"error": "rating_score must be between 1 and 5."}, status=400)

       rating = Rating.objects.filter(
           student_id=student_id, tutor_id=tutor_id
       ).order_by('-id').first()
       if rating is None:
           return Response({"error": "No existing rating found for this pair."}, status=404)

       rating.rating_score = rating_score
       rating.save(update_fields=['rating_score'])
       update_tutor_rating_average(rating.tutor)
       return Response({"ok": True, "rating_score": rating.rating_score})
   ```
   `Rating` and `update_tutor_rating_average` already exist in this file — confirm `Rating` is imported at the top (it's used elsewhere in `views.py`, e.g. in `submit_rating`); if not already imported, add it to whichever existing import statement already imports sibling models (do not create a new import line for it alone).
2. In `backend/studybuddy/urls.py`, add immediately after the two existing algorithm-demo routes:
   ```python
   path('dev/algorithm-demo/rating/', views.algorithm_demo_update_rating),
   ```
3. Verify: `cd backend && venv\Scripts\python.exe manage.py check` — must run clean, no errors.
4. Commit: `git add backend/studybuddy/views.py backend/studybuddy/urls.py && git commit -m "feat: add staff-only endpoint to edit algorithm demo ratings"`

---

## Task 2 — Backend: tests for the new endpoint

**Files:**
- Modify: `backend/studybuddy/tests.py`

Find the existing test class covering `algorithm_demo_search_tutees` / `algorithm_demo_recommend` (search `algorithm_demo` in `tests.py`) and add these as new test methods in that same class, reusing its existing `setUp()` and the same `ALGORITHM_DEMO_TOOLS_ENABLED` override pattern already used by that class's tests.

1. `test_algorithm_demo_update_rating_changes_score`:
   - Arrange a `Rating` row for a known `(student, tutor)` pair with `rating_score=3`.
   - PATCH `dev/algorithm-demo/rating/` with `{student_id, tutor_id, rating_score: 5}` as the SuperAdmin test client, with the demo-tools flag enabled (matching this class's existing override style).
   - Assert response status `200` and body `{"ok": True, "rating_score": 5}`.
   - Refresh the `Rating` row from the DB (`.refresh_from_db()`), assert `rating_score == 5`.
2. `test_algorithm_demo_update_rating_recomputes_tutor_average`:
   - Same setup. After the PATCH, refresh the `Tutor` row from the DB and assert `rating_average` now matches the recalculated average across that tutor's `Rating` rows (not the pre-edit value) — this proves `update_tutor_rating_average` actually ran.
3. `test_algorithm_demo_update_rating_rejects_out_of_range_score`:
   - PATCH with `rating_score: 0` → assert `400`.
   - PATCH with `rating_score: 6` → assert `400`.
4. `test_algorithm_demo_update_rating_404_when_no_rating_exists`:
   - PATCH with a `student_id`/`tutor_id` pair that has no `Rating` row → assert `404`.
   - Assert `Rating.objects.filter(student_id=..., tutor_id=...).count() == 0` both before and after the PATCH (proves nothing was created).
5. `test_algorithm_demo_update_rating_requires_superadmin`:
   - Match this test class's existing gating-test shape for the other two algorithm-demo endpoints: a non-SuperAdmin authenticated client → `403`; a SuperAdmin client with `ALGORITHM_DEMO_TOOLS_ENABLED` off → `403`.

Verify: `cd backend && venv\Scripts\python.exe manage.py test studybuddy.tests` passes, including all 5 new tests. (The full suite may have pre-existing unrelated failures in this repo — if so, confirm your 5 new tests specifically pass and that you have not introduced new failures beyond what existed before your change, e.g. by running the suite once on the commit before Task 1 if you're unsure of the baseline.)

Commit: `git add backend/studybuddy/tests.py && git commit -m "test: cover algorithm demo rating-edit endpoint"`

---

## Task 3 — Frontend: API helper

**Files:**
- Modify: `src/services/api/algorithmDemo.js`

1. Add, following the existing two exports' style in this file exactly (same `api.<method>` call shape, same arrow-function export style):
   ```js
   export const updateAlgorithmDemoRating = (studentId, tutorId, ratingScore) =>
     api.patch('dev/algorithm-demo/rating/', {
       student_id: studentId,
       tutor_id: tutorId,
       rating_score: ratingScore
     })
   ```
2. Verify: `npm run lint` clean.
3. Commit: `git add src/services/api/algorithmDemo.js && git commit -m "feat: add algorithm demo rating-update API helper"`

---

## Task 4 — Frontend: editable neighbor rows in AlgorithmDemoBreakdown.vue

**Files:**
- Modify: `src/components/algorithm-demo/AlgorithmDemoBreakdown.vue`

Depends on Task 3 (imports `updateAlgorithmDemoRating` from it).

1. Add the import: `import { updateAlgorithmDemoRating } from '@/services/api/algorithmDemo'`.
2. Add `defineEmits(['rating-updated'])`.
3. Add local reactive state for the per-neighbor edit UI, alongside the existing `bars`/`cfBar`/etc. reactive state in this component's `<script setup>`:
   ```js
   const neighborDrafts = reactive({})   // { [neighbor_id]: draftScore }
   const neighborSaving = reactive({})   // { [neighbor_id]: boolean }
   const neighborError = reactive({})    // { [neighbor_id]: string }
   ```
4. In the existing `animate(row)` function (search for `function animate(row)`), alongside the existing `resetBars()` call, initialize the draft state for the new row: iterate `row.cf.neighbors` and set `neighborDrafts[n.neighbor_id] = n.rating` for each; clear any `neighborSaving`/`neighborError` entries whose keys are not in the new row's neighbor list (so stale UI state from a previously-viewed tutor doesn't leak into the newly-selected one).
5. Add a save function:
   ```js
   async function saveNeighborRating(neighbor) {
     const draft = neighborDrafts[neighbor.neighbor_id]
     neighborSaving[neighbor.neighbor_id] = true
     neighborError[neighbor.neighbor_id] = ''
     try {
       await updateAlgorithmDemoRating(neighbor.neighbor_id, props.row.tutor_id, draft)
       emit('rating-updated')
     } catch (err) {
       neighborError[neighbor.neighbor_id] =
         err.response?.data?.error || 'Could not save this rating.'
     } finally {
       neighborSaving[neighbor.neighbor_id] = false
     }
   }
   ```
6. Replace the current static neighbor-list line:
   ```html
   {{ neighbor.name }} — similarity {{ neighbor.similarity.toFixed(2) }}, rated this tutor
   {{ neighbor.rating }}/5
   ```
   with:
   ```html
   <div v-for="neighbor in row.cf.neighbors" :key="neighbor.neighbor_id" class="neighbor-row">
     <span>{{ neighbor.name }} — similarity {{ neighbor.similarity.toFixed(2) }}, rated this tutor</span>
     <input
       type="number"
       min="1"
       max="5"
       class="neighbor-rating-input"
       v-model.number="neighborDrafts[neighbor.neighbor_id]"
     />
     <button
       type="button"
       class="neighbor-save-btn"
       :disabled="neighborSaving[neighbor.neighbor_id] || neighborDrafts[neighbor.neighbor_id] === neighbor.rating"
       @click="saveNeighborRating(neighbor)"
     >
       {{ neighborSaving[neighbor.neighbor_id] ? 'Saving…' : 'Save' }}
     </button>
     <span v-if="neighborError[neighbor.neighbor_id]" class="neighbor-error">
       {{ neighborError[neighbor.neighbor_id] }}
     </span>
   </div>
   ```
   (This replaces the existing `v-for` that currently renders that static line — do not add a second `v-for`, edit the existing one in place.)
7. Add scoped CSS for the four new classes in this component's existing `<style scoped>` block, matching the file's existing visual conventions (it already uses CSS custom properties like `--sb-card-border`, `--sb-text-muted`, `--sb-danger` — do not hardcode hex colors):
   - `.neighbor-row` — flex row, `align-items: center`, small gap (match existing `.neighbor-list` spacing in this file).
   - `.neighbor-rating-input` — small fixed width (e.g. `56px`), bordered with `var(--sb-card-border)`.
   - `.neighbor-save-btn` — small pill button; check `.claude/skills/shadcn-components.md` for this project's `.sb-btn-pill` convention and reuse it if it fits, otherwise a minimal small button consistent with this file's existing button-less style.
   - `.neighbor-error` — `color: var(--sb-danger); font-size: 11px;`
8. Verify: `npm run lint` clean, no unused imports/vars.
9. Commit: `git add src/components/algorithm-demo/AlgorithmDemoBreakdown.vue && git commit -m "feat: make algorithm demo neighbor ratings inline-editable"`

---

## Task 5 — Frontend: wire refetch-on-save in AlgorithmDemoPairPicker.vue

**Files:**
- Modify: `src/components/algorithm-demo/AlgorithmDemoPairPicker.vue`

Depends on Task 4 (listens for the `rating-updated` event it emits).

1. Extract the fetch-and-populate body of the existing `onTuteeChange` function into a standalone `refetchRows()` that does NOT reset `selectedTutorId`:
   ```js
   async function refetchRows() {
     if (!selectedTuteeId.value) return
     loading.value = true
     errorMessage.value = ''
     try {
       const { data } = await getAlgorithmDemoRecommendation(selectedTuteeId.value, props.institutionId)
       rows.value = data.rows
       reason.value = data.reason
     } catch (err) {
       errorMessage.value = err.response?.data?.error || 'Could not load candidate tutors.'
     } finally {
       loading.value = false
     }
   }

   async function onTuteeChange(tuteeId) {
     selectedTuteeId.value = tuteeId
     selectedTutorId.value = null
     rows.value = []
     reason.value = null
     errorMessage.value = ''
     if (!tuteeId) return
     await refetchRows()
   }
   ```
   (This replaces the existing `onTuteeChange` function body — reuse its existing try/catch error-handling logic verbatim inside `refetchRows`, just don't duplicate the reset lines that now live only in `onTuteeChange`.)
2. Add a handler:
   ```js
   function onRatingUpdated() {
     refetchRows()
   }
   ```
3. In the template, change:
   ```html
   <AlgorithmDemoBreakdown :row="selectedRow" />
   ```
   to:
   ```html
   <AlgorithmDemoBreakdown :row="selectedRow" @rating-updated="onRatingUpdated" />
   ```
4. `selectedRow` is a computed matching `row.tutor_id === selectedTutorId.value` against the `rows` array — since `refetchRows()` repopulates `rows` with a fresh array but does not touch `selectedTutorId`, `selectedRow` should re-resolve correctly to the same tutor's updated row automatically. Confirm this holds during Task 6's manual verification rather than assuming it from reading the code alone.
5. Verify: `npm run lint` clean.
6. Commit: `git add src/components/algorithm-demo/AlgorithmDemoPairPicker.vue && git commit -m "feat: refetch algorithm demo breakdown after a rating edit"`

---

## Task 6 — End-to-end manual verification

No files changed in this task — it's a live check.

1. Backend: ensure `ALGORITHM_DEMO_TOOLS_ENABLED=true` is set in the local `.env` used by the Django server, then run `cd backend && venv\Scripts\python.exe manage.py runserver 8000`.
2. If the local dev database doesn't already have the thesis demo personas seeded, run `venv\Scripts\python.exe manage.py reset_demo_data` first (this is destructive to existing Tutee/Tutor demo data — only run it against a local/dev database, and only if you don't already have the seeded personas).
3. Frontend: `npm run dev`.
4. Log in as the existing SuperAdmin account, navigate to `/superadmin/algorithm-demo` → Compare Pair tab.
5. Select tutee `diane.cruz@cpu.edu.ph`, tutor `Elena Bautista`. Confirm the neighbor list now shows editable number inputs + Save buttons instead of static text.
6. Change one neighbor's rating value down to `1`, click Save. Confirm: the button shows "Saving…" briefly, then the CF bar/label and Hybrid Score visibly re-animate to new (lower) values, with no page reload.
7. Re-select `Miguel Torres` for the same tutee. Confirm his breakdown is unaffected by the edit made against Elena (this proves the PATCH correctly scoped to the `(student, tutor)` pair it was called with).
8. Attempt the same PATCH request directly (e.g. via `curl` or browser devtools) while `ALGORITHM_DEMO_TOOLS_ENABLED=false` — confirm a clean `403` JSON response, not a stack trace or blank screen.
9. Re-run `reset_demo_data` afterward to restore clean seed values before any further demo/testing work continues on this database.

---

## Risks / things to watch for

- If a `(student, tutor)` pair somehow has more than one `Rating` row (possible in the generic filler pool seeded by `reset_demo_data.py`, though not for the named thesis personas used in Task 6's verification), the endpoint edits the most-recently-inserted one by `id`. This is a pre-existing quirk of how `CF.py`'s `build_rating_matrix()` picks a rating for a given pair (last one iterated wins) — not something this feature needs to fix, just be aware the edited row and the row CF actually uses could theoretically diverge on a filler-pool pair. Not expected to matter for the named personas this feature is built to demo against.
- Reset `neighborDrafts`/`neighborSaving`/`neighborError` state correctly when the selected row changes (Task 4, step 4) — otherwise switching tutors mid-edit could leave stale "Saving…" or error text visible against the wrong tutor's neighbor list. Explicitly check this during Task 6's manual verification (switch tutee/tutor mid-edit, confirm no stale UI state persists).

---

## Report back

After completing all 6 tasks, write a short summary covering:
- Commits created (short SHA + one-line message) for each task.
- Backend test results: command run and pass/fail counts, noting any pre-existing unrelated failures separately from your new tests.
- Lint/build results: `npm run lint` and `npm run build` output status.
- Manual verification (Task 6): confirm each of steps 5–9 passed, and flag anything that didn't behave as expected.
- Any deviations from this handoff and why.

If you get blocked or something in this handoff doesn't match what you find in the actual files (e.g. a line-number reference is stale, a function name has changed), stop and describe the mismatch rather than guessing — this handoff was written against the codebase state as of 2026-07-08 and the plan/spec docs listed above are the source of truth if anything drifted.

---

## Changelog

- 2026-07-08: Created — transcribed from the approved plan/spec into a single self-contained document for Codex CLI to execute directly, after switching away from in-session Claude subagent execution.
- 2026-07-08: Discovered Task 1 was already implemented as uncommitted working-tree changes (matching this doc's Task 1 exactly); committed it and updated the summary so Codex starts at Task 2.
