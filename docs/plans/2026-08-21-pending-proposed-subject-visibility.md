---
title: Pending proposed subject visibility
date: 2026-08-21
status: Done
summary: Proposed subjects survive a reload in the tutor picker and now say they are awaiting review.
spec: ../mockups/2026-08-21-pending-proposed-subject-chips.html
---

# Pending proposed subject visibility

## Status & Progress Summary

**Done (2026-08-21).** Both defects fixed and covered by tests: the catalog merge keeps a proposed
subject visible across reloads, and the selection tray groups pending proposals under an
"Awaiting admin review" sub-row, mirrored inline on search-result rows.

## Goal

A tutor who proposes a subject missing from the catalog should keep seeing that subject in their
selection, and should be able to tell that it is not live yet. Neither held before this change: the
chip disappeared on reload, and while visible it was indistinguishable from an approved subject.

## Approach

Two separate defects, one screen.

**Disappearing chip.** `TutorSubjectSetup.vue` loads two lists: the catalog
(`GET /subjects/?catalog_scope=all`, approved subjects only) and the tutor's own subjects
(`GET /tutor/subjects/`, which includes their `status='pending'` proposals). `SubjectTaxonomyPicker`
renders its selection tray by filtering its `subjects` prop, so a selected subject absent from the
catalog rendered no chip while still counting towards the N/8 counter. `handleProposal` papered over
this by pushing the new subject into both arrays by hand, so it only surfaced after a reload.

Fixed in the view rather than the API: a `mergeIntoCatalog` helper keeps the picker's catalog a
superset of the selection. The backend alternative (honouring `include_current` inside the
`catalog_scope=all` branch) was rejected because that branch is shared with other callers, and
"the catalog is approved subjects" is worth keeping true server-side.

**No pending marker.** Chosen from three options shown in a ui-preview session; see the mockup
linked in `spec` above. Approved chips stay on the tray's first row, proposed ones drop to a
sub-row under an "Awaiting admin review" label, so one label covers any number of pending chips.
Search-result rows carry the same words inline beside the subject name, since a row has no sub-row
to belong to.
The amber accent is `--sb-pop-yellow-deep` (the only amber token defined in both themes, unlike
`--sb-warning-text`), and the label reuses the picker's existing `.section-label`.

## Steps

1. Add `mergeIntoCatalog` to `TutorSubjectSetup.vue`; call it from `loadSubjects` and
   `handleProposal`.
2. Split the picker's selection into `approvedSelection` / `pendingSelection` on
   `subject.status === 'pending'`.
3. Render the pending sub-row and its `.subject-chip.pending` styling.
4. Mirror the marker on search-result rows as an inline `.pending-flag`.
5. Prune a removed proposal from the merged catalog so it can't strand as a stale chip.
6. Cover all of it with tests in `src/views/TutorSubjectSetup.test.js`.

## Risks

- `SubjectTaxonomyPicker` is shared. The sub-row only appears when a selected subject carries
  `status: 'pending'`, so other callers are unaffected.
- The amber chip styling is scoped to `.subject-chip.selected.pending`, so an unselected chip can
  never borrow the selected chip's checkmark.
- `--sb-pop-yellow-deep` at 10% over the card background is a low-contrast fill; the chip's meaning
  rests on the row label, not on the colour alone.

## Checks to run

- `npx vitest run src/views/TutorSubjectSetup.test.js` - 5 passing.
- `npm run test` - no new failures beyond the pre-existing `BookingTimeRangePicker`,
  `assets/tokens`, and `useOrbitStripComposable` ones (the last is a midnight-boundary flake:
  it builds `now - 15min` against today's date key, so it fails when run just after 00:00).
- `npm run lint` - no new errors beyond the pre-existing `make_algo_pptx.*` `no-undef` ones.

## Changelog

- **2026-08-21** - Plan written after the fix and the ui-preview design session; records the
  catalog-merge fix, option C for the pending marker, and the checks run. Created at status Done.
- **2026-08-21** - Follow-up: mirrored the pending marker onto search-result rows, scoped the amber
  chip styling to selected chips, and pruned removed proposals from the merged catalog (a
  follow-on defect introduced by the merge itself). Tests now 5.
