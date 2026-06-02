# Phase B — Session Cancellation (Both Roles) — Design Spec

**Date:** 2026-06-02
**Status:** Approved for planning
**Stack:** Vue 3 (Composition API), Pinia, Django REST

---

## Goal

Let **both** the tutee and the tutor cancel a session — covering **Pending** and
**Confirmed-upcoming** sessions — with a **required reason** and a **date cutoff**
(no cancelling the day of or the day before the session). No money moves
(payment happens after the session).

## What already exists (important)

Tutee cancellation is **already built and partially covers this**:
- Backend `cancel_booking` (`backend/studybuddy/views.py:1814`) → route
  `bookings/<int:booking_id>/cancel/` — student-only, cancels the whole booking
  group, notifies both parties, touches no payment.
- Frontend "Cancel Session" button + confirm modal in
  `src/views/TuteeSessionDetailsFlow.vue:146`, wired via
  `completedSessions.cancelSession` (`src/stores/completedSessions.js:167`).

Gaps vs. the desired behaviour:

| Desired | Today | Gap to close |
|---|---|---|
| Both roles cancel | Tutee only | Add tutor cancellation |
| Pending **and** Confirmed-upcoming | Confirmed "Upcoming" only | Allow Pending (tutee withdraw) |
| Block same-day **and** day-before | Blocks same-day only | Tighten cutoff |
| Required reason | No reason captured | Add required reason + storage |

## Decisions (from clarification)

1. **Who:** both tutee and tutor.
2. **Which sessions:** Pending **and** Confirmed-upcoming.
3. **Cutoff:** cannot cancel when `session_date` is today or tomorrow.
4. **Reason:** **required**; surfaced to the other party; UX nudges the canceller
   to coordinate via Chat.
5. **Payment:** untouched (post-session payment model → nothing to refund).

### Design note — tutor + Pending
The tutor already has **Reject** for pending requests
(`reject_booking`, `src/views/TutorRequestedSessions.vue`). To avoid a redundant
control, the tutor does **not** get a separate "cancel" button for Pending — Reject
covers that case. The tutor's new **Cancel** button applies to **Confirmed-upcoming**
sessions. The backend endpoint still authorizes either party for either state, so the
system-level rule ("both roles, both states") holds; we simply don't render a
duplicate tutor button. Tutee Cancel covers both Pending (withdraw) and
Confirmed-upcoming.

## Data model

Add to `Booking` (`backend/studybuddy/models.py`):

```python
cancellation_reason = models.TextField(blank=True, default='')
cancelled_by_role = models.CharField(
    max_length=10, blank=True, default='',
    choices=[('tutee', 'Tutee'), ('tutor', 'Tutor')],
)
```

`'Cancelled'` status already exists in `STATUS_CHOICES`. One migration required.

## API

Extend the existing endpoint (no new route, no urls change):

`POST /bookings/<booking_id>/cancel/`
- **Body:** `{ "reason": "<string>" }` (required, min 5 non-whitespace chars).
- **Auth:** caller must be the booking's student **or** the booking's tutor; else 403.
- **Allowed states:** raw status `Pending`, or display status `Upcoming`
  (Confirmed and not yet started). Else 400.
- **Cutoff:** reject when `session_date <= today + 1 day` → 400.
- **Effect:** set the whole group to `Cancelled`, store `cancellation_reason` and
  `cancelled_by_role`, notify the **other** party (and confirm to the canceller)
  with the reason included, log a booking event.
- **Errors:** 400 missing/short reason; 400 wrong state; 400 inside cutoff; 403 not a party.

## Frontend

### Tutee — `src/views/TuteeSessionDetailsFlow.vue`
- Show Cancel for **Pending** as well as Upcoming.
- Tighten enable rule: session date must be **after tomorrow**.
- Cancel modal gains a **required reason** textarea (confirm disabled until ≥5 chars)
  and a "Message your tutor in Chat" link (`/chat`).
- Pass the reason to `cancelSession(id, reason)`.

### Tutor — `src/views/TutorBookingDetailsFlow.vue`
- Add a **Cancel Session** button for Confirmed-upcoming sessions (display status
  `upcoming`), subject to the same cutoff.
- Reuse an equivalent modal (required reason + "Message your tutee in Chat" link).
- Wire to a new `cancelBooking(reason)` action in
  `src/stores/tutorBookingDetails.js` → same endpoint.

### Stores
- `completedSessions.js`: `cancelSession(id, reason)` sends `{ reason }` in the body.
- `tutorBookingDetails.js`: new `cancelBooking(reason)` → posts to the endpoint, refreshes.

## Out of scope
- Refunds / payment reversal (none needed).
- Cancellation analytics / rate-limiting / abuse scoring beyond the date cutoff.
- A dedicated tutor "withdraw pending" button (Reject already covers it).

## Success criteria

1. A tutee can withdraw a **Pending** request (date ≥ 2 days out) with a reason; the
   tutor is notified with that reason; status becomes `Cancelled`.
2. A tutee can cancel a **Confirmed-upcoming** session (date ≥ 2 days out) with a reason.
3. A tutor can cancel a **Confirmed-upcoming** session with a reason; the tutee is notified.
4. Cancelling is blocked (clear message) when the session is today or tomorrow.
5. Submitting with an empty/short reason is blocked client- and server-side.
6. No payment records are altered by a cancellation.
7. `npm run build`, `makemigrations`/`migrate`, and `manage.py check` all pass.
