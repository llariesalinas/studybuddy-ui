# Sidebar Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the plain dark sidebar in `App.vue` with a polished, theme-adaptive `AppSidebar.vue` component (Indicator-Rail structure, Aurora-Light skin matched to the Dashboard) that adds a profile block, grouped sections, a pinned footer, and a persisted collapse-to-icon-rail toggle.

**Architecture:** Extract the sidebar from `App.vue` into a token-driven `AppSidebar.vue` that reads the auth + sidebar stores and emits `@logout`/`@open-support` so `App.vue` keeps owning the modals. Collapse state lives in a new `stores/sidebar.js` Pinia store persisted to `localStorage` (mirroring `stores/theme.js`), initialized in `main.js`.

**Tech Stack:** Vue 3 (`<script setup>`), Pinia, Vue Router, Bootstrap 5 + Bootstrap Icons, Vitest + `@vue/test-utils` (jsdom).

## Status & Progress Summary

- **Status:** Approved — not started.
- **Branch:** `feature-sidebar-redesign` (spec committed `105491b`).
- **Spec:** `docs/specs/2026-06-21-sidebar-redesign-design.md`.
- **Progress:** 0/4 tasks complete.
  - [ ] Task 1 — Sidebar collapse store
  - [ ] Task 2 — Initialize store at startup
  - [ ] Task 3 — AppSidebar.vue component
  - [ ] Task 4 — Wire AppSidebar into App.vue

## Global Constraints

- Frontend style: 2-space indent, single quotes, no semicolons, 100-char lines (Prettier).
- No hardcoded hex colors in component logic — use CSS custom properties (`--sb-*`). Local
  green-tint vars are defined once on the component root (the `Dashboard.vue` pattern), not inlined.
- Do not modify `src/assets/main.css`.
- Role visibility logic is unchanged from the current `App.vue` sidebar (tutee / tutor / admin /
  superadmin). This is a restyle + regroup only.
- Theme attribute is `data-sb-theme` on `<html>`; dark overrides use `[data-sb-theme="dark"] …`.
- Icons are Bootstrap Icons (`bi bi-*`).
- Baseline checks: `npm run lint` and `npm run build` must pass. Vitest for store/component tests.
- Commits: conventional prefixes, imperative subject, no `--no-verify`, no AI signature/co-author
  trailers.

---

## File Structure

- **Create** `src/stores/sidebar.js` — collapse state store (`collapsed`, `toggle`, `setCollapsed`,
  `initSidebar`), persisted to `localStorage['sb-sidebar-collapsed']`.
- **Create** `src/stores/sidebar.test.js` — unit tests for the store.
- **Create** `src/components/AppSidebar.vue` — the full sidebar UI (brand, collapse toggle, profile,
  Menu/Support sections, footer). Props: none. Emits: `logout`, `open-support`.
- **Create** `src/components/AppSidebar.test.js` — behavioral tests (role rendering, collapse class,
  emitted events).
- **Modify** `src/main.js` — call `useSidebarStore().initSidebar()` next to the theme init.
- **Modify** `src/App.vue` — replace the `<aside class="sidebar">…</aside>` block with
  `<AppSidebar @logout="openLogoutModal" @open-support="() => openSupport('Other')" />`; remove the
  sidebar-only CSS (`.active-nav`, `.nav-link:hover`) now living in the component.

---

## Task 1: Sidebar collapse store

**Files:**
- Create: `src/stores/sidebar.js`
- Test: `src/stores/sidebar.test.js`

**Interfaces:**
- Consumes: nothing.
- Produces: `useSidebarStore()` exposing `collapsed: Ref<boolean>`, `toggle(): void`,
  `setCollapsed(value: boolean): void`, `initSidebar(): void`. Persistence key:
  `'sb-sidebar-collapsed'` storing `'1'` (collapsed) or `'0'` (expanded).

- [ ] **Step 1: Write the failing test**

