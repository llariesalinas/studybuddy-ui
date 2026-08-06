# Tie Breaker for equal hybrid scores — session summary

**Plan:** [2026-08-06-tie-breaker.md](../plans/2026-08-06-tie-breaker.md)
**Decision record:** [ADR-0009](../adr/0009-tie-breaker-upcoming-week-load.md)
**Mockup:** [2026-08-06-tie-breaker-demo-panel.html](../mockups/2026-08-06-tie-breaker-demo-panel.html)
**Commit:** `c343cc3` on `feat/subjects-reseed`

## What shipped

All eight planned steps, as specified.

| File | Change |
| --- | --- |
| `backend/studybuddy/recommender/workload.py` (new) | `get_upcoming_week_loads()` — one grouped aggregate over candidate tutor ids |
| `backend/studybuddy/recommender/hybrid.py` | `HYBRID_SCORE_PRECISION = 3`; sort key `(-round(score, 3), load, profile_id)`; load attached to each recommendation |
| `backend/studybuddy/recommender/demo.py` | Same ranking rule (it scores candidates itself) plus `_mark_tie_groups` |
| `src/components/algorithm-demo/AlgorithmDemoRankedList.vue` | Scores at 3dp, Tie Breaker badge, tied peers passed to the pane |
| `src/components/algorithm-demo/AlgorithmDemoBreakdown.vue` | Tie Breaker derivation block, tied tutors only |
| `src/config.js` | `HYBRID_SCORE_PRECISION`, `UPCOMING_WEEK_DAYS` |
| `CONTEXT.md` | Glossary entries for Tie Breaker and Upcoming Week Load |

## Deviations from the plan

Three, all additive:

1. **`tie_group_id` as the tie-group shape.** The plan said "tie-group membership" without specifying a
   representation. An id per group lets the panel find a tutor's tied peers by filtering rows, rather
   than embedding a duplicate peer list on every row.
2. **Two constants exported from `src/config.js`.** The plan didn't mention them; without them the
   frontend would hardcode the precision and the window length, which the repo's conventions forbid.
   They carry a comment tying them to their backend counterparts.
3. **`AlgorithmDemoRankedList.test.js` (5 cases).** The plan listed backend tests only. The badge
   predicate and tied-peer computation are real logic and were otherwise uncovered.

## Checks run

| Check | Result |
| --- | --- |
| `npm run build` | Clean |
| `npm run test` | 93 passed (was 88 — 5 new) |
| `npm run lint` | 4 pre-existing `no-undef` errors in `make_algo_pptx.cjs`/`.js`, both untouched by this work; no new findings |
| `python manage.py test studybuddy` | 370 tests across 7 runs; 11 failures, **all verified pre-existing** |

The backend suite could not be run in one pass: the test database is remote (Supabase behind the
Supavisor pooler), so it exceeds the 10-minute command limit, and `--parallel` fails because cloning
the test database is blocked while the pooler holds a connection. It was run in chunks of test
classes totalling exactly the 370 tests the runner collects.

The 11 failures — cashout amounts, avatar upload, dev-wallet, dev live-session, verification dev
tools, superadmin analytics — were each re-run against a stashed (clean) tree and failed identically,
confirming they predate this work. New tests added here: 23 backend, 5 frontend, all passing.

## Note on process

The first test run died on a stale test-database connection and the implementation was written while
the database rebuilt, so the TDD red phase was never observed. A mutation check was substituted:
reverting the sort key to the old score-only version fails 4 of the 7 ordering tests, confirming they
bind to real behaviour rather than passing vacuously.

No visual check was done in a running app — the demo tool needs a SuperAdmin login against seeded
data, which is not seeded locally (a known blocker since 2026-08-04). The design was validated
against the mockup instead.

## Known issue left open

`Tutor.accepted_session_load()` (`backend/studybuddy/models.py:283`) has no date bound, and no
cleanup job exists anywhere in the app. A booking left at `Awaiting Payment Verification` after its
session date counts against the Accepted Session Load Limit permanently, and since that limit gates
booking creation and hides the tutor from search, an active tutor can silently become unbookable.
Out of scope here and not fixed; it needs its own plan, because the fix is either a date bound
(changing what the limit means) or a lifecycle job (changing when a booking dies). Not yet filed as
an issue — awaiting the go-ahead.
