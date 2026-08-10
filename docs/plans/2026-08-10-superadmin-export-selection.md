---
title: SuperAdmin export selection modal
date: 2026-08-10
status: Done
summary: Adds a shared SbExportModal so Reports exports only the ticked sections, and rewires the Users page's Export CSV to actually export the filtered user list.
spec: ../mockups/2026-08-10-superadmin-export-selection.html
---

# SuperAdmin export selection modal

<!-- LIVING SUMMARY: keep this section and the Changelog current on every edit -->

## Status & Progress Summary

**Status (2026-08-10): Done — implemented on `feat/superadmin-export-selection`, all eight steps,
no design deviations.** Branched off `fix/find-tutors-search-and-booking-location`, the only branch
line that already carries the five-section export (`main` and `develop` do not). Chosen mockup at
`docs/mockups/2026-08-10-superadmin-export-selection.html`.

Shipped: `src/utils/csv.js`, `src/constants/superadminExports.js`, `src/components/SbExportModal.vue`,
store actions `exportUsersCsv` plus a `sections`/`filename` option on `exportAnalyticsCsv`, both
views rewired, and `AdminAnalyticsExportView` gated per section behind `_resolve_sections()` /
`_build_filename()`.

Three additions beyond the written steps, each noted below: formula-injection neutralising in the
CSV escaper, per-section lazy querying in the export view, and routing the pre-existing
`exportUserCsv` through the shared `downloadCsv`.

Checks: 13/13 new frontend unit tests, 155/155 full frontend suite, 9/9
`SuperAdminRedesignApiTests` (including three new export tests — the class is
`SuperAdminRedesignApiTests`, not `SuperAdminAnalyticsApiTests` as this plan first said), lint and
build clean. The backend suite ran fine against the shared DB with `--keepdb`, so the 2026-08-08
blocker did not recur. **Manual in-app click-through is still outstanding.**

## Goal

Two SuperAdmin "Export" buttons currently give the admin no say in what comes out:

1. `SuperAdminReports.vue:31` always writes all five sections (Summary, Sessions Over Time, Top
   Tutors, Subject Popularity, Booking Transactions) into a single CSV, so an admin who wants only
   the transaction ledger has to open a combined file and delete four sections by hand.
2. `SuperAdminUsers.vue:214` is worse — its "Export CSV" calls
   `store.exportAnalyticsCsv({ period: 'all' })`, meaning it exports the **analytics report**,
   all-time, ignoring the page's search/role/institution/status filters entirely. It has never
   exported user data. Neither `exportUsersCsv` nor `/admin/users/export/` exists, despite
   `2026-08-08-superadmin-reports-csv-export.md:106` referring to the former.

Put a selection modal in front of both, and make the Users export export users.

## Approach

- **One shared component**, `src/components/SbExportModal.vue`. `SbSelectModal.vue` is not reusable
  here: it is single-select and owns its own trigger button, and six filter dropdowns already
  depend on its behaviour. The new component copies its `Teleport` + `role="dialog"` +
  backdrop/keydown pattern (`SbSelectModal.vue:26-127`) rather than extending it.
- **Layout C** from the preview: compact tick list on the left, a manifest on the right listing the
  ticked items in file order plus the resulting filename. The manifest deliberately shows **section
  names only, not column headers** — a preview of column headers would have to mirror the backend
  `csv.writer` and could drift silently. Below 560px the panes stack.
- **Opens all-ticked**; Export is disabled while zero are ticked, so there is no empty-file case.
  All-ticked matches the backend's omitted-`sections` default, so the modal only ever *narrows*
  today's output and no existing workflow is lost.
- **Reports** passes the five sections. The endpoint gains a `sections=` query param taking
  comma-separated slugs (`summary`, `sessions_over_time`, `top_tutors`, `subject_popularity`,
  `transactions`); unknown slugs are ignored and an omitted param still returns all five, keeping
  the existing caller and the existing test valid.
- **Users** passes four column groups — Identity, Institution & Status, Tutor Metrics, Wallet —
  built from fields `AdminUserSerializer` (`serializers.py:68`) already returns. Rows are always the
  current `filteredUsers` (`SuperAdminUsers.vue:181`); the modal states "Exporting 42 of 310 users"
  and lists the active filters so the scope is never ambiguous. Generated client-side because
  `/admin/users/` already returns the full unpaginated list — a new endpoint would duplicate
  filtering logic that exists on screen.
- **Filenames** name the content: exactly one item ticked gives
  `studybuddy-transactions-2026-08-10.csv`, several give `studybuddy-report-2026-08-10.csv`, and
  Users gives `studybuddy-users-2026-08-10.csv`. Without this, three exports on one day collide as
  `report(1).csv` / `report(2).csv`.
- **`src/utils/csv.js`** (new, alongside `src/utils/time.js`) owns value escaping, date formatting,
  and the blob download, so the escaper is written once rather than hand-rolled in a component.
- No ADR: this adds a picker in front of an existing endpoint, it does not move a system boundary.

