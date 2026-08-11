---
title: SuperAdmin report drill-down pages
date: 2026-08-11
status: Done
summary: Give the Top performers and Subject popularity cards a "View all" link to dedicated, filterable pages showing every row, and align the xlsx export with them.
spec: ../mockups/2026-08-11-superadmin-report-drilldown.html
---

# SuperAdmin report drill-down pages

## Status & Progress Summary

**Done.** Implemented, committed (`5761627`), pushed, PR #123 open against `main`.

Backend and frontend are both green: `SuperAdminRedesignApiTests` 16/16 (up from 11), frontend
179/179 (up from 166), lint at its documented baseline, build clean. Verified against the
development database: the cards still truncate at 5 and 10, `view=full` returns 159 tutors and 106
subjects, and the totals match those lists exactly.

The full backend suite question is resolved: 417 tests, 4 failures, all confirmed pre-existing and
unrelated to this plan's diff (analytics/reporting code only; no bookings, sessions, dev-live
overrides, or cache touched). Full evidence and the disproved "order-dependent" theory are recorded
in the xlsx-export plan's Checks to run, since that is where the question originated. Root cause not
found; left for a dedicated `diagnosing-bugs` session, not a blocker here.

One incident to record: `CONTEXT.md` was overwritten during this work after a bad existence check,
then restored from `HEAD` with the new terms appended in the file's own style. The committed 376
lines are intact; uncommitted working-tree edits to that file were lost. A separate, unrelated
uncommitted addition (Catalog Description / Tutor Note / Selected Subjects, for the in-flight
subject-picker work) was drafted afterward and is still awaiting the user's review before it is
committed on its own.

Shape is settled (drill-down, one page per dataset) and recorded in the mockup linked above. A
second grilling round then settled three more points: the page shows **Period-Active Tutors** and
must not be titled "All tutors"; a zero-filled 163-row roster was rejected because the Users tab
already is that roster; and the API must return `tutor_total` / `subject_total`, since the card
cannot otherwise label its own link and the count changes with the period (23 / 125 / 159 / 159).
Vocabulary pinned in [`CONTEXT.md`](../../CONTEXT.md).

A third round closed the remaining questions: pages are titled **Tutor performance** and **Subject
popularity**, there is **no rank column**, **null ratings sort last**, and undefined tie-breaking is
**out of scope** by explicit decision (recorded under Risks). Drill-down is confirmed as the shape.

Session summary written:
[`2026-08-11-superadmin-report-drilldown-pages-summary.md`](../session-summaries/2026-08-11-superadmin-report-drilldown-pages-summary.md).
The full-suite question that kept this at In Progress is now resolved (see above); nothing left
open for this plan specifically.

## Goal

The SuperAdmin reports dashboard truncates its two ranked datasets so aggressively that the numbers
cannot be audited: it shows 5 of 159 tutors and 5 of 106 subjects. Give SuperAdmins a way to see
every row, without turning the dashboard into a wall of data.

## Approach

Each capped card keeps its top-5 summary and gains a **View all** pill that navigates to a dedicated
page for that dataset. Drill-down was chosen over expanding the card in place because it is the only
option where both surfaces can be named honestly — the card stays "Top performers" showing 5, and
the destination is "Tutor performance" showing every Period-Active Tutor. In-place expansion forced
the card's title to be wrong in one state or the other.

Rejected alternatives, all mocked up and reviewed:

- **Expand in place** — 159 rows is roughly six screens; it buries the cards below it.
- **Internal scroll at fixed height** — nested scrollbars, and scanning 159 rows through a six-row
  window is worse than paging away to a real page.
- **Full-width in-card takeover** — the right layout, but it reflows the two-column grid on every
  toggle. The drill-down page delivers the same layout without the reflow.
- **One combined report page** — 265 rows on a single page; reaching subjects means scrolling past
  every tutor, and per-dataset search/sort collide.
- **Tabbed dashboard** — ruled out by the user early; far larger change, no tab infrastructure exists.

Key decisions:

- **Filters travel in the query string** (`?period=30d&institution=3`). Without this the destination
  can show a different slice than the card that was clicked, Back loses the dashboard's filters, and
  refresh resets to all-time/all-institutions. It also makes the pages linkable, which report pages
  should be.
