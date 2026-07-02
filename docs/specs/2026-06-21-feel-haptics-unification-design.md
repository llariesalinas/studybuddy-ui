# Unified Feel & Haptics ("Balanced", profile-derived) — Design Spec

Date: 2026-06-21
Status: Done
Reference artifact: `docs/artifacts/2026-06-21-feel-haptics-calibrations-reference.html`
(the "Balanced" column from a 3-calibration visual-companion session — Subtle /
Balanced / Lively; user picked Balanced)

---

## Overview

Make the whole app feel like it came from one hand. Today there are **two
coexisting motion systems**:

1. A global `.sb-*` vocabulary split between [`App.vue`](../../src/App.vue) and
   [`main.css`](../../src/assets/main.css) — tokens
   (`--sb-t-quick`, `--sb-t-normal`, `--sb-spring`, `--sb-spring-fast`), the
   primitive classes `.sb-btn` (hover `translateY(-3px)`, press `scale(0.96)`)
   and `.sb-interactive` (lift `-6px`), plus a keyframe library (`sb-pop`,
   `sb-shake`, `sb-stagger-in`, `sb-scale-in`, `sb-toast-in`, `sb-bubble-in`,
   `sb-tab-indicator`, `sb-success-border`) and a `prefers-reduced-motion`
   guard. These classes were rolled out app-wide in the May pass
   ([2026-05-25-haptics-rollout.md](../plans/2026-05-25-haptics-rollout.md)).
2. The **profile views'** own inline patterns
   ([`TutorProfile.vue`](../../src/views/TutorProfile.vue),
   [`TuteeProfile.vue`](../../src/views/TuteeProfile.vue)) — press `scale(0.97)`,
   spring `cubic-bezier(0.16, 1, 0.3, 1)`, soft focus halos
   (`0 0 0 4px rgba(0,137,90,.12)`), accordion `max-height` reveals, and
   direct `box-shadow` hover transitions.

This spec promotes the **profile's feel** to the canonical language and
collapses the two systems into one source of truth, retuned to the user-picked
**Balanced** calibration. The profile stops being a *separate* implementation
and becomes the *reference* implementation that everything else inherits.

This is an **interaction-feel + consistency** pass. It is not a visual redesign:
no color, layout, typography, or content changes.

## Goals

- **One canonical motion language**, derived from the profile, applied to every
  interactive surface: buttons, form controls, cards/rows, navigation, and
  overlays/transitions.
- **Single source of truth** in `src/assets/main.css`: tokens + a small primitive class set.
  Consistency flows from the tokens, not from blanket element selectors.
- **Close the gaps** the May rollout left — chiefly the missing input/form-control
  feel and focus halo — and audit views built after that rollout.
- **Stay within the documented performance guardrails** so we do not reintroduce
  the jank removed in the June-7 cleanup.

## Canonical feel (the "Balanced" calibration)

All values live as CSS custom properties in `src/assets/main.css` `:root`. Components and the
primitive classes reference the tokens; no component hardcodes a curve or a
magnitude.

| Token | Value | Role |
|---|---|---|
| `--sb-spring` | `cubic-bezier(0.16, 1, 0.3, 1)` | the one easing curve (confirm existing) |
| `--sb-t-quick` | `130ms` | quick transitions (press release, focus) |
| `--sb-t-normal` | `180ms` | standard hover/entrance transitions |
| `--sb-lift-control` | `-4px` | hover lift for buttons / pills / controls |
| `--sb-lift-surface` | `-6px` | hover lift for cards / rows / larger surfaces |
| `--sb-press` | `0.97` | press-down scale |
| `--sb-halo` | `0 0 0 4px rgba(0, 137, 90, 0.12)` | focus halo |
| `--sb-shadow-rest` / `--sb-shadow-hover` | `0 6px 16px rgba(15,23,42,.06)` / `0 16px 36px rgba(15,23,42,.12)` | layered surface shadow |
| `--sb-shadow-rest-brand` / `--sb-shadow-hover-brand` | `0 8px 18px rgba(0,137,90,.20)` / `0 14px 30px rgba(0,137,90,.28)` | layered primary-control shadow |

Decision: keep the **`-4px` control / `-6px` surface** lift split (larger surfaces
naturally carry a bit more lift). This is tunable — both come from one token, so
changing the feel later is a one-line edit.

## Primitive classes (one place, propagates everywhere)

