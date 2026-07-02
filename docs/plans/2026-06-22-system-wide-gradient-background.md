---
title: Superseded system-wide gradient background approach
date: 2026-06-22
status: Done
outcome: Superseded
spec: ../specs/2026-06-22-system-background-unification-design.md
---

# Superseded system-wide gradient background approach

## Status & Progress Summary

This gradient-only approach was replaced before final delivery by the reusable landing-style
wash in the [system background unification plan](2026-06-22-system-background-unification.md).
The details below are retained as a record of the earlier diagnosis, not the shipped design.

## Goal

Replace the flat, plain-white/black page backgrounds on authenticated views with the same
`--sb-bg-gradient` already used on public auth pages, and fix the hard square-edge artifact on
short pages (e.g. Login) — without introducing scroll-repaint performance regressions.

## Approach

Two root causes, two single-point fixes (not per-view edits):

1. **Square-edge bug:** `html, body { min-height: 100%; }` in `src/assets/main.css` collapses to
   content height (not viewport height) when page content is shorter than the viewport, because
   percentage `min-height` resolves against `html`'s computed height rather than the viewport.
   `body`'s gradient background then only paints within that shrunk box, leaving the browser's
   default canvas color visible below it. Fix: use `min-height: 100vh` instead of `100%`.
2. **Plain white authenticated views:** every authenticated route renders inside
   `<main class="app-main app-main-surface">` (`src/App.vue`), which paints a flat `var(--sb-bg)`
   color over the whole shell. Changing this single class to `var(--sb-bg-gradient)` propagates
   the gradient to every authenticated view with one edit, instead of touching 50+ view files.

Per-view usages of `var(--sb-bg)` (skeleton loaders, filter panels in `Dashboard.vue`,
`FindTutors.vue`, `Chat.vue`, etc.) are intentional flat tints sitting on cards/panels, not page
backgrounds — left untouched to avoid visual regressions.

**Performance:** drop `background-attachment: fixed` everywhere it's used for this gradient.
`.app-main` is `overflow-auto` and scrolls constantly on long views (AdminUsers, TuteeSessions);
`fixed` attachment forces the browser to repaint the background on every scroll frame since it's
anchored to the viewport rather than the scrolling box. Default (`scroll`) attachment ties the
background to the element's own box, so it paints once and doesn't repaint during internal
scrolling.

## Steps

1. `src/assets/main.css`: change `html, body { min-height: 100%; }` to `min-height: 100vh;`.
2. `src/assets/main.css`: remove `background-attachment: fixed;` from the `body` background rule.
3. `src/App.vue`: change `.app-main-surface { background: var(--sb-bg); }` to
   `background: var(--sb-bg-gradient);` (no `fixed` attachment).
4. Leave all per-view `var(--sb-bg)` usages (skeletons, filter panels) unchanged.

## Risks

- Removing `background-attachment: fixed` from `body` could theoretically reveal a seam if a
  public page scrolls past 100vh — mitigated by the `min-height: 100vh` fix, since the gradient
  is sized to the box itself (`linear-gradient`, no tiling) and will stretch to cover any box
  height without banding.
- `.app-main`'s gradient must still read correctly against the sidebar and card surfaces in both
  light and dark themes — verify visually, not just by diffing CSS.

## Checks to run

- `npm run build` — confirm no build errors.
- Manual visual check, light + dark theme:
  - Login page (short content) — no square edge, gradient fills full viewport.
  - A long-scrolling authenticated view (e.g. AdminUsers) — gradient visible behind content, no
    seam at the sidebar boundary, smooth scroll with no visible repaint/flicker.

## Changelog

- 2026-06-22: Plan created and approved.
- 2026-06-22: Implemented all 3 edits, build passed, visual check confirmed fix; status set to
  Done.
