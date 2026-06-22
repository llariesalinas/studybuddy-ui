---
title: System background unification (landing-style, seamless)
date: 2026-06-22
status: Approved
spec: this document
---

# System Background Unification

> **Visual reference (viewable HTML):**
> [`docs/artifacts/2026-06-22-system-background-preview.html`](../artifacts/2026-06-22-system-background-preview.html)
> — side-by-side current-vs-proposed comparison with a light/dark toggle. The proposed
> pane is the visual target this spec implements as `SbBgWash.vue`.

## Goal

Replace the system-wide background used on every non-landing screen (public auth pages
and the authenticated app shell) with the landing page's seamless background treatment,
so that:

1. The visible horizontal **seam bug** is eliminated.
2. The system background **reflects the colors of the landing page**.

The fix and the feature are the same change: the seam comes from the legacy overlay, and
the landing page already has the desired seamless, on-palette background.

## Background / Root cause

Two pieces produce today's system background, both in `src/assets/main.css`:

- `body { background: var(--sb-bg-gradient) }` — a `135deg` diagonal linear gradient
  (`main.css:117`).
- `body > #app::before` — the aurora radial gradients, but `position: absolute` with a
  fixed `height: 680px` (`main.css:135-146`).

Below 680px the aurora layer ends abruptly, producing a hard horizontal line. On short
pages with a tall viewport (e.g. the login screen) the seam is clearly visible — this is
the band seen at the bottom of the login screenshot.

The landing page (`src/views/LandingPage.vue`, `.bgwash`, line ~867) instead uses a
`position: fixed; inset: 0` full-viewport vertical wash
(`aurora-wash-start → sb-bg → aurora-wash-end`) plus three large soft radial "blobs" in
the brand palette (primary green, mid-green, pop-yellow, aurora-violet, pop-pink,
pop-orange). Because it is fixed and full-viewport, it never seams.

## Decisions (locked with user)

- **Scope:** Everywhere — public auth pages AND the authenticated app shell. The landing
  page keeps its own existing background.
- **Motion:** Static (no swaying animation) in the shared app background. The landing page
  keeps its existing animated blobs.
- **Implementation:** A reusable Vue component, rendered once in `App.vue`. The blob
  palette is centralized so the landing page and the app background cannot drift apart.

## Approach

### 1. New component `src/components/SbBgWash.vue`

A presentational, prop-light component that renders the seamless background:

- Root element: `position: fixed; inset: 0; z-index: -1; pointer-events: none;
  overflow: hidden`.
- Background: the vertical wash gradient
  `linear-gradient(180deg, var(--sb-aurora-wash-start) 0%, var(--sb-bg) 42%,
  var(--sb-aurora-wash-end) 100%)`.
- Three child blob elements using the centralized blob variables (see part 2). Static
  (no animation).
- No props required for the initial scope. (A future `animated` prop could be added if the
  landing page is later migrated onto this component, but that is out of scope here.)

Rationale for `position: fixed` despite the existing perf note (which warned against fixed
+ animated backgrounds): the wash is **static**, so the fixed layer is painted once and
never repaints on scroll. This matches the landing page, which already uses
`position: fixed` acceptably.

### 2. Centralize the blob palette in `src/assets/main.css`

Add three CSS variables holding the blob `radial-gradient` stacks, for both the light
`:root` and the dark theme block:

- `--sb-wash-blob-1` (green / mid-green / yellow cluster)
- `--sb-wash-blob-2` (violet / pink cluster)
- `--sb-wash-blob-3` (orange / green cluster)

These mirror the current `.bgwash .b1/.b2/.b3` definitions in `LandingPage.vue`. Both
`SbBgWash.vue` and `LandingPage.vue` then consume these variables instead of inlining the
gradients, guaranteeing the app background reflects the landing palette and the two stay in
sync.

### 3. Wire into `App.vue`

- Import `SbBgWash` and render it once at the top of the template:
  `<SbBgWash v-if="route.name !== 'home'" />`. The `home` route is the landing page, which
  keeps its own animated `.bgwash`; the guard prevents a double background there.
- Remove `background: var(--sb-bg-gradient)` from `.app-main-surface` (`App.vue:582`) so the
  fixed wash shows through the scrolling main area. Confirm the main scroll surface is
  transparent (content cards keep their own surfaces).

### 4. Clean up `src/assets/main.css`

- Delete the `body > #app::before` 680px aurora block (`main.css:135-146`) — the seam
  source.
- Delete the now-unused `body.sb-landing-route > #app::before` opt-out
  (`main.css:148-151`) and the `sb-aurora-fade-in` keyframe + reduced-motion rule
  (`main.css:153-167`), unless still referenced elsewhere.
- Replace `body { background: var(--sb-bg-gradient) }` with a solid fallback
  `background: var(--sb-bg)` (the fixed wash covers it; the solid color is the paint-before
  fallback and prevents a flash).
- Remove the `--sb-bg-gradient` variable if it is unused after these edits (grep to
  confirm). Keep it if any other consumer remains.

The `body.sb-landing-route` class toggling in `LandingPage.vue` (mount/unmount) can remain
or be removed depending on whether any remaining CSS still references it; remove only if it
becomes dead.

## Components / boundaries

- `SbBgWash.vue` — single responsibility: paint the seamless background. No inputs, no
  external dependencies beyond CSS variables. Testable by snapshot/visual.
- `main.css` — owns the palette variables (single source of truth for wash + blobs).
- `App.vue` — decides when the shared background renders (everywhere except landing).
- `LandingPage.vue` — keeps its own animated background, but now sources blob colors from
  the shared variables.

## Risks

- **Opaque ancestors occluding the fixed wash.** If any element between `#app` and the
  content paints an opaque background (e.g. `.app-main-surface`), the wash is hidden. Mitigation:
  make the main scroll surface transparent (part 3) and visually verify both layouts.
- **Stacking context.** `body > #app` is `position: relative; z-index: 1`. A fixed child
  with `z-index: -1` stays within `#app`'s stacking context, behind its content but above
  `body` — the same model the old `::before` used, so behavior is preserved.
- **Double background on landing.** Prevented by the `route.name !== 'home'` guard; verify
  no flash on navigating to/from the landing page.
- **Dark mode parity.** All variables already have dark-theme values; verify the wash reads
  correctly in dark mode (the HTML preview confirms the direction).

## Checks to run

- `npm run lint`
- `npm run build`
- Dev server: load `/login` (public) and one authenticated page in both light and dark
  mode; screenshot to confirm no seam at any scroll depth and that the palette matches the
  landing page. Compare the result against the proposed pane in
  `docs/artifacts/2026-06-22-system-background-preview.html`.
- Navigate to `/` (landing) and back; confirm no double background or flash.

## Reference

Interactive comparison preview (current vs proposed, light/dark):
`docs/artifacts/2026-06-22-system-background-preview.html`.
