# Animation System Expansion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add 3 animation layers (entrance transitions, data micro-interactions, feedback & flow) app-wide using CSS + Vue Transition — no new dependencies.

**Architecture:** Global keyframes and utility classes go into App.vue's non-scoped `<style>`. Per-view wiring uses each view's own `<style scoped>`. Three new files: `src/stores/toast.js` (Pinia queue), `src/components/SbToast.vue` (renderer, teleported to body), `src/components/SbStepBar.vue` (progress bar). All `alert()` calls across the app are migrated to `toastStore.push()`.

**Tech Stack:** Vue 3 Composition API, Pinia, Bootstrap 5, CSS keyframe animations — no new npm packages.

---

## File Map

| File | Status | Responsibility |
|---|---|---|
| `src/App.vue` | Modify | Add `--sb-t-slow` token, 6 new keyframes, utility classes, page `<Transition>`, toast mount |
| `src/stores/toast.js` | Create | Pinia toast queue (push, dismiss, auto-expire) |
| `src/components/SbToast.vue` | Create | Renders toast stack, teleported to `<body>` |
| `src/components/SbStepBar.vue` | Create | Animated progress bar driven by `current` / `total` props |
| `src/views/PreferenceSetup.vue` | Modify | Replace Bootstrap progress bar with `SbStepBar` |
| `src/views/Dashboard.vue` | Modify | Stagger stat cards on mount |
| `src/views/TutorDashboard.vue` | Modify | Stagger stat cards on mount |
| `src/views/TuteeSessions.vue` | Modify | Tab indicator on active filter pill |
| `src/views/SessionsReports.vue` | Modify | Tab indicator on active filter pill |
| `src/views/TutorSessionsReports.vue` | Modify | Tab indicator on active filter pill |
| `src/views/TutorProfile.vue` | Modify | Accordion body `<Transition>` with JS height hook |
| `src/views/PostSessionPaymentView.vue` | Modify | Success pop + alert → toast |
| `src/views/TutorPaymentScreen.vue` | Modify | Success pop + alert → toast |
| Multiple views (listed per task) | Modify | Replace `alert()` with `toastStore.push()` |

---

## Task 1: Global CSS Foundation (App.vue)

**Files:**
- Modify: `src/App.vue` — style block only

Add `--sb-t-slow`, six keyframes, utility classes, and the reduced-motion safety net to the non-scoped `<style>` in `src/App.vue`.

- [ ] **Step 1: Add `--sb-t-slow` to `:root`**

In `src/App.vue`, find the `:root` block (currently ends with `--sb-t-normal: 250ms;`). Add the missing token on the line after `--sb-t-normal`:

```css
--sb-t-slow: 400ms;
```

After the edit the bottom of `:root` should read:
```css
  --sb-t-quick: 120ms;
  --sb-t-normal: 250ms;
  --sb-t-slow: 400ms;
}
```

- [ ] **Step 2: Add six new keyframes after the existing `sb-shake` keyframe**

Find `@keyframes sb-shake { ... }` (currently the last keyframe in the file). Insert the following block immediately after its closing `}`:

```css
/* --- Layer A/B/C Keyframes --- */
@keyframes sb-stagger-in {
  from { opacity: 0; transform: translateY(10px); }
  to   { opacity: 1; transform: translateY(0); }
}

@keyframes sb-scale-in {
  from { opacity: 0; transform: scale(0.94); }
  to   { opacity: 1; transform: scale(1); }
}

@keyframes sb-shimmer {
  0%   { background-position: -600px 0; }
  100% { background-position:  600px 0; }
}

@keyframes sb-tab-indicator {
  from { transform: scaleX(0); opacity: 0; }
  to   { transform: scaleX(1); opacity: 1; }
}

@keyframes sb-toast-in {
  from { opacity: 0; transform: translateY(-14px) scale(0.95); }
  to   { opacity: 1; transform: translateY(0)   scale(1); }
}

@keyframes sb-success-border {
  0%   { box-shadow: 0 0 0 0 rgba(0, 137, 90, 0.5); }
  60%  { box-shadow: 0 0 0 6px rgba(0, 137, 90, 0); }
  100% { box-shadow: none; }
}
```

- [ ] **Step 3: Add utility classes after the new keyframes**

Immediately after the keyframes block from Step 2, insert:

```css
/* --- Layer A: Stagger entrance --- */
.sb-stagger-item {
  animation: sb-stagger-in var(--sb-t-normal) var(--sb-spring) both;
  opacity: 0;
}

/* --- Layer A: Modal scale-in (all Bootstrap modals, no per-modal changes needed) --- */
.modal.show .modal-content {
  animation: sb-scale-in var(--sb-t-normal) var(--sb-spring) both;
}

/* --- Layer B: Skeleton shimmer --- */
.sb-skeleton {
  background: linear-gradient(
    90deg,
    rgba(226, 232, 240, 0.8) 25%,
    rgba(203, 213, 225, 0.9) 50%,
    rgba(226, 232, 240, 0.8) 75%
  );
  background-size: 600px 100%;
  animation: sb-shimmer 1.6s ease-in-out infinite;
  border-radius: 12px;
}

/* --- Layer C: Success card border pulse --- */
.sb-success-card {
  animation: sb-success-border 600ms var(--sb-spring) both;
}

/* --- Accessibility: kill all motion for users who ask --- */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 1ms !important;
    animation-delay: 0ms !important;
    transition-duration: 1ms !important;
  }
}
```

- [ ] **Step 4: Verify visually**

Run `npm run dev`. Open any Bootstrap modal (e.g. sidebar logout button). The modal dialog should scale up from 0.94 → 1 when it opens. Open DevTools → Elements, check that `:root` has `--sb-t-slow: 400ms`.

