# Tutor schedule AM/PM period rail

## Summary

Implemented the selected Design 3 treatment for tutor availability slots. Each slot now shows a
left-side period rail (`AM` or `PM`), a 12-hour time range, and a compact descriptor so times are no
longer ambiguous. Slots that cross noon show both endpoint periods directly in the range, for
example `11:30 AM - 12:00 PM`, instead of using a combined `AM/PM` rail.

## Changed

- Updated `TutorSchedule.vue` slot markup to use the period rail layout.
- Added display-only helpers for slot period labels, 12-hour ranges, and descriptors.
- Removed the combined `AM/PM` rail state for noon-crossing slots.
- Adjusted selected and blocked slot styling so the new rail treatment keeps existing interaction
  states clear.
- Kept stored availability times in 24-hour format; this change only affects presentation.

## Verification

- `npm run build`
- `npx eslint src/views/TutorSchedule.vue`

## Notes

- Browser navigation to `/tch-availability` redirected to `/login`, so live tutor data could not be
  inspected without an authenticated session.
