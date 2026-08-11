---
title: Typography system rollout (Plus Jakarta Sans)
date: 2026-08-11
status: In Progress
summary: Load Plus Jakarta Sans via @fontsource, add --sb-font-base/--sb-font-mono tokens, repoint every hardcoded font-family in the authenticated app to them. Landing page excluded by decision.
spec: ../adr/0012-typography-system.md
---

# Typography system rollout (Plus Jakarta Sans)

## Status & Progress Summary

**2026-08-12 — Implemented on `feat/typography-system-rollout`; visual verification still
pending.** Grilled end-to-end via `/grill-with-docs` + `ui-preview` (font-comparison and
before/after mockups): typeface settled on Plus Jakarta Sans, loaded self-hosted via
`@fontsource-variable/plus-jakarta-sans` rather than a Google Fonts `<link>`, full variable weight
range, centralized behind two new tokens (`--sb-font-base`, `--sb-font-mono`). Root cause confirmed
by codebase audit: `'Inter'` was declared in two places but never actually loaded (no `@font-face`,
no link tag, no package), silently falling back to system fonts the whole time. Landing page
excluded from scope entirely by explicit product decision (user likes it as-is), not a technical
constraint. Recorded as [ADR-0012](../adr/0012-typography-system.md) (renumbered from 0011 on
consolidation — see Changelog). All 14 steps applied, including Step 6
(`SbExportModal.vue`) since this branch is based on `feat/superadmin-report-xlsx-export`, where
that file exists. `npm run build` and `npm run lint` pass. Remaining: the plan's Checks-to-run item
4 (manual visual confirmation in a running app) has not been done.

## Goal

Fix the app's inconsistent typography by actually loading a font instead of declaring one that
silently falls back, and by centralizing the font-family into one CSS token so it can never drift
file-by-file again. Full decision record: [ADR-0012](../adr/0012-typography-system.md). Decision
mockup: [`docs/mockups/2026-08-11-typography-system.html`](../mockups/2026-08-11-typography-system.html).

## Approach

1. Install `@fontsource-variable/plus-jakarta-sans` and import it once in `src/main.js`.
2. Add two new tokens to `main.css`'s `:root` block: `--sb-font-base` (Plus Jakarta Sans) and
   `--sb-font-mono` (centralizing the existing monospace stacks).
3. Repoint every hardcoded `font-family` declaration in the authenticated app to one of those two
   tokens, in the same change — this is a one-time full sweep, not a partial migration.
4. Leave `LandingPage.vue` completely untouched (both its body font-family and its Georgia
   decorative accent) — this is a product decision, not an oversight. Do not add either new token
   there.
5. Leave every `font-family: inherit;` declaration untouched — it already resolves through the
   cascade automatically once the parent picks up `--sb-font-base`.

This is a purely mechanical, low-risk CSS change: no logic, no markup structure, no component
behavior changes anywhere.

## Steps

Follow these in order. **Re-verify each `old_string` against the live file with Read before
editing** — line numbers below are a locator, not a guarantee; if a file has changed since this
plan was written, the surrounding code (imports, other properties) is the reliable anchor, not the
line number.

### Step 0 — Confirm which branch you're on

Run `git branch --show-current`. `SbExportModal.vue` (Step 6 below) only exists on
`feat/superadmin-report-xlsx-export` (or a branch that has merged it) — it does not exist on
`origin/main`. If `src/components/SbExportModal.vue` does not exist in your checkout, skip Step 6
entirely; do not create the file or fail the plan over it.

### Step 1 — Install the font package

```bash
npm install @fontsource-variable/plus-jakarta-sans
```

Confirm it landed in `package.json` under `dependencies` (not `devDependencies`) and that
`package-lock.json` changed.

### Step 2 — Import the font in `src/main.js`

Read `src/main.js` first. Find this block near the top:

