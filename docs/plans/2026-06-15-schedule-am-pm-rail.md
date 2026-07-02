---
title: Tutor schedule AM/PM period rail
date: 2026-06-15
status: Done
spec: ../artifacts/2026-06-15-schedule-am-pm-preview.html
---

# Tutor schedule AM/PM period rail

## Goal

Make weekly availability slots clearly show whether they are AM or PM so tutors do not have to
interpret ambiguous 24-hour entries such as `01:30 - 02:00`.

## Approach

Use the selected Design 3 treatment from the preview: each slot keeps the existing pill shape but
adds a compact left rail with `AM` or `PM`, plus a 12-hour time range and a short period descriptor.
For slots that cross noon, show each endpoint period in the range itself, such as
`11:30 AM - 12:00 PM`. Keep existing selected and blocked states working.

## Steps

1. Add schedule helpers for display range, period rail label, and period descriptor.
2. Update the slot pill template to use the period rail layout.
3. Adjust scoped CSS for normal, selected, and blocked states.
4. Run the frontend build and visually verify the schedule view.

## Risks

- Longer noon-crossing ranges need to fit inside narrow day columns.
- Selected and blocked states must remain visibly distinct after the slot layout changes.
- Existing 24-hour storage should remain unchanged; this is a display-only update.

## Checks to run

- `npm run build` should complete successfully.
- Browser verification should confirm the schedule page renders without clipped slot text.

## Outcome

Implemented in `src/views/TutorSchedule.vue` and verified with `npm run build` plus targeted ESLint.
Updated the noon-crossing display to avoid a combined `AM/PM` rail. Live route verification
redirected to login without an authenticated session.