- [ ] **Step 5: Commit**

```
git add src/App.vue
git commit -m "feat: add animation tokens, keyframes, and utility classes to App.vue"
```

---

## Task 2: Page Route Transition (App.vue)

**Files:**
- Modify: `src/App.vue` — template and style

Wrap the authenticated-layout `<router-view />` in a `<Transition>` so routes fade + slide in. The sidebar and header stay static.

- [ ] **Step 1: Wrap the authenticated `<router-view />` with `<Transition>`**

In `src/App.vue`, find this line (inside `<main>` after the `<RatingReminderBanner>` component):

```html
      <router-view />
```

Replace it with:

```html
      <Transition name="page" mode="out-in">
        <router-view :key="route.name" />
      </Transition>
```

`route` is already imported via `const route = useRoute()` in the script.

- [ ] **Step 2: Wrap the public-layout `<router-view />` too**

In the same file, find the first `<router-view />` (inside `<div v-if="isPublicRoute">`):

```html
  <div v-if="isPublicRoute" class="public-layout">
    <router-view />
  </div>
```

Replace with:

```html
  <div v-if="isPublicRoute" class="public-layout">
    <Transition name="page" mode="out-in">
      <router-view :key="route.name" />
    </Transition>
  </div>
```

- [ ] **Step 3: Add page transition CSS to the global style**

In the non-scoped `<style>` in `src/App.vue`, add after the `.sb-interactive:active` block (before `/* --- Animation Keyframes ---*/`):

```css
/* --- Page Route Transition --- */
.page-enter-active {
  transition: opacity var(--sb-t-normal) var(--sb-spring),
              transform var(--sb-t-normal) var(--sb-spring);
}
.page-enter-from {
  opacity: 0;
  transform: translateY(8px);
}
.page-leave-active {
  transition: opacity var(--sb-t-quick) ease;
}
.page-leave-to {
  opacity: 0;
}
```

- [ ] **Step 4: Verify visually**

In the running dev server, click between Dashboard and Sessions in the sidebar. The page content should fade out quickly, then the next page slides up and fades in. The sidebar and top header must NOT move.

- [ ] **Step 5: Commit**

```
git add src/App.vue
git commit -m "feat: add page route transition (fade + slide, out-in mode)"
```

---

## Task 3: Toast Store

**Files:**
- Create: `src/stores/toast.js`

- [ ] **Step 1: Create the file**

Create `src/stores/toast.js` with this exact content:

```js
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useToastStore = defineStore('toast', () => {
  const toasts = ref([])
  let nextId = 0

  function push(message, type = 'success', duration = 3500) {
    const id = ++nextId
    toasts.value.push({ id, message, type })
    setTimeout(() => dismiss(id), duration)
  }

  function dismiss(id) {
    const idx = toasts.value.findIndex(t => t.id === id)
    if (idx !== -1) toasts.value.splice(idx, 1)
  }

  return { toasts, push, dismiss }
})
```

- [ ] **Step 2: Verify the file exists and is syntactically correct**

Run: `npm run lint -- src/stores/toast.js`

Expected: no errors.

- [ ] **Step 3: Commit**

```
git add src/stores/toast.js
git commit -m "feat: add toast store (Pinia queue with auto-dismiss)"
```

---

## Task 4: Toast Component + App.vue Mount

**Files:**
- Create: `src/components/SbToast.vue`
- Modify: `src/App.vue` — script and template

- [ ] **Step 1: Create `src/components/SbToast.vue`**

```vue
<template>
  <Teleport to="body">
    <div class="sb-toast-stack">
      <TransitionGroup name="toast">
        <div
          v-for="toast in toastStore.toasts"
          :key="toast.id"
          class="sb-toast"
          :class="`sb-toast--${toast.type}`"
          role="alert"
          aria-live="polite"
          @click="toastStore.dismiss(toast.id)"
        >
          <span class="sb-toast-dot"></span>
          {{ toast.message }}
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup>
import { useToastStore } from '@/stores/toast'
const toastStore = useToastStore()
</script>

<style scoped>
.sb-toast-stack {
  position: fixed;
  top: 20px;
  right: 24px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 8px;
  pointer-events: none;
}

.sb-toast {
  background: var(--sb-dark);
  color: #ffffff;
  border-radius: 12px;
  padding: 12px 18px;
  font-size: 13px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 10px;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.22);
  cursor: pointer;
  pointer-events: auto;
  max-width: 320px;
}

.sb-toast--error   { background: #7f1d1d; }
.sb-toast--warning { background: #78350f; }

.sb-toast-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--sb-primary);
  flex-shrink: 0;
}
.sb-toast--error .sb-toast-dot   { background: #fca5a5; }
.sb-toast--warning .sb-toast-dot { background: #fcd34d; }

/* TransitionGroup hooks — sb-toast-in keyframe is defined globally in App.vue */
.toast-enter-active {
  animation: sb-toast-in var(--sb-t-normal) var(--sb-spring-fast) both;
}
.toast-leave-active {
  transition: opacity var(--sb-t-quick) ease, transform var(--sb-t-quick) ease;
}
.toast-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}
</style>
```

- [ ] **Step 2: Import and mount `SbToast` in `src/App.vue`**

In `src/App.vue` `<script setup>`, add at the bottom of the existing imports:

```js
import SbToast from '@/components/SbToast.vue'
```

In the template, add `<SbToast />` as the very last element before the closing `</template>` tag. The template structure has two root branches (`v-if="isPublicRoute"` and `v-else`). Vue 3 allows multiple root nodes, so add it after both:

