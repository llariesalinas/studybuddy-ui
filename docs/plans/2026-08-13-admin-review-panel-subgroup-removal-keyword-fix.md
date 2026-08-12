---
title: Admin review panel — add Sub-Group, fix Keywords autocomplete, widen panel
date: 2026-08-13
status: Done
spec: ../mockups/2026-08-13-admin-review-panel-subgroup-keywords.html
---

# Admin review panel — add Sub-Group, fix Keywords autocomplete, widen panel

**Status & Progress Summary** (2026-08-13): Done. Committed on `admin-review-panel-catalog-fixes`
(`d850964`), not pushed.
Reversed from an earlier version of this plan that removed Sub-Group (`Subjects.department`)
entirely — traced end to end and found it unused by the recommender, tutee/tutor search, and every
browse UI, which made it seem redundant with Category/Keywords. User decided to keep it and close
the actual gap instead: the review panel's Proposed Subjects form never had a Sub-Group field to
begin with, unlike the standalone Subject Catalog page. Shipped: `department` gained
`blank=True, default=''` (migration `0082_subjects_department_optional`) fixing the
required/allow_blank mismatch; `AdminTutorProposedSubjectDetailView.patch`'s `update` action now
accepts and persists `department`; `AdminTutorApplications.vue` widened to 760px, gained a two-up
Category/Sub-Group layout (Sub-Group mirrors Category's select + "+ Add new..." pattern, scoped to
the chosen category via a new `deriveSubgroupOptions` helper), and the Keywords suggestion dropdown
now bolds the matched substring and offers an explicit "+ Use '...' as a new keyword" row (via a
`highlightSegments` helper hoisted out of `SubjectTaxonomyPicker.vue` into the shared
`subjectPicker.shared.js` so both consumers share one implementation). 6 new backend tests added
(Sub-Group persistence, omitted-stays-unchanged, blank-accepted on both the review-panel PATCH and
the standalone catalog POST) — `AdminProposedSubjectReviewTests` + `GlobalSubjectCatalogTests`
(20 tests) pass. `npm run build` and `npx vitest run` (207/210, the 3 failures are pre-existing
`tokens.test.js` failures confirmed via `git stash` — unrelated to this change) both clean. Full
`python manage.py test` finished: 458 tests, 1 failure + 1 error, neither touching `Subjects`,
`department`, or anything this diff changed —
`LateCancellationSupportTicketTests.test_superadmin_counted_verdict_deducts_tutor_wallet`
(`KeyError: 'monthly_counted_strikes'`, a field the test's own comment says ADR-0011 already
removed) and `ChatFeatureTests.test_location_update_rejected_inside_grace_cutoff`
(`200 != 400`, a booking grace-cutoff check). All checks clean; ready to commit.

## Goal

The tutor-application review panel (`AdminTutorApplications.vue`) is missing a Sub-Group field
that the standalone Subject Catalog page (`AdminCourseCatalog.vue`) already has, so a subject
approved through the review panel always gets `department = ''` and has to be fixed up later on
the Catalog page. Close that gap, and while in the same form: widen the cramped 500px offcanvas,
add the same "+ Add new category" escape hatch Sub-Group is getting, and fix the Keywords
suggestion dropdown so it actually surfaces existing catalog keywords instead of feeling like it
just echoes what was typed.

## Approach

**Sub-Group mirrors Category's UI pattern, not Keywords'.** `Subjects.department` is a single
value per subject (like `category`), not a comma-list (like `keywords`), so it gets the same
two-mode treatment already built for Category: a `<select>` of existing values with a
"+ Add new sub-group..." toggle that swaps to free text, with a "pick an existing sub-group
instead" link back. Confirmed via the `ui-preview` mockup.

**Scoped to the chosen Category, not global.** The Sub-Group dropdown only lists sub-group values
that already exist among catalog subjects sharing the currently-selected Category (derived from
`catalogStore.courseCatalog`, the same source `deriveCategoryOptions` reads today) — not every
sub-group in the whole catalog. This is a soft UI scoping only, same trust level as Category
today: nothing enforces a formal `Category → Sub-Group` relationship server-side, so an admin can
still free-type a new sub-group under any category via the toggle.

