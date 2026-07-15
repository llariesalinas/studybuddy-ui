---
title: Face-to-face campus location modal
date: 2026-07-07
status: Approved
spec:
---

# Face-to-face campus location modal

<!-- LIVING SUMMARY: keep this section and the Changelog current on every edit -->

## Status & Progress Summary

**Status (2026-07-07): Approved — handed off for implementation.** Grilled end-to-end (9
decisions) via `/grill-with-docs`, domain terms recorded in `CONTEXT.md`, ADR 0007 written for the
not-persisted liability acknowledgment decision. All open items (icons, copy, component contract,
mount/revisit edge case) have since been pinned down below — nothing left for the implementer to
decide. No code written yet.

## Handoff note (read this first)

This plan is written to be followed **exactly**, without re-deciding anything already decided
below. Every copy string, class name, prop/emit name, icon, and edge-case behavior in this
document is final — do not substitute different wording, a different component API, or different
icons "for consistency" or any other reason. If you hit something this plan does not cover, stop
and flag it rather than improvising a resolution.

Three files only:

1. **New file**: `src/components/CampusLocationModal.vue`
2. **Edit**: `src/views/InitialBooking.vue`
3. **Edit**: `src/views/FindTutors.vue`

No backend changes, no store changes to `src/stores/initialbookingprefs.js` or
`src/stores/findTutors.js` (the campus-type choice is local component state only — see
[ADR 0007](../adr/0007-off-campus-liability-acknowledgment-not-persisted.md)).

## Goal

Replace the current free-text-only "Preferred Location" field with a guided modal flow that
forces a Tutee booking a Face-to-face session to declare whether it's Inside or Outside campus,
and to acknowledge a liability disclaimer before entering an off-campus location — so students
don't casually type an off-campus address without seeing that Studybuddy isn't liable for those
sessions.

## Component: `src/components/CampusLocationModal.vue`

Build this first; both views consume it identically.

### Props / Emits contract (exact)

```js
const props = defineProps({
  open: { type: Boolean, required: true },
})
const emit = defineEmits(['update:open', 'select', 'cancel'])
```

- Parent controls visibility via `v-model:open="showCampusModal"`.
- `select` fires with payload `'inside'` or `'outside'` exactly once, when the flow completes
  successfully (Inside Campus clicked, or Outside Campus → "Yes, Continue" clicked). The component
  also emits `update:open` with `false` in the same handler to close itself — the parent does not
  need a separate close call.
- `cancel` fires when the *first* screen (campus choice) is dismissed without a choice (X button or
  backdrop click). The component also emits `update:open` with `false`.
- Dismissing the *second* screen (liability confirm) — via "Go Back", the X button, or backdrop
  click, all three behave identically — does **not** emit `cancel` and does **not** close the
  modal. It returns to the first screen. Only the first screen's dismissal cancels.

### Internal state

```js
const screen = ref('choice') // 'choice' | 'confirm'

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) screen.value = 'choice'
  },
)
```

Resetting `screen` to `'choice'` whenever the modal opens ensures a fresh flow every time,
regardless of where the user left off last time.

### Template structure

Model the modal chrome after `src/components/CashInModal.vue` (dark backdrop div + `modal fade
show d-block` + `modal-dialog modal-dialog-centered` + `modal-content` with `modal-header
border-0` / body / `modal-footer border-0`, `sb-btn` on all buttons). Do not import or reuse
`CashInModal.vue`'s scoped styles directly — write new scoped CSS for this component following the
same structural pattern (own `.btn-close`, own primary/secondary button classes).

**Screen `'choice'`:**

- Header: title `Choose Meeting Location`, close button (`btn-close`) → calls a `dismissChoice()`
  handler that emits `cancel` then `update:open(false)`.
