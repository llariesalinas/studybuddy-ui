# Plan: Sidebar Notification Count Badge

**Date:** 2026-05-23
**Feature:** Add an unread notification count badge to the sidebar nav in App.vue
**Requirement:** Badge shows unread count from the Pinia notifications store and updates in real time (via existing 15-second polling already wired in NotificationBell.vue).

---

## Context

The `useNotificationsStore` at `src/stores/notifications.js` already exposes:
- `notifications` — reactive array
- `unreadCount` — computed, filters `!is_read`
- `fetchNotifications()` — fetches from `/notifications/`

`src/components/NotificationBell.vue` (rendered in the header) polls every 15 seconds and on `visibilitychange`. Because `useNotificationsStore` is a singleton Pinia store, the sidebar badge shares the same reactive state without any extra polling.

`App.vue` already:
- imports `useNotificationsStore` (line 232)
- instantiates `notificationsStore` (line 239)
- calls `notificationsStore.fetchNotifications()` in `onMounted` (line 291)

No `/notifications` route exists in `src/router/index.js` and no `src/views/Notifications.vue` exists. The sidebar item will therefore be a visual nav label with a badge (not a router-link to a non-existent route).

---

## Tasks

### Task 1 — Add Notifications nav item with badge to the sidebar in App.vue

**File to modify:** `src/App.vue`

**Where to insert:** Inside `<ul class="nav nav-pills flex-column mb-auto">`, after the Profile `<li>` (line 20–24) and before the Sessions `<li v-if="userRole === 'tutee'">` (line 26). This placement makes Notifications appear for all authenticated users regardless of role.

**HTML to insert (no router-link — /notifications route does not exist):**

```html
<li class="nav-item mb-2">
  <span class="nav-link text-white opacity-75 d-flex align-items-center justify-content-between">
    <span class="d-flex align-items-center">
      <i class="bi bi-bell me-3"></i> Notifications
    </span>
    <span
      v-if="notificationsStore.unreadCount > 0"
      class="sidebar-notification-badge"
      :aria-label="`${notificationsStore.unreadCount} unread notification${notificationsStore.unreadCount === 1 ? '' : 's'}`"
    >
      {{ notificationsStore.unreadCount > 99 ? '99+' : notificationsStore.unreadCount }}
    </span>
  </span>
</li>
```

**Why a `<span>` and not a `<router-link>`:**
The router has no `/notifications` route. Using `<router-link to="/notifications">` would render a broken link. The sidebar badge serves as a real-time visual indicator; clicking the bell in the header opens the full notification dropdown. Once a `/notifications` view is built (out of scope here), this `<span>` can be upgraded to a `<router-link>` with `active-class="active-nav"` in a single-line change.

**CSS to append to the `<style>` block in App.vue** (the style block is not scoped — this is correct for sidebar styles):

```css
/* --- Sidebar Notification Badge --- */
.sidebar-notification-badge {
  min-width: 20px;
  height: 20px;
  padding: 0 5px;
  border-radius: 999px;
  background: #dc3545;
  color: #ffffff;
  font-size: 11px;
  font-weight: 800;
  line-height: 20px;
  text-align: center;
  flex-shrink: 0;
}
```

**No new imports or store instantiation needed** — `notificationsStore` is already defined in `<script setup>` at line 239.

**Verification steps:**
1. Start the dev server: `npm run dev`
2. Log in as either a tutee or a tutor who has at least one unread notification.
3. Check the sidebar — a red pill badge should appear next to "Notifications" showing the unread count.
4. Open the NotificationBell in the header and mark a notification as read — the sidebar badge should decrement (optimistic update fires immediately via `markAsRead` in the store, which mutates `notifications.value` in place).
5. When all notifications are read, the badge must not render at all (controlled by `v-if="notificationsStore.unreadCount > 0"`).
6. Verify the layout: the sidebar item should not break the existing sidebar width (250px) or push other items down unexpectedly.
7. Log out and verify the sidebar (and badge) is gone on public routes.

**Commit:**
```
git add src/App.vue
git commit -m "feat(sidebar): add unread notification count badge to sidebar nav"
```

---

## Acceptance Criteria

- A bell icon with label "Notifications" appears in the sidebar for all authenticated users (both tutor and tutee roles).
- A red pill badge shows the integer unread count when `notificationsStore.unreadCount > 0`.
- The badge is hidden (not merely `0`) when there are no unread notifications (`v-if`, not `v-show`).
- Counts above 99 display as `99+`.
- The badge count reflects the same Pinia store state as the header `NotificationBell` — no separate fetch or polling needed.
- Marking a notification as read via the header bell immediately decrements the badge (optimistic store update).
- No existing sidebar links or layout are broken.
- No new dependencies, routes, views, or polling intervals are introduced.

---

## Risk Notes

- **No new polling required.** `NotificationBell.vue` polls every 15s and on `visibilitychange`. `App.vue` already calls `fetchNotifications()` on mount. The sidebar badge is purely reactive via the shared Pinia store.
- **API failure is graceful.** `fetchNotifications` has a `try/catch`; on failure the store retains its previous value. An empty `notifications` array yields `unreadCount = 0`, hiding the badge — a safe default.
- **No route required.** The sidebar item uses a `<span>` instead of a `<router-link>` to avoid linking to the non-existent `/notifications` route.
- **Zero new dependencies.** Uses Bootstrap Icons class `bi-bell` (already in the project and used in `NotificationBell.vue`) and the existing Pinia store.
- **Upgrade path.** When a `/notifications` view is added, replacing `<span class="nav-link ...">` with `<router-link to="/notifications" class="nav-link ..." active-class="active-nav">` is the only change needed.
