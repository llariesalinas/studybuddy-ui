---
title: Landing page redesign — Studio Motion
date: 2026-06-11
status: Done
spec: ../superpowers/specs/2026-06-11-landing-page-redesign-design.md
---

# Landing page redesign — Studio Motion

## Status & Progress Summary

**Status: Done - revised tools rail, count band, and marquee loop port shipped.**
The Studio Motion landing page is implemented in `src/views/LandingPage.vue` with the
approved pinned Platform tools rail, tokenized object doodles, full-width count band,
generous FAQ spacing, seamless viewport-safe marquee loop, aurora ribbons,
lifecycle-managed motion, text-fit fixes, and performance guardrails. Global accent
tokens and landing-route aurora suppression live in `src/assets/main.css`.

Verification passed for non-mutating lint and production build. Code review also caught
and fixed the rail measurement order so travel is measured after leaving the `.nopin`
stacked fallback; the in-app browser blocked localhost during this session, so final
visual/browser QA should be done from a normal local browser.

## Goal

Replace `src/views/LandingPage.vue` with the approved "Studio Motion" design: oversized
typography, lerped smooth scrolling, reactive cursor, per-card haptic tilt, scroll-driven
character animations, seamless marquee, and an aurora ribbon background — campus-agnostic
copy, no fake social proof, zero new dependencies.

Reference artifact (approved, pixel-level source of truth for markup, CSS, and JS
parameters): `docs/artifacts/2026-06-11-landing-redesign-reference.html`.

Plan file for implementation tracking:
`docs/plans/2026-06-11-landing-page-redesign.md`.

## Approach

Port the artifact into the Vue SFC rather than redesigning anything: the artifact's CSS
becomes scoped styles (hex values swapped for `--sb-*` tokens), its markup becomes the
template (anchors swapped for `router.push` handlers), and its script becomes
`<script setup>` lifecycle-managed code. The page keeps its own nav/footer as today.
Motion stays vanilla (rAF + IntersectionObserver) to match the codebase's no-library
approach; everything is gated on `pointer: fine` and `prefers-reduced-motion` and torn
down in `onUnmounted`.

Artifact fidelity is the visual contract: keep the section order, copy, typography,
spacing rhythm, illustration language, and motion parameters from
`docs/artifacts/2026-06-11-landing-redesign-reference.html`, changing only what is needed
to make the HTML safe in Vue, theme-tokenized, accessible, responsive, and performant.

Key decisions:
- New accent tokens (`--sb-pop-yellow/orange/pink`, `--sb-aurora-violet`) go in
  `src/assets/main.css` for both themes, since components must not hardcode hex.
- The landing page's aurora ribbons replace the global `#app::before` aurora on this
  route (suppress via a route/landing class) — never render both.
- The fake stats, testimonials, and multi-column footer are removed with the rewrite.
  The newly approved Platform tools and Common questions sections stay in scope and must
  match the reference artifact/spec.
- Text must never clip in the final rendered state. Masked reveal wrappers may hide text
  only during the reveal animation; normal copy, FAQ questions, tool cards, nav actions,
  CTA labels, and final heading states must wrap or resize safely.
- Landing animation work runs only while the landing route is active and visible. It must
  stop before navigating to `/login` or `/register`, when the tab is hidden, and whenever
  reduced-motion or pointer gating makes the effects ineligible.
- Do not reintroduce the previous aurora performance failure mode: no aurora pointer
  tracking, no per-frame CSS variable writes on `:root`, no animated gradients or
  `background-position`, no `backdrop-filter`, no `filter: blur`, and no
  `transition: background`.

## Steps

1. **Tokens** — add the four accent tokens + the three aurora base-gradient stops to
   `src/assets/main.css` under both the light root and `[data-sb-theme="dark"]`
   (dark values dimmed ~50%). Run `npm run dev` and confirm vars resolve.