## Steps

1. Branch `feat/superadmin-export-selection` off current HEAD. Leave the in-flight subject-picker
   edits in the working tree untouched and unstaged.
2. Add `src/utils/csv.js` — `escapeCsvValue`, `buildCsv(rows)`, `downloadCsv(filename, text)`, and
   `exportDateStamp()`. Extract the existing blob-download logic shape from `superadmin.js:297-304`
   so both paths agree.
3. Add `src/components/SbExportModal.vue` — props `title`, `items` (`{ id, label }`), `scopeLine`,
   `open`; `v-model` of ticked ids; emits `confirm` and `close`. Renders the layout-C split with
   the manifest and computed filename, Select all / Clear all, and Export disabled at zero.
4. `src/stores/superadmin.js`: give `exportAnalyticsCsv` a `sections` option that is passed through
   as a comma-joined query param and drives the download filename. Add `exportUsersCsv(rows,
   groupIds)` which builds the CSV client-side via `src/utils/csv.js`.
5. `SuperAdminReports.vue`: Export button opens `SbExportModal` with the five sections; confirm
   calls `exportAnalyticsCsv({ institutionId, period, sections })`.
6. `SuperAdminUsers.vue`: replace the `exportAnalyticsCsv({ period: 'all' })` call outright. Export
   opens `SbExportModal` with the four column groups and a scope line derived from `filteredUsers`
   and the active filters; confirm calls `exportUsersCsv(filteredUsers, groups)`.
7. `backend/studybuddy/admin_views.py` `AdminAnalyticsExportView`: parse `sections`, map slugs to
   the five writer blocks, skip unticked ones, and keep all-five as the default when the param is
   absent or empty after filtering. Set `Content-Disposition` to match the frontend filename rule.
8. Tests: Vitest for `csv.js` (quoting a value containing a comma, a quote, a newline) and for
   `SbExportModal` (opens all-ticked, Export disabled at zero, emits the ticked ids). Extend the
   existing analytics-export Django test to assert `sections=summary` returns only that section and
   that omitting the param still returns all five.

## Risks

- `manage.py test` was blocked on 2026-08-08 by the shared remote Supabase test DB plus a
  pre-existing `PaymentMethod` seed/fixture collision (see
  `2026-08-08-superadmin-reports-csv-export.md:25`). If it blocks again, report that plainly rather
  than claiming the backend is verified.
- Client-side user export holds the whole filtered list in memory and builds one string. Fine at
  current scale (the full list is already loaded into the store), but it is not a streaming export.
- Tutor-only fields are blank for tutee rows when Tutor Metrics is ticked. That is intended; the
  alternative (splitting the export by role) was not asked for.
- The five-section export this builds on is not yet merged to `main`. If it lands via a squash
  merge, rebasing this branch will need care.

## Checks to run

- `npx vitest run src/utils/csv.test.js src/components/SbExportModal.test.js` — new unit tests pass.
- `npm run test` — full frontend suite, to catch anything depending on the old export behaviour.
- `npm run lint` and `npm run build` — clean.
- `python manage.py test studybuddy.tests.SuperAdminRedesignApiTests --keepdb` — section filtering
  asserted. (The analytics export tests live in `SuperAdminRedesignApiTests`; there is no
  `SuperAdminAnalyticsApiTests` class.)
- Manual: as superadmin, on Reports tick only Booking Transactions and confirm the file is a flat
  single-section CSV named `studybuddy-transactions-<date>.csv`; on Users apply a role filter and
  confirm the exported row count matches the on-screen count and the ticked column groups.

## Changelog

| Date | Change |
|------|--------|
| 2026-08-10 | Plan written after a `grill-with-docs` session; layout chosen via `ui-preview` (option C of three), mockup promoted to `docs/mockups/2026-08-10-superadmin-export-selection.html`. Approved for implementation |
| 2026-08-10 | Implemented all eight steps and marked Done. Three deliberate additions to the plan as written: (1) `escapeCsvValue` also prefixes `=`/`+`/`-`/`@` with a quote, since a display name like `=cmd` would otherwise execute as a formula when the file is opened — the export writes user-controlled strings, so this belonged in the shared escaper; (2) each section in `AdminAnalyticsExportView` now queries only when selected, so a transactions-only export no longer pays for the top-tutors and subject-popularity aggregates; (3) the pre-existing `exportUserCsv` was routed through the new `downloadCsv` rather than keeping its own copy of the blob/anchor dance. Also fixed a bug the component tests caught: `selectedIds` was only seeded by the `open` watcher, so a modal mounted with `open` already true started empty and un-exportable. Filenames now use `todayKey()` instead of the previous `toISOString().slice(0, 10)`, which stamped the next day's date for Manila evenings. Checks: 155/155 frontend, 9/9 `SuperAdminRedesignApiTests`, lint and build clean; manual click-through outstanding — [Summary](../session-summaries/2026-08-10-superadmin-export-selection-summary.md) |
