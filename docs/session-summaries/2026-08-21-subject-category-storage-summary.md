# Subject category storage - session summary

Date: 2026-08-21
Plan: [docs/plans/2026-08-21-subject-category-storage.md](../plans/2026-08-21-subject-category-storage.md)

## What shipped

Categories stopped being an emergent property of subject rows and became a stored entity.

- **New `SubjectCategory` model** (`backend/studybuddy/models.py`): `name` (unique, plus a
  `UniqueConstraint` on `Lower('name')` so `sports` cannot join `Sports`), `display_order`,
  `is_system`. Auto `id` PK so a rename does not break the foreign key.
- **`Subjects.category` is now a ForeignKey**, non-nullable, `on_delete=models.SET(get_uncategorized)`.
- **Migration `0085_subjectcategory`** creates the table, seeds one row per taxonomy category,
  backfills every existing category string (minting rows for admin-added values not in the
  fixture, folding case variants, mapping `NULL`/`''` onto `Uncategorized`), then drops the old
  column and makes the FK non-nullable.
- **`Uncategorized` and `Sports` seeded**, appended to `subject_taxonomy.CATEGORIES`.
- **New endpoint** `admin/subject-categories/` (GET/POST/PATCH/DELETE, SuperAdmin only), refusing
  deletion of an `is_system` row and logging how many subjects a delete moved.
- **`AdminCourseCatalog.vue` can now mint a category** via `+ Add new category...`; it previously
  had a plain `<select>` and no way to create one at all.
- **`deriveCategoryOptions()` and `TAXONOMY_CATEGORIES` deleted**; both admin screens read the
  stored list through the catalog store.

## Deviations from the plan

1. **`Subjects.category` got `default=get_uncategorized_id`.** The plan said non-nullable and
   stopped there. Making it non-nullable broke roughly 30 existing `Subjects.objects.create()`
   calls that pass no category. The default is the better answer rather than a workaround: "no
   category stated" and "category deleted out from under it" are the same situation, and giving
   them one representation is the whole point of the sink.
2. **`recommender/cbf.py` needed a real fix, not a mechanical one.** `values_list('category')` now
   yields ids while `ts.subject.category` yields an object, so the same-field comparison would
   have silently never matched and quietly degraded every recommendation. Both sides now compare
   ids. `Uncategorized` is excluded from the target set - it is a fallback bucket, so two subjects
   sharing it are not in the same field, and the legacy `NULL`/`''` categories it replaces were
   skipped there for the same reason.
3. **`select_related('category')` added** to the subject querysets that feed `SubjectSerializer`
   and to the tutor-subject payloads, since rendering the category by name is otherwise a
   per-row query.
4. **`reset_demo_data` now clears categories too**, after the subjects, so the `on_delete`
   fallback does not recreate `Uncategorized` on the way out.
5. **Two serializer payloads leaked the category object** (`get_proposed_subjects`,
   `get_selected_subjects` in `TutorApplicationSerializer`) and now emit `.name`.
6. **`ADD_NEW_OPTION` extracted** to `src/constants/subjectTaxonomy.js`. The `'__add_new__'`
   sentinel was repeated across the review panel and was about to be repeated again in the catalog
   screen.
7. **A category rename/delete management screen was not built**, as scoped. The model and endpoint
   support both.
8. **The tutor-proposal contract change showed up in the suite exactly where the plan predicted.**
   `test_proposal_accepts_a_category_outside_the_curated_taxonomy` encoded the old rule (any
   category string is accepted and created on the spot). It was rewritten to keep its original
   intent - an admin-added category beyond the curated six must still be accepted - by creating
   the category first, and `test_proposal_rejects_a_category_that_does_not_exist` was added for
   the new rule. This is safe because the tutor-side picker only offers existing categories, but
   any client that free-types a category on that path will now get a 400 instead of minting one.

## Flaky tests observed, not caused here

Three tests failed on one full run and passed on the next, with a different one failing instead:
`SessionCheckInTests.test_tutee_can_record_midpoint_check_in`,
`SessionCheckInTests.test_duplicate_check_in_returns_existing_response`,
`ChatFeatureTests.test_confirmed_active_session_returns_ongoing`, and
`ChatFeatureTests.test_location_update_rejected_inside_grace_cutoff`. All four depend on wall-clock
time relative to a session window or the 12-hour grace cutoff, and none of them reads
`Subjects.category`. Worth pinning to a frozen clock at some point; out of scope here.

## Operational note

A killed test run leaves an idle Postgres connection on `test_postgres`, after which Django cannot
create or drop the test database ("database is being accessed by other users"). Terminating that
backend clears it.

## Checks run

- `python manage.py makemigrations --check --dry-run` - no changes detected; migration state
  matches the models.
- `python manage.py check` - no issues.
- `python manage.py test studybuddy` - **517 tests, 1 failure**. The failure is
  `ChatFeatureTests.test_location_update_rejected_inside_grace_cutoff`, which is clock-dependent
  and unrelated: its own comment states "the session is today at 14:00 and the cutoff is 12 hours
  out, so it has already passed", which only holds when the suite runs after 02:00. This run
  finished at 00:2x, so 14:00 was still ~14 hours away, the grace cutoff had genuinely not passed,
  and the 200 it returned is correct behaviour.
- `python manage.py test` on the category-related classes (`SubjectCategoryStorageTests`,
  `AdminCourseCatalogTaxonomyTests`, `AdminProposedSubjectReviewTests`,
  `TutorSubjectProposalTests`, `SubjectTaxonomyModuleTests`) - 40 tests, OK.
- `npx vitest run src/stores/catalog.test.js src/components/subjectPicker.shared.test.js` -
  17 passed.
- `npm run lint` - 4 pre-existing `no-undef` errors in `make_algo_pptx.cjs` / `make_algo_pptx.js`,
  neither touched by this change. Nothing in the changed files.
- `npm run build` - clean.
- Full `npm run test`: 9 unrelated failures in `src/assets/tokens.test.js` and
  `src/components/BookingTimeRangePicker.test.js`, which belong to the in-flight mode-switcher
  work already in the tree, not to this change.

## Not run

- **`python manage.py seed_data` against a fresh database.** It would wipe the local dev data, so
  it was not run unilaterally. Covered indirectly by
  `test_seed_data_assigns_category_rows_and_keeps_empty_ones`, which calls the command's
  `_seed_subjects()` directly and asserts that `Sports` and `Uncategorized` survive with no
  subjects and that `subjects_by_category` is still keyed by name.
- **The migration against production data.** The backfill is the risky step: verify the distinct
  `category` values in the production database before running it, particularly any case variants,
  which the `Lower('name')` constraint will fold into one row.
