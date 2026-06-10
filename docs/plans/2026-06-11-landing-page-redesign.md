---
title: Landing page redesign — Studio Motion
date: 2026-06-11
status: Approved
spec: ../superpowers/specs/2026-06-11-landing-page-redesign-design.md
---

# Landing page redesign — Studio Motion

## Status & Progress Summary

**Status: Approved — not started.** Design phase is complete: the "Studio Motion"
direction was chosen after three mockup rounds, refined (campus-agnostic copy, aurora
background, seamless marquee, per-card haptic tilt, scroll-reactive characters), and
signed off on 2026-06-11. The approved mockup is archived at
`docs/artifacts/2026-06-11-landing-redesign-reference.html` and the design spec at
`docs/superpowers/specs/2026-06-11-landing-page-redesign-design.md`. No application code
has been touched yet; implementation begins at Step 1 (tokens).

## Goal

Replace `src/views/LandingPage.vue` with the approved "Studio Motion" design: oversized
typography, lerped smooth scrolling, reactive cursor, per-card haptic tilt, scroll-driven
character animations, seamless marquee, and an aurora ribbon background — campus-agnostic
copy, no fake social proof, zero new dependencies.

Reference artifact (approved, pixel-level source of truth for markup, CSS, and JS
parameters): `docs/artifacts/2026-06-11-landing-redesign-reference.html`.

## Approach

Port the artifact into the Vue SFC rather than redesigning anything: the artifact's CSS
becomes scoped styles (hex values swapped for `--sb-*` tokens), its markup becomes the
template (anchors swapped for `router.push` handlers), and its script becomes
`<script setup>` lifecycle-managed code. The page keeps its own nav/footer as today.
Motion stays vanilla (rAF + IntersectionObserver) to match the codebase's no-library
approach; everything is gated on `pointer: fine` and `prefers-reduced-motion` and torn
down in `onUnmounted`.

Key decisions:
- New accent tokens (`--sb-pop-yellow/orange/pink`, `--sb-aurora-violet`) go in
  `src/assets/main.css` for both themes, since components must not hardcode hex.
- The landing page's aurora ribbons replace the global `#app::before` aurora on this
  route (suppress via a route/landing class) — never render both.
- The old FAQ, tools grid, stats, testimonials, and multi-column footer are removed with
  the rewrite (per spec).

## Steps

1. **Tokens** — add the four accent tokens + the three aurora base-gradient stops to
   `src/assets/main.css` under both the light root and `[data-sb-theme="dark"]`
   (dark values dimmed ~50%). Run `npm run dev` and confirm vars resolve.
2. **Static rebuild of `LandingPage.vue`** — replace template + scoped styles with the
   artifact's sections (nav w/ existing theme toggle, hero, marquee, 3 panels, count
   strip, CTA panel, footer), no JS motion yet. SVG fills/strokes via classes bound to
   tokens. CTAs use `router.push('/register' | '/login')`. Verify all sections render
   in light + dark, desktop + mobile widths.
3. **Reveal layer** — IntersectionObserver for `.reveal`, hero line masks, panel
   clip-path reveals, count-up numbers (1100ms cubic ease-out, fire once). Reduced-motion
   fallback: everything visible, no transitions.
4. **Continuous-motion layer** — lerped smooth scroll (spacer + fixed content,
   factor 0.085, ResizeObserver for height), custom cursor (lerp 0.2, grow on
   interactive), illustration parallax (`data-depth`), character wiggle (`.char` groups,
   formulas + amps from spec), per-card tilt (configs from spec), magnetic CTA (0.35).
   Gate all of it on `pointer: fine` + no reduced motion; store every rAF id, listener,
   and observer; remove all of them in `onUnmounted`.
5. **Aurora + global-aurora suppression** — add the `.bgwash` ribbons; suppress the
   global `#app::before` aurora while the landing route is active (CSS class on `#app`
   or route-scoped rule). Confirm only one aurora paints.
6. **Polish + a11y pass** — focus styles, aria-hidden on decorative layers, heading
   order, marquee seamlessness check (track width must equal exactly 2x each half),
   dark-mode contrast of marquee/count strip.
7. **Verification + docs** — run checks below; smoke-test nav → `/login`/`/register`
   and back (no stray rAF/listeners — confirm via Performance monitor or console
   counters); write the session summary in `docs/session-summaries/` and flip this
   plan's status to Done (mirror in `README.md` index).

## Risks

- **Smooth scroll vs. app shell**: `App.vue` page transitions + a `position: fixed`
  content wrapper can fight (transformed ancestors break `position: fixed` children).
  Mitigation: keep the smooth-scroll wrapper inside the landing page only, and verify
  the route-leave transition; if it glitches, fall back to native scroll + keep all
  other motion (acceptable degradation, decided in review if hit).
- **Leaked loops/listeners** after navigation — the page runs 2 rAF loops; missing
  teardown would burn CPU app-wide. `onUnmounted` must cancel both and remove all
  listeners/observers (explicit step 4 acceptance criterion).
- **Global aurora double-paint** (step 5) — visual mud + extra paint cost if both render.
- **Marquee regression**: any future copy edit that changes one half's width breaks the
  seamless loop; keep the two halves as a single repeated constant in the template
  (`v-for="n in 2"` over the same items array) so they cannot drift.
- **SVG `var()` quirks**: presentation attributes don't accept `var()`; fills must be
  set via CSS classes or `style` bindings. Caught in step 2 rendering check.
- **Scroll restoration**: router `scrollBehavior` + the spacer technique — confirm
  returning to `/` lands at top with correct body height.

## Checks to run

- `npm run lint` — passes with no new warnings.
- `npm run build` — succeeds (note: the post-build hook may auto-commit staged changes;
  stage intentionally before building).
- Manual (dev server, fine pointer): hero reveal on load; marquee loops with no visible
  jump for 2+ cycles; each panel card tilts with its distinct config and colored shadow;
  characters wiggle during scroll and settle when idle; counters animate once; magnetic
  CTA pulls and springs back; cursor grows over links.
- Manual (degraded): DevTools → emulate `prefers-reduced-motion: reduce` → no animation,
  all content visible; device emulation (touch) → native scroll, no cursor, no tilt.
- Dark mode toggle: all sections legible, aurora dimmed, no hardcoded-light surfaces.
- Navigate `/` → `/login` → back: no console errors, no residual scroll listeners
  (check `getEventListeners(window)` in DevTools), correct scroll position.

## Changelog

- **2026-06-11** — Plan created from the approved Studio Motion design. Captured the
  7-step implementation sequence, risks (smooth-scroll vs app shell, teardown, aurora
  double-paint, marquee drift), and verification checklist. Status set to Approved;
  reference artifact and spec saved alongside.
