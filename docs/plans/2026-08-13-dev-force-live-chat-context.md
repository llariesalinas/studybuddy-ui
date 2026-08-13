---
title: Chat banner ignores the dev force-live override
date: 2026-08-13
status: Done
summary: Chat recomputes session status from real booking rows instead of the dev-live override, so forcing a session live leaves the chat banner reading "Upcoming"; fixed by extracting the status helpers into a shared module both views and chat import, and pushing a symmetric system pill plus a context broadcast from the dev endpoints.
spec:
---

# Chat banner ignores the dev force-live override

**Status & Progress Summary** (2026-08-13): Done. Ten decisions settled by grilling; the
transcript design was picked from a `ui-preview` comparison, promoted to
[`docs/mockups/2026-08-13-dev-force-live-chat-pills.html`](../mockups/2026-08-13-dev-force-live-chat-pills.html).
Sibling to [`2026-08-13-dev-force-live-midnight-crossing-bug.md`](2026-08-13-dev-force-live-midnight-crossing-bug.md)
(same dev tool, unrelated root cause, already Done). Implemented per plan; two-axis code review
(Standards + Spec, run in parallel) found no hard violations and confirmed the safety-critical
Decision 3 boundary holds; both axes independently flagged the same minor undocumented deviation
(below), both fixed. 462/462 backend tests green, lint/build clean. Not pushed.

## Goal

Forcing a session live leaves the chat banner and its session card reading "Upcoming" with the real
schedule, while every other surface correctly shows the simulated live session. Make chat honor the
dev-live override so an in-session chat UI can actually be tested.

## Approach

Two independent causes, both fixed here.

**Cause 1 — chat duplicates the status logic.** `get_current_booking_context`
(`backend/studybuddy/chat/services.py:208-223`) re-implements the Upcoming / Ongoing /
Payment Required decision inline from `booking.session_date` + `availability.time_slot`. It never
calls `apply_dev_live_override` or `get_display_status` (`backend/studybuddy/views.py:1059-1095`),
so it is structurally blind to the override — a hard page reload does not help, because chat
recomputes from real data every time. `get_current_booking_contexts` (the bulk room-list path,
`services.py:357-378`) carries the same duplicated block.

**Cause 2 — force-live never reaches chat.** `dev_force_booking_live` (`views.py:3649-3655`) sets
the cache and returns the detail payload without notifying the room.
`broadcast_booking_context_updated` (`services.py:680`) already exists and `chat.js:606` already
handles the `booking_context_updated` event — but nothing in the backend emits it today, so that
client handler is currently dead code. The existing dev refresh signal
(`DevSessionQaPanel.vue:142-156` writing `studybuddy_dev_live_refresh` to `localStorage`, consumed
by `App.vue:671-677`) refreshes sessions and active-session state but never chat, and only ever
reaches other tabs in the same browser — not the other participant.

Decisions taken (grilled, in order):

1. **Chat follows the override for status *and* displayed times**, mirroring `build_combined_block`,
   rather than flipping the badge alone. A card reading "Ongoing" beside a start time an hour in the
   future is the confusion this tool exists to avoid.
2. **`time_blocks` collapses too**, to a single block matching the simulated window, so the payload
   is not internally contradictory. Nothing in `src/` renders `time_blocks` today (`grep` returns
   zero hits), but leaving it real would plant a contradiction for the first consumer.
3. **The override applies only on the live banner paths**, not inside `serialize_booking_context`.
   Message metadata is immutable JSON persisted to the database and rendered by `Chat.vue:110`;
   baking a simulated window into it would outlive the 6-hour cache TTL as a permanent artifact of a
   transient dev state. Accepted cost: a booking-event card posted during an active override shows
   the real window while the banner above shows the simulated one.
4. **Shared helpers move to a new neutral module** (`backend/studybuddy/booking_status.py`).
   `views.py:86` imports `chat.services` at module level, so chat cannot import views at module
   level. These helpers take bookings and times and return a string — they have no request-handling
   dependency and do not belong in a 6,000-line views module. `views.py` imports the names back, so
   no other call site changes.
5. **Server push, not client refresh** — the dev endpoints call
   `broadcast_booking_context_updated(room)`. Only this reaches the other participant on another
   device, which is the actual two-sided test scenario.
6. **A visible system pill accompanies the push**, posted via `create_chat_message(...,
   sender=None, message_type='system')` — the centered grey pill at `Chat.vue:119-124` — not
   `create_booking_event`. A booking event would stamp a `serialize_booking_context` snapshot
   carrying the real window (decision 3) directly beneath a banner showing the simulated one, and
   would mint synthetic domain events that analytics and the reports export would have to filter.
7. **Symmetric pills**: clearing posts "Dev: forced live state cleared." as well. Otherwise the
   newest and only marker in the transcript contradicts a silently-reverted banner. Chosen from a
   `ui-preview` side-by-side; accepted cost is transcript noise on a full QA cycle.
8. **Chat replicates the `tutor_confirmed` dev branch** (`views.py:2126-2132`), which forces
   "Payment Required" whenever dev tools are enabled and no override is active. It fires precisely
   when someone clears an override on a tutor-confirmed booking, so skipping it would reintroduce
   drift at the exact moment the "cleared" pill posts. It moves into `booking_status.py` as one
   named helper both callers use, rather than being copy-pasted.

## Steps

1. Create `backend/studybuddy/booking_status.py`; move `DEV_LIVE_PHASES`,
   `DEV_LIVE_CACHE_TIMEOUT_SECONDS`, `get_dev_live_cache_keys_for_booking`,
   `get_dev_live_override_for_bookings`, `set_dev_live_override_for_bookings`,
   `clear_dev_live_override_for_bookings`, `build_dev_live_override`, `apply_dev_live_override`,
   and `get_display_status` out of `views.py`. Add a named helper for the `tutor_confirmed`
   dev branch currently inline at `views.py:2126-2132`.
