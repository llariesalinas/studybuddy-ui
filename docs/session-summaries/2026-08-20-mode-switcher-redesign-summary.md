# Mode switcher redesign - session summary (2026-08-20)

Plan: [`docs/plans/2026-08-20-mode-switcher-redesign.md`](../plans/2026-08-20-mode-switcher-redesign.md)
Design artifact: [`docs/mockups/2026-08-20-mode-switcher.html`](../mockups/2026-08-20-mode-switcher.html)

## What shipped

All seven planned steps. `SbModeSwitcher.vue` was rewritten from a single unstyled button into a
self-styled two-cell segmented control, moved out of the sidebar footer, and given the accessibility
layer the earlier `/impeccable audit` had identified but never delivered.

| File | Change |
| --- | --- |
| `src/components/SbModeSwitcher.vue` | Rewritten: segmented `role="radiogroup"`, own `<style scoped>`, collapsed variant, roving tabindex, dialog focus management |
| `src/components/AppSidebar.vue` | Mount moved from inside `.sb-footer` to just above it (1 line) |
| `src/components/SbModeSwitcher.test.js` | New - 13 tests |
| `docs/mockups/2026-08-20-mode-switcher.html` | New - chosen design, both rail widths, light and dark |
| `docs/plans/2026-08-20-mode-switcher-redesign.md` | New |

## The root cause, confirmed

The session opened with an unresolved lead carried over from the previous handoff: the switcher
*might* be rendering unstyled. It was, and the evidence is direct. Mounting `AppSidebar` with the
real component instead of the stub `AppSidebar.test.js` normally installs:

```
LOGOUT:  <button data-v-53430c37="" type="button" class="sb-item sb-item-btn ...">
SWITCH:  <button type="button" class="sb-item ...">          <- no scope id
```

The component's template root was `<template v-if>` wrapping a `<button>` and a `<Teleport>` - a
multi-root fragment, which Vue 3 does not give the parent's scope id. `.sb-item`, `.sb-chip`, and
`.sb-item-label` are declared only inside `AppSidebar.vue`'s scoped block, so every class it rendered
was inert. `SbThemeToggle.vue` served as the control group: single `<label>` root, so it correctly
receives both the `sb-footer-toggle` class and the scope id. One component was affected, not a class
of them.

The three previous attempts to verify this from `dist/` had all failed. A mounted-component test
settled it in one run, which is worth remembering: the question was about *runtime attribute
application*, and only a runtime check could answer it.

## Deviations from the plan

Three, all small.

1. **`var(--sb-radius-pill, 999px)` was written and then removed.** No `--sb-radius-*` token exists
   anywhere in `main.css`; radii in this codebase are literals. A `var()` with a fallback would have
   worked, but reading a token that is declared nowhere is precisely the `admin.css` trap DESIGN.md
   documents. Replaced with `999px`, matching the surrounding code.
2. **Cell font-size landed at `0.8rem`, not `0.76rem`.** The Impeccable detector flagged `0.76rem` as
   off the DESIGN.md type ramp; `0.8rem` (12.8px) sits against the documented 13px label token and
   clears the check.
3. **Test teardown needed restructuring.** `document.body.innerHTML = ''` in `beforeEach` stranded
   the `Teleport` anchors of wrappers left mounted from the previous test, producing an
   `insertBefore` of null. Replaced with an `afterEach` that unmounts tracked wrappers first.

## Design decisions worth carrying forward

- **The fix was ownership, not a scope id.** Collapsing the component to a single root would also
  have made `.sb-item` apply, but it leaves the component's appearance defined in a file that does
  not import it. A component that renders a class it does not declare is the defect.
- **Selection tracks committed state, never intent.** `aria-checked` is bound to
  `authStore.user.role`, so the cell moves only after `switchMode()` resolves. A segmented control
  implies instant switching, and for an unprovisioned target the first activation opens the setup
  dialog instead - an optimistic flip would make the control lie.
- **Arrow keys move focus without selecting.** The standard radiogroup pattern selects on arrow,
  which here would switch mode and navigate the app on every keypress. Activation stays on
  Space/Enter and click, which the ARIA practices allow when selection has significant consequences.
- **The busy state is announced, not disabled.** The old control set `:disabled` while switching,
  dropping focus to `<body>` exactly as the route changed. The group is now marked `aria-busy` and
  ignores activations instead.

## Checks run

| Check | Result |
| --- | --- |
| `npx vitest run src/components/SbModeSwitcher.test.js` | **13 passed, 0 failed** |
| `npx vitest run` | 226 tests: **216 passed, 9 failed, 1 pending** - the 9 pre-existing failures, unchanged |
| `npx vitest run src/assets/tokens.test.js` | **20 undeclared-token violations** - the baseline exactly, no new ones |
| `npm run lint` | 4 errors, all pre-existing `no-undef` in `make_algo_pptx.cjs` / `.js` |
| `npm run build` | Succeeds |
| `detect.mjs` on `SbModeSwitcher.vue` | **0 findings** |

The token count is the one that mattered. It is an already-failing test, so pass/fail hides
regressions inside it; the first draft of the styles would have added a violation and the count
caught it.

## Not done

- **No browser run.** The control has never been seen rendering in a real session. `/impeccable live`
  against the running dev server (Vite is up on 5173) is the immediate follow-up, and it needs a
  dual-role login, which needs the backend started with `EMAIL_DELIVERY_DISABLED=true` in its process
  environment to bypass the login OTP.
- **The `/impeccable audit` is still incomplete.** Accessibility and Theming are characterised;
  Performance, Responsive, and Implementation Integrity remain unassessed, so there is still no
  health score.
- **Uncommitted from the previous session:** `DESIGN.md` and `.impeccable/design.json`. Still awaiting
  a decision on whether to commit them as a `docs:` change.
