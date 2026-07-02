---
title: System background unification
date: 2026-06-22
status: Done
spec: ../specs/2026-06-22-system-background-unification-design.md
---

# System background unification

## Goal

Replace the legacy two-layer system background with the landing page's seamless wash on every
non-landing route, eliminating the 680px horizontal seam while keeping light and dark themes in
the same StudyBuddy palette.

## Approach

Render a static `SbBgWash` once in `App.vue` for all routes except `home`. Keep blob gradients as
shared CSS variables so the static system wash and animated landing wash use one palette, and let
auth and authenticated content surfaces remain transparent above it.

## Steps

1. Add `src/components/SbBgWash.vue` as a fixed, pointer-inert, full-viewport wash.
2. Centralize the three landing blob gradient stacks in `src/assets/main.css` for light and dark
   themes.
3. Remove the obsolete diagonal background token, 680px `#app::before` aurora, and one-shot fade.
4. Render the shared wash outside the landing route and make `.app-main-surface` transparent.
5. Update `LandingPage.vue` to consume the centralized blob gradients while retaining its motion.
6. Verify the build, lint, both themes, and navigation between `/login` and `/`.

## Risks

- An opaque app-shell ancestor could hide the fixed wash.
- A negative stacking layer could fall behind the app if `#app` did not establish its intended
  stacking context.
- Rendering the shared wash on `home` would double the landing background.

## Checks run

- `npm run build` — passed.
- `npm run lint` — Oxlint passed; ESLint is blocked by two pre-existing unused helpers in
  `src/views/Dashboard.vue` (`getTutorRatingLabel` and `getTutorPrimarySubject`).
- Browser verification — `/login` passed in light and dark mode; the wash fills the viewport,
  auth content is transparent, and the removed `#app::before` has no generated content.
- Route verification — `/login` → `/` removes the shared wash and keeps the landing animation;
  `/` → `/login` restores exactly one shared wash without leaving `sb-landing-route` on `body`.

## Changelog

- 2026-06-22: Implemented and verified; status set to Done.