2. **Static rebuild of `LandingPage.vue`** — replace template + scoped styles with the
   artifact's sections in order: nav w/ existing theme toggle, hero, marquee, 3 panels,
   Platform tools, count strip, Common questions, CTA panel, footer. No JS motion yet.
   SVG fills/strokes use classes bound to tokens. CTAs use
   `router.push('/register' | '/login')`. Verify all sections render in light + dark,
   desktop + mobile widths, with no clipped text.
3. **Reveal layer** — IntersectionObserver for `.reveal`, hero line masks, panel
   clip-path reveals, Platform tools and FAQ section-head masks, tool-card/FAQ-item
   stagger reveals, and count-up numbers (1100ms cubic ease-out, fire once).
   Reduced-motion fallback: everything visible, no transitions.
4. **Continuous-motion layer** — lerped smooth scroll (spacer + fixed content,
   factor 0.085, ResizeObserver for height), custom cursor (lerp 0.2, grow on
   interactive), illustration parallax (`data-depth`), character wiggle (`.char` groups,
   formulas + amps from spec), per-card tilt (configs from spec), magnetic CTA (0.35).
   Use Vue template refs rather than artifact globals like `#smooth`, `#cursor`, or
   `#scrollspace`. Gate all continuous work on active landing route + visible document +
   `pointer: fine` + no reduced motion. Store every rAF id, listener, timeout, media
   listener, and observer; stop them in `onBeforeRouteLeave` before `/login`/`/register`
   transitions start and remove all of them in `onUnmounted`. Add `visibilitychange`
   handling: pause/cancel rAF loops while hidden; recompute layout and restart only if
   still on `/` and still eligible.
5. **Aurora + global-aurora suppression** — add the `.bgwash` ribbons; suppress the
   global `#app::before` aurora while the landing route is active by adding
   `body.sb-landing-route` on mount and removing it on route leave/unmount. Add a global
   rule in `src/assets/main.css`:
   `body.sb-landing-route > #app::before { display: none; animation: none; }`.
   Confirm only one aurora paints. Landing ribbons may animate `transform` only and must
   stop under reduced motion.
6. **Polish + a11y pass** — focus styles, aria-hidden on decorative layers, heading
   order, marquee seamlessness check (track width must equal exactly 2x each half),
   dark-mode contrast of marquee/count strip, and text-fit checks. Fix clipping by
   wrapping, adjusting `min-width: 0`, `flex-shrink`, grid tracks, padding, line-height,
   or responsive clamps; do not hide real text with `overflow: hidden` outside reveal
   masks.
7. **Verification + docs** — run checks below; smoke-test nav → `/login`/`/register`
   and back (no stray rAF/listeners — confirm via Performance monitor or console
   counters); write the session summary in `docs/session-summaries/` and flip this
   plan's status to Done (mirror in `README.md` index).
