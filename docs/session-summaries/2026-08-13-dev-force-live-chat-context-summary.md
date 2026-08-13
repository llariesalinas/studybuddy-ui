---
title: Chat banner ignores the dev force-live override
date: 2026-08-13
plan: ../plans/2026-08-13-dev-force-live-chat-context.md
---

# Dev force-live chat context — summary

## What was reported

Forcing a session live via the dev QA panel left the chat banner and its session card
reading "Upcoming" with the real schedule, while the sessions screens correctly showed
the simulated live session.

## Diagnosis

Two independent causes:

1. `get_current_booking_context` / `get_current_booking_contexts` in
   `backend/studybuddy/chat/services.py` re-implemented the Upcoming/Ongoing/Payment
   Required decision inline from real booking rows and never called
   `apply_dev_live_override` — chat was structurally blind to the override.
2. `dev_force_booking_live` / `dev_clear_booking_live` in `backend/studybuddy/views.py`
   never notified the chat room. `broadcast_booking_context_updated` already existed and
   the client already handled the `booking_context_updated` event
   (`src/stores/chat.js:606`), but nothing on the backend emitted it.

## What shipped

- `backend/studybuddy/booking_status.py` (new): the dev-live override machinery
  (`DEV_LIVE_PHASES`, the cache helpers, `build_dev_live_override`,
  `apply_dev_live_override`, `get_display_status`) moved out of `views.py`, plus a new
  named helper `apply_dev_confirmed_gate` that replaces two identical inline
  `tutor_confirmed`-forces-"Payment Required" blocks that were already duplicated inside
  `views.py` itself. Extracted rather than left in `views.py` because `views.py` imports
  `chat.services` at module level, so `chat.services` can't import `views.py` back.
- `backend/studybuddy/views.py`: imports the moved names back; all six call sites
  unchanged in behavior; both duplicated `tutor_confirmed` gates now call
  `apply_dev_confirmed_gate`; `dev_force_booking_live` / `dev_clear_booking_live` each
  call a new `announce_dev_live_change(booking, message)` helper that posts a system chat
  message (`sender=None`, `message_type='system'`) and calls
  `broadcast_booking_context_updated`.
- `backend/studybuddy/chat/services.py`: new `apply_confirmed_status_and_dev_override`
  helper, called from both status paths for a Confirmed booking. Rewrites `status`,
  `status_intent`, and — only while an override is active — `date`/`startTime`/
  `endTime`/`time_blocks`/`hasMultipleTimeBlocks` to match the simulated window.
  `serialize_booking_context` itself is untouched, so the snapshot `create_booking_event`
  stamps into persisted chat message metadata always keeps the real window, even during
  an active override.
- `backend/studybuddy/tests.py`: one new regression test,
  `test_location_update_snapshot_keeps_real_window_during_override`, covering the
  persisted-metadata invariant above (chosen as the single test to write, per the user's
  call during grilling, since it's the one invariant nothing else enforces structurally).
  Verified against both pre-fix and post-fix code by temporarily reintroducing the bug,
  confirming the test fails, then reverting.

Ten decisions behind this were settled via `/grilling` before any code was written; full
rationale is in the plan. UI design for the chat transcript (symmetric system pills vs.
other options) was chosen via a `ui-preview` side-by-side, saved to
[`docs/mockups/2026-08-13-dev-force-live-chat-pills.html`](../mockups/2026-08-13-dev-force-live-chat-pills.html).

## Deviations from the plan

- The moved `get_dev_live_override_for_bookings` / `set_dev_live_override_for_bookings` /
  `clear_dev_live_override_for_bookings` no longer re-sort `bookings` via
  `sort_bookings_for_session_group` before iterating, though the pre-move originals did.
  Forced by the same import-cycle constraint driving the module split
  (`sort_bookings_for_session_group` lives in `views.py`). Safe because every real call
  site already hands in a pre-sorted group and every booking in one group resolves to the
  same cache key regardless of order. Flagged independently by both the Standards and
  Spec review passes; now documented in-code at each of the three call sites and recorded
  in the plan's Risks section.
- During code review, extracted `announce_dev_live_change` to remove a duplicated 3-line
  "get room, post pill, broadcast" shape that had been written identically into both
  `dev_force_booking_live` and `dev_clear_booking_live`. Not in the original plan text,
  added as a direct result of the Standards review.

## Code review

Two-axis review (Standards + Spec) run as parallel subagents against
`docs/plans/2026-08-13-dev-force-live-chat-context.md`. Standards: no hard violations,
two minor judgment-call findings (both fixed — see Deviations above, plus a missing
comment on two of the three cache helpers explaining the dropped sort, now added).
Spec: no missing or incorrect requirements; independently traced the safety-critical
Decision 3 boundary (override never applied inside `serialize_booking_context`) call site
by call site and confirmed it holds, and confirmed the two system pills are symmetric and
match the plan's wording exactly.

## Checks run

- `python manage.py test studybuddy.tests.DevLiveSessionTests --keepdb` — 7/7 (includes
  the new test)
- `python manage.py test studybuddy.tests.ChatFeatureTests --keepdb` — 38/38
- `python manage.py test studybuddy.tests.BookingVerificationGateTests
  studybuddy.tests.LateCancellationStrikeWindowTests
  studybuddy.tests.LateCancellationSupportTicketTests --keepdb` — 46/46
- `python manage.py test --keepdb` (full backend suite) — 462/462
- `npm run lint` — clean except the 4 pre-existing `no-undef` errors in
  `make_algo_pptx.*` (unrelated, no frontend files touched this session)
- `npm run build` — clean

## Not pushed

Local commit only, pending review — no push without confirmation, per project rules.