```js
// src/stores/sidebar.test.js
import { beforeEach, describe, expect, it } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useSidebarStore } from './sidebar'

describe('sidebar store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
  })

  it('defaults to expanded', () => {
    const store = useSidebarStore()
    expect(store.collapsed).toBe(false)
  })

  it('toggle flips collapsed and persists', () => {
    const store = useSidebarStore()
    store.toggle()
    expect(store.collapsed).toBe(true)
    expect(localStorage.getItem('sb-sidebar-collapsed')).toBe('1')
    store.toggle()
    expect(store.collapsed).toBe(false)
    expect(localStorage.getItem('sb-sidebar-collapsed')).toBe('0')
  })

  it('setCollapsed sets an explicit value', () => {
    const store = useSidebarStore()
    store.setCollapsed(true)
    expect(store.collapsed).toBe(true)
  })

  it('initSidebar reads a persisted collapsed value', () => {
    localStorage.setItem('sb-sidebar-collapsed', '1')
    const store = useSidebarStore()
    store.initSidebar()
    expect(store.collapsed).toBe(true)
  })
})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npx vitest run src/stores/sidebar.test.js`
Expected: FAIL — cannot resolve `./sidebar` (module does not exist yet).

- [ ] **Step 3: Write minimal implementation**

```js
// src/stores/sidebar.js
import { ref } from 'vue'
import { defineStore } from 'pinia'

const STORAGE_KEY = 'sb-sidebar-collapsed'

export const useSidebarStore = defineStore('sidebar', () => {
  const collapsed = ref(false)

  function setCollapsed(value) {
    collapsed.value = Boolean(value)
    localStorage.setItem(STORAGE_KEY, collapsed.value ? '1' : '0')
  }

  function toggle() {
    setCollapsed(!collapsed.value)
  }

  function initSidebar() {
    collapsed.value = localStorage.getItem(STORAGE_KEY) === '1'
  }

  return { collapsed, setCollapsed, toggle, initSidebar }
})
```

- [ ] **Step 4: Run test to verify it passes**

Run: `npx vitest run src/stores/sidebar.test.js`
Expected: PASS (4 tests).

- [ ] **Step 5: Commit**

```bash
git add src/stores/sidebar.js src/stores/sidebar.test.js
git commit -m "feat: add sidebar collapse store with persistence"
```

---

## Task 2: Initialize the sidebar store at startup

**Files:**
- Modify: `src/main.js:33-34` (next to the theme init)

**Interfaces:**
- Consumes: `useSidebarStore().initSidebar()` from Task 1.
- Produces: collapse state restored from `localStorage` before the app mounts.

- [ ] **Step 1: Add the import**

In `src/main.js`, below the existing theme import (line 6), add:

```js
import { useSidebarStore } from '@/stores/sidebar'
```

- [ ] **Step 2: Initialize after the theme store**

In `src/main.js`, immediately after these existing lines:

```js
const themeStore = useThemeStore()
themeStore.initTheme()
```

add:

```js
const sidebarStore = useSidebarStore()
sidebarStore.initSidebar()
```

- [ ] **Step 3: Verify the build**

Run: `npm run build`
Expected: build succeeds with no errors.

- [ ] **Step 4: Commit**

```bash
git add src/main.js
git commit -m "feat: restore sidebar collapse state on startup"
```

---

## Task 3: AppSidebar.vue component

**Files:**
- Create: `src/components/AppSidebar.vue`
- Test: `src/components/AppSidebar.test.js`

**Interfaces:**
- Consumes: `useAuthStore()` (`user.fname`, `user.lname`, `user.role`, `user.profile_picture_url`),
  `useSidebarStore()` (`collapsed`, `toggle`), `RouterLink`, `SbThemeToggle`.
- Produces: a default-export component. Props: none. Emits: `logout` (click on the Log out button),
  `open-support` (click on Help). Root element carries class `sb-sidebar` and, when collapsed, the
  additional class `sb-sidebar--collapsed`.

