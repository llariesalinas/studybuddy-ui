---
title: SuperAdmin tutor/tutee stats, schedule & bookings
date: 2026-07-13
status: Approved
summary: Add Schedule and Bookings tabs plus expanded stats to SuperAdminUserModal, with per-tab CSV export.
spec: ../mockups/2026-07-13-superadmin-tutor-tutee-stats.html
---

# SuperAdmin tutor/tutee stats, schedule & bookings

## Status & Progress Summary

Spec approved via `/grill-with-docs` + `/to-spec` on 2026-07-13. Design decisions locked (tabs
layout, Option B profile cards, live computation, lazy per-tab loading, per-tab CSV export). No
implementation started yet — next step is `/to-tickets` or `/implement`.

## Problem Statement

When a SuperAdmin opens a user's detail modal from the user management table, they only see
account/verification data — institution, join date, profile status, domain exemption, and (for
tutors) wallet balance, completed-session count, and average rating. There is no way to see a
tutor's actual weekly schedule, a user's booking history, deeper rating/subject/cancellation
detail, or who they interact with most — all of which admins need when investigating disputes,
verifying activity claims, or auditing a specific account. None of this data can currently be
exported either, so any investigation that needs to leave the modal (e.g. attach evidence to a
support ticket) requires manual copy-paste.

## Solution

Extend `SuperAdminUserModal.vue` with two new tabs alongside the existing Profile/Actions tabs:

- **Schedule** (tutors only) — a weekly grid of the tutor's `TutorAvailability` slots, showing
  Open / Booked / Inactive per cell, with booked cells linking to the matching row in Bookings.
- **Bookings** (all roles) — a single paginated, date-filterable table of that user's booking
  history (as tutor or tutee), newest first.

The existing Profile tab gains new sectioned stat cards: rating breakdown (distribution, not just
average), recent written reviews, subjects taught/studied, split cancellation counts, and top-3
most-frequent counterparts. Each of the three tabs (Profile, Schedule, Bookings) gets its own CSV
export button, exporting that tab's current (filtered, where applicable) data.

All new data is computed live on request — no new denormalized fields or migrations — and loads
lazily per tab on first click, cached client-side thereafter.

Design reference: `docs/mockups/2026-07-13-superadmin-tutor-tutee-stats.html` (supersedes the
2026-07-12 slide-over-panel mockup, which explored the same problem with a different UI pattern
that was not carried forward).

## User Stories

1. As a SuperAdmin, I want to see a tutor's weekly availability grid, so that I can verify whether
   their claimed availability matches what's actually configured.
2. As a SuperAdmin, I want booked slots in the schedule grid to be visually distinct from open and
   inactive slots, so that I can tell at a glance how much of a tutor's time is committed.
3. As a SuperAdmin, I want to click a booked slot in the schedule grid and jump straight to that
   booking's row in the Bookings tab, so that I don't have to search for it manually.
4. As a SuperAdmin, I want to see a user's full booking history (as tutor or tutee), so that I can
   investigate disputes or verify activity when a user contacts support.
5. As a SuperAdmin, I want the booking history table to show both the tutor's and tutee's name on
   every row, so that I don't have to guess the counterpart from context.
6. As a SuperAdmin, I want the booking history to default to the most recent bookings without any
   filter applied, so that the common case (checking recent activity) requires no setup.
7. As a SuperAdmin, I want quick date-range presets (7/30/90 days, all time) for the booking
   history, so that I can narrow to a common window with one click.
8. As a SuperAdmin, I want a custom date range option for the booking history, so that I can
   investigate a specific incident from a known date.
9. As a SuperAdmin, I want the booking history paginated at 10 rows per page, so that the modal
   doesn't have to load a user's entire history at once.
10. As a SuperAdmin, I want to see a tutor's star-rating distribution (not just the average), so
    that I can distinguish a tutor with consistently good reviews from one with mixed results.
11. As a SuperAdmin, I want to see a tutor's 3-5 most recent written reviews, so that I have
    qualitative context alongside the numeric rating.
12. As a SuperAdmin, I want to see the subjects a tutor teaches (with expertise level) or a tutee
    has studied, so that I understand their activity on the platform at a glance.
