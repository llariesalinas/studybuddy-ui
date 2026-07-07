# Algorithm Demo — Live Rating Edit (dev feature) — Design Spec

**Date:** 2026-07-08
**Status:** Approved
**Stack:** Vue 3 (Composition API), Django REST
**Builds on:** [2026-07-04-superadmin-algorithm-demo-design.md](2026-07-04-superadmin-algorithm-demo-design.md)

---

## Goal

Let a SuperAdmin change a contributing neighbor's rating **from inside the
Algorithm Demo page itself** (Compare Pair tab) and watch the CF score and
Hybrid Score recompute and re-animate live, without leaving the page or
opening Django admin.

This exists to make the "the algorithm updates when ratings change" point of
a thesis-defense demo self-contained: today, proving that requires editing a
`Rating` row in `/admin/` in a separate tab, then tabbing back and reloading.
This closes that gap with one inline edit.

Dev/demo-only, same as the rest of the Algorithm Demo tool — gated by the
existing `ALGORITHM_DEMO_TOOLS_ENABLED` flag and `IsSuperAdminUser`.

---

## What already exists (important)

No changes to the recommender algorithm itself.

- `CF.py`'s `build_rating_matrix()` queries `Rating.objects.select_related(...)`
  fresh from the DB on every call — there is no caching in the demo path
  (`demo.py`'s `build_algorithm_demo_recommendation` calls it directly). So
  once a `Rating.rating_score` changes in the DB, the very next
  `dev/algorithm-demo/recommend/` call already reflects it. Nothing to
  invalidate.
- `AlgorithmDemoBreakdown.vue:118-124` already renders the exact rows this
  feature needs to make editable — one line per contributing neighbor:
  `{{ neighbor.name }} — similarity {{ neighbor.similarity.toFixed(2) }},
  rated this tutor {{ neighbor.rating }}/5`. `neighbor.rating` is the
  `rating_score` `compute_cf_breakdown` (`CF.py:106-121`) pulled from that
  neighbor's `Rating` row for the currently-selected tutor.
- `update_tutor_rating_average(tutor)` (`views.py:991-994`) is the existing
  helper that recomputes `Tutor.rating_average` from all its `Rating` rows —
  reused here instead of duplicated.
- The three-endpoint staff-only pattern this follows
  (`views.py:389-421`, `urls.py:164-165`): `IsAuthenticated + IsSuperAdminUser`,
  `if not settings.ALGORITHM_DEMO_TOOLS_ENABLED: return 403` as the first line
  of the view body.

---

## Design

### 1. Data model — one new endpoint

`PATCH dev/algorithm-demo/rating/`

Request body: `{ "student_id": <int>, "tutor_id": <int>, "rating_score": <int 1-5> }`

- `student_id` is the neighbor's `UserProfile.id` (same id already returned as
  `neighbor.neighbor_id` in the `cf.neighbors` payload).
