---
title: Algorithm Demo — Live Rating Edit
date: 2026-07-08
status: In Progress
spec: ../specs/2026-07-08-algorithm-demo-live-rating-edit-design.md
---

# Algorithm Demo — Live Rating Edit Implementation Plan

> **For agentic workers:** Use superpowers:subagent-driven-development to execute task-by-task.

**Goal:** Let a SuperAdmin edit a contributing neighbor's rating inline in the Algorithm Demo's Compare Pair tab and watch the CF/hybrid breakdown recompute live, without leaving the page.
**Stack:** Vue 3, Pinia, Django REST, Bootstrap 5

---

## Status / Progress Summary

Plan approved from spec; about to begin execution via subagent-driven-development, starting with Task 1 (backend endpoint). No tasks completed yet.

## Changelog

- 2026-07-08: Plan created from the approved spec.
- 2026-07-08: Marked In Progress — beginning Task 1.

---

### Task 1: Backend — new PATCH endpoint to edit a rating

**Files:**
- Modify: `backend/studybuddy/views.py`
- Modify: `backend/studybuddy/urls.py`

- [ ] Step 1: In `backend/studybuddy/views.py`, in the "Recommendation algorithm demo tool (staff-only)" section (near line 389, right after `algorithm_demo_recommend`), add:
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
  `Rating` and `update_tutor_rating_average` are already defined/imported in this file (confirm — `Rating` is used elsewhere in `views.py`, e.g. `submit_rating`; `update_tutor_rating_average` is defined at line ~991). No new imports needed.
- [ ] Step 2: In `backend/studybuddy/urls.py`, add the route right after the existing two algorithm-demo routes (near line 165):
  ```python
  path('dev/algorithm-demo/rating/', views.algorithm_demo_update_rating),
  ```
- [ ] Step 3: Verify — `cd backend && venv\Scripts\python.exe manage.py check` runs clean (no import/syntax errors).
- [ ] Step 4: Commit — `git commit -m "feat: add staff-only endpoint to edit algorithm demo ratings"`

---

### Task 2: Backend tests for the new endpoint

**Files:**
- Modify: `backend/studybuddy/tests.py`

Follow the existing test class/setup pattern already used for
`algorithm_demo_search_tutees` / `algorithm_demo_recommend` in this file (same
`ALGORITHM_DEMO_TOOLS_ENABLED` override pattern, same SuperAdmin test client
setup) — find that test class first and add these as new test methods in it,
reusing its `setUp`.

- [ ] Step 1: Add `test_algorithm_demo_update_rating_changes_score`:
  - Arrange a `Rating` row for a known `(student, tutor)` pair with
    `rating_score=3`.
  - PATCH `dev/algorithm-demo/rating/` with `{student_id, tutor_id,
    rating_score: 5}` as the SuperAdmin test client, with
    `ALGORITHM_DEMO_TOOLS_ENABLED=True` (matching the existing tests'
    override style).
  - Assert response `200`, `{"ok": True, "rating_score": 5}`.
  - Refresh the `Rating` row from the DB, assert `rating_score == 5`.
- [ ] Step 2: Add `test_algorithm_demo_update_rating_recomputes_tutor_average`:
  - Same setup, but assert `tutor.rating_average` (refreshed from DB) changed
    to match the new average across that tutor's `Rating` rows after the
    PATCH — proves `update_tutor_rating_average` was actually invoked, not
    just that the `Rating` row changed.
- [ ] Step 3: Add `test_algorithm_demo_update_rating_rejects_out_of_range_score`:
  - PATCH with `rating_score: 0` → assert `400`.
  - PATCH with `rating_score: 6` → assert `400`.
- [ ] Step 4: Add `test_algorithm_demo_update_rating_404_when_no_rating_exists`:
  - PATCH with a `student_id`/`tutor_id` pair that has no `Rating` row →
    assert `404`, and assert no `Rating` row was created (`Rating.objects.filter(...).count() == 0` before and after).
