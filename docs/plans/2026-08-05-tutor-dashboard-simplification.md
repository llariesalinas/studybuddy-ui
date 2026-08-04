---
title: Tutor dashboard simplification and booking pagination
date: 2026-08-05
status: In Progress
summary: Replace the six-card metric grid with a 3-metric strip and rebuild the booking list as a date-grouped, day-packed paginated schedule with a Needs Attention rail.
spec: ../mockups/2026-08-05-tutor-dashboard-simplification.html
---

# Tutor dashboard simplification and booking pagination

Agreed design: [`docs/mockups/2026-08-05-tutor-dashboard-simplification.html`](../mockups/2026-08-05-tutor-dashboard-simplification.html)

**Status & Progress Summary** (2026-08-05, updated): In Progress — compiled to a Codex brief at
`docs/briefs/2026-08-05-tutor-dashboard-simplification.md`. Amended before dispatch: a
pre-brief check found that `Pending` bookings can no longer be created (ADR 0008 / Instant Booking;
the live path sets `status='Confirmed'` at `views.py:2670`), so the rail's `Requests` subsection is
now conditional and self-retiring, and its cap-plus-expander was dropped as solving an impossible
state. Everything else from the design session stands. A grill +
ui-preview session settled every design question across five mockup rounds: dashboard reframed as a
work queue rather than a metrics report, six metric cards cut to a three-value compact strip, and
the booking list rebuilt as a date-grouped schedule with client-side day-packed pagination beside a
`Needs Attention` rail. Two findings from the code changed the design mid-session — `get_display_status`
splits `Confirmed` into three clock-dependent states (so an ended session showing `Payment Required`
would have been buried by pagination), and `OngoingBookingBar` is already mounted app-wide (so the
proposed pinned live bar was dropped as duplication). No backend change required. Next step is
implementation against the Steps below.

## Goal

`TutorDashboard.vue` currently renders six equally-weighted metric cards above an unpaginated list
of full-size booking cards. It reads as a metrics report competing with a work queue, and the
booking list grows without bound. Make bookings the page, cut the metric strip to what a tutor
actually acts on, and paginate the list.

## Approach

Decided in a grill + ui-preview session on 2026-08-05. Key decisions and the reasoning behind each:

**Bookings are the page.** A tutor's daily loop is "who booked me, what do I owe." Wallet, earnings
and rating are lookup-when-curious numbers that already have dedicated screens.

**Three metrics, compact strip.** Keep Wallet Balance, Avg Rating, Accepted Sessions. Drop Earnings
and Total Sessions (both already on `TutorSessionsReports.vue:311,319`) and Next Session (redundant
once the schedule is the page). Remove the ring and bar visuals entirely — the bars were fabricated
data (`TutorDashboard.vue:164,191,216` used hardcoded arrays), so this also removes the only
invented numbers on the screen.

**Layout pattern: sidebar-and-main** (`1fr + 300px`), schedule in the main column, a `Needs
Attention` rail on the right. Chosen over a vertical stack because a heavy request week grows the
rail rather than pushing the schedule off-screen. Right rather than left, since the app already has
a nav sidebar on the left.

**Date-grouped rows.** Date headers absorb the repeated date field; each row carries time, student,
subject, duration, status, action.

**Client-side pagination.** `tutor_dashboard` (`backend/studybuddy/views.py:2217-2266`) already
returns every upcoming booking and groups them into contiguous blocks in Python, so server-side
paging would still fetch and group the full queryset — no DB saving. **No backend change required.**

**Day-packed pages.** Accumulate whole days toward a target of 6 bookings, never splitting a day
across pages; always take at least one day so a single heavy day gets its own page. Avoids the same
date header appearing at the bottom of one page and the top of the next.

**Status routing.** Route on `raw_status` for every bucket *except* Payments, which routes on the
derived `status`. This is deliberate: `get_display_status` (`views.py:1028-1048`) turns a
`Confirmed` booking into `Upcoming` / `Ongoing` / `Payment Required` depending on the clock, and
`display_status` is additionally rewritten to `Payment Required` when `BOOKING_DEV_TOOLS_ENABLED`
is on (`views.py:2047-2053`). Routing the other buckets by display value would make behaviour differ
between environments.

| Booking | Rail | Schedule |
| --- | --- | --- |
| `raw_status = Pending` (legacy only) | Requests, if any exist | — |
| `display = Payment Required` | Payments | yes |
| `raw = Awaiting Payment Verification` | Payments | yes |
| `display = Upcoming` / `Ongoing` | — | yes |

A Pending booking is a *request*, not committed time, so it must not render as a scheduled session.
Payment-bucket bookings are committed time that also owe an action, so they appear in both.

**Pending is vestigial — the Requests subsection is conditional and self-retiring.** ADR 0008
(`docs/adr/0008-instant-booking-replaces-request-to-book.md:19`) records that Instant Booking removed
the approve/reject flow outright and that `Pending` "survives only as a historical status value on old
rows". The code agrees: the only live creation path sets `status='Confirmed'` (`views.py:2670`), and
the other `Booking.objects.create` (`views.py:2453`) sits inside a `"""`-commented-out `bulk_booking`.
So the Requests subsection renders **only when legacy Pending rows are present**, with **no cap and no
expander** — the uncapped-requests problem those solved cannot occur. It disappears on its own once
legacy rows age past the date filter. For every tutor without pre-migration data the rail holds
Payments alone.

**No pinned Ongoing bar.** `OngoingBookingBar.vue` is already mounted globally (`App.vue:255`) and
handles live sessions, handoff, and sessions starting within `UPCOMING_WINDOW_MS = 15 min`
(`stores/activeSession.js:10`). A dashboard bar would duplicate it. `Ongoing` gets an inline pill only.

