# Real-Time Behavior and Booking Concurrency

This document answers a recurring question: "Is anything in StudyBuddy real-time, and what stops two tutees from double-booking the same slot?" Keep it updated if the chat/WebSocket scope or the booking confirm view changes.

## Is anything real-time?

Only chat. `backend/studybuddy/chat/consumers.py` and `routing.py` implement a Django Channels WebSocket consumer, wired up on the frontend in `src/stores/chat.js`. That is the only push channel in the app.

Everything else — including tutor availability and booking state — is **pull, not push**. Views like `TutorDetails.vue` fetch data once in `onMounted` and again only after an explicit user action (submitting a booking, reloading, re-navigating). There is no server-initiated update telling an open tab "this slot was just taken."

## What that means for a tutee

Concretely:

1. Tutee A opens a tutor's page and sees a 3pm slot listed as open.
2. Tutee B books that same slot a moment later.
3. Tutee A's screen still shows the slot as open — nothing pushes the change to their browser.
4. If Tutee A then tries to book it, the request goes to the backend, which is the actual source of truth.

So the frontend can be stale. The question is whether that staleness can ever result in an actual double-booking. It cannot — see below.

## Why tutor review does *not* prevent the race

It's tempting to assume the `Pending` → tutor-approves-or-rejects workflow is what prevents two tutees from landing on the same slot. It isn't. Tutor review happens **after** a booking already exists and is already the sole claim on that slot. It's a decision about whether to accept a booking that has already won the race, not a mechanism for arbitrating between two competing requests — the system never lets two competing `Pending` requests for the same slot/date coexist in the first place.

## What actually prevents double-booking

Two layers, in order of what actually fires first:

**1. Row locking in the confirm view** (`backend/studybuddy/views.py`, `confirm_payment_and_book`, ~line 2453):

```python
with transaction.atomic():
    for slot in slots:
        availability = get_object_or_404(
            TutorAvailability.objects.select_for_update(),
            id=slot["availability_id"],
            tutor=tutor
        )
        ...
        conflict_exists = Booking.objects.filter(
            availability=availability,
            session_date=session_date,
            status__in=["Confirmed", "Pending", "Completed"]
        ).exists()

        if conflict_exists:
            return Response({"error": "This slot is already booked for that date."}, status=400)
```

`select_for_update()` takes a database row lock on the `TutorAvailability` row for the duration of the transaction. If Tutee A and Tutee B submit near-simultaneous requests for the same slot, the second request **blocks** at that line until the first transaction commits. Only then does its `conflict_exists` check run — by which point Tutee A's `Pending` booking already exists, so Tutee B's check correctly finds it and returns a clean `400` ("This slot is already booked for that date.") instead of creating a duplicate.

**2. A database-level `UniqueConstraint`** (`backend/studybuddy/models.py`, `Booking.Meta`, ~line 883):

```python
constraints = [
    models.UniqueConstraint(
        fields=['availability', 'session_date'],
        condition=Q(status__in=['Pending', 'Confirmed', 'Awaiting Payment Verification', 'Completed']),
        name='unique_active_booking_per_slot_date',
    ),
]
```

This is the backstop in case any other code path ever creates a `Booking` without going through the locked view above (a different endpoint, a bulk script, a future bug). Note that `confirm_payment_and_book` does not currently catch `IntegrityError` from this constraint the way `admin_claim_ticket` does for support tickets — it doesn't need to, because the row lock already prevents the race from ever reaching the constraint in normal operation.

## Summary

| Layer | Purpose | Fires when |
|---|---|---|
| WebSocket (chat only) | Real-time message push | Never for bookings/availability |
| Frontend re-fetch | Shows current state | Page load / user action, not continuously |
| `select_for_update()` + `transaction.atomic()` | Serializes concurrent booking attempts on the same slot | Every call to `confirm_payment_and_book` |
| DB `UniqueConstraint` | Backstop against duplicate active bookings | Only if the above is ever bypassed |
| Tutor `Pending` → `Approved`/`Rejected` review | Business decision on an already-uncontested booking | After the slot is already locked to one booking |

Net effect: the UI is not real-time and can display stale availability, but this cannot produce an actual double-booking — the backend resolves the race deterministically at booking time and returns a clear error to whichever request loses.
