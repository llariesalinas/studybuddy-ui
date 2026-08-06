---
title: Tie Breaker for equal hybrid scores
date: 2026-08-06
status: Done
summary: Break equal hybrid scores by Upcoming Week Load so equally-matched tutors share work.
spec: ../adr/0009-tie-breaker-upcoming-week-load.md
---

# Tie Breaker for equal hybrid scores

## Status & Progress Summary

**Done** — shipped as `c343cc3` on `feat/subjects-reseed`. All eight steps landed as planned,
with three additive deviations recorded below. Full check results and the process caveats are in the
[session summary](../session-summaries/2026-08-06-tie-breaker-summary.md). Not pushed.

## Goal

Give the recommender a defined ordering when two tutors score the same. Today
`recommend_tutors_hybrid` sorts on score alone (`hybrid.py:186`); Python's stable sort leaves ties
resolved by database row order, which is undefined and unexplainable. Ties are not rare: CBF
sub-scores are largely discrete (specific 0/1, general 0/1, course 0/0.5/1, level 0/1) and CF is
coerced to 0 for every Cold-Start tutee, so identical floats are common.

Among equally-matched tutors, prefer the one with fewer sessions booked in the coming week.

## Approach

The ranking key becomes, in order:

1. `round(hybrid_score, 3)` descending
2. **Upcoming Week Load** ascending
3. `profile_id` ascending

**Upcoming Week Load** — count of `Booking` rows for a tutor with status in
`TUTOR_ACCEPTED_SESSION_LOAD_STATUSES` (`Confirmed`, `Awaiting Payment Verification`) and
`session_date` within `[today, today + 7)` in Manila local time. Counted as individual session
occurrences, not grouped into packages: the window is already date-bounded, so occurrences are the
correct burden measure.

This is deliberately distinct from **Accepted Session Load** (`Tutor.accepted_session_load()`,
`models.py:283`), which has no date bound and groups by `session_group_id`. Both terms are defined
in `CONTEXT.md`.

Key decisions and why (full alternatives and trade-offs in ADR-0009):

- **Quantize to 3 decimals** rather than exact float equality or an epsilon band. An epsilon band
  is not transitive, so the resulting sort is ill-defined; 3dp matches the precision the API
  already returns (`views.py:3960`), so "equal on screen" and "equal to the algorithm" agree.
- **Absolute count, not utilization.** Simpler to defend and keeps the tutor-set
  `session_load_limit` out of the formula entirely.
- **Window anchored to today**, not to the requested session date. `requested_date` is optional
  in `recommend_tutors_view`, so anchoring to it would require implementing and justifying two
  rules, and would make load a per-request rather than per-tutor value.
- **Residual ties go to lowest `profile_id`** — deterministic and trivial, at the cost that the
  equity rotation never reaches identically-loaded tutors.
- **Applied inside `recommend_tutors_hybrid`**, so tutee search and dashboard recommendations
  order identically and ranking logic stays in the recommender module.

The demo tool (`demo.py`) does not call `recommend_tutors_hybrid` — it loops candidates itself
(`demo.py:135`) — so it needs the load and tie-group data added separately. Chosen UI is in
`docs/mockups/2026-08-06-tie-breaker-demo-panel.html`: a Tie Breaker badge on tie-group rows, and
the derivation in the breakdown pane alongside the existing CBF and CF derivations.

## Steps

1. Add an `upcoming_week_load` helper to the recommender that takes candidate tutor ids and
   returns a dict of counts via a single grouped aggregate — no per-tutor query.
2. Apply the three-part sort key in `recommend_tutors_hybrid`; attach the load to each
   recommendation dict so callers can read it without recomputing.
3. Add `upcoming_week_load` and tie-group membership to `demo.py` rows.
4. `AlgorithmDemoRankedList.vue`: render scores at 3 decimals (currently `toFixed(2)`, line 186)
   and add the Tie Breaker badge to tie-group rows.
5. `AlgorithmDemoBreakdown.vue`: render the Tie Breaker block only when the selected tutor is in a
   tie group.
6. Add `Tie Breaker` and `Upcoming Week Load` entries to `CONTEXT.md`, each with an `_Avoid_` line
   ("workload", bare "session load").
7. Write ADR-0009.
8. Tests (backend): exact-tie ordering by load; 3dp quantization boundary (a 0.0004 gap ties, a
   0.0015 gap does not); window edges (today counts, day 7 excluded); `Cancelled`/`Rejected`/
   `Completed` excluded; residual tie falls to lowest `profile_id`; a score gap above the
   quantization threshold is never overridden by load.

## Risks

- **Dashboard cache.** `dashboard.py` caches recommendations for 600s per tutee, so a change in a
  tutor's load takes up to 10 minutes to affect dashboard ordering. Acceptable — it also stops the
  ordering churning mid-browse.
- **Query cost.** One extra aggregate per recommendation call. Must stay a single grouped query;
  a per-tutor count would be an N+1 across every candidate.
- **Timezone.** The window must use Manila local dates, consistent with the rest of the booking
  code. A UTC boundary would shift the window by hours and flip counts near midnight.
- **Pre-existing, out of scope:** `accepted_session_load()` has no date bound, so a past session
  stuck at `Awaiting Payment Verification` counts against the Session Load Limit gate forever.
  Not fixed here; to be filed separately.

## Checks to run

- `cd backend && python manage.py test studybuddy` — all pass, including the new tie-break tests.
- `npm run lint` — clean.
- `npm run build` — succeeds.
- `npm run test` — existing frontend suite still passes.

## Changelog

- **2026-08-06** — Plan created from a grilling session. Scope narrowed from the proposed 4-tier
  cascade to Inverse Workload only (response latency has no data source under ADR-0008 Instant
  Booking; schedule overlap is already consumed by the candidate-filter stages; stochastic jitter
  rejected as irreproducible). Trigger set to 3dp quantization, window to next 7 days anchored on
  today, counting absolute occurrences. Demo-tool UI chosen (option C, badge plus derivation
  pane) and saved to `docs/mockups/2026-08-06-tie-breaker-demo-panel.html`. Status: Approved.
- **2026-08-06** — Implemented all eight steps. Two additions beyond the written plan: a
  `tie_group_id` tag on demo rows (the plan said "tie-group membership" without specifying the
  shape — an id per group lets the panel find a tutor's tied peers without duplicating rows), and
  `HYBRID_SCORE_PRECISION` / `UPCOMING_WEEK_DAYS` exported from `src/config.js` so the frontend
  does not hardcode either. Added `AlgorithmDemoRankedList.test.js` (5 cases), which the plan did
  not call for — the badge and tie-peer logic were otherwise untested. Status: In Progress.
- **2026-08-07** — Verified and committed as `c343cc3`. Full Django suite run in chunks (370 tests;
  the remote Supabase test DB exceeds the command timeout in one pass and `--parallel` cannot clone
  past the pooler): 11 failures, each re-run against a stashed clean tree and confirmed pre-existing.
  Frontend build/lint/tests clean. Status: Done. The `accepted_session_load()` stale-row issue
  remains open and unfiled.