13. As a SuperAdmin, I want cancellation counts split into "cancelled by this user" and "cancelled
    by their counterpart," so that I can tell whether a user is flaky or is being stood up by
    others.
14. As a SuperAdmin, I want to see a user's top 3 most-frequent counterparts (most-booked tutors
    for a tutee, most-frequent students for a tutor), so that I can spot recurring pairings.
15. As a SuperAdmin, I want each tab (Profile, Schedule, Bookings) to have its own CSV export
    button, so that I can pull exactly the data I need for a given investigation without a
    combined dump.
16. As a SuperAdmin, I want the Bookings CSV export to respect whatever date filter I currently
    have applied, so that the exported file matches what I'm looking at on screen.
17. As a SuperAdmin, I want the new tabs' data to load only when I click into them, so that
    opening the modal for a quick profile check stays fast.
18. As a SuperAdmin, I want tab data to stay loaded when I switch away and back within the same
    modal session, so that I'm not waiting on repeat network requests.
19. As a SuperAdmin viewing a Tutee's modal, I want the Schedule tab to be absent (not just empty),
    since tutees have no availability to display.
20. As a SuperAdmin viewing a Tutee's modal, I want the rating-breakdown and recent-reviews
    sections absent from Profile, since tutees are not rated in this system.

## Implementation Decisions

**Frontend (`SuperAdminUserModal.vue`)**
- Add two tabs to the existing tab bar: `Schedule` (rendered only when `role === 'Tutor'`) and
  `Bookings` (all roles), following the same tab-switch pattern already used for Profile/Actions.
- Profile tab gains new sectioned cards (per the "Option B" layout in the design mockup): Rating
  breakdown, Recent reviews, Subjects, Cancellations, Most-frequent counterparts. Rating breakdown
  and Recent reviews render only for tutors.
- Each new tab's data (Schedule grid, Bookings page, expanded Profile stats) is fetched lazily —
  on first activation of that tab — via new methods on `src/stores/superadmin.js`, following the
  existing `api.get('/admin/users/...', { params })` pattern already used there. Fetched data is
  cached in component/store state keyed by user id + tab, so switching tabs within one modal
  session does not refetch.
- Bookings tab: table with columns date, time, subject, tutor name, tutee name, session mode,
  status; pagination controls (10/page); a date filter row with preset buttons (Last 7/30/90
  days, All time) plus a custom-range option (from/to date inputs). Changing the filter resets to
  page 1 and refetches.
