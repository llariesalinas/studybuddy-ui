---
title: Ongoing-booking live status surface
date: 2026-06-14
status: In Progress
spec: ../specs/2026-06-14-ongoing-booking-live-status-design.md
---

# Ongoing-booking live status surface

## Status & Progress Summary

**Status:** Code complete, automated checks green; live-flow smoke pending - **Last updated:** 2026-06-14

Centralized the session check-in timing into an app-wide singleton store and added a
Grab-style persistent bottom dock bar so live status + venue/midpoint check-ins work on
every authenticated page, for both roles. Backend untouched.

- [x] Task 1 — `activeSession` store (timer, derivations, dismissal persistence)
- [x] Task 2 — `OngoingBookingBar.vue` dock card (both roles)
- [x] Task 3 — mount bar + global tutee modals in `App.vue`, wire polling lifecycle
- [x] Task 4 — refactor `TuteeSessionDetailsFlow.vue` to read from the store
- [x] Task 5 — verify: `npm run build` ✓, `npm run lint` clean on touched files ✓, `npm run test` 19 passed ✓, app boots with no console errors ✓
- [ ] Manual: drive the live venue/midpoint flow with an authenticated booking in its window (needs seed data + login)

## Goal

Make the live session experience flawless: a persistent bottom dock card follows the
user across every authenticated page showing live booking status, and the venue +
midpoint check-ins fire reliably regardless of which page the user is on.

## Approach

Hoist the timing/trigger logic out of `TuteeSessionDetailsFlow.vue` (where it dies on
navigation) into a singleton Pinia store driven by one ~30s poll. A new
`OngoingBookingBar.vue` and the two existing check-in modals mount once in the
authenticated shell of `App.vue`. See the spec for full rationale and field names.

Key decisions: both roles see the bar; tutee-only check-in modals; smart polling (no
WebSocket); global modal delivery; dismissals persisted per `bookingId:event`.

---

## Task 1: `activeSession` Pinia store

**Files:**
- Create: `src/stores/activeSession.js`

- [ ] Step 1: Create the store. It reuses `useSessionsStore` for data and owns the
  timer, the active-booking derivation, phase/dueCheckIn logic, and dismissal
  persistence (`localStorage` key `studybuddy_dismissed_checkins`). Reuse the
  `parseSessionDateTime` Manila-local parsing pattern from the session view.

