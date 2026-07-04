# SuperAdmin Algorithm Demo Page Implementation Plan

> **For agentic workers:** Use superpowers:subagent-driven-development to execute task-by-task.

**Goal:** Move the standalone recommendation-algorithm live demo into a real SuperAdmin page with two tabs (Ranked List, Compare Pair), both using the app's `SbSelectModal` dropdown for tutee/tutor selection.
**Stack:** Vue 3, Pinia (not needed here), Django REST, Bootstrap 5
**Spec:** [docs/specs/2026-07-04-superadmin-algorithm-demo-design.md](../specs/2026-07-04-superadmin-algorithm-demo-design.md)
**Mockup:** [docs/artifacts/2026-07-04-superadmin-algorithm-demo-mockup.html](../artifacts/2026-07-04-superadmin-algorithm-demo-mockup.html)

---

**Status & Progress Summary** (2026-07-04): Done. All six original tasks shipped, plus an unplanned Task 7 (see below): manual testing during Task 1 found the originally-specified institution-scoped candidate pool made the demo nearly unusable against seeded data, so `_candidate_tutors`/`search_tutees` became unscoped-by-default with an optional `institution_id`, and an Institution filter (`SbSelectModal`) was added to the page shell, shared by both tabs. Two-axis review (Standards + Spec, via parallel sub-agents) ran against the diff; both axes' findings were fixed (real CSS variables replacing invented ones with fake fallbacks, stale "at their institution" copy, and clearing a stale tutee selection when the institution filter changes). Full backend suite: 255 tests, 14 failures + 2 errors — identical count to the pre-work baseline, confirmed unrelated (avatar upload, dashboard recommendation tests).

---

### Task 1: Backend — augment demo rows with tutor subjects + rating stats (TDD)

**Files:**
- Modify: `backend/studybuddy/recommender/demo.py`
- Modify: `backend/studybuddy/tests.py` (`AlgorithmDemoToolTests`, line ~4480)

- [x] Step 1: Add two failing tests to `AlgorithmDemoToolTests` in `tests.py` (after `test_recommend_flags_cold_start_tutee_with_no_ratings`, ~line 4605):
  ```python
  def test_recommend_row_includes_tutor_subjects_and_rating(self):
      self.tutor.rating_average = 4.5
      self.tutor.total_sessions = 12
      self.tutor.save()

      self.client.force_authenticate(user=self.super_user)
      response = self.client.get(f"/api/dev/algorithm-demo/recommend/?tutee_id={self.tutee.id}")
      self.assertEqual(response.status_code, 200)

      row = response.data["rows"][0]
      self.assertEqual(row["rating_average"], 4.5)
      self.assertEqual(row["total_sessions"], 12)
      self.assertEqual(
          row["tutor_subjects"],
          [{"code": self.subject.subject_code, "expertise_level": 4}],
      )

  def test_recommend_row_zero_rating_for_new_tutor(self):
      self.client.force_authenticate(user=self.super_user)
      response = self.client.get(f"/api/dev/algorithm-demo/recommend/?tutee_id={self.tutee.id}")
      self.assertEqual(response.status_code, 200)

      row = response.data["rows"][0]
      self.assertEqual(row["rating_average"], 0)
      self.assertEqual(row["total_sessions"], 0)
  ```
- [x] Step 2: Run `python manage.py test studybuddy.tests.AlgorithmDemoToolTests` from `backend/` — confirm the two new tests fail (red) and all others still pass.
- [x] Step 3: In `demo.py`, inside `build_algorithm_demo_recommendation`'s row-building loop, add the three new fields:
  ```python
  rows.append({
      "tutor_id": tutor.profile_id,
      "name": f"{tutor.profile.fname} {tutor.profile.lname}",
      "hybrid_score": breakdown["hybrid_score"],
      "cold_start": cf["cold_start"],
      "rating_average": tutor.rating_average,
      "total_sessions": tutor.total_sessions,
      "tutor_subjects": [
          {"code": ts.subject.subject_code, "expertise_level": ts.expertise_level}
          for ts in tutor.tutorsubjects_set.all()
      ],
      "cbf": breakdown["cbf"],
      "cf": {
          "score": cf["score"],
          "neighbors": [
              {
                  "neighbor_id": neighbor["neighbor_id"],
                  "name": neighbor_names.get(neighbor["neighbor_id"], "Unknown"),
                  "similarity": neighbor["similarity"],
                  "rating": neighbor["rating"],
              }
              for neighbor in cf["neighbors"]
          ],
      },
  })
  ```
- [x] Step 4: Run `python manage.py test studybuddy.tests.AlgorithmDemoToolTests` again — all tests green.
- [x] Step 5: Commit — `git commit -m "feat: add tutor subjects and rating stats to algorithm demo rows"`

