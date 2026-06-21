---
title: Sidebar Redesign (Indicator Rail / Aurora Light)
date: 2026-06-21
status: Approved
spec: this document
---

# Sidebar Redesign — Design

## Goal

Replace the plain dark sidebar in `App.vue` with a polished, theme-adaptive sidebar that
matches the Dashboard's visual language, adds a profile block and grouped sections, moves
logout/theme into a pinned footer, and can collapse to an icon-only rail.

Chosen direction: **C (Indicator Rail)** structure wearing the **Aurora Light** skin, with colors
matched to `src/views/Dashboard.vue`. Scope agreed up front: visual refresh **plus** structural
reorganization, collapse feature **built** (not just styled), sidebar **adapts to theme**.

## Approach

Extract the sidebar from `App.vue` (currently ~970 lines) into a dedicated, token-driven
component, and store collapse state in a small Pinia store that persists to `localStorage`
(mirroring `stores/theme.js`). All colors come from existing CSS custom properties so light/dark
"just works"; only a few green-tint accents need explicit dark overrides.

### Components / units

- **`src/components/AppSidebar.vue`** (new) — owns the entire sidebar UI and the collapse toggle.
  - Reads `useAuthStore()` for `user.fname`, `user.lname`, `user.role`, `user.profile_picture_url`,
    and `useChatStore()` is **not** needed here (chat lives in the top header, unchanged).
  - Reads `useSidebarStore()` for `collapsed`.
  - Emits `@logout` and `@open-support` up to `App.vue`, which keeps ownership of the logout modal
    and `SupportModal` (no behavior change to those flows).
  - Role-based nav item visibility is identical to today's logic (tutee / tutor / admin /
    superadmin). This is a restyle + regroup, not a permissions change.
- **`src/stores/sidebar.js`** (new) — `collapsed` ref, `toggle()`, `setCollapsed(v)`, and
  `initSidebar()` that reads `localStorage['sb-sidebar-collapsed']`. Initialized once at app
  startup alongside the existing theme init.
- **`src/App.vue`** (edit) — swap the `<aside class="sidebar">` block for `<AppSidebar @logout="openLogoutModal" @open-support="openSupport('Other')" />`. Sidebar-specific CSS moves
  into `AppSidebar.vue`'s scoped styles; the shared `.active-nav`/`.nav-link` rules used only by the
  sidebar move with it.
- **`src/assets/main.css`** (edit) — promote `--sb-green-tint` and `--sb-green-border` (currently
  local to `.dashboard-shell`) into the global `:root` (and the dark block) so both the Dashboard
  and the sidebar share them instead of redefining. No value changes.

### Layout (top → bottom)

1. **Brand row** — green rounded-square badge (`bi bi-book`, gradient `--sb-primary` → `--sb-primary-mid`)
   + "StudyBuddy" wordmark + collapse toggle button (`bi bi-chevron-left` expanded / `bi bi-chevron-right`
   collapsed).
2. **Profile block** — `RouterLink` to the role's profile route. Avatar shows
   `profile_picture_url` if present, else initials (fname/lname) on a green gradient. Name =
   `fname lname`; sub-line = capitalized role (+ "· CPU" optional). Green-tinted rounded container.
3. **Section "Menu"** — kicker label (Dashboard `.panel-kicker` style) + the role's primary nav
   items, each `chip + label`, active item shows the sliding rail indicator.
4. **Section "Support"** — Help item (`bi bi-question-circle`, emits `@open-support`).
5. **Spacer** (`flex: 1`).
6. **Footer (pinned)** — top divider, then Log out (`bi bi-box-arrow-right`, emits `@logout`) and
   the existing `<SbThemeToggle />`.

### Visual tokens (matched to Dashboard)

- Sidebar surface: `var(--sb-card-bg)` with a `1px var(--sb-card-border)` right edge (sibling of
  `.glass-panel`).
- Nav row radius 12px; icon chip 32–34px, radius 12px.
  - Inactive chip: `var(--sb-bg)` background, `--sb-text-muted` icon.
  - Hover row: `color-mix(var(--sb-card-bg), --sb-primary)` subtle tint.
  - **Active row**: `--sb-green-tint` background, `--sb-primary` text, **filled `--sb-primary` chip
    with white icon**, plus a 4px rounded left-rail indicator (`--sb-primary`).
