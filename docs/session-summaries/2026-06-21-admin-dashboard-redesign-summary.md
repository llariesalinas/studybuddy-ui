---
title: Institutional Admin dashboard redesign (Phase 1) — session summary
date: 2026-06-21
plan: ../plans/2026-06-21-admin-dashboard-redesign.md
spec: ../specs/2026-06-21-admin-dashboard-redesign-design.md
artifact: ../artifacts/2026-06-21-admin-dashboard-redesign-preview.html
status: Done
---

# Summary

Phase 1 of aligning the institutional **Admin** area with the SuperAdmin
redesign. This phase covers the **Dashboard** only; Users, Reports, Withdrawals,
and Support are future phases. Layout chosen: **Variant A — Operations-first**.

## What shipped

### Backend (`backend/studybuddy/admin_views.py`, `urls.py`)
- Extended `AdminStatsView` (`GET /admin/stats`) with institution-scoped keys
  (additive — existing keys untouched, SuperAdmin gets platform-wide values it
  ignores):
  - `institution_name`
  - `new_members_this_month`
  - `sessions_this_week`, `sessions_last_week` (status in Confirmed/Completed)
  - `completed_sessions`, `cancelled_sessions`, `completion_rate` (last 30 days,
    `0.0` when no sessions)
  - `subject_demand` (top 5): demand = tutee `Preference.subjects`, supply =
    `TutorSubjects`, `gap` when demand>0 and supply==0
  - `top_tutors` (top 4): completed sessions + avg rating + course
- Added `AdminOperationalQueueView` (`GET /admin/operational-queue/`): returns
  `{count, items}` of institution-scoped to-dos — withdrawals (pending/failed),
  open support tickets, pending tutor applications — each routing to the screen
  that resolves it. Wired into `urls.py`.

### Frontend
- `src/stores/admin.js`: added `operationalQueue` state, loading/error keys,
  `fetchOperationalQueue` (promise-guarded), exports, and persist path.
- `src/views/AdminDashboard.vue`: full rebuild to Variant A — role header with
  institution name, 4 KPI cards (Active Members, Sessions This Week, Completion
  Rate, Needs Attention), enrollment sparkline (reuses `enrollment_trend`),
  operational queue panel, subject-demand bars (with ⚠ gap flag), top-tutors
  leaderboard. Loading/empty states throughout; `useHaptics` on queue clicks.
  Scoped styles adapted from `SuperAdminDashboard.vue`; only `--sb-*` tokens.

### Tests (`backend/studybuddy/tests.py`)
- `AdminDashboardMetricsTests`: asserts `/admin/stats` returns the new scoped
  metrics (sessions this week, completion_rate 50%, subject demand, top tutors),
  and that `/admin/operational-queue/` is institution-scoped (excludes another
  institution's withdrawal).

## Deviations from plan / spec
- Added `institution_name` to the stats payload (not in the original spec) so the
  dashboard header can show the institution — small, additive.
- KPI tone for Completion Rate uses the existing `tone-warning` accent (amber) to
  keep four visually distinct cards, matching SuperAdmin's tone palette.

## Checks run
- `python manage.py check` — no issues.
- ORM lookups verified directly against the live dev DB via `manage.py`-style
  shell (subject demand/supply, top tutors completed+rating, queue counts) —
  returned correct, sensibly-scoped values.
- `npx eslint src/stores/admin.js src/views/AdminDashboard.vue` — clean.
- `npm run build` — succeeds.

## Known caveat — Django test runner blocked here
Same environment constraint as the avatar-compression work:
- The DB is remote Supabase via the **connection pooler**; the pooler holds a
  session on `test_postgres`, so Django can't drop/recreate the test DB
  ("database is being accessed by other users").
- A SQLite in-memory fallback fails because a migration
  (`0041_recommendation_filter_indexes`) uses Postgres-only SQL
  (`CREATE INDEX ... IF NOT EXISTS`), which SQLite can't parse.

The two new tests are written and the query logic is verified against live data.
To execute them: point `DB_*` at a **direct** (non-pooler) Postgres endpoint or a
local Postgres, then `python manage.py test studybuddy.tests.AdminDashboardMetricsTests`.

## Not verified in-app
Full browser render of `/admin/dashboard` needs an authenticated **Admin**
session (JWT + role guard), which isn't available here. The approved interactive
mockup covers the visual design; lint/build confirm the component compiles.

## Next phases (same design language)
Users, Reports, Withdrawals, Support — each as its own plan/spec.
