---
title: Mode switcher redesign and scoped-style fix
date: 2026-08-20
status: Done
summary: The sidebar mode switcher renders unstyled because it is a multi-root fragment borrowing AppSidebar's scoped CSS; replace it with a self-styled segmented control above the footer and ship the confirmed accessibility fixes with it.
spec: ../mockups/2026-08-20-mode-switcher.html
---

# Mode switcher redesign and scoped-style fix

## Status & Progress Summary

**Status:** Done - all 7 steps implemented and verified.

`SbModeSwitcher.vue` is now a self-styled two-cell segmented control mounted above the sidebar
footer, with the full accessibility layer. 13 new tests pass. The full suite sits at 216 passed /
9 failed - the 9 pre-existing failures, unchanged. `tokens.test.js` reports **20** undeclared-token
violations, the baseline exactly. `npm run lint` shows only the 4 pre-existing `no-undef` errors,
`npm run build` succeeds, and the Impeccable detector reports 0 findings on the rewritten component.

Three small deviations (a removed `--sb-radius-pill` var that does not exist, a font-size moved to
`0.8rem` to clear the type ramp, and restructured test teardown for `Teleport`) are recorded in
[`docs/session-summaries/2026-08-20-mode-switcher-redesign-summary.md`](../session-summaries/2026-08-20-mode-switcher-redesign-summary.md).

Still outstanding: the control has never been seen in a browser. `/impeccable live` is the follow-up.

The root-cause question that blocked this work was resolved first. `SbModeSwitcher.vue` **rendered
unstyled** in the sidebar footer. Verified by mounting the real component inside `AppSidebar.vue` (rather than
the stub `AppSidebar.test.js` normally installs) and comparing rendered attributes:

```
LOGOUT:  <button data-v-53430c37="" type="button" class="sb-item sb-item-btn ...">
SWITCH:  <button type="button" class="sb-item ...">          <- no scope id
```

Two facts make it conclusive. First, the component's template root is `<template v-if="isSwitchable">`
wrapping a `<button>` **and** a `<Teleport>` - a multi-root fragment. Vue 3 forwards a parent's scope
id to a child's root only when `filterSingleRoot` finds exactly one root, so `data-v-53430c37` is
never applied. Second, `.sb-item`, `.sb-chip`, and `.sb-item-label` are declared **only** inside
`AppSidebar.vue`'s `<style scoped>` block and nowhere global. Every class the switcher renders is
therefore inert.

`SbThemeToggle.vue` is the control group: it has a single `<label>` root, so it correctly receives
both the `sb-footer-toggle` class and the parent scope id. The bug is specific to this one component.

Design was taken through three interactive options at both rail widths; the segmented control was
chosen. The decision artifact is
[`docs/mockups/2026-08-20-mode-switcher.html`](../mockups/2026-08-20-mode-switcher.html).

## Goal

Make the Tutor/Tutee mode switcher a real, styled, accessible control - one that shows which mode
you are in, survives the collapsed 76px rail with its meaning intact, and stops silently depending on
another component's scoped stylesheet.

## Approach

**Three decisions, in dependency order.**

### 1. The component owns its CSS

The fix is not to add a scope id. It is to stop borrowing. `SbModeSwitcher.vue` gets its own
`<style scoped>` block declaring every class it renders. Its own scope id is applied to its own
template elements regardless of root count, so the fragment can stay - and it must, because the
`Teleport` has to remain a sibling root rather than nest inside the button.

Rejected alternative: collapse to a single root by moving `v-if` onto the button and hoisting the
`Teleport` out. That would make the parent's `.sb-item` rules apply again, but it leaves the
component's appearance defined in a file that does not import it - the exact coupling that produced
this bug. A component that renders a class it does not define is the defect, not the symptom.

### 2. Form: a segmented control, above the footer

| | Current | Chosen |
| --- | --- | --- |
| What it communicates | an action ("Switch to Tutor") | a state ("you are Tutee") plus the action |
| Placement | inside `.sb-footer`, `flex: 1`, competing with Log out | above the footer divider, full width |
| Collapsed rail | a bare `bi-arrow-left-right` chip | two labelled cells, `TE` / `TR` |

Placement above the `.sb-footer` border-top leaves the footer's `justify-content: space-between` row
untouched, which fixes the Log out label clipping as a side effect rather than as extra work.

Shape and colour come entirely from the existing system: a 999px pill per DESIGN.md's
*Pill-Or-Card Rule*, filled with `--sb-primary` on the selected cell, `--sb-bg` track,
`--sb-card-border` hairline, `--sb-text-muted` on the unselected cell. No new radius, no new hue, no
literal colours - `tokens.test.js` enforces this.

Selection is a **filled cell**, not the `.sb-pill` outline convention. The outline convention exists
for independent filter pills where a fill swap would hurt label legibility; these two cells are
mutually exclusive segments, and a fill is the standard way to show which one is live.

### 3. The selected cell reflects committed state, never intent

A segmented control implies instant switching. For a user whose other mode is not provisioned, the
first activation opens the setup dialog instead. The selected cell therefore moves only when
`authStore.switchMode()` resolves - never on click. If the switch fails or the dialog is dismissed,
the control still reads the mode the user is actually in.

### 4. Accessibility, shipped with the form

These were confirmed by source inspection during the audit and are independent of which form was
chosen:

