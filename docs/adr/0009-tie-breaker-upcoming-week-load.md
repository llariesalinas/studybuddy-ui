# Tie Breaker on Upcoming Week Load

Equal Hybrid Scores are common, not rare. CBF sub-scores are largely discrete — Specific 0/1,
General 0/1, Course 0/0.5/1, Level 0/1 — and CF is coerced to 0 for every Cold-Start tutee, so two
tutors in the same course and year teaching the requested subject at the same expertise level
produce a bit-identical float. `recommend_tutors_hybrid` sorted on score alone, and Python's stable
sort left those ties resolved by database row order: undefined, and impossible to account for in
the algorithm demo tool. The Tie Breaker gives them a defined ordering — among equally-matched
tutors, the one with fewer sessions booked in the coming week ranks higher.

We considered a four-tier cascade (reliability and engagement, then platform equity, then schedule
density, then stochastic jitter) and rejected three of its four tiers. Response latency has no data
source: `Tutor.response_time` is a self-declared dropdown, and under ADR-0008 there is no
accept/decline event to measure. Schedule overlap is already consumed upstream by the three-stage
candidate filter, which admits only fully-overlapping tutors in its first stage, so the metric is
constant where it would fire most. Stochastic jitter was rejected because true randomness reorders
results between page loads and cannot be reproduced in a defense. Session Completion Rate is
buildable and was dropped only for scope — equally-matched tutors are, by construction, equally
suitable, so a second quality metric buys little.

The trigger is the Hybrid Score quantized to 3 decimals, not exact float equality and not an
epsilon band. An epsilon band is not transitive — with a band of 0.01, A=0.850 ties B=0.845 and
B ties C=0.840, but A does not tie C — so no consistent ordering exists and the outcome depends on
which pairs the sort happens to compare. Quantization is a true equivalence relation, and 3
decimals is the precision the API already returns, so "equal on screen" and "equal to the
algorithm" agree.

**Upcoming Week Load** is the count of a tutor's bookings in `Confirmed` or `Awaiting Payment
Verification` with a session date in the next 7 days, Manila local, counted as occurrences rather
than grouped into packages. It is deliberately distinct from the existing **Accepted Session Load**
that drives the Session Load Limit gate, which has no date bound and therefore counts a session
stuck at `Awaiting Payment Verification` as active workload forever — penalizing exactly the
early-active tutors this rule exists to help. The cost accepted is two similar-sounding load
numbers in the system, mitigated by naming both in `CONTEXT.md`.

Trade-offs accepted. Absolute count rather than utilization, so a tutor at 9 of a self-set limit of
10 and one at 9 of 20 are treated identically; utilization was the more principled measure but
drags the tutor-set `session_load_limit` into the ranking formula. The window is anchored to today
rather than to the requested session date, so a booking three weeks out is still ranked on this
week's load; anchoring to the request would require a second rule for the case where no date was
given, and would make load a per-request value that cannot be computed once. Residual ties — equal
score and equal load, which is every pair of new tutors at zero — fall to the lowest `profile_id`,
so the equity rotation never reaches that class and early registrants hold the position
permanently; a deterministic hash of tutee and tutor would have distributed it, and was declined
for simplicity.

Consequences worth noting: the rule lives in `recommend_tutors_hybrid`, so tutee search and
dashboard recommendations order identically, and the dashboard's 600-second cache freezes an
ordering for up to ten minutes. The tie is surfaced in the algorithm demo tool but never to tutees
— a visible "fewer bookings this week" reads as unpopular rather than available, and would leak
one tutor's booking volume onto another's search result.