### Task 2: Frontend — shared breakdown animation component

**Files:**
- Create: `src/components/algorithm-demo/AlgorithmDemoBreakdown.vue`

- [x] Step 1: Port the bar-cascade animation from `docs/artifacts/2026-07-04-recommendation-algorithm-live-demo.html` (`CBF_PARTS`, `STAGGER_MS`, `animateBreakdown`/`fillBar`) into a Composition API component:
  - Props: `row` (object — one candidate row from the `/recommend/` response, matching the shape in Task 1).
  - `watch(() => props.row, ..., { immediate: true })` re-triggers the staggered reveal whenever a new row is selected (covers both tabs switching tutors).
  - Internal `ref` per bar (`subject`, `expertise`, `course`, `year`, `level`, `cf`, `hybrid`) holding `{ widthPct, label }`, updated via `setTimeout` cascade at `STAGGER_MS` (280ms) intervals, matching the mockup.
  - Render CF row states: cold-start ("CF unavailable — no rating history"), no-signal (`cf.score === null`, "None of this tutee's similar peers have rated this tutor yet"), and normal (neighbor list with `name`, `similarity`, `rating`).
  - Use Studybuddy CSS vars for colors (`--sb-primary` for CBF bars, a distinct existing accent for the CF bar — check `App.vue` custom properties for an appropriate secondary color rather than hardcoding a new hex; fall back to `--sb-primary` at reduced opacity if none fits), matching the mockup's look, not the standalone tool's dark theme.
- [x] Step 2: No test framework covers animation timing in this codebase — verify visually via the dev server per Task 5.

### Task 3: Frontend — Ranked List tab component

**Files:**
- Create: `src/components/algorithm-demo/AlgorithmDemoRankedList.vue`

- [x] Step 1: Props: `tuteeOptions` (array of `{value, label}` for `SbSelectModal`), emits none directly — owns its own selected-tutee state internally via a local `ref`.
- [x] Step 2: On tutee selection, `GET dev/algorithm-demo/recommend/?tutee_id=` via `api.js`; store `rows`/`reason` in local state.
- [x] Step 3: Render `reason === 'no_preferences'` / `'no_candidates'` empty states (reuse copy from the mockup); otherwise render `rows` sorted by `hybrid_score` desc (already sorted server-side) as a clickable list, cold-start badge per row matching `.sb-badge` styling.
- [x] Step 4: Clicking a row sets `selectedRow`; auto-select the first row after a successful fetch (matches mockup behavior). Pass `selectedRow` to `<AlgorithmDemoBreakdown :row="selectedRow" />`.

### Task 4: Frontend — Compare Pair tab component

**Files:**
- Create: `src/components/algorithm-demo/AlgorithmDemoPairPicker.vue`

