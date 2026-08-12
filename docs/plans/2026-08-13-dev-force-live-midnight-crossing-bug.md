---
title: Dev force-live tool returns "Payment Required" instead of "Ongoing" near midnight
date: 2026-08-13
status: Done
summary: Fixed DevLiveSessionTests flakiness (previously misdiagnosed as intermittent) — the dev "force live" booking tool silently failed near local midnight because the override stored one shared date for both the start and end of the simulated session window.
---

# Dev force-live tool returns "Payment Required" instead of "Ongoing" near midnight

**Status & Progress Summary** (2026-08-13): Done. Root cause found, fixed, and verified against the
live bug (reproduced at the actual failure time, 00:4x Asia/Manila). Added a deterministic
regression test (frozen clock) so it can't silently regress into being wall-clock-dependent again.
Confirmed the fix against the old code (test fails without it, passes with it). `DevLiveSessionTests`
6/6, plus `BookingVerificationGateTests`, `LateCancellationStrikeWindowTests`,
`LateCancellationSupportTicketTests`, `ChatFeatureTests` all pass except two pre-existing,
unrelated failures (see Risks).

## Goal

The dev tool that force-simulates a live tutoring session (used to test in-session UI without
waiting for a real scheduled slot) was intermittently returning `"Payment Required"` instead of
`"Ongoing"` after forcing a session live. Previously tracked in `docs/plans/README.md`'s history as
unexplained flakiness in `DevLiveSessionTests` (417→453 tests, 4 failures, "root cause not found,
left for a dedicated diagnosing-bugs session").

## Approach

**Root cause: `build_dev_live_override()` only stored one shared date.** The dev-live override
simulates a session window as `current_time + phase_offset_minutes` for both a start and end
moment. Some phases' offset windows cross local midnight — `'ending'` is `(-55, +5)` minutes, which
crosses backward whenever the real clock is within 55 minutes past midnight (exactly the situation
when this was diagnosed: 00:4x Asia/Manila). `build_dev_live_override` computed `start_at`/`end_at`
as full datetimes correctly, but the cache payload only kept `start_at.date()` as a single `"date"`
field, using it for *both* `start_time` and `end_time` when reconstructed. When the two moments
land on different calendar dates, recombining the later `end_time` with the earlier `date` produces
an `end_at` *before* `start_at` — an impossible, empty "Ongoing" window — so
`get_display_status()` fell through to its `else: return 'Payment Required'` branch.

This is why it looked like flakiness rather than a deterministic bug: it's 100% deterministic
*given the wall-clock time*, but which of the 5 phases (`upcoming`/`start`/`midpoint`/`ending`/
`handoff`, offsets ranging up to ±72 minutes) happens to straddle midnight varies with what time of
day the test suite runs — so different test runs at different times of day saw different subsets
of `DevLiveSessionTests` fail, with no code change in between.

**Fix: carry both dates through the whole chain.** `build_dev_live_override` now stores `end_date`
alongside `date` (kept as the start date). `apply_dev_live_override` returns a 4-tuple
(`start_date, start_time, end_date, end_time`) instead of 3; the no-override fallback path returns
`session_date` for both. `get_display_status` takes `start_date`/`end_date` separately and combines
each with its own time to build `start_at`/`end_at`. All four call sites
(`get_current_display_status_for_booking`, `build_combined_block`, `build_booking_detail_payload`,
`cancel_booking`) updated to match — the last of these was missed on the first pass and only caught
by re-running the full suite (see Risks).

**Backward compatibility for in-flight cache entries:** `apply_dev_live_override` reads
`override.get("end_date", override["date"])` rather than a bare `override["end_date"]`, so any
override already sitting in the cache (6-hour TTL) from before this fix deploys doesn't raise a
`KeyError` — it just falls back to the old (potentially still-buggy-if-crossing-midnight) behavior
until it expires or is re-forced.

**Regression test freezes the clock.** `test_force_live_ongoing_survives_a_midnight_crossing`
patches `django.utils.timezone.now` to 00:30 and forces `phase='ending'` (guaranteed to cross
midnight backward at that moment), so the bug can't silently reappear depending on what time
someone happens to run the suite. Verified this test fails on the pre-fix code and passes on the
fix (stashed `views.py`, ran the new test alone, confirmed the same `'Payment Required' !=
'Ongoing'` failure; restored and re-confirmed green).

## Steps

1. `backend/studybuddy/views.py`: `build_dev_live_override`, `apply_dev_live_override`,
   `get_display_status` — carry both dates through.
2. Update all 4 call sites to the new 4-arg `apply_dev_live_override` return / 5-arg
   `get_display_status` signature.
3. `backend/studybuddy/tests.py`: add `test_force_live_ongoing_survives_a_midnight_crossing`
   (frozen clock, deterministic).
4. Verify: `DevLiveSessionTests` (6/6), broader booking/cancellation/support-ticket test classes
   for regressions from the signature change, and the new test against pre-fix code.

## Risks

- Two failures remain in the full suite, both confirmed pre-existing and unrelated to this fix:
  - `ChatFeatureTests.test_location_update_rejected_inside_grace_cutoff` — a separate,
    wall-clock-dependent test bug (assumes "now" is past 02:00 AM on the session day; fails in the
    same near-midnight window this session's work happened in). Uses
    `Booking.tutor_can_edit_location()`, not any function touched by this fix.
  - `LateCancellationSupportTicketTests.test_superadmin_counted_verdict_deducts_tutor_wallet` —
    asserts `response.data["monthly_counted_strikes"]`, a field that doesn't exist anywhere in the
    codebase (`grep` confirms zero matches) — an incomplete/stale assertion predating this session,
    unrelated to booking status.
  - Neither was fixed here; flagged for a separate pass.
- The general (non-dev-tool) session end-time computation shared by these same call sites
  (`datetime.combine(first_booking.session_date, last_booking.availability.time_slot) +
  timedelta(minutes=SESSION_SLOT_MINUTES)).time()`) has the *same* class of bug for a real booking
  whose slot + duration crosses midnight — it also only keeps `.time()`, discarding any date
  rollover. Out of scope here (this fix only addresses the dev-live override path, which is what
  was actually reported broken and tested), but worth a dedicated look if real near-midnight
  bookings are ever reported showing the wrong status.

## Checks to run

- `python manage.py test studybuddy.tests.DevLiveSessionTests` — 6/6
- `python manage.py test studybuddy.tests.BookingVerificationGateTests
  studybuddy.tests.LateCancellationStrikeWindowTests
  studybuddy.tests.LateCancellationSupportTicketTests studybuddy.tests.ChatFeatureTests` — all pass
  except the two pre-existing, unrelated failures noted above

## Changelog

- 2026-08-13: Root cause found (reproduced live, confirmed via direct trace and by checking server
  wall-clock time matched the failure window), fixed across all 4 call sites (one missed on first
  pass, caught by the full suite and fixed), regression test added and verified against both pre-
  and post-fix code.
