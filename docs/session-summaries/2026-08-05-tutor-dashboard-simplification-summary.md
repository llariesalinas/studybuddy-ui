# Tutor dashboard simplification — session summary

**Date:** 2026-08-05
**Plan:** [`docs/plans/2026-08-05-tutor-dashboard-simplification.md`](../plans/2026-08-05-tutor-dashboard-simplification.md)
**Brief:** [`docs/briefs/2026-08-05-tutor-dashboard-simplification.md`](../briefs/2026-08-05-tutor-dashboard-simplification.md)
**Mockup:** [`docs/mockups/2026-08-05-tutor-dashboard-simplification.html`](../mockups/2026-08-05-tutor-dashboard-simplification.html)
**Executor:** Codex CLI, reviewed and completed in Claude Code.

## What shipped

`src/views/TutorDashboard.vue` rebuilt from a six-card metric grid over an unpaginated booking-card
list into a work queue:

- **Metric strip** — three values (Wallet Balance, Avg Rating, Accepted Sessions) in a flat strip.
  Earnings and Total Sessions dropped (both already on `TutorSessionsReports.vue:311,319`), Next
  Session dropped as redundant once the schedule is the page. All ring/bar visuals deleted, which
  removed the only fabricated data on the screen — the sparkline arrays were hardcoded.
- **Layout** — `sidebar-and-main` CSS Grid, `1fr 300px`, collapsing to a single column below 900px
  with the rail ordered first.
- **Schedule** — date-grouped rows (time · student · subject + duration · status · View), paginated
  client-side on whole-day boundaries toward a target of 6 bookings, never splitting a day. Pager
  reports the true range, and `currentPage` is clamped when the data reloads.
- **Needs Attention rail** — `Payments` (uncapped) and `Requests` (conditional). Removed from the
  DOM entirely when empty so the schedule reflows to full width.
- **States** — new-tutor hero with a "Check my availability" CTA routing to `tch-availability`;
  load-limit banner copy unchanged, paired with a tinted Accepted cell; loading/error/Retry preserved.
- **New module** — `src/services/tutorDashboard.js` with `splitBookingsByAttention`, `groupByDate`
  and `dayPackedPages`, plus `src/services/tutorDashboard.test.js`.

**No backend change.** The existing `tutor_dashboard` payload already carried every field needed.

## Deviations from plan

- **Requests subsection reduced to conditional, cap and expander dropped.** Caught during
  `/codex-brief` compilation, before dispatch. ADR 0008 (Instant Booking) and the code
  (`views.py:2670` sets `status='Confirmed'`; the only other `Booking.objects.create` at
  `views.py:2453` is commented out) established that `Pending` bookings can no longer be created.
  The cap-plus-expander guarded against an unreachable state — a tutor accumulating dozens of pending
  requests — so it was removed and the subsection now renders only when legacy Pending rows exist.
  The plan and mockup were amended before the brief was written.
- **No pinned Ongoing bar**, decided during the design session: `OngoingBookingBar.vue` is already
  mounted app-wide (`App.vue:255`) with a 15-minute lead window (`stores/activeSession.js:10`), so a
  dashboard bar would have duplicated it. `Ongoing` renders as an inline pill.
- **Codex logged one deviation**, verified accurate: `npm run lint` is blocked by a pre-existing
  unused `draftSubjectCodes` parameter in `src/composables/useSubjectCatalog.js`, outside the brief's
  allowed files and left unchanged.

## Review findings and resolution

Three defects found in review, all fixed in-place rather than redispatched:

1. **`getDateAccent` computed date keys in UTC** via `toISOString().slice(0, 10)`. At UTC+8 every
   local time before 08:00 resolves to the previous UTC date, so "Today"/"Tomorrow" accents would be
   wrong for the first eight hours of every Manila day. Replaced with a local-parts date key.
2. **Date headers always read "sessions"**, rendering "1 sessions" for single-session days. Added
   `formatSessionCount`, matching the file's existing `formatDuration` pluralization pattern.
3. **`dayPackedPages` core path untested** — tests covered only the oversized-day and empty-input
   branches, not the main "accumulate until the next day would exceed target" behaviour. Test added.

Codex's logged evidence was independently reproduced and matched (17 files / 81 tests, build clean).
One gap in its evidence: `npm run lint` runs `run-s lint:*`, so the oxlint failure short-circuits the
chain and ESLint never ran. ESLint independently reports 4 further errors, all `no-undef` on
`require`/`process` in the root-level `make_algo_pptx.cjs` / `make_algo_pptx.js` scripts — pre-existing,
unrelated, and confirmed unmodified by this work.

## Known gap, not addressed

If a tutor's only bookings are legacy `Pending` rows, the schedule column renders its header with no
rows, no pager and no empty state, since the empty hero keys off `upcomingBookings.length` rather than
the schedule bucket. Left alone deliberately — adding copy for it would mean inventing UI that was
never designed or approved. Rare and cosmetic; worth a decision if legacy rows prove common.

## Checks run

| Command | Result |
| --- | --- |
| `npm run test` | **82 passed / 17 files** (81 before, +1 added in review) |
| `npm run build` | **Clean**, built in 3.02s |
| `npx eslint` on the four touched files | **No issues found** |
| `oxlint` on the four touched files | **0 warnings, 0 errors** |
| `npm run lint` (whole repo) | Fails on pre-existing unrelated issues only — see above |

Backend untouched, so `python manage.py test` was not run.

## Commits

- `feat: add tutor dashboard booking split and day-packing helpers`
- `refactor: rebuild tutor dashboard as a paginated schedule with attention rail`
- `docs: close out tutor dashboard simplification`

All local on `feat/subjects-reseed`. Nothing pushed.
