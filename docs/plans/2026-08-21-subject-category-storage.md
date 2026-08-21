---
title: subject-category-storage
date: 2026-08-21
status: Done
summary: Give Category its own table so it can exist without subjects, and seed Uncategorized and Sports.
spec:
---

# subject-category-storage

## Goal

A subject category currently has no storage of its own: the pickable list is derived from the
distinct `Subjects.category` strings already in the catalog, unioned with a hardcoded floor of six
names. A category with no subjects is therefore unrepresentable, which is why `Uncategorized` and
`Sports` could not be added and why an admin-created category disappears when its last subject is
removed. Give `SubjectCategory` a table and a foreign key, so a category is a thing that exists on
its own.

## Approach

`Subjects` already follows the pattern "Python fixture seeds it, a DB table owns it"
(`subject_taxonomy.SUBJECTS` -> `seed_data.py` -> the `studybuddy_subjects` table). Categories have
the fixture half and no table half. This change gives them the same two-layer shape:
`subject_taxonomy.CATEGORIES` stays the seed source, a new table becomes the runtime source of
truth, and the frontend fetches the list instead of deriving it.

Decisions settled in the grilling session:

- **A real table, not a widened hardcoded list.** The two requested categories are exactly the
  cases the derived model cannot represent: `Uncategorized` must persist while empty (that is its
  job) and `Sports` starts with zero subjects.
- **ForeignKey, not a validated string.** A free `CharField` leaves the same drift: a write that
  bypasses the serializer still mints a phantom category. The FK also makes a rename one write
  instead of ~140.
- **Auto `id` PK.** Using `name` as a natural key would forfeit the rename-for-free property the
  FK just bought. No `code` slug: `Subjects.subject_code` exists because subject codes travel in
  URLs; categories are referenced by name and do not need a second identifier to keep in sync.
- **`display_order`.** `deriveCategoryOptions()` returns the six curated categories in authored
  order (Mathematics first, Hobbies & Arts last), then admin-added ones alphabetically. Sorting by
  name would silently reshuffle every picker. Seeded 10/20/30... so a category can be wedged in
  later without renumbering; `Uncategorized` gets 999 so the fallback sorts last.
- **`on_delete=models.SET(get_uncategorized)`.** CASCADE is ruled out - `TutorSubjects` and
  `Preference.subjects` FK into `Subjects`, so it would strip tutor expertise and tutee
  preferences. PROTECT is safe but walls the admin in, since this change ships no bulk-reassign
  UI. SET moves orphans to the sink, losing nothing. The tradeoff is that SET is quiet, mitigated
  by a delete confirmation that states the subject count rather than by a different `on_delete`.
- **Non-nullable FK.** `Subjects.category` is `null=True, blank=True` today, so "no category" has
  three representations (`NULL`, `''`, and now `Uncategorized`). The migration backfills the first
  two into the third and the column becomes `null=False`.
- **`is_system`.** `Uncategorized` is the deletion sink, so it must not be deletable or the sink
  can vanish. One boolean, `True` only for `Uncategorized`, enforced by the delete endpoint.
- **Case-insensitive uniqueness.** `UniqueConstraint` on `Lower('name')` so `sports` cannot join
  `Sports`. Input is trimmed; stored as typed.
- **API shape unchanged.** `SubjectSerializer` keeps emitting `category` as a plain name string via
  `SlugRelatedField`, so no existing frontend read of `subject.category` breaks.
- **Categories are admin-owned.** `propose_tutor_subject` resolves the submitted name against
  existing categories (case-insensitive) and rejects an unknown one; the tutor-side picker only
  offers existing categories, so a mismatch signals a client bug rather than a legitimate case. The
  admin review panel keeps its ability to mint a new category on approval.

Out of scope: a category rename/delete management screen. The model supports both; no UI ships here.

## Steps

1. Add `SubjectCategory` to `backend/studybuddy/models.py` (`name` unique, `display_order`,
   `is_system`, `Meta.ordering = ['display_order', 'name']`, `UniqueConstraint` on `Lower('name')`)
   and a module-level `get_uncategorized()` for `on_delete`.
2. Append `Uncategorized` and `Sports` to `subject_taxonomy.CATEGORIES` - appended, never
   prepended, because `CATEGORIES[:1]` is the seed affinity default in `seed_data.py:505,524`.
3. Migration `0085`: create the table, seed one row per `CATEGORIES` entry with `display_order`
   10/20/30... (`Uncategorized` 999, `is_system=True`), add a nullable `category_fk`, backfill it
   from the existing `category` strings (creating rows for any admin-added value not in the
   fixture, and mapping `NULL`/`''` to `Uncategorized`), then drop the old column, rename, and set
   `null=False`.
4. Point `SubjectSerializer.category` at a `SlugRelatedField(slug_field='name')` and replace the
   stale free-text comment.
5. Update the write paths: `AdminCourseCatalogView.post/patch` (get-or-create the category so an
   admin can still mint one), its `get` category filter (`category` -> `category__name`),
   `admin_views.py:1750-1760` review-panel approval, and `views.py:4460` tutor proposal
   (resolve-or-reject).
6. Add `GET/POST/PATCH/DELETE admin/subject-categories/` with `IsSuperAdminUser`, refusing deletion
   of an `is_system` row and reporting the affected subject count.
7. Frontend: add category fetch/CRUD to `src/services/`, expose the list through
   `src/stores/catalog.js`, delete `deriveCategoryOptions()` and `TAXONOMY_CATEGORIES` from
   `src/constants/subjectTaxonomy.js`, and repoint `AdminCourseCatalog.vue:30` and
   `AdminTutorApplications.vue:432`.
8. Add `+ Add new category...` to `AdminCourseCatalog.vue` - it currently has a plain `<select>`
   and cannot mint a category at all, unlike the review panel.
9. Update `seed_data.py` to seed categories before subjects, and update `tests.py:9933-9936`
   (which asserts every `SUBJECTS` category is in `CATEGORIES`) plus
   `src/constants/subjectTaxonomy.js` consumers' tests.

## Risks

- **The backfill is the dangerous step.** It rewrites every `Subjects` row. Any distinct string in
  production not present in the fixture must become a row rather than being dropped on the floor;
  verify the distinct-value list against the DB before running it.
- **Case-collapse on backfill.** If production already holds both `Sports` and `sports`, the
  `Lower('name')` constraint makes them one row. The migration must fold them deliberately (first
  spelling wins) rather than crashing halfway.
- **`SET` is quiet.** Deleting a populated category relabels its subjects with no hard stop; the
  confirmation copy is the only guard.
- **Tutor proposal now rejects unknown categories** where it previously accepted anything. Correct
  per the admin-owned decision, but it is a behavior change on a tutor-facing path.
- **Ordering regression.** If `display_order` is seeded wrong, every picker reshuffles visibly.

## Checks to run

- `cd backend && python manage.py migrate` - applies cleanly on a copy of the dev DB.
- `cd backend && python manage.py test` - full Django suite passes.
- `cd backend && python manage.py seed_data` on a fresh DB - subjects land in the right categories
  and the picker order matches today's authored order.
- `npm run test` - Vitest, including `src/stores/catalog.test.js` and
  `src/components/subjectPicker.shared.test.js`.
- `npm run lint` and `npm run build` - both clean.