- Backdrop click → same `dismissChoice()` behavior.
- Body: two full-width buttons, stacked or side-by-side (match `.mode-button-group` grid pattern
  from `InitialBooking.vue` — `grid-template-columns: repeat(2, minmax(0, 1fr))`, `gap: 8px`):
  - **Inside Campus** — icon `bi-building-fill`, label text exactly `Inside Campus`. Click →
    `emit('select', 'inside')` then `emit('update:open', false)`.
  - **Outside Campus** — icon `bi-signpost-split-fill`, label text exactly `Outside Campus`. Click
    → sets `screen.value = 'confirm'` (does not close the modal, does not emit yet).

**Screen `'confirm'`:**

- Header: title `Off-Campus Session`, close button → calls `backToChoice()` handler that sets
  `screen.value = 'choice'` (no emit).
- Backdrop click → same `backToChoice()` behavior.
- Body text, exact copy:
  > Sessions held outside CPU campus are not covered by StudyBuddy. Please meet in a safe, public
  > location. Are you sure you want to continue?
- Footer buttons:
  - **Go Back** (secondary style, left) → `backToChoice()`.
  - **Yes, Continue** (primary style, right) → `emit('select', 'outside')` then
    `emit('update:open', false)`.

## Wiring into `src/views/InitialBooking.vue`

1. Import and register `CampusLocationModal`.
2. Add local state (component-local `ref`s, not store fields):
   ```js
   const showCampusModal = ref(false)
   const campusLocationType = ref(null) // 'inside' | 'outside' | null
   ```
3. Modify `selectMode` (currently at `src/views/InitialBooking.vue:189`):
   ```js
   const selectMode = (value) => {
     store.selectedMode = value

     if (value === 'Face-to-face') {
       showCampusModal.value = true
     } else {
       store.selectedLocation = ''
       campusLocationType.value = null
     }
   }
   ```
4. Add handlers:
   ```js
   const onCampusTypeSelected = (type) => {
     campusLocationType.value = type
   }

   const onCampusModalCancelled = () => {
     store.selectedMode = null
     store.selectedLocation = ''
     campusLocationType.value = null
   }
   ```
5. **Mount/revisit edge case** — `campusLocationType` is component-local state, but
   `store.selectedMode` can already be `'Face-to-face'` on mount (persisted Pinia store, e.g. user
   navigated to `/find-tutors` and back). Add to the existing `onMounted` block: if
   `store.selectedMode === 'Face-to-face'` and `campusLocationType.value` is `null`, set
   `showCampusModal.value = true` so the user re-confirms the campus type rather than seeing a
   mode selected with no location field. Do not silently keep the stale `store.selectedLocation`
   text visible without a campus-type label — the field must stay hidden until
   `campusLocationType` is set again.
6. Replace the existing inline location block (currently `src/views/InitialBooking.vue:47-56`):
   ```html
   <div v-if="store.selectedMode === 'Face-to-face' && campusLocationType" class="mb-3">
     <div class="d-flex justify-content-between align-items-center mb-1">
       <label class="form-label fw-semibold small mb-0">
         Location ({{ campusLocationType === 'inside' ? 'Inside Campus' : 'Outside Campus' }})
       </label>
       <button
         type="button"
         class="btn btn-link btn-sm p-0"
         @click="showCampusModal = true"
       >
         Change
       </button>
     </div>
     <input
       type="text"
       v-model="store.selectedLocation"
       class="form-control border-sb shadow-none sb-field"
       placeholder="e.g. Library Room 3, Cafeteria..."
       required
     />
   </div>

   <CampusLocationModal
     v-model:open="showCampusModal"
     @select="onCampusTypeSelected"
     @cancel="onCampusModalCancelled"
   />
   ```
   Place the `<CampusLocationModal>` tag as a sibling near the end of the `<form>`, not nested
   inside any conditional block — modals render as fixed-position overlays.

## Wiring into `src/views/FindTutors.vue`

Same component, adapted for the refine-filters panel where mode is chosen via `SbSelectModal`
(`modeModel`, currently `src/views/FindTutors.vue:24-32`) and is clearable (`Any Mode` = `null` is
a valid state, unlike `InitialBooking.vue` where a mode is always required).

