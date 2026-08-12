---
title: Logo watermark in sidebar brand badge
date: 2026-08-12
status: Done
summary: Replace the sidebar's generic book-icon brand badge with the real StudyBuddy logo at full opacity.
spec: ../mockups/2026-08-12-logo-watermark.html
---

# Logo watermark in sidebar brand badge

## Status & Progress Summary

**Status:** Done — implemented, built successfully, not yet committed.
**Tasks complete:** 2 / 2 (design decided via `/ui-preview`; sidebar badge implemented and verified with `npm run build`)
**Next:** Commit the change (asset + `AppSidebar.vue`) and write the session summary.

## Goal

Reinforce the StudyBuddy brand by showing the real logo somewhere persistent in the
authenticated app shell.

## Approach

Two design directions were explored via `/ui-preview`:

1. **Fixed-position watermark** — a low-opacity (6-12%) logo pinned to the top-left
   corner of the main content area, independent of the sidebar. Rejected: it read as
   a decorative background wash, not a brand label, and looked disconnected from the
   sidebar's existing brand row.
2. **Sidebar brand badge (chosen)** — the logo replaces the existing green "S" /
   book-icon badge in `AppSidebar.vue`'s brand row, sitting directly next to the
   "StudyBuddy" wordmark at full opacity, exactly like a normal logo mark. Two sizes
   were compared (34px matching the old badge, 40px for more presence); 40px won.

The logo asset itself changed mid-session: the original `Logo-2d.svg` (a traced
vector path, recolorable via CSS fill) was swapped for `ribbon_S_logo(1) (1).svg`
(an SVG wrapper around an embedded raster PNG with Adobe content-credentials
metadata — not recolorable, ships at its own baked-in color). The final
implementation uses the ribbon logo as-is.

## Steps

1. Copy `ribbon_S_logo(1) (1).svg` to `src/assets/logos/studybuddy-logo.svg`.
2. In `AppSidebar.vue`, replace `<i class="bi bi-book"></i>` inside `.sb-brand-badge`
   with `<img src="@/assets/logos/studybuddy-logo.svg" alt="" class="sb-brand-logo" />`.
3. Resize `.sb-brand-badge` from 34px to 40px, drop the gradient background (the
   logo carries its own color), add `.sb-brand-logo { object-fit: contain }`.
4. No changes needed to `App.vue` — the fixed-watermark approach explored earlier
   was fully reverted.

## Risks

- The ribbon SVG is ~1.4MB (raster PNG + C2PA metadata wrapper), far heavier than a
  typical icon asset. Worth re-exporting as an optimized SVG/PNG before this ships
  broadly — flagged to the user, not blocking for now.
- Collapsed sidebar hides `.sb-brand-badge` entirely (pre-existing `display: none`
  rule) — matches the prior icon's behavior, not a regression, but the logo won't be
  visible when the sidebar is collapsed.

## Checks to run

- `npm run build` — passed (10.43s, no errors).
- `npm run lint` — pre-existing failures only in unrelated `make_algo_pptx.*` files;
  no new lint issues from this change.

## Changelog

- **2026-08-12** — Session picked up from a handoff doc. Explored a fixed-position
  watermark (App.vue, top-left, 3 opacity/size options) via `/ui-preview`, live-tested
  Option B in the actual running app in a worktree. User redirected the design toward
  a sidebar brand-badge label instead of a watermark; killed the dev server and
  returned to `/ui-preview` for the pivot. Compared 34px vs 40px badge sizes in
  context; user picked 40px. Implemented in `AppSidebar.vue`, reverted the earlier
  `App.vue` watermark changes, verified with `npm run build`. Plan file created and
  set to Done; mockup promoted to `docs/mockups/2026-08-12-logo-watermark.html`.
