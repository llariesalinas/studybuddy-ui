# Recommendation algorithm live demo tool — summary

Shipped as planned in [docs/plans/2026-07-04-recommendation-algorithm-demo-tool.md](../plans/2026-07-04-recommendation-algorithm-demo-tool.md).

## What shipped

- **Backend**: `backend/studybuddy/recommender/demo.py` (new) — `search_tutees` (multi-word
  full-name search) and `build_algorithm_demo_recommendation`, which runs the real candidate
  filtering (subject preference match + institution filter, same as
  `get_dashboard_recommendations`) and returns every candidate tutor's full Hybrid Score
  breakdown.
- To expose the breakdown without duplicating formulas, `cbf.py`, `CF.py`, and `hybrid.py` each
  gained a `*_breakdown` function (`compute_cbf_breakdown`, `compute_cf_breakdown`,
  `hybrid_prediction_breakdown`) that the existing `compute_cbf_score` / `compute_cf_score` /
  `hybrid_prediction` now delegate to — behavior-preserving refactors, verified against the
  existing `RecommenderNeighborReuseTests` suite.
- Two new endpoints (`dev/algorithm-demo/tutees/`, `dev/algorithm-demo/recommend/`), gated by
  `IsAuthenticated` + `IsSuperAdminUser` + a new `ALGORITHM_DEMO_TOOLS_ENABLED` settings flag
  (default off), mirroring the `VERIFICATION_DEV_TOOLS_ENABLED` pattern.
- **Frontend**: standalone tool at
  `docs/artifacts/2026-07-04-recommendation-algorithm-live-demo.html` — login form (two-step
  email/password + email-OTP, auto-filling the backend's DEBUG-mode `debug_code`), searchable
  tutee dropdown, split view (ranked list + detail panel), and a staged bar-cascade animation
  that reveals each CBF sub-score, then the CF score + contributing Top-K Neighbors (or a
  "Cold Start" badge), then merges into the final Hybrid Score bar.
- Domain glossary additions to `CONTEXT.md`: Hybrid Score, CBF Score, CF Score, Top-K Neighbor,
  Cold-Start Tutee.

## Deviations from the plan

- **Login flow**: the plan assumed a single-step email/password → JWT login. The real `login/`
  endpoint always requires a follow-up email-OTP step (`login/verify-otp/`). Implemented as a
  two-step form; in DEBUG mode the OTP code is auto-filled from the backend's `debug_code` field,
  so the live demo never actually depends on email delivery.
- **Candidate pipeline reuse**: the plan said the demo would "run `recommend_tutors_hybrid`."
  Since that function only returns a final score (not sub-scores), `demo.py` instead calls
  `hybrid_prediction_breakdown` directly per candidate tutor — functionally identical, verified
  byte-for-byte against `hybrid_prediction`'s output in
  `test_recommend_matches_direct_hybrid_computation`.
- **Permission gate**: implemented as `IsSuperAdminUser` (SuperAdmin role only), not the looser
  `IsAdminUser` (which also covers `Admin` role and `is_staff`). This follows the codebase's actual
  precedent for dev-tools endpoints that expose other users' personal data
  (`AdminUserVerificationDevToolsView`, SuperAdmin-only), which is stricter than the plan's
  informal "staff/superadmin" wording. Left as-is given the endpoint returns real students' names
  and rating history; documented inline in `views.py`.

## Bugs found and fixed during manual verification

- Tutee search only matched a single word against `fname` OR `lname`, so typing a full name
  ("John Miller") returned zero results. Fixed to split the query into words and require each to
  match `fname` or `lname` (`test_tutee_search_matches_full_name` added).
- When a tutee has rating history but none of their similar peers rated a specific tutor
  (`cf.score` is `null`, not Cold-Start), the "no signal" label was immediately overwritten by
  `fillBar`'s own label-setting logic, displaying a misleading "0.00". Fixed by passing `null` as
  the label so the custom text isn't clobbered.

## Checks run

- `python manage.py test studybuddy.tests.AlgorithmDemoToolTests` — 9/9 pass.
- `python manage.py test studybuddy.tests.RecommenderNeighborReuseTests` — 4/4 pass (confirms the
  CBF/CF/hybrid refactors are behavior-preserving).
- Full backend suite (`python manage.py test studybuddy`) — 249 tests, 14 failures + 2 errors, all
  pre-existing and unrelated to this change (confirmed by reproducing the same failures against
  the pre-refactor code via `git stash`). Root cause: the shared Supabase Postgres test database is
  accessed through a connection pooler that doesn't cleanly support Django's per-test transaction
  rollback (seen directly as a `UniqueViolation` on a supposedly-per-test row), causing state to
  leak across test runs. Out of scope for this change; flagged for the team separately.
- Manual walkthrough against the local dev server with real seeded data: login (two-step OTP),
  tutee search (single-word and full-name), a Cold-Start tutee (all candidates capped at
  `0.7 × CBF`), and a tutee with real CF signal (verified `Hybrid Score = 0.7×CBF + 0.3×(CF/5)`
  arithmetic by hand against the API response).
- Two-axis review (`/review` skill, Standards + Spec sub-agents) — no hard standards violations;
  the one spec-permission divergence above was deliberate and is now documented inline.
