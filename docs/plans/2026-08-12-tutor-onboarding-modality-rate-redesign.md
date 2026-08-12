---
title: Tutor onboarding modality and rate field redesign
date: 2026-08-12
status: In Progress
summary: Restyle TutorPreferenceSetup's modality toggles as pills and its hourly-rate input as a typable/scrubbable field, matching the app's canonical feel tokens.
spec: ../mockups/2026-08-12-tutor-onboarding-modality-pills.html
---

# Tutor onboarding modality and rate field redesign

**Status & Progress Summary** (2026-08-12): In Progress. Design settled through a
`grill-with-docs` + `ui-preview` session (see prior entry). Implemented in
`src/views/TutorPreferenceSetup.vue` plus a new `src/utils/rateScrub.js` (pure drag-math,
unit-tested). A `/code-review` pass (Standards + Spec axes) caught two real issues, both fixed:
the modality pills originally hand-wrote hover/press/shadow CSS instead of reusing the house
`.sb-btn`/`.sb-pill` primitives that `InitialBooking.vue`'s near-identical `.mode-button` already
layers on top of — refactored to match that reference component's exact local-override shape; and
the drag hint/`ew-resize` cursor showed unconditionally, misleading touch users who can't drag —
gated behind `@media (hover: hover) and (pointer: fine)`, mirroring the pattern the pills already
used. Also added `PHP_PER_PIXEL`/`MIN_HOURLY_RATE` named constants in `rateScrub.js` (previously a
bare magic `1`), reused for the submit-time rate validation too. `prefers-reduced-motion` was
flagged as unverified by the spec review but turned out already covered by `main.css`'s blanket
`*, *::before, *::after` guard — no fix needed. 184/184 tests pass, lint clean (pre-existing
`make_algo_pptx.*` errors only), build succeeds. Manual browser walkthrough (light/dark theme,
`prefers-reduced-motion` on) still outstanding before moving to Done.

## Goal

`src/views/TutorPreferenceSetup.vue` — the first step of tutor onboarding — has two
fields that predate the app's later design decisions and no longer match: the
modality toggles are plain Bootstrap switches, and the hourly-rate field is a bare
`<input type="number">` with no currency affordance. Bring both in line with
patterns already shipped elsewhere in the app, without inventing new interaction
models.

## Approach

**Modality (`can_online` / `can_f2f`)** — restyle the two existing checkboxes as
multi-select pill toggle buttons, visually matching the tutee's "Preferred Mode"
picker in `InitialBooking.vue` (`.mode-button` family, Bootstrap Icons
`bi-camera-video-fill` / `bi-geo-alt-fill`). Deliberately **not** copying that
picker's single-select radiogroup semantics — a tutor can genuinely support both
modes at once, so both booleans stay independently toggleable. Only the visual
language changes; the data model (`can_online`, `can_f2f`) is unchanged.

Motion for both fields is built exclusively from the tokens already defined in
`src/assets/main.css` per
[`docs/specs/2026-06-21-feel-haptics-unification-design.md`](../specs/2026-06-21-feel-haptics-unification-design.md):
`--sb-lift-control` (-4px hover lift), `--sb-press` (0.97 press scale),
`--sb-halo` (focus halo), the one spring curve, and the `sb-pop` /
`sb-scale-in` keyframes already in the app's library. No new easing, no blur, no
decorative/pointer-driven motion — consistent with that spec's explicit
guardrails.

**Hourly rate (`hourly_rate`)** — after comparing three directions (plain
restyled input; a dual-purpose slider+stepper; a scrubbable field), settled on a
single `<input>` that is both typable and drag-scrubbable:

- Click and type — a normal text field, `PHP` prefix, using the app's existing
  `.sb-field` primitive (immediate border-color + halo snap on focus, no
  transition — matches how every other field in the app already behaves).
- Click-drag horizontally anywhere else on the field — scrubs the value by ±1 per
  unit of drag (the Figma/After Effects "scrub number" pattern).

This was chosen over two alternatives considered and rejected:
- **Reusing `BudgetRangeSlider.vue`** (dual-handle range) — wrong semantic; that
  component picks a *range* for filtering, not a single declared value.
