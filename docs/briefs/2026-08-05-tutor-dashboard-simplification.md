# Brief: Tutor dashboard simplification and booking pagination

Follow this brief exactly. Standing rules are in AGENTS.md. Reference:
[`docs/plans/2026-08-05-tutor-dashboard-simplification.md`](../plans/2026-08-05-tutor-dashboard-simplification.md)
and the agreed design at
[`docs/mockups/2026-08-05-tutor-dashboard-simplification.html`](../mockups/2026-08-05-tutor-dashboard-simplification.html)
(open it — it is the visual source of truth for layout, states and copy).

## Scope

Rewrite `src/views/TutorDashboard.vue` from a six-card metric grid over an unpaginated booking-card
list into a work queue: a three-value compact metric strip above a two-column
`sidebar-and-main` layout, with a date-grouped, client-side-paginated schedule in the main column and
a `Needs Attention` rail on the right.

**In scope:** `src/views/TutorDashboard.vue`, a new pure helper module for day-packing and
status-routing, and Vitest coverage for that helper. Updating the existing
`src/views/TutorDashboard.test.js` so it still passes.

**Out of scope — do not touch:**
- Any file under `backend/`. **No backend change is required.** The endpoint already returns
  everything needed. Do not add pagination params, do not modify `tutor_dashboard`.
- `src/views/TutorSchedule.vue`, `src/views/TutorSessionsReports.vue`,
  `src/views/TutorBookingDetailsFlow.vue`, `src/components/OngoingBookingBar.vue`.
- The global `OngoingBookingBar` behaviour. Do **not** add a pinned "live session" bar to the
  dashboard — it already exists app-wide at `src/App.vue:255`.
- Any other view's styling. No drive-by refactors.

## Execution checklist

### 1. Extract a pure helper module

Create `src/services/tutorDashboard.js` (plain functions, no Vue imports) exporting:

- `splitBookingsByAttention(bookings)` → `{ requests, payments, schedule }`
- `groupByDate(bookings)` → ordered array of `{ date, bookings }`, days ascending, bookings ascending
  by `startTime` within a day
- `dayPackedPages(dayGroups, target = 6)` → array of pages, each an array of day groups

Routing rules for `splitBookingsByAttention` — **read this carefully, it is the subtlest part**:

| Booking | `requests` | `payments` | `schedule` |
| --- | --- | --- | --- |
| `raw_status === 'Pending'` | yes | — | — |
| `status === 'Payment Required'` | — | yes | yes |
| `raw_status === 'Awaiting Payment Verification'` | — | yes | yes |
| everything else (`Upcoming`, `Ongoing`, …) | — | — | yes |

- Route on **`raw_status`** for every bucket **except** the `Payment Required` case, which routes on
  the derived **`status`** field. This is deliberate. `get_display_status`
  (`backend/studybuddy/views.py:1028-1048`) turns a `Confirmed` booking into `Upcoming` / `Ongoing` /
  `Payment Required` depending on the clock, and `display_status` is *additionally* rewritten to
  `Payment Required` when `BOOKING_DEV_TOOLS_ENABLED` is on (`views.py:2047-2053`). Routing the other
  buckets by display value would make behaviour differ between environments.
- Compare statuses case-insensitively and tolerate `null`/`undefined` — the fallback list (see item 4)
  may omit `raw_status`. A booking missing `raw_status` must fall through to `schedule`, never be
  dropped from all three buckets.

`dayPackedPages` rules:
- Accumulate whole day groups until adding the next group would exceed `target` bookings.
- **Never split a day across pages.**
- Always emit at least one day per page, so a single day with more than `target` bookings gets its
  own page rather than looping forever.
- Page sizes therefore vary; that is expected.

- [ ] `src/services/tutorDashboard.js` exists and exports the three functions, with no Vue imports.
- [ ] `splitBookingsByAttention` implements the table above, is case-insensitive, and sends a booking
      with a missing `raw_status` to `schedule`.
- [ ] `dayPackedPages` never splits a day, always emits ≥1 day per page, and handles a single day
      larger than `target`.
- [ ] Tests in `src/services/tutorDashboard.test.js` cover: each routing row; a `Payment Required`
      booking appearing in **both** `payments` and `schedule`; a `Pending` booking appearing **only**
      in `requests`; a missing-`raw_status` booking landing in `schedule`; day-packing with an
      oversized single day; and an empty input.

### 2. Metric strip

