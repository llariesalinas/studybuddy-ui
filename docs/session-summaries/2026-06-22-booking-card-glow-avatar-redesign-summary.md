---
title: Booking card glow-avatar redesign
date: 2026-06-22
plan: ../plans/2026-06-22-booking-card-glow-avatar-redesign.md
spec: ../specs/2026-06-22-booking-card-glow-avatar-redesign-design.md
---

# Booking card glow-avatar redesign — summary

The shared inline chat booking card now uses the approved Option C treatment for every booking
status while preserving its existing data and interactions.

## What changed

- Restructured the render-function markup around normalized `booking-card-*` class names.
- Added status-tinted borders and soft shadows for warning, primary, info, danger, and neutral
  cards using existing StudyBuddy tokens.
- Replaced the circular icon container with a 40px rounded-square gradient avatar. The existing
  status icon map remains unchanged; no profile photos are introduced.
- Added a rounded metadata panel around the existing date, time, duration, and optional location.
- Added a trailing arrow to the right-aligned “View session details” link.
- Updated the existing 900px and 700px responsive selectors for the renamed grid, header, and
  pill elements.

## Unchanged behavior

The booking props, status/accent maps, status/icon maps, emitted `location-saved` event, pending
F2F location editor, and tutor/tutee details targets are unchanged.

## Verification

- Targeted ESLint passed for `src/views/Chat.vue`.
- Production build passed with 284 modules transformed.
- Full lint reached ESLint but remains blocked by two pre-existing unused helpers in
  `src/views/Dashboard.vue` (`getTutorRatingLabel` and `getTutorPrimarySubject`).
- Old selector names were fully removed.
- The approved three-option reference remains open in the in-app browser. Live `/chat` visual QA
  requires an authenticated session containing a booking event; the current preview session was
  redirected to `/login`.

## Post-ship audit (2026-06-22)

The initial implementation matched the written spec's markup/class structure but had drifted from
the actual picked mockup (Option C) on three visual details: a single flat shadow instead of the
mockup's two-layer colored-glow + ambient shadow, an all-caps "eyebrow"-style pill instead of the
mockup's softer mixed-case pill, and centered instead of top-aligned header content. Fixed by
layering the box-shadow per accent, bumping card padding 14px → 16px, restyling `.booking-card-pill`
to drop uppercase/letter-spacing and match the mockup's size/weight/padding, and switching
`.booking-card-head` to `align-items: flex-start`. Verified by rendering the exact compiled CSS in
an isolated static page and screenshotting it next to the original mockup — confirmed the glow,
pill, and alignment now match. `npx eslint src/views/Chat.vue` and `npm run build` both pass.