```js
// 1. Import Bootstrap CSS
import 'bootstrap/dist/css/bootstrap.min.css'
// 2. Import Bootstrap Icons
import 'bootstrap-icons/font/bootstrap-icons.css'
import './assets/main.css'
```

Replace it with:

```js
// 1. Import Bootstrap CSS
import 'bootstrap/dist/css/bootstrap.min.css'
// 2. Import Bootstrap Icons
import 'bootstrap-icons/font/bootstrap-icons.css'
// 3. Import Plus Jakarta Sans (variable font, full weight range) — see ADR-0012
import '@fontsource-variable/plus-jakarta-sans'
import './assets/main.css'
```

(The font import must come before `./assets/main.css` so the `--sb-font-base` token that
references it is available once app styles apply, though CSS custom properties don't strictly
require import order — keep this order anyway for readability: framework CSS, then font, then app
CSS.)

### Step 3 — Add the two tokens to `src/assets/main.css`

Read `src/assets/main.css` first. In the `:root { ... }` block, find this line (near the end of
the block, right before `--sb-density-scale: 1;`):

```css
  --sb-shadow-hover-brand: 0 14px 30px rgba(0, 137, 90, 0.28);
  --sb-density-scale: 1;
}
```

Replace it with:

```css
  --sb-shadow-hover-brand: 0 14px 30px rgba(0, 137, 90, 0.28);
  --sb-density-scale: 1;
  /* Typography system — see ADR-0012 */
  --sb-font-base: 'Plus Jakarta Sans', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --sb-font-mono: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
}
```

These tokens do **not** need a `[data-sb-theme="dark"]` override — font-family doesn't vary by
theme in this app.

### Step 4 — Repoint `main.css`'s own body rule

Still in `src/assets/main.css`, find:

```css
body {
  background: var(--sb-bg);
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
}
```

Replace with:

```css
body {
  background: var(--sb-bg);
  font-family: var(--sb-font-base);
}
```

### Step 5 — Repoint `src/assets/base.css`

Read `src/assets/base.css` first, locate the `body { ... font-family: Inter, ... }` rule around
line 61-77 (it spans multiple lines with each fallback on its own line). Replace the entire
`font-family:` block (from `font-family:` through the closing `;` of its value list) with:

```css
  font-family: var(--sb-font-base);
```

Keep every other property in that `body` rule (`min-height`, `color`, `background`, `transition`,
`line-height`) unchanged.

### Step 6 — `src/components/SbExportModal.vue` (skip if the file doesn't exist — see Step 0)

Find:

```css
  font-family: ui-monospace, Menlo, Consolas, monospace;
```

Replace with:

```css
  font-family: var(--sb-font-mono);
```

### Step 7 — `src/components/VerificationDevPanel.vue`

Find:

```css
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
```

Replace with:

```css
  font-family: var(--sb-font-mono);
```

### Step 8 — `src/components/AuthShell.vue`

Find:

```css
  font-family:
    system-ui,
    -apple-system,
    BlinkMacSystemFont,
    'Segoe UI',
    sans-serif;
```

Replace with:

```css
  font-family: var(--sb-font-base);
```

### Step 9 — `src/views/Dashboard.vue`

Find:

```css
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
```

