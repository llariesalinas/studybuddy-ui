---
title: Institutional Admin dashboard redesign (Phase 1)
date: 2026-06-21
status: Done
spec: ../specs/2026-06-21-admin-dashboard-redesign-design.md
---

# Institutional Admin Dashboard Redesign — Phase 1 Implementation Plan

> **For agentic workers:** sequential tasks; execute top to bottom.

**Goal:** Redesign `AdminDashboard.vue` to Variant A (Operations-first), aligned
with the SuperAdmin design language, backed by institution-scoped metrics.
**Stack:** Vue 3, Pinia, Django REST, Bootstrap 5
**Artifact:** [preview](../artifacts/2026-06-21-admin-dashboard-redesign-preview.html)

---

## Status & Progress Summary

**Status:** Done — all tasks implemented and committed. `npm run lint` (changed
files) and `npm run build` pass; backend `manage.py check` passes and the new ORM
queries were verified against the live dev DB (correct scoped values). The Django
test runner could NOT execute here (remote Supabase test DB held by the
connection pooler; SQLite fallback blocked by a Postgres-only migration) — tests
are written and will run against a local/direct Postgres. See summary.
- [x] Task 1 — Backend: extend `/admin/stats` with KPI metrics + demand + top tutors
- [x] Task 2 — Backend: new `/admin/operational-queue/` endpoint
- [x] Task 3 — Backend tests (written; runner blocked by env)
- [x] Task 4 — Store: `operationalQueue` state + `fetchOperationalQueue`
- [x] Task 5 — `AdminDashboard.vue` Variant A redesign
- [x] Task 6 — Verify (lint, build) + commit

---

## Task 1 — Extend AdminStatsView

**Files:** `backend/studybuddy/admin_views.py`

- [ ] In `AdminStatsView.get`, after existing scoped querysets, compute (all
  institution-scoped, reusing the existing `inst` filter block):
  - `week_start` = Monday of current ISO week; `last_week_start` = week_start - 7d
  - `sessions_this_week` = `Booking` count, `session_date__gte=week_start`,
    `status__in=['Confirmed','Completed']`, scoped `tutor__profile__institution`
  - `sessions_last_week` = same for `[last_week_start, week_start)`
  - 30-day window `win_start = today - 30d`; over bookings with
    `session_date__gte=win_start`:
    - `completed_sessions` = status `Completed`
    - `cancelled_sessions` = status in `['Cancelled','Rejected']`
    - `completion_rate` = `round(completed / (completed + cancelled) * 100, 1)`
      or `0.0` when denominator is 0
  - `new_members_this_month` = tutors+tutees with `date_joined__gte=month_start`
  - `subject_demand` (max 5): for institution subjects, `demand` =
    distinct tutees in institution whose `Preference.subjects` include it,
    `supply` = institution `TutorSubjects` count, `gap` = demand>0 and supply==0;
    ordered by demand desc
  - `top_tutors` (max 4): institution tutors annotated with completed-session
    count + `avg_rating` (from `ratings`), ordered by completed desc
- [ ] Add all new keys to the `stats` dict (additive; keep existing keys)
- [ ] Manual sanity: `python manage.py shell` or rely on Task 3 tests

## Task 2 — Operational queue endpoint

**Files:** `backend/studybuddy/admin_views.py`, `backend/studybuddy/urls.py`

- [ ] Add `AdminOperationalQueueView(BaseAdminView)` with
  `permission_classes = [IsAuthenticated, IsAdminUser]`, `get` returns
  `{count, items}`:
  - withdrawals: `WithdrawalRequest` `status__in=('pending','failed')` scoped
    `tutor__profile__institution` → one summary row, route `/admin/withdrawals`
  - support: `SupportTicket` `status__in=('Open','In_Progress')` scoped
    `user__institution` → one row, route `/admin/support`
  - tutor applications: `TutorApplication` `application_status='pending'` scoped
    `profile__institution` → one row, route `/admin/users`
  - `count` = sum of the three underlying totals; omit a group row when its
    total is 0