**Load-limit banner unchanged.** Keep the existing two-sentence copy verbatim — it already names the
remedy — and add a gold tint to the Accepted cell so banner and number refer to each other. No
"Learn more" button: no help or FAQ route exists, and `SupportModal` is a contact form, not docs.

## Steps

1. Replace `dashboardMetrics` with the 3-metric compact strip; delete the ring/bar SVG markup, the
   `bars`/`progress`/`visual`/`tone` fields, and their CSS.
2. Add a `metricStrip` computed and an `isAtCapacity` flag for the gold tint on the Accepted cell.
3. Add derived state splitting `upcomingBookings` into `attentionRequests`, `attentionPayments`, and
   `scheduleBookings`, per the routing table above. Key off `raw_status` except the payment bucket.
4. Group `scheduleBookings` by `date` into ordered day groups.
5. Implement `dayPackedPages(groups, target = 6)` — greedy: accumulate days until adding the next
   would exceed the target; always emit at least one day per page. Extract as a small pure helper so
   it can be unit-tested directly.
6. Add `currentPage` ref, clamp it when the booking data changes, and reset to 1 on refresh.
7. Rebuild the template: banner (conditional) → metric strip → grid. Grid is `1fr 300px` when the
   rail has content, `1fr` when empty (`v-if` the rail out of the DOM, do not render it empty).
8. Build the rail: `Payments` subsection always rendered when it has rows; `Requests` subsection
   rendered only when legacy Pending rows exist — no cap, no expander.
9. Build the schedule: date-grouped rows, pager with actual range label ("Showing 1-5 of 9").
10. Replace the empty state with the "No sessions yet" hero plus a **Check my availability** button
    routing to `tch-availability`.
11. Responsive: below ~900px collapse to one column with the rail first; rows stack within.
12. Add Vitest coverage for the day-packing helper and the status-routing split.

## Risks

- **`display_status` is environment-dependent.** If `BOOKING_DEV_TOOLS_ENABLED` is on, Confirmed +
  `tutor_confirmed` bookings display as `Payment Required` and will land in the rail. Intended, but
  it means dev and prod rails differ — verify with the flag off before calling it done.
- **Day-packing with one heavy day.** A day with 8 bookings produces an 8-row page. Accepted by
  design (never split a day), but confirm it doesn't look broken.
- **Page index vs. refreshing data.** `route.query.refresh` triggers `loadTutorDashboard`
  (`TutorDashboard.vue:364-369`); if the tutor is on page 3 and the list shrinks, the index must be
  clamped or the schedule renders empty.
- **Layout shift from the collapsing rail.** Column widths change between visits depending on whether
  anything is pending. Accepted in exchange for not reserving 300px for an empty state.
- **Fallback path.** `upcomingBookings` falls back to `sessionsStore.upcomingSessions` when the API
  list is empty (`TutorDashboard.vue:245-249`). That fallback shape may lack `raw_status` — the split
  must degrade safely rather than dropping bookings from both columns.
- **Legacy Pending rows are the only source for the Requests subsection.** Seed/demo data may still
  contain them, so the section can appear in dev while being absent in production. Do not treat its
  presence in a local run as proof the path is live.
- **Accepted Sessions count vs. rail count** are different numbers (`accepted_session_load` counts
  accepted sessions; the rail counts requests + payment items). Don't let the labels imply they match.

## Checks to run

- `npm run lint` — clean.
- `npm run test` — existing suite green, plus new day-packing and routing tests.
- `npm run build` — succeeds.
- Manual, with `BOOKING_DEV_TOOLS_ENABLED` off: a tutor with 0 bookings (empty hero), a tutor with
  pending + payment items (rail populated, both columns), a tutor with nothing pending (rail
  collapsed, schedule full-width), and a tutor at 10/10 (banner + gold Accepted cell).
- No backend change, so no migration and no `python manage.py test` run required for this work.

## Changelog

- **2026-08-05** — Plan created at status Approved after a grill + ui-preview session. Decisions
  recorded: work-queue framing; 3-metric compact strip (Wallet, Rating, Accepted) with fake
  sparklines removed; right-rail `sidebar-and-main` layout; date-grouped rows; client-side
  day-packed pagination (target 6, never split a day); `Needs Attention` rail with `Requests`
  (capped at 5 + expander) and `Payments` (uncapped) subsections; status routing on `raw_status`
  except the Payments bucket; rail collapses out of the DOM when empty; new-tutor empty state with
  a `tch-availability` CTA; load-limit banner copy kept verbatim with a gold tint on the Accepted
  cell. Two mid-session reversals: pinned Ongoing bar dropped (duplicates the global
  `OngoingBookingBar`), and the "Payment Required" bucket added to the rail after
  `get_display_status` was found to split `Confirmed` into three clock-dependent states. Agreed
  mockup promoted to `docs/mockups/2026-08-05-tutor-dashboard-simplification.html`.
- **2026-08-05** — Amended during `/codex-brief` compilation, before dispatch. A pre-brief check of
  ADR 0008 and the booking-creation paths established that `Pending` bookings can no longer be
  created (Instant Booking; `views.py:2670` sets `status='Confirmed'`, and the only other
  `Booking.objects.create` at `views.py:2453` is commented out). The `Requests` subsection would
  therefore be permanently empty for any tutor without pre-migration data. Changed to a conditional,
  self-retiring subsection with the cap and inline expander removed, since the uncapped-requests
  state they guarded against is unreachable. Added a risk note that demo/seed data may still contain
  legacy Pending rows. Status moved to In Progress; brief written to
  `docs/briefs/2026-08-05-tutor-dashboard-simplification.md`.