(This line sits inside the `.dashboard-shell` or equivalent root rule — confirm by reading the
surrounding block, it's the only `font-family` declaration in this file.) Replace with:

```css
  font-family: var(--sb-font-base);
```

Leave the separate `font-family: inherit;` rule later in this file (around line 871) untouched.

### Step 10 — `src/views/TuteeProfile.vue`

Find:

```css
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
```

Replace with:

```css
  font-family: var(--sb-font-base);
```

### Step 11 — `src/views/TutorProfile.vue`

Find:

```css
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
```

Replace with:

```css
  font-family: var(--sb-font-base);
```

### Step 12 — `src/views/TutorWallet.vue`

Find (inside `.wallet-shell`):

```css
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
```

Replace with:

```css
  font-family: var(--sb-font-base);
```

### Step 13 — Explicitly do NOT touch these

Confirm (do not edit) that the following are still exactly as they were before this plan:

- `src/views/LandingPage.vue` — both the `.studio-landing { font-family: 'Inter', ... }` rule and
  the `.tslab .num { font-family: Georgia, ... }` rule. Zero changes to this file.
- `src/components/BudgetRangeSlider.vue:161`, `src/views/TutorSubjectSetup.vue:365`, and the three
  `font-family: inherit;` occurrences in `src/components/SubjectTaxonomyPicker.vue` — leave as
  `inherit`, do not repoint to a token.

### Step 14 — Final sweep check

Run this to confirm no stray hardcoded stacks were missed or wrongly left behind outside the
declared exceptions:

```bash
grep -rn "font-family" src/ --include="*.vue" --include="*.css"
```

Expected output after this plan: every result is either `var(--sb-font-base)`,
`var(--sb-font-mono)`, `inherit`, or inside `LandingPage.vue` (the two untouched exceptions). If
anything else shows up, it was missed — fix it before moving on.

## Risks

- **Line numbers drift.** Anchor edits on the surrounding code shown above, not on line numbers,
  in case other work has touched these files since this plan was written.
- **`SbExportModal.vue` branch-conditional.** Confirmed not to exist on `origin/main` as of
  2026-08-11 — only on `feat/superadmin-report-xlsx-export`. Step 0 handles this; do not treat a
  missing file as a failure.
- **Visual divergence from the landing page is intentional**, not a bug to "fix" by extending the
  sweep there — Step 13 exists specifically to prevent an executor from "helpfully" including it.
- **FOUT (flash of unstyled text) is expected and acceptable** — `@fontsource` variable font
  imports use `font-display: swap` by default, so text renders in the fallback stack first and
  swaps to Plus Jakarta Sans once loaded. This is not a regression to fix.

## Checks to run

1. `npm run build` — must succeed with no errors.
2. `npm run lint` — must pass (oxlint + ESLint, both with `--fix`).
3. `grep -rn "font-family" src/ --include="*.vue" --include="*.css"` — output must match Step 14's
   expected result exactly (only `var(--sb-font-base)`, `var(--sb-font-mono)`, `inherit`, or
   `LandingPage.vue` matches remain).
4. `npm run dev`, then visually confirm in the browser: Dashboard, a Tutor profile page, the
   Tutor Wallet page, and an auth screen (`/login`) all render in Plus Jakarta Sans; the landing
   page (`/`) is visually unchanged from before this plan.

## Changelog

- **2026-08-11** — Plan created and approved. Grilled to 8 decisions (new ADR vs. update, typeface,
  loading mechanism, weight range, token location, mono exception, landing-page scope, rollout
  atomicity) via `/grill-with-docs`, confirmed against two `ui-preview` mockup rounds. Recorded as
  [ADR-0012](../adr/0012-typography-system.md). Not yet implemented.
- **2026-08-12** — Implemented Steps 0–14 on `feat/typography-system-rollout`, based on
  `feat/superadmin-report-xlsx-export` so `SbExportModal.vue` (Step 6) is included rather than
  skipped. ADR renumbered 0011 → 0012 during consolidation (`main` had independently gained its
  own 0011, `provisional-late-cancellation-strikes`, in the meantime — no content change, number
  only). `npm run build` and `npm run lint` both pass (the 4 lint errors reported are pre-existing
  `no-undef` issues in `make_algo_pptx.cjs`/`.js`, unrelated to this change, confirmed present
  before it too). This branch supersedes and consolidates three earlier working branches:
  `worktree-typography-adr` (docs only), `worktree-typography-rollout` (code without
  `SbExportModal.vue`), and `fix/sbexportmodal-typography-token` (a temporary standalone fix with
  a duplicate `--sb-font-mono` definition, no longer needed here). Still open: Checks-to-run item 4
  (visual browser confirmation) has not been done yet.
