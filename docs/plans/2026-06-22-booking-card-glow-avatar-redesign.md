---
title: Booking card glow-avatar redesign
date: 2026-06-22
status: Done
spec: ../specs/2026-06-22-booking-card-glow-avatar-redesign-design.md
---

# Booking card glow-avatar redesign

## Status & Progress Summary

Done. Initial implementation shipped, then audited against the picked Option C mockup and
corrected — shadow, pill styling, and header alignment now match the mockup (see Changelog).

## Goal

Give the shared chat booking card stronger hierarchy and StudyBuddy-specific polish without
changing booking data, status behavior, location editing, or navigation.

## Approach

Apply the approved Option C treatment inside `Chat.vue`'s existing render-function component:
status-tinted card depth, a rounded-square gradient icon avatar, a compact tinted metadata panel,
and a clearer session-details affordance. Keep the existing status accent and icon maps as the
single behavior source for every booking status.

## Steps

1. Restructure the render tree into `booking-card-head`, `booking-card-avatar`,
   `booking-card-pill`, and `booking-card-grid` elements.
2. Add per-accent border and shadow tints using existing StudyBuddy color tokens.
3. Replace the circular avatar fill with a 40px rounded-square accent gradient.
4. Turn the metadata grid into a padded, rounded panel without changing its content or order.
5. Right-align the details link and add a decorative trailing arrow.
6. Rename responsive selectors in lockstep and confirm no old booking-card class names remain.

## Risks

- Render-function nesting or stale CSS selectors could leave elements unstyled.
- Long status labels and narrow chat widths could force awkward wrapping.
- Status tints need sufficient contrast in both light and dark themes.

## Checks run

- `npx eslint src/views/Chat.vue` — passed.
- `npm run build` — passed; 284 modules transformed.
- `npm run lint` — Oxlint passed; ESLint remains blocked by two unrelated pre-existing unused
  helpers in `src/views/Dashboard.vue` at lines 639 and 641.
- Selector audit — no `booking-avatar`, `booking-pill`, `booking-grid`, or
  `booking-card-header` references remain.
- Browser route check — `/chat` correctly redirected the unauthenticated preview session to
  `/login`; an authenticated inline booking event was therefore unavailable for live QA.

## Changelog

- 2026-06-22: Implemented the approved glow-avatar design and marked the plan Done.
- 2026-06-22: Audit found the shipped CSS had diverged from the picked Option C
  mockup in three ways: a single flat shadow instead of the mockup's two-layer
  colored-glow + ambient shadow, a smaller all-caps "eyebrow"-style pill
  instead of the mockup's softer mixed-case pill, and `align-items: center`
  on the header instead of `flex-start`. Fixed `.booking-card.booking-card--*`
  shadows to layer a colored glow with a neutral ambient shadow, bumped card
  padding 14px → 16px, restyled `.booking-card-pill` to drop uppercase/
  letter-spacing and match the mockup's size/weight, and switched
  `.booking-card-head` to `align-items: flex-start`. Verified by rendering the
  exact compiled CSS in an isolated static page and screenshotting it
  alongside the original mockup. `npx eslint` and `npm run build` both pass.