2. `views.py`: import the names back; update the six call sites; use the new helper in
   `build_combined_block`.
3. `chat/services.py`: replace the inline status block in `get_current_booking_context` and
   `get_current_booking_contexts` with the shared helpers, applying the override to `status`,
   `status_intent`, `date`, `startTime`, `endTime`, and `time_blocks` — on the banner paths only,
   leaving `serialize_booking_context` (and therefore persisted message metadata) untouched.
4. `views.py`: in `dev_force_booking_live` and `dev_clear_booking_live`, post the system pill and
   call `broadcast_booking_context_updated(room)` via `get_canonical_room_for_booking`.
5. Add the single regression test (see Risks) and run the checks below.

## Risks

- **Test coverage is deliberately one test** (user's call). The chosen assertion is decision 3 —
  that persisted `booking_event` metadata still carries the *real* window under an active override —
  because that invariant is enforced by nothing but which function calls the override helper, and a
  future refactor pushing the override down into `serialize_booking_context` would break it
  silently. The `Ongoing` behavior is left to manual verification, since it is what you see the
  first time you use the tool. Uncovered by automated tests: the pill symmetry (decision 7), the
  `time_blocks` collapse (decision 2), and the `tutor_confirmed` branch in chat (decision 8).
- **Same date-collapsing flaw, second instance.** `serialize_time_block`
  (`chat/services.py:111-114`) computes `end_time` as
  `(datetime.combine(session_date, time_slot) + timedelta(...)).time()`, discarding any date
  rollover — the exact pattern fixed in the midnight-crossing plan, whose Risks section flagged that
  the general (non-dev-tool) computation still has it. Known and out of scope here; this plan only
  routes chat through the override, it does not fix real near-midnight bookings.
- **`views.py` churn overlaps today's other work.** The midnight-crossing fix edited the same
  functions earlier today. Step 1 moves them wholesale, so that work should be settled and committed
  first.
- **Deviation from Step 1, found during implementation and confirmed safe:** the moved
  `get_dev_live_override_for_bookings`/`set_...`/`clear_...` no longer re-sort `bookings` via
  `sort_bookings_for_session_group` before iterating, though the pre-move originals did. Not a
  "move" in the strict sense Step 1 describes. Forced by the same import-cycle constraint behind
  decision 4 (`sort_bookings_for_session_group` lives in `views.py`; importing it back into
  `booking_status.py` would reopen the cycle). Safe because every real call site already hands in
  a pre-sorted group, and every booking within one group resolves to the same cache key regardless
  of order, so which one is checked first can't change the result. Flagged independently by both
  the Standards and Spec review passes; documented in-code at each of the three call sites.
- **Backward compatibility is already handled** upstream: `apply_dev_live_override` reads
  `override.get("end_date", override["date"])`, so overrides sitting in the 6-hour cache from before
  today's deploy do not raise.
- Transcript noise: a QA cycle of start -> midpoint -> ending -> clear leaves four pills in the
  room permanently. Accepted.

## Checks to run

- `python manage.py test studybuddy.tests.DevLiveSessionTests` — 6/6 plus the new test
- `python manage.py test studybuddy.tests.ChatFeatureTests` — no new failures beyond the two
  pre-existing ones recorded in the midnight-crossing plan
  (`test_location_update_rejected_inside_grace_cutoff`, wall-clock-dependent; and
  `test_superadmin_counted_verdict_deducts_tutor_wallet`, a stale assertion)
- `npm run lint` and `npm run build` — clean (no frontend changes expected, run as a baseline)
- Manual: force a session live from the QA panel, confirm the chat banner flips to Ongoing on the
  simulated window on *both* sides, and that the pill posts on force and on clear

## Changelog

- 2026-08-13: Plan created from a ten-decision grill. Two root causes traced and confirmed by
  reading the code (chat duplicating the status logic; dev endpoints never broadcasting). Transcript
  design chosen via `ui-preview` — symmetric pills, promoted to
  [`docs/mockups/2026-08-13-dev-force-live-chat-pills.html`](../mockups/2026-08-13-dev-force-live-chat-pills.html).
  No code written.
- 2026-08-13: Implemented all 5 steps. `booking_status.py` created; `views.py` and
  `chat/services.py` both updated to import from it; force/clear endpoints post the symmetric
  pill and broadcast via a new small `announce_dev_live_change` helper (added during code review
  to remove a duplicated 3-line shape between the two endpoints, per the Standards review below).
  Regression test added and verified both ways (fails on the pre-fix behavior via a deliberate
  temporary break, passes on the fix). `DevLiveSessionTests` 7/7, `ChatFeatureTests` 38/38,
  `BookingVerificationGateTests`/`LateCancellationStrikeWindowTests`/
  `LateCancellationSupportTicketTests` 46/46, full backend suite 462/462, lint clean (4
  pre-existing unrelated `no-undef` errors in `make_algo_pptx.*`), build clean. Two-axis code
  review run in parallel subagents: Standards found no hard violations (flagged a missing comment
  on two helper functions, now added, and the duplicated pill/broadcast shape, now extracted);
  Spec found no missing or incorrect requirements and independently confirmed the Decision 3
  persistence boundary holds by tracing every call site; both axes independently flagged the same
  minor undocumented deviation from Step 1 (dropping the internal sort in the moved cache
  helpers), recorded above under Risks. Plan moved Approved -> Done.
