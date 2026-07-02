---
title: System background unification
date: 2026-06-22
plan: ../plans/2026-06-22-system-background-unification.md
spec: ../specs/2026-06-22-system-background-unification-design.md
---

# System background unification — summary

The seamless landing-style background now covers every non-landing route in light and dark mode.
The fixed 680px aurora overlay and its visible horizontal boundary have been removed.

## What changed

- Added `src/components/SbBgWash.vue`, a static full-viewport background with three brand-palette
  blobs and no pointer interaction or animation.
- Added `--sb-wash-blob-1`, `--sb-wash-blob-2`, and `--sb-wash-blob-3` to the light and dark theme
  tokens in `src/assets/main.css`.
- Replaced the body's diagonal gradient with a solid paint-before fallback and deleted the legacy
  `#app::before` aurora, fade animation, and now-unused gradient tokens.
- Rendered `SbBgWash` once in `App.vue` for every route except `home`, and made the authenticated
  app main surface transparent.
- Updated `LandingPage.vue` to use the shared blob variables while preserving its existing sway
  animations.

## Verification

- `npm run build` passed (284 modules transformed).
- `npm run lint`: Oxlint passed; ESLint still reports two unrelated pre-existing unused helpers in
  `src/views/Dashboard.vue` at lines 639 and 641.
- Browser checks confirmed a single fixed wash on `/login`, full viewport coverage, transparent
  auth content, no legacy pseudo-element, correct light/dark computed gradients, and clean
  background handoff when navigating `/login` → `/` → `/login`.

Authenticated-route visual verification was not performed because the browser session had no
login credentials. The shared app boundary was verified structurally: `.app-main-surface` is
transparent and the production build includes `SbBgWash` at the `App.vue` root.