- **Sorting is client-side** over the already-loaded array. At 159 and 106 rows server-side sort
  earns nothing. Revisit only if these lists reach the thousands.
- **Page titles: "Tutor performance" and "Subject popularity".** Neither claims completeness.
  Subtitles state the population and window explicitly ("159 tutors with sessions · All time ·
  Central Philippine University").
- **No rank column.** The sessions figure is already visible and sortable, so a rank adds nothing,
  and it is the only column whose meaning breaks under re-sort — `#1` would have to mean either row
  position or a fixed sessions rank, and silently switching between them is worse than omitting it.
- **Null ratings sort last in both directions.** One tutor has completed sessions but no rating at
  all, so `Avg('rating__rating_score')` yields `None`. Coercing it to 0 would rank an unrated tutor
  below a genuine 1-star tutor, which is a stronger claim than the data supports.
- **Subjects render as a sortable table** on the detail page, with a share-of-bookings percentage
  column replacing the dashboard's bar track. The bar visual does not survive 106 rows.
- **The export follows the dashboard.** Ticking "Top Tutors" or "Subject Popularity" now yields
  every row rather than 5 and 10. An export that silently disagrees with the screen it came from is
  the confusion that prompted this work.
- **One API parameter, not new endpoints.** `AdminAnalyticsView` already owns substantial shared
  logic for the date window, institution filter and completed-booking queryset (roughly
  `admin_views.py:1200-1289`). A `view=full` parameter reuses all of it; separate endpoints would
  duplicate it.
- **The page shows Period-Active Tutors, and says so.** The query is booking-driven
  (`completed_bookings.values('tutor')`, `admin_views.py:168`), so a tutor who completed nothing in
  the window is absent. The page is therefore *not* "All tutors" and must not be titled that — see
  [`CONTEXT.md`](../../CONTEXT.md). Titling it "All tutors" would rebuild the exact naming problem
  that drill-down was chosen to solve.
- **No zero-filled roster.** A tutor-driven left join showing all 163 tutors with zeros was
  considered and rejected: the Users tab already is the full roster, filterable by role and
  institution, carrying each tutor's lifetime sessions and rating. Duplicating it here would be a
  worse copy, because bolting "who is idle" onto a period filter makes idleness mean something
  different on every period change. Reports earns its place through the two things Users lacks
  entirely — **earnings** and **period scoping** — not through completeness of the roster.
- **The row counts must come from the API.** `view=summary` gains `tutor_total` and `subject_total`.
  These are period-dependent and change with the filters: 23 tutors at 7d, 125 at 30d, 159 at 90d
  and all time. The link itself is a plain **"View all" pill with no number** -- a count in the
  label competes with the figures already in the card for attention and has to be kept correct on
  every period change for no real gain. The totals still earn their place: they decide whether the
  pill appears at all, since offering "View all" on a card already showing everything is a promise
  the destination cannot keep.

## Steps

1. **Backend — make the caps a parameter, not a constant.** In `backend/studybuddy/admin_views.py`,
   allow `top_tutor_rows(..., limit=None)` and `subject_popularity_rows(..., limit=None)` to mean
   "no cap" (skip the slice when `limit is None`). Keep the existing defaults so current callers are
   unchanged.
2. **Backend — add `view` to `AdminAnalyticsView`.** Accept `view=summary` (default, current
   behaviour) and `view=full` (uncapped `top_tutors` and `subject_popularity`). Validate against a
   named tuple of allowed values in the same style as the existing `ANALYTICS_PERIODS` check, and
   fall back to `summary` on anything unrecognised.
2b. **Backend — return the totals.** Add `tutor_total` and `subject_total` to both responses,
   counted from the same `completed_bookings` queryset the rows come from so they cannot drift from
   the list they describe. Without these the card's "View all N" label has no source.
3. **Backend — uncap the export.** Have `AdminAnalyticsExportView` call both row helpers with
   `limit=None` so the Top Tutors and Subject Popularity sheets carry every row.
4. **Backend — tests.** Extend `SuperAdminRedesignApiTests`: `view=full` returns more rows than the
   default; the default response is byte-for-byte unchanged; the export sheets contain every row.
   Check the existing export tests for row-count assertions that the uncapping will invalidate.
5. **Frontend — remove the redundant client-side slice.** `SuperAdminReports.vue:314` slices subject
   popularity to 5 while the server already sends 10. Replace the magic `5` with a named constant
   shared by both cards so the dashboard's summary length is stated once.
6. **Frontend — store action.** Add `fetchAnalyticsDetail(institutionId, period)` to
   `src/stores/superadmin.js` alongside `fetchAnalytics`, hitting `/admin/analytics/` with
   `view=full`, into its own state key with its own loading/error flags. Follow the existing
   `api.get` pattern in that store.
7. **Frontend — routes.** Add `/superadmin/reports/tutors` and `/superadmin/reports/subjects` to
   `src/router/index.js`, both lazy-loaded with `meta: { requiresAuth: true, role: 'SuperAdmin' }`,
   matching the sibling SuperAdmin entries.
8. **Frontend — detail view.** One component serving both routes, with per-dataset column
   definitions in a constants module in the style of `src/constants/superadminExports.js`. Reads
   `period` and `institution` from the query string, renders breadcrumb, period chips, search box,
   sortable headers, and an Export button scoped to that dataset. Reuse the existing card/table
   styling and `--sb-*` tokens rather than introducing new visual language.
9. **Frontend — wire the cards.** Add the "View all" pill to both card headings, carrying the
   dashboard's current `period` and `selectedInstitutionId` into the query string. Render it only
   when the total exceeds the card's row limit.
10. **Docs.** Session summary in `docs/session-summaries/`, then regenerate the plan dashboard.

## Risks

- **The export row-count change is user-visible.** Anyone who has been reading the 5-row Top Tutors
  sheet as "the top 5" will now get 159 rows. Intended, but worth announcing.
- **Existing export tests may assert row counts** and will fail once the sheets are uncapped. That
  is a correct failure; update the assertions rather than re-capping.
- **`view=full` shifts payload size** from ~15 rows to ~265. Trivial at current scale, but it is the
  parameter to watch if the platform grows; it is the natural place to add pagination later.
- **Query-string filters must round-trip exactly.** If the detail page's period chips write back to
  the URL, the Back button's history entries can multiply. Use `router.replace` for filter changes
  within the page, `router.push` only for the initial navigation.
- **Institution filter is a name-vs-id trap.** The dashboard holds `selectedInstitutionId` as a
  string; the detail page must not coerce it in a way that breaks the "All institutions" empty case.
- **Unrelated in-flight work is in the tree** (subject picker components, `PreferenceSetup.vue`).
  Do not stage it with this change.
- **Tie-breaking is undefined, and deliberately left that way.** `top_tutor_rows` orders by
  `.order_by('-sessions')` alone (`admin_views.py:175`), and the data is full of ties (13, 13, 9, 9,
  9 in the top five). Postgres gives no stable order within a tie group, so which tutors occupy the
  bottom of the top-5 can differ between two refreshes of identical data, and a client-side re-sort
  inherits that unstable base. Raised during planning and explicitly ruled out of scope: it does not
  affect tutor screening, which is what these figures are read for. The one-line fix if it ever
  matters is a secondary key — `.order_by('-sessions', 'tutor__profile__lname',
  'tutor__profile__fname')`. Pre-existing; not caused by this change.

## Checks to run

- `cd backend && venv/Scripts/python.exe manage.py test studybuddy.tests.SuperAdminRedesignApiTests --keepdb` — all pass.
- `cd backend && venv/Scripts/python.exe manage.py test --keepdb` — full suite; note the outstanding
  `DevLiveSessionTests` order-dependence question from the xlsx export work, which predates this plan.
- `npm run test` — all frontend tests pass.
- `npm run lint` — clean apart from the four pre-existing `no-undef` errors in `make_algo_pptx.cjs`
  and `make_algo_pptx.js`, which are unrelated and must not be "fixed" here.
- `npm run build` — completes without errors.
- Manual: from the dashboard, click "View all" on each card with a period and an institution
  selected; confirm the destination shows the same slice, that Back restores the dashboard's
  filters, and that a hard refresh of the detail URL preserves them.
- Manual: export with Top Tutors and Subject Popularity ticked; confirm the sheets carry 159 and 106
  rows and agree with the detail pages.

## Changelog

| Date | Change |
|---|---|
| 2026-08-11 | Created. Design settled through a grilling session; drill-down chosen over four mocked alternatives. Mockup saved to `docs/mockups/2026-08-11-superadmin-report-drilldown.html`. |
| 2026-08-11 | Implemented. Backend: `TOP_TUTORS_CARD_LIMIT` / `SUBJECT_POPULARITY_CARD_LIMIT` replace the magic 5 and 10, both row helpers accept `limit=None`, `AdminAnalyticsView` gains `view=full` and returns `tutor_total` / `subject_total`, and the export calls both helpers uncapped. Frontend: two routes onto one `SuperAdminReportDetail.vue` driven by `REPORT_DETAIL_DATASETS`, a `fetchAnalyticsDetail` store action with its own state and flags, "View all" pills on both cards, and the redundant `.slice(0, 5)` replaced by the shared constant. The null-last comparator was extracted to `sortReportRows` so it could be tested rather than buried in the component. Checks: backend 16/16, frontend 179/179, lint at baseline, build clean, dev-DB spot check 5/10 card and 159/106 full with matching totals. Full backend suite still unresolved after three killed runs. **Incident:** `CONTEXT.md` was overwritten by a Write that followed a Glob wrongly reporting the file absent; restored from `HEAD` and the new terms re-added in the file's existing `**Term**:` / `_Avoid_:` style, but uncommitted edits to it were lost. |
| 2026-08-11 | Session summary written; PR #123 opened with the plan left In Progress, since the full backend suite still had no verdict after three killed runs. |
| 2026-08-12 | Full backend suite ran to completion: 417 tests, 4 failures, all confirmed pre-existing and unrelated to this plan's diff. Full evidence recorded in the xlsx-export plan, where the question originated. Status set to Done. Drafted (uncommitted) three `CONTEXT.md` entries -- Catalog Description, Tutor Note, Selected Subjects -- for the unrelated in-flight subject-picker work, as a reconstruction attempt after the earlier `CONTEXT.md` incident; awaiting the user's review, not part of this plan. |
| 2026-08-11 | Dropped the count from the drill-down link: it is now a plain "View all" pill rather than "View all 159 →". The totals stay in the payload because they gate whether the pill renders at all. |
| 2026-08-11 | Third grilling round, closing the plan. Pages titled **Tutor performance** and **Subject popularity** — neither claims completeness, subtitles carry the population and window. **No rank column**: the sessions figure is already visible and sortable, and rank is the only column whose meaning breaks on re-sort. **Null ratings sort last** in both directions rather than coercing to 0, which would rank the one unrated tutor below a genuine 1-star one. **Tie-breaking left undefined by explicit decision** — surfaced as a live defect (`.order_by('-sessions')` alone, with ties at 13/13/9/9/9, so the bottom of the top-5 can shift between identical refreshes) and ruled out of scope as irrelevant to tutor screening; recorded under Risks with the one-line fix. Drill-down shape confirmed. Mockup updated to match; its earlier "All tutors / 159 at 30d" labels were wrong on both counts. |
| 2026-08-11 | Second grilling round. Killed the zero-filled 163-tutor roster option — the Users tab already is the full roster (all 163, filterable by role and institution, with lifetime sessions and rating), so Reports would have been a worse copy; Reports earns its place on earnings and period scoping, which Users lacks entirely. Recorded that the page shows Period-Active Tutors and must not be titled "All tutors", since the booking-driven query at `admin_views.py:168` omits anyone idle in the window. Added step 2b: the API must return `tutor_total` / `subject_total`, because the summary payload has no count today and the figure is period-dependent (23 at 7d, 125 at 30d, 159 at 90d and all time) — the mockup's hardcoded "159" was wrong on the page's own default period. Vocabulary pinned in a new root `CONTEXT.md`. |
