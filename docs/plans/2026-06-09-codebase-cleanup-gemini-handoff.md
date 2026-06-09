# Gemini Handoff — StudyBuddy UI Codebase Cleanup Scan

## Status & Progress Summary
**Status:** Draft — ready for Gemini execution  
**Phase:** Handoff document complete. No code has been changed yet.  
**Next step:** Give this document to Gemini CLI to run the scan across `src/`. Review findings, then prioritize fixes.

---

## Context

This is a Vue 3 + Vite frontend at `C:\FIles\Studybuddy\FrontEnd\studybuddy-ui\src\`.
The goal is a full codebase scan for bloat, dead code, and repeating CSS patterns — without wasting tokens reading files you don't need to.

Two dashboards have already been manually inspected (`src/views/Dashboard.vue` and `src/views/TutorDashboard.vue`) and reveal clear patterns to hunt for across the rest of the codebase. Use those findings as the blueprint for what to look for everywhere else.

---

## Confirmed Problems (already found — do NOT re-scan these two files)

### Dead code in Dashboard.vue
- `formatTutorMeta()` (line 638) — defined but never called in the template. Delete it.
- `.weekly-session-meta` CSS class (line 1224) — no element uses it. Delete it.
- `.weekly-session-duration` CSS class (line 1234) — no element uses it. Delete it.
- CSS variables on `.dashboard-shell` (lines 710–716): `--sb-primary`, `--sb-primary-hover`, `--sb-dark` are already global. Only keep the aliases (`--sb-ink`, `--sb-muted`, `--sb-divider`) that remap global vars to local names.

### App.vue route-header chain (lines 172–267)
13 separate `<div v-if="route.path === '...'">` blocks hardcoding page titles. Replace with a `PAGE_HEADERS` computed map keyed by route path. `/tch-requestedSessions` stays special-cased (it has a live badge). Everything else collapses to one `<div>`.

### App.vue sidebar nav (lines 17–101)
~85 lines of repeated `<li>` elements, all the same shape. Replace with a `navItems` array filtered by `userRole`, rendered by one `v-for`.

### App.vue: duplicate `closeLogoutModal()` call in `logout()` (lines 407 + 412)

### Scaffold leftovers — delete immediately
These are default Vue CLI scaffolding files with zero usage:
- `src/components/HelloWorld.vue`
- `src/components/TheWelcome.vue`
- `src/components/WelcomeItem.vue`
- `src/components/icons/IconCommunity.vue`
- `src/components/icons/IconDocumentation.vue`
- `src/components/icons/IconEcosystem.vue`
- `src/components/icons/IconSupport.vue`
- `src/components/icons/IconTooling.vue`
- `src/stores/counter.js`

Verify none are imported anywhere before deleting (grep `HelloWorld`, `TheWelcome`, `WelcomeItem`, `counter` across `src/`).

---

## CSS Patterns to Hunt For (scan every `.vue` file in `src/views/` and `src/components/`)

### Pattern 1 — Duplicated panel header blocks
Both dashboards independently define `.panel-header`, `.panel-kicker`, `.panel-title`, `.panel-subtitle` with near-identical rules inside scoped `<style scoped>` blocks. Look for these class names in any other view or component. If 3+ files define them, extract a shared `panel.css` utility or add them to `src/assets/main.css`.

**What to look for:**
```css
.panel-header { display: flex; justify-content: space-between; ... }
.panel-kicker { font-size: ~0.7rem; font-weight: 700/800; text-transform: uppercase; }
.panel-title  { font-weight: 800; letter-spacing: 0; }
```

### Pattern 2 — Duplicated metric/stat card blocks
`.metric-card`, `.metric-icon`, `.metric-label`, `.metric-value` appear in both dashboards with `scoped` styles. Check `AdminDashboard.vue`, `TutorSessionsReports.vue`, `SessionsReports.vue` for the same shapes. If repeated, candidates for a shared `MetricCard.vue` component.

### Pattern 3 — Status badge / pill color system split across files
TutorDashboard.vue defines a proper `.status-badge` + modifier classes (`.status-badge-upcoming`, `.status-badge-completed`, `.status-badge-danger`, etc.).
Dashboard.vue uses `.weekly-session-card-upcoming`, `.weekly-session-card-pending`, etc. for left-border coloring.
Other views (`TuteeSessions.vue`, `TutorRequestedSessions.vue`, `TuteeSessionDetailsFlow.vue`) almost certainly define their own status coloring too.

**Goal:** Find every place status colors are defined. Consolidate into one shared set of CSS custom properties or a single `status.css` file. The token values are:
- upcoming/confirmed: `#0ea5e9` border / `rgba(13,202,240,0.12)` bg
- ongoing: `#0d6efd`
- completed: `var(--sb-primary)` (#00895a)
- pending: `#fbbf24`
- awaiting verification / payment required: `#f97316`
- rejected / cancelled: `#dc2626` / `#9ca3af`

### Pattern 4 — Glass card base style redefined per component
Dashboard.vue: `.glass-panel { border: 1px solid var(--sb-card-border); border-radius: 18px; background: color-mix(...); box-shadow: 0 8px 20px ... }`
TutorDashboard.vue: `.metric-card, .bookings-panel, .booking-card { border: 1px solid var(--dashboard-border); background: var(--dashboard-glass-strong); box-shadow: 0 10px 24px ... }`

Same concept. Check every view for a hand-rolled card base style. If this appears in 4+ files, add `.sb-card` to `main.css` and replace the local rules.

### Pattern 5 — Local CSS variable aliasing of globals
Dashboard.vue re-declares `--sb-ink: var(--sb-text-main)` etc. on `.dashboard-shell`.
TutorDashboard.vue re-declares `--dashboard-ink: var(--sb-text-main)` etc. on `.tutor-dashboard`.

This is fine when the alias adds meaning (component-scoped token), but when it's just `--foo: var(--sb-foo)` with no change, it's noise. Flag every instance where a local var is a 1:1 alias of a global with no override.

### Pattern 6 — Hardcoded magic values to CSS variables
Grep across all `<style>` blocks for:
- `border-radius: 999px` — should be `var(--sb-radius-pill)`
- `letter-spacing: 0` repeated as a reset — should be a base rule or utility
- `font-weight: 800` / `font-weight: 850` — suggest `--sb-fw-bold` / `--sb-fw-extrabold`
- `rgba(0, 137, 90, 0.1)` and variants — should be `color-mix(in srgb, var(--sb-primary) 10%, transparent)`
- Hardcoded hex `#00895a`, `#00704a` outside of `:root` — should use `var(--sb-primary)`

### Pattern 7 — Empty/loading state panels duplicated
Dashboard.vue: `.day-empty-state` (dashed border, flex column, centered, muted text)
TutorDashboard.vue: `.state-panel` (same structure)

Check all other views for a local empty-state or loading-state block. If 4+ files define their own, extract a `<SbEmptyState>` component.

### Pattern 8 — Inline `style=""` on elements
App.vue line 11: `style="width: 250px; background-color: var(--sb-dark);"` on the sidebar `<aside>`.
Grep `src/` for `style="` in templates. Flag any that are not truly dynamic (i.e. not `:style`). Static inline styles should move to CSS.

---

## Stores to audit for usage

These stores were found but may be unused or partially wired:
- `src/stores/counter.js` — scaffold leftover, almost certainly dead
- `src/stores/preferences.js` — check if imported anywhere besides `PreferenceSetup.vue`
- `src/stores/registrationinfo.js` — check if still used after registration refactors
- `src/stores/initialbookingprefs.js` — verify still active in booking flow
- `src/stores/tutorBookingDetails.js` — check vs `bookedSessionDetails.js` for overlap

For each: grep its store name (e.g. `usePreferencesStore`) across all `.vue` and `.js` files. If only one importer exists, consider inlining the state. If zero importers, delete.

---

## Services to audit

- `src/services/api/cache.js` — has a `.test.js` file, so it's tested. Still verify it's imported somewhere in the app (not just tests).
- `src/services/api/registerapi.js` — separate unauthenticated Axios instance. Confirm it's used only in `Register.vue` / `PreferenceSetup.vue` and not duplicated.

---

## Scan Method (token-efficient)

1. **Grep first, read second.** For each pattern above, grep the class name or value across `src/`. Only read the full file if grep confirms a hit.
2. **Check stores with a single grep per store**: `grep -r "useCounterStore\|usePreferencesStore\|useRegistrationStore" src/`
3. **CSS grep targets:**
   ```
   grep -r "border-radius: 999px" src/
   grep -r "letter-spacing: 0" src/
   grep -r "font-weight: 8[05]0" src/
   grep -r "#00895a\|#00704a" src/
   grep -r "panel-kicker\|panel-header\|panel-title" src/
   grep -r "status-badge\|session-card-" src/
   grep -r "state-panel\|empty-state" src/
   ```
4. **For dead CSS**: For each class found in a `<style scoped>` block, grep the class name in the same file's `<template>` block only.

---

## Output Format Expected

For each finding, report:
- **File** (relative path)
- **What** (class name, function, variable, or element)
- **Why it's bloat** (dead, duplicate, magic value, etc.)
- **Fix** (delete / extract / replace with variable / consolidate)
- **Severity**: `low` (cosmetic), `medium` (duplication), `high` (dead code / broken)

Group findings by pattern number above. At the end, give a short summary of the highest-value changes to make first.

---

## Changelog

- **2026-06-09** — Initial handoff document created. Manually inspected `Dashboard.vue` and `TutorDashboard.vue`. Identified 8 CSS patterns to scan for, confirmed scaffold leftovers, dead function, dead CSS classes, and App.vue structural bloat. Scan instructions written for token-efficient Gemini execution.
