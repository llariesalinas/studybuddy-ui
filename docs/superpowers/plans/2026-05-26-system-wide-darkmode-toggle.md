# Plan: System-Wide Dark Mode Toggle

**Date:** 2026-05-26
**Branch:** feature/darkmode-toggle (branch from ryan/LatestWorking)
**Spec:** Inline in this document

---

## Overview

Add a system-wide light/dark theme toggle to StudyBuddy UI. Light is the default. Theme persists
in `localStorage` and is applied via `data-sb-theme` on `<html>`. Authenticated pages get the
toggle in the sidebar footer. Public/auth pages get it in nav actions.

---

## Key Design Decisions

| Decision | Choice | Reason |
|---|---|---|
| Default theme | Light | First-visit UX; no OS preference detection |
| Persistence | Manual `localStorage` (not Pinia persisted state) | Avoids plugin dependency for one value |
| Theme attribute | `data-sb-theme="light|dark"` on `<html>` | CSS cascade; no JS needed after initial apply |
| Sidebar | Always dark (`--sb-dark: #0A1916`) | Brand identity; unchanged across themes |
| FOUC trade-off | Accepted | Returning dark users see flash; fixable via `index.html` script post-MVP |
| CSS strategy | Custom utility classes (`.sb-surface`, etc.) | No `[data-sb-theme] .bg-white` selectors |
| Toggle import | Per-component (matches codebase pattern) | Consistency |

---

## Token Spec — Dark Mode Values

These tokens are added to `main.css` under `[data-sb-theme="dark"] :root` (or directly on `[data-sb-theme="dark"]`).
All agents must use these values; do not invent values.

```css
[data-sb-theme="dark"] {
  --sb-bg:              #0f1a16;
  --sb-card-bg:         #162a20;
  --sb-card-border:     #1e3829;
  --sb-surface:         #162a20;
  --sb-text-main:       #e2ede8;
  --sb-text-muted:      #8ba89a;
  --sb-text-secondary:  #a8bdb5;
  --sb-text-dark:       #e2ede8;
  --sb-border-light:    #1e3829;
}
```

Light mode (default — these are already in `:root`, listed here for reference):
```css
/* Already in :root — do not duplicate */
--sb-bg:              #F8F9FA;
--sb-card-bg:         #ffffff;
--sb-card-border:     #EAEAEA;
--sb-surface:         #ffffff;
--sb-text-main:       #163127;
--sb-text-muted:      #6b7280;
--sb-text-secondary:  #495057;
--sb-text-dark:       #212529;
--sb-border-light:    #e0e7e3;
```

Utility classes to add (light values via CSS vars; dark inherits from `[data-sb-theme="dark"]` override):
```css
.sb-surface        { background-color: var(--sb-surface); }
.sb-text           { color: var(--sb-text-main); }
.sb-muted          { color: var(--sb-text-muted); }
.sb-card-surface   { background-color: var(--sb-card-bg); border-color: var(--sb-card-border); }
```

---

## Critical Context for All Agents

### `main.css` is currently unused / not imported
`src/assets/main.css` exists but is **not imported** in `main.js` or anywhere else.
`src/App.vue`'s global `<style>` block (no `scoped`) is the **live token source**.

**Resolution (Agent 1 task):**
1. Add `import './assets/main.css'` to `main.js` after Bootstrap CSS.
2. Migrate ALL tokens from App.vue's `<style>` `:root` block into `main.css` `:root`.
3. Remove the entire `:root` block from App.vue (keep non-root rules in App.vue).
4. `main.css` `:root` already has a partial copy — use App.vue as the authoritative source;
   App.vue has additional vars (`--sb-topbar-height`, `--sb-bell-size`, `--sb-spring`, etc.)
   that are missing from `main.css`.

### App.vue dual ownership
Agent 1 adds the sidebar footer toggle.
Agent 4 does further App.vue shell polish but **must** run after Agent 1 and read the
Agent-1-modified App.vue before making edits. Never overwrite Agent 1's sidebar toggle addition.

---

## Preflight (Main Integrator)

```bash
git status
# If clean:
git commit --allow-empty -m "Before adding system wide darkmode toggle"
# If tracked changes exist, STOP and report before proceeding.
```

Spawn workers only after baseline commit exists.

---

