# Institution course catalog summary

Implemented the institution-scoped catalog feature from
`docs/specs/2026-07-05-institution-course-catalog-design.md`.

## Shipped

- Added `Subjects.owning_institution` for institution-private Custom Subjects.
- Added `InstitutionCourseCatalog` for Partner Institution + Course + Subject curation.
- Added admin APIs to list/add/remove catalog entries and create Custom Subjects.
- Scoped `SubjectListView` so private subjects are only visible to their owning institution.
- Added `AdminCourseCatalog.vue`, route/sidebar navigation, and catalog-store methods.
- Updated `reset_demo_data` so CPU and North University seed visibly different catalogs, including
  a North-only Custom Subject.
- Refined `CONTEXT.md` glossary entries for Institution Course Catalog, Institution Catalog Entry,
  and Custom Subject.

## Verification

- `python manage.py check` passed.
- `python manage.py test studybuddy.tests.InstitutionCourseCatalogTests --keepdb` passed
  (6 tests).
- `npm run lint` passed after rerunning outside the sandbox because Windows blocked child-process
  spawning inside the sandbox.
- `npm run build` passed after rerunning outside the sandbox for the same child-process reason.
- `python manage.py test --keepdb` completed with the broader pre-existing backend baseline still
  failing (15 failures, 3 errors in this keepdb run), including recommendation, email queue,
  avatar, and payment-method/test-db-state failures outside this feature.