- `tutor_id` is `Tutor.profile_id` (same id already used as `tutor_id`
  throughout `demo.py`'s response rows).

View logic (`views.py`, next to the two existing algorithm-demo views):

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

Notes:
- This edits an **existing** `Rating` row only — it never creates one. If a
  student/tutor pair somehow has no `Rating` row (shouldn't happen for a row
  already showing in the neighbor list, since that list is only populated
  from `Rating` rows in the first place), it 404s rather than silently
  creating one.
- If a `(student, tutor)` pair has more than one `Rating` row (possible in
  the generic filler pool, where a tutee could book+rate the same tutor
  across two different completed sessions), this updates the most recent one
  by `id` — matching the same row `build_rating_matrix()` effectively uses,
  since that function's dict-overwrite (`ratings[student_id][tutor_id] = ...`)
  keeps whichever row the unordered queryset iterates last, which in
  practice on an untouched table is insertion/id order. This is a pre-existing
  quirk of `build_rating_matrix`, not something this feature needs to fix —
  documented here so the "it edited the wrong row" case is understood if it
  ever comes up on a filler-pool pair rather than a named persona.
- Route registration (`urls.py`, next to the other two):
  ```python
  path('dev/algorithm-demo/rating/', views.algorithm_demo_update_rating),
  ```

### 2. Component structure

```
src/components/algorithm-demo/
  AlgorithmDemoBreakdown.vue   — neighbor-list rows become editable:
                                 number input (1-5) + inline save button,
                                 replacing the static "rated this tutor X/5"
                                 text. Emits `rating-updated` on save success.
  AlgorithmDemoPairPicker.vue  — listens for `rating-updated` from the
                                 breakdown child, re-calls
                                 getAlgorithmDemoRecommendation for the
                                 current tutee (same call already used in
                                 onTuteeChange), which re-populates `rows`
                                 and re-triggers the breakdown's existing
                                 `watch(() => props.row, animate)`.
```

`AlgorithmDemoBreakdown.vue` changes, per neighbor row:
- Replace the static text with an editable `<input type="number" min="1"
  max="5">` bound to a local per-neighbor draft value, plus a small save
  icon button that only enables when the draft differs from
  `neighbor.rating`.
- On save click: call `updateAlgorithmDemoRating(neighbor.neighbor_id,
  row.tutor_id, draftValue)`, show a small inline "Saving…" / error state on
  the row itself (matching the existing `errorMessage` pattern used
  elsewhere in this component tree), then emit `rating-updated` on success.
- No optimistic update — the row's displayed value only changes once the
  parent's re-fetch returns, so what's on screen always matches the DB
  (matters for a demo: no showing a number that didn't actually save).

New API helper, `src/services/api/algorithmDemo.js`:

```js
export const updateAlgorithmDemoRating = (studentId, tutorId, ratingScore) =>
  api.patch('dev/algorithm-demo/rating/', {
    student_id: studentId,
    tutor_id: tutorId,
    rating_score: ratingScore
  })
```

### 3. Integration points

- `AlgorithmDemoPairPicker.vue` adds a handler:
  ```js
  function onRatingUpdated() {
    onTuteeChange(selectedTuteeId.value)  // re-fetch, keeps selectedTutorId as-is
  }
  ```
  Passed to `AlgorithmDemoBreakdown` as `@rating-updated="onRatingUpdated"`.
  Since `onTuteeChange` resets `selectedTutorId.value = null` today (line 44),
  it needs a small adjustment so re-running it for a refresh doesn't drop the
  currently-selected tutor: extract the fetch-and-populate body into a
  `refetchRows()` helper that `onTuteeChange` calls after resetting selection,
  and that `onRatingUpdated` calls directly without resetting
  `selectedTutorId`.
- No router changes, no new store, no changes to `Ranked List` tab — editing
  is Compare Pair only, since that's the tab with a single focused
  tutee/tutor pair and its neighbor breakdown already on screen.
- No changes to `ALGORITHM_DEMO_TOOLS_ENABLED` gating — the new endpoint
  follows the exact same check as the other two.

---

## Out of scope

- Editing any rating not currently shown in the selected pair's neighbor list
  (explicitly decided against in favor of switching tutee/tutor pairs to see
  different neighbor rows — see conversation decision record).
- A "reset to seed values" undo button — `reset_demo_data` already exists for
  that and is the documented way back to a clean state.
- Creating new `Rating` rows (e.g. rating a tutor the neighbor never actually
  booked) — out of scope; this only edits existing rows.
- Editing ratings from the Ranked List tab — Compare Pair only.
- Any change to `CF.py`, `hybrid.py`, or caching behavior — none needed.

---

## Tests to add (`backend/studybuddy/tests.py`)

1. `test_algorithm_demo_update_rating_changes_score` — PATCH with valid
   `student_id`/`tutor_id`/`rating_score` updates the `Rating` row and
   returns the new value.
2. `test_algorithm_demo_update_rating_recomputes_tutor_average` — after a
   successful PATCH, `Tutor.rating_average` reflects the new score (asserts
   `update_tutor_rating_average` was actually invoked, not just that the
   `Rating` row changed).
3. `test_algorithm_demo_update_rating_rejects_out_of_range_score` — `0` or
   `6` returns 400.
4. `test_algorithm_demo_update_rating_404_when_no_rating_exists` — a
   student/tutor pair with no `Rating` row returns 404, does not create one.
5. `test_algorithm_demo_update_rating_requires_superadmin` — same
   `IsSuperAdminUser` + `ALGORITHM_DEMO_TOOLS_ENABLED` gating test shape as
   the existing two endpoints' tests.

---

## Verification

1. `python manage.py test studybuddy.tests` — full suite green, including
   the five new cases above.
2. `npm run lint` and `npm run build` — clean.
3. With `ALGORITHM_DEMO_TOOLS_ENABLED=true` locally, after `reset_demo_data`:
   - Log in as SuperAdmin → Algorithm Demo → Compare Pair → select
     `diane.cruz@cpu.edu.ph` → `Elena Bautista`.
   - Edit one contributing neighbor's rating of Elena from `5` down to `1`,
     save, confirm the CF bar, CF score label, and Hybrid Score all
     re-animate to new (lower) values within the same page, no reload.
   - Re-select `Miguel Torres` for the same tutee, confirm his breakdown is
     unaffected by the edit made against Elena.
   - Attempt the same PATCH via a raw HTTP client while
     `ALGORITHM_DEMO_TOOLS_ENABLED=false` — confirm 403, not a stack trace.