```html
  <SbToast />
</template>
```

- [ ] **Step 3: Verify toasts work**

In a browser console on the running dev server, open Vue DevTools → Pinia → toast store. Call `useToastStore().push('Hello toast!')`. A dark toast should slide in from the top-right and auto-dismiss after 3.5 seconds. Click it early to dismiss manually.

- [ ] **Step 4: Commit**

```
git add src/components/SbToast.vue src/App.vue
git commit -m "feat: add SbToast component and mount in App.vue shell"
```

---

## Task 5: SbStepBar Component + PreferenceSetup.vue

**Files:**
- Create: `src/components/SbStepBar.vue`
- Modify: `src/views/PreferenceSetup.vue`

- [ ] **Step 1: Create `src/components/SbStepBar.vue`**

```vue
<template>
  <div class="sb-step-bar" :aria-label="`Step ${current} of ${total}`">
    <div class="sb-step-bar-labels">
      <span class="sb-step-label">Step {{ current }} of {{ total }}</span>
      <span class="sb-step-label sb-step-label--right">{{ Math.round((current / total) * 100) }}%</span>
    </div>
    <div class="sb-step-track">
      <div class="sb-step-fill" :style="{ width: `${(current / total) * 100}%` }"></div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  current: { type: Number, required: true },
  total:   { type: Number, required: true },
})
</script>

<style scoped>
.sb-step-bar { width: 100%; }

.sb-step-bar-labels {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
}

.sb-step-label {
  font-size: 12px;
  font-weight: 700;
  color: var(--sb-text-secondary, #475569);
}

.sb-step-track {
  height: 6px;
  background: rgba(0, 137, 90, 0.15);
  border-radius: 999px;
  overflow: hidden;
}

.sb-step-fill {
  height: 100%;
  background: var(--sb-primary);
  border-radius: 999px;
  transition: width 700ms var(--sb-spring);
}
</style>
```

- [ ] **Step 2: Replace Bootstrap progress bar in `src/views/PreferenceSetup.vue`**

`PreferenceSetup.vue` already has a `currentCard` (0-based, 0–2) and `totalCards = 3`. Find and replace the existing progress block (lines ~20–28):

Old:
```html
          <!-- PROGRESS -->
          <div class="mb-4">
            <div class="progress" style="height:8px;">
              <div
                class="progress-bar bg-success"
                :style="{ width: progressPercentage + '%' }"
              ></div>
            </div>
          </div>
```

New:
```html
          <!-- PROGRESS -->
          <div class="mb-4">
            <SbStepBar :current="currentCard + 1" :total="totalCards" />
          </div>
```

- [ ] **Step 3: Import `SbStepBar` in `PreferenceSetup.vue`**

In `<script setup>` of `PreferenceSetup.vue`, add the import (after existing imports):

```js
import SbStepBar from '@/components/SbStepBar.vue'
```

- [ ] **Step 4: Verify**

Navigate to `/preferencesetup` (register a new account or use a dev shortcut). Step through the 3 cards. The progress bar fill should animate smoothly to `33%` → `67%` → `100%` as you advance. The label should read "Step 1 of 3", "Step 2 of 3", "Step 3 of 3".

- [ ] **Step 5: Commit**

```
git add src/components/SbStepBar.vue src/views/PreferenceSetup.vue
git commit -m "feat: add SbStepBar component and wire into PreferenceSetup"
```

---

## Task 6: Dashboard Stat Card Stagger

**Files:**
- Modify: `src/views/Dashboard.vue`
- Modify: `src/views/TutorDashboard.vue`

Apply `sb-stagger-item` to stat tiles so they stagger in after data loads.

### Dashboard.vue

- [ ] **Step 1: Add stagger to the tutee stat grid**

In `src/views/Dashboard.vue`, find the outer `<div>` of each stat card (lines ~4–19). The cards are rendered with `v-for="(stat, index) in stats"`. The column wrapper is:

```html
      <div v-for="(stat, index) in stats" :key="index" class="col-md-3">
        <div class="card border-sb shadow-sm rounded-4 h-100 p-3 d-flex flex-row align-items-center stat-card">
```

Replace those two lines with:

```html
      <div
        v-for="(stat, index) in stats"
        :key="index"
        class="col-md-3"
      >
        <div
          class="card border-sb shadow-sm rounded-4 h-100 p-3 d-flex flex-row align-items-center stat-card sb-stagger-item"
          :style="{ animationDelay: `${index * 0.07}s` }"
        >
```

The cards stagger in as soon as the component mounts. The existing `<Transition name="fade">` on the inner `<h2>` handles the loading → loaded content transition separately.

- [ ] **Step 2: Verify Dashboard.vue stagger**

Hard-refresh the dashboard while logged in as a tutee. While the data is loading the cards are visible (no animation). When `loading` becomes false, the 4 stat tiles should stagger in — first card at 0ms, second at 70ms, third at 140ms, fourth at 210ms.

### TutorDashboard.vue

- [ ] **Step 3: Add stagger to the tutor stat cards**

In `src/views/TutorDashboard.vue`, the 3 stat cards are written as separate `<div class="col-md-4">` blocks (not a `v-for`). Identify the common stat card wrapper. The first card starts around line 6.

Add `sb-stagger-item` and a hardcoded `animationDelay` to the `.card` div in each of the 3 stat columns:

Card 1 (Total Sessions):
```html
        <div class="card border-sb rounded-4 p-4 shadow-sm h-100 sb-stagger-item" style="animation-delay: 0s;">
```

Card 2 (Avg Rating):
```html
        <div class="card border-sb rounded-4 p-4 shadow-sm h-100 sb-stagger-item" style="animation-delay: 0.07s;">
```