1. Import and register `CampusLocationModal`.
2. Add the same two local refs (`showCampusModal`, `campusLocationType`).
3. Add a watcher on `modeModel`:
   ```js
   watch(modeModel, (newMode, previousMode) => {
     if (newMode === 'Face-to-face' && previousMode !== 'Face-to-face') {
       showCampusModal.value = true
     }
     if (newMode !== 'Face-to-face') {
       campusLocationType.value = null
     }
   })
   ```
4. Add the same `onCampusTypeSelected` / `onCampusModalCancelled` handlers as InitialBooking, except
   `onCampusModalCancelled` sets `modeModel = null` (clears to "Any Mode") instead of
   `store.selectedMode = null` — match whatever the existing clearable-mode reset pattern already
   uses in this file for consistency (check how the "Any Mode" clear button already resets
   `modeModel` and mirror it exactly, do not invent a new reset path).
5. Same mount-revisit handling as Step 5 above: if `modeModel.value === 'Face-to-face'` on mount
   and `campusLocationType.value` is `null`, open the modal.
6. Change the location field's `v-if` (currently `src/views/FindTutors.vue:36`) from
   `modeModel === 'Face-to-face'` to `modeModel === 'Face-to-face' && campusLocationType`, and add
   the same label-with-"Change"-link treatment as InitialBooking (adapt to this panel's smaller
   `col-lg-3 col-md-3` column width — keep the label/Change link on one line if it fits, wrap if
   not; do not shrink the column width to force a fit).
7. Place `<CampusLocationModal>` as a sibling near the end of the `<form>`.

## Risks

- Two integration points means the shared component's contract must fit both a required-mode flow
  (InitialBooking) and a clearable-mode flow (FindTutors) — the prop/emit contract above is
  designed to be flow-agnostic (it only ever reports a campus-type choice or a cancellation; it
  never assumes what "cancel" should reset to). Do not let one view's requirements leak into the
  component itself.
- Since the liability acknowledgment isn't persisted, a future request for an actual audit trail
  will require backend changes — flagged in ADR 0007, not a blocker now.
- `store.selectedLocation` staying free-text (no structured campus-type field sent anywhere)
  could confuse a future reader expecting Inside/Outside campus to be recorded on the Booking —
  mitigated by the CONTEXT.md glossary entry, not by any code change.

## Checks to run

- `npm run lint`
- `npm run build`
- Manual verification in the browser, both on `InitialBooking.vue` and `FindTutors.vue`:
  1. Face-to-face → Inside Campus → location field appears labeled `Location (Inside Campus)`.
  2. Face-to-face → Outside Campus → confirm modal appears with the exact copy above → "Yes,
     Continue" → location field appears labeled `Location (Outside Campus)`.
  3. Face-to-face → Outside Campus → confirm modal → "Go Back" → returns to the choice screen (not
     fully closed, not mode reset).
  4. Face-to-face → Outside Campus → confirm modal → X button or backdrop click → same as "Go
     Back" (returns to choice screen).
  5. Face-to-face → choice modal → X button or backdrop click (no choice made) → mode resets to
     unselected (InitialBooking) / clears to "Any Mode" (FindTutors).
  6. After a campus type is set, click "Change" → reopens the choice modal, fresh (`screen` resets
     to `'choice'` even if they'd previously gone through the confirm screen).
  7. Navigate away with Face-to-face + a campus type already chosen, then back to the same view →
     modal reopens automatically per the mount/revisit edge case (Step 5 in each wiring section).

## Changelog

| Date | Change |
|------|--------|
| 2026-07-07 | Created plan from the `/grill-with-docs` session (9 decisions); added Status & Progress Summary and Changelog sections per the living-plan convention |
| 2026-07-07 | Rewritten as an exact implementation handoff for Codex: pinned down the component's props/emits contract, exact copy/icons, template structure, wiring code for both views, and the mount/revisit edge case that was previously undecided |
