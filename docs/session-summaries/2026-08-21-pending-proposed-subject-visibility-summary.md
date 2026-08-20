# Pending proposed subject visibility - session summary

**Date:** 2026-08-21
**Plan:** [docs/plans/2026-08-21-pending-proposed-subject-visibility.md](../plans/2026-08-21-pending-proposed-subject-visibility.md)
**Mockup:** [docs/mockups/2026-08-21-pending-proposed-subject-chips.html](../mockups/2026-08-21-pending-proposed-subject-chips.html)

## What shipped

Started as a debugging session ("adding a new proposed subject doesn't show up") and ended with two
fixes on the tutor subject-setup screen.

1. **Proposed subject vanished on reload.** `TutorSubjectSetup.vue` gained `mergeIntoCatalog`,
   which unions any selected subject missing from the catalog response into `allSubjects`. Called
   from `loadSubjects` and from `handleProposal` (replacing a bare `allSubjects.value.push`). Root
   cause: `GET /subjects/?catalog_scope=all` returns approved subjects only, while
   `GET /tutor/subjects/` returns the tutor's pending proposals too, and the picker renders its tray
   by filtering the catalog prop.
2. **No pending marker.** `SubjectTaxonomyPicker.vue` splits the tray into `approvedSelection` and
   `pendingSelection` and renders the pending ones under an "Awaiting admin review" sub-row with
   `.subject-chip.selected.pending` styling. The picker's search-result rows carry the same words
   inline as `.pending-flag`.
3. **Stale catalog entry after removal** (follow-on defect introduced by fix 1). `handleRemove` now
   prunes a removed *pending* subject from `allSubjects`; removing a proposal deletes the subject
   server-side, so leaving it in the merged catalog stranded it as an unselected chip. Approved
   subjects still stay in the catalog.

`PENDING_STATUS` / `isPendingSubject` were added to `subjectPicker.shared.js` so the view and the
picker share one definition instead of two `'pending'` literals.

## Deviations from plan

The plan was written after the work, not before: the first fix came out of a live debugging trace,
and the second was scoped only once the first was done. Nothing in the shipped code differs from
what the plan describes.

Design choice: three treatments were shown over ui-preview (inline badge / dashed amber chip /
grouped sub-row). The user picked the grouped sub-row (option C); the assistant had recommended the
inline badge (option A). The other two screens stayed in the gitignored session directory.

The marker was mirrored onto search-result rows in a follow-up pass, after the user approved it.

Implementation detail not in the original options: the amber accent uses `--sb-pop-yellow-deep`
rather than `--sb-warning-text`, because only the former is redefined for the dark theme -- the
mockup's literal `#946200` would have been dark-on-dark.

## Checks run

- `npx vitest run src/views/TutorSubjectSetup.test.js` - 5 passed (new file).
- `npx vitest run src/views/TutorSubjectSetup.test.js src/components/subjectPicker.shared.test.js` -
  16 passed.
- Mutation check 1: reverting `mergeIntoCatalog` made the load test fail with
  `expected 'Add your subjects2/8...' to contain 'Underwater Basket Weaving'` - the exact symptom
  reported. Restored after.
- Mutation check 2: reverting the `handleRemove` prune made the removal test fail
  (`expected [ DOMWrapper ] to have a length of +0 but got 1`). Restored after.
- `npm run test` (final, 00:40) - 2 files failing (`BookingTimeRangePicker.test.js`,
  `assets/tokens.test.js`), 224 passed. `useOrbitStripComposable.test.js` passed on this run,
  confirming the midnight-boundary diagnosis below.
- `npm run test` (earlier, 00:14) - 3 files failing (`BookingTimeRangePicker.test.js`, `assets/tokens.test.js`,
  `useOrbitStripComposable.test.js`); all independent of this change. Confirmed by stashing both
  edited source files and re-running `useOrbitStripComposable.test.js`, which failed identically
  (`expected null to be 'live'`). That one is a midnight-boundary flake - the test pairs
  `startTime: now - 15min` with `date: now`, so just after 00:00 the start time lands on the
  previous day and the session never reads as live. Worth fixing separately.
- `npm run lint` - 4 pre-existing `no-undef` errors in `make_algo_pptx.cjs` / `make_algo_pptx.js`.

## Not done

- The browse-mode chips (inside a focused category) show no pending marker beyond the amber styling
  they inherit when selected.
- Nothing committed or pushed.
