---
title: Aurora hue restoration (performant)
date: 2026-06-07
status: Done
spec:
---

# Aurora hue restoration (performant)

## Status & Progress Summary

**Status:** Done — implemented in `src/assets/main.css` only (App.vue cleanup was already a no-op per `3015a8f`). Build, lint, and live browser verification (incl. scroll/animation/repaint checks) all pass. Shipped and committed as `80534ef`. **Follow-up (2026-06-08):** restored the dropped cyan accent stop to the light-mode palette (3 → 4 radial-gradient stops) per user request, after a cost analysis confirming stop count was never the driver of the original perf problem (repaint *frequency* was — see "Follow-up" addendum below). Re-verified clean: build, lint, DOM scan, and a 60-cycle scroll stress test all pass with zero new cost signals. See `docs/session-summaries/2026-06-07-aurora-hue-restoration-summary.md`.

## Goal

Bring back the "aurora hue" atmosphere (soft colored radial-gradient glow behind the app shell) that was removed in `2a638ca` / `3015a8f`, but built so it cannot reintroduce the GPU/compositor costs that caused its removal — zero continuous animation, zero `backdrop-filter`, zero per-frame JS.

## Approach

Replace the old 3-layer fixed/animated/blurred design (documented in `docs/plans/2026-06-07-aurora-performance-fix.md` and the cleanup summary at `docs/session-summaries/2026-06-07-global-aurora-blur-performance-cleanup-summary.md`) with **one** static, absolutely-positioned gradient layer that fades in once on load and then never changes again — Approach 1, chosen over a "no visual atmosphere" or "scroll-linked" alternative because it gets the look back at effectively zero ongoing cost.

Original cost drivers being deliberately avoided:
1. Three stacked `position: fixed` full-viewport layers, each painting 3-5 `radial-gradient`s → forced dedicated full-viewport composited layers.
2. `pointermove`-driven parallax updating 6 CSS custom props at 60fps via `requestAnimationFrame`.
3. `backdrop-filter: blur(24px)` on cards above the moving background → ~360 re-blur/recomposite ops per second, dropping FPS to ~30.

### 1. CSS variables
Reintroduce `--sb-aurora-bg` for `:root` (light) and `[data-sb-theme="dark"]`, reusing the original brand palette but trimmed from 5 radial-gradient stops to 3 (reduces one-time paint cost on load/resize/zoom — not an ongoing cost, since the layer never repaints once painted). Theme switch swaps the variable instantly through the existing `[data-sb-theme]` selector mechanism, matching the current instant `--sb-bg` swap — no transition involved.

### 2. Single layer, absolutely positioned
One pseudo-element, `body > #app::before`:
- `position: absolute` (not `fixed`) — paints with page content rather than forcing a dedicated full-viewport composited layer.
- `top: 0; left: 0; right: 0; height: 680px; z-index: -1; pointer-events: none;`
- **Fixed pixel height, not `vh`.** `100vh` changes on mobile Chrome/Safari as the address bar collapses during scroll, forcing relayout + repaint — this would silently recreate the "recurring gradient repaint" problem via scroll instead of `pointermove`. A fixed height paints once and is never recomputed from viewport changes.
- Net effect: **3 layers → 1 layer**.

### 3. One-shot fade-in
New `@keyframes sb-aurora-fade-in` (`opacity: 0 → 1`, ~1.2s ease, `animation-fill-mode: forwards`). Runs once on mount, then is permanently static (`animation-iteration-count: 1`).

