---
title: Subject picker description highlight + proposal notes label
date: 2026-08-13
status: In Progress
summary: Replace the "via 'query'" badge on SubjectTaxonomyPicker's search results with a bold in-text highlight of the matched term inside the description, and rename the proposal form's Description label to "Proposal Notes (optional):".
---

# Subject picker description highlight + proposal notes label

**Status & Progress Summary** (2026-08-13): Implemented and build-verified (`npm run build`, `npm
run lint` clean aside from pre-existing unrelated errors; `subjectPicker.shared.test.js` still
passes 13/13, untouched by this change). Manual visual verification (search "shapes" → bold
"Shapes" in Geometry's description, no badge anywhere) outstanding.

## Goal

On the tutor onboarding "Add your subjects" search step (`TutorSubjectSetup.vue` →
`SubjectTaxonomyPicker.vue`), replace the `via "shapes"` pill badge on matching subject cards with
an in-text bold highlight of the matched term inside the subject's description. Separately, rename
the "propose a new subject" form's "Description (optional)" label to
"Proposal Notes (optional):".

## Approach

**Scope: `SubjectTaxonomyPicker.vue` only.** The same "via ..." badge pattern also exists in
`SubjectPickerModal.vue` (used in booking/tutee subject-selection flows), sharing
`subjectPicker.shared.js`'s `searchSubjects()` and its `matchedViaHint` flag. That component is
untouched — its badge stays as-is. `matchedViaHint` itself is left in place (still needed by
`SubjectPickerModal.vue`); `SubjectTaxonomyPicker.vue` simply stops rendering it.

**Highlight only covers what's visibly true.** `matchedViaHint` is `true` whenever a subject
matched via keywords *or* description, without saying which — a subject can match purely because a
keyword contains the term, with the term never appearing in the description text shown on the
card. In that case there is nothing to bold, and per the interview that's fine: the card just shows
normally, no fallback badge. This falls out naturally from splitting the description into
match/non-match segments — if the description doesn't contain the query, the "match" segment is
just empty and the whole text renders as plain, unstyled text.

**Rendering approach: segment the description, not `v-html`.** Description text comes from admin-
authored catalog data (low risk either way), but building the highlighted text as an array of
`{ text, match }` segments and rendering each as a plain text node or a `<strong>` avoids any
injection surface entirely, so there's no reason to reach for `v-html`. A local helper function in
`SubjectTaxonomyPicker.vue`'s `<script setup>` does the case-insensitive split; matching is
case-insensitive but preserves the original casing of the matched substring as it appears in the
description.

**Style: bold only**, no color or background change — keeps the description's existing muted
gray text, just heavier weight on the matched span. No new CSS variable/accent needed.

**Label change is purely cosmetic** — `proposal.description` already flows straight through to the
tutor's proposal note field on submit; only the visible `<label>` text changes.

## Steps

1. `src/components/SubjectTaxonomyPicker.vue`:
   - Add a local `highlightSegments(text, query)` helper: case-insensitive split of `text` on the
     first occurrence(s) of `query`, returning `[{ text, match: boolean }, ...]`; returns
     `[{ text, match: false }]` unchanged when `query` is empty or not found.
   - In the result row, replace the description `<span class="desc">{{ subject.description }}</span>`
     with a loop over `highlightSegments(subject.description, searchQuery)`, rendering each segment
     as `<strong>` when `match` is true, plain text otherwise.
   - Remove the `<span v-else-if="subject.matchedViaHint" class="via-badge">` block entirely.
   - Remove the now-unused `.result-row .via-badge` CSS rule.
2. `src/views/TutorSubjectSetup.vue`: change the `<label for="proposal-description">` text from
   "Description (optional)" to "Proposal Notes (optional):".
3. Manually verify: search "shapes" → Geometry's description shows "**Shapes**, angles, area..."
   in bold, no badge anywhere on the row; search something that only hits a keyword (not the
   description text) → card appears with no badge and no bold anywhere in its description.

## Risks

- None expected to be structural — this is a display-only change to one component's result-row
  rendering and one label string. `matchedViaHint` remains computed but unused in this component,
  which is intentional (kept for `SubjectPickerModal.vue`), not dead-code drift to worry about.

## Checks to run

- `npm run lint`
- `npm run build`
- Manual verification per step 3 above.

## Changelog

- 2026-08-13: Plan created and approved via `/grill-with-docs` interview.
- 2026-08-13: Implemented all 3 steps. `npm run build`/`lint` clean; `subjectPicker.shared.test.js`
  still 13/13 (untouched — the change is scoped to `SubjectTaxonomyPicker.vue`'s own render logic).
