# Brief: CF same-course peer neighbors + glossary sync

Follow this brief exactly. Standing rules are in AGENTS.md. Reference:
[`docs/tickets.md`](../tickets.md) (tickets 2 and 3) and
[`docs/plans/2026-07-15-recommender-weight-rebalance.md`](../plans/2026-07-15-recommender-weight-rebalance.md).

## Scope

Covers the two remaining tickets of the recommender weight rebalance:

1. **CF same-course peer neighbors with per-tutor global fallback**
2. **Glossary and docs sync** (CONTEXT.md), blocked by 1 — do it second.

Out of scope: everything CBF-side (ticket 1, already shipped in commit `5ef4372` — do not
rework `cbf.py` weights or the Specific/General/Expertise logic), the hybrid 0.7/0.3 split,
Cold-Start weight reallocation, the follow-up tickets listed in the plan (admin subject
editing, category data hygiene), and the pre-existing test failures noted below.

## Execution checklist

### 1. CF same-course peer neighbors with per-tutor global fallback

**What to build:** CF predictions come from "peers" — Top-K neighbors drawn from students in
the same course (exact `course` equality) — so a tutee's score feels like "students in your
program rated this tutor". Two top-5 neighbor lists are computed once per request (peer pool
and global pool); per candidate tutor, the peer prediction is used when its denominator is
nonzero, otherwise the global prediction. Only positive Pearson similarity (`> 0`) qualifies
a neighbor, in both pools. A null-course tutee has an empty peer pool (global-only).
Cold-Start behavior is unchanged. The algorithm demo shows which pool (peer/global) each
tutor's CF prediction used.

Exact rules (final, from the approved plan):

- **Positive similarity only:** in `top_k`, a student qualifies as a neighbor only when
  Pearson `similarity > 0` (strictly — zero carries no information). This resolves the
  commented-out `if similarity >= 0` block in `CF.py`.
- **Peer pool:** neighbors restricted to students whose `UserProfile.course` equals the
  tutee's course (exact `course_id` equality, no strand tier). Null course means an empty
  peer pool. The ratings matrix has no course data — build the peer id set with ONE query
  (e.g. `UserProfile.objects.filter(id__in=ratings.keys(), course_id=...)`), never
  per-student. Design the pure functions so dict-only tests can pass candidate ids / pools
  explicitly (existing test ratings matrices use fake ids with no UserProfile rows).
- **Per-tutor fallback:** compute BOTH top-5 lists once per request. For each candidate
  tutor: use the peer prediction when its denominator (sum of `abs(similarity)` over
  neighbors who rated that tutor) is nonzero; otherwise the global prediction. Per-TUTOR,
  not per-request. (The plan records a revisit trigger: reconsider per-request fallback when
  rating density is high — recorded intent only, do not implement.)
- **Pool label:** the CF breakdown must expose which pool produced the prediction — a
  `"pool"` key with `"peer"` / `"global"` (None or similar for cold-start / no signal).
- **Cold-Start unchanged:** student absent from the ratings matrix keeps returning score
  `None` with `cold_start: True`; the hybrid keeps coercing `None` to 0; the CF weight is
  never reallocated to CBF.

Acceptance criteria:

- [ ] `top_k` excludes non-positive similarity neighbors in both pools — covered by a test.
- [ ] Peer pool contains only same-course students; null-course tutee gets an empty peer
      pool — covered by tests.
- [ ] Per-tutor fallback: peer prediction used when peer denominator is nonzero, global
      otherwise — covered by a test at the tutor level and the pool level (empty peer pool
      means everything falls back to global).
- [ ] Neighbor lists computed once per request (existing neighbor-reuse tests still pass or
      are updated to the two-list shape).
- [ ] CF breakdown exposes which pool each prediction used; demo tool and its UI surface it.
- [ ] Recommender-related test classes green; `npm run lint` and `npm run build` pass.

Files involved (located at export time; tickets are path-free by convention, so paths live
here):

