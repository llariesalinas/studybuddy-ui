---
title: Institutional Admin dashboard redesign (Phase 1 of admin-area alignment)
date: 2026-06-21
status: Approved
artifact: ../artifacts/2026-06-21-admin-dashboard-redesign-preview.html
---

# Institutional Admin Dashboard Redesign — Phase 1

## Context

This is **Phase 1** of a larger initiative to align the whole institutional
**Admin** area (Dashboard, Users, Reports, Withdrawals, Support) with the
recently redesigned **SuperAdmin** screens. Phase 1 covers the **Dashboard**
only; the other four screens are explicitly out of scope here and will follow as
separate phases reusing the same design language.

Chosen layout: **Variant A — Operations-first** (see the artifact preview).

## Design principle: split the lens

The institutional Admin is scoped to **one institution** and lacks the
SuperAdmin's platform-governance pending-actions (institution requests,
admin-account requests, domain exemptions). So the metrics deliberately differ
from SuperAdmin:

- **SuperAdmin = platform governance & money** — cross-institution totals,
  commissions/revenue, governance queue.
- **Institutional Admin = their community's health & daily operations** — scoped
  to one institution.

## Visual language (reused verbatim from SuperAdminDashboard.vue)

`.dashboard-role-header`, `.kpi-grid` / `.kpi-card` (icon tone, label, value,
delta), `.dashboard-split`, `.surface-panel`, `.panel-heading`, `.soft-pill`,
`.metric-pill`, `.link-button`, tone classes (`tone-primary/info/warning/danger`),
the SVG enrollment sparkline (area `path` + `polyline`), and `useHaptics`. No new
color literals — only the existing `--sb-*` tokens.

## Layout (Variant A)

1. `.dashboard-role-header` — eyebrow "Dashboard view", h1 "Admin", a sub-line
   with the institution name, and the role pill ("Institution Admin").
2. `.kpi-grid` — 4 KPI cards (below).
3. `.dashboard-split` — enrollment sparkline (left) + operational queue (right).
4. `.two-up` — subject demand (left) + top tutors (right).

## The 4 headline KPIs (locked)

All institution-scoped via the existing `BaseAdminView` role filter pattern in
`AdminStatsView`.

| Card | Value | Delta | Source |
|---|---|---|---|
| **Active Members** | `total_tutors + total_tutees` | `+N this month` | existing counts + new `new_members_this_month` |
| **Sessions This Week** | `sessions_this_week` | `vs last week` (`sessions_last_week`) | `Booking` count, `session_date` in current ISO week, status in `Confirmed`/`Completed` |
| **Completion Rate** | `completion_rate` % | `+/- pts` vs prior window | `Completed / (Completed + Cancelled + Rejected)` over last 30 days |
| **Needs Attention** | `operationalQueue.count` | `N urgent` | the operational-queue endpoint (below) |

`Needs Attention` reads its number from the operational-queue fetch (not stats),
mirroring how SuperAdmin's "Pending Actions" card reads `pendingActions.count`.

## Panels

### Enrollment sparkline
Uses the existing `enrollment_trend` already returned by `AdminStatsView`
(14-day list of `{date, new_tutors, new_tutees}`, institution-scoped). Sparkline
math copied from `SuperAdminDashboard.vue` (`sparklinePoints` / `sparklineAreaPath`).

### Operational queue (the "needs attention" panel)
New endpoint `GET /admin/operational-queue/` returns institution-scoped items the
admin must act on, in the SuperAdmin pending-actions shape:
```json
{ "count": 7, "items": [
  { "type": "withdrawal", "id": 12, "title": "2 withdrawals awaiting review",
    "meta": "PHP 9,400 total - oldest 2 days ago", "route": "/admin/withdrawals" },
  ...
] }
```
Item groups:
- `withdrawal` — `WithdrawalRequest` with `status in ('pending','failed')`
  (scope `tutor__profile__institution`), route `/admin/withdrawals`.
- `support` — `SupportTicket` with `status in ('Open','In_Progress')`
  (scope `user__institution`), route `/admin/support`.
- `tutor_application` — `TutorApplication` with `application_status='pending'`
  (scope `profile__institution`), route `/admin/users`.

Each group is one summarized row (count + meta), matching the mockup. `count` is
the **sum of underlying items** (not the number of group rows), so the KPI is
meaningful. Frontend rows route via `router.push(item.route)` — **no mutations**
on the dashboard (resolving happens on the destination screen).

