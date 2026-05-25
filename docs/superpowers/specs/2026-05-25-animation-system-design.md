# Animation System Expansion — Design Spec
**Date:** 2026-05-25
**Status:** Approved — ready for implementation plan
**Scope:** App-wide animation layer 2 (entrance transitions, data micro-interactions, feedback & flow)

---

## Context

StudyBuddy already has a CSS-first haptics layer (`.sb-btn`, `.sb-interactive`, 4 keyframes, Chat.vue wiring) defined in `docs/superpowers/specs/2026-05-22-feel-haptics-design.md`. That work is complete.

This spec defines the **next animation layer**: 7 new animations across 3 categories. All animations must honour the constraints in `StudyBuddyDesign.md` (project root).

---

## Hard Constraints (from StudyBuddyDesign.md)

1. **Use only existing easing tokens** — `--sb-spring`, `--sb-spring-fast`, `--sb-t-quick` (120ms), `--sb-t-normal` (250ms), `--sb-t-slow` (400ms). Never hardcode a new `cubic-bezier`.
2. **Never animate history** — entrance animations apply only to newly rendered/mounted nodes. Existing list content must not replay on re-render.
3. **No new dependencies** — pure CSS + Vue `<Transition>` / `<TransitionGroup>`.
4. **Aurora blobs do not animate continuously** — foreground elements get the motion, not the background.
5. **Glass-first aesthetic** — modals use `rgba(255,255,255,0.86)` + `backdrop-filter: blur(24px)`, not flat white.
6. **Globals go in App.vue non-scoped `<style>`** — per-view wiring goes in the view's own `<style scoped>`.

---

## Design Token Already in App.vue :root

```css
--sb-spring:      cubic-bezier(0.16, 1, 0.3, 1);
--sb-spring-fast: cubic-bezier(0.34, 1.56, 0.64, 1);
--sb-t-quick:     120ms;
--sb-t-normal:    250ms;
--sb-t-slow:      400ms;   /* ← verify this is present; add if missing */
```

---

## Files Changed Summary

| File | Change |
|---|---|
| `src/App.vue` | Add 4 keyframes + `.sb-skeleton` class + modal auto-animation + page `<Transition>` + toast slot + toast store import |
| `src/stores/toast.js` | NEW — minimal toast store (message queue, auto-dismiss) |
| `src/components/SbToast.vue` | NEW — toast display component (renders store queue) |
| `src/components/SbStepBar.vue` | NEW — booking progress bar component |
| `src/views/Dashboard.vue` | Wire stat count-in stagger on mount |
| `src/views/TutorDashboard.vue` | Wire stat count-in stagger on mount |
| `src/views/TuteeSessions.vue` | Wire tab indicator slide on active filter |
| `src/views/TutorSessionsReports.vue` | Wire tab indicator slide |
| `src/views/SessionsReports.vue` | Wire tab indicator slide |
| `src/views/TutorProfile.vue` | Wire accordion expand transition |
| `src/views/PreferenceSetup.vue` | Wire accordion expand transition |
| `src/views/InitialBooking.vue` | Replace step indicator with `SbStepBar` |
| `src/views/TuteeSessionDetailsFlow.vue` | Replace step indicator with `SbStepBar` |
| `src/views/PostSessionPaymentView.vue` | Add success-pop on payment confirm |
| `src/views/TutorPaymentScreen.vue` | Add success-pop on verify confirm |
| All views with `alert()` calls | Replace with `toastStore.push(...)` |

---

## Layer A — View & Component Entrance Transitions

### A1. `sb-stagger-in` (global keyframe + utility)

**What:** Cards, stat tiles, and list rows stagger in on page mount — each child 70ms after the previous.

**Keyframe to add to App.vue global style:**
```css
@keyframes sb-stagger-in {
  from { opacity: 0; transform: translateY(10px); }
  to   { opacity: 1; transform: translateY(0); }
}
```

**Usage pattern (per-view wiring):**
```html
<!-- In each stat card or list row -->
<div
  class="card sb-stagger-item"
  :style="{ animationDelay: `${index * 0.07}s` }"
>
```
```css
/* In App.vue global */
.sb-stagger-item {
  animation: sb-stagger-in var(--sb-t-normal) var(--sb-spring) both;
  opacity: 0;
}
```

**Rule:** Only wrap elements inside `v-if` blocks or after `onMounted` resolves — never on `v-for` lists that are re-rendered on filter change (that would animate history).

**Wire in:** `Dashboard.vue` stat cards (4 tiles), `TutorDashboard.vue` stat cards.

---

### A2. `sb-scale-in` — Modal Auto-Animation

**What:** Bootstrap modals scale from 0.94→1 + fade on open. No per-modal changes needed — single global selector.

**CSS to add to App.vue global style:**
```css
@keyframes sb-scale-in {
  from { opacity: 0; transform: scale(0.94); }
  to   { opacity: 1; transform: scale(1); }
}

.modal.show .modal-content {
  animation: sb-scale-in var(--sb-t-normal) var(--sb-spring) both;
}
```