- **`.sb-btn` / `.sb-interactive`** — retune transforms to the tokens above.
  Compatible elevated controls opt into **`.sb-elevated`** (plus
  **`.sb-elevated--brand`** for primary controls), whose `::after` pre-renders
  the deeper shadow and fades its opacity. Table rows, clipped surfaces, and
  elements already using `::after` remain transform-only.
- **`.sb-field`** (new) — the profile's input/form-control feel applied as a
  canonical primitive: immediate border-color + `--sb-halo` on focus, on
  `<input>`/`<select>`/`<textarea>`. Paired with a global
  `:focus-visible` halo so keyboard focus is consistent even on controls that
  never receive the class. This is the genuinely-missing piece — inputs have no
  canonical treatment today.
- Press-scale and the focus halo are **universal**; hover-lift stays **opt-in**
  via class to avoid surprise regressions on bespoke components.

## Reconcile divergence

- Replace the hardcoded `cubic-bezier(0.16,1,0.3,1)` literals and one-off
  `transform`/`box-shadow` transitions in `TutorProfile.vue`, `TuteeProfile.vue`
  and peers with token references, so there is a single curve/magnitude source.
- Audit views built **after** the May rollout — SuperAdmin
  ([`SuperAdminDashboard.vue`](../../src/views/SuperAdminDashboard.vue),
  [`SuperAdminReports.vue`](../../src/views/SuperAdminReports.vue)), the admin
  dashboard redesign, and the session-details views
  ([`src/components/session/`](../../src/components/session)) — to confirm
  buttons/cards carry the primitive classes and inputs carry the focus treatment.

## Overlays & transitions

- Standardize the existing entrance keyframes (`sb-stagger-in`, `sb-scale-in`,
  `sb-toast-in`, modal/`sb-bubble-in`) on the canonical spring + `--sb-t-normal`,
  so lists, toasts, and modals settle with the same curve. No new keyframes.

## Performance guardrails (hard rules)

Derived from the June-7 incident
([2026-06-07-global-aurora-blur-performance-cleanup-summary.md](../session-summaries/2026-06-07-global-aurora-blur-performance-cleanup-summary.md)),
where compositor-heavy effects caused sluggish scrolling and GPU/DWM load:

- Animate **only** `transform` and `opacity`. Never animate layout properties
  (`width`/`height`/`top`/`left`) or paint-heavy properties across many elements.
- **No** `backdrop-filter` / `-webkit-backdrop-filter`, **no** `filter: blur()`,
  **no** full-viewport animated gradient/aurora layers, **no** JS pointer-driven
  motion.
- Shadows animate via **pseudo-element opacity**, never `box-shadow` spread on
  lists/grids.
- Keep and honor the existing `prefers-reduced-motion` guard; new motion must be
  covered by it.

## Rollout — phased, each phase independently shippable and verifiable

Each phase ends with `npm run build` + a browser check of the affected surfaces.

- **P1 — Tokens + primitive retune.** Add the new tokens; retune `.sb-btn` /
  `.sb-interactive` to the Balanced values and the layered-shadow technique.
  *(Biggest payoff, lowest risk — already-applied classes inherit instantly.)*
- **P2 — Input & focus feel.** Add `.sb-field` + the global `:focus-visible`
  halo; apply to form controls.
- **P3 — Audit & transitions.** Fill gaps on post-May views; standardize
  overlay/list entrance transitions on the canonical spring/timing.
- **P4 — Reconcile inline divergence.** Point the profile views' (and peers')
  hardcoded curves/transitions at the tokens; remove duplicated literals.

## Out of scope (YAGNI)

- No new decorative/signature animations beyond standardizing what exists.
- No color, layout, typography, or content/visual redesign.
- No reintroduction of blur/backdrop/aurora or any pointer-driven motion.
- No new dependencies; pure CSS + existing class application.
- Physical vibration behavior in `useHaptics()` is unchanged; "haptics" in this
  spec refers to CSS interaction feel.
- `SessionAurora.vue` is the sole documented temporary blur exception and is
  handled by a separate cleanup.

## Checks to run

- `npm run lint`
- `npm test`
- `npm run build`
- Per-phase browser pass on representative surfaces (a profile view, a dashboard
  with cards, a form, a modal/toast), confirming: hover lift + shadow, press
  scale, focus halo, no console errors, and no animated `box-shadow`/`blur`
  layers in computed styles.
