# Tutor subject keyword search + onboarding back-navigation — session summary

**Plan:** [docs/plans/2026-07-18-tutor-subject-keyword-search.md](../plans/2026-07-18-tutor-subject-keyword-search.md)
**Status:** Done
**Commit:** `5bdc25e` on `feat/subjects-reseed`

## What shipped

- `Subjects.keywords` — a new admin-editable, comma-separated text field (migration
  `0078_subjects_keywords`), exposed via `SubjectSerializer`.
- `SubjectTaxonomyPicker.vue` gained a persistent search input above the category grid. Typing
  filters the already-loaded subject list client-side (name, category, keywords) into a
  dropdown-row list, tagging keyword-only matches with a `via "..."` badge. Clearing the search
  returns to the existing category-card browsing UI. Used identically across all 4 call sites
  (tutor onboarding, FindTutors, InitialBooking, PreferenceSetup).
- Zero-result search on tutor onboarding (`TutorSubjectSetup.vue`) shows a "Can't find it?
  Propose it" prompt that opens the existing propose-subject form, pre-filling `subject_name` and
  silently (no visible field) seeding `keywords` from the search text. The other 3 (tutee-facing)
  screens show a plain empty state — no capture.
- `AdminCourseCatalog.vue` gained a `keywords` field on its add/edit form, and its own search now
  also matches on `keywords`.
- `AdminTutorApplications.vue`'s proposed-subject review rows are now inline-editable
  (`subject_name`, `category`, `keywords`, `description`) before approve/reject, via a new
  `action=update` path on `AdminTutorProposedSubjectDetailView` that atomically updates both the
  `Subjects` row and the related `TutorSubjects.description`.
- Back-navigation added across the 3-step tutor onboarding flow: a "← Back" button next to
  Continue (Subjects step) and next to Skip (Verify step). Required relaxing the router guard in
  `src/router/index.js` from "always force to next incomplete step" to "allow any step at or
  behind the furthest completed one; only block skipping ahead."
- New `src/constants/subjectTaxonomy.js` — extracted during code review to remove a hardcoded
  taxonomy-category list duplicated between `AdminCourseCatalog.vue` and the new
  `AdminTutorApplications.vue` edit form.

## Deviations from the plan

- `propose_tutor_subject`'s response body (a pre-existing hand-built dict) was missing `keywords`
  — fixed during code review since the frontend pushes that response directly into its local
  subject list.
- The commit bundles an unrelated, already-in-progress "remove institution matching constraint"
  change (see `docs/plans/2026-07-17-remove-institution-matching-constraint.md`) that was sitting
  uncommitted in the same shared backend files (`views.py`, `serializers.py`, `tests.py`) before
  this session started. Bundling was an explicit user decision (not this plan's scope) made after
  discovering the mixed-file situation; a third, still-unrelated batch of pending work (docs status
  cleanup, `TutorDetails.vue`) was identified and deliberately left uncommitted.

## Checks run

- `npm run lint` — clean (4 pre-existing errors in unrelated `make_algo_pptx.*` files, not touched
  by this work).
- `npm run build` — succeeds.
- `python manage.py test` (targeted): `GlobalSubjectCatalogTests`, `TutorSubjectProposalTests`,
  `AdminProposedSubjectReviewTests` — 21 tests, all pass.
- `python manage.py test` (full suite): 339 tests, 19 failures + 1 error — all in unrelated areas
  (cashout fee math, avatar upload, verification-dev-tools env flags); confirmed via diff
  inspection to predate this session's changes.
- Two-axis `/code-review` (Standards + Spec) against `HEAD`, scoped to this feature's files.
  Findings fixed: hardcoded taxonomy list (→ shared constant), `keywords` missing from the
  propose-subject response, missing `docs/architecture/booking-flow.md` update, and a minor
  duplicate-match-logic cleanup in `SubjectTaxonomyPicker.vue`.

## Not done

- **Manual in-browser verification was not performed** — no dev server was launched to click
  through search/select on the 4 picker call sites, the full propose → admin-review → approve
  loop, or the new Back buttons. Only static code review and automated tests were run. This should
  be done before considering the feature fully verified.
