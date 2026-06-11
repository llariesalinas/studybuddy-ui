---
title: Venue confirmation modal + mid-session check-in modal
date: 2026-06-08
status: Done
spec:
---

# Venue confirmation modal + mid-session check-in modal

## Status & Progress Summary

**Status:** Done - **Last updated:** 2026-06-11

Implemented as tutee self-attestation with two booking-scoped check-in endpoints.
Venue confirmation appears for face-to-face sessions during the active session window;
the midpoint check-in appears after the computed halfway point. Responses are stored in
`SessionCheckIn`, returned from booking detail, and shown on the tutor booking detail
page. "No" / "having issues" answers open the existing support flow after saving.

## Goal

Add (a) a modal at session start where the tutee self-confirms they're at the venue,
logged for tracking, and (b) a standalone popup mid-session asking "Is your session
going well?"

## Approach

Current state: there is **no** geolocation infrastructure — `Booking.preferred_location`
(`backend/studybuddy/models.py` ~line 529) is a plain text field, no lat/long anywhere,
no `navigator.geolocation` usage, and no `session_started_at`/`ended_at` timestamps
(session timing is inferred from `session_date` + the linked `TutorAvailability.time_slot`).
Reusable modal patterns exist — `SupportModal.vue`/`RatingStackModal.vue` use Vue 3
Teleport with close-emit conventions.

Decisions: venue check is **self-attestation** (Yes/No "Confirm you're at the venue",
no GPS/geocoding), and the mid-session check-in is a **standalone popup modal** (not
built on the existing chat feature). Both choices avoid building new geolocation
infrastructure and a parallel chat-injection mechanism.

## Steps

1. Backend: add a small `SessionCheckIn` model (booking FK, `event_type`:
   `venue_confirm` | `midpoint_checkin`, `response`, `responded_at`) rather than
   bolting one-off columns onto `Booking` — keeps the log append-only and queryable.
2. Backend: add endpoints to record a venue confirmation and a check-in response.
3. Frontend: build `VenueConfirmModal.vue` (Teleport pattern, following
   `SupportModal.vue`) — appears when the tutee opens the session view at/after the
   scheduled start time, asks "Confirm you're at [preferred_location]" Yes/No, posts
   the response.
4. Frontend: build `SessionCheckInModal.vue` — triggered at the session midpoint
   (computed from `time_slot` duration), "Is your session going well?" with quick
   responses (e.g., Good / Having issues).
5. Wire the trigger/timing logic into the active-session view (e.g.
   `TuteeSessionDetailsFlow.vue`), comparing current time against `session_date` +
   `time_slot`.
6. Decide and implement the "no" / "having issues" path for each modal — e.g. a venue
   mismatch flags the booking for the tutor/admin; "having issues" routes to the
   existing support/chat flow.

## Risks

- "Session start" and "midpoint" can currently only be inferred from `session_date` +
  `time_slot`, not an actual real-world start event — may be worth adding real
  `session_started_at`/`ended_at` timestamps captured when the modal is answered, so
  the "tracking ... once the session ends" requirement has something concrete to log
  against.
- Self-attestation is weaker evidence than GPS for "tracking of location" — worth
  confirming with the user that a logged Yes/No + timestamp satisfies that requirement.
- Modal trigger timing needs care to avoid firing at the wrong moment (e.g., tutee
  opening the page early, or returning to it after the session is already over).

## Checks to run

- Walk a confirmed F2F booking through: session window opens → venue modal appears and
  is answered → midpoint reached → check-in modal appears and is answered → both
  responses are visible to the tutor/admin afterward.
- `npm run lint` and `npm run build` pass; backend test run
  (`backend/studybuddy/tests.py`) passes.

## Changelog

- **2026-06-11**: Added `SessionCheckIn` model + migration, booking-scoped venue and
  midpoint check-in endpoints, tutee modal prompts, support routing for negative
  responses, tutor detail check-in visibility, and focused backend coverage. Verified
  with `python manage.py test studybuddy.tests.SessionCheckInTests --keepdb`,
  `npm run lint`, and `npm run build`.
