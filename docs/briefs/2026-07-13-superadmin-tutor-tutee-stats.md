# Brief: SuperAdmin tutor/tutee stats, schedule & bookings

Follow this brief exactly. Standing rules are in AGENTS.md. Reference:
`docs/plans/2026-07-13-superadmin-tutor-tutee-stats.md` (full spec) and
`docs/mockups/2026-07-13-superadmin-tutor-tutee-stats.html` (approved visual design).

## Scope

In scope — the whole spec (no tickets file exists for this plan yet):

- Three new read endpoints + three matching CSV export endpoints under `admin/users/<pk>/...`.
- Two new tabs (Schedule, Bookings) in `SuperAdminUserModal.vue`, plus new stat sections in the
  existing Profile tab.
- Lazy per-tab data loading with client-side caching, and a CSV export button per tab.

Out of scope (do not touch):

- `AdminUserListView`'s existing list/patch behavior, and the Actions tab.
- Any schema change, migration, or new model field — everything is computed live from existing
  models (`Booking`, `Rating`, `TutorSubjects`, `TutorAvailability`, `Tutor`).
- "Hours learning/taught" — no duration field exists and adding one is explicitly out of scope.
- A combined/bundled export, gamification, or any tutor/tutee-facing (non-admin) view.

## Execution checklist

### 1. Backend: `GET admin/users/<pk>/bookings/` + `GET admin/users/<pk>/bookings/export/`

Build a paginated, date-filterable booking-history endpoint, plus its CSV twin.

- New view class(es) in `backend/studybuddy/admin_views.py`, following the exact
  `permission_classes = [permissions.IsAuthenticated, IsSuperAdminUser]` pattern already used by
  `AdminUserListView` (lines 319-438) in that file.
- Query `Booking` rows where the target user (by `pk`, a `UserProfile` id) is either `student` or
  `tutor.profile`. Support query params `date_from`, `date_to` (both optional; unfiltered =
  "all time"), and `page` (default 1), fixed `page_size=10`. No project-wide
  `DEFAULT_PAGINATION_CLASS` exists (`backend/backend/settings.py` lines 122-137) — implement
  pagination locally in this view, do not add one globally.
- Each row must return: date, time (via the linked `TutorAvailability.time_slot`), subject name,
  tutor's full name, tutee's full name, session mode, status — regardless of which role's modal
  triggered the request (both names always present).
- Response includes pagination metadata: `total`, `page`, `page_size`.
- `bookings/export/` reuses the same filtering (no pagination — full filtered set), returns
  `text/csv` via `csv.writer`/`HttpResponse`, following the exact pattern in
  `AdminAnalyticsExportView` (`admin_views.py` lines 824-884): `Content-Disposition` header, header
  row, one row per booking with the same columns as the JSON endpoint.
- Add both URLs in `backend/studybuddy/urls.py` near the existing `admin/users/` block (around
  line 56) and `admin/analytics/export/` (line 65), matching the flat `admin/<resource>/<pk>/<sub>/`
  convention already there.

**Acceptance criteria**
- [ ] Unfiltered request returns the 10 most recent bookings (by date/time descending), correct
      pagination metadata.
- [ ] `date_from`/`date_to` narrows results correctly; invalid/reversed ranges return a 400.
- [ ] Both tutor and tutee names appear on every row regardless of which user's `pk` was queried.
- [ ] `bookings/export/` returns `Content-Type: text/csv`, correct header row, and rows matching
      the same filter as the JSON endpoint for identical query params.
- [ ] Both endpoints 403 for a non-SuperAdmin caller (reuse `IsSuperAdminUser`).

### 2. Backend: `GET admin/users/<pk>/availability/` + `.../availability/export/`

Tutor-only weekly schedule endpoint, plus CSV twin.

- New view in `admin_views.py`. If the target user's role is not `Tutor`, return 400.
- For the tutor (via `Tutor` model, `models.py` lines 211-306, one-to-one on `UserProfile`), return
  every `TutorAvailability` row (`models.py` lines 679-708: fields `day`, `time_slot`,
  `is_active`, `is_booked`) with a computed `state`: `"booked"` if `is_active and is_booked`,
  `"inactive"` if `not is_active`, else `"open"`.
- For `state == "booked"` rows, include the matching `Booking.id` (join on the `availability` FK
  from `Booking`, `models.py` lines 746-845) so the frontend can jump to that row in the Bookings
  tab.
- `.../availability/export/` — same data as CSV: day, time slot, state, booking id (blank if not
  booked). Same `AdminAnalyticsExportView`-style CSV pattern.
- Add both URLs in `urls.py` next to the bookings URLs from item 1.

**Acceptance criteria**
- [ ] Requesting for a Tutee `pk` returns 400.
- [ ] Every `TutorAvailability` row for the tutor is present with the correct computed `state`.
- [ ] Booked rows include the correct linked `Booking.id`.
- [ ] Export endpoint returns `text/csv` with matching data.