**No per-file wiring needed.** All Bootstrap modals get this automatically.

---

### A3. Page Route Transition

**What:** Route changes fade + slide the `<router-view>` content in softly. The aurora background and sidebar stay static.

**Change in `src/App.vue` template:**
```html
<!-- Replace bare <router-view /> with: -->
<Transition name="page" mode="out-in">
  <router-view :key="route.name" />
</Transition>
```

**CSS to add to App.vue global style:**
```css
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

**Note:** Use `mode="out-in"` so the leaving page fully fades before the entering page appears — prevents two views overlapping on the glass background.

---

## Layer B — Data & State Micro-interactions

### B1. `sb-skeleton` — Global Shimmer Utility

**What:** Standardises skeleton loading across all views. Already used in `Dashboard.vue` and `TutorWallet.vue` with ad-hoc styles — replace those with the global class.

**Keyframe + class to add to App.vue global style:**
```css
@keyframes sb-shimmer {
  0%   { background-position: -600px 0; }
  100% { background-position: 600px 0; }
}

.sb-skeleton {
  background: linear-gradient(
    90deg,
    rgba(226, 232, 240, 0.8) 25%,
    rgba(203, 213, 225, 0.9) 50%,
    rgba(226, 232, 240, 0.8) 75%
  );
  background-size: 600px 100%;
  animation: sb-shimmer 1.6s ease-in-out infinite;
  border-radius: var(--sb-r-md, 12px);
}
```

**Views to update:** Replace any inline shimmer/placeholder CSS in `Dashboard.vue`, `TutorWallet.vue`, `TutorDashboard.vue`, `TutorRequestedSessions.vue` with `class="sb-skeleton"`.

---

### B2. Stat Count-In (Dashboard entrance)

**What:** Stat number tiles slide up + fade in after data resolves, staggered per tile. This is the `sb-stagger-in` keyframe applied specifically to stat values after loading resolves.

**Pattern in `Dashboard.vue` and `TutorDashboard.vue`:**
```html
<div
  v-for="(stat, index) in stats"
  :key="index"
  class="stat-card sb-stagger-item"
  :style="!loading ? { animationDelay: `${index * 0.07}s` } : {}"
>
```

The stat number `<h2>` inside the card also gets `sb-stagger-item` with a slightly longer delay so the label appears first, number second.

---

### B3. Tab Indicator Slide

**What:** When the active filter pill/tab changes, a green underline slides to the new active item using `::after` + `transform: scaleX`.

**CSS to add per-view (scoped) in `TuteeSessions.vue`, `SessionsReports.vue`, `TutorSessionsReports.vue`:**
```css
.filter-tab-group {
  position: relative;
}
.filter-tab {
  position: relative;
}
.filter-tab.active::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--sb-primary);
  transform-origin: left center;
  animation: sb-tab-indicator var(--sb-t-normal) var(--sb-spring) both;
}
```

**Keyframe to add to App.vue global:**
```css
@keyframes sb-tab-indicator {
  from { transform: scaleX(0); opacity: 0; }
  to   { transform: scaleX(1); opacity: 1; }
}
```

**Template pattern:** The `active` class already exists on filter buttons — just add the CSS. No JS changes needed.

---

## Layer C — Feedback & Flow Animations

### C1. Toast Notification System

**What:** A global, non-blocking toast replaces all `alert()` calls in the app. Slides in from top-right with spring-fast overshoot. Auto-dismisses after 3500ms.

**New file: `src/stores/toast.js`**
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

**New file: `src/components/SbToast.vue`**
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
.sb-toast--error { background: #7f1d1d; }
.sb-toast--warning { background: #78350f; }
.sb-toast-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--sb-primary);
  flex-shrink: 0;
}
.sb-toast--error .sb-toast-dot { background: #fca5a5; }
.sb-toast--warning .sb-toast-dot { background: #fcd34d; }

.toast-enter-active {
  animation: sb-toast-in var(--sb-t-normal) var(--sb-spring-fast) both;
}
.toast-leave-active {
  transition: opacity var(--sb-t-quick) ease, transform var(--sb-t-quick) ease;
}
.toast-leave-to { opacity: 0; transform: translateY(-6px); }
</style>
```

**Keyframe to add to App.vue global:**
```css
@keyframes sb-toast-in {
  from { opacity: 0; transform: translateY(-14px) scale(0.95); }
  to   { opacity: 1; transform: translateY(0) scale(1); }
}
```

**Mount in App.vue template:**
```html
<SbToast />  <!-- add just before closing </template> -->
```

**Replace `alert()` calls with:**
```js
import { useToastStore } from '@/stores/toast'
const toastStore = useToastStore()

// Instead of: alert('Cash-out request submitted.')
toastStore.push('Cash-out request submitted.')

// Instead of: alert(result.error)
toastStore.push(result.error, 'error')
```

**Views with `alert()` to migrate:** `TutorWallet.vue` (2 alerts), `TutorRequestedSessions.vue` (implicit error handling), `TutorProfile.vue`.

---

