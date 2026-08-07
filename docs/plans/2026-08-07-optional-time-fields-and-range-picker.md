---
title: Optional time fields and a single-modal time range picker
date: 2026-08-07
status: In Progress  # Draft | Approved | In Progress | Blocked | Done
spec:                # none yet
---

# Optional time fields and a single-modal time range picker

## Goal

Let a Tutee search for tutors without committing to a start and end time on the Initial Booking
page (`/initial-booking`) and the Find Tutors page (`/find-tutors`), and replace the two-field,
two-modal time UI with one field and one modal that resolves the common cases in a single tap.

## Background — what the current code actually does

**The backend already supports omitted times.** `get_recommendation_time_slots`
(`backend/studybuddy/views.py:3759`) returns `None` when either bound is missing or when
`end <= start`. `get_recommendation_candidate_tutors` then skips Stage 1 (exact date + all slots)
and the slot-level booking/override exclusions, and returns Stage 2 (tutors with *any* active
availability on that weekday, minus full-day overrides) — exactly the right semantics for "any
time that day". `recommend_tutors_view` requires only `subject`; date and times are already
optional parameters. **No backend behavior change is needed.**

**The restriction is entirely client-side, in three places:**

| Location | Current behavior |
| --- | --- |
| [InitialBooking.vue:296](../../src/views/InitialBooking.vue:296) | `if (!startTime \|\| !endTime) return` — a *silent* bail with no toast. Pressing "Find Tutor" without times does nothing at all, with no feedback. This is a live UX bug, not just a restriction. |
| [FindTutors.vue:511](../../src/views/FindTutors.vue:511) | Toasts "Please select a start and end time." and blocks the search. |
| [FindTutors.vue:430](../../src/views/FindTutors.vue:430) | `canRunRecommendation()` requires `date && startTime && endTime`, gating the auto-fetch on mount and on route update. |

**Downstream is unaffected.** `TutorDetails.vue` reads only `subject`, `mode`, and `location` off
the two stores — the actual session times come from the tutor's availability calendar on that
page. The search-time filter never reaches `POST bookings/confirm/`, so relaxing it cannot touch
the Booking Gate or Instant Booking (ADR-0008) paths.

**Both views also auto-invent an end time.** `selectedStartTimeModel` /`startTimeModel` call
`nextTimeSlot(value)` to force `end = start + 1h`, then auto-open the second modal via
`endTimePickerRef`. The user ends up with an end time they never chose.

## Approach

Two coupled changes, in this order: (A) drop the client-side requirement, (B) collapse the two
pickers into one range picker whose empty state *is* the new "any time" case. (B) depends on (A) —
a range picker with no way to express "unset" would just move the problem.

### A. Make the time filter optional

- **Contract:** both bounds set, or neither. A half-set range is meaningless to the backend
  (`get_recommendation_time_slots` discards it anyway) and the new picker only commits a complete
  range, so "exactly one set" can only arrive from stale `sessionStorage`. Treat that case as
  "any time": clear both and proceed, no toast.
- **Do not** make `date` optional. Backend Stage 3 would handle it, but the user asked for the
  time fields; date-optional is a separate decision (it changes what the Find Tutors empty state
  means) and is out of scope here.
- Remaining validations stay, but become conditional on both bounds being present: the
  past-start-time check (`isPastTimeForDate`) and the `end <= start` check.
- Fix the latent gap in `canRunRecommendation()`: it never checks `subject`, but the backend 400s
  without one. New gate is `Boolean(filters.subject && filters.date)`.

**Broader results with no time picked are the point, not a side effect.** Omitting the time filter
moves a search from Stage 1 (exact date + every requested slot) to Stage 2 (any tutor with active
availability that weekday), so the result set gets larger and less precise — which is exactly what
a Tutee who isn't set on a specific time range wants to see. Two consequences to accept
deliberately rather than design around:

