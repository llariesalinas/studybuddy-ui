# Studybuddy

Peer-to-peer tutoring platform for Central Philippine University students. This file is the
project's glossary — domain terms only, no implementation detail.

## Language

### Support

**Support Ticket**:
A user-reported issue that Studybuddy support staff can claim, discuss in a support chat, and
resolve. A Support Ticket moves through a lifecycle: Open -> In Progress -> Escalated -> Resolved.
_Avoid_: Issue (too vague), support chat (the chat is only the conversation attached to the
ticket)

**Escalated Support Ticket**:
A Support Ticket that an institution admin cannot resolve and has raised to SuperAdmin attention.
It remains the same ticket, but its lifecycle state changes to Escalated and responsibility moves
from the institution admin to SuperAdmin. Escalated Support Tickets leave the institution admin's
active queue and appear in the SuperAdmin support queue. Escalation requires a short reason that
explains why SuperAdmin intervention is needed. Once escalated, only SuperAdmins can resolve the
ticket. Escalation clears the institution admin as the active owner; a SuperAdmin can then claim
the ticket as the new owner. The reporter sees a calm system message in the support chat when the
ticket is escalated. SuperAdmins claim Escalated Support Tickets from the SuperAdmin support
queue rather than receiving auto-assigned tickets.
_Avoid_: Forwarded ticket, transferred ticket

### Payouts & cash-out

**Payout Destination**:
A tutor's saved place to receive cash-out funds — a GCash account or a bank account. Stored as
`TutorPayoutAccount`.
_Avoid_: Withdrawal method, payout account (use the model name only when referring to the row
itself, not the concept)

**Receiving Institution**:
The bank or e-wallet provider a Payout Destination sends funds to (e.g. BDO, GCash). Identified
by an institution ID/code sourced from PayMongo's network directory — PayMongo does not provide a
logo for these, only a name and code.
_Avoid_: Bank (too narrow — e-wallets are also receiving institutions), provider

**Withdrawal Request**:
A tutor's request to cash out wallet balance to a Payout Destination. Has its own lifecycle
(pending → processed/rejected/failed/flagged) independent of the Payout Destination it targets.
_Avoid_: Cash-out (use for the user-facing action/flow; Withdrawal Request is the record)

**Rail** _(deprecated term — see ADR 0001)_:
Previously: which interbank settlement network (InstaPay vs PESONet) a Withdrawal Request moved
through. As of ADR 0001, Studybuddy only ever uses InstaPay, so this is no longer a live decision
in the domain — only a historical term for anyone reading older code/data.

**InstaPay Cap**:
The ₱50,000 per-transaction ceiling enforced by the InstaPay network itself (not a Studybuddy
choice) that a single Withdrawal Request cannot exceed.

### Sessions & the countdown surface

**Display Status**:
The time-aware status shown to users for a Booking (`Upcoming`, `Ongoing`, `Payment Required`,
`Awaiting Verification`, `Completed`, or a passthrough of the raw status for `Pending` /
`Rejected` / `Cancelled`). Computed server-side per request by `get_display_status`
(`backend/studybuddy/views.py:851`) from the Booking's raw `status` field plus the current time —
it is never stored, only derived. Contrast with the Booking's raw `status` field
(`Pending` / `Confirmed` / `Awaiting Payment Verification` / `Completed` / `Rejected` /
`Cancelled`), which only changes on explicit user/admin action.
_Avoid_: "session status" as a stand-in for the raw `status` field — always be clear which of the
two is meant.

**Handoff**:
A UI-only grouping, not a Display Status value of its own: a session whose Display Status is
`Payment Required` or `Awaiting Verification` — i.e. its scheduled window has ended but payment or
payment verification is still unresolved. Introduced for the Orbit Strip countdown surface to give
these two Display Statuses a shared identity distinct from `Upcoming`/`Ongoing`.
_Avoid_: "pending" (already means something else — a Booking awaiting tutor confirmation)

**Queue Item** / **Front-of-Queue**:
The single most urgent session Studybuddy surfaces to a user across all of their sessions at any
moment, chosen by priority: Live > Handoff > Upcoming-within-15-minutes > none. Owned by
`src/stores/activeSession.js`. A user can have many sessions in flight; at most one is ever the
Queue Item.
_Avoid_: "active session" alone (ambiguous with `activeSession.js`'s existing `activeBooking`,
which only recognizes `ongoing`/`upcoming` sessions inside their time window and predates the
Handoff concept)

**Orbit Zone**:
One of four presentation bands in the countdown UI (the "Orbit Strip") that visualize progress
through the current Queue Item's active window — countdown-to-start while Upcoming, elapsed time
while Live, or time-since-ended (capped at 24 hours) while in Handoff. Orbit Zones are a rhythm
for the UI only; they do not correspond to Booking status transitions, and are distinct from the
five lifecycle steps (`Requested`/`Confirmed`/`In session now`/`Payment needed or Awaiting
verification`/`Completed`) that `SessionTimeline.vue` already renders for the full booking
lifecycle. The Orbit Strip replaces `SessionTimeline` only while a session is the Queue Item;
`SessionTimeline` continues to own every other state (far-future confirmed, completed, pending,
etc.).
_Avoid_: "phase" (the codebase already uses `sessionPhase` for a narrower, Live-only concept —
`before`/`venue-window`/`midpoint`/`over` — which is being superseded by Orbit Zones for display
purposes but may still be referenced internally)