## Agent 1: Theme Architecture Worker

**Files owned:** `src/stores/theme.js` (new), `src/main.js`, `src/assets/main.css`, `src/App.vue`

### Step 1.1 — Create `src/stores/theme.js`

```js
import { ref } from 'vue'
import { defineStore } from 'pinia'

export const useThemeStore = defineStore('theme', () => {
  const theme = ref('light')

  function setTheme(value) {
    if (value !== 'light' && value !== 'dark') return
    theme.value = value
    document.documentElement.setAttribute('data-sb-theme', value)
    localStorage.setItem('sb-theme', value)
  }

  function toggleTheme() {
    setTheme(theme.value === 'light' ? 'dark' : 'light')
  }

  function initTheme() {
    const saved = localStorage.getItem('sb-theme')
    setTheme(saved === 'dark' ? 'dark' : 'light')
  }

  return { theme, setTheme, toggleTheme, initTheme }
})
```

**No `persist: true`** — localStorage is managed manually above.

### Step 1.2 — Migrate tokens: App.vue → main.css

In `src/assets/main.css`:
- Keep existing `:root` but **replace** it with App.vue's complete `:root` (App.vue is authoritative;
  it has vars main.css is missing: `--sb-topbar-height`, `--sb-bell-size`, `--sb-bell-gap`,
  `--sb-main-padding`, `--sb-spring`, `--sb-spring-fast`, `--sb-t-quick`, `--sb-t-normal`, `--sb-t-slow`).
- Add the dark token block from the Token Spec above.
- Add the `.sb-surface`, `.sb-text`, `.sb-muted`, `.sb-card-surface` utility classes.
- Move `body { background-color: var(--sb-bg); ... }` into `main.css`.

In `src/App.vue` `<style>` block:
- Remove the `:root { ... }` block entirely (it now lives in main.css).
- Remove the `body { ... }` block.
- Keep all other rules (`.active-nav`, `.sb-btn`, `.sb-interactive`, keyframes, etc.).

### Step 1.3 — Update `src/main.js`

```js
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'

import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap-icons/font/bootstrap-icons.css'
import './assets/main.css'    // ← ADD THIS (was missing)

const app = createApp(App)
const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)
app.use(pinia)
app.use(router)

const authStore = useAuthStore()
authStore.initializeAuth()

const themeStore = useThemeStore()
themeStore.initTheme()    // ← ADD BEFORE mount

app.mount('#app')

import 'bootstrap/dist/js/bootstrap.bundle.min.js'
```

### Step 1.4 — Add sidebar footer toggle in App.vue

In App.vue template, after `</ul>` (line ~97) and before `</aside>` (line ~98),
add the toggle with a bottom spacer:

```html
      <!-- Theme toggle in sidebar footer -->
      <div class="mt-auto pt-3 border-top border-secondary border-opacity-25">
        <SbThemeToggle />
      </div>
```

Add import at top of `<script setup>`:
```js
import SbThemeToggle from '@/components/SbThemeToggle.vue'
```

### Step 1.5 — Commit

```
git add src/stores/theme.js src/main.js src/assets/main.css src/App.vue
git commit -m "feat(theme): add theme store, migrate CSS tokens, add sidebar toggle"
```

---

## Agent 2: Toggle Component Worker

**Files owned:** `src/components/SbThemeToggle.vue` (new)

**Import strategy:** Per-component import (match codebase pattern — no global registration).

Build checkbox-based toggle. Specs:
- `aria-label="Toggle light/dark theme"`
- `:checked="themeStore.theme === 'dark'"`, `@change="themeStore.toggleTheme()"`
- Sun + cloud morph for light; crescent moon + stars for dark
- Fixed dimensions; smooth CSS transition
- `@media (prefers-reduced-motion: reduce)` → near-instant visual changes (≤1ms transitions)
- No external dependencies

