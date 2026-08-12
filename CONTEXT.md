# Studybuddy

Peer-to-peer tutoring platform for Central Philippine University students. This file is the
project's glossary — domain terms only, no implementation detail.

## Language

### Support

**Support Ticket**:
A user-reported or system-opened issue that Studybuddy support staff can claim, discuss in a
support chat, and resolve. (System-opened example: the ticket a Late Cancellation automatically
creates for admin review — worded neutrally, since the "reporter" is the platform, not a person.) A Support Ticket moves through a lifecycle: Open -> In Progress -> Escalated -> Resolved.
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
The Content-Based Filtering half of the Hybrid Score — how well a Tutor's profile fits the
Tutee's requested subject and profile, independent of any other student's history. A weighted sum
of six sub-scores: Specific Subject match (0.40), General Subject match (0.20), expertise (0.15),
course match (0.10), year-level proximity (0.10), and teaching-level fit (0.05). With a requested
subject, Specific/General/Expertise use it; without one, the Tutee's preference
list is the target set. Specific is an exact subject-code match; General includes Specific matches
and same non-null `Subjects.category` matches, so it is a superset. A null category never produces
General or same-field expertise credit. Expertise uses exact matches first, then same-field matches
only when there is no exact match; it is otherwise zero. An empty request and empty preference list
produce zero subject signals. An exact-subject-match Tutor can never be outranked on subject signals
by a same-field-only Tutor (dominance property). Computed by `compute_cbf_score`
(`backend/studybuddy/recommender/cbf.py`). Weights per the 2026-07-15 recommender weight
rebalance plan.

**CF Score**:
The Collaborative Filtering half of the Hybrid Score — a predicted rating for a (Tutee, Tutor)
pair derived from how similar Tutees (see Top-K Neighbor) have rated that Tutor. It prefers the
same-course Peer Pool when its neighbors rated the candidate Tutor, otherwise uses a global-pool
prediction for that Tutor. Computed by
`compute_cf_score_with_fallback` (`backend/studybuddy/recommender/CF.py`). Returns `None` when the Tutee has
no Rating history at all — see Cold-Start Tutee for what happens to the Hybrid Score in that case.

**Top-K Neighbor**:
One of up to 5 other Tutees whose past Ratings are most similar (by Pearson similarity, and only
with positive similarity — a Tutee with opposite or zero-information taste never qualifies) to
the Tutee being scored. Found by `top_k` (`backend/studybuddy/recommender/CF.py`). Two neighbor
lists are computed once per recommendation request and reused across every candidate Tutor: the
Peer Pool and the global pool.

