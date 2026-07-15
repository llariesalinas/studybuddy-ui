# SuperAdmin Algorithm Demo Page — Session Summary

**Date:** 2026-07-04
**Plan:** [docs/plans/2026-07-04-superadmin-algorithm-demo.md](../plans/2026-07-04-superadmin-algorithm-demo.md)
**Spec:** [docs/specs/2026-07-04-superadmin-algorithm-demo-design.md](../specs/2026-07-04-superadmin-algorithm-demo-design.md)

## What shipped

Moved the standalone recommendation-algorithm live demo tool into the real
SuperAdmin panel as `/superadmin/algorithm-demo`, with two tabs:

- **Ranked List** — pick a tutee, see every subject-matching candidate tutor
  ranked by Hybrid Score, click any row to animate its CBF/CF breakdown.
- **Compare Pair** — pick a tutee, then a tutor, see a stat card for each side
  (subject preferences/expertise, tutor rating history), then the same
  animated breakdown.

Both tabs share one `AlgorithmDemoBreakdown.vue` component for the bar-cascade
calculation animation, and use the app's existing `SbSelectModal` searchable
dropdown for both tutee and tutor selection — no free-text search, no native
`<select>`, no separate login/OTP flow (the standalone tool's own auth screens
were dropped since the SuperAdmin is already authenticated in-app).

Backend: `demo.py`'s row builder gained `rating_average`, `total_sessions`,
and `tutor_subjects` per candidate row (TDD, `AlgorithmDemoToolTests`). No new
endpoints — both existing `dev/algorithm-demo/` routes were reused.

## Deviation from the plan: institution scoping

The original spec/plan said the tutor candidate pool should mirror
production's institution-scoped matching exactly. During Task 1's manual
testing this made the demo nearly unusable — the seeded dataset rarely has a
tutee and tutor sharing an institution, so most tutees showed "no candidates."

Changed mid-implementation, confirmed with the user: `_candidate_tutors` and
`search_tutees` in `demo.py` are now **unscoped by institution by default**
(any subject-matching tutor, any institution) and take an optional
`institution_id` to scope down to one institution instead. An **Institution
filter** (`SbSelectModal`, defaulting to "All institutions") was added to the
page shell, shared by both tabs via an `institutionId` prop threaded through
to the `/recommend/` and `/tutees/` calls.

This only affects the staff-only demo tool (`demo.py`) — production matching
(`get_recommendation_candidate_tutors`, `get_dashboard_recommendations`) is
untouched and remains institution-scoped.

## Review findings, fixed

Ran a two-axis review (Standards + Spec, parallel sub-agents) against the
diff. Both passes found real issues, all fixed before commit:

- **Standards**: `AlgorithmDemoBreakdown.vue`, `AlgorithmDemoRankedList.vue`,
  `AlgorithmDemoPairPicker.vue`, and `SuperAdminAlgorithmDemo.vue` used
  `var(--sb-muted, #6b7c76)`, `var(--sb-green-tint, #e3f3ea)`, and
  `var(--sb-green-border, #cfe8db)` — none of those three custom properties
  exist in `main.css`, so the hardcoded fallback hex was always what
  rendered. Replaced with the real tokens (`--sb-text-muted`) and
  `color-mix()` off `--sb-primary`/`--sb-danger`, matching how badges are
  tinted elsewhere in `main.css`. Also replaced hardcoded `#fff`/`#eff3f1`
  card and track backgrounds with `--sb-card-bg`/`--sb-card-border`, which
  fixes a real dark-mode bug (the literal white/light-gray never adapted to
  the app's dark theme).
- **Spec**: two empty-state strings ("No candidate tutors match this tutee's
  institution and subjects" / "...at their institution") still implied
  institution scoping was always active, misleading now that it defaults to
  unscoped — reworded to only mention institution when a filter is actually
  set. Also found a stale-selection edge case: changing the institution
  filter while a tutee was already selected re-fetched the same tutee under
  the new institution rather than clearing the now-possibly-invalid
  selection — fixed by clearing the tutee selection on institution change in
  both tab components.

## Checks run

- `python manage.py test studybuddy.tests.AlgorithmDemoToolTests` — 14/14
  green (11 original + 3 new institution-scoping tests), run multiple times
  through TDD red/green cycles.
- `python manage.py test` (full suite) — 255 tests, 14 failures + 2 errors.
  Identical failure count to the pre-work baseline run; confirmed unrelated
  (avatar upload tests, a dashboard recommendation test — none touch
  `demo.py`, `views.py`'s algorithm-demo endpoints, or the frontend files
  changed here).
- `npm run lint` — 18 pre-existing errors in 8 unrelated files (counts match
  exactly before and after this work); zero errors in any new file.
- `npm run build` — clean, both before and after the CSS-variable fixes.
- Manual browser verification (logged in as a SuperAdmin dev account):
  both tabs load real seeded data, ranked list auto-selects and animates the
  top match, Compare Pair renders both stat cards and the same animation,
  the institution filter narrows both the tutee picker and tutor candidate
  pool (confirmed via network requests carrying `institution_id`), and
  empty/no-preference states render correctly.

## Not done / explicitly out of scope

- The standalone HTML demo tool and its backing tests were left in place —
  cleanup was explicitly out of scope for this change.
- `DEFAULT_TUTEE_SEARCH_LIMIT` was raised from 20 to 500 (the frontend now
  fetches the full roster once for client-side dropdown search instead of
  re-querying per keystroke); not raised further or made server-search-driven
  since 500 comfortably covers the current seeded dataset (380 tutees).
