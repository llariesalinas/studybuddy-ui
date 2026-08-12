# Instant Booking replaces request-to-book

Panel feedback asked us to cut the manual tutor confirmation layer entirely. We considered a
per-tutor opt-in flag (two coexisting booking paths) and a hard block on late cancellations
(admin pre-approval to cancel), and rejected both: the opt-in keeps the confirmation layer alive
for every opted-out tutor, and admin pre-approval converts honest late cancellations into silent
no-shows whenever no admin is online. Instead, Instant Booking is the platform's only booking
model — a slot inside a tutor's published availability confirms immediately — and the tutor's
protection moves from pre-confirmation review to post-hoc accountability: penalty-free
cancellation before a 12-hour Grace Cutoff, and after it a self-serve Late Cancellation that
auto-opens a Support Ticket for admin review (excused, or a Counted Strike: flat P50 wallet
deduction for tutors, none for tutees who have no wallet, and a shared cap of 3 counted strikes
per calendar month before booking/search-visibility suspension).

The trade-off accepted: tutors lose per-tutee vetting before commitment. Chat (auto-opened with a
system message at confirmation) and cancel-before-cutoff are the replacements. Stale recurring
availability is bounded by a 14-day Booking Horizon rather than freshness nagging or dormancy
detection. The old approve/reject endpoints and the tutor requested-sessions screen are removed
outright, not deprecated; `Pending` survives only as a historical status value on old rows.

**Superseded in part by [ADR-0011](0011-provisional-late-cancellation-strikes.md):** the cap of 3
described above was a count of *counted* strikes per calendar month. It is now 3 *active* strikes
in a rolling 14-day window, where an unresolved ticket counts provisionally and only an excused
verdict relieves it. The rest of this decision — instant confirmation, the Grace Cutoff, the P50
tutor deduction on a counted verdict — stands unchanged.

Consequences worth noting: the three tutor-side gates formerly enforced at accept time
(verification, non-negative wallet, Accepted Session Load Limit) now gate booking creation and
are surfaced by hiding the tutor from search, with the server-side check as the authoritative
backstop; and Support Tickets gain a system-opened variant (the reporter is the platform, not a
person).
