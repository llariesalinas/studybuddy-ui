# Phase A Completion Report — Booking "tutors won't load" Fix

**Date completed:** 2026-06-02
**Branch:** feature-darkmode-toggle
**Plan:** `docs/superpowers/plans/2026-06-02-booking-tutor-load-fix.md`
**Spec:** `docs/superpowers/specs/2026-06-02-booking-tutor-load-fix-design.md`

## Summary

Tutor searches returned an empty results page even when tutors existed. The
recommender requires a candidate tutor to have an active 30-minute availability row
for **every** contiguous slot in the requested range, but the seed data only created
sparse, on-the-hour, 2-hours-apart slots that could never satisfy a multi-slot
search. Fixed by seeding contiguous 30-minute availability blocks, and clarified the
results empty-state copy so failures are understandable.

## Root cause

- `get_recommendation_candidate_tutors` (`backend/studybuddy/views.py:2362-2381`)
  filters `matching_available_slots == len(required_slots)` — all 30-min sub-slots
  must exist and be active.
- Seed `TIME_SLOTS = [08:00, 10:00, 13:00, 15:00, 17:00]` (2 random per day) never
  produced `:30` slots or adjacent slots → every multi-slot search matched zero
  tutors.
- The matching logic is correct (protects booking integrity) and the tutor schedule
  editor already authors contiguous 30-min slots — so this was a **seed-data realism
  bug**, not a logic bug.

## Changes

| File | Change | Commit |
|---|---|---|
| `backend/studybuddy/management/commands/seed_data.py` | Generate contiguous 30-min availability blocks (random 4–6h block starting 08:00–13:00 per assigned day) | `aaf5a7b` |
| `src/views/FindTutors.vue` | Context-aware empty state: distinguishes "no API results (availability/subject)" from "budget filter removed everything" | `7f11b08` |

## Verification

| Check | Result |
|---|---|
| `python manage.py check` | ✅ "System check identified no issues" |
| `python manage.py seed_data` | ✅ Completed: "Seeding complete. Database ready for evaluation." |
| Half-hour slots created | ✅ `TutorAvailability` `08:30` exists; **29 distinct** slot times (was 5); 1316 active rows |
| Recommender — single 30-min slot | ✅ candidate tutors found: 1 (MATH101, future Fri) |
| Recommender — **multi-slot 2h search (09:00–11:00, 4 slots)** — the original failing case | ✅ candidate tutors found: 1 (MATH101, future Wed) — previously always 0 |
| `npm run build` | ✅ Built in 3.95s, no errors |

The bug surface (the recommender returning empty) is verified programmatically.
A live browser click-through of `/book → /find-tutors` was **not** performed in this
session (would require running the Django backend + dev server + a seeded login); the
empty-state copy change is a compiled conditional and the recommender result is proven
at the query layer.

## Notes / follow-ups

- **`faker` was missing from the venv and is not pinned in
  `backend/requirements.txt`.** Installed `faker==40.20.0` into `backend/venv` to run
  the seed. Consider adding it as a dev requirement so seeding works on a fresh clone.
- Re-running `seed_data` is additive/idempotent for availability
  (`get_or_create` on `(tutor, day, time_slot)`) and guarded for bookings
  (existence check on `(availability, session_date)`).

## Deviations from plan

- None functionally. Verification emphasized the recommender query layer (the actual
  bug) rather than a manual UI walkthrough; documented above for transparency.
