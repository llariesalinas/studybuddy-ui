# SbSelectModal rollout completion

**Date:** 2026-06-03
**Plan:** `docs/plans/2026-06-03-replace-selects-with-sbselectmodal.md`
**Status:** Completed

## Summary

Implemented a reusable, dark-mode-aware `SbSelectModal` and replaced native selects in the planned
booking, onboarding, setup, schedule, registration, and tutor wallet flows. Admin filter selects
remain intentionally out of scope.

## Changes

- Added `src/components/SbSelectModal.vue` with flat and grouped options, search, clear behavior,
  Teleport modal rendering, Escape/backdrop close, body scroll locking, focus restoration, and ARIA
  dialog/listbox semantics.
- Added `src/composables/useSubjectCatalog.js` and refactored `TuteeProfile.vue` to reuse the
  subject catalog logic for level scoping, grouping, recommendations, search, pruning, and selected
  subject ordering.
- Replaced native selects in `InitialBooking.vue`, `FindTutors.vue`, `Register.vue`,
  `TutorSchedule.vue`, `TutorPreferenceSetup.vue`, `PreferenceSetup.vue`, and `TutorWallet.vue`.
- Preserved key values and side effects: subject codes, mode strings, institution ids as strings,
  `Tutee`/`Tutor` role casing, `Mon` through `Sun` day codes, teaching-level values, course-change
  subject clearing, and wallet required-field checks.
- Updated `FindTutors.vue` so empty subject and mode values remain valid broad filters.

## Verification

- `npm run build` passed.
- Direct non-mutating `npx oxlint` passed for all changed files.
- Direct non-mutating `npx eslint` passed for all changed files.
- Full `npm run lint` is blocked by pre-existing unused-expression errors in `src/views/TutorProfile.vue`
  at `openAccordionPanel` and `closeAccordionPanel`, unrelated to this rollout.

## Notes

- General subject support uses `is_general` or `applies_to_all` when present, with a frontend
  department/category allow-list fallback.
- Admin views still contain native filter selects by design for this pass.