- Ranking stays pure Hybrid Score. A time-less search does **not** reward tutors who happen to be
  free at a convenient hour, because there is no requested hour to be convenient relative to.
  Ordering is the same subject/profile fit it always was.
- Stage 2 skips the slot-level booking and slot-override exclusions (they need `required_slots` to
  filter on), keeping only the full-day override exclusion. A tutor with *some* of that day booked
  still surfaces, correctly — their remaining free slots are real, and the Tutee picks from the
  tutor's actual availability calendar on `TutorDetails` anyway.

The results header should therefore say what the search actually covered — "Tutors available on
{date}" when no time is set, versus "Tutors available {date}, {range}" when one is. Without that,
a broad result set reads as a filter that silently failed.

### B. One field, one modal — `BookingTimeRangePicker.vue`

Replaces both `BookingTimePicker` instances. `BookingTimePicker.vue` has no other consumers
(verified) and gets deleted.

**Model shape:** `v-model:start` / `v-model:end`, *not* a single object. This keeps the store
fields (`selectedStartTime`/`selectedEndTime`, `filters.startTime`/`filters.endTime`) and both
persisted `sessionStorage` payloads (`sb-initial-booking`, `sb-find-tutors`) unchanged — no
migration, no shape change rippling into `syncInitialBookingPrefs`.

**Form factor: an anchored dropdown, not a modal.** (Revised 2026-08-07 — the first build used a
Teleported modal with preset chips; replaced on request with a conventional dropdown time picker.)
The trigger opens a panel positioned directly beneath the field, holding two side-by-side
scrolling lists — `Start` and `End` — the familiar Google-Calendar shape. No overlay, no backdrop,
no Teleport.

**What makes it faster than what's there now:**

1. **One trigger, one open.** Today: open modal → pick start → modal auto-closes → second modal
   auto-opens → pick end. Four state changes and two full-screen overlays for one decision. New:
   one dropdown, both columns visible at once, closes when the range is complete.
2. **Start and end are visible together.** The old UI hid the end options behind a second modal
   that only appeared after the start was chosen, so the two halves of one decision were never
   on screen at the same time.
3. **No AM/PM tab.** The old segmented control hid half the day; picking 1 PM after a 9 AM start
   cost a tab switch. Both columns are now plain scrolling lists of all 24 hours. No hour is ever
   hidden — tutors can and do publish any of the 24 slots (`TutorSchedule.vue:364` generates the
   full range), so a 6 AM–10 PM hard window would silently drop real availability.
4. **Duration hints on the end column** (`10:00 AM   1 hr`, `12:00 PM   3 hrs`), computed against
   the chosen start. Answers "how long is this?" without arithmetic.
5. **Explicit end time.** Drop the `nextTimeSlot` auto-fill and the `endTimePickerRef` auto-open
   cascade from both views. Nothing is committed until the user picks an end.
6. **An `Any time` action in the footer**, alongside a hint line that tracks the pending state
   (`Pick a start time` → `From 9:00 AM — pick an end time`). `Any time` is load-bearing: it's how
   a user gets back to the unset state.

Closing without a complete range (outside click, Escape, re-clicking the trigger) discards the
pending start and commits nothing — preserving the both-or-neither contract from section A.

**Keep the `.time-trigger` class name** — the *name*, not the rules inside it (see B2 for the
restyle) — because `InitialBooking.vue`'s `:deep(.time-trigger…)` focus overrides key off it.
The dropdown form factor drops `.time-modal` entirely, which also retires its
`[data-sb-density='compact']` entry in `src/assets/main.css:113`: a `px`-bounded dropdown has no
`vh` to correct, so the whole `--sb-vh-fix` concern disappears rather than needing to be handled.

**Disabled states** carry over from `BookingTimePicker`: hours already past when
`selectedDate === today`; hours at or before the pending start while choosing the end.

**Accessibility:** `role="dialog"` + `aria-modal`, Esc to close, `aria-pressed` on chips, and
roving arrow-key focus across the chip list — matching the precedent set by `SubjectPickerModal`.

