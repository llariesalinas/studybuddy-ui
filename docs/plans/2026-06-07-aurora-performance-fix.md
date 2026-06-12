---
title: Aurora performance fix — make gradient static
date: 2026-06-07
status: Done
spec:
---

# Aurora performance fix — make gradient static

## Status & Progress Summary

**Status:** Done — both file changes implemented, build passes, dev server verified.

---

## Goal

The tutee dashboard felt sluggish (~30fps) whenever the mouse moved. Fix it without changing the visual design — keep the aurora gradient background, the glassmorphism cards, and the dark/light mode toggle exactly as they are.

## Approach

Root cause was a GPU paint storm triggered by the interaction between:

1. A `pointermove`-driven aurora parallax (`App.vue`) that updated 6 CSS custom properties on `:root` at up to 60fps via `requestAnimationFrame`.
2. `backdrop-filter: blur(24px)` on 6 `.glass-panel` elements on the dashboard (4 metric cards + weekly panel + recommendation panel).

`backdrop-filter` cannot cache its result when the background behind it changes — it must resample and re-blur on every frame. With the aurora moving at 60fps, that's 360 blur operations/second; the GPU drops to ~30fps to compensate.

Fix: stop the aurora from responding to mouse movement. A backdrop-filter on a **static** background is computed once and cached at zero ongoing cost. The aurora colors, gradients, and overall look are unchanged.

## Steps

1. **`src/App.vue`** — Replace the `setupAuroraPointerMotion` function body with a no-op. Remove all pointer-motion helpers: `setAuroraMovement`, `scheduleAuroraMovement`, `handleAuroraPointerMove`, `resetAuroraMovement`, and the module-level variables `auroraFrameId`, `auroraPointerTarget`, `auroraMotionEnabled`. Keep `teardownAuroraPointerMotion` as an empty stub (its call site in `onUnmounted` stays).

2. **`src/assets/main.css`** — For each of the three aurora pseudo-elements (`body::before`, `body::after`, `body > #app::before`):
   - Remove the `transform` transition line (the `420ms`/`620ms`/`520ms` spring lines).
   - Remove `will-change: transform`.
   - Replace `translate3d(var(--sb-aurora-*-x), var(--sb-aurora-*-y), 0) scale(...)` transforms with a plain static `scale(...)` (or no transform for `body::after`).
   - Keep `transition: background 320ms ease` — still needed for dark/light mode switching.

## Risks

- **Visual regression:** the aurora no longer reacts to the mouse. The gradient becomes a fixed decorative background. This is intentional and the expected trade-off.
- **`transform-origin: 50% 10%` on `body::before`** now only applies to `scale(1.035)`, pulling the scale anchor slightly upward. Verify the visual result; remove if unintended.
- **`@media (prefers-reduced-motion)` override** for the aurora pseudo-elements is now a no-op (the normal rules already match). Dead code — safe to remove in a future cleanup.
- **Orphaned CSS vars:** `--sb-aurora-base-x/y`, `--sb-aurora-overlay-x/y`, `--sb-aurora-sheen-x/y` are still declared in the `:root` block but are no longer used. Harmless; remove in a follow-up.

## Checks to run

- `npm run build` — should pass with no errors.
- Open the tutee dashboard, move the mouse vigorously — should feel smooth with no jank.
- Chrome DevTools → Performance tab → record while moving mouse → no large "Composite Layers" blocks per frame.
- Toggle dark/light mode — background should still transition smoothly (the `background 320ms ease` is kept).
- Confirm glass-panel cards look correct in both modes.

## Changelog

- **2026-06-07** — Plan created and implemented in the same session. Root cause identified (pointermove aurora parallax + backdrop-filter paint storm). Fix applied to `src/App.vue` and `src/assets/main.css`. `npm run build` passes. Summary at [`docs/session-summaries/2026-06-07-aurora-performance-fix-summary.md`](../session-summaries/2026-06-07-aurora-performance-fix-summary.md).
