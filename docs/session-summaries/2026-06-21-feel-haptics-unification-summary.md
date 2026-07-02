---
title: Unified feel & haptics (Balanced calibration)
date: 2026-06-22
plan: ../plans/2026-06-21-feel-haptics-unification.md
spec: ../specs/2026-06-21-feel-haptics-unification-design.md
---

# Unified feel & haptics — summary

P1 (Balanced tokens + `.sb-btn`/`.sb-interactive` retune) and P2 (`.sb-field` + focus-visible
halo) had already shipped in `src/assets/main.css`. This session audited P3 and P4, which the
spec marked Done but had real gaps, and fixed both without changing any visual design beyond
unifying onto the canonical tokens.

## What changed

- **P3 gap (post-May audit):** `SessionHero.vue`, `SessionInfoGrid.vue`, and
  `SessionTimeline.vue` each had a duplicated `.session-card:hover` rule with a hardcoded
  `transform: translateY(-3px)`. Replaced with `var(--sb-lift-surface)` (`-6px`) in all three
  files so the hover lift is token-driven like the rest of the app.
- **P4 gap (inline divergence):** `TutorProfile.vue` (two instances) and `TuteeProfile.vue` (one
  instance) hardcoded the focus-halo `box-shadow: 0 0 0 4px rgba(0, 137, 90, 0.1[0-2])` instead of
  referencing `var(--sb-halo)`. Replaced all three so the halo now adapts in dark mode (it
  previously did not).
- Confirmed the profile views' transition timing/curve already referenced `var(--sb-t-normal)` /
  `var(--sb-spring)` — no further P4 changes needed there.
- Wrote the plan file that should have accompanied the original P1/P2 work, since none existed,
  and added it to `docs/plans/README.md`.

## Unchanged behavior

No color, layout, typography, or content changes. `SuperAdminDashboard.vue` and
`SuperAdminReports.vue` were checked and already carry `.sb-card-lift` / `.sb-field` correctly —
no changes needed there.

## Verification

- `npx eslint` on every touched file — passed.
- `npm run build` — passed.
- Browser/visual pass on the new `-6px` session-card hover lift and the dark-mode halo color is
  still pending — flagged as a risk in the plan file.