### B2. Visual spec — which "house style" the picker follows

There are **two modal generations coexisting on these two screens**, and picking the wrong one is
how the new field ends up looking out of place. The Find Tutors filter bar alone renders both:

| Component | Generation | Dialog surface | Backdrop | Radius | Title | Icon button |
| --- | --- | --- | --- | --- | --- | --- |
| `SubjectPickerModal`, `SbSelectModal` | **Current** | `color-mix(in srgb, var(--sb-card-bg) 94%, transparent)` | `rgba(7, 19, 16, 0.48)` | `20px` | `850` | `999px` circle |
| `BookingDatePicker`, `BookingTimePicker` | Older | hardcoded `#ffffff` | `rgba(15, 23, 42, 0.44)` | `18px` | `800` | `10px` rounded square + uppercase "kicker" |

**Build the new picker in the current generation.** Since the form factor is a dropdown rather
than a dialog, the closest neighbour to match is `FindTutors.vue`'s own `.budget-dropdown-panel` —
the other anchored dropdown on the same filter bar — with `SubjectPickerModal`'s option rows for
the lists inside. Concretely:

- Trigger: `min-height: 42px` and `border-radius: 0.375rem` to sit flush with the adjacent
  `.date-trigger`, `1px solid var(--sb-card-border)`,
  `background: color-mix(in srgb, var(--sb-card-bg) 86%, transparent)`, `color: var(--sb-text-main)`,
  placeholder in `var(--sb-text-muted)`, chevron in `var(--sb-primary)`. Hover/focus:
  `border-color: var(--sb-primary)` + `box-shadow: 0 0 0 4px color-mix(in srgb, var(--sb-primary) 12%, transparent)`.
- Panel: `position: absolute; top: calc(100% + 0.5rem)`, `width: min(340px, 92vw)`,
  `border-radius: 18px`, `background: var(--sb-card-bg)`, `border: 1px solid var(--sb-card-border)`,
  `box-shadow: 0 20px 44px rgba(10, 122, 81, 0.12)`, `z-index: 25` — the same shadow, z-index and
  `@media (max-width: 991px)` static-collapse `.budget-dropdown-panel` already uses, so the two
  dropdowns on that filter bar behave identically.
- Option rows: `border-radius: 9px`, transparent by default, `var(--sb-primary-light)` on hover —
  matching `SubjectPickerModal`'s list rows. Selected row fills `var(--sb-primary)` with
  `var(--sb-primary-contrast)` text. Reuse `.sb-btn` so press/timing
  (`--sb-t-normal`, `--sb-spring`, `--sb-press`) match every other control.
- No uppercase "kicker" line. The current generation dropped it; keeping it would date the new
  component on arrival.

**Why not just copy `BookingTimePicker`'s styles:** they hardcode `#ffffff` surfaces and
`rgba(0, 137, 90, …)` accents, which means both Booking pickers **are already broken in dark
mode** — the theme is real and user-toggleable (`SbThemeToggle.vue`, `src/stores/theme.js` sets
`data-sb-theme` on `documentElement`, and `main.css:160` redefines the full token set). A cloned
picker would render as a white card with dark-on-dark text the moment a Tutee flips the toggle.

### B3. Tokenize `BookingDatePicker.vue` in the same pass

This is the part that actually delivers "doesn't look out of place," and it is a scope addition —
call it out at review time rather than letting it pass silently.

`BookingDatePicker` sits in the **same form row** as the new time field on both screens. If the
time picker is tokenized and the date picker is not, the two adjacent controls visibly diverge in
dark mode (one themed, one glaring white) — trading the old inconsistency for a worse, more
obvious one. Swap its ~12 color literals for the equivalent tokens: `#ffffff` → `var(--sb-card-bg)`
(surfaces) and `var(--sb-primary-contrast)` (selected-cell text), `rgba(0, 137, 90, …)` →
`color-mix(… var(--sb-primary) …)`, `rgba(15, 23, 42, …)` → the shared backdrop/shadow values
above. Purely mechanical, no structural change, no behavior change.