Card 3 (Earnings, the dark card):
```html
          class="card border-0 rounded-4 p-4 shadow-sm h-100 sb-stagger-item"
          style="background-color: var(--sb-dark); animation-delay: 0.14s;"
```

- [ ] **Step 4: Verify TutorDashboard stagger**

Log in as a tutor and hard-refresh `/tch-dashboard`. The 3 stat cards should stagger in with 70ms offsets.

- [ ] **Step 5: Commit**

```
git add src/views/Dashboard.vue src/views/TutorDashboard.vue
git commit -m "feat: stagger stat cards on dashboard mount (sb-stagger-item)"
```

---

## Task 7: Tab Indicator on Filter Pills

**Files:**
- Modify: `src/views/TuteeSessions.vue`
- Modify: `src/views/SessionsReports.vue`
- Modify: `src/views/TutorSessionsReports.vue`

All three views have the same pill-filter pattern. Apply the same changes to each.

The pattern in all three views:
```html
<button
  v-for="filter in filters"
  :key="filter.value"
  @click="currentFilter = filter.value"
  class="btn rounded-pill px-3 py-1 fw-semibold text-muted shadow-none sb-btn"
  :class="currentFilter === filter.value ? 'bg-white text-dark shadow-sm' : 'btn-light'"
>
```

- [ ] **Step 1: Update filter buttons in `TuteeSessions.vue`**

Find the filter button in `src/views/TuteeSessions.vue` and add `filter-tab` to the static class list and `:class` `active` binding:

```html
<button
  v-for="filter in filters"
  :key="filter.value"
  @click="currentFilter = filter.value"
  class="btn rounded-pill px-3 py-1 fw-semibold text-muted shadow-none sb-btn filter-tab"
  :class="currentFilter === filter.value ? ['bg-white', 'text-dark', 'shadow-sm', 'active'] : 'btn-light'"
>
```

- [ ] **Step 2: Add tab indicator CSS to `TuteeSessions.vue` scoped style**

