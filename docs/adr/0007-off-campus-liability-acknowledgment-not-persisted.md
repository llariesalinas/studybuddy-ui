---
status: accepted
---

# Off-campus liability acknowledgment is UI-only, not persisted

When a Tutee books a Face-to-face session and selects Outside Campus, a confirmation modal warns
that Studybuddy is not liable for off-campus sessions and requires the Tutee to confirm before
entering a location. We decided this acknowledgment is a client-side UX gate only: it is not
written to the `initialbookingprefs` store beyond the immediate modal flow, not sent to the
backend, and not attached to the resulting Booking record.

The alternative — persisting a flag (e.g. `is_off_campus` + `acknowledged_liability`) on the
Booking — would give admins/legal a queryable record of which sessions were off-campus and
confirmed as such, at the cost of a backend model change, a migration, and API surface for a
feature whose only current requirement is "make the user click through a warning." We chose the
UI-only gate because no current requirement asks for that record, and scope stayed intentionally
small: one popup, one confirm, done.

This is deliberately reversible-but-not-free: if Studybuddy later needs an actual liability record
(e.g. for a real legal/compliance need), that requires a backend field, a migration, and wiring the
acknowledgment through `POST bookings/confirm/` — treat that as new work, not an oversight in this
implementation.