Bringing `BookingDatePicker`'s *structure* fully in line with the current generation (radius,
title weight, dropping its kicker) is optional and cosmetic — do it only if it looks off once the
two sit side by side. The dark-mode tokenization is not optional.

### C. Extract the duplicated time helpers

`padNumber`, `todayKey`, `timeToMinutes`, `currentComparableMinutes`, `isPastTimeForDate`,
`isPastDate`, and `nextTimeSlot` are copy-pasted between `InitialBooking.vue` (lines 153–191),
`FindTutors.vue` (lines 230–272), and `BookingTimePicker.vue` (lines 118–135). The new component
needs them too, so extract to `src/utils/time.js` and import in all three places. Period
boundaries and preset ranges go in `src/config.js` per CLAUDE.md's "add new tunables here" rule.

## Steps

1. Add `src/utils/time.js` with the shared helpers and `src/utils/time.test.js` covering them
   (TDD — write the tests first; the helpers are pure and cheap to pin down).
2. ~~Add period/preset constants to `src/config.js`.~~ Dropped with the preset chips in the
   dropdown redesign — the two columns need no configuration.
3. Build `src/components/BookingTimeRangePicker.vue` per sections B and B2 (current-generation
   tokens, no hardcoded colors, no kicker line), with
   `src/components/BookingTimeRangePicker.test.js`: end options disabled until a start is chosen;
   only later hours enabled as ends; duration hints; `Any time` emits `null`/`null`; past hours
   disabled when the date is today; outside-click and Escape discard a half-finished range; both
   models always emit together.
4. Swap it into `InitialBooking.vue`: replace the two-`col-6` row (lines 61–86) with one full-width
   field labelled `Time (optional)`; delete `endTimePickerRef`, `nextTimeSlot`, the auto-open
   `nextTick`, and the local helpers; make the time validations in `findTutor` conditional and
   remove the silent `return` at line 296.
5. Swap it into `FindTutors.vue`: replace the two `col-lg-3` time columns (lines 79–104) with one;
   same deletions; drop the "Please select a start and end time." toast; relax
   `canRunRecommendation()` to `subject && date`.
6. Delete `src/components/BookingTimePicker.vue`.
6a. Tokenize `BookingDatePicker.vue` per section B3 so the adjacent field in the same row matches
    in both themes. Scope addition — flag it in the PR description.
7. Update copy in `FindTutors.vue`: trigger placeholder `Any time`, labels `Time (optional)`, a
   results header that names the date and the range only when one is set (per section A), and an
   `emptyStateMessage` that suggests clearing the time filter when one is set.
8. Add a backend regression test in `RecommendTutorsViewTests`
   (`backend/studybuddy/tests.py:656`) — the `recommend()` helper at line 742 always sends times,
   so the date-without-time path is currently untested. Assert that
   `recommend(start_time=None, end_time=None)` returns the Stage 2 (date-only) candidate set. This
   locks the contract the frontend now depends on.
9. Manual pass on the dev server: both pages, with and without times, Online and Face-to-face,
   plus a reload mid-flow to confirm the `sessionStorage` round-trip. **Run the whole pass twice —
   once light, once with the theme toggle flipped to dark** — and check the new picker against its
   row neighbours (`BookingDatePicker`, `SubjectPickerModal`, `SbSelectModal`) side by side at
   both `md` and `lg` widths, and at Tutee density (`data-sb-density='compact'`).

## Risks

- **Stale `sessionStorage`.** Existing `sb-initial-booking` / `sb-find-tutors` payloads may hold a
  half-set or now-past range. The "clear both, proceed as any time" rule in section A covers it;
  make sure the picker renders a half-set model as empty rather than crashing.
- **Density (`--sb-vh-fix`).** Moot after the dropdown redesign — the panel is bounded in `px`,
  so there is no `vh` needing the `[data-sb-density='compact']` correction. The now-unused
  `.time-modal` entry in `main.css` was removed rather than left dangling.
