# Dashboard load performance (backend) — summary

**Plan:** [2026-06-07-dashboard-load-performance.md](../plans/2026-06-07-dashboard-load-performance.md)
**Date:** 2026-06-07
**Status:** Done. Phase 1 complete and verified end-to-end (code, unit tests, applied
migration + `EXPLAIN ANALYZE`, and a `DEBUG=False` decisive re-measure); Phase 2
(pagination) ruled out by the re-measure. The redis e2e check is accepted as a
known gap — this machine has no redis-server, Docker, or WSL to stand one up,
and closing it would require installing new infrastructure (Memurai or Docker
Desktop), which was declined.

## What shipped

- **New cached recommendations endpoint.** `GET /api/recommendations/`
  (`dashboard_recommendations` in `backend/studybuddy/views.py`, registered in
  `backend/studybuddy/urls.py`) returns only `get_dashboard_recommendations`.
  The store (`src/stores/completedSessions.js`) now calls `/recommendations`
  instead of `/dashboard`, so the dashboard's recommendations call is a Redis
  cache hit instead of recomputing all-time `upcoming`/`completed` that no page
  read. `student_dashboard` left intact (deprecated, safe-to-remove later).
- **N+1 fixes** (`backend/studybuddy/views.py`): `list_bookings` +=
  `tutor__profile__course`; `student_dashboard` (both querysets) += `student`,
  `rating`.
- **Composite indexes** on `Booking` (`backend/studybuddy/models.py`):
  `(student, status, session_date)`, `(tutor, status, session_date)` — migration
  `0053_booking_studybuddy__student_d2f4ac_idx_and_more.py`.
- **redis bump** `5.2.1 → 7.4.0` (`backend/requirements.txt`) retained; used only
  through Django's `RedisCache` + `channels_redis`.
- **Regression tests**: `DashboardLoadPerformanceTests` in
  `backend/studybuddy/tests.py`.

## Deviation from plan

- The query-count guard caught a bug in the first cut: adding `rating` alone left
  a `student` N+1 in `student_dashboard` (6 → 9 queries as bookings grew).
  Fixed by also `select_related('student')`. The plan/test earned their keep.

## Checks run

- `python manage.py test studybuddy.tests.DashboardLoadPerformanceTests` — 4/4
  pass (endpoint shape, auth 401/403, constant query count for `list_bookings`
  and `student_dashboard`).
- `python manage.py test studybuddy.tests.StudentDashboardRecommendationTests` —
  5/5 pass under `LocMemCache` (existing dashboard/cache logic intact).
- redis-py 7.4.0 imports with Django 6.0.2 + channels_redis 4.2.1; Django's
  `RedisCache` drove it with no API errors.

## Follow-up verification (2026-06-07, same session)

- **Migration `0053` applied** to the dev Postgres DB
  (`python manage.py migrate studybuddy 0053_...`) — both composite indexes
  (`studybuddy__student_d2f4ac_idx`, `studybuddy__tutor_i_ebe003_idx`) confirmed
  present via `pg_indexes`.
- **`EXPLAIN ANALYZE` confirms index usage**: the real `student_dashboard`
  upcoming-sessions query (`student=<profile>, status='Confirmed',
  session_date__gte=today`) now plans as a single
  `Index Scan using studybuddy__student_d2f4ac_idx` with all three columns in
  `Index Cond` — replacing the prior FK-index-scan + filter + sort. Other
  query shapes (equality-only lookups, the `completed` query without a
  `session_date` filter) still pick the existing single-column FK index, which
  is the cheaper plan at the current ~440-row table size — expected, and the
  composite index is selected exactly when its full 3-column condition matches.

## Decisive re-measure (2026-06-07, same session)

Ran the backend with `DEBUG=False` and timed the hot endpoints directly. The
planned browser/FCP walkthrough hit a wall: `settings.py` hardcodes
`SECURE_SSL_REDIRECT = True` whenever `DEBUG=False`, and the local dev server
has no TLS listener — so every plain-HTTP request 301s to an `https://` URL
nothing is serving. Worked around it with a one-shot script (seeded a
throwaway test account with ~18 bookings — close to the heaviest real student
in the dev DB at 39 — minted its own JWT, timed the endpoints with the
`X-Forwarded-Proto: https` header `SECURE_PROXY_SSL_HEADER` already trusts,
then deleted every trace of the account):

- `/api/bookings/`: **~0.55–0.58s** (vs. dev/`DEBUG=True` ~9.2s)
- `/api/recommendations/`: **~0.44–0.48s** (vs. the old `/dashboard` ~6.1s)

**Verdict: Phase 2 (`/bookings/` pagination) is not needed.** The original
~9s/~6s was almost entirely `DEBUG=True` overhead plus the N+1s/uncached-recs
that Phase 1 already fixed — not a data-volume problem pagination would solve.

## Not done — accepted gap

- **Redis end-to-end**: no redis-server, Docker, or WSL available on this
  machine, so the `RedisCache` path remains unexercised against a live server.
  redis-py 7.4.0 imports cleanly and Django's `RedisCache` drives it with no
  API errors. Closing this fully would require installing new infrastructure
  (Memurai or Docker Desktop) — declined for this pass; the plan is closed out
  as Done with this as a known, low-risk residual.

## Rendering / frontend siblings (separate plans, same session)

Blur fill-rate reduction, scroll containment, hover scoping, poll interval
60s, and lazy Dashboard route are tracked under
[Aurora performance fix](../plans/2026-06-07-aurora-performance-fix.md),
[Dashboard card stability](../plans/2026-06-07-dashboard-card-stability.md), and
[Notifications timeout fix](../plans/2026-06-07-notifications-timeout-fix.md).