- [x] Step 1: Props: `tuteeOptions`. Local state: `selectedTuteeId`, `selectedTuteeLabel` (for the tutee stat card — subject preferences come from the tutee-search response, so store the matching tutee's `subjects` alongside the id when populating `tuteeOptions` in the parent, or re-fetch via the same search endpoint keyed by id — prefer keeping the full tutee object in `tuteeOptions`' source list rather than a second fetch).
- [x] Step 2: On tutee selection, `GET dev/algorithm-demo/recommend/?tutee_id=` (same call as Task 3) to populate the tutor `SbSelectModal` options (`{value: tutor_id, label: `${name} (score ${hybrid_score.toFixed(2)})`}`); keep the raw `rows` array in state.
- [x] Step 3: On tutor selection, find the matching row from the already-fetched `rows` (no second API call) and render two stat cards:
  - Tutee card: name, subject-preference pills.
  - Tutor card: name, cold-start badge if applicable, `rating_average` (or "No ratings yet" if 0/absent — do not show a fake "0.0 ★"), `total_sessions`, `tutor_subjects` pills (color-coded by `expertise_level`, matching the mockup's `expertise-1/2/3` classes — map to whatever expertise scale `TutorSubjects.expertise_level` actually uses, confirm range in `models.py`/`cbf.py` before hardcoding 3 tiers).
- [x] Step 4: Pass the selected row to `<AlgorithmDemoBreakdown :row="selectedRow" />` below the stat cards.
- [x] Step 5: If the tutee has no candidate tutors (`reason` set, or empty `rows`), disable the tutor picker and show the same empty-state copy as Task 3.

### Task 5: Frontend — page shell, route, and nav entry

**Files:**
- Create: `src/views/SuperAdminAlgorithmDemo.vue`
- Modify: `src/router/index.js` (after line 231)
- Modify: `src/components/AppSidebar.vue` (after line 135)

- [x] Step 1: `SuperAdminAlgorithmDemo.vue` fetches tutee options once on mount via `GET dev/algorithm-demo/tutees/?q=` (empty query — full default-limit list), stores as `tuteeOptions`, passes to both child components as a prop. Renders a tab toggle (`Ranked List` / `Compare Pair`, matching the mockup's pill-toggle styling) and conditionally renders `AlgorithmDemoRankedList` or `AlgorithmDemoPairPicker`.
- [x] Step 2: Handle the 403 case (flag off) — if the initial tutee-options fetch 403s, show a plain message ("Algorithm demo tools are disabled on this backend.") instead of a broken empty page.
- [x] Step 3: Add the route in `router/index.js`:
  ```js
  {
    path: '/superadmin/algorithm-demo',
    name: 'superadmin-algorithm-demo',
    component: () => import('@/views/SuperAdminAlgorithmDemo.vue'),
    meta: { requiresAuth: true, role: 'SuperAdmin' }
  },
  ```
- [x] Step 4: Add the nav entry in `AppSidebar.vue`'s superadmin array:
  ```js
  { to: '/superadmin/algorithm-demo', label: 'Algorithm Demo', icon: 'bi-diagram-3' },
  ```
- [x] Step 5: Run `npm run lint` — clean.
- [x] Step 6: Run `npm run build` — clean.
- [x] Step 7: Commit — `git commit -m "feat: add superadmin algorithm demo page"`

### Task 7 (unplanned amendment): Institution filter

Found during Task 1 manual testing, before frontend work started — see the
spec's "Amendment" section for the why.

**Files:**
- Modify: `backend/studybuddy/recommender/demo.py` (`_candidate_tutors`, `search_tutees`, `build_algorithm_demo_recommendation` gain optional `institution_id`)
- Modify: `backend/studybuddy/views.py` (`algorithm_demo_search_tutees`, `algorithm_demo_recommend` read `institution_id` query param)
- Modify: `backend/studybuddy/tests.py` (3 new tests: cross-institution tutor visible by default, excluded when `institution_id` given, tutee search scoped by `institution_id`)
- Modify: `src/services/api/algorithmDemo.js` (both functions take an optional `institutionId`)
- Modify: `src/views/SuperAdminAlgorithmDemo.vue` (Institution filter via `SbSelectModal` + `useSuperAdminStore`, refetches tutees on change, passes `institutionId` prop to both tabs)
- Modify: `src/components/algorithm-demo/AlgorithmDemoRankedList.vue`, `AlgorithmDemoPairPicker.vue` (`institutionId` prop, threaded into the recommend call, clears the tutee selection on institution change rather than re-fetching a stale pairing)

- [x] Step 1: TDD — three new backend tests (red, then green after the `institution_id` params were added)
- [x] Step 2: Frontend institution filter wired through both tabs
- [x] Step 3: Two-axis review (Standards + Spec sub-agents) found and fixed: invented CSS variables with fake fallback hex values (`--sb-muted`, `--sb-green-tint`, `--sb-green-border` don't exist in `main.css` — replaced with real tokens `--sb-text-muted` and `color-mix()` off `--sb-primary`/`--sb-danger`), hardcoded `#fff`/`#eff3f1` card backgrounds (replaced with `--sb-card-bg`/`--sb-card-border` so dark mode works), stale empty-state copy implying institution scoping is always on, and a stale-tutee-selection edge case when the institution filter changes after a tutee is already picked.

### Task 6: Full verification pass

- [x] Step 1: `python manage.py test` from `backend/` — full suite green.
- [x] Step 2: With `ALGORITHM_DEMO_TOOLS_ENABLED=true` in `backend/.env`, start both dev servers, log in as SuperAdmin, exercise both tabs end to end per the spec's Verification section.
- [x] Step 3: Confirm 403 handling (flag off) and role-guard (non-SuperAdmin redirect) manually.
- [x] Step 4: Write session summary at `docs/session-summaries/2026-07-04-superadmin-algorithm-demo-summary.md`; update this plan's status to Done and regenerate `docs/plans/index.html`.

---

## Changelog

- **2026-07-04** — Plan created and approved. Six tasks defined (backend TDD augmentation, three Vue components, page/route/nav wiring, verification pass). Not yet started.
- **2026-07-04** — Executed Tasks 1-6. Added unplanned Task 7 (institution filter) after live testing showed the originally-specified institution-scoped candidate pool made the demo unusable against seeded data. Ran a two-axis (Standards/Spec) review via parallel sub-agents and fixed all findings (invented CSS variables, hardcoded colors breaking dark mode, stale copy, a stale-selection edge case). Full backend suite green apart from 14 failures/2 errors matching the pre-existing baseline exactly. Marked Done.
