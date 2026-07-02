# Chat Accept / Reject Pending Sessions — Design Spec

**Date:** 2026-06-14
**Status:** Approved for planning
**Stack:** Vue 3 (Composition API), Pinia, Django REST
**Mockup:** [docs/artifacts/2026-06-14-chat-accept-reject-mockups.html](../../artifacts/2026-06-14-chat-accept-reject-mockups.html) (Option C)

---

## Problem

A tutor with a pending session can already **edit the final meeting location** from the
chat room banner (`ChatBanner.vue`, `status_intent === 'pending_location'`). But to
actually **accept or reject** that pending request they have to leave the conversation and
go to `TutorRequestedSessions.vue`. For convenience, the tutor should be able to accept or
reject the pending session without leaving the chat.

## Goal

Let the tutor accept or reject a pending session directly from the chat banner, alongside
the existing edit-location control. Tutees never see these controls.

## Scope

**Frontend-only.** The backend endpoints, the store-call pattern, and the booking `id` in
the banner context all already exist.

- `POST bookings/<id>/approve/` — `approve_booking` (`backend/studybuddy/views.py:2316`)
- `POST bookings/<id>/reject/` — `reject_booking` (`backend/studybuddy/views.py:2363`)
- Both already call `create_booking_event(...)`, which broadcasts `booking_context_updated`
  over the chat websocket — so the banner refreshes for both parties automatically.
- The banner context already carries the representative booking `id`
  (`serialize_booking_context`, `backend/studybuddy/chat/services.py:147`).

Out of scope: any backend change, reject reason / confirmation step (one-click reject, to
match `TutorRequestedSessions.vue`), tutee-side actions, online vs. F2F booking rules.

## Chosen design — Option C ("Confirm & Accept")

The tutor's pending banner shows:

- **F2F (`pending_location`):** an editable location chip + a primary **"Confirm & Accept"**
  button + a quiet **"Reject"** text button.
  - "Confirm & Accept" is the one-tap combine: if the location draft was edited, PATCH it
    first, then approve. If no location is set, block with the existing required-location
    error (F2F cannot be approved without a location).
- **Online (`pending`):** a primary **"Accept"** button + a quiet **"Reject"** text button.
  No location control.
- **Tutee:** unchanged — keeps the "waiting for confirmation" copy and, on F2F, the existing
  "Suggest change" control. No accept/reject.

One-click reject — no confirmation dialog, no reason — matching the existing requested-sessions
behavior.

## Data / store

Add two methods to `src/stores/chat.js`, mirroring the existing `updatePendingLocation`
(call the endpoint, then `await fetchRooms({ force: true })`):

```js
async function acceptBooking(bookingId) {
  const response = await api.post(`bookings/${bookingId}/approve/`)
  await fetchRooms({ force: true })
  return response.data
}

async function rejectBooking(bookingId) {
  const response = await api.post(`bookings/${bookingId}/reject/`)
  await fetchRooms({ force: true })
  return response.data
}
```

Both use the authenticated `api.js` instance. The booking id is `bannerContext.id`.
Export both from the store's return object alongside `updatePendingLocation`.

> The websocket `booking_context_updated` event already refreshes the banner; the
> `fetchRooms({ force: true })` is a consistency fallback, matching `updatePendingLocation`.

## Component — `src/components/ChatBanner.vue`

Add tutor-only controls to the two pending templates.

**State (script):**
- `accepting = ref(false)`, `rejecting = ref(false)` — drive disabled/spinner states.
- Reuse the existing `locationError` ref for failures from any of the three calls.
- Reuse the existing `locationDraft` / `editing` refs for the F2F location chip.

**`pending_location` (F2F), `isTutor` only:**
- Editable location chip (reuse existing `startEditing` / `saveLocation` flow for the Edit
  affordance).
- "Confirm & Accept" button → `confirmAndAccept()`:
  1. `const loc = locationDraft.value.trim()` — if empty, set `locationError` and return.
  2. If `loc !== bannerContext.preferred_location`, `await chatStore.updatePendingLocation(id, loc)`.
  3. `await chatStore.acceptBooking(bannerContext.id)`.
  4. On error, surface `error.response?.data?.error` in `locationError`.
- "Reject" text button → `reject()` → `chatStore.rejectBooking(bannerContext.id)`.

**`pending` (online), `isTutor` only:**
- "Accept" button → `accept()` → `chatStore.acceptBooking(bannerContext.id)`.
- "Reject" text button → `reject()`.

**Tutee branches:** unchanged.

**Styling:** reuse existing `.chat-banner__btn`, `.chat-banner__btn--primary`,
`.chat-banner__btn--ghost`. Add a `.chat-banner__btn--danger-text` (reject text link) and a
`.chat-banner__loc-chip` styled with existing CSS variables (`--sb-primary`, `--sb-danger-bs`,
`--sb-warning-text`). No hardcoded hex.

## Integration points

- No router changes, no new store, no backend changes.
- `isTutor` is already passed as a prop to `ChatBanner.vue` by `Chat.vue`.
- Loading/disabled states prevent double-submits.

## Edge cases

- **F2F accept with empty location:** blocked client-side with the existing required-location
  message; backend would also reject, but we stop it earlier.
- **Stale state (already accepted/rejected elsewhere):** the backend returns 400
  ("Only pending bookings can be approved/rejected."); surface `error.response.data.error`
  and let the forced `fetchRooms` reconcile the banner.
- **Negative wallet balance:** `approve_booking` returns 400 with a wallet message; surfaced
  the same way.
- **Double-click:** guarded by `accepting` / `rejecting` disabled flags.

## Checks to run

- `npm run lint` — passes clean.
- `npm run build` — succeeds.
- `npm run test` — existing suite stays green (add a chat-store test for `acceptBooking` /
  `rejectBooking` if the store is covered).
- Manual: tutor F2F pending banner → edit location → Confirm & Accept → banner flips to
  Confirmed; tutor online pending → Accept; tutor Reject → banner flips to Rejected; tutee
  view shows no accept/reject.