```vue
<template>
  <label class="sb-theme-toggle" :aria-label="`Switch to ${themeStore.theme === 'dark' ? 'light' : 'dark'} mode`">
    <input
      type="checkbox"
      class="sb-theme-toggle__input"
      :checked="themeStore.theme === 'dark'"
      @change="themeStore.toggleTheme()"
    />
    <span class="sb-theme-toggle__track" aria-hidden="true">
      <span class="sb-theme-toggle__thumb">
        <span class="sb-theme-toggle__icon sb-theme-toggle__icon--sun">☀️</span>
        <span class="sb-theme-toggle__icon sb-theme-toggle__icon--moon">🌙</span>
      </span>
    </span>
    <span class="sb-theme-toggle__label">{{ themeStore.theme === 'dark' ? 'Dark' : 'Light' }}</span>
  </label>
</template>

<script setup>
import { useThemeStore } from '@/stores/theme'
const themeStore = useThemeStore()
</script>
```

Style the toggle with scoped CSS; implement the visual design (sky/cloud for light, moon/stars for dark).

### Step 2 — Commit

```
git add src/components/SbThemeToggle.vue
git commit -m "feat(theme): add SbThemeToggle checkbox component"
```

---

## Agent 3: Background Samples Worker

**Runs after Agent 2.**
**Files owned:** `docs/theme-previews/` (create directory + 3 HTML files)

Create the directory first, then create:
- `docs/theme-previews/aurora-glass.html` — aurora gradient bg, glass card surfaces, sidebar mock
- `docs/theme-previews/quiet-app-canvas.html` — dark green-tinted canvas, muted surfaces, clean layout
- `docs/theme-previews/full-night-sky.html` — deep navy/space bg, starfield, bright surfaces

Each sample must show:
- App background
- Mock sidebar (always dark, `#0A1916`)
- Card surfaces
- The toggle concept (can be static mockup)
- Text readability (`.sb-text-main` and `.sb-text-muted` samples)

### Step 3 — No commit needed (docs only, not shipped code)

Main Integrator opens all three samples, screenshots them, presents to user.
Default if no choice given: **Quiet App Canvas**.

---

## Agent 4: Shell + High-Traffic View Polish Worker

**Runs after Agent 1 is complete AND background choice is confirmed (default: Quiet App Canvas).**

**IMPORTANT:** Read Agent 1's modified `App.vue` and `main.css` before making any edits.
Do NOT re-add the sidebar toggle — Agent 1 already added it.

**Files owned:**
- `src/App.vue` (polish only — token-swap broken Bootstrap utilities in shell header)
- `src/views/LandingPage.vue`
- `src/components/AuthShell.vue`
- `src/views/PreferenceSetup.vue`
- `src/views/TutorPreferenceSetup.vue`
- `src/views/Dashboard.vue`
- `src/views/TutorDashboard.vue`
- `src/views/FindTutors.vue`
- `src/views/TuteeSessions.vue`
- `src/views/AdminDashboard.vue`

### Step 4.1 — App.vue shell header

In the `<main>` area's `<header>` (line ~138), replace hardcoded Bootstrap classes:
- `text-dark` → `sb-text`
- `text-muted` → `sb-muted`
- `bg-white` (if present) → `sb-surface`

Replace the inline `style="background-color: var(--sb-bg);"` on `<main>` with a CSS class.

### Step 4.2 — LandingPage.vue: nav toggle placement

The nav actions div is:
```html
<div class="sb-nav-actions">
  <button class="sb-nav-link">Log in</button>
  <button class="sb-btn-pill sb-btn-small hover-lift">Get started</button>
</div>
```

Add the toggle AFTER the "Get started" button:
```html
  <SbThemeToggle />
```

Add import: `import SbThemeToggle from '@/components/SbThemeToggle.vue'`

### Step 4.3 — AuthShell.vue: toggle placement

`AuthShell.vue` has no "nav actions" — it has a `.sb-auth-brand` link at top-left.
Add the toggle as an absolutely positioned element in the top-right of `.sb-auth-page`:

In template, after the `<a class="sb-auth-brand">` element:
```html
    <div class="sb-auth-theme-toggle">
      <SbThemeToggle />
    </div>
```

Add to `AuthShell.vue` scoped styles:
```css
.sb-auth-theme-toggle {
  position: absolute;
  top: 24px;
  right: 24px;
}
.sb-auth-page {
  position: relative; /* ensure this already exists or add it */
}
```

Add import: `import SbThemeToggle from '@/components/SbThemeToggle.vue'`

### Step 4.4 — PreferenceSetup.vue: toggle in existing navbar