- **[P1]** The setup dialog declares `role="dialog"` and `aria-modal="true"` with no accessible name.
  Add `aria-labelledby` pointing at the `<h5 class="modal-title">` (WCAG 4.1.2).
- **[P1]** No focus management anywhere in the file: no Escape-to-close, no focus trap, focus never
  enters the dialog and is never restored to the trigger. Users can tab out of an `aria-modal`
  dialog (WCAG 2.1.2 / 2.4.3).
- **[P2]** Focus is dropped mid-switch: the trigger sets `:disabled` while `isSwitching`, and
  disabling a focused element sends focus to `<body>` exactly as the route changes. Mark the group
  `aria-busy` and ignore activations while switching instead of disabling the focused cell.
- **[P2]** The busy state is silent. Announce it rather than only swapping a label.
- **[P3]** `<i class="bi bi-arrow-left-right">` and friends lack `aria-hidden="true"`.

Plus what the new form itself requires: `role="radiogroup"` with an accessible name, `role="radio"`
cells with `aria-checked`, a single tab stop with roving `tabindex`, and Left/Right (and Up/Down when
collapsed) arrow-key movement.

### 5. Collapsed state

`SbModeSwitcher` reads `useSidebarStore()` directly for `collapsed`, consistent with how it already
reaches for `auth`, `profile`, and `toast` rather than taking props. A parent-descendant selector
(`.sb-sidebar--collapsed .sb-mode`) cannot work here - that is the same cross-component coupling this
plan exists to remove.

Collapsed, the group stacks vertically (matching `.sb-sidebar--collapsed .sb-footer`) and shows `TE`
/ `TR`. The visible text is an abbreviation only: each cell keeps the full mode name as its
accessible name and a `title` for the hover tooltip.

## Steps

1. Promote the chosen design to `docs/mockups/2026-08-20-mode-switcher.html` and save this plan.
   *(done)*
2. Rewrite `src/components/SbModeSwitcher.vue`:
   - segmented `role="radiogroup"` replacing the single button,
   - its own `<style scoped>` block using tokens only,
   - collapsed variant driven by `useSidebarStore()`,
   - roving tabindex and arrow-key handling,
   - `aria-busy` during the switch, replacing `:disabled` on the focused cell.
3. Add the dialog accessibility layer in the same file: `aria-labelledby`, Escape-to-close, focus
   trap, focus restore to the activating cell, `aria-hidden` on decorative icons.
4. Move the `<SbModeSwitcher />` mount in `src/components/AppSidebar.vue` from inside `.sb-footer` to
   just above it, after `.sb-spacer`.
5. Add `src/components/SbModeSwitcher.test.js` covering: renders nothing for a non-switchable role,
   marks the current mode checked, does not move selection until the switch resolves, opens the
   dialog for an unprovisioned target, closes on Escape, and restores focus on close.
6. Add one regression test asserting the switcher renders its own classes when mounted inside
   `AppSidebar` un-stubbed - the guard for the bug this plan fixes.
7. Run the checks below, then write the session summary and regenerate the plans index.

## Risks

- **`tokens.test.js` is an already-failing test.** Its baseline is **20 violations**. Pass/fail hides
  regressions inside it, so the violation *count* must be compared, not the status. The previous
  session added two violations here and only a review caught it.
- **The state-vs-intent rule is easy to get wrong.** An optimistic `aria-checked` flip on click would
  make the control lie whenever the target mode is unprovisioned or the request fails.
- **Focus trap plus `Teleport` plus Bootstrap's backdrop.** The component renders its own backdrop
  marked `data-sb-owned` so `clearBootstrapModalState()` does not remove it; the trap must not fight
  that, and Escape must not leave the backdrop orphaned.
- **Collapsed abbreviations.** `TE` / `TR` are a compromise. They need the accessible name and title
  to carry the real meaning, or the control regresses to the ambiguity it was chosen to avoid.
- **Baseline test noise.** `npx vitest run` has **9 pre-existing failures** and `npm run lint` has
  **4 pre-existing `no-undef` errors** in `make_algo_pptx.cjs` / `.js`. Neither count may grow.
- **Not visually confirmed in a browser.** No live end-to-end run of the dual-role switch flow has
  ever been done. `/impeccable live` against the running dev server is the follow-up, and it needs a
  dual-role login (the backend must run with `EMAIL_DELIVERY_DISABLED=true` in its process
  environment to bypass the login OTP).

## Checks to run

- `npx vitest run src/components/SbModeSwitcher.test.js` - new suite passes.
- `npx vitest run` - 9 pre-existing failures and no more.
- `npx vitest run src/assets/tokens.test.js` - **20 violations**, unchanged. Read the count, not the
  status.
- `npm run lint` - only the 4 pre-existing `no-undef` errors.
- `npm run build` - succeeds.
- Manual, in `/impeccable live`: expanded and collapsed rail, light and dark, keyboard-only pass
  through the group and the dialog.

## Changelog

- **2026-08-20** - Implemented and verified; status Approved -> Done. Summary written.

- **2026-08-20** - Plan created. Root cause confirmed by mounted-component test (multi-root fragment
  does not inherit the parent scope id); segmented control chosen from three interactive options;
  accessibility findings from the incomplete `/impeccable audit` folded into scope.