```js
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { useSessionsStore } from '@/stores/completedSessions'
import { SESSION_POLL_INTERVAL_MS } from '@/config.js'

const DISMISSED_KEY = 'studybuddy_dismissed_checkins'
const ACTIVE_STATUSES = ['ongoing', 'upcoming']

const loadDismissed = () => {
  if (typeof window === 'undefined') return {}
  try {
    return JSON.parse(window.localStorage.getItem(DISMISSED_KEY) || '{}') || {}
  } catch {
    return {}
  }
}

const toMinutes = (timeValue) => {
  if (!timeValue) return 0
  const [h = 0, m = 0] = String(timeValue).split(':').map((p) => Number.parseInt(p, 10) || 0)
  return h * 60 + m
}

const parseDateTime = (dateValue, timeValue) => {
  if (!dateValue || !timeValue) return null
  const normalized = String(timeValue).length === 5 ? `${timeValue}:00` : timeValue
  const parsed = new Date(`${dateValue}T${normalized}`)
  return Number.isNaN(parsed.getTime()) ? null : parsed
}

export const useActiveSessionStore = defineStore('activeSession', () => {
  const sessionsStore = useSessionsStore()

  const currentTime = ref(new Date())
  const activeDetail = ref(null)
  const dismissed = ref(loadDismissed())
  let pollTimer = null

  const activeBooking = computed(() => {
    const now = currentTime.value.getTime()
    const candidates = sessionsStore.sessions
      .filter((s) => ACTIVE_STATUSES.includes(String(s.status || '').toLowerCase()))
      .filter((s) => {
        const start = parseDateTime(s.date, s.startTime)
        const end = parseDateTime(s.date, s.endTime)
        if (!start || !end) return false
        return now >= start.getTime() && now < end.getTime()
      })
      .sort((a, b) => {
        const dateDiff = new Date(a.date) - new Date(b.date)
        return dateDiff !== 0 ? dateDiff : toMinutes(a.startTime) - toMinutes(b.startTime)
      })
    return candidates[0] || null
  })

  const detailSession = computed(() => activeDetail.value?.session || null)
  const sessionStartAt = computed(() => parseDateTime(detailSession.value?.date, detailSession.value?.start_time))
  const sessionEndAt = computed(() => parseDateTime(detailSession.value?.date, detailSession.value?.end_time))
  const sessionMidpointAt = computed(() => {
    if (!sessionStartAt.value || !sessionEndAt.value) return null
    return new Date((sessionStartAt.value.getTime() + sessionEndAt.value.getTime()) / 2)
  })

  const isWithinWindow = computed(() => {
    if (!sessionStartAt.value || !sessionEndAt.value) return false
    const now = currentTime.value.getTime()
    return now >= sessionStartAt.value.getTime() && now < sessionEndAt.value.getTime()
  })

  const isConfirmed = computed(() => String(detailSession.value?.raw_status || '').toLowerCase() === 'confirmed')
  const isFaceToFace = computed(() => detailSession.value?.session_mode === 'F2F')
  const venueCheckIn = computed(() => activeDetail.value?.check_ins?.venue_confirm || null)
  const midpointCheckIn = computed(() => activeDetail.value?.check_ins?.midpoint_checkin || null)
  const preferredLocation = computed(() => detailSession.value?.preferred_location || '')

  const isDismissed = (event) => {
    const id = activeDetail.value?.id ?? activeBooking.value?.id
    return id != null && dismissed.value[`${id}:${event}`] === true
  }

  const venueDue = computed(() => (
    isConfirmed.value && isFaceToFace.value && isWithinWindow.value
    && !venueCheckIn.value && !isDismissed('venue')
  ))

  const midpointDue = computed(() => (
    isConfirmed.value && isWithinWindow.value && sessionMidpointAt.value
    && currentTime.value.getTime() >= sessionMidpointAt.value.getTime()
    && !midpointCheckIn.value && !isDismissed('midpoint') && !venueDue.value
  ))

  const dueCheckIn = computed(() => (venueDue.value ? 'venue' : midpointDue.value ? 'midpoint' : null))

  const sessionPhase = computed(() => {
    if (!sessionStartAt.value || !sessionEndAt.value) return 'before'
    const now = currentTime.value.getTime()
    if (now < sessionStartAt.value.getTime()) return 'before'
    if (now >= sessionEndAt.value.getTime()) return 'over'
    if (sessionMidpointAt.value && now >= sessionMidpointAt.value.getTime()) return 'midpoint'
    return 'venue-window'
  })

  const refreshActive = async () => {
    await sessionsStore.fetchSessions()
    const booking = activeBooking.value
    if (!booking) {
      activeDetail.value = null
      return
    }
    if (String(activeDetail.value?.id) !== String(booking.id) || true) {
      activeDetail.value = await sessionsStore.fetchSessionById(booking.id)
    }
  }

  const startPolling = () => {
    if (pollTimer) return
    currentTime.value = new Date()
    refreshActive()
    pollTimer = window.setInterval(() => {
      currentTime.value = new Date()
      refreshActive()
    }, SESSION_POLL_INTERVAL_MS)
  }

  const stopPolling = () => {
    if (pollTimer) {
      window.clearInterval(pollTimer)
      pollTimer = null
    }
    activeDetail.value = null
  }

  const persistDismissed = () => {
    if (typeof window !== 'undefined') {
      window.localStorage.setItem(DISMISSED_KEY, JSON.stringify(dismissed.value))
    }
  }

  const dismiss = (event) => {
    const id = activeDetail.value?.id ?? activeBooking.value?.id
    if (id == null) return
    dismissed.value = { ...dismissed.value, [`${id}:${event}`]: true }
    persistDismissed()
  }

  const confirmVenue = async (response) => {
    const id = activeDetail.value?.id ?? activeBooking.value?.id
    if (id == null) return
    activeDetail.value = await sessionsStore.confirmVenue(id, response)
  }

  const submitMidpointCheckIn = async (response) => {
    const id = activeDetail.value?.id ?? activeBooking.value?.id
    if (id == null) return
    activeDetail.value = await sessionsStore.submitMidpointCheckIn(id, response)
  }

  return {
    currentTime, activeDetail, activeBooking, dueCheckIn, sessionPhase,
    sessionStartAt, sessionEndAt, sessionMidpointAt, preferredLocation,
    isWithinWindow, startPolling, stopPolling, refreshActive, dismiss,
    confirmVenue, submitMidpointCheckIn,
  }
})
```

- [ ] Step 2: Commit — `git commit -m "feat: add activeSession store for app-wide session tracking"`

## Task 2: `OngoingBookingBar.vue` dock card

**Files:**
- Create: `src/components/OngoingBookingBar.vue`