**Reference — keep these route/role mappings identical to current `App.vue`:**
- tutee/tutor (not admin/superadmin): Dashboard → `tutor` ? `/tch-dashboard` : `/dashboard`;
  Profile → `tutor` ? `/tutor-profile` : `/tutee-profile`.
- tutee: Sessions → `/tuteeSessions` (`bi-search`).
- tutor: Schedule → `/tch-availability` (`bi-calendar3`); Sessions & Reports → `/reports`
  (`bi-file-earmark-text`); Wallet → `/tch-wallet` (`bi-wallet2`).
- admin: Dashboard `/admin/dashboard` (`bi-grid-1x2`); Withdrawals `/admin/withdrawals`
  (`bi-wallet2`); Users `/admin/users` (`bi-people`); Reports `/admin/reports`
  (`bi-bar-chart-line`); Support Desk `/admin/support` (`bi-headset`).
- superadmin: Dashboard `/superadmin/dashboard` (`bi-grid-1x2`); Institutions
  `/superadmin/institutions` (`bi-building`); All Users `/superadmin/users` (`bi-people`); Reports
  `/superadmin/reports` (`bi-bar-chart-line`).

- [ ] **Step 1: Write the failing test**

```js
// src/components/AppSidebar.test.js
import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

let authStore
let sidebarStore

vi.mock('@/stores/auth', () => ({ useAuthStore: () => authStore }))
vi.mock('@/stores/sidebar', () => ({ useSidebarStore: () => sidebarStore }))

const { default: AppSidebar } = await import('./AppSidebar.vue')

const mountSidebar = () =>
  mount(AppSidebar, {
    global: {
      stubs: {
        RouterLink: { template: '<a><slot /></a>' },
        SbThemeToggle: true,
      },
    },
  })

describe('AppSidebar', () => {
  beforeEach(() => {
    authStore = {
      user: { fname: 'Ryan', lname: 'D', role: 'tutee', profile_picture_url: null },
    }
    sidebarStore = { collapsed: false, toggle: vi.fn() }
  })

  it('renders tutee nav items', () => {
    const wrapper = mountSidebar()
    const text = wrapper.text()
    expect(text).toContain('Dashboard')
    expect(text).toContain('Profile')
    expect(text).toContain('Sessions')
  })

  it('shows initials when no profile picture', () => {
    const wrapper = mountSidebar()
    expect(wrapper.text()).toContain('RD')
  })

  it('emits logout when the log out button is clicked', async () => {
    const wrapper = mountSidebar()
    await wrapper.get('[data-test="logout"]').trigger('click')
    expect(wrapper.emitted('logout')).toBeTruthy()
  })

  it('emits open-support when help is clicked', async () => {
    const wrapper = mountSidebar()
    await wrapper.get('[data-test="help"]').trigger('click')
    expect(wrapper.emitted('open-support')).toBeTruthy()
  })

  it('calls toggle when the collapse button is clicked', async () => {
    const wrapper = mountSidebar()
    await wrapper.get('[data-test="collapse-toggle"]').trigger('click')
    expect(sidebarStore.toggle).toHaveBeenCalled()
  })

  it('adds the collapsed class when collapsed', () => {
    sidebarStore.collapsed = true
    const wrapper = mountSidebar()
    expect(wrapper.get('.sb-sidebar').classes()).toContain('sb-sidebar--collapsed')
  })
})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npx vitest run src/components/AppSidebar.test.js`
Expected: FAIL — cannot resolve `./AppSidebar.vue`.

- [ ] **Step 3: Write the component**

Create `src/components/AppSidebar.vue`:

```vue
<template>
  <aside class="sb-sidebar" :class="{ 'sb-sidebar--collapsed': sidebar.collapsed }">
    <div class="sb-brand">
      <span class="sb-brand-badge"><i class="bi bi-book"></i></span>
      <span class="sb-brand-word">StudyBuddy</span>
      <button
        type="button"
        class="sb-collapse-btn sb-btn"
        data-test="collapse-toggle"
        :aria-label="sidebar.collapsed ? 'Expand sidebar' : 'Collapse sidebar'"
        :aria-expanded="!sidebar.collapsed"
        @click="sidebar.toggle()"
      >
        <i class="bi" :class="sidebar.collapsed ? 'bi-chevron-right' : 'bi-chevron-left'"></i>
      </button>
    </div>

    <RouterLink :to="profileRoute" class="sb-profile" :title="fullName">
      <span class="sb-avatar">
        <img v-if="user?.profile_picture_url" :src="user.profile_picture_url" :alt="fullName" />
        <span v-else>{{ initials }}</span>
      </span>
      <span class="sb-profile-copy">
        <span class="sb-profile-name">{{ fullName }}</span>
        <span class="sb-profile-role">{{ roleLabel }}</span>
      </span>
    </RouterLink>

    <p class="sb-section-label">Menu</p>
    <nav class="sb-nav" aria-label="Primary">
      <RouterLink
        v-for="item in menuItems"
        :key="item.to"
        :to="item.to"
        class="sb-item"
        active-class="sb-item--active"
        :title="item.label"
        :aria-label="item.label"
      >
        <span class="sb-chip"><i class="bi" :class="item.icon"></i></span>
        <span class="sb-item-label">{{ item.label }}</span>
      </RouterLink>
    </nav>

    <p class="sb-section-label">Support</p>
    <nav class="sb-nav" aria-label="Support">
      <button
        type="button"
        class="sb-item sb-item-btn"
        data-test="help"
        title="Help"
        aria-label="Help"
        @click="emit('open-support')"
      >
        <span class="sb-chip"><i class="bi bi-question-circle"></i></span>
        <span class="sb-item-label">Help</span>
      </button>
    </nav>

    <div class="sb-spacer"></div>

    <div class="sb-footer">
      <button
        type="button"
        class="sb-item sb-item-btn sb-item--danger"
        data-test="logout"
        title="Log out"
        aria-label="Log out"
        @click="emit('logout')"
      >
        <span class="sb-chip"><i class="bi bi-box-arrow-right"></i></span>
        <span class="sb-item-label">Log out</span>
      </button>
      <SbThemeToggle class="sb-footer-toggle" />
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useSidebarStore } from '@/stores/sidebar'
import SbThemeToggle from '@/components/SbThemeToggle.vue'

const emit = defineEmits(['logout', 'open-support'])

const authStore = useAuthStore()
const sidebar = useSidebarStore()

const user = computed(() => authStore.user)
const role = computed(() => user.value?.role?.toLowerCase() || null)

const fullName = computed(() => {
  const first = user.value?.fname || ''
  const last = user.value?.lname || ''
  return `${first} ${last}`.trim() || 'Studybuddy User'
})

const initials = computed(() => {
  const first = user.value?.fname?.[0] || ''
  const last = user.value?.lname?.[0] || ''
  return `${first}${last}`.toUpperCase() || 'SB'
})

const roleLabel = computed(() => {
  if (!role.value) return ''
  return role.value.charAt(0).toUpperCase() + role.value.slice(1)
})

const profileRoute = computed(() => {
  if (role.value === 'tutor') return '/tutor-profile'
  if (role.value === 'admin' || role.value === 'superadmin') return '/admin/dashboard'
  return '/tutee-profile'
})

const menuItems = computed(() => {
  if (role.value === 'admin') {
    return [
      { to: '/admin/dashboard', label: 'Dashboard', icon: 'bi-grid-1x2' },
      { to: '/admin/withdrawals', label: 'Withdrawals', icon: 'bi-wallet2' },
      { to: '/admin/users', label: 'Users', icon: 'bi-people' },
      { to: '/admin/reports', label: 'Reports', icon: 'bi-bar-chart-line' },
      { to: '/admin/support', label: 'Support Desk', icon: 'bi-headset' },
    ]
  }

  if (role.value === 'superadmin') {
    return [
      { to: '/superadmin/dashboard', label: 'Dashboard', icon: 'bi-grid-1x2' },
      { to: '/superadmin/institutions', label: 'Institutions', icon: 'bi-building' },
      { to: '/superadmin/users', label: 'All Users', icon: 'bi-people' },
      { to: '/superadmin/reports', label: 'Reports', icon: 'bi-bar-chart-line' },
    ]
  }

  if (role.value === 'tutor') {
    return [
      { to: '/tch-dashboard', label: 'Dashboard', icon: 'bi-grid-1x2' },
      { to: '/tutor-profile', label: 'Profile', icon: 'bi-person' },
      { to: '/tch-availability', label: 'Schedule', icon: 'bi-calendar3' },
      { to: '/reports', label: 'Sessions & Reports', icon: 'bi-file-earmark-text' },
      { to: '/tch-wallet', label: 'Wallet', icon: 'bi-wallet2' },
    ]
  }

  return [
    { to: '/dashboard', label: 'Dashboard', icon: 'bi-grid-1x2' },
    { to: '/tutee-profile', label: 'Profile', icon: 'bi-person' },
    { to: '/tuteeSessions', label: 'Sessions', icon: 'bi-search' },
  ]
})
</script>

<style scoped>
.sb-sidebar {
  --sb-sidebar-width: 250px;
  --sb-green-tint: #edf7f3;
  --sb-green-border: #b8dece;
  display: flex;
  flex-direction: column;
  width: var(--sb-sidebar-width);
  flex: 0 0 var(--sb-sidebar-width);
  height: 100vh;
  padding: 1rem 0.75rem;
  background: var(--sb-card-bg);
  border-right: 1px solid var(--sb-card-border);
  transition: width var(--sb-t-normal) var(--sb-spring),
              flex-basis var(--sb-t-normal) var(--sb-spring);
  overflow: hidden;
}

.sb-sidebar--collapsed {
  --sb-sidebar-width: 76px;
}

.sb-brand {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.4rem 0.5rem 0.85rem;
}

.sb-brand-badge {
  display: grid;
  place-items: center;
  width: 34px;
  height: 34px;
  flex: 0 0 auto;
  border-radius: 10px;
  background: linear-gradient(135deg, var(--sb-primary), var(--sb-primary-mid));
  color: #fff;
  font-size: 1.05rem;
}

.sb-brand-word {
  font-size: 1.05rem;
  font-weight: 800;
  letter-spacing: -0.01em;
  color: var(--sb-text-main);
  white-space: nowrap;
}

.sb-collapse-btn {
  display: grid;
  place-items: center;
  width: 28px;
  height: 28px;
  margin-left: auto;
  border: 0;
  border-radius: 8px;
  background: var(--sb-bg);
  color: var(--sb-text-muted);
}

.sb-profile {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  margin: 0 0.25rem 0.5rem;
  padding: 0.6rem;
  border-radius: 14px;
  background: var(--sb-green-tint);
  text-decoration: none;
}

.sb-avatar {
  display: grid;
  place-items: center;
  width: 38px;
  height: 38px;
  flex: 0 0 auto;
  border-radius: 50%;
  overflow: hidden;
  background: linear-gradient(135deg, var(--sb-primary), var(--sb-primary-mid));
  color: #fff;
  font-size: 0.85rem;
  font-weight: 800;
}

.sb-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.sb-profile-copy {
  display: grid;
  gap: 0.1rem;
  min-width: 0;
}

.sb-profile-name {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--sb-text-main);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sb-profile-role {
  font-size: 0.72rem;
  color: var(--sb-text-muted);
}

.sb-section-label {
  margin: 0.85rem 0 0.35rem;
  padding: 0 0.85rem;
  font-size: 0.72rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--sb-text-muted);
}

.sb-nav {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.sb-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: 0.7rem;
  width: 100%;
  padding: 0.5rem 0.6rem;
  border: 0;
  border-radius: 12px;
  background: transparent;
  color: var(--sb-text-secondary);
  font-size: 0.9rem;
  font-weight: 500;
  text-align: left;
  text-decoration: none;
  cursor: pointer;
  transition: background-color var(--sb-t-normal) var(--sb-spring),
              color var(--sb-t-normal) var(--sb-spring);
}

.sb-item:hover {
  background: color-mix(in srgb, var(--sb-card-bg) 88%, var(--sb-primary));
  color: var(--sb-text-main);
}

.sb-item--active {
  background: var(--sb-green-tint);
  color: var(--sb-primary);
  font-weight: 700;
}

.sb-item--active::before {
  content: '';
  position: absolute;
  left: -0.6rem;
  top: 0.45rem;
  bottom: 0.45rem;
  width: 4px;
  border-radius: 0 4px 4px 0;
  background: var(--sb-primary);
}

.sb-chip {
  display: grid;
  place-items: center;
  width: 32px;
  height: 32px;
  flex: 0 0 auto;
  border-radius: 10px;
  background: var(--sb-bg);
  color: var(--sb-text-muted);
  font-size: 0.95rem;
  transition: background-color var(--sb-t-normal) var(--sb-spring),
              color var(--sb-t-normal) var(--sb-spring);
}

.sb-item--active .sb-chip {
  background: var(--sb-primary);
  color: #fff;
}

.sb-item-label {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sb-item--danger { color: var(--sb-danger); }
.sb-item--danger .sb-chip { background: color-mix(in srgb, var(--sb-danger) 12%, transparent); color: var(--sb-danger); }

.sb-spacer { flex: 1 1 auto; }

.sb-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  margin-top: 0.5rem;
  padding-top: 0.75rem;
  border-top: 1px solid var(--sb-card-border);
}

.sb-footer .sb-item { width: auto; flex: 1; }

/* Collapsed state */
.sb-sidebar--collapsed .sb-brand { justify-content: center; }
.sb-sidebar--collapsed .sb-brand-word,
.sb-sidebar--collapsed .sb-collapse-btn,
.sb-sidebar--collapsed .sb-profile-copy,
.sb-sidebar--collapsed .sb-section-label,
.sb-sidebar--collapsed .sb-item-label,
.sb-sidebar--collapsed .sb-footer-toggle {
  display: none;
}

.sb-sidebar--collapsed .sb-profile { justify-content: center; padding: 0.4rem; }
.sb-sidebar--collapsed .sb-item { justify-content: center; padding: 0.5rem; }
.sb-sidebar--collapsed .sb-footer { flex-direction: column; }
.sb-sidebar--collapsed .sb-footer .sb-item { width: 100%; justify-content: center; }

/* Dark theme accents */
:global([data-sb-theme='dark']) .sb-sidebar {
  --sb-green-tint: rgba(0, 137, 90, 0.16);
  --sb-green-border: #1f4d3c;
}

:global([data-sb-theme='dark']) .sb-item--active {
  color: #7fe3b8;
}

:global([data-sb-theme='dark']) .sb-item--active .sb-chip {
  background: rgba(0, 137, 90, 0.28);
  color: #7fe3b8;
}
</style>
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `npx vitest run src/components/AppSidebar.test.js`
Expected: PASS (6 tests).

- [ ] **Step 5: Run lint**

Run: `npm run lint`
Expected: no errors on `src/components/AppSidebar.vue`.

- [ ] **Step 6: Commit**

```bash
git add src/components/AppSidebar.vue src/components/AppSidebar.test.js
git commit -m "feat: add AppSidebar component with collapse and theme support"
```

---

## Task 4: Wire AppSidebar into App.vue

**Files:**
- Modify: `src/App.vue` — template (replace the `<aside class="sidebar">…</aside>` block, lines
  ~11-134), script (import `AppSidebar`), style (remove `.active-nav` and `.nav-link:hover`).

**Interfaces:**
- Consumes: `AppSidebar` (emits `logout`, `open-support`) from Task 3; existing `openLogoutModal`
  and `openSupport` handlers in `App.vue`.
- Produces: the authenticated layout renders the new sidebar; logout + support flows unchanged.

- [ ] **Step 1: Import the component**

In `src/App.vue` `<script setup>`, add alongside the other component imports (near `SbThemeToggle`):

```js
import AppSidebar from '@/components/AppSidebar.vue'
```

- [ ] **Step 2: Replace the sidebar markup**

In `src/App.vue`, replace the entire `<aside class="sidebar …"> … </aside>` element (the brand,
the `<ul class="nav nav-pills …">` list, and the footer utility `<div class="mt-auto …">`) with:

```vue
<AppSidebar @logout="openLogoutModal" @open-support="() => openSupport('Other')" />
```

Leave the `SupportModal`, logout modal, and `<main>` blocks that follow exactly as they are.

- [ ] **Step 3: Remove the now-orphaned sidebar CSS**

In `src/App.vue` `<style>`, delete the sidebar-only rules (they now live in `AppSidebar.vue`):

```css
/* --- Sidebar Navigation Styles --- */
.active-nav { … }
.nav-link:hover { … }
```

Do not remove `.sb-btn`, `.sb-interactive`, `.app-main*`, or the chat/header rules — those are still
used by the rest of `App.vue`.

- [ ] **Step 4: Run lint and build**

Run: `npm run lint`
Expected: no errors.

Run: `npm run build`
Expected: build succeeds.

- [ ] **Step 5: Manual verification (preview)**

Start the dev server and verify in the browser:
- Sidebar renders for a tutee; nav items match (Dashboard, Profile, Sessions).
- The active item shows the green chip + left rail indicator and follows route changes.
- Collapse toggle shrinks to the icon rail and persists across a reload.
- Toggle the theme: sidebar adapts (light surface / deep-green dark surface), active accent stays
  legible.
- Click Log out → logout modal opens. Click Help → support modal opens.
- Visit `/chat` → layout still correct (no clipping) collapsed and expanded.

Expected: all pass. If anything fails, fix in `AppSidebar.vue` and re-run Steps 4-5.

- [ ] **Step 6: Commit**

```bash
git add src/App.vue
git commit -m "feat: replace App.vue sidebar with AppSidebar component"
```

---

## Self-Review

- **Spec coverage:** profile block (Task 3 template), grouped Menu/Support sections (Task 3),
  pinned footer with logout + theme toggle (Task 3), sliding rail active indicator + chips
  (Task 3 styles), collapse + persistence (Tasks 1-3), theme adaptation (Task 3 dark overrides),
  extraction into `AppSidebar.vue` + event wiring (Tasks 3-4), local green-tint tokens (Task 3
  styles, no `main.css` change). Role visibility preserved (Task 3 `menuItems`/`profileRoute`).
- **Placeholder scan:** none — every step shows full code or exact commands/expected output.
- **Type/name consistency:** store API (`collapsed`, `toggle`, `setCollapsed`, `initSidebar`) is
  identical across Tasks 1-3; the component root class `sb-sidebar` / `sb-sidebar--collapsed` and the
  `data-test` hooks (`collapse-toggle`, `help`, `logout`) match between the component and its test;
  emitted events `logout` / `open-support` match the `App.vue` wiring in Task 4.

## Notes / deviations from spec

- Green-tint tokens are defined locally on the sidebar root (not promoted to `main.css`), matching
  the `Dashboard.vue` `.dashboard-shell` pattern. The spec was updated to reflect this.
- Mobile slide-over drawer remains out of scope; collapse is a desktop affordance.

## Changelog

- **2026-06-21** — Plan created from the approved spec (4 tasks: store, startup init, component,
  App.vue wiring). Recorded the local green-tint-token deviation from the spec.
