# 0012 — Typography System: Plus Jakarta Sans via Tokenized Font Stacks

## Status

Approved (2026-08-11)

_Numbered 0011 when originally drafted; renumbered to 0012 on consolidation because
`main` had independently gained its own 0011
([provisional-late-cancellation-strikes](0011-provisional-late-cancellation-strikes.md))
in the meantime. No content change, number only._

## Context

The frontend has no consistent typeface. A grep of every `font-family` declaration in `src/`
turned up four different stacks in active use:

- `'Inter', system-ui, -apple-system, sans-serif` — `main.css:215`, `LandingPage.vue:855`
- `system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif` (no Inter) —
  `base.css:67`, `AuthShell.vue:57`, `Dashboard.vue:714`, `TuteeProfile.vue:983`,
  `TutorProfile.vue:1132`, `TutorWallet.vue:729`
- `ui-monospace, Menlo, Consolas, monospace` and `ui-monospace, SFMono-Regular, Menlo, monospace` —
  two slightly different monospace stacks in `SbExportModal.vue:392` and
  `VerificationDevPanel.vue:153`
- `Georgia, 'Times New Roman', serif` — one decorative element, `LandingPage.vue:1438`

Critically, **`'Inter'` is declared in two places but never actually loaded anywhere** — there is
no `@font-face` rule, no `<link>` to a font host, and no font package in `package.json`. Every
"Inter" declaration was already silently falling back to the system font. The visible
inconsistency is a symptom of a mechanical problem: components don't share a single source of
truth for typography, so each one accumulated its own hand-typed stack over time.

`SbExportModal.vue` (monospace, xlsx-export UI) exists only on the in-progress
`feat/superadmin-report-xlsx-export` branch, not yet on `origin/main`. Anyone re-running the
`font-family` audit before implementing should do so from the branch current at that time, not
from a stale `main`.

Decision mockup: [`docs/mockups/2026-08-11-typography-system.html`](../mockups/2026-08-11-typography-system.html).

## Decision

**Typeface:** Plus Jakarta Sans, loaded system-wide as the base UI font.

**Loading mechanism:** self-hosted via `@fontsource-variable/plus-jakarta-sans` (npm package,
bundled by Vite, served same-origin) — not a Google Fonts `<link>` tag. This avoids two extra
external origins (`fonts.googleapis.com`, `fonts.gstatic.com`) and keeps the font under our own
cache control. The full variable font is loaded (weight range 200–800) rather than a static-weight
subset, so no component is ever blocked on a weight that wasn't pre-subsetted, and `font-display:
swap` is used so text renders in the fallback stack immediately rather than blocking on the font
file.

**Centralization:** a new `--sb-font-base` custom property, defined in `main.css`'s `:root` token
block alongside the existing `--sb-*` tokens (`--sb-primary`, `--sb-bg`, etc.):

```css
--sb-font-base: 'Plus Jakarta Sans', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
```

Every component's hardcoded `font-family` declaration is repointed to `var(--sb-font-base)` in the
same change (see Steps below) — this is a one-time full sweep, not a partial rollout, because a
half-migrated state is exactly the kind of drift that caused this ADR.

**Monospace exception:** a second token, `--sb-font-mono`, centralizes the two existing (slightly
different) monospace stacks used for code/data display:

```css
--sb-font-mono: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
```

`SbExportModal.vue` and `VerificationDevPanel.vue` both repoint to this token.

**Landing page exception:** `LandingPage.vue` is explicitly **out of scope** for this rollout, by
product decision (not a technical constraint) — its current look, including the `'Inter'`-declared
body font (which today silently renders as system-ui) and the decorative Georgia serif
step-numbers (`.tslab .num`, line 1438), is kept as-is. Do not add `--sb-font-base` or
`--sb-font-mono` to any rule in `LandingPage.vue` as part of this ADR.

**`font-family: inherit` declarations** (`BudgetRangeSlider.vue:161`, `TutorSubjectSetup.vue:365`,
three rules in `SubjectTaxonomyPicker.vue`) are left untouched — they already resolve through the
cascade to whatever the parent ends up being, so once the parent chain resolves to
`--sb-font-base` they follow automatically. No edit needed there.

## Consequences

- One CSS variable change (`--sb-font-base`) is now sufficient to re-theme the entire app's
  typography in the future — no more per-file hunts.
- Slightly larger initial CSS/font payload than "no webfont at all," in exchange for the app
  finally rendering the font it always intended to.
- `LandingPage.vue` will visibly diverge from the rest of the app (system-ui vs. Plus Jakarta
  Sans) until/unless a future decision brings it into the token system. This divergence is
  accepted, not accidental.
- Any new component must reference `var(--sb-font-base)` (or `var(--sb-font-mono)` for code/data
  display) rather than typing a new stack — this ADR is the reference for that expectation.

## Related

- [Rollout plan](../plans/2026-08-11-typography-system-rollout.md)
- Mockup: [`docs/mockups/2026-08-11-typography-system.html`](../mockups/2026-08-11-typography-system.html)
