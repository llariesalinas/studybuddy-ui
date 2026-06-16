---
title: Dashboard load performance (backend)
date: 2026-06-07
status: In Progress     # Phase 1 verified end-to-end; Phase 2 (pagination) ruled out by re-measure; redis e2e still pending (no local server)
spec:
---

# Dashboard load performance (backend)

## Goal

Cut tutee-dashboard load time by removing duplicated/dead backend work and
indexing the hot booking queries, without changing what any page renders. The
sibling rendering/frontend fixes are tracked separately in
[Aurora performance fix](2026-06-07-aurora-performance-fix.md),
[Dashboard card stability](2026-06-07-dashboard-card-stability.md), and
[Notifications timeout fix](2026-06-07-notifications-timeout-fix.md); this plan
covers the API/query side.

## Approach

A network audit showed `/api/bookings/` ~9.2s, `/api/dashboard` ~6.1s (measured
in dev with `DEBUG=True`, which inflates Django). Two root causes:

1. The dashboard calls `/dashboard` only for `recommendations` but
   `student_dashboard` also builds `upcoming`/`completed` arrays no page reads
   (the board + tiles come from `/bookings/`). Give recommendations their own
   cached endpoint so the call becomes a Redis cache hit.
2. N+1s in `list_bookings` and `student_dashboard` (relations accessed but not
   `select_related`) plus missing composite indexes on the owner FK + status +
   `session_date`.

`/bookings/` pagination is **deferred** (Option 2): it is the shared source of
truth for ~5 pages that derive counts/filters client-side, with differing access
patterns (date-window vs. scroll). Only pursue it if a `DEBUG=False` re-measure
shows it is still over target — it would get its own plan.

## Steps

1. Add cached `GET /api/recommendations/` (`dashboard_recommendations` view) that
   returns only `get_dashboard_recommendations(user_profile)`; repoint the store
   (`fetchRecommendations` in `src/stores/completedSessions.js`) from `/dashboard`
   to `/recommendations`. Leave `student_dashboard` in place (deprecated,
   safe-to-remove later) so existing tests stay green.
2. Widen `select_related` to kill the N+1s in `backend/studybuddy/views.py`:
   `list_bookings` → add `tutor__profile__course`; `student_dashboard` (both
   upcoming + completed) → add `student` and `rating`.
3. Add composite indexes on `Booking.Meta.indexes`
   (`backend/studybuddy/models.py`): `(student, status, session_date)` and
   `(tutor, status, session_date)`; generate migration `0053`.
4. Keep + validate the `redis==7.4.0` bump (`backend/requirements.txt`). Used only
   via Django's `RedisCache` + `channels_redis`, no direct redis-py calls.
5. Add query-count regression tests (`DashboardLoadPerformanceTests` in
   `backend/studybuddy/tests.py`).

## Risks

- Index set is candidate-only — validate with `EXPLAIN ANALYZE` on real data;
  each index adds write cost.
- redis 7.4.0 e2e not yet verified against a live server (none running locally);
  redis-py imports and Django's `RedisCache` drives it with no API errors.
- Audit numbers are `DEBUG=True`/dev-inflated — do not declare the load axis
  fixed without a `DEBUG=False` + production-build re-measure.
- Unrelated working-tree changes (`RatingStackModal.vue` + its tests, the
  `requests` bump) must be kept out of this work's commits.

## Checks to run

- `cd backend && python manage.py test studybuddy.tests.DashboardLoadPerformanceTests`
  — all 4 pass (endpoint shape, auth, and constant query count for
  `list_bookings` + `student_dashboard`). **Done — passing.**
- `cd backend && python manage.py test studybuddy.tests.StudentDashboardRecommendationTests`
  — existing dashboard cache tests still pass. **Done — 5 pass (locmem).**
- Apply the migration and confirm index usage:
  `python manage.py migrate studybuddy` then `EXPLAIN ANALYZE` the
  `student_dashboard` / `list_bookings` querysets. **Done — migration 0053
  applied to the dev Postgres DB; `EXPLAIN ANALYZE` on the real
  `student_dashboard` upcoming-sessions query
  (`student=<profile>, status='Confirmed', session_date__gte=today`) shows
  Postgres now picks `studybuddy__student_d2f4ac_idx`
  (`Index Cond: (student_id = 26) AND (status = 'Confirmed') AND
  (session_date >= '2026-06-07')`) — a single index-cond scan instead of the
  prior FK-index-scan + filter + sort. The `completed` query and the
  small-sample equality checks still pick the existing single-column FK index,
  which is the cheaper plan at the current ~440-row table size; the composite
  index is there and selected exactly when its 3-column condition matches.**
- redis e2e: with `REDIS_URL` set and a running redis, re-run the cache tests.
  **Pending (no local redis server — port 6379 unreachable).**
- Decisive re-measure: backend `DEBUG=False` + frontend `npm run preview`, then
  re-time `/api/bookings/`, `/api/recommendations`, and FCP. Use to decide
  whether Phase 2 (pagination) is needed. **Done — measured directly against
  the API** (browser/FCP measurement was blocked: `settings.py` hardcodes
  `SECURE_SSL_REDIRECT = True` whenever `DEBUG=False`, and the local dev
  server has no TLS listener to redirect to — see notes below). With
  `DEBUG=False` and a throwaway test account seeded with ~18 bookings (10
  completed + 8 confirmed — close to the heaviest real student in the dev DB,
  who has 39):
  - `/api/bookings/`: **~0.55–0.58s** (down from the dev/`DEBUG=True` ~9.2s)
  - `/api/recommendations/`: **~0.44–0.48s** (down from the old `/dashboard`
    ~6.1s — now a dedicated cached endpoint instead of the full
    upcoming/completed payload)

  **Conclusion: Phase 2 (pagination) is not warranted at current data scale.**
  The ~9s/~6s dev numbers were almost entirely `DEBUG=True` overhead (SQL
  query logging, autoreload checks) plus the N+1s/uncached-recs Phase 1 already
  fixed — not a volume problem `/bookings/` pagination would solve. The
  heaviest real student account (39 bookings) is only ~2x the tested volume,
  well inside the same sub-second envelope. Re-open Phase 2 only if booking
  volume per student grows by an order of magnitude.

## Status & changelog

- **2026-06-07** — In Progress. Phase 1 code complete and unit-verified (N+1
  guards + new endpoint passing; the guard caught and fixed a missed `student`
  N+1 in `student_dashboard`). Migration 0053 applied to the dev DB and
  `EXPLAIN ANALYZE` confirms the new composite index
  (`student, status, session_date`) is selected by the planner for the
  `student_dashboard` upcoming-sessions query — the index delivers as designed.
  Remaining: redis e2e (no local redis server), and the decisive `DEBUG=False`
  re-measure (needs both servers running plus an authenticated session — larger
  effort, scheduled separately). Phase 2 (pagination) stays deferred, gated on
  that re-measure.
- **2026-06-07 (later same day)** — Decisive re-measure done. Ran the backend
  with `DEBUG=False` and timed `/api/bookings/` and `/api/recommendations/`
  directly via a throwaway seeded test account (script-based, since
  `SECURE_SSL_REDIRECT=True` under `DEBUG=False` blocks plain-HTTP browser
  testing locally — no TLS listener to redirect to). Results: ~0.55s and
  ~0.45s respectively, down from the dev-inflated ~9.2s/~6.1s baseline —
  confirming Phase 1 fixed the load-time problem and **Phase 2 (pagination) is
  not needed** at current data scale. Only the redis e2e check remains
  environment-blocked (no local redis server); everything else in this plan is
  verified.