Replace the `dashboardMetrics` computed (`src/views/TutorDashboard.vue:156-218`) with exactly three
metrics: **Wallet Balance**, **Avg Rating** (`x.x / 5.0`), **Accepted Sessions** (`n / limit`).

Delete outright: the `Earnings`, `Total Sessions` and `Next Session` metrics; the `visual`, `tone`,
`bars` and `progress` fields; the ring `<svg>` and `.metric-bars` markup (`:21-40`); and all
now-unused CSS (`.metric-ring*`, `.metric-bars*`, `.metric-icon-*`, `.metric-visual*`). The bar
arrays were hardcoded fake data — they must not survive in any form.

`Earnings` and `Total Sessions` already exist on `TutorSessionsReports.vue:311,319`; nothing is lost.

- [ ] Exactly three metrics render, in a single horizontal strip of equal-width cells.
- [ ] No SVG rings, no bar sparklines, and no hardcoded numeric arrays anywhere in the file.
- [ ] When `accepted_session_load >= session_load_limit`, the Accepted cell gets a gold tint plus an
      "At capacity" note (see the mockup's "At the accepted-session limit" section).

### 3. Layout

Two-column CSS Grid: `1fr 300px`, gap `~14px`, `align-items: start`. Main column = schedule, right
column = `Needs Attention` rail.

- When the rail has **no** content, `v-if` the entire rail out of the DOM and drop the grid to a
  single column so the schedule reflows to full width. Do **not** render an empty rail container or
  an "all caught up" placeholder.
- Below ~900px collapse to one column with the rail **first**, and let rows stack internally.

- [ ] Grid is `1fr 300px` with content, single-column without.
- [ ] Empty rail is absent from the DOM, not merely visually hidden.
- [ ] At narrow widths the page is one column, rail first, with no horizontal scrolling.

### 4. Schedule column

Heading **"Full Schedule"** with an `n committed` count. Rows grouped under date headers showing the
weekday/date, a `· Today` / `· Tomorrow` accent where applicable, and an `n sessions` count.

Each row: start time · student name + `subject · duration` · status pill · `View` button routing to
`booking-details` with the booking id (reuse the existing `goToBookingDetails` and `getBookingId`).

Keep the existing fallback at `src/views/TutorDashboard.vue:245-249` (`apiBookings.length ?
apiBookings : fallbackBookings`) — it must keep working, which is why item 1 requires tolerating a
missing `raw_status`.

Pager below the list: `Showing X-Y of N` on the left (**actual** range — page sizes vary), numbered
pages with prev/next on the right. Clamp `currentPage` whenever the booking data reloads: the
existing `route.query.refresh` watcher (`:364-369`) can shrink the list while the tutor sits on
page 3, which must not render an empty schedule.

- [ ] Rows are grouped under date headers; the date is not repeated per row.
- [ ] Pager shows the true range and total; page sizes may differ between pages.
- [ ] Reloading data while on a page beyond the new last page clamps to the last valid page.
- [ ] `View` still navigates to the `booking-details` route with the same id resolution as today.
- [ ] `Ongoing` bookings render inline with a distinct pill — **no** pinned bar.

### 5. Needs Attention rail

Heading **"Needs Attention"** with a total count. Two subsections:

- **Payments** — always rendered when it has rows. **Never capped.**
- **Requests** — rendered **only if** `requests.length > 0`. **No cap, no expander.**

**Why Requests is conditional:** `Pending` bookings can no longer be created. ADR 0008
(`docs/adr/0008-instant-booking-replaces-request-to-book.md:19`) records that Instant Booking removed
the approve/reject flow outright and that `Pending` "survives only as a historical status value on old
rows"; the only live creation path sets `status='Confirmed'` (`backend/studybuddy/views.py:2670`).
The subsection exists solely so legacy rows are not stranded, and retires itself once they age out.
Do not build a cap or an expander for it — the earlier design called for one, and it was removed
because the state it guarded against is unreachable.

Rail rows are narrow (300px), so stack internally: name, then `subject` + date/time, then pill +
`View`. See the mockup.

- [ ] Payments subsection renders uncapped whenever it has rows.
- [ ] Requests subsection is absent from the DOM when there are no legacy Pending bookings.
- [ ] Neither subsection has a cap or "show more" control.
- [ ] Rail header count equals `requests.length + payments.length`.

### 6. Empty and warning states

**No bookings at all:** replace the current dashed panel (`:123-126`) with a hero reading
**"No sessions yet"**, sub-copy *"Tutees find you through your subjects and availability. Make sure
both are set so you show up in search."*, and a primary button **"Check my availability"** routing to
the named route `tch-availability` (`src/router/index.js:147-152`).

**Load limit:** keep the existing banner at `:3-5` with its **copy unchanged, verbatim** — it already
names the remedy. Do **not** add a "Learn more" button; there is no help or FAQ route to link to.
Pair it with the gold Accepted cell from item 2.

Preserve the existing loading and error states, including the Retry button.

- [ ] Empty hero renders with the CTA, and the button navigates to `tch-availability`.
- [ ] Load-limit banner text is byte-identical to the current copy and has no button.
- [ ] Loading spinner, error message and Retry still work.

### 7. Keep the existing test green

`src/views/TutorDashboard.test.js` mounts the component and asserts on `Wallet Balance` and
`PHP 1,250`. Both survive this redesign, so it should keep passing — update it only if the redesign
genuinely changes its assumptions, and say so under Deviations if you do.

- [ ] `src/views/TutorDashboard.test.js` passes, updated only if genuinely necessary.

## Context

**Files, located fresh for this brief:**

| Path | Role |
| --- | --- |
| `src/views/TutorDashboard.vue` | The component being rewritten (839 lines, template + `<script setup>` + scoped CSS) |
| `src/views/TutorDashboard.test.js` | Existing Vitest mount test that must stay green |
| `src/services/tutorDashboard.js` | **New** — pure helper module |
| `src/services/tutorDashboard.test.js` | **New** — its unit tests |
| `src/router/index.js:147-152` | `tch-availability` route for the empty-state CTA |
| `backend/studybuddy/views.py:2176-2267` | `tutor_dashboard` endpoint — **read only, do not modify** |
| `backend/studybuddy/views.py:1028-1048` | `get_display_status` — read only; explains the status split |
| `docs/adr/0008-instant-booking-replaces-request-to-book.md` | Why Requests is conditional |

**Payload shape** returned by `tutor-dashboard/`, per `build_combined_block`
(`backend/studybuddy/views.py:2055-2077`) — everything the UI needs already exists:

`id`, `session_group_id`, `booking_request_id`, `status` (derived display value), `raw_status`
(DB value), `date`, `student`, `tuteeName`, `subject`, `startTime` (`"HH:MM"`), `endTime` (`"HH:MM"`),
`duration_hours`, `preferred_location`, `session_mode`.

Top-level: `total_sessions`, `rating_average`, `hourly_rate`, `total_earnings`, `session_load_limit`,
`accepted_session_load`, `session_load_remaining`, `upcoming_bookings`.

Possible `status` values on this screen: `Pending`, `Upcoming`, `Ongoing`, `Payment Required`,
`Awaiting Verification`.

**Conventions (from `.claude/CLAUDE.md`):**
- Vue 3 `<script setup>`, Composition API. 2-space indent, LF, 100-char lines.
- Prettier: **single quotes, no semicolons**.
- **No hardcoded hex colours** — use the `--sb-*` CSS custom properties defined in `App.vue`
  (`--sb-primary`, `--sb-card-bg`, `--sb-card-border`, `--sb-text-main`, `--sb-text-muted`, …). The
  existing file's `color-mix(in srgb, var(--sb-primary) …)` pattern is the house style; follow it.
  The mockup uses literal hex only because it is a standalone HTML file — **do not copy those hex
  values into the component.**
- Reuse local component patterns (`.sb-btn-pill`, `.sb-card`, `.sb-badge`) where they fit.
- **No emojis** anywhere — code, comments, or docs.
- Keep API access going through `src/services/api/api.js`; do not add axios/fetch calls.

**Existing status-pill classes** in the component (`status-badge-upcoming`, `-ongoing`, `-warning`,
`-completed`, `-danger`, `-pending`) and `getStatusClass` (`:340-360`) already cover every value
above — reuse them rather than inventing new ones.

## Contract

- Work ONLY this brief — no scope creep, no drive-by refactors.
- TDD: failing test first, then the minimal implementation, matching existing style.
- Run typecheck and the relevant tests; get them green; paste commands and output under Test evidence.
- NEVER commit, push, branch, or run any git write. Leave the tree dirty.
- Record anything done differently, and why, under Deviations.

Commands to run and paste output for:

```
npm run lint
npm run test
npm run build
```

Do **not** run `python manage.py test` — no backend file is touched by this brief.

## Test evidence

(Codex fills this in.)

## Deviations

(Codex fills this in.)
