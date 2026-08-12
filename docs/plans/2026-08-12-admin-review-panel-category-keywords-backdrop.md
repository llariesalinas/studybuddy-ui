---
title: Admin review panel — category taxonomy gap, keyword catalog check, backdrop fix
date: 2026-08-12
status: In Progress
summary: Let admins add a new category inline when a proposed subject's category doesn't match the catalog, suggest existing keywords while editing, and fix the segmented backdrop caused by the compact-density zoom bug.
spec: ../mockups/2026-08-12-admin-review-panel-category-keywords-backdrop.html
---

# Admin review panel — category taxonomy gap, keyword catalog check, backdrop fix

**Status & Progress Summary** (2026-08-12): Implemented and build-verified (`npm run build`, `npm
run lint` clean aside from pre-existing unrelated errors). One deviation from the approved design:
the Keywords field uses a custom-styled suggestion dropdown instead of a native `<datalist>` — the
datalist popup rendered with unstyled OS/browser chrome (plain dark box) that clashed with the
form, so it was swapped for a small absolutely-positioned dropdown matching `sb-card`/`sb-field`
styling. A success toast now confirms when a new category is
added on save, and the save also syncs into `catalogStore` locally so the category/keyword lists
update in the same session without a refetch. Merged `tutor-onboarding-plus-logo` onto this branch
(merge commit `16fb225`) so both feature sets ship together; resolved the resulting field-name
conflict in favor of `catalog_description` (the real backend field) and fixed an
`AdminTutorApplications.vue` script mismerge that had dropped the `savingSubjectEdit` ref (caught
by lint immediately after). **Found and fixed the actual cause of "Save Changes does nothing":**
`AdminTutorProposedSubjectDetailView.patch` (`backend/studybuddy/admin_views.py`) had its own
hardcoded validation rejecting any category outside `subject_taxonomy.CATEGORIES` — a leftover
400 guard that predates this feature and directly contradicts the "derive categories dynamically,
no fixed allowlist" design decision. Removed it, updated the one test that asserted the old
behavior, added a companion test for the still-required non-empty check, and added a failure
toast so a rejected save is no longer silent. All 10 tests in `AdminProposedSubjectReviewTests`
pass; `npm run build`/`lint` clean. The reported "backdrop broken again" was investigated and the
CSS fix (`zoom` scoped to `#app`) is confirmed intact and present in the built bundle — most likely
a stale dev-server/browser state after the branch churn, not a source regression; a dev-server
restart and hard refresh should resolve it, to be confirmed by the user.

Follow-up gap found by the user: a category added via the review panel didn't show up in the
**Course Catalog** page's (`AdminCourseCatalog.vue`) own category dropdown, because that page
still read the static `TAXONOMY_CATEGORIES` constant directly. Its create/edit form would also
have hit the same class of backend rejection as the "Save Changes does nothing" bug, via a second,
separate hardcoded check: `SubjectSerializer.validate_category`. Fixed both — the dropdown now uses
`deriveCategoryOptions(catalogStore.courseCatalog)` (same helper as the review panel), and the
serializer validator was removed. Course Catalog still has no "add a brand new category" input
itself (per the earlier "this panel only" scope decision) — this fix only makes *already-existing*
categories (however they were added) consistently selectable and saveable everywhere they're
shown, which is a data-consistency fix, not new scope. Updated/added backend tests; all pass.

## Goal

In the SuperAdmin "Review Application" offcanvas (`AdminTutorApplications.vue`), the Proposed
Subjects edit form silently fails to show a category when the tutor's proposed value isn't one of
the 6 hardcoded taxonomy categories, and the Keywords field has no way to check whether a keyword
already exists in the catalog. Separately, the offcanvas backdrop only dims part of the screen
when "Compact density" is active, because of a CSS `zoom` bug — that fix is app-wide, not
panel-specific.

## Approach

**Category taxonomy becomes dynamic.** `TAXONOMY_CATEGORIES` (`src/constants/subjectTaxonomy.js`)
stops being the sole source of categories. The list shown to admins is derived from the distinct
`category` values already present in `catalogStore.courseCatalog`, unioned with the original 6 as
a permanent floor so the list never shrinks below them. No backend model/migration — `Subjects.category`
is already a free-text field, so "adding a category" is just saving a subject with a new value.

