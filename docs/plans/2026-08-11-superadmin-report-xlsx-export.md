---
title: SuperAdmin report export becomes a readable XLSX workbook
date: 2026-08-11
status: In Progress
summary: Replace the stacked multi-section analytics CSV with a one-sheet-per-section XLSX, and fix the subject-popularity and top-tutor aggregates it reports.
spec:
---

# SuperAdmin report export becomes a readable XLSX workbook

Builds on [2026-08-10-superadmin-export-selection.md](2026-08-10-superadmin-export-selection.md),
which added the section-picking modal this export is driven by, and on
[2026-08-08-superadmin-reports-csv-export.md](2026-08-08-superadmin-reports-csv-export.md), which
introduced the CSV this plan replaces.

## Status & Progress Summary

**Status (2026-08-11): In Progress — all twelve steps implemented on
`feat/superadmin-report-xlsx-export`, checks running.** Settled in a `grill-with-docs` session;
eight decisions taken, recorded under Approach and Steps. No mockup, since the deliverable is a
file format rather than a screen.

Shipped so far: `openpyxl==3.1.5` in `backend/requirements.txt`; `write_xlsx_cell`,
`autosize_xlsx_columns` and `add_xlsx_sheet` helpers plus `subject_popularity_rows` and
`top_tutor_rows` in `admin_views.py`; `AdminAnalyticsExportView` rewritten to emit a workbook;
`AdminAnalyticsView` switched to the two corrected aggregates; `exportFilename` given an extension
argument, a `fileExtension` prop on `SbExportModal`, and `exportAnalyticsCsv` renamed to
`exportAnalyticsWorkbook`.

Started from a narrow request ("remove the Report/Period/Date range/Institution/Generated rows")
which widened once the file was read as an analyst would read it: the metadata rows were the
smallest of three problems, alongside an unparseable container and two aggregates that do not
measure what their labels claim.

## Goal

Make the SuperAdmin analytics download something a person can actually read, and make the numbers
in it mean what their labels say. Today `AdminAnalyticsExportView` glues five differently-shaped
tables into one CSV stream, and two of those tables aggregate the wrong thing.

## Approach

The export's job was settled during grilling: it is a **human-readable printout**, not a data feed
for an analyst. The dashboard in `SuperAdminReports.vue` already renders these figures on screen,
so the download exists to be read, filed and printed.

That choice makes CSV the wrong container. Every readability complaint about the current file --
`########` date columns, truncated tutor names, peso amounts rendered as bare floats -- is CSV
lacking column widths and number formats. Those cannot be fixed within CSV. So the export becomes
an **XLSX workbook with one sheet per section**, which also happens to leave each sheet as a clean
rectangle, keeping analyst use possible without designing for it.

Key decisions:

- **One sheet per section**, in the existing `ANALYTICS_EXPORT_SECTIONS` order. Section slugs and
  the `sections` query param are unchanged, so the modal contract holds.
- **Report metadata moves to a leading "Report Info" sheet.** The original request was to delete
  the Report/Period/Date range/Institution/Generated rows. They are removed from the top of the
  data, but kept as their own sheet: a standalone printout that does not say which period and
  institution it covers cannot be trusted later, and institution scope in particular changes the
  numbers without changing their appearance.
- **Summary transposes** from one wide six-column row to six label/value rows. Reads like a
  receipt, prints without horizontal scrolling. This makes Summary un-stackable across exports,
  which is an accepted trade given the printout framing.
- **The Users export stays CSV.** It is a single tidy table built client-side from
  `USER_COLUMN_GROUPS`; it is not broken, and matching extensions is not worth a ~400KB browser
  XLSX writer or a new backend endpoint.
- **Two aggregates are corrected**, because a well-formatted printout of wrong numbers is worse
  than the ugly CSV it replaces. Details in Steps 5 and 6.

`openpyxl` is added to `backend/requirements.txt` -- pure Python, no system packages, installs
cleanly on Render.

## Steps

1. Add `openpyxl` to `backend/requirements.txt` and install it.
2. Extract the hardcoded `Decimal('0.10')` commission rate (three occurrences in
   `admin_views.py`) into a module-level `PLATFORM_COMMISSION_RATE` constant, with a derived
   payout rate.