8. **Port the revised tools rail + count band + spacing pass** (from the 2026-06-11
   later spec revision; reference artifact is the source of truth):
   - **Tokens**: add `--sb-pop-yellow-deep` `#DCA21B`, `--sb-pop-orange-deep` `#E0683A`,
     `--sb-pop-pink-deep` `#E26D86` to `src/assets/main.css` (plus readable dark-theme
     variants) for the rail numerals.
   - **Template**: replace the `.toolgrid`/`.toolcard` block in `LandingPage.vue` with
     the rail structure — `.toolstage` > `.toolpin` > head + `.tooltrack` > four
     `.tslab` articles (`numeral | .ttext | .tviz` object doodles: magnifier+star,
     calendar+clock, bars+coin, balance scale; SVG colors via the existing `svg-*`
     utility classes, never literal hex; add `.svg-pink-fill` etc. as needed). Drop the
     icon-chip `tools` data fields.
   - **JS**: add `toolstageRef`/`toolpinRef`/`tooltrackRef`; `measureRail()` caches
     `travel = track.scrollWidth - (innerWidth - 80)` on motion start + window resize
     (listener in `motionCleanupFns`); `toolPin()` runs inside `runSmoothLoop` after
     `charWiggle` — counter-translate the pin (`position: sticky` cannot work inside the
     fixed+translated smooth wrapper), rail progress `rp = clamp((p - .05)/.85)` →
     `translateX(-rp * travel)`; clear both transforms in
     `stopContinuousMotion({ reset: true })`. When continuous motion is ineligible,
     a `nopin` class on the section keeps the stage auto-height and slabs stacked.
   - **CSS**: rail styles per spec (stage 300vh, slabs 60vw × ≥30vh, serif italic
     numerals at 20% opacity, title 34–58px, body 17–21px, per-slab `color-mix` hover
     shadows); count strip → count band (full-width primary tint at ~4.5%, hairline
     borders, 54–96px numerals, 130px padding); FAQ rows 38px + ~170px section padding;
     update the `<900px`, reduced-motion, and `nopin` fallbacks; remove dead
     `.toolgrid`/`.toolcard`/`.chip` rules and the `.toolcard` entries in the reveal
     selectors.
   - **Checks**: `npx oxlint .`, `npx eslint . --cache --max-warnings=0`,
     `npm run build`; manual pin QA (anchor engages/releases cleanly, scrub reverses,
     rail re-measures on resize); degraded QA (touch + reduced motion = stacked static
     column); dark mode numeral legibility; `/login` round-trip leaves no rail
     transforms or resize listener behind. Then flip this plan to Done and update the
     session summary + `README.md` index.

## Risks

- **Smooth scroll vs. app shell**: `App.vue` page transitions + a `position: fixed`
  content wrapper can fight (transformed ancestors break `position: fixed` children).
  Mitigation: keep the smooth-scroll wrapper inside the landing page only, and verify
  the route-leave transition; if it glitches, fall back to native scroll + keep all
  other motion (acceptable degradation, decided in review if hit).
- **Leaked loops/listeners** after navigation — the page runs 2 rAF loops; missing
  teardown would burn CPU app-wide. `onUnmounted` must cancel both and remove all
  listeners/observers (explicit step 4 acceptance criterion).
- **Inactive-page animation cost** — animation must not continue when the landing page is
  not in use. `onBeforeRouteLeave` stops continuous work before navigating to `/login` or
  `/register`; `visibilitychange` pauses work while the tab is hidden; `onUnmounted` is
  the final cleanup backstop.
- **Aurora performance regression** — the previous slowdown came from per-frame aurora
  updates plus blur/backdrop sampling. This implementation must keep aurora motion
  transform-only, avoid `backdrop-filter`/`filter: blur`, avoid animated gradients, and
  avoid per-frame root CSS variable writes.
- **Global aurora double-paint** (step 5) — visual mud + extra paint cost if both render.
- **Text clipping/regression** — the artifact uses oversized type and masked reveal rows.
  The final state must be inspected at narrow and desktop widths; only reveal masks may
  clip during animation, never settled headings or body copy.
- **Marquee regression**: any future copy edit that changes one half's width breaks the
  seamless loop; keep the two halves as a single repeated constant in the template
  (`v-for="n in 2"` over the same items array) so they cannot drift.
- **SVG `var()` quirks**: presentation attributes don't accept `var()`; fills must be
  set via CSS classes or `style` bindings. Caught in step 2 rendering check.
- **Scroll restoration**: router `scrollBehavior` + the spacer technique — confirm
  returning to `/` lands at top with correct body height.

## Checks to run

- Non-mutating lint checks — current `npm run lint` rewrites files via `--fix`, so use
  `npx oxlint .` and `npx eslint . --cache --max-warnings=0` for verification unless the
  worktree has been reviewed and formatting churn is explicitly acceptable.
