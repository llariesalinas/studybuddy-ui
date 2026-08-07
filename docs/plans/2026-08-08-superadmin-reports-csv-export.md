---
title: SuperAdmin Reports CSV export
date: 2026-08-08
status: In Progress
summary: Replaces the Reports page's institution-rollup CSV with a multi-section export covering daily sessions, top tutors, subject popularity, and per-booking transaction detail.
spec:
---

# SuperAdmin Reports CSV export

<!-- LIVING SUMMARY: keep this section and the Changelog current on every edit -->

## Status & Progress Summary

**Status (2026-08-08): In Progress — implemented on `feat/superadmin-reports-csv-export`
(branched off `main`, separate from `feat/superadmin-users-csv-export`); verification blocked,
done by code trace instead.** Scope decided via `AskUserQuestion`: per-booking transaction detail,
daily time-series rows, top-tutors/subject-popularity sections (declined "keep institution
rollup"). Rewrote `AdminAnalyticsExportView` (`admin_views.py:1151`) per Steps 1-4: dropped the
per-institution loop, added the five sections (Summary, Sessions Over Time, Top Tutors, Subject
Popularity, Booking Transactions). Updated
`test_analytics_includes_completion_subject_popularity_and_csv` (Step 5) to assert the new section
titles and a transaction row instead of the old flat header.

`python -m py_compile` and `manage.py check` both pass. Could not run `manage.py test`:
`backend/.env` points `DATABASES` at a live remote Supabase Postgres, not local — a stuck session
was already holding `test_postgres` open (blocking recreation), and the kept db had stale data
that collided with this test's own `PaymentMethod.objects.create(code="online", ...)`. That
collision turned out to be **pre-existing and unrelated to this change**: migration
`0031_online_payment_method.py` seeds a `PaymentMethod(code='online')` row via `update_or_create`
as part of every fresh test-db build, so this test's own `.create(code="online")` in its setUp
will always hit the unique constraint, on any branch, once the test db is genuinely fresh — worth
a separate fix, not touched here (small/focused-changes rule; not this plan's concern). Given the
user's go-ahead to skip the automated run and review by hand: traced the new view logic by hand
against this test's fixture data (one Completed+Paid booking, tutor "Tutor One" at the seeded
institution, subject "College Algebra", tutee "Target User", amount 500.00) and confirmed the
Summary/Sessions-Over-Time/Top-Tutors/Subject-Popularity/Booking-Transactions sections all
produce the exact values the updated test asserts. Not yet confirmed by an actual test run or
in-app click-through.

## Goal

`AdminAnalyticsExportView` (`backend/studybuddy/admin_views.py:1151`) currently writes one CSV
row per institution, with metrics aggregated over the entire selected period. It duplicates the
"Institution Breakdown" table already visible on `SuperAdminReports.vue` and adds no data an admin
couldn't already read off the screen — so exporting it has no real data impact. Rework the export
to carry data that only exists as charts/aggregates on screen today, plus raw transaction detail
that doesn't exist on screen at all.

## Approach

- Per the user's picks, the new CSV has four sections instead of the old single institution table:
  1. **Summary** — period, date range, institution filter, generated-at timestamp, and the
     same total/completed sessions, completion rate, gross revenue, commissions, and payouts
     shown in the dashboard's metric cards.
  2. **Sessions Over Time** — one row per day in the selected period (`date`, `completed_sessions`),
     mirroring the chart data (`sessions_over_time`) instead of collapsing it into one aggregate.
  3. **Top Tutors** — same five tutors/columns as the on-screen leaderboard (name, sessions,
     rating, earnings), now capturable outside a screenshot.
  4. **Subject Popularity** — subject name + booking count, same as the on-screen list.
  5. **Booking Transactions** — new, not shown on screen anywhere: one row per completed, paid
     booking in scope (`session_date`, `institution`, `tutor`, `tutee`, `subject`, `amount`,
     `commission`, `payout`). This is the actual "real data impact" — the level of detail an admin
     would need to reconcile revenue/commission figures against individual sessions.
- Sections are written into the same CSV file, each preceded by a blank line and a
  single-cell section-title row (a common convention for combined-report CSVs; Excel/Sheets
  import it as one sheet, and each section's header row is easy to spot).
- Institution and period filtering stays exactly as today (`institution_id` / `period` query
  params, same `ANALYTICS_PERIODS` lookup) — only what gets written changes, not how the request
  is scoped.
- The old per-institution rollup rows are dropped entirely. Transaction rows carry an institution
  column, so an admin who wants an institution-level breakdown across all institutions can get it
  with a pivot table in Excel/Sheets — a strict superset of what the old rollup offered.
- "Booking Transactions" is scoped to `status='Completed'` with `payment__payment_status='Paid'`
  bookings only — a booking without a paid payment isn't a transaction, so it's excluded rather
  than emitted with blank/zero amount columns.
- No frontend changes needed: `exportAnalyticsCsv` (`superadmin.js:320`) and the Export button in
  `SuperAdminReports.vue` already just stream whatever the endpoint returns as a blob download.
  Only the backend view changes.
- `commission`/`payout` per transaction use the same 10%/90% split already hardcoded elsewhere in
  this view and `AdminAnalyticsView` (not introducing a new magic number, matching the existing
  one).

## Steps

1. In `AdminAnalyticsExportView.get()`, keep the existing period/institution resolution
   (`start_date`, `chart_days`, `qs_bookings`, `qs_tutors`), but drop the per-institution loop.
2. Add the daily-counts aggregation (`completed_bookings.values('session_date').annotate(...)`),
   the top-tutors query, and the subject-popularity query — same shapes as
   `AdminAnalyticsView.get()` (lines 1082-1133), scoped through this view's own `qs_bookings`/
   `qs_tutors`.
3. Add the `Booking Transactions` queryset: `completed_bookings` filtered to
   `payment__payment_status='Paid'`, `select_related('payment', 'student', 'tutor__profile__institution', 'subject')`,
   ordered by `session_date`.
4. Write the five sections in order (Summary, Sessions Over Time, Top Tutors, Subject Popularity,
   Booking Transactions), blank line + title row between each, via the existing `csv.writer`.
5. Update `test_analytics_includes_completion_subject_popularity_and_csv`
   (`backend/studybuddy/tests.py:203`) — its CSV assertion checks for the old
   `date,institution,tutors,...` header; replace with assertions against the new section titles
   and the transaction row for the booking it creates.

## Risks

- Large "all-time" exports scan every completed+paid booking with no pagination — acceptable at
  current scale (same assumption already made for the per-institution loop it replaces, and for
  the client-side full-user-list export in `exportUsersCsv`).
- Multi-section CSVs with blank-line separators are readable in Excel/Sheets as one sheet but
  don't parse as a single flat table with `pandas.read_csv` or similar without extra handling —
  acceptable since the consumer here is a human admin opening it in a spreadsheet, not another
  program.
- `tutor.profile.institution` can be null for a tutor with no institution set; render as an empty
  string rather than raising.

## Checks to run

- `python manage.py test studybuddy.tests.SuperAdminAnalyticsApiTests` (or the specific test
  method) — confirms the endpoint still returns 200 and the new section/row assertions pass.
- `python manage.py test` — full backend suite, to catch any other test asserting the old CSV
  shape.
- Manual: log in as superadmin, open Reports, export CSV with and without an institution filter,
  open in Excel/Sheets, confirm all five sections and the summary numbers match the on-screen
  metric cards.

## Changelog

| Date | Change |
|------|--------|
| 2026-08-08 | Plan drafted after grilling scope via `AskUserQuestion`; awaiting approval before implementation |
| 2026-08-08 | Approved; branched `feat/superadmin-reports-csv-export` off `main`; implemented Steps 1-5 (rewrote `AdminAnalyticsExportView`, updated the export test). `py_compile`/`manage.py check` clean. `manage.py test` blocked by the shared remote Supabase test DB (stuck session + a pre-existing, unrelated `PaymentMethod` seed-migration/test-fixture collision); verified the new logic by hand-tracing it against the test fixture instead, per the user's choice |
