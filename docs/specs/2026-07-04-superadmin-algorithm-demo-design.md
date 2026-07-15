# SuperAdmin Algorithm Demo Page — Design Spec

**Date:** 2026-07-04
**Status:** Done
**Stack:** Vue 3 (Composition API), Django REST
**Mockup:** [docs/artifacts/2026-07-04-superadmin-algorithm-demo-mockup.html](../artifacts/2026-07-04-superadmin-algorithm-demo-mockup.html)

---

## Amendment (implemented during Task 1, before frontend work)

Manual testing surfaced that mirroring production's institution-scoped candidate
pool (as originally specified below) made the demo nearly unusable: the seeded
dataset rarely has a tutee and tutor sharing an institution, so most tutees
showed "no candidates."

Changed: `_candidate_tutors` and `search_tutees` in `demo.py` are **unscoped by
institution by default** (any subject-matching tutor, regardless of
institution) and take an optional `institution_id` param to scope down to one
institution instead. The frontend adds an **Institution filter**
(`SbSelectModal`, defaulting to "All institutions") on the page shell, shared by
both tabs, wired through `institutionId` props into each tab component and the
`getAlgorithmDemoRecommendation` / `searchAlgorithmDemoTutees` calls.

Everything below this point is the original spec, kept as-is for the decision
record; read `_candidate_tutors`' docstring in `demo.py` as the current source
of truth over the "institution filter" wording below.

---

## Goal

Move the standalone recommendation-algorithm live demo tool
(`docs/artifacts/2026-07-04-recommendation-algorithm-live-demo.html`) into the real
SuperAdmin panel as a proper page, so a SuperAdmin can demonstrate the hybrid
recommender (CBF + CF) to a thesis/capstone panel from inside the logged-in app
instead of a separate HTML file with its own login flow.

Two ways to run the demo, as two tabs on one page:

1. **Ranked List** — pick a tutee, see every subject-matching candidate tutor
   ranked by Hybrid Score, click any row to animate its score breakdown.
2. **Compare Pair** — pick a tutee, then explicitly pick one tutor from that
   tutee's candidate pool, see a stat card for each side (subject preferences /
   expertise, tutor rating history), then the same animated breakdown.

Both tutee and tutor selection use the app's existing searchable dropdown
(`SbSelectModal`), not a free-text input or a native `<select>` — confirmed with
the interactive mockup linked above.

---

## What already exists (important)

This is a UI relocation plus a small data augmentation, not a new algorithm or
new endpoints.

- **`backend/studybuddy/recommender/demo.py`** — `search_tutees(query)` and
  `build_algorithm_demo_recommendation(tutee)`. The latter returns, per candidate
  tutor: `hybrid_score`, `cold_start`, `cbf` (breakdown per sub-score: `subject`,
  `expertise`, `course`, `year`, `level`, each `{weight, value}`), and `cf`
  (`score`, `neighbors: [{neighbor_id, name, similarity, rating}]`). Reuses the
  real candidate pool (`_candidate_tutors`: subject match +
  `filter_tutors_by_institution`) — no reimplementation of the algorithm.
- **Endpoints** (`backend/studybuddy/views.py:390-412`), both
  `IsAuthenticated + IsSuperAdminUser`, gated by `settings.ALGORITHM_DEMO_TOOLS_ENABLED`
  (default `False`, `backend/backend/settings.py:268`):
  - `GET dev/algorithm-demo/tutees/?q=` (`urls.py:154`)
  - `GET dev/algorithm-demo/recommend/?tutee_id=` (`urls.py:155`)
- **`SbSelectModal.vue`** (`src/components/SbSelectModal.vue`) — the app's
  existing searchable/clearable dropdown modal, already used by
  `SuperAdminReports.vue` for institution filtering. Takes
  `options: [{value, label}]`, `v-model`, `searchable`, `clearable`,
  `placeholder`, `title`; emits `update:modelValue`.
- **SuperAdmin route/nav pattern** — routes registered in
  `src/router/index.js:207-231` (`role: 'SuperAdmin'` meta), nav entries in
  `src/components/AppSidebar.vue:128-137`.
- **`Tutor.rating_average`** and **`Tutor.total_sessions`**
  (`backend/studybuddy/models.py:263,293`) — already-stored fields, already
  surfaced elsewhere via `AdminUserSerializer.get_tutor_avg_rating` /
  `get_tutor_sessions_completed` (`serializers.py:123,115`). Reused here, not
  recomputed.

---

## Design

### 1. Data model — one additive backend change

`build_algorithm_demo_recommendation` in `demo.py` gains two fields per row, both
sourced from data already loaded on the `tutor` object (no extra queries —
`normalize_tutor_queryset` in `hybrid.py:78` already prefetches
`tutorsubjects_set__subject`):

```python
rows.append({
    "tutor_id": tutor.profile_id,
    "name": f"{tutor.profile.fname} {tutor.profile.lname}",
    "hybrid_score": breakdown["hybrid_score"],
    "cold_start": cf["cold_start"],
    "rating_average": tutor.rating_average,        # new
    "total_sessions": tutor.total_sessions,          # new
    "tutor_subjects": [                              # new
        {"code": ts.subject.subject_code, "expertise_level": ts.expertise_level}
        for ts in tutor.tutorsubjects_set.all()
    ],
    "cbf": breakdown["cbf"],
    "cf": {...},  # unchanged
})
```