### Subject demand
New key on `AdminStatsView`: `subject_demand` — top 5 subjects by **demand proxy**,
each `{ subject_name, demand, supply, gap }`:
- `demand` = number of tutees in the institution whose `Preference.subjects`
  include the subject (`Preference` -> `userprofile.institution`).
- `supply` = number of institution tutors teaching it (`TutorSubjects` ->
  `tutor.profile.institution`).
- `gap` = `true` when `demand > 0` and `supply == 0` (or supply well below demand).

Rendered as horizontal proportional bars (width = `demand / max_demand`), with a
⚠ flag on gap rows. **Note:** this is a preferences-vs-supply proxy because
`Booking` has no subject FK; documented as such.

### Top tutors
New key `top_tutors` on `AdminStatsView`: top 4 institution tutors by completed
sessions, each `{ name, completed_sessions, avg_rating, course }`. Rendered as a
ranked leaderboard with initials avatar and rating.

## Backend API contract (Phase 1)

### Extend `AdminStatsView` (`GET /admin/stats`)
Add to the response (institution-scoped, additive — existing keys unchanged):
- `new_members_this_month` (int)
- `sessions_this_week` (int), `sessions_last_week` (int)
- `completion_rate` (float, 1 dp), `completed_sessions` (int),
  `cancelled_sessions` (int) — over the last 30 days
- `subject_demand` (list, max 5)
- `top_tutors` (list, max 4)

SuperAdmin hits the same endpoint; it will receive these keys too (scoped to all
institutions) and simply ignore them. The added aggregates are cheap counts /
small group-bys.

### New `AdminOperationalQueueView` (`GET /admin/operational-queue/`)
- `permission_classes = [IsAuthenticated, IsAdminUser]`
- Institution-scoped via the same role-filter pattern.
- Returns `{ count, items[] }` as above.
- Wire into `urls.py`.

## Frontend changes (Phase 1)

### `src/stores/admin.js`
- Add state: `operationalQueue = ref({ count: 0, items: [] })`, plus
  `loading.operationalQueue` and `error.operationalQueue`.
- Add `fetchOperationalQueue(force = false)` with the same promise-guard pattern
  as `fetchStats`.
- Export both. (No new mutation actions — queue rows navigate to existing screens.)

### `src/views/AdminDashboard.vue` (full redesign to Variant A)
- Replace the Bootstrap-card KPIs + activity-feed + quick-actions with: KPI grid
  (computed `kpiCards`), enrollment sparkline, operational queue panel, subject
  demand panel, top tutors panel.
- `onMounted`: `store.fetchStats(true)` + `store.fetchOperationalQueue(true)`.
- Import `useHaptics`; fire `light` on KPI/queue/router interactions.
- Scoped styles copied/adapted from `SuperAdminDashboard.vue` so the two screens
  read as siblings.
- Keep the existing error-alert + retry pattern.

## Out of scope (later phases)
- AdminUsers, AdminReports, AdminWithdrawals, AdminSupport redesigns.
- Any mutation/resolution flow on the dashboard (queue only routes out).
- A real subject-demand source if/when `Booking` gains a subject FK (would
  replace the preferences proxy).
- Revenue/commission KPIs (SuperAdmin's lens).

## Risks
- `enrollment_trend` and `parse_bool`/`AdminPendingActionsView` are part of the
  **in-progress, uncommitted** SuperAdmin redesign in the working tree. Phase 1
  must layer additively on `AdminStatsView` without breaking those.
- Subject-demand proxy may read oddly if few tutees fill `Preference.subjects`;
  the panel must handle an empty/low-data state gracefully.
- Completion rate over a 30-day window can be `0/0` for quiet institutions —
  return `0.0` (not `NaN`) and show a neutral delta.
- `navigator.vibrate` is Android-Chrome only; haptics are enhancement-only.
- Adding keys to the shared `/admin/stats` slightly grows the SuperAdmin payload;
  acceptable, documented.

## Checks
- `python manage.py test studybuddy` — existing pass + new stats/queue tests.
- `npm run lint` — clean (changed files).
- `npm run build` — succeeds.
- Manual: dashboard KPIs + panels render with institution-scoped data; queue
  count matches the "Needs Attention" KPI; queue rows route correctly.