- `backend/studybuddy/recommender/CF.py` — `build_rating_matrix()` returns
  `{student_id: {tutor_profile_id: rating}}`; `sim()` Pearson; `top_k(ratings, student_id,
  k=5)` currently appends ALL similarities; `compute_cf_breakdown(ratings, student_id,
  tutor_id, k=5, neighbors=None)` returns `{"score", "cold_start", "neighbors"}` (score None
  when student unknown -> cold_start True, or when denominator 0); `compute_cf_score` wraps
  it; `recommend_tutors_cf` is a standalone CF-only path — keep it working (global pool only
  is fine). A clean shape: keep `compute_cf_breakdown` single-pool and add a fallback helper
  (e.g. `compute_cf_breakdown_with_fallback(ratings, student_id, tutor_id, peer_neighbors,
  global_neighbors)`) returning the breakdown plus `"pool"`.
- `backend/studybuddy/recommender/hybrid.py` — `recommend_tutors_hybrid(ratings,
  student_profile, requested_subject, candidate_qs=None)` computes
  `neighbors = top_k(...) if student_id in ratings else []` once per request and passes
  `neighbors=` into `hybrid_prediction` / `hybrid_prediction_breakdown` per tutor; both also
  take a `target_categories` kwarg from ticket 1 — preserve that pattern. Extend the
  once-per-request pattern to the two lists. Keep the `recommend_tutors_hybrid` signature
  unchanged: `backend/studybuddy/recommender/dashboard.py` (~line 125) and
  `backend/studybuddy/views.py` (~lines 3843-3855) call it and must need no edits.
- `backend/studybuddy/recommender/demo.py` — `build_algorithm_demo_recommendation` computes
  `neighbors` once and builds `_neighbor_name_map` over them; update to the two-list shape;
  the name map must cover BOTH pools; each row's `"cf"` dict gains the pool label.
- `src/components/algorithm-demo/AlgorithmDemoBreakdown.vue` — renders each row's CBF bars
  (`CBF_PARTS`, six keys since ticket 1) and CF/neighbor details. Add a small,
  style-consistent indicator of the pool ("Peer rating (same course)" vs "Global rating").
  Check `src/components/algorithm-demo/AlgorithmDemoRankedList.vue` and
  `src/views/SuperAdminAlgorithmDemo.vue` for other cf usages needing the same. Follow
  existing CSS custom properties (`--sb-*`), no hardcoded hex colors.
- `backend/studybuddy/tests.py` — single large file. `RecommenderNeighborReuseTests`
  (~line 4637) asserts neighbors computed once via `patch.object(hybrid, "top_k")` with
  `call_count == 1`: update to the two-list world. `CbfGraduatedSubjectMatchTests`
  (just below, ~4702) is ticket 1's — must stay 7/7, do not modify.
  `DashboardRecommendationServiceTests` and `AlgorithmDemoToolTests` (~5560+) exercise the
  downstream surfaces. Add a new class (e.g. `CfPeerNeighborTests`) for the required tests.

### 2. Glossary and docs sync

**What to build:** the glossary at repo-root `CONTEXT.md` reflects the shipped algorithm —
the CBF Score / CF Score / Top-K Neighbor entries sit at lines ~137-173 (the
General/Specific Subject and peer-pool wording added during the grill is already partially
there; verify it against the implementation rather than assuming).

Acceptance criteria:

- [ ] CONTEXT.md CBF Score entry matches the implemented weights and rules
      (0.40/0.20/0.15/0.10/0.10/0.05, Specific/General superset rule, null-category rule,
      expertise cascade, empty-request preference-list fallback).
- [ ] CONTEXT.md CF Score / Top-K Neighbor entries describe the same-course peer pool,
      per-tutor global fallback, positive-similarity filter, and the recorded per-request
      revisit trigger.
- [ ] No stale references to the old 0.35/0.20/0.20/0.15/0.10 weights anywhere in docs
      (grep `docs/` and `CONTEXT.md` for `0.35`).

## Context

- Glossary vocabulary (use these exact terms): Hybrid Score = `0.7 * CBF + 0.3 * (CF / 5)`
  (untouched); CBF Score sub-scores Specific Subject / General Subject / Expertise / Course /
  Year / Teaching Level; CF Score; Top-K Neighbor; Cold-Start (no Rating history; CF None
  coerced to 0).
