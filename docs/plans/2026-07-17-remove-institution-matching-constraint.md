---
title: Remove institution matching constraint, add institution label to TutorDetails
date: 2026-07-17
status: Approved
summary: Any tutee can now match any tutor regardless of institution; TutorDetails shows the tutor's university as a badge.
spec:
---

# Remove institution matching constraint, add institution label to TutorDetails

## Status & Progress Summary

Approved after a full grilling session (2026-07-17). Implementation starting now — steps 1-9 below
not yet executed.

## Goal

Institution-scoped matching (a CPU tutee can only see CPU tutors) was a leftover constraint from
before the institutional-Admin-role consolidation (`c5d58d0`, `f9dc843`), and now that only one
institution is actively seeded, it just narrows the demo/dev candidate pool for no product reason.
Remove the constraint so any tutee can match any tutor platform-wide, and since institution
affiliation is still a real, admin-screened fact about a tutor, surface it as a label on
`TutorDetails.vue` so tutees can still see it.

## Approach

Institution filtering is centralized in one helper, `filter_tutors_by_institution()`
(`backend/studybuddy/recommender/utils.py`), called from exactly three places: tutor search
(`views.py:1904`), the booking/recommend candidate pool (`views.py:3740`), and dashboard
recommendations (`recommender/dashboard.py:76,118`). CBF/CF scoring itself never references
institution — it's a pre-filter on the candidate queryset, not a scoring weight — so removing the
three call sites and deleting the now-dead helper removes the constraint everywhere at once with
no scoring-logic changes.

Registration stays as-is: `PartnerInstitution`, the email-domain validation, and each user's
`institution_id` remain untouched. This is a matching-only change — institution remains a real
identity, just no longer a candidate-pool filter.

The `TutorDetailSerializer` doesn't expose institution today; add a plain field sourced from the
existing `profile.institution` FK (no migration needed). On the frontend, add a badge next to the
existing Verified badge in `TutorDetails.vue`'s `.name-row`, styled as a sibling of
`.verified-badge`. No null-state handling — tutors are admin-screened before onboarding, so
`institution_name` is always present.

`InstitutionScopedMatchingTests` (`tests.py:6721`) currently asserts the exact behavior being
removed; rewrite it to assert cross-institution matches now succeed instead of being excluded, and
drop the null-institution scoping tests as moot.

Two docs describe the old institution-scoped behavior and need correcting once this ships:
`docs/architecture/algorithm-demo-guide.html`'s "Scope" fact-card (the demo tool's
unscoped-by-default behavior stops being an exception once real matching is unscoped too) and
`docs/architecture/demo-data-testing-accounts.html`'s stale institutional-Admin-role rows (already
known-stale from the earlier Admin/SuperAdmin consolidation, unrelated to this change but adjacent
enough to fix in the same pass).

## Steps

1. Remove the `filter_tutors_by_institution(...)` call at `views.py:1904` (tutor search) — use the
   plain queryset.
2. Remove the `filter_tutors_by_institution(...)` call at `views.py:3740`
   (`get_recommendation_candidate_tutors`) — use the plain queryset.
3. Remove both `filter_tutors_by_institution(...)` calls in `recommender/dashboard.py`
   (`_fallback` and `get_dashboard_recommendations`) — use the plain queryset.
4. Delete `filter_tutors_by_institution()` from `recommender/utils.py` and its now-unused import
   in `views.py` and `dashboard.py`.
5. Add `institution_name` to `TutorDetailSerializer` (`serializers.py:257`), sourced from
   `profile.institution.institution_name`.
6. Add an institution badge to `TutorDetails.vue`'s `.name-row`, next to `.verified-badge`, wired
   to the new `institution_name` field; add matching CSS as a sibling of `.verified-badge`.
7. Rewrite `InstitutionScopedMatchingTests` (`tests.py:6721`) — flip exclusion assertions to
   inclusion assertions for cross-institution matches, drop the null-institution-tutee tests, add
   coverage for the new serializer field.
8. Correct `docs/architecture/algorithm-demo-guide.html`'s "Scope" fact-card and
   `docs/architecture/demo-data-testing-accounts.html`'s stale institutional-Admin rows.
9. Run backend and frontend checks (see below); regenerate `docs/plans/index.html`.

## Risks

- Any other call site referencing `filter_tutors_by_institution` that a grep missed would break on
  import removal — mitigated by re-grepping after the edit, before deleting the helper.
- Existing tests beyond `InstitutionScopedMatchingTests` that assert candidate-pool size or
  same-institution-only results (e.g. in booking or dashboard test suites) may also depend on the
  old scoping and need adjusting alongside the dedicated class.
- `demo.py`'s `institution_id` optional-filter param (used only by the SuperAdmin Algorithm Demo
  tool) is a separate, already-optional mechanism and is out of scope for this change — left as-is.

## Checks to run

- `cd backend && venv\Scripts\python.exe manage.py test studybuddy.tests.InstitutionScopedMatchingTests` —
  rewritten tests pass.
- `cd backend && venv\Scripts\python.exe manage.py test` — full backend suite, no regressions.
- `npm run lint` — clean.
- `npm run build` — clean.
- Manual: open `TutorDetails.vue` for a seeded tutor (e.g. T1 Marisol Aquino) and confirm the
  institution badge renders next to the name.

## Changelog

- 2026-07-17: Plan drafted and approved via grilling session; implementation starting.
