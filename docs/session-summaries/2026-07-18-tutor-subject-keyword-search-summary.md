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

## Manual verification (2026-07-19)

Launched both dev servers (`npm run dev` + `manage.py runserver`) and drove the app in a browser.

- **Found and fixed a real bug first:** the dev database had never had migration
  `0078_subjects_keywords` applied — `makemigrations` was run during implementation, but only the
  *test* DB got `migrate`d (via `manage.py test`), not the dev DB. `/api/subjects/` 500'd
  (`column studybuddy_subjects.keywords does not exist`) until `python manage.py migrate studybuddy
  0078_subjects_keywords` was run. Any developer pulling this branch would have hit this.
- Registered a fresh tutor and confirmed: dropdown search results render correctly; a keyword-only
  match (searching "qubits" against a subject with "qubits" only in its `keywords` field, not its
  name) renders the `via "qubits"` badge; selecting a result shows "✓ Added" and keeps the search
  open; the zero-result state shows "Can't find it? Propose it" only on tutor onboarding; the
  propose form pre-fills `subject_name` with no visible keywords field, and the seeded value was
  confirmed via a direct DB read (`keywords: 'quantum computing xyz'`) after submission.
- Confirmed the admin review screen (`AdminTutorApplications.vue`) surfaces that seeded `keywords`
  value in its inline edit form, that editing and saving it persists correctly (`action=update`),
  and that approving moves the subject into the catalog where the updated keywords are then
  searchable and correctly badge-flagged.
- Confirmed the router guard in both directions: Back navigation between onboarding steps no
  longer bounces forward (tested on the original tutor, which had already completed Subjects);
  and, using a second fresh account with zero progress, a direct URL attempt to skip ahead to
  `/tutor-setup/verification` correctly redirected back to the actual furthest-incomplete step
  (Preferences) instead of loading.
- All QA accounts, the test proposed subject, and the test application created for this pass were
  deleted from the dev DB afterward; both dev servers were stopped.