- Ticket 1 (already merged) renamed the CBF breakdown keys to
  `specific, general, expertise, course, year, level`, each `{weight, value, contribution}`,
  and introduced `resolve_target_categories()` + a `target_categories` precompute-once kwarg
  threaded through `hybrid.py` and `demo.py`. Mirror that precompute-once pattern for the
  two neighbor lists.
- Known pre-existing failures — do NOT fix, do not add new ones: `AlgorithmDemoToolTests`
  has 3 failures + 3 errors (`test_recommend_flags_cold_start_tutee_with_no_ratings`,
  `test_recommend_row_includes_tutor_subjects_and_rating`,
  `test_recommend_row_zero_rating_for_new_tutor` (errors);
  `test_recommend_includes_subject_matching_tutor_from_other_institution`,
  `test_recommend_institution_id_filter_excludes_other_institution_tutor`,
  `test_recommend_matches_direct_hybrid_computation` (failures)) — root cause is course-less
  test tutees, unrelated to this work.
- Backend test commands (from `backend/`):
  `python manage.py test studybuddy.tests.<Class> --keepdb`. Run: your new class,
  `RecommenderNeighborReuseTests`, `CbfGraduatedSubjectMatchTests`,
  `DashboardRecommendationServiceTests`, `AlgorithmDemoToolTests` (expect exactly the six
  pre-existing failure names above, no new ones). Do not run the full suite — the reviewer
  runs it at the end. The test DB requires the `.env` in `backend/` (already present in this
  tree); `--parallel` is known to fail against the pooled test database — run serially.
- Conventions: PEP 8, module-level constants (no magic numbers), 2-space/no-semicolon
  Prettier style in Vue, no emojis anywhere, frontend API calls stay in `src/services/`
  (not needed here — the demo endpoint payload just gains a field).

## Contract

- Work ONLY this brief — no scope creep, no drive-by refactors.
- TDD: failing test first, then the minimal implementation, matching existing style.
- Run the relevant tests; get them green; paste commands and output under Test evidence.
- NEVER commit, push, branch, or run any git write. Leave the tree dirty.
- Record anything done differently, and why, under Deviations.

## Test evidence

- `cd backend; python manage.py test studybuddy.tests.CfPeerNeighborTests studybuddy.tests.RecommenderNeighborReuseTests studybuddy.tests.CbfGraduatedSubjectMatchTests --keepdb`
  - Passed: 14 tests.
- `npm run lint`
  - Passed: oxlint reported 0 warnings/errors; ESLint completed successfully.
- `npm run build`
  - Passed: Vite production build completed successfully.
- `cd backend; python manage.py test studybuddy.tests.CbfGraduatedSubjectMatchTests studybuddy.tests.DashboardRecommendationServiceTests studybuddy.tests.AlgorithmDemoToolTests --keepdb`
  - Completed its test output in 139.361 seconds but the command runner timed out at 145 seconds.
    The output contained the six documented AlgorithmDemoToolTests failures/errors and five
    additional existing DashboardRecommendationServiceTests failures/errors; no changes were
    made to those unrelated test fixtures or recommendation candidate filtering.
- `cd backend; python manage.py test studybuddy.tests.DashboardRecommendationServiceTests --keepdb`
  - Completed: 7 tests, with 4 failures and 1 error in the pre-existing course-less/
    institution-less dashboard fixtures that return no candidates.
- `cd backend; python manage.py test studybuddy.tests.AlgorithmDemoToolTests --keepdb`
  - Completed: 20 tests, with exactly the documented 3 failures and 3 errors; the other 14 passed.
- `rg -n "W_SUBJECT|0\.35·s_subject|0\.35/0\.20/0\.20/0\.15/0\.10" docs CONTEXT.md`
  - Remaining hits are intentional historical plan/ticket/brief references; stale explanatory
    documentation was updated.
- `git diff --check`
  - Passed (aside from the existing unreadable `backend/.pytest_cache/` warning).

## Deviations

- Updated two older explanatory HTML documents in addition to `CONTEXT.md` and the algorithm
  explainer artifact so the repository has no stale live description of the retired CBF weights.
- The requested combined downstream Django command exceeded the command runner's 145-second
  limit after emitting its complete test result. The documented AlgorithmDemoToolTests failures
  remain, and the run also exposed pre-existing DashboardRecommendationServiceTests fixture
  failures; both are outside this brief's scope and were left unchanged.
