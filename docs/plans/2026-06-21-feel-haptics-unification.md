---
title: Unified feel & haptics (Balanced calibration)
date: 2026-06-21
status: Done
spec: ../specs/2026-06-21-feel-haptics-unification-design.md
---

# Unified feel & haptics (Balanced calibration)

## Status & Progress Summary

Done. P1 (tokens + primitive retune) and P2 (`.sb-field` + focus-visible halo) shipped first.
This entry was written retroactively to close two gaps found during a later audit: P3 (post-May
view audit) had missed the `src/components/session/` cards, and P4 (reconciling inline
divergence) had missed three hardcoded focus-halo literals and three hardcoded hover-lift
magnitudes in `TutorProfile.vue`/`TuteeProfile.vue`/`src/components/session/*`. Both are now
fixed; see Changelog.

## Goal

Collapse the app's two coexisting motion systems (the global `.sb-*` vocabulary and the profile
views' own inline patterns) into one token-driven "Balanced" calibration, so every interactive
surface shares the same curve, timing, lift, press, and focus-halo values.

## Approach

Promote the profile's feel to the canonical language. Add the missing tokens
(`--sb-lift-control`, `--sb-lift-surface`, `--sb-press`, `--sb-halo`,
`--sb-shadow-rest`/`--sb-shadow-hover` (+ `-brand` variants)) to `src/assets/main.css`, retune
`.sb-btn`/`.sb-interactive` to reference them, add `.sb-field` for form controls, then audit
views built after the May 2026-05-25 rollout and reconcile any component still hardcoding a
curve/magnitude instead of referencing a token.

## Steps

1. **P1 — Tokens + primitive retune.** Add the Balanced tokens to `main.css`; retune `.sb-btn` /
   `.sb-interactive` transforms and add the `.sb-elevated` / `.sb-elevated--brand` layered-shadow
   primitive. *(Done prior to this entry.)*
2. **P2 — Input & focus feel.** Add `.sb-field` plus a global `:focus-visible` halo for form
   controls. *(Done prior to this entry.)*
3. **P3 — Audit & transitions.** Confirm post-May views (SuperAdmin dashboard/reports, the admin
   dashboard redesign, `src/components/session/`) carry the primitive classes or token
   references. Found `SessionHero.vue`, `SessionInfoGrid.vue`, and `SessionTimeline.vue` each
   duplicated a `.session-card:hover` rule with a hardcoded `translateY(-3px)` instead of a lift
   token — fixed in this entry.
4. **P4 — Reconcile inline divergence.** Point `TutorProfile.vue` / `TuteeProfile.vue`'s
   hardcoded focus-halo `box-shadow: 0 0 0 4px rgba(0, 137, 90, 0.1[0-2])` literals (3 instances)
   at `var(--sb-halo)` so they inherit dark-mode adaptation instead of a fixed light-mode-only
   color. Confirmed the profile views' transition timing/curve already referenced
   `var(--sb-t-normal)` / `var(--sb-spring)` (no further change needed there).

## Risks

- The `.session-card` hover lift (`-3px` → `var(--sb-lift-surface)`, i.e. `-6px`) doubles the
  hover-lift distance on three non-clickable display cards (`SessionHero`, `SessionInfoGrid`,
  `SessionTimeline`). This is a deliberate consequence of unifying onto the canonical surface-lift
  token, not a regression, but it is a visible magnitude change worth a quick browser glance.
- `--sb-halo` resolves through `--sb-focus-ring`, which has a different dark-mode value than the
  light-mode literal it replaces — intentional (closes a dark-mode gap), but flag if a dark-mode
  screenshot shows an unexpected halo color shift.

## Checks to run

- `npx eslint` on each touched file — passed.
- `npm run build` — passed.
- Browser pass (not yet done in this entry): hover a `SessionInfoGrid`/`SessionTimeline` card and
  confirm the larger lift reads fine; focus a profile subject-description input/textarea in both
  light and dark mode and confirm the halo still looks like a focus ring.

## Changelog

- 2026-06-21: P1 and P2 implemented (tokens, `.sb-btn`/`.sb-interactive` retune, `.sb-field`,
  focus-visible halo). Spec marked Done, but no plan file was written at the time.
- 2026-06-22: Audit found P3/P4 gaps (see Steps 3-4) and fixed them. Wrote this plan file
  retroactively per the project's plan-before-code convention, since the original P1/P2 work had
  shipped without one.