**Category mismatch handling is scoped to this panel only.** `AdminCourseCatalog.vue`'s add/edit
form and `TutorSubjectSetup.vue`'s proposal flow keep their existing dropdown as-is; they'll pick
up newly-added categories implicitly (since the list is now derived from the catalog) but don't
get a new "add category" affordance in this pass.

When the edit form opens on a subject whose proposed category isn't in the derived list, it
auto-detects the mismatch, shows an inline note, and pre-selects "+ Add new category" mode with
the text input prefilled with the tutor's original proposed value — nothing is silently dropped.
The admin can accept it, edit it, or switch back to picking an existing category.

**Keywords get autocomplete suggestions.** Originally planned as a native `<datalist>`; switched
during implementation to a small custom dropdown (styled to match `sb-field`/`sb-card`) after
testing showed the datalist popup renders with unstyled OS/browser chrome that clashed with the
form. Built from every distinct keyword across all catalog subjects' comma-separated `keywords`
field, filtered against the in-progress comma segment as the admin types; picking a suggestion
completes that segment and adds a trailing `, ` to continue. Typing something new still just adds
it, same as today. Requires importing `useCatalogStore` and calling `fetchCourseCatalog()` in
`AdminTutorApplications.vue`, which doesn't happen today.

**Backdrop fix is a CSS-only, app-wide change.** Root cause: `main.css`'s
`:root[data-sb-density='compact'] { zoom: var(--sb-density-scale); }` scales the entire `<html>`
subtree, but Bootstrap's `.offcanvas-backdrop` (and the same class used as a manual backdrop div
in `AdminUsers.vue`/`AdminInstitutions.vue`/`AdminSupport.vue`) is `position: fixed` — under
Chromium's `zoom`, its fixed containing block is miscalculated, so the dim overlay only paints
~80% of the width/height from the top-left, leaving the rest of the (zoomed) viewport undimmed.
Live-validated fix: move the `zoom` declaration off `:root`/`<html>` and apply it only to `#app`
instead. Since Bootstrap's backdrop is appended as a sibling of `#app` under `<body>`, it then
sits outside the zoomed coordinate space and lines up with the real viewport again. All the other
`[data-sb-density='compact'] .selector { ... var(--sb-vh-fix) ... }` rules stay untouched — they
key off the `data-sb-density` attribute (still set on `<html>` by `density.js`, unchanged) and the
`--sb-density-scale`/`--sb-vh-fix` custom properties, not off where `zoom` itself is applied.

Mockup reviewed and approved: `docs/mockups/2026-08-12-admin-review-panel-category-keywords-backdrop.html`.

## Steps

1. **`src/constants/subjectTaxonomy.js`** — keep `TAXONOMY_CATEGORIES` as the floor constant, add
   a helper (or move the derivation into `useSubjectCatalog.js`/a new small composable) that merges
   it with distinct categories from `catalogStore.courseCatalog`.
2. **`src/stores/catalog.js`** — no changes expected; `fetchCourseCatalog` already exists.
3. **`src/views/AdminTutorApplications.vue`**:
   - Import `useCatalogStore`, call `fetchCourseCatalog()` on mount (or lazily when the offcanvas
     opens) so the derived category list and keyword datalist have data.
   - Replace the static `taxonomyCategories` computed with the catalog-derived list.
   - Add mismatch detection when `startSubjectEdit` runs: if `subject.category` isn't in the
     derived list, set the form into "add new category" mode, prefilled with `subject.category`,
     and show the inline warning note.
   - Add the `+ Add new category` option to the `<select>` and the small text-input/save/cancel
     sub-flow, matching the mockup.
   - Add a `<datalist id="catalog-keywords">` populated from the distinct keywords across
     `catalogStore.courseCatalog`, and wire it to the Keywords `<input>` via `list="catalog-keywords"`.
4. **`src/assets/main.css`** — in the compact-density block, remove `zoom: var(--sb-density-scale);`
   from `:root[data-sb-density='compact']` and add `[data-sb-density='compact'] #app { zoom: var(--sb-density-scale); }`.