`PreferenceSetup.vue` has a Bootstrap navbar:
```html
<nav class="navbar navbar-expand-lg bg-white py-3">
  <div class="container">
    <a class="navbar-brand fw-bold fs-4">StudyBuddy</a>
  </div>
</nav>
```

Add toggle to the container:
```html
<nav class="navbar navbar-expand-lg bg-white py-3">
  <div class="container d-flex justify-content-between align-items-center">
    <a class="navbar-brand fw-bold fs-4">StudyBuddy</a>
    <SbThemeToggle />
  </div>
</nav>
```

### Step 4.5 — TutorPreferenceSetup.vue: no existing navbar — create minimal bar

`TutorPreferenceSetup.vue` has **no navbar** — opens with `<div class="min-vh-100 bg-light py-5">`.
Add a minimal top bar:

```html
<template>
  <div class="min-vh-100 py-5" style="background-color: var(--sb-bg);">
    <div class="container-fluid px-4 mb-3 d-flex justify-content-between align-items-center">
      <span class="fw-bold">StudyBuddy</span>
      <SbThemeToggle />
    </div>
    <!-- existing container content unchanged -->
```

### Step 4.6 — Dashboard.vue, TutorDashboard.vue

Replace Bootstrap light utilities on card surfaces, table surfaces, filter pills, sticky headers:
- `bg-white` → add `sb-surface` class
- `text-dark` → `sb-text`
- `text-muted` → `sb-muted`
- Inline `style="background: #fff"` → inline `style="background: var(--sb-card-bg)"` or `sb-surface`

Do NOT touch status badge colors (`.text-success`, `.text-danger` etc.) — semantic colors are preserved.

### Step 4.7 — FindTutors.vue, TuteeSessions.vue, AdminDashboard.vue

Same token-swap strategy as Step 4.6. Focus on:
- Table surfaces and header rows
- Filter/search pill backgrounds
- Sticky headers
- Empty-state cards

### Step 4.8 — Commit

```
git add src/App.vue src/views/LandingPage.vue src/components/AuthShell.vue \
        src/views/PreferenceSetup.vue src/views/TutorPreferenceSetup.vue \
        src/views/Dashboard.vue src/views/TutorDashboard.vue \
        src/views/FindTutors.vue src/views/TuteeSessions.vue src/views/AdminDashboard.vue
git commit -m "feat(theme): apply dark-mode tokens across shell and high-traffic views"
```

---

## Post-MVP Note: FOUC Fix

Returning dark-mode users will briefly see light mode before JS initializes (`initTheme()` runs
after the bundle loads). To eliminate this, add an inline script to `index.html`:

```html
<script>
  (function(){
    var t = localStorage.getItem('sb-theme');
    document.documentElement.setAttribute('data-sb-theme', t === 'dark' ? 'dark' : 'light');
  })();
</script>
```

This is out of scope for the current plan but should be done before public launch.

---

## Implementation Rules (Carry Through All Agents)

- Do NOT use selectors like `[data-sb-theme="dark"] .bg-white` — use custom classes.
- Use the token spec table above for all dark values — do not invent values.
- Sidebar (`--sb-dark: #0A1916`) is always dark — unchanged across themes.
- Do not sweep pages not listed above; fix only the shell and listed high-traffic routes.
- `pinia-plugin-persistedstate` is installed but must NOT be used for the theme store.
- Per-component imports for `SbThemeToggle`.

---

## Test Plan

**Build check:**
```bash
npm run build  # must pass with 0 errors
```

**Manual verification:**
| Check | Steps |
|---|---|
| Fresh browser → light | Clear localStorage, hard reload `/` |
| Dark persists after reload | Toggle dark, reload — must stay dark |
| Light persists after reload | Toggle light, reload — must stay light |
| Sidebar toggle visible | Log in, check bottom of sidebar |
| Public toggle visible | Open `/`, check nav |
| Auth toggle visible | Open `/login`, check top-right |
| No header/sidebar overlap | Resize to ≤768px |
| Reduced motion | `@media (prefers-reduced-motion: reduce)` active → animation near-instant |

**Pages to browser-check in both themes:**
`/`, `/login`, `/register`, `/preferencesetup`, `/tutor-setup`,
`/dashboard`, `/tch-dashboard`, `/find-tutors`, `/tuteeSessions`, `/admin/dashboard`