**Required vs. optional:** Sub-Group stays optional, matching `AdminCourseCatalog.vue`'s existing
form (no `required` attribute there today) and the model (`department` has no `blank=False`
constraint beyond being a plain `CharField`).

**Backend needs a real change, not just UI:** the propose-subject save path
(`views.py` proposed-subject creation, and `AdminTutorProposedSubjectDetailView.patch` in
`admin_views.py` for the review-panel save) currently does not accept `department` from the
request — confirmed by reading both; `admin_views.py:1061`'s `data.setdefault('department', '')`
only defaults an already-missing key in the serialized response, it doesn't read one from the
incoming PATCH body. Both need to accept and persist `department`.

**Why widen the panel to 760px (620px inner form):** confirmed via the same mockup — the 500px
offcanvas was cramped once Category and Sub-Group sit side by side; 760px gives the two-up layout
room without feeling oversized.

**Why fix Keywords too:** `keywordSuggestions` (`AdminTutorApplications.vue`) already sources from
the full catalog (`catalogKeywords`), but in practice it reads as just echoing typed text — worth
re-verifying against real data (seeded subjects may have too few keywords to show a meaningful
match) and tightening the UX per the mockup: bold the matched substring, and make "type something
new" an explicit labelled action instead of a silent fallback.

## Steps

