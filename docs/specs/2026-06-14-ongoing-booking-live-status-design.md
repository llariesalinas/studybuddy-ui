# Ongoing-booking live status surface — Design Spec

**Date:** 2026-06-14
**Status:** Approved for planning
**Stack:** Vue 3 (Composition API), Pinia, Vue Router, Bootstrap 5
**Spec drives plan:** `docs/plans/2026-06-14-ongoing-booking-live-status.md`

---

## Goal

Make the live session experience "flawless," Grab-style: while a booking is in its
session window, a **persistent bottom dock card** follows the user across every
authenticated page showing live status, and the venue + midpoint check-ins fire
**reliably regardless of which page the user is on** — not only when they happen to be
sitting on the session details page.

## What already exists (important)

The check-in feature shipped (plan `2026-06-08-venue-session-checkin-modals.md`,
status Done) but the timing/trigger logic lives **only inside**
`src/views/TuteeSessionDetailsFlow.vue`:

- A `setInterval` clock (`checkInClock`, 30s) updates a local `currentTime` ref
  (`TuteeSessionDetailsFlow.vue:636-643`).
- `shouldPromptVenueConfirmation` / `shouldPromptMidpointCheckIn` computeds
  (`:425-441`) gate the modals; watchers open them (`:618-634`).
- Modals: `src/components/VenueConfirmModal.vue`, `src/components/SessionCheckInModal.vue`.
- Store actions exist: `confirmVenue`, `submitMidpointCheckIn`
  (`src/stores/completedSessions.js:277-287`), plus `ongoingSessions` /
  `upcomingSessions` getters (`:295-305`).

**The flaw:** all of the above is mounted with the session page. Navigate away → the
interval is cleared (`onBeforeUnmount`, `:645-648`) → no prompts, no live status.
Dismissals are local refs, so they also reset on remount.

### Backend payload shape (already available — no backend changes)

| Source | Fields used |
|---|---|
| `GET /bookings/` (list, via `fetchSessions`) | `id`, `status`, `date`, `startTime`, `endTime`, `session_group_id` |
| `GET /bookings/:id/` (detail, via `fetchSessionById`) | `session.status`, `session.raw_status` (`confirmed`), `session.session_mode` (`F2F`), `session.date`, `session.start_time`, `session.end_time`, `check_ins.venue_confirm`, `check_ins.midpoint_checkin`, `tutor.name` |
| `POST /bookings/:id/venue-confirmation/` | body `{ response }` |
| `POST /bookings/:id/midpoint-check-in/` | body `{ response }` |

## Decisions (from clarification)

1. **Role scope:** both tutee and tutor see the live bar. The tutee additionally gets
   the venue + midpoint check-in modals; the tutor sees status only (no modals).
2. **Live updates:** smart polling — one app-wide ~30s timer refreshes the active
   booking and drives a local clock for start/midpoint triggers. No WebSocket.
3. **Check-in delivery:** the due check-in is a **centered global modal** that appears
   over whatever page the tutee is on; the bar shows a "check-in due" state as backup.
4. **Surface layout:** option A — **bottom dock card** persistent on every
   authenticated page, with a booked → started → midpoint → ending timeline and an
   "Open" action that routes to the session detail.

## Architecture

### New singleton store — `src/stores/activeSession.js`

A Pinia store is a process-wide singleton, which guarantees a single timer and a single
source of truth (eliminating the double-modal risk). It owns:

**State**
- `currentTime` (ref, updated by the timer)
- `activeBookingId` (ref)
- `activeDetail` (ref — the `fetchSessionById` payload for the active booking)
- `dismissed` (ref object keyed `"<bookingId>:<event>"`, mirrored to `localStorage`
  under `studybuddy_dismissed_checkins`)
- private `pollTimer`

**Derivations (getters / computed)**
- `activeBooking` — from `useSessionsStore().sessions`, pick the single best candidate:
  status `ongoing`; or status `upcoming` whose `date` + `startTime` is reached and whose
  `endTime` not yet passed. If several, choose the earliest by date+start.
- `sessionStartAt` / `sessionEndAt` / `sessionMidpointAt` — parsed from `activeDetail`
  (`session.date` + `session.start_time` / `end_time`), reusing the existing
  `parseSessionDateTime` logic (Manila-local `new Date('YYYY-MM-DDTHH:MM:SS')`).
