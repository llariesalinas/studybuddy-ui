# Booking Flow

This document describes the end-to-end tutee booking flow in StudyBuddy. It is the authoritative source for architectural questions about how a tutee finds a tutor and books a session. Keep it updated whenever the flow changes.

## Instant Booking safeguards

`POST bookings/confirm/` confirms a booking immediately; new rows are never Pending. It enforces
the Booking Horizon (14 days), tutor verification, non-negative wallet balance, Accepted Session
Load Limit, and Monthly Strike Cap. Online session groups receive one server-generated Meeting
Link; a chat room is opened with a neutral system message and both parties are notified.

Cancellation remains self-serve. Before the Grace Cutoff (12 hours before the session) it is
penalty-free. A Late Cancellation cancels immediately but creates a system-opened Support Ticket.
An admin resolves it as excused or counted; a Counted Strike deducts P50 from a tutor wallet and
three counted strikes in a calendar month suspend a tutee from booking or hide a tutor from search.
The old approve/reject step and requested-sessions route are removed.

## Overview

The booking flow is a 4-step process: preferences → search → slot selection → confirm.

```
Dashboard (InitialBooking.vue)
  → /find-tutors (FindTutors.vue)
    → /tutor/:id (TutorDetails.vue)
      → POST bookings/confirm/ → /dashboard
```

## Step 1 — Initial Preferences

**View:** `InitialBooking.vue` (embedded on the tutee dashboard, not a standalone route)  
**Store:** `src/stores/initialbookingprefs.js` (persisted to sessionStorage)

The tutee fills out a search form:
- Subject — `SubjectTaxonomyPicker.vue` (category grid → subject chips), loaded from
  `GET subjects/`. Subjects are the Preply-style taxonomy (see
  `docs/plans/2026-07-16-subjects-taxonomy-reseed.md`): every subject carries a taxonomy
  `category` (Mathematics & Data Sciences, Natural Sciences, Technology & Computer Science,
  Business/Finance/Economics, Humanities & Social Sciences, Hobbies & Arts) and an internal
  `department` sub-group that is never shown in the UI. Subject codes are opaque slugs
  (`organic-chemistry`) and are likewise never displayed. Course-based subject gating was
  retired — any tutee can search any approved subject regardless of their own course.
- Date (date picker)
- Time range — start time and end time (30-minute slots)
- Mode: Online or Face-to-face
- Preferred location (only shown when Face-to-face is selected)
- Budget range (min/max hourly rate slider)

On submit, `findTutor()` validates all inputs, copies the values into `src/stores/findTutors.js` via `findTutorsStore.setFilters(...)`, then navigates to `/find-tutors`.

## Step 2 — Tutor Search Results

**View:** `FindTutors.vue` (route: `/find-tutors`)  
**Store:** `src/stores/findTutors.js`

Uses the filters saved in `findTutors` store to call the backend search/recommendation API. The tutee browses the tutor list and clicks a tutor card to navigate to `/tutor/:id`.

## Step 3 — Tutor Detail and Slot Selection

**View:** `TutorDetails.vue` (route: `/tutor/:id`)  
**Stores read:** `src/stores/initialbookingprefs.js`, `src/stores/findTutors.js`, `src/stores/bookedSessionDetails.js`

On mount:
- Fetches tutor profile via `GET tutors/:id/`
- Fetches weekly availability via `GET tutors/:id/availability/?month_offset=N`
- Resets `tuteePaymentDetails` store

The tutee selects time slots from a week-by-week calendar. Client-side rules enforced:
- Only same-day multi-slot bookings are allowed
- Selected slots must be contiguous (no gaps between them)
- Face-to-face mode reveals a location input bound to `bookedSessionDetails.bookedSessionLocation`

The right sidebar shows a live estimated cost counter (slots × 0.5 hours × hourly rate).

## Step 4 — Confirm Booking

**Function:** `confirmBooking()` in `TutorDetails.vue`  
**API:** `POST bookings/confirm/`

When the tutee clicks **Confirm Booking**:
1. Writes to `bookedSessionDetails` store: tutorID, tutorName, subject, mode, sessions array
2. Calls `POST bookings/confirm/` with `{ tutor_id, slots[], preferred_location }`
3. On success: resets `initialbookingprefs` and `findTutors` stores, redirects to `/dashboard?refresh=<timestamp>`

## Store Roles

| Store | File | Role |
|---|---|---|
| `initialbookingprefs` | `src/stores/initialbookingprefs.js` | Search form state — sessionStorage, reset after confirm |
| `findTutors` | `src/stores/findTutors.js` | Active filter state and tutor results |
| `bookedSessionDetails` | `src/stores/bookedSessionDetails.js` | Selected tutor + slot array — passed to confirm API |
| `tuteePaymentDetails` | `src/stores/tuteePaymentDetails.js` | Payment method + receipt image — used only by PaymentScreenTutee (see below) |

## Dead Route: PaymentScreenTutee

**View:** `PaymentScreenTutee.vue` (route: `/payment-tutee/:bookingId`)

This view exists and has a full payment UI — cash vs. online payment, receipt image upload, transaction reference field. However, **nothing in the active codebase navigates to it**. `TutorDetails.vue` calls `POST bookings/confirm/` directly without a payment step.

This is planned future work. The plan at `docs/plans/2026-06-08-online-only-payments.md` documents `PaymentScreenTutee.vue` as a target for the online-only payment feature. Do not treat it as the current payment entry point.

## API Endpoints

| Method | Endpoint | Called From |
|---|---|---|
| `GET` | `subjects/` | `InitialBooking.vue` (via `catalogStore.fetchSubjects()`) |
| `GET` | `tutors/:id/` | `TutorDetails.vue` on mount |
| `GET` | `tutors/:id/availability/?month_offset=N` | `TutorDetails.vue` on mount and week navigation |
| `POST` | `bookings/confirm/` | `TutorDetails.vue:confirmBooking()` — active confirm path |
| `GET` | `payment-methods/` | `PaymentScreenTutee.vue` on mount — currently unused in active flow |
