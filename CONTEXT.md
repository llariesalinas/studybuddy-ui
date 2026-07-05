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
A tutor's saved place to receive cash-out funds — a GCash account or a bank account. The
`TutorPayoutAccount` model that once stored this separately was removed (migration
`0063_remove_tutorpayoutaccount.py`); the account details (`account_number`, `account_name`,
`bank_name`, `receiving_institution_*`) now live directly on the `WithdrawalRequest` that used
them, denormalized at request time rather than referenced from a standalone row.
_Avoid_: Withdrawal method, `TutorPayoutAccount` (removed — do not reference as a live model)

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

**Midpoint Check-in**:
A lightweight self-report a participant makes while a session is Live, answering whether things
are on track (`good`) or they are having issues (`issues`). Its purpose is to let support step in
while there is still time to help, rather than after the fact. At most one Midpoint Check-in per
session; once recorded it is shown back as a settled status, not re-asked. Surfaced in the UI as
the "Mid-session pulse" card and confirmed with a deliberate hold gesture (pointer) or a single
press (keyboard / assistive tech) to avoid accidental submission.
_Avoid_: "rating" (that is the post-session score, a different concept), "All good?" (an older
one-tap control that only recorded `good` and gave no way to flag `issues`)

**Accepted Session Load**:
The number of future or unresolved accepted session groups a Tutor is currently carrying, including
`Confirmed` and `Awaiting Payment Verification` groups. Count session groups, not individual
30-minute Booking rows, because a multi-slot appointment is one tutoring commitment.
_Avoid_: accepted booking rows, raw slot count, pending requests

**Accepted Session Load Limit**:
The maximum Accepted Session Load a Tutor may carry before Studybuddy blocks accepting another
booking request. The default limit is 10 session groups, but an institution admin may adjust a
Tutor's limit from Tutor Management for tutors in that admin's institution; the rationale can live
in a Support Ticket and its chat rather than in a required edit note. The editable range is 1 to 20
session groups. The limit is prospective: it blocks new accepts only and does not retroactively
cancel existing accepted sessions.
_Avoid_: pending request limit, booking row limit, slot limit

### Recommendation & matching

**Hybrid Score**:
The final ranking number the tutor recommender produces for a (Tutee, Tutor) pair:
`0.7 * CBF Score + 0.3 * (CF Score / 5)`. Computed by `hybrid_prediction`
(`backend/studybuddy/recommender/hybrid.py:10`). This is the number shown to students as
"recommended for you" ordering.
_Avoid_: "match score", "recommendation score" — the codebase and this glossary use Hybrid Score
only.

**CBF Score**:
The Content-Based Filtering half of the Hybrid Score — how well a Tutor's profile fits a Tutee's
stated preferences, independent of any other student's history. A weighted sum of five sub-scores:
subject match (0.35), expertise level (0.20), course match (0.20), year-level proximity (0.15),
and teaching-level fit (0.10). Computed by `compute_cbf_score`
(`backend/studybuddy/recommender/cbf.py:23`).

**CF Score**:
The Collaborative Filtering half of the Hybrid Score — a predicted rating for a (Tutee, Tutor)
pair derived from how similar Tutees (see Top-K Neighbor) have rated that Tutor. Computed by
`compute_cf_score` (`backend/studybuddy/recommender/CF.py:88`). Returns `None` when the Tutee has
no Rating history at all — see Cold-Start Tutee for what happens to the Hybrid Score in that case.

**Top-K Neighbor**:
One of up to 5 other Tutees whose past Ratings are most similar (by Pearson similarity) to the
Tutee being scored. Found by `top_k` (`backend/studybuddy/recommender/CF.py:64`). A Tutee's set of
Top-K Neighbors is computed once per recommendation request and reused across every candidate
Tutor in that request.

**Cold-Start Tutee**:
A Tutee with no Rating history, so `compute_cf_score` returns `None` for every Tutor. `None` is
coerced to `0` in `hybrid_prediction`, not excluded from the weighting — so a Cold-Start Tutee's
Hybrid Score is always `0.7 * CBF Score`, capped below what a Tutee with rating history could
reach for an identical CBF match. This is a property of the current formula (CF weight is never
reallocated to CBF when CF is unavailable), not a bug. Surfaced in the UI as a "Cold Start" badge
with the subtext "CF unavailable — no rating history."
_Avoid_: "new user" (too broad — a Tutee with bookings but no completed/rated ones is also
Cold-Start; the defining trait is absence of Rating rows, not account age)

### Institution catalog

**Institution Course Catalog**:
The list of course-subject pairings that a specific Partner Institution offers or recognizes inside
Studybuddy. It is institution-scoped: one institution admin curates only their own institution's
catalog, and their changes must not alter another institution's catalog.
_Avoid_: global subject list, shared institution catalog

**Institution Catalog Entry**:
A single institution-scoped relationship that says one Subject belongs under one Course for one
Partner Institution. This is a curation record, not a new global Subject definition.
_Avoid_: subject creation (unless we truly mean adding a brand-new master Subject for every
institution)