- `isWithinSessionWindow` — `start <= currentTime < end`.
- `dueCheckIn` — `'venue'` when: face-to-face (`session_mode === 'F2F'`),
  `raw_status === 'confirmed'`, in window, no `check_ins.venue_confirm`, not dismissed.
  `'midpoint'` when: confirmed, in window, `currentTime >= midpoint`, no
  `check_ins.midpoint_checkin`, not dismissed, and venue is not currently due/open.
  Else `null`.
- `sessionPhase` — `before | venue-window | midpoint | ending | over` for the timeline.

**Actions**
- `startPolling()` — idempotent; sets `currentTime`, starts a 30s interval that updates
  `currentTime`, calls `refreshActive()`. Called from `App.vue` once authenticated.
- `stopPolling()` — clears the timer and active state. Called on logout.
- `refreshActive()` — `fetchSessions()`; if there is an `activeBooking`, ensure
  `activeDetail` is loaded/refreshed via `fetchSessionById`; if no active booking, clear
  `activeDetail` and (optionally) skip detail polling to avoid waste.
- `confirmVenue(response)` / `submitMidpointCheckIn(response)` — delegate to the existing
  sessions-store actions, then refresh `activeDetail`.
- `dismiss(event)` — record `"<id>:<event>"` in `dismissed` + `localStorage`.

### New component — `src/components/OngoingBookingBar.vue` (both roles)

- Reads `activeBooking`, `activeDetail`, `sessionPhase`, `dueCheckIn` from the store.
- Renders nothing when there is no active booking.
- Bottom dock card: status pill, tutor/tutee name + subject, the
  booked → started → midpoint → ending timeline, and an "Open" button.
- "Open" routes by role: tutee → `{ name: 'tuteeSessionDetails', params: { id } }`,
  tutor → `{ name: 'booking-details', params: { id } }`.
- Styling: `.bg-sb-primary` / `.text-sb-primary` and existing `.sb-*` patterns — no
  hardcoded hex.

### Global check-in modals (tutee only)

Mount `VenueConfirmModal.vue` and `SessionCheckInModal.vue` once at app level, opened by
watching `dueCheckIn`. Submit via the store; on `'no'` / `'issues'` route to the existing
support flow (same behavior as today). Tutor role never mounts these.

### Integration points

- **`src/App.vue`** (authenticated shell only, not public/admin-less routes): render
  `<OngoingBookingBar />` and the two tutee-only modals beside `<router-view>`; call
  `activeSession.startPolling()` when authenticated and `stopPolling()` on logout.
- **`src/views/TuteeSessionDetailsFlow.vue`**: remove the local `checkInClock`,
  `currentTime`, `shouldPrompt*` computeds, and modal-open watchers; read live state
  from the store instead. Keep the page's inline status display. This removes the
  duplicate trigger path so a check-in can never fire twice.

## Edge cases (the "flawless" requirements)

- Exactly one active session surfaced at a time (earliest by date+start).
- Venue modal never shown for online (`session_mode !== 'F2F'`) sessions.
- Dismissals persist per `bookingId:event` across navigation and reload (store +
  `localStorage`), so a dismissed prompt does not reappear.
- Polling stops when there are no upcoming/ongoing sessions; resumes when one appears.
- Tutor sees the bar but never the check-in modals.
- Bar/modals only mount inside the authenticated shell; never on public routes.
- No double-fire: the session detail page no longer triggers modals.

## Non-goals (YAGNI)

- No WebSocket/real-time push (polling is sufficient for a tutoring session cadence).
- No auto-navigation/redirect at session time (global modal + persistent bar cover it).
- No geolocation/GPS (venue check-in stays self-attestation, unchanged).
- No backend/schema/serializer changes.

## Checks to run

- `npm run lint` and `npm run build` pass.
- Manual: with a confirmed F2F booking, from a non-session page (e.g. dashboard), at
  start time the venue modal appears and the dock bar shows the active session; at the
  midpoint the check-in modal appears; answers persist and the bar reflects them; tutor
  account sees the bar but no modals; dismissed prompts stay dismissed after navigating
  and after reload.