- [ ] Step 1: Build a bottom dock card that renders only when `activeBooking` exists.
  Read from `useActiveSessionStore`. Show a status pill, the partner name + subject, the
  booked -> started -> midpoint -> ending timeline keyed off `sessionPhase` (and a
  "check-in due" accent when `dueCheckIn` is set), and an "Open" button. Route by role:
  tutee -> `tuteeSessionDetails`, tutor -> `booking-details`. Use `.bg-sb-primary` /
  `.text-sb-primary` / `.sb-*` classes and CSS vars only (no hardcoded hex). The dock is
  `position: fixed; bottom` within the authenticated shell.
- [ ] Step 2: Determine role via `useAuthStore().user?.role?.toLowerCase()`; derive the
  partner label from `activeDetail.tutor?.name` (tutee view) or `activeDetail.tutee?.name`
  (tutor view), falling back to the subject.
- [ ] Step 3: Commit — `git commit -m "feat: add OngoingBookingBar dock card"`

## Task 3: Mount bar + global modals in `App.vue`

**Files:**
- Modify: `src/App.vue`

- [ ] Step 1: Import `OngoingBookingBar`, `VenueConfirmModal`, `SessionCheckInModal`,
  `useActiveSessionStore`, `useToastStore`. Add `const activeSession = useActiveSessionStore()`.
- [ ] Step 2: In the authenticated shell (the `v-else` block, before `</main>`/`<SbToast/>`),
  render `<OngoingBookingBar v-if="authStore.isAuthenticated && !isPublicRoute" />` and,
  tutee-only, the two modals driven by `activeSession.dueCheckIn`.
- [ ] Step 3: Add local refs `isSubmittingCheckIn`, plus `dueCheckIn`-watching open state.
  Handlers call `activeSession.confirmVenue/submitMidpointCheckIn`; on `'no'`/`'issues'`
  open the existing support flow via `openSupport('Booking', id)`. Close handlers call
  `activeSession.dismiss('venue'|'midpoint')`.
- [ ] Step 4: In `onMounted`, when authenticated call `activeSession.startPolling()`
  (any role). In `logout()` and `onBeforeUnmount`, call `activeSession.stopPolling()`.
- [ ] Step 5: Verify `npm run build`; commit — `git commit -m "feat: surface ongoing booking bar and global check-ins app-wide"`

## Task 4: Refactor `TuteeSessionDetailsFlow.vue`

**Files:**
- Modify: `src/views/TuteeSessionDetailsFlow.vue`

- [ ] Step 1: Remove the local `checkInClock` interval, `currentTime` ref, the
  `shouldPromptVenueConfirmation` / `shouldPromptMidpointCheckIn` computeds, the two
  modal-open watchers, and the in-page `<VenueConfirmModal>` / `<SessionCheckInModal>`
  (these are now global). Keep the inline status display, the cancel/payment/rating flows.
- [ ] Step 2: Keep `onMounted` loading the session detail for the page itself; drop the
  interval setup/teardown that only fed the removed triggers.
- [ ] Step 3: Verify `npm run build`; commit — `git commit -m "refactor: read session check-ins from activeSession store"`

## Task 5: Verify

- [ ] `npm run lint` passes.
- [ ] `npm run build` passes.
- [ ] `npm run test` (vitest) passes — confirm existing store tests unaffected.

## Risks

- Double-fire if the page refactor (Task 4) is incomplete — both paths would open modals.
  Mitigation: Task 4 removes the page's modal mounts and triggers entirely.
- `refreshActive` always refetching detail each tick is a minor extra request; acceptable
  at 60s cadence. Could later short-circuit when the id is unchanged and no check-in due.
- Active-booking selection from the list relies on `status`/`date`/`startTime`/`endTime`
  fields from `/bookings/`; if a grouped multi-slot session reports merged times, the
  window check still holds (uses min start / max end via existing merge).

## Checks to run

- `npm run lint`, `npm run build`, `npm run test` all pass.
- Manual smoke per the spec's check list (start-time venue modal from a non-session page,
  midpoint modal, persistence of dismissals, tutor sees bar but no modals).

## Changelog

- **2026-06-14**: Plan created from approved spec; status In Progress.
- **2026-06-14**: Implemented all 5 tasks — added `src/stores/activeSession.js`
  (singleton poll + phase/dueCheckIn derivations + per-`bookingId:event` dismissal
  persistence), `src/components/OngoingBookingBar.vue` (both-role bottom dock card),
  mounted the bar + tutee-only global check-in modals in `App.vue` with start/stop
  polling on auth/logout, and stripped the duplicate timer/triggers/modals out of
  `TuteeSessionDetailsFlow.vue`. Verified: build passes, lint clean on touched files,
  vitest 19/19 pass, app boots with no console errors. Remaining: manual smoke of the
  live venue/midpoint flow against a seeded in-window booking.