3. Rewrite `AdminAnalyticsExportView.get` to build an `openpyxl` workbook instead of a
   `csv.writer`: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` content type,
   `.xlsx` filename from `_build_filename`. Add small shared helpers for writing a sheet's header
   row (bold, frozen) and applying column widths.
4. Write the "Report Info" sheet first: Report, Period, Date range, Institution filter, Generated
   at. Always present, regardless of which sections were ticked.
5. Fix Subject Popularity in **both** `AdminAnalyticsView` (line ~1160) and
   `AdminAnalyticsExportView`. Replace the `TutorSubjects -> Tutor -> Booking` cross-product with
   `completed_bookings.values('subject__subject_name').annotate(booking_count=Count('id'))`. The
   current join counts every subject a tutor teaches against every booking that tutor completed,
   so a tutor teaching five subjects smears one booking across all five.
6. Fix Top Tutors scoping in both views. Today `total_sessions` and `rating_average` are lifetime
   fields on `Tutor` while earnings are period-scoped, so a 30-day report shows a lifetime session
   count beside 30 days of revenue. Replace with a single grouped aggregate over
   `completed_bookings` -- `Count('id')`, `Avg('rating__rating_score')`, and
   `Sum('payment__amount')` filtered to Paid -- ranked by period sessions. `Payment` and `Rating`
   are both `OneToOneField` to `Booking`, so there is no join fan-out. This also collapses the
   existing per-tutor query loop (5 queries) into one.
7. Transpose the Summary sheet to label/value rows.
8. Give every sheet a "No data for this period." note under its header when it has no rows, so an
   empty result is distinguishable from a broken export.
9. Apply number formats: peso currency on money columns, real dates on date columns, sensible
   column widths, bold header rows.
10. Frontend: point the Reports filename builder at `.xlsx`, and update the Reports screen's
    export copy from "CSV" to "spreadsheet". `downloadCsv` already passes a Blob through with the
    server's content type, so no change is needed there. The Users screen keeps its CSV wording.
11. Update `backend/studybuddy/tests.py` for the workbook response and both corrected aggregates.
12. Write the session summary and regenerate `docs/plans/index.html`.

## Risks

- **Numbers will visibly move.** Steps 5 and 6 change figures shown on the live dashboard, not
  just in the file. Subject counts will drop sharply, subject ranking will change, and bookings
  with no subject fall into `General`. Top-tutor rankings will reshuffle. Anyone who has quoted
  the old figures will notice.
- **New runtime dependency.** `openpyxl` must be present on Render for the export to work at all;
  a missing install turns a working feature into a 500.
- **Period = "all time"** still zero-fills one row per day since the earliest booking in Sessions
  Over Time. Unchanged behaviour, but it can produce a very long sheet.
- **Streaming.** The CSV wrote directly to an `HttpResponse`; a workbook must be built fully in
  memory before saving. Fine at current data volumes, but Booking Transactions is unbounded and
  would be the first section to strain it.
- **Period-scoped rating** no longer matches the tutor's profile rating, which may read as a bug
  to someone comparing the two screens. Mitigated by the Report Info sheet stating the range.
- **Formula injection carries over to XLSX.** `openpyxl` writes a string beginning with `=` as a
  real formula, so the protection `escapeCsvValue` added in the previous plan does not come along
  for free -- the export writes user-controlled names and subject titles. Every string cell must
  be forced to `data_type = 's'`.

## Checks to run

- `cd backend && python manage.py test studybuddy` -- all tests pass, including the updated export
  and analytics assertions.
- `npm run test` -- frontend suite passes, including `SbExportModal.test.js`.
- `npm run lint` and `npm run build` -- clean.
- Manual: download a report from `SuperAdminReports.vue` with all sections ticked, and again with
  one ticked. Confirm the file opens in Excel, has a Report Info sheet plus one sheet per ticked
  section, money reads as pesos, dates read as dates, and no sheet shows `########`.
- Manual: pick an institution with no activity in the window and confirm empty sheets carry the
  "No data for this period." note.

## Changelog

| Date | Change |
|------|--------|
| 2026-08-11 | Plan written after a `grill-with-docs` session. Eight decisions settled: printout (not data feed) framing; XLSX one-sheet-per-section via `openpyxl`; metadata to a leading Report Info sheet; Users export stays CSV; Summary transposed to label/value rows; Subject Popularity cross-product bug fixed in export and dashboard; Top Tutors made fully period-scoped; empty sections get a "No data" note. Approved for implementation |
| 2026-08-11 | Added a formula-injection risk: `openpyxl` writes `=`-prefixed strings as live formulas, so the `escapeCsvValue` protection from the export-selection plan does not carry over and string cells must be forced to `data_type = 's'` |
| 2026-08-11 | Implemented all twelve steps on `feat/superadmin-report-xlsx-export`. Two additions beyond the written steps: (1) `qs_tutors` became dead in both analytics views once Top Tutors and Subject Popularity started deriving from `completed_bookings`, so it was removed -- institution scoping now flows entirely through `qs_bookings`; (2) the store action `exportAnalyticsCsv` was renamed `exportAnalyticsWorkbook` and the Reports failure toast reworded, since neither said "CSV" truthfully any more. Checks: 11/11 `SuperAdminRedesignApiTests`, 166/166 frontend, build clean; lint clean apart from 4 pre-existing `no-undef` errors in the untouched `make_algo_pptx` scripts |