- [ ] Step 5: Add `test_algorithm_demo_update_rating_requires_superadmin`:
  - Same shape as this file's existing gating tests for the other two
    algorithm-demo endpoints (non-SuperAdmin client → 403; `ALGORITHM_DEMO_TOOLS_ENABLED=False` → 403 even as SuperAdmin).
- [ ] Step 6: Verify — `cd backend && venv\Scripts\python.exe manage.py test studybuddy.tests` passes, including all 5 new tests.
- [ ] Step 7: Commit — `git commit -m "test: cover algorithm demo rating-edit endpoint"`

---

### Task 3: Frontend — API helper

**Files:**
- Modify: `src/services/api/algorithmDemo.js`

- [ ] Step 1: Add, following the existing two exports' style in this file:
  ```js
  export const updateAlgorithmDemoRating = (studentId, tutorId, ratingScore) =>
    api.patch('dev/algorithm-demo/rating/', {
      student_id: studentId,
      tutor_id: tutorId,
      rating_score: ratingScore
    })
  ```
- [ ] Step 2: Verify — `npm run lint` clean on this file.
- [ ] Step 3: Commit — `git commit -m "feat: add algorithm demo rating-update API helper"`

*(Depends on Task 1 for the endpoint to exist, but can be implemented/committed independently since it's just an Axios call shape.)*

---

### Task 4: Frontend — editable neighbor rows in AlgorithmDemoBreakdown.vue

**Files:**
- Modify: `src/components/algorithm-demo/AlgorithmDemoBreakdown.vue`

Depends on Task 3 (imports `updateAlgorithmDemoRating`).

- [ ] Step 1: Add the import: `import { updateAlgorithmDemoRating } from '@/services/api/algorithmDemo'`.
- [ ] Step 2: Define `defineEmits(['rating-updated'])`.
- [ ] Step 3: Add local reactive state for the per-neighbor edit UI:
  ```js
  const neighborDrafts = reactive({})     // { [neighbor_id]: draftScore }
  const neighborSaving = reactive({})     // { [neighbor_id]: boolean }
  const neighborError = reactive({})      // { [neighbor_id]: string }
  ```
  Initialize/reset `neighborDrafts[neighbor.neighbor_id]` to `neighbor.rating`
  whenever `row` changes (in the existing `animate(row)` function, alongside
  `resetBars()` — iterate `row.cf.neighbors` and set
  `neighborDrafts[n.neighbor_id] = n.rating`, clear any stale
  `neighborSaving`/`neighborError` entries for neighbor ids not in the new
  row).
- [ ] Step 4: Add a `saveNeighborRating(neighbor)` function:
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
- [ ] Step 5: Replace the static neighbor-list line (current lines ~120-123):
  ```html
  {{ neighbor.name }} — similarity {{ neighbor.similarity.toFixed(2) }}, rated this tutor
  {{ neighbor.rating }}/5
  ```
  with an editable version:
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
- [ ] Step 6: Add scoped styles for `.neighbor-row` (flex row, gap, align-items center — match the existing `.neighbor-list` spacing already in this file), `.neighbor-rating-input` (small width, e.g. `56px`, matching existing input styling conventions in this codebase — check `src/assets` for the shared input class if one exists, otherwise a minimal bordered input using `--sb-card-border`), `.neighbor-save-btn` (reuse `.sb-btn-pill` pattern per `.claude/skills/shadcn-components.md` if applicable), `.neighbor-error` (color `var(--sb-danger)`, font-size `11px`).
- [ ] Step 7: Verify — `npm run lint` clean; no unused imports/vars.
- [ ] Step 8: Commit — `git commit -m "feat: make algorithm demo neighbor ratings inline-editable"`

---

### Task 5: Frontend — wire refetch-on-save in AlgorithmDemoPairPicker.vue

**Files:**
- Modify: `src/components/algorithm-demo/AlgorithmDemoPairPicker.vue`

Depends on Task 4 (the `rating-updated` event must exist to listen for it).

- [ ] Step 1: Extract the fetch-and-populate body of `onTuteeChange` (current
  lines 42-61) into a standalone `refetchRows()` that fetches rows for
  `selectedTuteeId.value` and populates `rows`/`reason`/`errorMessage`
  without touching `selectedTutorId`:
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
- [ ] Step 2: Add `onRatingUpdated`:
  ```js
  function onRatingUpdated() {
    refetchRows()
  }
  ```
- [ ] Step 3: Pass the handler down to the breakdown child. In the template,
  the `<AlgorithmDemoBreakdown :row="selectedRow" />` line becomes:
  ```html
  <AlgorithmDemoBreakdown :row="selectedRow" @rating-updated="onRatingUpdated" />
  ```
- [ ] Step 4: Confirm `selectedRow` (computed from `rows` + `selectedTutorId`)
  still resolves correctly after `refetchRows()` repopulates `rows` with a
  new array — since it matches by `row.tutor_id === selectedTutorId.value`
  and `selectedTutorId` is untouched by `refetchRows`, this should just work;
  verify by manual test in Task 6 rather than assuming.
- [ ] Step 5: Verify — `npm run lint` clean.
- [ ] Step 6: Commit — `git commit -m "feat: refetch algorithm demo breakdown after a rating edit"`

---

### Task 6: End-to-end manual verification

**Files:** none (verification only)

- [ ] Step 1: Backend: set `ALGORITHM_DEMO_TOOLS_ENABLED=true` in the local
  `.env`, run `cd backend && venv\Scripts\python.exe manage.py runserver 8000`.
- [ ] Step 2: If the local DB doesn't already have the thesis demo personas,
  run `venv\Scripts\python.exe manage.py reset_demo_data`.
- [ ] Step 3: Frontend: `npm run dev`.
- [ ] Step 4: Log in as the existing SuperAdmin account, navigate to
  `/superadmin/algorithm-demo` → Compare Pair tab.
- [ ] Step 5: Select tutee `diane.cruz@cpu.edu.ph`, tutor `Elena Bautista`.
  Confirm the neighbor list now shows editable number inputs + Save buttons
  instead of static text.
- [ ] Step 6: Change one neighbor's rating from its current value down to
  `1`, click Save. Confirm: the button shows "Saving…" briefly, then the CF
  bar/label and Hybrid Score re-animate to new (lower) values without a page
  reload.
- [ ] Step 7: Re-select `Miguel Torres` for the same tutee. Confirm his
  breakdown is unaffected by the edit made against Elena (proves the PATCH
  scoped to the right `(student, tutor)` pair).
- [ ] Step 8: With browser devtools or `curl`, attempt the same PATCH while
  `ALGORITHM_DEMO_TOOLS_ENABLED=false` — confirm `403`, not a stack trace or
  blank screen.
- [ ] Step 9: Re-run `reset_demo_data` afterward to restore clean seed values
  before any other demo/testing work continues.

---

## Risks

- If a `(student, tutor)` pair has more than one `Rating` row (possible in
  the generic filler pool), the endpoint edits the most-recently-inserted one
  by `id`, which should match what `build_rating_matrix()` effectively uses —
  but this is unverified for filler-pool pairs specifically. Low risk since
  the demo's real usage is against the named personas (Bea/Carlo/Diane ×
  Miguel/Elena/anchors), which each have exactly one `Rating` row per pair by
  construction in `reset_demo_data.py`.
- `neighborDrafts`/`neighborSaving`/`neighborError` keyed by `neighbor_id`
  need to be reset when `row` changes (Task 4, Step 3) or stale saving/error
  state could leak across a tutor switch — covered explicitly in the plan,
  worth double-checking during Task 6 manual verification (switch tutors
  mid-edit, confirm no stale "Saving…" state persists).

## Checks to run

- `cd backend && venv\Scripts\python.exe manage.py test studybuddy.tests` — full suite green.
- `npm run lint` — clean.
- `npm run build` — clean.
- Manual verification per Task 6.
