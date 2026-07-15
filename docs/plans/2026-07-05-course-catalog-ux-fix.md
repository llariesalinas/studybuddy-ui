---
title: Course catalog UX fix
date: 2026-07-05
status: Done
spec:
---

# Course catalog UX fix

## Status & Progress Summary

**Status:** Done — all four changes implemented; review-caught modal bug fixed (see changelog); lint clean, build passes.

## Goal

Fix the Admin Course Catalog screen so it works for any course (not just the hardcoded 9 from seed
data), enforce course-level subject visibility across the institution system, auto-fill
`subject.category` when an admin adds a subject to a course catalog, and replace the course
dropdown with a searchable modal picker.

## Approach

The backend filtering is already correct — `SubjectListView` routes through
`subject_selection_queryset_for_profile` (course-level, no fallback) by default and only bypasses
to `visible_subject_queryset_for_profile` when the admin catalog screen sends `catalog_scope=all`.
`reset_demo_data.py` already seeds both institutions with full catalog entries.

The only backend change is auto-filling `subject.category` on catalog entry creation
(fill-only-if-blank — never overwrite). The frontend "Available Subjects" panel has a hard category
filter that breaks for any course not in the original 9; removing it makes the screen work for any
course an admin picks. The course `<select>` is replaced with a searchable modal picker.

Key decisions settled in grilling:
- Available Subjects: show all institution-visible subjects (no hard category gate)
- `subject.category` auto-fill: fill-only-if-blank on Add, to self-heal courses like BA-POLSCI
- Subject visibility elsewhere: course-level filtering, no fallback (already implemented in backend)
- Grandfathering: subjects already in a user's profile stay visible via `include_current=True`
- CBF already catalog-aware: `get_student_subject_codes` filters through
  `recognized_subject_codes_for_profile`, so catalog changes immediately affect matching scores
- Global subjects: keep as static seeded list; no SuperAdmin UI for adding them (deferred)

## Steps

1. **`admin_views.py`** — in `AdminCourseCatalogView` POST handler, after the catalog entry is
   created, check if `entry.subject.category` is blank; if so, write the course code and save the
   subject row.
2. **`AdminCourseCatalog.vue`** — remove the `selectedCourseCategories` computed and its filter
   from `availableSubjects`; show all subjects from `catalogStore.subjects` directly (search/sort
   still applies).
3. **`AdminCourseCatalog.vue`** — replace the course `<select>` in the toolbar with a button
   showing the current course name; clicking it opens a Bootstrap modal with a search input and a
   scrollable list of courses to pick from.
4. **`docs/artifacts/2026-07-04-recommendation-algorithm-explainer.html`** — add a note in the CBF
   section explaining catalog-awareness of `get_student_subject_codes`, and add a new row in the
   Known Gotchas table: "Subject in preferences doesn't contribute to matching."

## Risks

- Removing the category filter means the Available Subjects panel for a superadmin scoped to an
  institution with no catalog entries shows every global subject — which is correct but may feel
  noisy. Search and the "Add/Added" button state mitigate this.
- Auto-filling `subject.category` writes to a global subject row shared across institutions; using
  fill-only-if-blank avoids overwriting but means the first institution to add a subject "wins" its
  category tag. Acceptable because category is a soft display hint, not a hard routing field.
- The course modal replaces a `<select>` so keyboard/form semantics change slightly; ensure it is
  also operable for the SuperAdmin institution+course selection flow.

## Checks to run

- `cd backend && python manage.py test studybuddy.tests.InstitutionCourseCatalogTests`
  Passing result: catalog tests still pass with no regressions.
- `npm run lint`
  Passing result: no lint errors on changed files.
- `npm run build`
  Passing result: build completes with no type/import errors.
- Manual verification:
  - Select a course not in original seed data → Available Subjects is populated
  - Add a subject with blank category → subject.category is now set to the course code
  - Course picker modal opens, search filters the list, selecting a course closes the modal and
    loads that course's catalog

## Changelog

- **2026-07-05** — Plan created after grilling session covering all design decisions (category filter removal, fill-only-if-blank auto-fill, course modal picker, catalog-aware CBF, grandfathering edge case). Status set to In Progress; implementation pending.
- **2026-07-05** — Implemented: auto-fill `subject.category` in `admin_views.py` POST handler; removed hard category filter from `availableSubjects` in `AdminCourseCatalog.vue`; replaced course `<select>` with searchable modal picker; added catalog-awareness section and two new gotcha rows to algorithm explainer; fixed pre-existing `pruneSubjectsForCurrentLevel` unused-var lint error in `TuteeProfile.vue`. Lint clean, build passes.
- **2026-07-05 (review fix)** — Review caught that the course modal used `window.bootstrap.Modal`, but `main.js` only imports Bootstrap CSS (JS is not attached to `window`), so the modal would never open. Rewrote it to the codebase's standard pure-Vue-state modal pattern (`showCourseModal` ref + `v-if` backdrop + `:class="{ show, 'd-block' }"`), matching `AdminInstitutions.vue`. Re-verified lint + build. Status: Done.
