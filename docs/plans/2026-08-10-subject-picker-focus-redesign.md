---
title: Subject picker focus redesign
date: 2026-08-10
status: Done
summary: Rework SubjectTaxonomyPicker so browsing focuses one category behind a real back pill, and searching keeps descriptive rows instead of destroying the browse view.
spec: ../mockups/2026-08-10-subject-picker-focus-redesign.html
---

# Subject picker focus redesign

**Status & Progress Summary** (2026-08-10): Done. Design locked after a grilling + `ui-preview`
session across four mockup rounds; the user rejected a persistent category grid and a persistent
category rail as "too crowded" in favour of focus-one-category browsing, chose the bordered back pill
over a text link, and asked to preserve today's descriptive search rows. All six steps implemented in
`src/components/SubjectTaxonomyPicker.vue` (rewritten into four explicit view states);
`subjectPicker.shared.js` untouched, so `SubjectPickerModal.vue` is unaffected and now visually
diverges pending a follow-up. `npx eslint` clean, `npm run test` 136/136, `npm run build` succeeds.
[Summary](../session-summaries/2026-08-10-subject-picker-focus-redesign-summary.md).

## Goal

`SubjectTaxonomyPicker.vue` (onboarding step 3 for tutees, subject setup for tutors) has two
defects reported from the live screen:

1. **Conflicting visual language.** The drill-down pane paints a per-category accent (violet for
   Technology) while its back control and selection state use brand green, and every one of the 17
   chips repeats the category's coloured dot. Three colour systems compete inside one pane.
2. **No back control that reads as one.** The back affordance exists (`SubjectTaxonomyPicker.vue:59`)
   but is a bare green text button labelled "All categories" sitting where a heading would go, so it
   reads as a section title.

A third defect surfaced during the design session: typing a single character **destroys** the browse
view. `v-if="searchQuery"` at line 14 wraps a `<template v-else>`, so search does not overlay the
category view — it replaces it outright, category grid and all.

## Approach

Locked in after a grilling + `ui-preview` session (4 rounds of mockups). The final design is saved at
[`docs/mockups/2026-08-10-subject-picker-focus-redesign.html`](../mockups/2026-08-10-subject-picker-focus-redesign.html).

**Colour rule (resolves defect 1).** Category colour marks *category identity only* and appears
exactly once per context — the dot beside the category heading, and the left rule on a category card.
Brand green marks *state and controls only* — selection, links, buttons. The per-chip category dots
are deleted; the pane heading already declares the category, so 17 repetitions were pure noise.

**Focus browsing (resolves defect 2).** Opening a category still replaces the grid — the user
explicitly chose focus over a persistent grid or rail. The back control becomes a bordered pill,
`<- All categories`, on its own line above a divider, with the category name as a proper heading
below it. A bordered pill was chosen over a text link precisely because the bare-text version is what
failed.

**Chips for browsing, rows for searching (resolves defect 3).** Browsing a category shows compact
chips — the user is scanning names they half-recognise. Searching shows the existing descriptive rows
(name, category, description, `via "<query>"` keyword badge), which the user asked to preserve: the
description is what distinguishes Java from JavaScript. Search no longer discards context:

- **Searching from the top level** renders a "Jump to a category" band showing *only* categories
  containing matches with their match counts, then "Matching subjects" rows below. Cards are a
  shortcut, not a wall — select straight from a row, or click a card to enter that category already
  filtered. Clearing the query restores the full grid.
- **Searching inside a category** keeps the back pill and category heading in place and swaps only the
  chips for rows, scoped to that category. The row's category line is dropped (the heading says it).
  Matches in other categories get one quiet line: "N more matches in X — search all categories".

## Steps

1. Restructure `SubjectTaxonomyPicker.vue`'s template into four explicit states driven by
   `activeCategory` x `searchQuery`: grid, focused-category (chips), top-level search (cards + rows),
   focused search (rows). Extract the row markup so the two search states share it.
2. Add derived state to the `<script setup>`: matches grouped by category, per-category match counts,
   and an `outsideMatchCount` for the "N more matches" hint line. Reuse `searchSubjects` from
   `subjectPicker.shared.js` — no change to the shared module's contract.
3. Scope in-category search to the active category, with the hint line's link clearing
   `activeCategory` to widen to all categories.
4. Rewrite the scoped styles: delete `.dot`, `.breadcrumb`, `.drill-pane`'s left accent bar and the
   `.monogram`; add `.back-pill`, the category heading block, the "jump to a category" band, and the
   compact result rows. Keep every colour on an `--sb-*` custom property; keep the `.cat-*` classes
   since they still drive the identity dot and card rule.
5. Verify both consumers still work: `PreferenceSetup.vue:183` (no cap, no propose) and
   `TutorSubjectSetup.vue:32` (`max-selection`, `allow-propose`). The propose CTA must survive in the
   no-results state, and the selection tray must keep respecting `maxSelection`.
6. Run the checks below, then write the session summary.

## Risks

- **Two consumers, one component.** Tutor setup passes `max-selection` and `allow-propose`; the
  redesign must not drop the propose CTA (only reachable today from the empty search state) or the
  `Selected n/max` counter in the tray.
- **`SubjectPickerModal.vue` shares the `.cat-*` convention** (line 537) and the shared helpers, but is
  a separate component with its own styles. It is deliberately out of scope — the two will diverge
  visually until a follow-up aligns them. Worth flagging rather than silently widening the change.
- **Existing tests may assert on removed markup.** The `.dot`, `.breadcrumb`, and the "All categories"
  text button are all disappearing; any test selecting them needs updating.
- **Empty states multiply.** Four view states means four ways to have nothing to show (no categories,
  category with no subjects, no search hits in category, no search hits anywhere). The
  no-hits-anywhere case is the one that must keep the propose CTA.

## Checks to run

- `npm run lint` — oxlint + ESLint clean.
- `npm run test` — Vitest suite green, in particular any subject-picker specs.
- `npm run build` — production build succeeds.
- Manual: walk both consumers through all four states, confirm the back pill returns to the grid,
  confirm clearing the search restores the prior context rather than resetting to the grid, and
  confirm selection survives every state transition.

## Changelog

- **2026-08-10** — Plan created at status Approved. Design settled through four `ui-preview` rounds:
  (1) three architectures (floating results / filter-in-place / persistent rail), (2) the user's own
  "cards on top, panel below" idea in one-slot and two-section variants, (3) a stripped-back
  focus-one-category design after the user called the stacked layouts too crowded, (4) the combined
  final adding narrowed category cards above the preserved descriptive search rows. Decisions locked:
  bordered back pill; category colour once per context; per-chip dots deleted; chips for browsing,
  rows for searching; in-category search scoped to that category with a hint link to widen.
- **2026-08-10** — Implemented and moved to Done. `SubjectTaxonomyPicker.vue` rewritten into four
  view states with new derived state (`scopedResults`, `outsideMatchCount`, `matchedCategories`,
  `countLine`, `searchPlaceholder`). One judgement call beyond the plan: the propose CTA is suppressed
  in the in-category no-results state when matches exist elsewhere, so the "search all categories"
  hint is the single obvious next action. Checks: eslint clean, 136/136 tests, build succeeds. No
  existing test referenced the removed markup, so that risk did not materialise.