5. Spot-check the `--sb-vh-fix` consumers listed in `main.css` (`.vh-100`, `.sb-sidebar`,
   `.admin-applications`, modal/dialog max-heights, etc.) still render correctly at compact density
   after the zoom-scope change, across Tutor/Tutee/SuperAdmin surfaces that use compact density.
6. Manually verify in the browser: open the Review Application panel with compact density on, on
   the SuperAdmin Applications page and on Users/Institutions/Support (which share the same
   backdrop bug), confirming the dim overlay now covers the full viewport.

## Risks

- Deriving categories from the catalog means a typo saved as a new category becomes a permanent
  option until an admin edits every subject that used it — accepted tradeoff per the "derive
  dynamically" decision (no backend model in this pass).
- `#app` is a Vue-mounted root div; confirm no other code assumes `zoom` lives on `<html>`
  (e.g. media queries or `window.devicePixelRatio`-based logic) before landing the CSS change.
- Compact density is used by Tutor/Tutee/SuperAdmin roles across many views (see
  `docs/plans/2026-08-10-superadmin-ui-80-percent-density.md` and its Tutor/Tutee predecessors) —
  the zoom-scope change is global, so the spot-check in step 5 needs to cover all three, not just
  the Applications page.

## Checks to run

- `npm run lint`
- `npm run build`
- Manual verification per step 6 above (compact density + Review Application panel, all four admin
  offcanvas panels).

## Changelog

- 2026-08-12: Plan created and approved via `/grill-with-docs` interview + `ui-preview` mockup.
- 2026-08-12: Implemented on `admin-review-panel-catalog-fixes` (branched off `main`). Keywords
  field switched from the planned native `<datalist>` to a custom dropdown after manual testing
  showed the datalist's unstyled browser popup. `npm run build` and `npm run lint` pass. Manual
  verification (compact-density backdrop, mismatch flow, keyword suggestions) still to be run.
  Committed as `f22dd53`.
- 2026-08-12: Added a success toast ("'X' added as a new category.") on `saveSubjectEdit` when the
  saved subject introduces a category not already in the derived taxonomy list, via the existing
  `useToastStore`/`SbToast` (already mounted globally in `App.vue`).
- 2026-08-12: Added `catalogStore.upsertLocalCatalogSubject()` and call it from `saveSubjectEdit`
  right after a successful save, so the derived category/keyword lists update immediately in the
  same session instead of waiting on the next `fetchCourseCatalog()`. `updateTutorProposedSubject`
  persists through a different endpoint than `catalogStore`'s own CRUD actions, so `courseCatalog`
  wasn't reflecting the save until this local sync was added.
- 2026-08-12: Merged `tutor-onboarding-plus-logo` onto this branch (merge commit `16fb225`);
  resolved conflicts, including a mismerge that briefly dropped `savingSubjectEdit`. Diagnosed
  "Save Changes does nothing" to a pre-existing hardcoded category allowlist in
  `AdminTutorProposedSubjectDetailView.patch` that 400'd any non-taxonomy category; removed it,
  updated/added backend tests, and added a failure toast so future save errors aren't silent.
  Confirmed the backdrop CSS fix is intact and present in the built bundle — the "broken again"
  report is most likely stale dev-server state from the branch churn, pending user confirmation
  after a restart/hard refresh.
- 2026-08-12: Fixed a second, related gap the user found: `AdminCourseCatalog.vue`'s category
  dropdown still read the static `TAXONOMY_CATEGORIES` constant, so a category added via the
  review panel didn't appear there. Switched it to the same `deriveCategoryOptions` helper, and
  removed the matching backend rejection (`SubjectSerializer.validate_category`), which would have
  400'd that page's own create/edit form for the same reason as the earlier "Save Changes does
  nothing" bug. Test `test_create_rejects_a_category_outside_the_taxonomy` replaced with
  `test_create_accepts_a_category_outside_the_curated_taxonomy` (also fixed a latent bug in the
  old test: it never supplied `department`, a required field, so its 400 was partly coincidental).