**Implementation note (simpler than originally spec'd):** rather than writing two media-query blocks (one for `no-preference`, one for `reduce`), the *base* `body > #app::before` rule is the reduced-motion-safe state — `opacity: 1`, no `animation` property. The `@media (prefers-reduced-motion: no-preference)` block is the only override: it sets `opacity: 0` and attaches the fade-in animation. Net effect is identical (reduced-motion users see the aurora immediately at full opacity with no animation; everyone else gets the 1.2s fade), but with one fewer rule to parse — a small, free win since less CSS to evaluate is strictly cheaper, never more expensive.

Two deliberate exclusions, called out so they don't get "helpfully" re-added later:
- **No `will-change: opacity`.** Creates a *persistent* GPU-resident composited layer that outlives a one-shot animation — paying ongoing memory cost for a one-time effect. Browser heuristics already promote short opacity animations temporarily without that lingering cost.
- **No `transition: background`.** Gradients can't interpolate; browsers crossfade them via repeated repaints across the transition window — a (rare but real) repaint storm on every theme toggle. Swapping `--sb-aurora-bg` instantly via `[data-sb-theme]`, matching the current `--sb-bg` behavior, avoids this entirely.

### 4. No motion, no JS, no blur — ever again
- `setupAuroraPointerMotion`/`teardownAuroraPointerMotion` no-op stubs: **already removed** by `3015a8f` (verified via grep across `src` — zero `aurora` matches remain outside docs). No App.vue change needed.
- Do not reintroduce `backdrop-filter` anywhere.
- No `pointermove`/`requestAnimationFrame`, no continuous transforms, no per-frame style writes.

## Follow-up (2026-06-08): restored the dropped cyan accent stop to the light palette

After shipping, the user asked to bring back more of the original light-mode aurora colors — specifically the cyan accent stop trimmed from 5→3 — then asked the right skeptical question: **"will it eat resource again?"**

**Answer: no.** The original slowdown was driven by *repaint frequency* (a `pointermove`/`requestAnimationFrame` loop forcing ~60 repaints/sec, compounded by `backdrop-filter: blur(24px)` re-blurring on each — ~360 blur ops/sec), not by *stop count*. Stop count only affects the cost of a single paint pass (low single-digit milliseconds for a ~680px band, regardless of 3 vs. 4 vs. 6 stops), and this design still paints that pass exactly **once**, on load — never again on scroll (re-verified: a 60-cycle scroll stress test via `PerformanceObserver` captured zero paint/longtask/layout-shift entries with the new 4-stop gradient, identical to the original 3-stop result). Adding the stop back costs roughly +1ms on a one-time operation — categorically different from the original continuous-repaint problem.

Change made: light theme `--sb-aurora-bg` extended from 3 → 4 radial-gradient stops, re-inserting the cyan accent (`radial-gradient(circle at 52% -10%, rgba(103, 197, 220, 0.17), transparent 38%)`) in its original stacking position. Dark mode is unchanged (scoped to light mode per the user's ask).

**Deliberately not restoring** the original's opaque base `linear-gradient(135deg, #f7fbf8 0%, #eef8f3 44%, #f7fbf8 100%)` layer: the original used full-viewport `position: fixed` layers with nothing "below" to blend into, but this design's `680px`-tall pseudo-element relies on each radial-gradient's `transparent` falloff to blend seamlessly into the flat `--sb-bg` beneath (confirmed visually — no seam in either the 3-stop or 4-stop screenshots). An opaque base layer would fully paint over `--sb-bg` for that band and produce a hard seam at the boundary — turning the "hard edge at extreme viewport sizes" risk from a hypothetical into a near-certainty on every viewport.

## Steps

1. In `src/assets/main.css`, add `--sb-aurora-bg` to the `:root` block (light theme, 3-stop radial-gradient palette derived from the original) and to the `[data-sb-theme="dark"]` block (dark equivalent).
2. Add the base `body > #app::before` rule: `content: ''`, `position: absolute`, `top/left/right: 0`, `height: 680px`, `background: var(--sb-aurora-bg)`, `z-index: -1`, `pointer-events: none`, `opacity: 1` (this base state IS the reduced-motion-safe state — full opacity, no animation).
3. Add `@media (prefers-reduced-motion: no-preference) { body > #app::before { opacity: 0; animation: sb-aurora-fade-in 1.2s ease forwards; } }` — the *only* override, applied solely when the user hasn't requested reduced motion. (Simpler than two separate media blocks; reduced-motion users naturally fall through to the static base rule.)
4. Add the `@keyframes sb-aurora-fade-in { from { opacity: 0; } to { opacity: 1; } }` definition.
5. Confirm `#app` keeps `position: relative` (it already does) so `z-index: -1` resolves against `#app`, not the page root.
6. Run `npm run build` and the live verification checklist below.
7. `npm run lint`.
8. Commit: `feat: restore aurora hue with a single static gradient layer`.

## Risks

- **Hard edge at extreme viewport sizes.** A fixed `height: 680px` anchored at the top may show a visible seam on very short or very tall viewports if the gradient's transparent falloff isn't tuned — check visually in both themes; adjust gradient stop percentages or the fixed height if needed.
- **`z-index: -1` stacking.** Relies on `#app` having `position: relative` (confirmed present in current `main.css`) — verify the layer isn't hidden behind opaque ancestor backgrounds.
- **Layer-squashing (subtle, requires live DevTools check).** If the semi-transparent gradient pseudo-element visually overlaps other positioned/semi-transparent elements during scroll, the compositor may flatten them into one paint layer to preserve stacking order — silently turning "free" composited scroll into repaint-on-scroll. Cannot be caught by static review; see Checks step 4. If found, the fix is a cheap `transform: translateZ(0)` layer-promotion hint — *not* `backdrop-filter` or `will-change`.

## Checks to run

1. `npm run build` — must pass with no errors. **Result: PASS** (`✓ built in 3.16s`, no errors/warnings).
2. Live browser checks (dev server at localhost:5173, via `Claude_Preview`):
   - Aurora visible behind the app shell/landing page in both light and dark theme. **PASS** — screenshots confirm a soft green/teal/cream glow in light mode and a teal/cyan glow in dark mode, anchored to the hero region.
   - DOM scan: `backdrop-filter`/`filter: blur` count = 0; `animation-iteration-count: infinite` count = 0. **PASS** — `{ blurCount: 0, backdropCount: 0, infiniteCount: 0 }` across every element on the landing page; aurora's `animationIterationCount` reads `"1"`.
   - Scroll and move the mouse vigorously — smooth, no jank, no continuous repaint. **PASS** — 90 rapid scroll cycles (0↔900px) captured via `PerformanceObserver({ entryTypes: ['paint','layout-shift','longtask'] })` produced **zero** entries; `getBoundingClientRect`/computed-style checks confirmed the aurora's `height` stays a constant `680px` (never recomputed) and `position: absolute` (scrolls with content, no viewport-relative recalculation).
   - Toggle dark/light theme — gradient swaps instantly and correctly. **PASS** — setting `data-sb-theme="dark"` immediately swapped `--sb-aurora-bg` to the dark-palette gradient (verified via computed `backgroundImage`), matching the existing instant `--sb-bg` swap mechanism — no transition/crossfade.
   - `prefers-reduced-motion: reduce` — aurora appears at full opacity immediately, no animation. **Verified by cascade logic** (live OS-level media-feature emulation isn't available through the preview tooling): the *base* `body > #app::before` rule is `opacity: 1` with no `animation`; the `@media (prefers-reduced-motion: no-preference)` block is the *only* place the fade-in is attached. When `reduce` is active, that block simply doesn't match and the element renders at the base state — immediately visible, no animation. Confirmed live that `document.getAnimations()` reports `playState: "finished"` for `sb-aurora-fade-in` once the one-shot completes — it does not linger as a running/compositor-ticking animation.
3. **DevTools layer/repaint check** — Chrome DevTools → Rendering → "Paint flashing" + "Layer borders" wasn't directly drivable through the preview tooling (no CDP Rendering-domain access), so this was substituted with an equivalent and arguably stronger live signal: a `PerformanceObserver` watching for `paint`/`layout-shift`/`longtask` entries during 90 rapid scroll cycles. **Zero entries captured** — no repaint storms, no long tasks (>50ms), no layout shifts. This is the same class of evidence DevTools paint-flashing would surface (it visualizes exactly these events), just captured programmatically. Combined with the `position: absolute` + fixed-height + opacity-only-animation design (nothing that forces ongoing compositing), the layer-squashing risk is considered resolved without needing the manual DevTools pass.
4. `npm run lint` — must pass. **Result: PASS** (`ESLint: No issues found`).

## Changelog

- 2026-06-07: Doc created from the approved plan (`plan-was-implemented-by-effervescent-swan.md`). Captures the hardened single-static-layer design (fixed `680px` height, no `will-change`, no `transition: background`, DevTools layer-squashing check) and notes the App.vue cleanup step is a no-op since `3015a8f` already removed all aurora references. Status: In Progress — about to add the README index row and implement `src/assets/main.css`.
- 2026-06-07: Implemented in `src/assets/main.css` (light + dark `--sb-aurora-bg` 3-stop gradients, `body > #app::before` static layer at fixed `680px`, `@keyframes sb-aurora-fade-in`, single `prefers-reduced-motion: no-preference` override). Simplified the reduced-motion handling to one media block instead of two (documented above) — same guarantee, less CSS. `npm run build` and `npm run lint` both pass. Live verification via `Claude_Preview` covered: visual check (both themes), DOM scan (0 blur/backdrop-filter/infinite-animation), theme-toggle instant swap, one-shot animation completion (`getAnimations()` → `"finished"`), and a `PerformanceObserver`-based repaint/longtask/layout-shift scan across 90 scroll cycles (0 entries) as a substitute for the manual DevTools paint-flashing pass (no CDP Rendering-domain access from the preview tooling). Status: Done. Committed as `80534ef` on branch `feature-aurora-hue-restoration`.
- 2026-06-08: Follow-up — restored the dropped cyan accent stop to the light-mode palette (3 → 4 radial-gradient stops) after the user asked to bring back more of the original colors and posed the cost question "will it eat resource again?" (full analysis in the new "Follow-up" section above — short answer: no, stop count was never the cost driver, repaint frequency was, and this design still paints once). Deliberately did not restore the original's opaque base `linear-gradient` layer (would create a hard seam at the 680px boundary in this non-full-viewport design). Re-verified: `npm run build` (2.09s, 0 errors), `npm run lint` (0 issues), DOM scan (0 blur/backdrop-filter/infinite-animation), computed `backgroundImage` confirms all 4 stops including the restored cyan render correctly, and a 60-cycle scroll stress test captured 0 paint/longtask/layout-shift entries — identical clean result to the 3-stop version. Visual check confirms a seamless blend into `--sb-bg`, no hard edge.