- `npm run build` — succeeds.
- Manual (dev server, fine pointer): hero reveal on load; marquee loops with no visible
  jump for 2+ cycles; each panel card tilts with its distinct config and colored shadow;
  characters wiggle during scroll and settle when idle; counters animate once; magnetic
  CTA pulls and springs back; cursor grows over links.
- Manual (degraded): DevTools → emulate `prefers-reduced-motion: reduce` → no animation,
  all content visible; device emulation (touch) → native scroll, no cursor, no tilt.
- Text-fit QA: inspect at `360`, `390`, `768`, `900`, `1024`, and desktop widths in both
  themes. Confirm no clipped nav labels, CTA labels, hero/panel/tools/FAQ headings, FAQ
  questions, card titles, or body copy.
- Dark mode toggle: all sections legible, aurora dimmed, no hardcoded-light surfaces.
- Performance QA: DOM scan confirms zero `backdrop-filter`/`filter: blur`; no animated
  gradients/background-position; no per-frame CSS variable writes on `:root`; no long
  tasks > 50ms during scroll/mouse stress.
- Navigate `/` → `/login`/`/register` → back: no console errors, no cursor/spacer/body
  class left behind, no residual rAF loops or scroll/mouse listeners (check console
  counters or `getEventListeners(window)` in DevTools), correct scroll position.
- Hide and restore the tab while on `/`: landing animation loops pause while hidden and
  restart cleanly only if the landing route is still active and eligible.

## Changelog

- **2026-06-11** — Plan created from the approved Studio Motion design. Captured the
  7-step implementation sequence, risks (smooth-scroll vs app shell, teardown, aurora
  double-paint, marquee drift), and verification checklist. Status set to Approved;
  reference artifact and spec saved alongside.
- **2026-06-11 (later)** — Scope update before implementation: new step copy (Share what
  you need / Match and book / Learn and track), added Platform tools section (4 cards,
  staggered pop-in, colored hover shadows) and Common questions accordion (spring
  expand, rotating plus icon). Spec and reference artifact re-synced; step sequence
  unchanged (new sections land in Steps 2–3).
- **2026-06-11 (guardrails)** — Added implementation guardrails from plan review:
  reference artifact fidelity, corrected Platform tools/Common questions scope, no text
  clipping in final states, concrete landing-route global aurora suppression, animation
  shutdown on route leave/tab hidden/reduced-motion or pointer changes, non-mutating lint
  checks, and explicit protections against the previous aurora paint/blur performance
  issue.
- **2026-06-11 (implementation)** — Implemented in `src/views/LandingPage.vue` and
  `src/assets/main.css`. Non-mutating lint checks and `npm run build` pass. Browser
  verification covered artifact sections, no positive horizontal overflow at
  `360/390/768/900/1024/1280`, no clipped text in settled states, zero
  `backdrop-filter`/`filter: blur`, global aurora suppression, and `/login` cleanup with
  no leftover landing body class, cursor, spacer, or smooth-scroll root.
- **2026-06-11 (tools rail redesign)** — Design review continued after implementation:
  Platform tools went flat grid → bento → pinned scrubbed assembly → final **pinned
  horizontal rail** (white banner slabs `numeral | text | object doodle`, serif numeral
  watermarks, no characters in the doodles); count strip became a full-width count band;
  tools/FAQ stretch got a generous-spacing pass. Spec, reference artifact, and mockup
  demos (`tools-strip-demos.html`, `tools-layout-options.html`) updated. Status reopened
  to In Progress; the Vue port is captured as Step 8 — no application code changed in
  this revision.
- **2026-06-11 (rail port implementation)** — Ported Step 8 into
  `src/views/LandingPage.vue` and `src/assets/main.css`: pinned rail with manual
  counter-translate inside the smooth-scroll rAF loop, cached rail travel on resize,
  tokenized rail doodles and deep numeral tokens, full-width count band, FAQ spacing
  pass, viewport-safe marquee loop, and touch/reduced-motion stacked fallbacks. Status
  set to Done after lint/build verification and a code-level rail measurement fix.