- [ ] Wire `path('admin/operational-queue/', AdminOperationalQueueView.as_view())`
  into `urls.py` near the other admin routes
- [ ] Import the view in `urls.py` if needed

## Task 3 — Backend tests

**Files:** `backend/studybuddy/tests.py`

- [ ] `AdminDashboardMetricsTests` (APITestCase): create an institution, an admin
  profile (role `Admin`, that institution), tutors/tutees/bookings/ratings; assert
  `/admin/stats` returns the new keys with correct scoped values (sessions this
  week, completion_rate, top_tutors length).
- [ ] Assert `/admin/operational-queue/` returns `count` and grouped `items` and
  is institution-scoped (a withdrawal/ticket in another institution is excluded).
- [ ] `python manage.py test studybuddy.tests.AdminDashboardMetricsTests`

## Task 4 — Admin store

**Files:** `src/stores/admin.js`

- [ ] Add `operationalQueue = ref({ count: 0, items: [] })`; add
  `loading.operationalQueue` and `error.operationalQueue` keys
- [ ] Add `fetchOperationalQueue(force=false)` using the same promise-guard
  pattern as `fetchStats`, GET `/admin/operational-queue/`
- [ ] Export `operationalQueue` and `fetchOperationalQueue`; add
  `operationalQueue` to the persist `paths`
- [ ] `npm run lint`

## Task 5 — AdminDashboard.vue redesign (Variant A)

**Files:** `src/views/AdminDashboard.vue`

- [ ] Replace template with Variant A: role header (with institution name),
  `kpi-grid` (computed `kpiCards`), `dashboard-split` (sparkline + operational
  queue), `two-up` (subject demand + top tutors). Keep error alert + retry.
- [ ] Script: `kpiCards` computed (Active Members, Sessions This Week, Completion
  Rate, Needs Attention=`store.operationalQueue.count`); sparkline computeds
  copied from SuperAdminDashboard; `subjectDemand`/`topTutors` from `store.stats`;
  `handleQueueRoute(item)` → `router.push(item.route)`; `useHaptics` light on
  interactions.
- [ ] `onMounted`: `store.fetchStats(true)` + `store.fetchOperationalQueue(true)`
- [ ] Scoped styles adapted from SuperAdminDashboard.vue (kpi-card, surface-panel,
  sparkline-wrap, pending-item, demand bars, leaderboard). Only `--sb-*` tokens.
- [ ] `npm run lint` and `npm run build`

## Task 6 — Verify + commit

- [ ] `python manage.py test studybuddy` (or the two new classes if the remote
  test DB blocks a full run — note any blocker honestly)
- [ ] `npm run lint` (changed files clean), `npm run build` (succeeds)
- [ ] Commit backend and frontend at logical stops with conventional messages
- [ ] Update this plan to Done; write session summary; update index row

## Risks
- Subject-demand proxy (preferences vs supply) — handle empty/low-data gracefully.
- Completion rate `0/0` → `0.0`.
- Shared `/admin/stats` payload grows for SuperAdmin too (ignored there).
- Remote Supabase test DB may block the Django runner (seen previously); verify
  what can be verified and report honestly.

## Checks to run
- `python manage.py test studybuddy` — pass.
- `npm run lint` — clean.
- `npm run build` — succeeds.

## Changelog
- 2026-06-21: Plan authored from approved spec; status In Progress.
- 2026-06-21: Implemented all tasks — extended `AdminStatsView` (sessions
  this/last week, completion rate, new members, subject demand, top tutors,
  institution name), added `AdminOperationalQueueView` + route, extended the
  admin store (`operationalQueue` + `fetchOperationalQueue`), and rebuilt
  `AdminDashboard.vue` to Variant A. Lint + build pass; queries verified against
  the live dev DB. Django test runner blocked by the remote Supabase pooler /
  PG-only migration on SQLite. Status set to Done.
- 2026-07-17: Frontmatter `status` was still `In Progress` despite the body
  already saying Done since 2026-06-21 — corrected to `Done` during a
  plan-vs-code implementation audit.