### 3. Backend: `GET admin/users/<pk>/stats/` + `.../stats/export/`

Expanded profile stats, computed live, no new fields.

- New view in `admin_views.py`. Compute, from existing models only:
  - **Rating distribution** (tutors only): count of ratings at each score 1-5, from `Rating`
    (`models.py` lines 990-1017) filtered by `tutor=<this tutor>`.
  - **Recent reviews** (tutors only): most recent 3-5 `Rating` rows (score + comment + reviewer
    name), newest first.
  - **Subjects**: for tutors, `TutorSubjects` rows (`models.py` lines 668-678: `subject`,
    `expertise_level`) for this tutor. For tutees, distinct `Subjects` (`models.py` lines 656-667)
    referenced by this user's `Booking.subject` across their bookings.
  - **Cancellations**: two counts from `Booking` where `status == "Cancelled"` and this user is a
    party — one where `cancelled_by_role` matches this user's role on that booking ("by user"),
    one where it doesn't ("by counterpart").
  - **Top-3 most-frequent counterparts**: group this user's `Booking` rows by counterpart (tutee's
    tutors, or tutor's students), count sessions per counterpart, return top 3 descending by
    count, with counterpart name + count.
  - For a Tutee `pk`, omit rating distribution and recent reviews from the response entirely (not
    empty arrays — the keys should not imply tutors-only data exists for a tutee).
- `.../stats/export/` — same computed stats flattened into key-value CSV rows (stat name, value;
  for rating distribution, one row per star level; for top-3 counterparts, one row per entry).
- Add both URLs in `urls.py` alongside the others.

**Acceptance criteria**
- [ ] Rating distribution counts sum to the tutor's total ratings count.
- [ ] Cancellation split matches known fixture data exactly (by-user vs by-counterpart).
- [ ] Top-3 counterparts ordered by session count descending; ties broken by counterpart name.
- [ ] Tutee response has no rating-distribution/recent-reviews keys.
- [ ] Export endpoint returns `text/csv` with correct flattened rows.

### 4. Frontend: `src/stores/superadmin.js` — new actions

Add store actions calling the three new endpoint groups, following the existing patterns in this
file (`api.get('/admin/users/...', { params })` as in `fetchUsers`, lines 70-95; blob-download CSV
pattern as in `exportAnalyticsCsv`, lines 284-309).

- `fetchUserBookings(userId, { page, dateFrom, dateTo })` → `GET admin/users/<id>/bookings/`.
- `exportUserBookingsCsv(userId, { dateFrom, dateTo })` → blob download, same pattern as
  `exportAnalyticsCsv`.
- `fetchUserAvailability(userId)` → `GET admin/users/<id>/availability/`.
- `exportUserAvailabilityCsv(userId)` → blob download.
- `fetchUserStats(userId)` → `GET admin/users/<id>/stats/`.
- `exportUserStatsCsv(userId)` → blob download.
- Add all six to the store's `return { ... }` export block (starts around line 311).

**Acceptance criteria**
- [ ] Each fetch action returns parsed JSON matching its endpoint's response shape.
- [ ] Each export action triggers a file download via the same `Blob`/temporary-`<a>` pattern as
      `exportAnalyticsCsv`, with a sensible filename (e.g. `bookings-<userId>.csv`).

### 5. Frontend: `src/components/SuperAdminUserModal.vue` — new tabs + expanded Profile

- Add `Schedule` and `Bookings` entries to the tab-button markup (currently Profile/Actions only,
  lines 30-51), following the existing button pattern. Render the `Schedule` tab button only when
  `props.user.role === 'Tutor'`.
- Extend `activeTab` handling (currently `ref('profile')`, line 204) to support `'schedule'` and
  `'bookings'` values, each with its own `v-if` template block (matching the existing
  Profile/Actions block structure at lines 53-86+).
- **Lazy loading + caching**: on first activation of `schedule` or `bookings` (or the new stats
  section within `profile`), call the matching store action once; cache the result in local
  component state keyed by tab, so re-switching tabs within the same modal open does not refetch.
  Reset the cache when the modal is opened for a different user.
- **Profile tab**: add sectioned cards (matching the "Option B" layout in
  `docs/mockups/2026-07-13-superadmin-tutor-tutee-stats.html`) for: Rating breakdown (bar-style
  1-5 star distribution, tutors only), Recent reviews (tutors only), Subjects (tag/chip list,
  tutor: with expertise level; tutee: without), Cancellations (two-number split), Most-frequent
  counterparts (top-3 list with session counts). Use this repo's existing card/badge/chip CSS
  patterns already present in this file rather than inventing new ones.
- **Schedule tab**: 7-column (Mon-Sun) x time-slot-row grid, one cell per `TutorAvailability` row,
  colored/styled per its `state` (open/booked/inactive) per the mockup, with a legend. Clicking a
  booked cell switches `activeTab` to `'bookings'` and scrolls to/highlights the row matching that
  cell's linked booking id.