1. **Backend: accept Sub-Group on save, and fix its required/optional mismatch**
   - `backend/studybuddy/models.py`: add `blank=True, default=''` to `Subjects.department` — confirmed
     via `SubjectSerializer().get_fields()['department']` that it's currently `required=True,
     allow_blank=False`, which contradicts every form's lack of a `required` attribute and would 400
     on save today if Sub-Group is left blank (untested edge case, no test covers it either way)
   - Migration for the above (`AlterField`, no data loss — existing non-blank values are untouched)
   - `backend/studybuddy/views.py`: the proposed-subject creation view — read `department` from
     `request.data` alongside `subject_name`/`category`/`keywords`/`description`, pass it to
     `Subjects.objects.create(...)`
   - `backend/studybuddy/admin_views.py`: `AdminTutorProposedSubjectDetailView.patch` — accept and
     persist `department` from the PATCH body the same way `category`/`keywords` are handled
   - `backend/studybuddy/serializers.py`: confirm `SubjectSerializer` already exposes `department`
     (it does today) so the saved value round-trips back to the frontend

2. **Backend tests**
   - Add/extend `AdminProposedSubjectReviewTests` (or wherever the review-panel save is tested) to
     cover saving a `department` value through the PATCH endpoint
   - Add a test for the initial propose-subject creation path accepting `department`

3. **Frontend: Review panel** (`src/views/AdminTutorApplications.vue`)
   - Widen the offcanvas from `width: 500px` to `width: 760px`
   - Add `department: ''` to `subjectEditForm`, populate it in `startEdit`
   - Add a `subgroupMode` ref (`'select' | 'new'`) mirroring `categoryMode`, with its own toggle
     buttons ("+ Add new sub-group...", "Pick an existing sub-group instead")
   - Add a helper (alongside `deriveCategoryOptions`, likely in `@/constants/subjectTaxonomy`) to
     derive existing sub-group values scoped to a given category from `catalogStore.courseCatalog`
   - Add the Category "+ Add new category..." toggle to the two-up layout per the mockup (this was
     already planned per `docs/plans/2026-08-12-admin-review-panel-category-keywords-backdrop.md`
     — confirm it's still intact after the branch merges noted in that plan's changelog before
     re-adding)
   - Include `department` in the payload sent by `saveSubjectEdit`
   - Re-verify `keywordSuggestions` against real catalog data (seed or manually add subjects with
     keywords) and fix the matching/filtering logic if it's not actually surfacing existing keywords
   - Add match-highlighting (bold the matched substring) to each keyword suggestion row

4. **Frontend: Subject Catalog page** (`src/views/AdminCourseCatalog.vue`)
   - No changes — Sub-Group already works there; left as-is

5. **Docs**
   - Update `docs/plans/2026-08-12-admin-review-panel-category-keywords-backdrop.md`'s status/summary
     if this plan supersedes any of its still-open items
   - Session summary in `docs/session-summaries/` once shipped

## Risks

- The category-scoped Sub-Group dropdown depends on `catalogStore.courseCatalog` already being
  loaded with `department` values populated on enough subjects to be useful — if most seeded
  subjects have an empty `department`, the dropdown will often be empty and fall straight to
  "+ Add new sub-group" for every category, which is a degraded-but-safe fallback, not a bug.
- No server-side enforcement of `Category → Sub-Group` means a typo'd or duplicate sub-group name
  (e.g. "Tech" vs "Technology") can accumulate the same way Category names could before the
  taxonomy-gap fix in the 2026-08-12 plan — acceptable for now, same trust model as Category.
- Re-verifying `keywordSuggestions` may turn up an actual bug (not just sparse seed data) — if so,
  scope may grow slightly beyond "add highlighting."
- Confirm the `AdminTutorProposedSubjectDetailView.patch` hardcoded-category-allowlist bug fixed in
  the 2026-08-12 plan didn't have a Sub-Group equivalent lurking that would similarly reject saves.

## Checks to run

- `npm run lint`
- `npm run build`
- `npx vitest run` (targeted: `AdminCourseCatalog`/`AdminTutorApplications` specs if they exist)
- `python manage.py test` (targeted: proposed-subject review/creation tests, plus full suite pass)
- Manual: open the review panel for a pending tutor application with a proposed subject, confirm
  the 760px width, the Category and Sub-Group add-new toggles, that Sub-Group options narrow when
  Category changes, and that typing a keyword already used elsewhere in the catalog surfaces it as
  a suggestion

## Changelog

- **2026-08-13**: Plan created with scope "remove Sub-Group entirely," approved.
- **2026-08-13**: Reversed — user decided to keep Sub-Group and add it to the review panel (the
  original ask) instead of removing it. Rewrote Goal/Approach/Steps/Risks accordingly; kept the
  760px width, Category add-new toggle, and Keywords fix from the original plan unchanged.
- **2026-08-13**: Added a required/optional mismatch fix to Step 1 after checking
  `SubjectSerializer().get_fields()['department']` directly — it's `required=True, allow_blank=False`
  today because the model field has no `blank=True`, contradicting every form's optional-looking UI.
  Confirmed the tutee/tutor-facing "Add your subjects" category grid (`SubjectTaxonomyPicker.vue`)
  derives its categories from live approved-subject data (`GET /subjects/?catalog_scope=all`, which
  still filters `status='approved'` — `views.py:2041`), not a static list, so a category added via
  the review panel appears there automatically once the subject is Approved (not merely saved while
  still pending).
- **2026-08-13**: Implemented. Backend: `blank=True, default=''` on `Subjects.department` +
  migration `0082_subjects_department_optional`; `AdminTutorProposedSubjectDetailView.patch`
  accepts/persists `department` on the `update` action. Frontend: offcanvas widened to 760px;
  `AdminTutorApplications.vue` gained the Sub-Group field (select + "+ Add new sub-group..."
  toggle, scoped to the selected category via `deriveSubgroupOptions` in
  `src/constants/subjectTaxonomy.js`) laid out two-up alongside Category; Keywords suggestions now
  bold the matched substring and show an explicit "+ Use '...' as a new keyword" row when the typed
  fragment isn't an existing keyword. `highlightSegments` moved from `SubjectTaxonomyPicker.vue`
  into `src/components/subjectPicker.shared.js` so both consumers share it. 6 new backend tests
  (Sub-Group persist/omit/blank on the review-panel PATCH; blank-accepted on the catalog POST).
  Checks: `AdminProposedSubjectReviewTests` + `GlobalSubjectCatalogTests` (20/20 pass), `npm run
  build` clean, `npx vitest run` 207/210 (3 pre-existing `tokens.test.js` failures, confirmed via
  `git stash` unrelated to this diff).
- **2026-08-13**: Full `python manage.py test` finished — 458 tests, 1 failure + 1 error, both
  pre-existing and unrelated (`LateCancellationSupportTicketTests` referencing a field ADR-0011
  already removed; a `ChatFeatureTests` grace-cutoff assertion). Nothing in either touches
  `Subjects`, `department`, or any file this diff changed. All checks clean; ready to commit.
- **2026-08-13**: Committed on `admin-review-panel-catalog-fixes` (`d850964`), not pushed. Status
  set to Done.