- **A slider + separate ± stepper row** — visually appealing but introduced a
  *third* distinct interaction model for editing the same `hourly_rate` field
  (alongside `TutorProfile.vue`'s existing pure `+`/`-` stepper used post-onboarding),
  and took up more vertical space than the simple field it was replacing. Explored
  three ways to shrink its footprint, then decided the added complexity wasn't
  earning its keep versus one field that both types and scrubs.

## Decisions locked

1. Modality: multi-select pill toggles (booleans unchanged), Bootstrap Icons, no
   emoji.
2. Hourly rate: single typable + scrubbable `<input>` with `PHP` prefix, ±1 per
   drag-unit, `.sb-field` focus behavior. No stepper buttons, no slider.

Mockups:
- [`docs/mockups/2026-08-12-tutor-onboarding-modality-pills.html`](../mockups/2026-08-12-tutor-onboarding-modality-pills.html)
- [`docs/mockups/2026-08-12-tutor-onboarding-rate-field.html`](../mockups/2026-08-12-tutor-onboarding-rate-field.html)

## Steps

1. Add a `.modality-pill-group` (or similarly named) style block to
   `TutorPreferenceSetup.vue`, replacing the two `form-check form-switch`
   toggles with pill buttons bound to `form.can_online` / `form.can_f2f`. Reuse
   the token-based CSS from the mockup rather than hand-tuning new values.
2. Replace the hourly-rate `<input type="number">` with the typable/scrubbable
   field: a text input (`inputmode="numeric"`) wrapped in a shell that adds
   pointer-drag handling (mousedown/mousemove/mouseup, `+1` per pixel of drag,
   clamped at 0) alongside normal typing, plus the `PHP` prefix. Keep it wired to
   `form.hourly_rate` and the existing `required` validation.
3. Verify keyboard-only and touch users can still fully operate the rate field
   without dragging (typing must always work standalone).
4. Confirm `prefers-reduced-motion` is respected (no motion is introduced beyond
   existing tokens, but re-check the pop/scale-in entrances specifically).
5. Manual browser pass on `TutorPreferenceSetup.vue`: hover/press/focus feel on
   both fields, drag-to-scrub on the rate field, submit flow still works end to
   end (`POST /tutor/setup/`).

## Risks

- Drag-to-scrub on a text input can conflict with native text selection if not
  scoped carefully (mockup only starts a scrub when the mousedown target isn't
  the input's text itself — the real implementation needs the same guard).
- Touch devices don't have a mouse-drag gesture matching desktop scrub; typing
  must remain fully sufficient on its own (already true by design, but worth
  explicit touch-device testing).
- `hourly_rate` is edited in two places now (this page and `TutorProfile.vue`'s
  own stepper) with two different interaction models — accepted tradeoff since
  onboarding privileges simplicity/first-impression and profile-edit privileges
  the existing shipped stepper; not unifying them in this pass.

## Checks to run

- `npm run lint`
- `npm run build`
- Manual browser pass on `TutorPreferenceSetup.vue` (see Steps 5) in both light
  and dark theme, and with `prefers-reduced-motion` enabled.

## Changelog

- **2026-08-12** — Plan created at status Approved. Both onboarding-field decisions
  locked via `grill-with-docs` + `ui-preview`: modality as multi-select pills
  (visual-only change, `can_online`/`can_f2f` untouched); hourly rate as a single
  typable/drag-scrubbable `<input>` after rejecting a slider+stepper hybrid for
  introducing a third interaction model alongside `TutorProfile.vue`'s existing
  stepper. Implementation not started.
- **2026-08-12 (implementation)** — Moved to In Progress. Implemented both fields
  plus `src/utils/rateScrub.js` with a TDD-first pure `computeScrubbedRate`
  function. `/code-review` (Standards + Spec) found and fixed: modality pills
  reused as `.sb-btn`/`.sb-pill` + `InitialBooking.vue`'s `.mode-button` local
  overrides instead of duplicating hover/press/shadow CSS; drag hint/cursor now
  gated to hover-capable pointers so touch users aren't shown an affordance they
  can't use; magic "1 PHP per pixel" and "0 floor" replaced with named constants
  shared between the scrub math and submit validation. 184/184 tests, lint clean
  (pre-existing unrelated errors only), build succeeds. Manual browser
  walkthrough still outstanding.