- Section kicker: 0.72rem, weight 800, uppercase, `--sb-text-muted`.
- Profile avatar: green gradient or `--sb-green-tint` bg with `--sb-primary` initials, 2px border
  (mirrors Dashboard `.tutor-avatar`).
- Soft shadow only on elevated elements: `0 8px 20px rgba(15, 23, 42, 0.06)`.

### Collapse behavior

- Widths: expanded **250px** (current), collapsed **76px**. CSS custom prop
  `--sb-sidebar-width` toggled on the root element; `aside` transitions `width` with
  `var(--sb-t-normal) var(--sb-spring)`.
- Collapsed state hides: wordmark, profile text, section kickers, nav labels, footer label text.
  Centers: badge, avatar, chips, footer icons (theme toggle + logout stack).
- Collapsed items expose `title` + `aria-label` for tooltip/screen-reader access.
- Collapse toggle: `aria-expanded`, `aria-controls`, visible in both states.
- Persistence: `localStorage['sb-sidebar-collapsed']` ('1'/'0') via `useSidebarStore`.
- Main content needs no change — `App.vue`'s `<main>` is already `flex-grow-1`, so it reflows as the
  sidebar width changes.

### Dark mode

- All surfaces/text use tokens, so dark uses the app's dark surfaces automatically (deep-green
  panels, not pure black — consistent with the Dashboard).
- Targeted overrides under `[data-sb-theme="dark"]` (scoped via `:deep`/global as needed) only for:
  active-row tint → `rgba(0, 137, 90, 0.16)`, active text → lighter green (`#7fe3b8`), and inactive
  chip background → a dark neutral. No layout differences between themes.

### Icons

Bootstrap Icons throughout (as today): `bi-grid-1x2` (dashboard), `bi-person` (profile),
`bi-search` (tutee sessions), `bi-calendar3` (schedule), `bi-file-earmark-text` (reports),
`bi-wallet2` (wallet), `bi-people`/`bi-building`/`bi-bar-chart-line`/`bi-headset` (admin/superadmin),
`bi-question-circle` (help), `bi-box-arrow-right` (logout), plus `bi-book` (brand) and
`bi-chevron-left`/`bi-chevron-right` (collapse).

### Accessibility

- Active link keeps `active-class="active-nav"` (router adds `aria-current` semantics via styling);
  ensure the active item is programmatically distinguishable.
- Collapse toggle and collapsed items carry `aria-label`/`aria-expanded`/`title`.
- Focus-visible rings use `--sb-primary`.
- Motion already respects `prefers-reduced-motion` via the global rule in `App.vue`.

## Risks

- **Logout / support wiring**: those modals stay in `App.vue`; the sidebar must emit events rather
  than own them. Mis-wiring would break logout. Mitigation: keep `openLogoutModal`/`openSupport`
  in `App.vue` and pass via events; verify both flows after the swap.
- **Sidebar-only CSS leakage**: `.active-nav`, `.nav-link:hover` currently live in `App.vue`'s
  global style. Moving them into a scoped component must not break other `.nav-link` usages
  elsewhere. Mitigation: these rules are sidebar-specific; confirm no other view depends on them
  before moving (grep `active-nav`).
- **Token promotion**: moving `--sb-green-tint`/`--sb-green-border` to `:root` must not change the
  Dashboard (same values). Mitigation: keep identical values; the `.dashboard-shell` local
  definitions can stay or be removed — keeping them is harmless (same value).
- **Collapse + layout**: ensure collapsed width doesn't clip content or break the chat view
  (`app-main-chat`). Mitigation: width is on the sidebar only; test chat route collapsed/expanded.
- **Mobile**: current layout has no mobile drawer; this redesign does not add one (out of scope).
  Collapse is a desktop affordance. Note for a future pass.

## Checks to run

- `npm run lint`
- `npm run build`
- Manual (preview): each role's sidebar renders; active indicator follows the route; collapse
  toggles + persists across reload; light/dark both look correct; logout modal and support modal
  still open; chat route unaffected.

## Out of scope

- Mobile slide-over drawer / hamburger.
- Changing which nav items each role sees (visibility logic unchanged).
- Top header (chat icon, notification bell, page titles) — untouched.
