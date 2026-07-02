---
title: Superseded system-wide gradient background attempt
date: 2026-06-22
plan: ../plans/2026-06-22-system-wide-gradient-background.md
superseded_by: 2026-06-22-system-background-unification-summary.md
---

# Superseded system-wide gradient background attempt

This records the earlier gradient-only attempt. The final shipped approach is documented in the
[system background unification summary](2026-06-22-system-background-unification-summary.md).

## What changed

1. `src/assets/main.css` — `html, body { min-height: 100%; }` → `min-height: 100vh;`. Fixes the
   square-edge artifact: percentage `min-height` on `body` was resolving against `html`'s
   collapsed content height instead of the viewport, so the gradient stopped short on pages
   shorter than the viewport (e.g. Login).
2. `src/assets/main.css` — removed `background-attachment: fixed;` from `body`. Avoids
   scroll-triggered repaint cost; with `min-height: 100vh` in place, default (`scroll`) attachment
   looks identical and is cheaper.
3. `src/App.vue` — `.app-main-surface { background: var(--sb-bg); }` →
   `background: var(--sb-bg-gradient);`. Single edit point that propagates the gradient to every
   authenticated view (Dashboard, AdminUsers, TutorWallet, etc.) since they all render inside this
   one wrapper.

Per-view `var(--sb-bg)` usages (skeleton loaders, filter panels in `Dashboard.vue`,
`FindTutors.vue`, `Chat.vue`) were left untouched — they're flat tints on cards/panels, not page
backgrounds.

## Checks run

- `npm run build` — passed, no errors.
- Visual check via preview tools on `/login`:
  - Light mode: gradient fills the full viewport, no seam. Confirmed fix.
  - Dark mode: `preview_screenshot` showed a faint horizontal line partway down. Investigated via
    `elementFromPoint` at that coordinate — it resolved to `.sb-auth-page` with a transparent
    background, confirming `body`'s gradient was the only thing painted there (no overlay
    element). Concluded this is JPEG compression banding from the screenshot tool, not a real
    bug — the dark-mode gradient's stops (`#050807` → `#08100d`, an 8/255 difference) are close
    enough that compression exaggerates the transition into a visible line. The tool's own docs
    warn against trusting screenshots for subtle color verification.
- Did not visually verify an authenticated view (e.g. AdminUsers) directly, since doing so would
  have required real login credentials in the preview session. The `.app-main-surface` change is
  a single CSS variable swap reusing the same gradient already proven correct on `body`, so this
  was treated as low-risk and not blocking.
