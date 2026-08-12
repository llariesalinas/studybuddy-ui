---
title: Authenticated view styling consistency (light mode)
date: 2026-08-11
status: Approved
spec: ../../StudyBuddyDesign.md
---

# Authenticated view styling consistency (light mode)

## Goal

Collapse three competing design systems into one, so the next feature inherits consistency instead
of re-forking it. Dark mode is explicitly deferred and recorded as a known gap.

## Approach

The app has a design system three times over and none of them agree:

- `src/assets/main.css` is the only stylesheet actually loaded (`src/main.js:14`) — 63 `--sb-*`
  tokens in `:root`.
- `src/assets/admin.css` and `src/assets/base.css` are **imported nowhere**. `admin.css` declares a
  rival `:root` whose `.sb-glass-card` / `.sb-table` / `.sb-badge` resolve to nothing.
- `StudyBuddyDesign.md` is the canonical design doc, and it documents `admin.css`. It mandates
  `SbStepBar.vue` (deleted 2026-07-07) and governs `--sb-aurora-bg`, which has never existed in
  `src/`.

Anyone writing new UI against the design doc reaches for tokens that resolve to `unset`. That is the
root cause of the drift, not carelessness. The result is 23 button vocabularies, 9 modal shells, 32
`.empty-state` sites defined in 11 independent scoped blocks, 9 page-container idioms, and
byte-identical CSS blocks copy-pasted across files with comments acknowledging the duplication.

**Dark mode is out of scope.** Work targets the default light theme only. This removes roughly half
of the original Stage 1 and shifts the effort onto structural de-forking, which is theme-agnostic.
Where a change makes dark mode work for free later at no light-mode cost it is taken; where it would
only help dark mode it is deferred and listed in `StudyBuddyDesign.md`'s new "Dark mode: known gaps"
section and in a skipped test.

Three standing decisions:

- **Delete `admin.css` and `base.css`** — do not wire `admin.css` up; its `:root` would clobber
  `--sb-primary` / `--sb-danger` / `--sb-surface` app-wide and its `.sb-badge` collides with a scoped
  `.sb-badge` owned by four `src/components/algorithm-demo/*.vue`. Port the good ideas first, then
  delete. `base.css` is unmodified `create-vue` scaffold whose `* { margin: 0; font-weight: normal }`
  would flatten Bootstrap typography.
- **Drop the `Inter` reference.** It appears only at `main.css:237` and in dead `base.css` — no
  `@font-face`, no link tag, no dependency, so removing it is provably zero-pixel. Add
  `--sb-font-body` holding the system stack four views already hardcode.
- **Build `SbEmptyState` only** — not `SbModal` (the nine shells share only a backdrop and a rounded
  surface) and not `SbPageContainer` (a `.sb-page` class plus one `App.vue` edit does the same
  without 30 imports).

## Steps

**Stage 0 — revertible baseline.** Verify green, commit the pre-existing working tree, branch to
`refactor/styling-consistency`, one commit per numbered stage from there.

**Stage 1 — one token layer, no shadowing.** Mostly zero-pixel in light mode; it removes redundancy
rather than restyling.

1. Add semantic ramps to `:root` — `--sb-{success,warning,danger,info}` × `{,-fg,-surface,-border}`,
   light values only. Direct fix for the 8-red / 6-amber spread. Also `--sb-skeleton-bg`,
   `--sb-font-body`. Mark `--sb-warning-bg` / `--sb-warning-text` / `--sb-danger-bs` legacy.
2. Promote `--sb-green-tint` / `--sb-green-border` to `:root` using the `color-mix()` formulas
   already at `TuteeProfile.vue:976`; delete the five local copies.
3. Delete the five re-pinned tokens at `Dashboard.vue:700-707` (all are the `:root` light values
   verbatim → zero-pixel), the no-op `--sb-dark` in both profile shells, and the four redundant
   `font-family` declarations.