In `<style scoped>` (or add one if it doesn't exist), add:

```css
.filter-tab {
  position: relative;
}
.filter-tab.active::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 12px;
  right: 12px;
  height: 2px;
  background: var(--sb-primary);
  border-radius: 999px;
  transform-origin: left center;
  animation: sb-tab-indicator var(--sb-t-normal) var(--sb-spring) both;
}
```

- [ ] **Step 3: Repeat for `SessionsReports.vue`**

Apply the same button class change and scoped CSS from Steps 1–2 to `src/views/SessionsReports.vue`. The filter button is at the same location (~lines 73–82).

- [ ] **Step 4: Repeat for `TutorSessionsReports.vue`**

Apply the same button class change and scoped CSS from Steps 1–2 to `src/views/TutorSessionsReports.vue`. The filter button is at the same location (~lines 68–78).

- [ ] **Step 5: Verify**

Visit `/tuteeSessions`, click between the filter pills (e.g., "All" → "Pending" → "Completed"). A green underline should animate in from the left each time the active pill changes. Same behavior in `/reports`.

- [ ] **Step 6: Commit**

```
git add src/views/TuteeSessions.vue src/views/SessionsReports.vue src/views/TutorSessionsReports.vue
git commit -m "feat: add tab indicator slide animation to session filter pills"
```

---

## Task 8: Accordion Body Transition (TutorProfile.vue)

**Files:**
- Modify: `src/views/TutorProfile.vue`

`TutorProfile.vue` has a subject accordion (`.subject-accordion-list`) where each body is toggled via `v-if="openSubjectCode === subject.subject_code"`. Currently the body appears instantly. Wrap it in a `<Transition>` with JS hooks for height animation.

- [ ] **Step 1: Wrap the accordion body in a `<Transition>` with JS hooks**

Find the accordion body block (around lines 172–179):

```html
      <div v-if="openSubjectCode === subject.subject_code" class="subject-accordion-body">
```

Replace with:

```html
      <Transition
        @before-enter="el => { el.style.maxHeight = '0'; el.style.opacity = '0' }"
        @enter="el => { el.offsetHeight; el.style.maxHeight = el.scrollHeight + 'px'; el.style.opacity = '1' }"
        @after-enter="el => { el.style.maxHeight = ''; el.style.opacity = '' }"
        @before-leave="el => { el.style.maxHeight = el.scrollHeight + 'px'; el.style.opacity = '1' }"
        @leave="el => { el.offsetHeight; el.style.maxHeight = '0'; el.style.opacity = '0' }"
        @after-leave="el => { el.style.maxHeight = ''; el.style.opacity = '' }"
      >
        <div v-if="openSubjectCode === subject.subject_code" class="subject-accordion-body">
```

And close the `<Transition>` tag after the accordion body's closing `</div>`:

```html
        </div>
      </Transition>
```

`el.offsetHeight` on the enter and leave hooks forces a browser reflow between the "before" and "after" style states, ensuring the transition fires.

- [ ] **Step 2: Update `.subject-accordion-body` CSS to support the transition**

In `src/views/TutorProfile.vue`'s `<style scoped>`, find `.subject-accordion-body`:

```css
.subject-accordion-body {
  padding: 0 18px 18px;
  display: grid;
  gap: 10px;
}
```

Replace with:

```css
.subject-accordion-body {
  padding: 0 18px 18px;
  display: grid;
  gap: 10px;
  overflow: hidden;
  transition: max-height var(--sb-t-slow) var(--sb-spring),
              opacity var(--sb-t-normal) ease;
}
```

The JS hooks on `@before-enter` and `@before-leave` manage the `max-height` and `opacity` states; the CSS `transition` handles the animation between them.

- [ ] **Step 3: Verify**

Go to `/tutor-profile` as a tutor. Click a subject accordion header. The body should smoothly expand downward (max-height transition + fade in). Click again — body collapses upward. The chevron icon should flip between up/down (already wired via `:class` — no change needed).

- [ ] **Step 4: Commit**

```
git add src/views/TutorProfile.vue
git commit -m "feat: animate accordion body expand/collapse in TutorProfile"
```

---

## Task 9: Success Pop (PostSessionPaymentView.vue + TutorPaymentScreen.vue)

**Files:**
- Modify: `src/views/PostSessionPaymentView.vue`
- Modify: `src/views/TutorPaymentScreen.vue`

Show an animated success checkmark + green border pulse after a payment action confirms.

### PostSessionPaymentView.vue

- [ ] **Step 1: Add `showSuccess` ref and trigger it on successful payment**

In `<script setup>` of `src/views/PostSessionPaymentView.vue`, add the ref after the existing refs:

```js
const showSuccess = ref(false)
```

In the `submitPayment` function, after `paymentStore.reset()` and before `router.push(...)`, add:

```js
showSuccess.value = true
await new Promise(resolve => setTimeout(resolve, 800))
```

This shows the success pop for 800ms before navigating away.

- [ ] **Step 2: Add success icon markup to the payment card**

Find the main payment card div (the one with class `card border-sb shadow-sm rounded-4 p-4`). Add the `:class` binding and the success icon:

```html
<div class="card border-sb shadow-sm rounded-4 p-4" :class="{ 'sb-success-card': showSuccess }">
  <Transition name="pop">
    <div v-if="showSuccess" class="success-icon-overlay">
      <div class="success-icon">✓</div>
    </div>
  </Transition>
  <!-- existing card content unchanged -->
```

- [ ] **Step 3: Add scoped CSS to `PostSessionPaymentView.vue`**

Add to `<style scoped>` (or create one):

```css
.success-icon-overlay {
  display: flex;
  justify-content: center;
  margin-bottom: 16px;
}
.success-icon {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: var(--sb-primary);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: 800;
}
.pop-enter-active {
  animation: sb-pop 350ms var(--sb-spring-fast) both;
}
```

### TutorPaymentScreen.vue

- [ ] **Step 4: Add success pop to `TutorPaymentScreen.vue`**

`TutorPaymentScreen.vue` currently has:
```js
const verify = (id) => {
  payments.value = payments.value.filter(p => p.id !== id)
  alert('Payment verified! Booking finalized.')
}
```

Replace the entire component with:

```vue
<template>
  <div class="p-4">
    <h2 class="fw-bold mb-4">Payment Verification</h2>

    <div class="card border-sb rounded-4 shadow-sm overflow-hidden" :class="{ 'sb-success-card': showSuccess }">
      <Transition name="pop">
        <div v-if="showSuccess" class="verify-success">
          <div class="success-icon">✓</div>
          <span class="ms-2 fw-semibold">Payment verified!</span>
        </div>
      </Transition>
      <div class="table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead class="bg-light">
            <tr>
              <th class="ps-4">Tutee</th>
              <th>Amount</th>
              <th>Status</th>
              <th class="text-end pe-4">Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="pay in payments" :key="pay.id">
              <td class="ps-4 fw-semibold">{{ pay.name }}</td>
              <td class="fw-bold">₱{{ pay.amount }}</td>
              <td><span class="badge bg-warning-subtle text-warning border border-warning">Pending</span></td>
              <td class="text-end pe-4">
                <button @click="verify(pay.id)" class="btn btn-sm bg-sb-primary text-white px-3 fw-bold sb-btn">Verify Paid</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useToastStore } from '@/stores/toast'

const toastStore = useToastStore()
const showSuccess = ref(false)
const payments = ref([
  { id: 1, name: 'Lia Salinas', amount: 250 },
  { id: 2, name: 'Reggie Cruz', amount: 500 }
])

const verify = (id) => {
  payments.value = payments.value.filter(p => p.id !== id)
  showSuccess.value = true
  toastStore.push('Payment verified! Booking finalized.')
  setTimeout(() => { showSuccess.value = false }, 1500)
}
</script>

<style scoped>
.verify-success {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 12px;
  background: rgba(0, 137, 90, 0.07);
  border-bottom: 1px solid rgba(0, 137, 90, 0.15);
  color: var(--sb-primary);
  font-size: 14px;
}
.success-icon {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--sb-primary);
  color: #fff;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 800;
}
.pop-enter-active {
  animation: sb-pop 350ms var(--sb-spring-fast) both;
}
</style>
```

- [ ] **Step 5: Verify**

Go to the tutor payment verification page. Click "Verify Paid". A success banner should pop in above the table with a green checkmark, and a toast should appear in the top-right. In PostSessionPaymentView, submit a payment — a checkmark should appear briefly before redirect.

- [ ] **Step 6: Commit**

```
git add src/views/PostSessionPaymentView.vue src/views/TutorPaymentScreen.vue
git commit -m "feat: add success pop animation on payment confirm"
```

---

## Task 10: Alert → Toast Migration (Wallet, Profile, Sessions)

**Files:**
- Modify: `src/views/TutorWallet.vue`
- Modify: `src/views/TutorProfile.vue`
- Modify: `src/views/TutorRequestedSessions.vue`

These are the views explicitly named in the spec as primary migration targets.

**The pattern for every file:** Add the import + store setup once, then replace each `alert(...)`.

### TutorWallet.vue

- [ ] **Step 1: Set up toast store in `TutorWallet.vue`**

In `<script setup>`, add after existing imports:

```js
import { useToastStore } from '@/stores/toast'
const toastStore = useToastStore()
```

- [ ] **Step 2: Replace all 5 `alert()` calls in `TutorWallet.vue`**

Find and replace each alert:

| Old | New |
|---|---|
| `alert('Select a receiving institution.')` | `toastStore.push('Select a receiving institution.', 'warning')` |
| `alert(error.response?.data?.error \|\| 'Unable to save payout destination.')` | `toastStore.push(error.response?.data?.error \|\| 'Unable to save payout destination.', 'error')` |
| `alert(cashoutError.value)` | `toastStore.push(cashoutError.value, 'error')` |
| `alert('Cash-out request submitted.')` | `toastStore.push('Cash-out request submitted.')` |
| `alert(result.error)` | `toastStore.push(result.error, 'error')` |

### TutorProfile.vue

- [ ] **Step 3: Set up toast store in `TutorProfile.vue`**

In `<script setup>`, add after existing imports:

```js
import { useToastStore } from '@/stores/toast'
const toastStore = useToastStore()
```

- [ ] **Step 4: Replace 2 `alert()` calls in `TutorProfile.vue`**

| Old | New |
|---|---|
| `alert('Profile Updated')` | `toastStore.push('Profile Updated')` |
| `alert('Profile update failed. Please try again.')` | `toastStore.push('Profile update failed. Please try again.', 'error')` |

### TutorRequestedSessions.vue

- [ ] **Step 5: Set up toast store in `TutorRequestedSessions.vue`**

In `<script setup>`, add after existing imports:

```js
import { useToastStore } from '@/stores/toast'
const toastStore = useToastStore()
```

- [ ] **Step 6: Replace 1 `alert()` call in `TutorRequestedSessions.vue`**

| Old | New |
|---|---|
| `alert(err.response?.data?.error \|\| 'Failed to save location. Please try again.')` | `toastStore.push(err.response?.data?.error \|\| 'Failed to save location. Please try again.', 'error')` |

- [ ] **Step 7: Verify**

Test a cash-out request in TutorWallet — should get a toast confirmation instead of a browser alert. Save profile in TutorProfile — should get a success toast in the top-right corner.

- [ ] **Step 8: Commit**

```
git add src/views/TutorWallet.vue src/views/TutorProfile.vue src/views/TutorRequestedSessions.vue
git commit -m "feat: migrate alert() to toastStore in wallet, profile, and sessions"
```

---

## Task 11: Alert → Toast Migration (Payments & Booking)

**Files:**
- Modify: `src/views/PostSessionPaymentView.vue`
- Modify: `src/views/PaymentScreenTutee.vue`
- Modify: `src/views/TuteeSessionDetailsFlow.vue`
- Modify: `src/views/TutorBookingDetailsFlow.vue`
- Modify: `src/views/BookingDetails.vue`

`TutorPaymentScreen.vue` was already migrated in Task 9.

For every file: add import + store, then replace each alert.

### PostSessionPaymentView.vue (3 remaining alerts — `showSuccess` toast was done in Task 9)

- [ ] **Step 1: Add toast store to `PostSessionPaymentView.vue`**

```js
import { useToastStore } from '@/stores/toast'
const toastStore = useToastStore()
```

- [ ] **Step 2: Replace remaining alerts in `PostSessionPaymentView.vue`**

| Old | New |
|---|---|
| `alert(error.response?.data?.error \|\| 'Unable to initiate payment. Please try again.')` | `toastStore.push(error.response?.data?.error \|\| 'Unable to initiate payment. Please try again.', 'error')` |
| `alert('Please select a payment method.')` | `toastStore.push('Please select a payment method.', 'warning')` |
| `alert('Please attach a receipt and enter the transaction reference.')` | `toastStore.push('Please attach a receipt and enter the transaction reference.', 'warning')` |
| `alert('Payment submitted. Waiting for tutor verification.')` | `toastStore.push('Payment submitted. Waiting for tutor verification.')` |
| `alert(error.response?.data?.error \|\| 'Unable to submit payment.')` | `toastStore.push(error.response?.data?.error \|\| 'Unable to submit payment.', 'error')` |

### PaymentScreenTutee.vue

- [ ] **Step 3: Add toast store to `PaymentScreenTutee.vue`**

```js
import { useToastStore } from '@/stores/toast'
const toastStore = useToastStore()
```

- [ ] **Step 4: Replace alerts in `PaymentScreenTutee.vue`**

| Old | New |
|---|---|
| `alert("No Sessions Selected.")` | `toastStore.push("No Sessions Selected.", 'warning')` |
| `alert("Please select a payment method.")` | `toastStore.push("Please select a payment method.", 'warning')` |
| `alert("Please attach a receipt and enter the transaction reference.")` | `toastStore.push("Please attach a receipt and enter the transaction reference.", 'warning')` |
| `alert("Booking Confirmed!")` | `toastStore.push("Booking Confirmed!")` |
| `alert(error.response?.data?.error \|\| "Something went wrong.")` | `toastStore.push(error.response?.data?.error \|\| "Something went wrong.", 'error')` |

### TuteeSessionDetailsFlow.vue

- [ ] **Step 5: Add toast store to `TuteeSessionDetailsFlow.vue`**

```js
import { useToastStore } from '@/stores/toast'
const toastStore = useToastStore()
```

- [ ] **Step 6: Replace alerts in `TuteeSessionDetailsFlow.vue`**

| Old | New |
|---|---|
| `alert('Session cancelled successfully.')` | `toastStore.push('Session cancelled successfully.')` |
| `alert(error.response?.data?.error \|\| 'Failed to cancel session.')` | `toastStore.push(error.response?.data?.error \|\| 'Failed to cancel session.', 'error')` |

### TutorBookingDetailsFlow.vue

- [ ] **Step 7: Add toast store to `TutorBookingDetailsFlow.vue`**

```js
import { useToastStore } from '@/stores/toast'
const toastStore = useToastStore()
```

- [ ] **Step 8: Replace alerts in `TutorBookingDetailsFlow.vue`**

| Old | New |
|---|---|
| `alert('Session marked as completed.')` | `toastStore.push('Session marked as completed.')` |
| `alert(error.response?.data?.error \|\| 'Failed to complete session.')` | `toastStore.push(error.response?.data?.error \|\| 'Failed to complete session.', 'error')` |
| `alert('Dev: session is ready for tutee payment.')` | `toastStore.push('Dev: session is ready for tutee payment.')` |
| `alert(error.response?.data?.error \|\| 'Failed to make session ready for payment.')` | `toastStore.push(error.response?.data?.error \|\| 'Failed to make session ready for payment.', 'error')` |

### BookingDetails.vue

- [ ] **Step 9: Add toast store to `BookingDetails.vue`**

```js
import { useToastStore } from '@/stores/toast'
const toastStore = useToastStore()
```

- [ ] **Step 10: Replace alerts in `BookingDetails.vue`**

| Old | New |
|---|---|
| `alert("Session marked as completed.")` | `toastStore.push("Session marked as completed.")` |
| `alert(error.response?.data?.error \|\| "Failed to complete session.")` | `toastStore.push(error.response?.data?.error \|\| "Failed to complete session.", 'error')` |

- [ ] **Step 11: Commit**

```
git add src/views/PostSessionPaymentView.vue src/views/PaymentScreenTutee.vue src/views/TuteeSessionDetailsFlow.vue src/views/TutorBookingDetailsFlow.vue src/views/BookingDetails.vue
git commit -m "feat: migrate alert() to toastStore in payment and booking flows"
```

---

## Task 12: Alert → Toast Migration (Forms, Search, Admin)

**Files:**
- Modify: `src/views/InitialBooking.vue`
- Modify: `src/views/FindTutors.vue`
- Modify: `src/views/TuteeProfile.vue`
- Modify: `src/views/TuteeSessionDetails.vue`
- Modify: `src/views/TutorDetails.vue`
- Modify: `src/views/TutorSchedule.vue`
- Modify: `src/views/TutorPreferenceSetup.vue`
- Modify: `src/views/PreferenceSetup.vue`
- Modify: `src/views/AdminUsers.vue`
- Modify: `src/views/AdminInstitutions.vue`
- Modify: `src/views/AdminWithdrawals.vue`
- Modify: `src/components/RatingStackModal.vue`

**The import pattern is the same for all files:**
```js
import { useToastStore } from '@/stores/toast'
const toastStore = useToastStore()
```

Add it once per file, then replace each `alert(...)`.

- [ ] **Step 1: Migrate `InitialBooking.vue` (4 validation alerts)**

After adding the import, replace:

| Old | New |
|---|---|
| `alert('Please select a session date.')` | `toastStore.push('Please select a session date.', 'warning')` |
| `alert('Please choose today or a future date.')` | `toastStore.push('Please choose today or a future date.', 'warning')` |
| `alert('Please choose a future start time.')` | `toastStore.push('Please choose a future start time.', 'warning')` |
| `alert('Please choose an end time after the start time.')` | `toastStore.push('Please choose an end time after the start time.', 'warning')` |

- [ ] **Step 2: Migrate `FindTutors.vue` (5 validation alerts)**

After adding the import, replace:

| Old | New |
|---|---|
| `alert('Please select a session date.')` | `toastStore.push('Please select a session date.', 'warning')` |
| `alert('Please choose today or a future date.')` | `toastStore.push('Please choose today or a future date.', 'warning')` |
| `alert('Please select a start and end time.')` | `toastStore.push('Please select a start and end time.', 'warning')` |
| `alert('Please choose a future start time.')` | `toastStore.push('Please choose a future start time.', 'warning')` |
| `alert('Please choose an end time after the start time.')` | `toastStore.push('Please choose an end time after the start time.', 'warning')` |

- [ ] **Step 3: Migrate `TuteeProfile.vue` (2 alerts)**

| Old | New |
|---|---|
| `alert("Profile updated successfully")` | `toastStore.push("Profile updated successfully")` |
| `alert("Failed to update profile")` | `toastStore.push("Failed to update profile", 'error')` |

- [ ] **Step 4: Migrate `TuteeSessionDetails.vue` (1 alert)**

| Old | New |
|---|---|
| `alert("Failed to submit rating. Please try again.")` | `toastStore.push("Failed to submit rating. Please try again.", 'error')` |

- [ ] **Step 5: Migrate `TutorDetails.vue` (5 alerts)**

| Old | New |
|---|---|
| `alert('Could not update favorite status. Please try again.')` | `toastStore.push('Could not update favorite status. Please try again.', 'error')` |
| `alert('You can book multiple slots only within the same week.')` | `toastStore.push('You can book multiple slots only within the same week.', 'warning')` |
| `alert('You can only book multiple sessions on the same day.')` | `toastStore.push('You can only book multiple sessions on the same day.', 'warning')` |
| `alert('The selected range includes unavailable in-between time slots.')` | `toastStore.push('The selected range includes unavailable in-between time slots.', 'warning')` |
| `alert('Booking Confirmed!')` | `toastStore.push('Booking Confirmed!')` |
| `alert(error.response?.data?.error \|\| 'Something went wrong.')` | `toastStore.push(error.response?.data?.error \|\| 'Something went wrong.', 'error')` |

- [ ] **Step 6: Migrate `TutorSchedule.vue` (7 alerts)**

| Old | New |
|---|---|
| `alert(error.response?.data?.error \|\| 'Unable to update the blocked date.')` | `toastStore.push(error.response?.data?.error \|\| 'Unable to update the blocked date.', 'error')` |
| `alert(error.response?.data?.error \|\| 'Unable to block the selected slots.')` | `toastStore.push(error.response?.data?.error \|\| 'Unable to block the selected slots.', 'error')` |
| `alert(error.response?.data?.error \|\| 'Unable to unblock the selected slots.')` | `toastStore.push(error.response?.data?.error \|\| 'Unable to unblock the selected slots.', 'error')` |
| `alert('Please complete all fields.')` | `toastStore.push('Please complete all fields.', 'warning')` |
| `alert('End time must be after start time.')` | `toastStore.push('End time must be after start time.', 'warning')` |
| `alert('All selected time slots already exist.')` | `toastStore.push('All selected time slots already exist.', 'warning')` |
| `` alert(`${createdCount} slot${createdCount > 1 ? 's were' : ' was'} added successfully.`) `` | `` toastStore.push(`${createdCount} slot${createdCount > 1 ? 's were' : ' was'} added successfully.`) `` |
| `alert('Something went wrong.')` | `toastStore.push('Something went wrong.', 'error')` |

- [ ] **Step 7: Migrate `TutorPreferenceSetup.vue` (1 alert)**

| Old | New |
|---|---|
| `alert("Could not save tutor profile.")` | `toastStore.push("Could not save tutor profile.", 'error')` |

- [ ] **Step 8: Migrate `PreferenceSetup.vue` (1 alert)**

| Old | New |
|---|---|
| `alert("Could not save preferences")` | `toastStore.push("Could not save preferences", 'error')` |

- [ ] **Step 9: Migrate `AdminUsers.vue` (2 alerts)**

| Old | New |
|---|---|
| `alert('Failed to update user status.')` | `toastStore.push('Failed to update user status.', 'error')` |
| `alert('Failed to delete user.')` | `toastStore.push('Failed to delete user.', 'error')` |

- [ ] **Step 10: Migrate `AdminInstitutions.vue` (2 alerts)**

| Old | New |
|---|---|
| `alert('Failed to update institution status.')` | `toastStore.push('Failed to update institution status.', 'error')` |
| `alert('Failed to add institution. Domain might already exist.')` | `toastStore.push('Failed to add institution. Domain might already exist.', 'error')` |

- [ ] **Step 11: Migrate `AdminWithdrawals.vue` (2 alerts)**

| Old | New |
|---|---|
| `alert('Update failed.')` (first occurrence) | `toastStore.push('Update failed.', 'error')` |
| `alert('Update failed.')` (second occurrence) | `toastStore.push('Update failed.', 'error')` |

- [ ] **Step 12: Migrate `RatingStackModal.vue` (1 alert)**

| Old | New |
|---|---|
| `alert('Failed to submit rating.')` | `toastStore.push('Failed to submit rating.', 'error')` |

- [ ] **Step 13: Final verification — no `alert(` left in src/**

Run: `grep -r "alert(" src/`

Expected: zero matches (or only comments/strings that aren't actual calls).

- [ ] **Step 14: Commit**

```
git add src/views/InitialBooking.vue src/views/FindTutors.vue src/views/TuteeProfile.vue src/views/TuteeSessionDetails.vue src/views/TutorDetails.vue src/views/TutorSchedule.vue src/views/TutorPreferenceSetup.vue src/views/PreferenceSetup.vue src/views/AdminUsers.vue src/views/AdminInstitutions.vue src/views/AdminWithdrawals.vue src/components/RatingStackModal.vue
git commit -m "feat: migrate all remaining alert() calls to toastStore"
```

---

## Verification Checklist (post all tasks)

Run through these manually after all tasks are complete:

- [ ] **Page transitions:** Sidebar click between Dashboard → Sessions → Profile. Content fades + slides in, sidebar stays fixed.
- [ ] **Modal scale-in:** Click sidebar logout. Modal should scale up from 0.94 → 1.
- [ ] **Stat stagger (tutee):** Hard-refresh `/dashboard`. 4 stat tiles stagger in left-to-right.
- [ ] **Stat stagger (tutor):** Hard-refresh `/tch-dashboard`. 3 stat cards stagger in.
- [ ] **Tab indicator:** Visit `/tuteeSessions`, click filter pills — green underline slides to the active one.
- [ ] **Toast success:** Submit a profile save — green toast in top-right, auto-dismisses in 3.5s.
- [ ] **Toast error:** Trigger a network failure — dark red toast appears.
- [ ] **Toast warning:** Try booking without selecting a date — amber/dark toast appears.
- [ ] **Toast dismiss:** Click a toast — it dismisses immediately.
- [ ] **Progress bar:** Load `/preferencesetup` — bar starts at 33%, advances to 67%, then 100%.
- [ ] **Accordion:** Open TutorProfile subject — body expands smoothly, chevron flips.
- [ ] **Success pop (tutor):** Click Verify Paid on TutorPaymentScreen — green pop banner + toast.
- [ ] **Reduced motion:** Enable "Reduce Motion" in OS settings — re-test page transitions and stagger; all should be instant.
- [ ] **No history replay:** Filter the sessions list — existing rows must NOT re-animate.
- [ ] **No alert() calls remaining:** `grep -r "alert(" src/` returns zero matches.