### C2. Booking Progress Bar (`SbStepBar`)

**What:** A reusable step-progress component used in multi-step booking flows. Fill width is driven by `currentStep / totalSteps`. Animates on mount and on step change.

**New file: `src/components/SbStepBar.vue`**
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
defineProps({ current: { type: Number, required: true }, total: { type: Number, required: true } })
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

**Wire in:**
- `src/views/InitialBooking.vue` — identify the existing step indicator and replace with `<SbStepBar :current="step" :total="3" />`
- `src/views/TuteeSessionDetailsFlow.vue` — same pattern

---

### C3. Accordion Expand / Collapse

**What:** Section toggles in `TutorProfile.vue` and `PreferenceSetup.vue` animate content open/close. The "+" icon rotates 45° and fills with `--sb-primary` when open — per `StudyBuddyDesign.md` spec.

**Pattern — wrap accordion content in a Vue `<Transition>` with JS hooks for height:**

```html
<button class="accordion-toggle" @click="open = !open" :aria-expanded="open">
  Edit Bio
  <span class="accordion-icon" :class="{ 'accordion-icon--open': open }">+</span>
</button>
<Transition
  @enter="el => { el.style.maxHeight = el.scrollHeight + 'px' }"
  @leave="el => { el.style.maxHeight = '0' }"
>
  <div v-if="open" class="accordion-body">
    <!-- content -->
  </div>
</Transition>
```

**CSS to add (scoped in each view):**
```css
.accordion-icon {
  display: inline-block;
  transition: transform var(--sb-t-normal) var(--sb-spring),
              color var(--sb-t-quick) ease;
}
.accordion-icon--open {
  transform: rotate(45deg);
  color: var(--sb-primary);
}
.accordion-body {
  overflow: hidden;
  max-height: 0;
  transition: max-height var(--sb-t-slow) var(--sb-spring),
              opacity var(--sb-t-normal) ease;
}
/* When Vue Transition sets maxHeight via JS hook, fade in content */
.v-enter-from.accordion-body { opacity: 0; }
.v-enter-to.accordion-body   { opacity: 1; }
.v-leave-to.accordion-body   { opacity: 0; }
```

---

### C4. Success State Pop

**What:** On payment confirmation or session verification, a success checkmark pops in using the existing `sb-pop` keyframe. A brief green border pulse appears on the containing card.

**Keyframe to add to App.vue global** (extends existing `sb-pop`):
```css
@keyframes sb-success-border {
  0%   { box-shadow: 0 0 0 0 rgba(0, 137, 90, 0.5); }
  60%  { box-shadow: 0 0 0 6px rgba(0, 137, 90, 0); }
  100% { box-shadow: none; }
}

.sb-success-card {
  animation: sb-success-border 600ms var(--sb-spring) both;
}
```

**Pattern — in `PostSessionPaymentView.vue` and `TutorPaymentScreen.vue`:**
```js
// After API confirms success:
showSuccess.value = true
```
```html
<div :class="{ 'sb-success-card': showSuccess }">
  <Transition name="pop">
    <div v-if="showSuccess" class="success-icon">✓</div>
  </Transition>
</div>
```
```css
/* Scoped, per-view */
.pop-enter-active { animation: sb-pop 350ms var(--sb-spring-fast) both; }
.success-icon {
  width: 48px; height: 48px; border-radius: 50%;
  background: var(--sb-primary); color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-size: 22px; font-weight: 800;
}
```

---

## Accessibility — prefers-reduced-motion

**Add to App.vue global style (single block covers everything):**
```css
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

This is a catch-all. No per-animation or per-component work needed.

---

## What Is NOT in This Spec

- No changes to Chat.vue (fully implemented in the previous haptics spec)
- No changes to LandingPage.vue (has its own animation system)
- No continuous aurora blob animations
- No third-party animation libraries
- No JS-driven number counting (stat count-in is CSS entrance only, not a number ticker)

---

## Verification Checklist

After implementation:
- [ ] Page transitions: navigate between Dashboard → Sessions → Profile — content should fade/slide in softly, sidebar stays static
- [ ] Modal scale-in: open the logout modal, any booking modal — should scale from 0.94→1
- [ ] Stat stagger: hard-refresh Dashboard — stat tiles should stagger in after data loads
- [ ] Skeleton: visit a page while throttling network — should show consistent shimmer
- [ ] Tab slide: click filter pills in TuteeSessions — green underline should slide to the active pill
- [ ] Toast: trigger a success action (confirm session, save profile) — toast should pop in from top-right and auto-dismiss in 3.5s
- [ ] Toast error: trigger a failure — dark red toast appears
- [ ] Progress bar: step through InitialBooking — bar fills smoothly on each step advance
- [ ] Accordion: open/close a profile section — content slides, "+" rotates to "×" in green
- [ ] Success pop: complete a payment — checkmark pops in, card border pulses green
- [ ] Reduced motion: enable "Reduce Motion" in OS accessibility settings — all animations should be instant (1ms)
- [ ] No history replay: re-filter a list — existing items must NOT re-animate