**Co-rated Set**:
The Tutors that two Tutees have both rated. Pearson similarity is computed over this intersection
and nothing else (`sim` in `backend/studybuddy/recommender/CF.py`), so a pair sharing one Tutor
scores 0 and is dropped, and a pair sharing exactly two always scores exactly +/-1 whatever the
values are — three or more is the point below which a similarity is degenerate rather than merely
weak. Note the average taken over the Co-rated Set is not the same number as the Tutee's overall
rating average: the former is what Pearson measures deviation from, the latter is what the CF
prediction's deviation term uses, and they diverge whenever either Tutee has rated a Tutor the
other has not. The algorithm demo tool shows the set expanded per neighbour, labelling both.
_Avoid_: "shared ratings" (ambiguous — the Tutors are shared, the scores are each Tutee's own),
"overlap" (used elsewhere for schedule overlap)

**Peer Pool**:
The Top-K Neighbors drawn only from Tutees with exactly the same course as the Tutee being scored
(no strand tier). CF prefers the Peer Pool per candidate Tutor ("peer ratings"); when no peer has
rated that Tutor, the prediction falls back to the global pool for that Tutor only (per-tutor
fallback). A Tutee with no course simply has an empty Peer Pool and is scored from the global
pool. Revisit trigger: at high rating density, per-request fallback may replace per-tutor
fallback for population purity.
_Avoid_: "coursemates" (informal), "same-strand peers" (strand does not qualify)

**Cold-Start Tutee**:
A Tutee with no Rating history, so `compute_cf_score` returns `None` for every Tutor. `None` is
coerced to `0` in `hybrid_prediction`, not excluded from the weighting — so a Cold-Start Tutee's
Hybrid Score is always `0.7 * CBF Score`, capped below what a Tutee with rating history could
reach for an identical CBF match. This is a property of the current formula (CF weight is never
reallocated to CBF when CF is unavailable), not a bug. Surfaced in the UI as a "Cold Start" badge
with the subtext "CF unavailable — no rating history."
_Avoid_: "new user" (too broad — a Tutee with bookings but no completed/rated ones is also
Cold-Start; the defining trait is absence of Rating rows, not account age)

**General Subject**:
A subject field that groups related Specific Subjects — e.g. Science is the General Subject under
which Biology and Physics live. Stored as `Subjects.category`. In CBF scoring, a General Subject
match means the tutor teaches at least one subject in the same field as the requested subject,
even if not the exact subject itself.
_Avoid_: "category" alone in domain conversation (ambiguous with other category fields), "related
subject"

**Specific Subject**:
An individual teachable subject identified by its subject code (e.g. Biology), living under
exactly one General Subject. A Specific Subject match in CBF scoring means the tutor teaches the
exact subject the Tutee requested.
_Avoid_: "exact subject", "subject" alone when the General/Specific distinction matters

**Tie Breaker**:
The rule that orders Tutors whose Hybrid Scores are equal. Two scores count as equal when they
agree to three decimals — the same precision the recommendation API returns, so a tie to the
algorithm is also a tie on screen. Tied Tutors rank by Upcoming Week Load ascending, and a Tutor
still tied after that ranks by profile id. Without it, equal scores were left in database row
order, which is undefined; ties are common rather than rare, because most CBF sub-scores are
discrete and CF is zero for every Cold-Start Tutee. Surfaced in the algorithm demo tool, never to
Tutees. See ADR-0009.
_Avoid_: "tiebreak rule", "secondary score", "Tier 1/2/3" (from the rejected multi-tier cascade)

**Upcoming Week Load**:
The number of sessions a Tutor has booked in the next seven days — `Confirmed` and
`Awaiting Payment Verification`, counting today and excluding day seven, in Manila local time.
The Tie Breaker's ranking input, on the principle that equally-matched Tutors should give way to
the one with the lighter week. Distinct from Accepted Session Load in both window and counting:
this one is date-bounded and counts each dated session separately rather than collapsing a
multi-slot appointment into one commitment.
_Avoid_: "workload" (ambiguous), "session load" alone (that is Accepted Session Load), "active
bookings"

### Verification & booking gates

**Booking Gate**:
The point in the booking flow where enrollment verification is actually enforced: a Tutee creating
a new Booking (`POST bookings/confirm/`), or a Tutor accepting a pending Booking request
(`POST bookings/<id>/approve/`). Enforcement is forward-only — it never touches existing Bookings,
wallet, or dashboard access, only the two actions above.
_Avoid_: "verification check" alone (too broad — doesn't distinguish which of the two gates below
is doing the checking)

**Reactive Gate**:
The existing, authoritative enforcement at a Booking Gate: the server rejects the disallowed
action with `403 {"code": "verification_required"}` only at the moment it's attempted, surfaced to
the user via a generic toast after the fact (`TutorDetails.vue`'s `confirmBooking`,
`TutorRequestedSessions.vue`'s `confirmSession`). This is the real source of truth — it cannot be
bypassed by client-side state.
_Avoid_: "the gate" alone once a Proactive UI Gate also exists for the same action — always say
which one.

**Proactive UI Gate**:
A client-side mirror of a Reactive Gate's condition that disables the triggering control (a
button) before the user can attempt the action at all, so they never reach the Reactive Gate's
403 in the first place. UX-only — it must reproduce the Reactive Gate's exact condition, never
invent a stricter or looser one, or the two will disagree (a wrongly-blocked control, or a
control that lets the user click through to a reactive failure anyway).
_Avoid_: calling this "the verification gate" as if it were authoritative — it is not; the
Reactive Gate is.

**Verification Enforcement** _(Tutee only)_:
The platform-wide on/off switch for the Tutee Booking Gate, driven by
`tutee_verification_enforced()` / `tuteeVerificationEnforced`. Unset/off means every Tutee is
inside the grace period and the Booking Gate does not block them regardless of their own
verification state. Tutors have no equivalent global switch — a Tutor's gating is entirely a
function of their own Renewal Required state, never a platform-wide flag.
_Avoid_: applying "enforcement" language to Tutors — their gate is always evaluated per-tutor, not
gated behind a platform switch.

**Renewal Required**:
The state of a Tutor or Tutee who was approved at least once but whose `document_renewal_status()`
has since lapsed to due, pending, or rejected. Distinct from *never-approved* (an Application
still `pending`/`rejected` on its first submission), which is a more severe state — for Tutors,
never-approved triggers a full-app lockout (`needsTutorApplicationLockout`), while Renewal Required
only ever blocks the Booking Gate, never general app access.
_Avoid_: "unverified" alone — always distinguish never-approved from Renewal Required, since they
have different consequences.

### Instant Booking & cancellation

**Instant Booking**:
The platform's only booking model: a Tutee booking a slot inside a Tutor's published availability
is confirmed immediately, with no manual acceptance step by the Tutor. Replaces request-to-book
(the old Pending -> tutor approves -> Confirmed flow). The Tutor's safety valve is cancellation
before the Grace Cutoff, not a pre-confirmation review.
_Avoid_: "auto-approval" (there is no approval step at all), "booking request" (nothing is
requested — the booking exists as Confirmed from the start)

**Grace Cutoff**:
The moment 12 hours before a session's start time, after which a cancellation stops being
penalty-free. A single platform-wide constant (not admin-configurable), applied symmetrically to
Tutors and Tutees. A booking created inside the final 12 hours (a "born-late" booking) is never
penalty-free to cancel, and the Tutee is warned of this at booking time.
_Avoid_: "decline window" (there is no separate decline action — cancellation is the single
concept; see Late Cancellation)

**Late Cancellation**:
A cancellation made after the Grace Cutoff. It is still self-serve — the booking ends immediately
and the other party is notified at once — but it automatically opens a Support Ticket against the
cancelling party (Tutor or Tutee) — a real Support Ticket in the institution admin's existing
queue, with a distinct category and an excused-or-counted verdict recorded at resolution. Admin judgment is post-review, never pre-approval: a
Late Cancellation is never blocked waiting for an admin.
_Avoid_: "decline" (a pre-cutoff cancellation is still a cancellation, just untracked), "no-show"
(a different, more severe event — the session was never cancelled at all), "cancellation request"
(nothing is requested — the cancellation takes effect immediately)

**Active Strike**:
A Late Cancellation ticket that still counts against its Strike Cap: opened within the last 14
days and not excused. An unresolved ticket is *provisional* — it counts from the moment it is
opened, before any admin has looked at it. Only an explicit excused verdict relieves a strike;
resolving as counted changes nothing about the count, because the ticket was already counting.
_Avoid_: "pending strike" (it is not waiting to take effect — it already has)

**Counted Strike**:
A Late Cancellation whose Support Ticket the admin resolved as counted rather than excused. The
verdict's only remaining consequence is money: for a Tutor it costs a flat P50 wallet deduction
(paid to the platform, not the wronged party; the deduction may push the wallet negative). Tutees
pay no fee — they have no wallet to deduct from. The *block* is provisional; the *money* is not —
a wallet debit cannot be undone, so it never fires on an unreviewed ticket. See ADR-0011.
_Avoid_: "penalty" alone (ambiguous between the fee and the cap), "fine" for Tutees (there is
none), treating it as the thing that causes a block (an Active Strike does that)

**Strike Cap**:
The limit of 3 Active Strikes, applied per user to both roles. Reaching the cap suspends the
role's core privilege: a Tutee cannot create new bookings; a Tutor's availability is hidden from
search. Existing confirmed sessions are untouched. Strikes expire individually, 14 days after
each was issued — the block lifts the moment the count drops below 3, with no shared reset date.
_Avoid_: "monthly cap" / "calendar reset" (the window is rolling per strike, not per month —
the calendar-month rule was replaced), "cancellation limit" (pre-cutoff and excused cancellations
are unlimited and uncounted)

**Booking Horizon**:
The farthest ahead a session can be instant-booked: 14 days from the moment of booking. Bounds
the damage a stale recurring availability slot can cause (a forgotten weekly slot can accumulate
at most two weeks of auto-confirmed sessions, not a semester's worth). A platform-wide constant.
Not the strike window: the Strike Cap's rolling window is also 14 days, but the two are unrelated
constants (`BOOKING_HORIZON_DAYS` vs `STRIKE_WINDOW_DAYS`) and either may change alone.
_Avoid_: "advance booking limit" (one canonical term)

**Meeting Link**:
The video-call URL for an Online session, generated automatically by the platform at booking
creation (one link per session group — both parties always see the same link). Exists only for
Online-mode bookings; Face-to-face sessions have a Preferred Location instead, never a Meeting
Link. Neither party supplies or edits the link.
_Avoid_: "call link" / "room link" (one canonical term), treating it as tutor-provided (it never
is)

### Booking mode & location

**Preferred Mode**:
The Tutee's chosen session format for a booking search — `Online` or `Face-to-face`. Set via the
pill buttons on `InitialBooking.vue` or the mode dropdown on `FindTutors.vue`'s refine-filters
panel; both write to `store.selectedMode` (`stores/initialbookingprefs.js`).
_Avoid_: "session type" (unused elsewhere in the glossary; keep "Preferred Mode")

**Campus Location Type**:
A required sub-choice of Preferred Mode = `Face-to-face`: `Inside Campus` or `Outside Campus`.
Captured via a popup modal immediately after Face-to-face is chosen, before the existing free-text
Preferred Location field is shown. Not sent to the backend — it only exists to decide whether the
Off-Campus Liability Acknowledgment gate applies, and to label the Preferred Location field for
the user's own reference (with a "Change" control to reopen the modal).
_Avoid_: "location type", "venue type"

**Off-Campus Liability Acknowledgment**:
A confirmation modal shown when a Tutee picks Outside Campus, warning that off-campus sessions are
not covered by Studybuddy. The Tutee must confirm before the Preferred Location field appears; if
they decline or dismiss it, the flow returns to the Campus Location Type choice (not persisted —
UI-only gate, no record kept of the acknowledgment; see ADR 0007).
_Avoid_: "consent", "waiver" (implies a stored/legal record, which this explicitly is not)

### Institution catalog

**Institution Course Catalog**:
The list of course-subject pairings that a specific Partner Institution offers or recognizes inside
Studybuddy. It is institution-scoped: one institution admin curates only their own institution's
catalog, and their changes must not alter another institution's catalog. The Course and Subject in
each pairing are chosen independently, not derived from the Subject's default category.
_Avoid_: global subject list, shared institution catalog

**Institution Catalog Entry**:
A single institution-scoped relationship that says one Subject belongs under one Course for one
Partner Institution. This is a curation record, not a new global Subject definition.
_Avoid_: subject creation (unless we truly mean adding a brand-new master Subject for every
institution)

**Custom Subject**:
A Subject owned by one Partner Institution and visible only to users and admins acting within that
institution. Custom Subjects can be curated into the owning institution's Institution Course
Catalog, but cannot be curated by other institutions.
_Avoid_: global subject, shared subject

### Reporting population

**Tutor Roster**:
Every Tutor account that exists, regardless of activity. This is what the SuperAdmin Users tab
lists — filterable by role, institution and status, but never by time.
_Avoid_: "all tutors" on any Reports surface (see Period-Active Tutor)

**Period-Active Tutor**:
A Tutor with at least one Completed session inside the reporting window. A strict subset of the
Tutor Roster, and the population every figure on the SuperAdmin Reports screen is drawn from. A
Tutor who taught nothing in the window is absent from Reports entirely — they are not shown as a
zero row. The two populations differ, and differ by period, so no Reports surface may be titled
"All tutors".
_Avoid_: all tutors, tutor list, roster (a roster includes the idle; this does not)

**Lifetime Sessions**:
A Tutor's total Completed sessions since joining. A stored field, surfaced on the Users tab and in
the user export.
_Avoid_: "sessions" unqualified when a Period Sessions figure is anywhere nearby

**Period Sessions**:
Completed sessions inside the selected reporting window, for the selected institution. Computed
per request on the Reports screen and its exports. Different from Lifetime Sessions for the same
Tutor; placing the two in one row without distinguishing labels has already produced one shipped
defect.
_Avoid_: total sessions (that phrasing means Lifetime Sessions)

**Earnings**:
A Tutor's share of Gross Revenue in the reporting window, from Paid payments only. Always
period-scoped — there is no lifetime earnings figure anywhere in the product.
_Avoid_: total earnings, wallet balance (a wallet balance is current funds, not period income)

**Period**:
The reporting window every Reports figure is scoped to (7d / 30d / 3m / all time). Changing it
changes the *population*, not just the totals: the set of Period-Active Tutors and the set of
Subjects with any bookings both shrink and grow with it.
_Avoid_: date range (the window is chosen from fixed options, not arbitrary endpoints)
