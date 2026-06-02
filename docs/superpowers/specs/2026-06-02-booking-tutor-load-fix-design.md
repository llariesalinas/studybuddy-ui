# Phase A — Booking "tutors won't load" Fix — Design Spec

**Date:** 2026-06-02
**Status:** Approved for planning
**Stack:** Vue 3 (Composition API), Pinia, Django REST

---

## Problem

When a tutee runs a search in the booking flow, the results page shows the empty
state ("No tutors match this budget range") even when tutors exist. No error is
thrown — the API returns an empty list.

## Root cause (confirmed)

The recommender requires a candidate tutor to have an **active 30-minute
availability row for _every_ contiguous slot** in the requested time range:

`backend/studybuddy/views.py:2362-2381`
```python
required_slots = get_recommendation_time_slots(start_time, end_time)  # every 30 min
...
.annotate(matching_available_slots=Count("tutoravailability__time_slot", filter=...))
.filter(matching_available_slots=len(required_slots))   # ALL slots must exist
```

`SESSION_SLOT_MINUTES = 30`, so a search for 08:00–09:00 needs rows at **08:00
AND 08:30**.

But the seed data creates only sparse, on-the-hour, 2-hours-apart slots:

`backend/studybuddy/management/commands/seed_data.py:245-258`
```python
TIME_SLOTS = [08:00, 10:00, 13:00, 15:00, 17:00]   # 2 random ones per day
```

There is never a `:30` slot and never two adjacent slots, so **no tutor can
satisfy any multi-slot request → every search returns empty.**

The matching logic is **correct** (it protects booking integrity — you should not
be matched with a tutor who is not free for the whole session). The tutor schedule
editor already produces contiguous 30-minute slots
(`src/views/TutorSchedule.vue:344`, `:707`), so real tutor data works. **This is a
seed-data realism bug, not a logic bug.**

A secondary UX bug: the empty state always blames the budget, hiding the real
cause (no availability / wrong subject).

## Decision

- **Do NOT loosen the matching logic.** Fix the data instead.
- Make the seed generate **realistic contiguous 30-minute availability blocks**.
- Make the results empty state **context-aware** so failures are understandable.

## Scope

### In scope
1. `backend/studybuddy/management/commands/seed_data.py` — generate contiguous
   30-minute availability blocks per assigned day.
2. `src/views/FindTutors.vue` — empty-state message reflects the real reason
   (no backend matches vs. client-side budget filter removed everything).

### Out of scope
- The recommender matching algorithm itself (intentionally unchanged).
- Real-tutor availability authoring (already correct).
- Any model/migration change (none needed).

## Data model

No changes. No migration.

## Behaviour after fix

- A normal booking search against freshly seeded data returns tutor cards.
- When zero tutors come back from the API, the empty state says availability/subject
  is the issue and suggests changing date/time/subject.
- When the API returns tutors but the client budget slider filters them all out, the
  empty state suggests widening the budget.

## Success criteria

1. Run `python manage.py seed_data`, log in as a seeded tutee, search for a seeded
   subject on a future date within 08:00–18:00 → at least one tutor card renders.
2. Searching a subject/time with genuinely no availability → empty state explains
   availability, not budget.
3. `npm run build` succeeds; Django `manage.py check` passes.