- **Bookings tab**: paginated table (columns: date, time, subject, tutor name, tutee name, mode,
  status), date-filter row with preset buttons (Last 7/30/90 days, All time) plus a custom
  from/to range option, and pagination controls. Changing any filter resets to page 1 and
  refetches via the store action.
- Add an "Export CSV" button to each of the three tabs (Profile, Schedule, Bookings), each calling
  its matching store export action. The Bookings export call must pass whatever date filter is
  currently applied in that tab's UI state.

**Acceptance criteria**
- [ ] Schedule tab button/content only appears for users with `role === 'Tutor'`.
- [ ] Switching to Schedule or Bookings for the first time triggers exactly one network request;
      switching away and back does not refetch.
- [ ] Opening the modal for a different user resets all cached tab data.
- [ ] Bookings tab pagination and date filters work end-to-end against the real endpoint.
- [ ] Clicking a booked Schedule cell switches to Bookings and highlights the correct row.
- [ ] Each tab's Export CSV button downloads a file via the store's export action.

## Context

- **Domain vocabulary**: "Tutee" = student role; "Tutor" = the paired role with a dedicated
  `Tutor` model (`UserProfile` has no separate `Tutee` model — tutees are plain `UserProfile` rows
  with `role='Tutee'`).
- **`Rating` is one-directional** — student rates tutor only. Never add a rating/review section
  for tutees; there is no model support for it.
- **No pagination convention exists project-wide** (`REST_FRAMEWORK` settings,
  `backend/backend/settings.py` lines 122-137, has no `DEFAULT_PAGINATION_CLASS`). Do not add one
  globally — implement pagination locally in the new bookings view only.
- **No schema changes anywhere in this brief.** Every new field is computed at request time from
  `Booking`, `Rating`, `TutorSubjects`, `Subjects`, `TutorAvailability`, `Tutor` — no migrations,
  no signals, no denormalized fields.
- **CSV export precedent**: `AdminAnalyticsExportView` (`admin_views.py` lines 824-884) on the
  backend, `exportAnalyticsCsv` (`superadmin.js` lines 284-309) on the frontend — copy these
  patterns rather than inventing a new export mechanism.
- **Test precedent**: `SuperAdminRedesignApiTests` (`backend/studybuddy/tests.py` lines 54-264)
  shows the `force_authenticate` + `self.client.get(...)` + status/Content-Type assertions pattern
  to follow for all new endpoint tests, including the CSV `Content-Type: text/csv` assertion at
  line 261.
- **Frontend styling**: this repo avoids hardcoded hex colors — use the CSS custom properties
  already defined in `App.vue` (`--sb-primary`, etc.) and the local component patterns in
  `.claude/skills/shadcn-components.md` (`.sb-btn-pill`, `.sb-card`, `.sb-badge`) rather than the
  raw hex values used in the throwaway HTML mockup — the mockup is a layout/behavior reference
  only, not a literal style source.
- **Approved visual reference**: `docs/mockups/2026-07-13-superadmin-tutor-tutee-stats.html` shows
  the agreed layout for all three tabs (Option B sectioned-card Profile, Schedule grid with
  legend, Bookings table with filters/pagination) — match its structure and information hierarchy,
  not its literal CSS.

## Contract

- Work ONLY this brief — no scope creep, no drive-by refactors.
- TDD: failing test first, then the minimal implementation, matching existing style.
- Run typecheck and the relevant tests; get them green; paste commands and output under Test
  evidence. Backend: `python manage.py test studybuddy.tests` (or the specific new test class).
  Frontend: `npm run lint` and `npm run build` (no new Vitest component tests required per this
  repo's convention — Vitest is reserved for store/logic-level tests).
- NEVER commit, push, branch, or run any git write. Leave the tree dirty.
- Record anything done differently, and why, under Deviations.

## Test evidence

- `python manage.py test studybuddy.tests.SuperAdminUserDetailApiTests --keepdb`
  - `Found 9 test(s).`
  - `Ran 9 tests in 30.944s`
  - `OK`
- `npm run lint:eslint -- --no-fix`
  - Exit code 0.
- `npm run build`
  - `320 modules transformed.`
  - `built in 3.83s`
- `git diff --check`
  - Exit code 0.
- `python manage.py test studybuddy.tests --keepdb`
  - Started, then interrupted at the owner's request so they can complete manual testing.
- `npm run lint`
  - Could not complete because of an unrelated pre-existing oxlint error at
    `src/router/index.js:266`: unused `from` parameter.

## Deviations

- The full Django test module was not completed because the owner asked to stop testing and hand
  off the implementation. The focused nine-test endpoint class passed.
- Aggregate frontend lint remains blocked by the pre-existing router error above. The ESLint half
  and production build both pass; the unrelated router file was not changed because it is outside
  this brief.
