# Logo watermark — session summary

**Plan:** [`docs/plans/2026-08-12-logo-watermark.md`](../plans/2026-08-12-logo-watermark.md)
**Mockup:** [`docs/mockups/2026-08-12-logo-watermark.html`](../mockups/2026-08-12-logo-watermark.html)

## What shipped

The StudyBuddy logo now appears in the sidebar's brand row (`AppSidebar.vue`), replacing the
generic book-icon badge — full opacity, 40×40px, right next to the "StudyBuddy" wordmark.

- `src/assets/logos/studybuddy-logo.svg` — new asset (`ribbon_S_logo(1) (1).svg`, provided by the
  user mid-session)
- `src/components/AppSidebar.vue` — `.sb-brand-badge` now renders `<img>` instead of `<i class="bi
  bi-book">`; resized 34px → 40px; dropped the gradient background (the logo is self-colored);
  added `.sb-brand-logo { object-fit: contain }`

## Deviation from the original plan

The handoff plan called for a **fixed-position, low-opacity watermark** pinned to the top-left of
the main content area (`App.vue`), with three size/opacity options (A/B/C). That direction was
fully explored and even live-tested in the running app (Option B: 64px, 10%/7% opacity) — but the
user redirected mid-session: they wanted the logo as a **full-opacity label in the sidebar**, not
a faded background watermark. The `App.vue` fixed-watermark code was written, tested live, then
reverted entirely. The final shipped design is the sidebar brand-badge approach only.

The logo asset itself also changed: the original `Logo-2d.svg` (traced vector path, recolored to
teal `#00895A` via CSS fill) was swapped for `ribbon_S_logo(1) (1).svg` at the user's request. This
second file is structurally different — an SVG wrapper around an embedded raster PNG with Adobe
content-credentials (C2PA) metadata — so it ships at its own baked-in color and can't be
recolored via CSS. It's also much heavier (~1.4MB vs ~44KB for the original).

## Checks run

- `npm run build` — passed, 10.43s, no errors.
- `npm run lint` — 4 pre-existing errors, all in unrelated `make_algo_pptx.cjs`/`.js` files; no
  new issues introduced by this change.

## Not done / flagged, not blocking

- The ribbon logo asset (~1.4MB) is heavy for a UI icon. Worth re-exporting as an optimized
  SVG/PNG before this ships broadly.
- When the sidebar is collapsed, `.sb-brand-badge` is hidden entirely (pre-existing `display:
  none` rule, unchanged) — the logo won't be visible in collapsed state. This matches the prior
  icon's behavior, not a regression, but wasn't explicitly re-confirmed with the user.