4. `TutorSchedule.vue:1076` — `--sb-pill-outline-color: #b42318` → `var(--sb-danger-fg)`.
5. De-fork `--wallet-*` (`TutorWallet.vue:716`) onto the ramp, keeping the private namespace.
6. `.sb-skeleton` (`main.css:549`) → `var(--sb-skeleton-bg)`. Zero consumers, so free.
7. Tokenize the four colour-token-free components: `VerificationBanner`, `OngoingBookingBar`,
   `RatingStackModal` (frozen class — token swaps only), `NotificationBell`. `NotificationBell` must
   ship with `App.vue`'s `.chat-icon-btn` or the header pair mismatches.
8. Correct `StudyBuddyDesign.md` and `AGENTS.md:32-33`'s stale "no frontend test script" claim.
9. `src/assets/tokens.test.js` — static analysis making steps 2–3 permanent.

**Stage 2 — de-fork the heaviest duplicate pairs.**

1. Profile button tiers → the canonical tier at `main.css:390-449`, adding `.sb-btn-on-brand-ghost`
   and `.sb-btn-quiet`. Deletes `TuteeProfile.vue:1138-1190` + `:1716` and **all four** TutorProfile
   fork regions (`:1283`, `:1885`, `:2024`, `:2207`).
2. Delete the two scoped `.glass-segment` copies — byte-identical to the global, so zero-pixel.
3. Promote the 10 duplicated admin-dashboard rule blocks to `main.css` under `sb-` prefixes; resolve
   the forked `.action-button` by deleting the name.
4. Tests: `data-test` attributes during migration + `TuteeProfile.test.js`.

**Stage 3 — shared primitives and remaining views.** Split `main.css` into `src/styles/` as a pure
move first; one global `.table` theme; `SbEmptyState.vue`; additive modal-shell classes; page-shell
padding sweep; `App.vue` page headers → route meta.

## Risks

- **Stage 2 button migration** — TuteeProfile and TutorProfile have already diverged (`font-weight`
  850 vs 800; only Tutee carries `min-height:42px` + pill radius). Adopting the canonical tier gives
  TutorProfile a visible restyle on the busiest page in the tutor app.
- **The frozen class set (20 classes)** keyed by the density block at `main.css:91-179`. Renaming one
  or removing the element carrying it silently stops a compensation rule matching, with no error.
  `density.test.js` in Stage 3 is the tripwire.
- **No `vh`/`vw`/`dvh`/`svh` in new CSS** — root `zoom` does not rescale viewport units, which is why
  those ~17 compensation rules exist. Never touch `--sb-density-scale`; `CampusLocationModal.vue:94`
  reads it and divides measured rect coordinates by it.
- **`src/App.vue`'s `<style>` block is unscoped** — edits there are global.
- Promoting `--sb-green-tint` to the derived `color-mix()` form is a small but real colour shift on
  the sidebar active item, auth card and dashboard (three files hardcode `#edf7f3`).
- jsdom does not apply SFC `<style>` blocks, so no test can assert a computed colour. Every test here
  is a class-contract assertion or static analysis of CSS text; the visual gate is manual.

## Checks to run

```
npm run test && npm run build && npm run lint:eslint && npm run format
```

`npm run build` is what proves nothing imported the deleted `admin.css` / `base.css`. `lint:eslint`
uses `--cache`; clear it after large edits.

Manual browser matrix at the end of each stage, via `preview_start` on the `studybuddy-ui` config in
`.claude/launch.json`. All cells light theme (dark deferred): tutee/compact, admin/comfortable (the
only 100% role, so it isolates density bugs), superadmin/compact, tutor/compact. Per cell: open one
modal from each compensated family and confirm no clipping or scroll trap, confirm `.modal-backdrop`
covers the full viewport at compact, open `CampusLocationModal` from a booking flow at compact and
confirm it centres on its anchor, scan tables for readable text. Finally screenshot Dashboard at
compact vs comfortable — compact must be an exact 0.8× scale, not a reflow.