No new endpoints. Both UI modes call the same two existing routes:
- `dev/algorithm-demo/tutees/?q=` populates the tutee `SbSelectModal` options
  (`{value: id, label: name}`), for both tabs.
- `dev/algorithm-demo/recommend/?tutee_id=` returns the full candidate list once
  a tutee is picked. **Ranked List** renders it as a sorted, clickable list.
  **Compare Pair** turns the same `rows` into the tutor `SbSelectModal`'s options
  (`{value: tutor_id, label: name}}`) and, once a tutor is picked, looks up that
  row from the already-fetched array — no second API call per tutor pick.

`search_tutees` needs no changes: called with an empty query it already returns
up to `DEFAULT_TUTEE_SEARCH_LIMIT` (20) tutees ordered by name, which is what
`SbSelectModal`'s built-in search filters client-side. If a panel demo ever needs
more than 20 tutees, raise the limit — out of scope here since it isn't a
constraint on any known demo dataset.

### 2. Component structure

```
src/views/SuperAdminAlgorithmDemo.vue          — page shell, owns tab state,
                                                   fetches tutee options once
src/components/algorithm-demo/
  AlgorithmDemoRankedList.vue                   — tutee SbSelectModal + ranked,
                                                   clickable tutor list
  AlgorithmDemoPairPicker.vue                   — tutee + tutor SbSelectModal
                                                   pair, two stat cards
  AlgorithmDemoBreakdown.vue                    — shared bar-cascade animation
                                                   (ported from the standalone
                                                   HTML's animateBreakdown/fillBar),
                                                   props: `row` (one candidate row)
```

`AlgorithmDemoBreakdown.vue` is the one piece of real animation logic, shared by
both tabs so the calculation presentation is identical regardless of how the
pair was picked.

### 3. Integration points

- Route: `src/router/index.js`, alongside the other superadmin routes
  (after line 231):
  ```js
  {
    path: '/superadmin/algorithm-demo',
    name: 'superadmin-algorithm-demo',
    component: () => import('@/views/SuperAdminAlgorithmDemo.vue'),
    meta: { requiresAuth: true, role: 'SuperAdmin' }
  },
  ```
- Nav: `src/components/AppSidebar.vue`, in the `superadmin` branch (after line 135):
  ```js
  { to: '/superadmin/algorithm-demo', label: 'Algorithm Demo', icon: 'bi-diagram-3' },
  ```
- All calls go through `src/services/api/api.js` (authenticated instance) —
  the standalone tool's manual login/OTP screens are dropped entirely, since the
  SuperAdmin is already authenticated in-app.
- No new Pinia store. This is a narrow testing tool; local `ref`/`reactive`
  state in `SuperAdminAlgorithmDemo.vue`, passed down as props, matches how
  similarly-scoped one-off admin tools are built elsewhere in this codebase.
- Still gated by `ALGORITHM_DEMO_TOOLS_ENABLED` (backend env var, default off).
  Nothing changes about that gate — it must be turned on in whatever backend
  environment the panel demo runs against.

---

## Out of scope

- Changing the tutor-selection pool to include non-subject-matching tutors
  (explicitly decided against — Compare Pair mirrors the real candidate pool).
- A merged single-screen view replacing the two tabs (explicitly decided
  against — Ranked List and Compare Pair stay as separate tabs).
- Deleting the standalone HTML tool or its backing endpoints/tests — out of
  scope for this change; can be cleaned up separately once the in-app page is
  verified working for a real panel demo.
- Raising `DEFAULT_TUTEE_SEARCH_LIMIT` or adding server-side search-as-you-type
  — client-side filtering of the existing 20-result payload is sufficient at
  current data scale.

---

## Tests to add (`backend/studybuddy/tests.py`)

Extend the existing algorithm-demo test coverage (added with the standalone
tool) to assert the three new row fields:

1. `test_recommend_row_includes_tutor_subjects_and_rating` — a row for a tutor
   with known `rating_average`, `total_sessions`, and `TutorSubjects` rows
   returns matching `rating_average`, `total_sessions`, and `tutor_subjects`
   (code + expertise_level) values.
2. `test_recommend_row_zero_rating_for_new_tutor` — a tutor with no sessions
   yet returns `rating_average: 0`, `total_sessions: 0`, not `null`/missing keys.

No new permission/gating tests needed — `IsSuperAdminUser` +
`ALGORITHM_DEMO_TOOLS_ENABLED` behavior is unchanged and already covered.

---

## Verification

1. `python manage.py test studybuddy.tests` — full suite green, including the
   two new/extended cases above.
2. `npm run lint` and `npm run build` — clean.
3. With `ALGORITHM_DEMO_TOOLS_ENABLED=true` locally: log in as SuperAdmin,
   navigate to **Algorithm Demo** in the sidebar, confirm:
   - Ranked List: picking a tutee populates a ranked list; clicking a tutor
     animates the same breakdown values the standalone tool produced for the
     same seeded pair.
   - Compare Pair: picking a tutee then a tutor shows both stat cards (subject
     preferences on the tutee side; rating average, sessions completed, and
     subject/expertise pills on the tutor side) before the calculation animates.
   - A tutee with no candidate tutors shows the existing empty-state message,
     not an error.
4. Confirm the page 403s (not a blank/broken screen) when
   `ALGORITHM_DEMO_TOOLS_ENABLED` is off, and is unreachable for non-SuperAdmin
   roles via the router guard.
