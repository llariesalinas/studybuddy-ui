---
title: Initial booking subject picker modal
date: 2026-07-20
status: In Progress
summary: Replace the inline SubjectTaxonomyPicker on InitialBooking with a compact trigger that opens a two-pane subject modal.
spec: ../mockups/2026-07-20-initial-booking-subject-modal.html
---

# Initial booking subject picker modal

## Status & Progress Summary

**In Progress** — implemented and committed (`21774b6`): shared search module
`src/components/subjectPicker.shared.js` (TDD, 9 tests), new `SubjectPickerModal.vue`
(trigger + two-pane modal, arrow-key nav, mobile pill collapse), swapped into
`InitialBooking.vue`; two-axis code review run and all actionable findings fixed. Scope
extended 2026-07-20: the flagged FindTutors.vue follow-up was confirmed and the same swap
applied there after a ui-preview comparison (modal chosen over popover/combobox alternatives).
Automated checks green (lint / build / 77-test suite). Remaining: the manual dev-server visual
pass from Checks to run — then this moves to Done.

## Goal

Fix the visual regression on `InitialBooking.vue` introduced by commit `2d1c1a8`, which replaced
the one-line `SbSelectModal` subject field with the inline `SubjectTaxonomyPicker`. That component
was built for full-width setup screens; inside the 600px booking card it consumes ~370px for a
single-select field, breaks the form rhythm (every sibling field is a ~42px trigger), and pushes
the Find Tutor button below the fold.

## Approach

Put the taxonomy browsing UI behind a compact trigger, in a dedicated modal — approved design in
the linked mockup (two-pane variant, StudyBuddy tokens).

- New component `src/components/SubjectPickerModal.vue`: a 42px trigger button (matching the
  Date/Time trigger pattern) that opens a centered modal.
- Modal layout: search input on top; below it a two-pane browser — category sidebar (existing
  category accent colors as dots, counts) on the left, subjects for the active category on the
  right. Typing in search hides the panes and shows a flat result list with category meta and the
  "via keyword" badge (reusing the keyword-match logic from `SubjectTaxonomyPicker.vue`).
- Mobile (<640px): sidebar collapses to a horizontally scrollable pill row.
- Single-select for this use: choosing a subject closes the modal and shows the subject name plus
  a category tag in the trigger.
- `SubjectTaxonomyPicker.vue` stays untouched — the tutor setup and preference screens keep the
  full inline browsing experience where it belongs.
- `InitialBooking.vue` swaps `<SubjectTaxonomyPicker>` for `<SubjectPickerModal>`; the
  `selectedSubjectCodes` computed and store wiring stay as-is (component keeps the same
  `modelValue` array + `subjects` props contract so the swap is minimal).

Why a new component instead of a `compact` prop on the picker: the modal has different structure
(overlay, panes, close-on-select) rather than a restyled version of the same markup; a prop-driven
fork of the picker would tangle both layouts in one file.

## Steps

1. Build `SubjectPickerModal.vue` (trigger + modal, two-pane browse, search override, mobile pill
   collapse), reusing the search/keyword matching logic and category color mapping from
   `SubjectTaxonomyPicker.vue`. Extract that shared logic into
   `src/components/subjectPicker.shared.js` (or a small composable) if duplication is non-trivial.
2. Swap the component into `InitialBooking.vue`; remove the now-unneeded inline-picker spacing.
3. Check the other `SubjectTaxonomyPicker` call sites (`FindTutors.vue`, `PreferenceSetup.vue`,
   `AdminCourseCatalog.vue`, tutor setup views) still render correctly — no changes expected.
4. Run checks; verify InitialBooking visually via the dev server.

## Risks

- FindTutors.vue also renders the picker inside a constrained column — if it suffers the same
  crowding, that is a follow-up swap, deliberately out of scope here. (Resolved 2026-07-20: the
  crowding was confirmed and the same swap applied after a ui-preview comparison against
  filter-bar-native alternatives — see
  [FindTutors mockup](../mockups/2026-07-20-findtutors-subject-modal.html).)
- Modal focus/keyboard handling: follow the existing pattern in `SbSelectModal.vue` /
  `CampusLocationModal.vue` rather than inventing new behavior.
- Category label truncation in the 148px sidebar for long names ("Business, Finance & Economics")
  — mockup uses shortened labels; confirm shortening map or ellipsis at build time.

## Checks to run

- `npm run lint` — passes with no new warnings.
- `npm run build` — production build succeeds.
- `npm run dev` — manual pass on /initial-booking: field is one line, modal opens, browse + search
  + select + clear work, mobile viewport collapses sidebar to pills.

## Changelog

- 2026-07-20 — Plan created with status Approved after ui-preview design session; diagnosis of
  the `2d1c1a8` regression, chosen two-pane modal design, steps, risks, and checks recorded.
- 2026-07-20 — Implemented (`21774b6`). Deviations from plan: shared logic landed as pure
  functions at `src/components/subjectPicker.shared.js` (plan's suggested name) rather than a
  composable; `SubjectTaxonomyPicker.vue` was minimally refactored onto the shared module
  (sanctioned by Step 1's extraction clause — props contract unchanged, other call sites
  verified). Code review (Standards + Spec axes) findings fixed: category-class map
  centralized, `isMatch` no longer leaked, arrow-key navigation added, sidebar labels
  ellipsized, re-click no longer clears the selection. Status Approved -> In Progress pending
  the manual dev-server pass.
- 2026-07-20 — Scope extended to FindTutors.vue: the risk section's flagged follow-up was
  confirmed live (inline picker inflating the col-lg-4 filter column). A ui-preview session
  compared reusing the modal vs an anchored popover vs a search-only combobox; the modal was
  chosen for consistency. Same two-line swap applied; mockup promoted to
  `../mockups/2026-07-20-findtutors-subject-modal.html`; lint/build/77-test suite green.