- **Dropdown clipping.** An absolutely positioned panel can overflow the viewport at the right
  edge of the `FindTutors` filter bar. `.budget-dropdown-panel` has the same exposure and the same
  `991px` static-collapse fallback, so behaviour is at least consistent — worth an eye during the
  manual pass at `lg`.
- **Dark mode is the easiest thing to miss here.** Neither existing Booking picker is themed, so
  there is no correct local example to copy from and the bug doesn't show up in a light-mode
  screenshot or in jsdom tests. The B2 token rules and the two-theme manual pass in step 9 are the
  only things catching it.
- **Layout reflow.** `FindTutors.vue`'s filter bar is a hand-tuned Bootstrap grid; going from two
  `col-lg-3` columns to one changes the wrap points. Check `md` and `lg` breakpoints, and the
  interaction with the absolutely-positioned `.budget-dropdown-panel`.
- **Auto-fetch on mount widens.** With `canRunRecommendation()` relaxed, arriving at
  `/find-tutors` with only a subject and date now fires a request that previously didn't. Intended,
  but it is a new request on a path that used to be silent.

## Checks to run

- `npm run test` — all Vitest suites green, including the two new files.
- `npm run lint` — oxlint + ESLint clean.
- `npm run build` — production build succeeds.
- `python manage.py test studybuddy.tests.RecommendTutorsViewTests` (from `backend/`) — the class
  passes including the new date-without-time cases. **Blocked, not yet run** — see below.
- Manual: step 9 above.

## Run log (2026-08-07)

**Redesign mid-implementation.** The first build shipped a Teleported modal with preset chips and
a single 24-hour chip column under sticky period headers. Replaced on request with the anchored
two-column dropdown described in B/B2 — closer to a conventional time picker and to
`.budget-dropdown-panel`, the neighbouring control on the same filter bar. Removed as part of the
swap: `DAY_PERIODS`/`TIME_RANGE_PRESETS` from `src/config.js`, the `.time-modal` density entry in
`main.css`, and two helpers in `src/utils/time.js` (`minutesToTime`, `getTimePeriod`) the dropdown
no longer needs. The store contract, both views, and section A's optional-time behavior were
unaffected — only the component and its tests changed.

Frontend, all green: `npm run test` 126 passed / 19 files (43 new), `npm run build` clean,
`npm run lint:eslint` clean. `npm run lint` as a whole still exits 1 on a **pre-existing**
`no-unused-vars` for `draftSubjectCodes` in `src/composables/useSubjectCatalog.js:8` — confirmed
present on `HEAD` before any of this work, in a file this plan never touches. Left alone as
out-of-scope; it does block the combined `lint` script from passing.

Backend tests **not run — blocked on database access.** `backend/.env` points `DB_HOST` at the
hosted Supabase pooler (`aws-1-ap-southeast-1.pooler.supabase.com`), and Django's test runner
wants to create and drop a `test_postgres` database there. Running that against a shared hosted
instance was not something to do unattended, so it was not attempted. The documented workaround
from the 2026-07-07 session (local PostgreSQL, credentials passed inline per-command, `.env` never
modified) also failed: a local server is listening on `localhost:5432` but rejected both
`postgres/postgres` and CI's `studybuddy/studybuddy` with `password authentication failed`.

`studybuddy/tests.py` compiles and `manage.py check` reports no issues, so the three new tests are
at least syntactically valid and the app config is sound — but they are unverified. Getting the
local Postgres password (or running the class elsewhere) is the one outstanding item before this
plan can move to Done.

## Out of scope

- Making the **date** field optional (backend Stage 3 supports it; it is a separate product call).
- Ranking or surfacing per-tutor matching slots on the Find Tutors result cards.
- Moving `BOOKING_HORIZON_DAYS` out of `BookingDatePicker.vue` into `src/config.js` — adjacent
  cleanup, not required here.