- Schedule tab: 7-column (Mon–Sun) x time-slot-row grid built from the tutor's `TutorAvailability`
  rows. Each cell is Open / Booked / Inactive per the `is_active`/`is_booked` combination. Clicking
  a Booked cell switches to the Bookings tab and scrolls to / highlights the matching booking row
  (matched by the booking's `availability` FK).
- Each tab (Profile, Schedule, Bookings) has its own "Export CSV" button, calling a matching
  export endpoint with `responseType: 'blob'`, following the existing
  `exportAnalyticsCsv` blob-download pattern in `superadmin.js`. The Bookings export request
  includes whatever date filter is currently applied.

**Backend (`backend/studybuddy/`)**
- New `APIView`-based endpoints under the existing `admin/users/<pk>/...` URL convention, gated by
  the existing `permissions.IsAuthenticated, IsSuperAdminUser` pattern used throughout
  `admin_views.py`:
  - `GET admin/users/<pk>/bookings/` — paginated (`page`, default 10/page), filterable by
    `date_from`/`date_to` query params. Returns bookings where the user is either `student` or
    `tutor.profile`, each row including subject name, both party names, mode, status, date/time
    (via the linked `TutorAvailability.time_slot`).
  - `GET admin/users/<pk>/bookings/export/` — same filtering as above (no pagination), returns
    `text/csv` via `csv.writer`, following the existing `AdminAnalyticsExportView` pattern.
  - `GET admin/users/<pk>/availability/` — tutor-only (400/403 if called for a non-tutor); returns
    all `TutorAvailability` rows for that tutor with computed state (open/booked/inactive) and,
    for booked slots, the linked booking id for client-side jump-to-booking.
  - `GET admin/users/<pk>/availability/export/` — CSV of the same slot data.
  - `GET admin/users/<pk>/stats/` — computes and returns: rating distribution (count per 1-5
    score, tutors only, from `Rating`), most recent 3-5 reviews (tutors only), subjects
    taught/studied (from `TutorSubjects` for tutors, distinct `Booking.subject` for tutees),
    cancellation counts split by `cancelled_by_role` matching vs. not matching this user's role on
    each booking, and top-3 most-frequent counterparts with session counts (grouped `Booking` by
    counterpart).
  - `GET admin/users/<pk>/stats/export/` — CSV of the same stats as flat key-value rows.
- No new pagination class is introduced project-wide; the Bookings endpoint implements its own
  simple `page`/`page_size` query-param handling (no existing `DEFAULT_PAGINATION_CLASS` exists in
  `REST_FRAMEWORK` settings to build on, and no other endpoint needs pagination yet).
- No schema changes. All values are computed on request from existing models
  (`Booking`, `Rating`, `TutorSubjects`, `TutorAvailability`) — no new fields, no signals, no
  migrations.

## Testing Decisions

- Tests exercise the Django REST API boundary only, via `APITestCase` with
  `force_authenticate(user=self.super_user)`, matching the existing pattern in
  `SuperAdminRedesignApiTests` (`backend/studybuddy/tests.py`). Tests should assert response
  status, response body shape/values, and — for export endpoints — `Content-Type: text/csv` and
  correct row content, not implementation details of how the queryset was built.
- Cases to cover per endpoint:
  - Bookings: default (unfiltered, page 1) returns 10 most recent; date-range filtering narrows
    correctly; pagination metadata (`total`, `page`, `page_size`) is correct; both tutor and tutee
    identities appear on each row regardless of which role's modal it was requested from.
  - Availability: tutor-only enforcement (403/400 for a tutee id); cell state matches
    `is_active`/`is_booked` combinations; booked cells include the correct booking id.
  - Stats: rating distribution sums to the known ratings count; cancellation split matches known
    fixture data; top-3 counterpart ordering is by session count descending; tutee responses omit
    rating/review fields entirely.
  - Export endpoints: correct `Content-Type`, correct header row, correct data rows for a known
    fixture, and that the Bookings export respects the same date filter as the JSON endpoint.
- No frontend component tests are added — this repo's frontend testing convention is `npm run
  lint` and `npm run build` as the baseline checks, with Vitest reserved for store/logic-level
  tests rather than admin UI components.

## Out of Scope

- "Hours learning/taught" — no duration field exists on `Booking`/`TutorAvailability` (slots are a
  single `time_slot`, not a start/end range); adding it would require a schema change and is not
  part of this spec.
- Any tutor-rates-student direction — `Rating` is one-directional (student rates tutor only), so
  tutees never get a rating breakdown/reviews section.
- Denormalized/cached stat fields, signals, or migrations — everything here is computed live.
- Combined/bundled export (all three tabs into one file) — each tab exports independently.
- Any change to `AdminUserListView`'s existing list/patch behavior, or to the Actions tab.
- A tutor/tutee-facing (non-admin) version of any of these views.
- Gamification (streaks, badges, levels) — confirmed not present anywhere in the codebase and not
  requested here.

## Further Notes

- This spec's design mockup (`docs/mockups/2026-07-13-superadmin-tutor-tutee-stats.html`)
  supersedes an earlier slide-over-panel exploration of the same underlying problem
  (`docs/mockups/2026-07-12-superadmin-user-drilldown.html`, decided 2026-07-12). That prior
  decision is left in place as a historical record but is not the direction being implemented.
- Since no `DEFAULT_PAGINATION_CLASS` exists yet in `REST_FRAMEWORK` settings, the pagination
  approach introduced for the Bookings endpoint is local to that endpoint, not a project-wide
  convention change.

## Changelog

- 2026-07-13: Spec created from `/grill-with-docs` interview + `/to-spec` synthesis. Mockup saved
  to `docs/mockups/2026-07-13-superadmin-tutor-tutee-stats.html`. Status: Approved.
