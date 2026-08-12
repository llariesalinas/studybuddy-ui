---
title: Chat session card shows tutor's course instead of the booked subject
date: 2026-08-13
status: Done
summary: serialize_booking_context() used the tutor's course/year-level as the session card's "subject" instead of the booking's actual Subjects FK.
spec:
---

# Chat session card shows tutor's course instead of the booked subject

## Status/Progress Summary

Done. `chat/services.py` reads `booking.subject` correctly, `select_related` updated on
all feeding querysets, and two regression tests pass in `ChatFeatureTests`.

## Changelog

- 2026-08-13: Plan written after the user noticed a cancelled-session card in chat
  labelled "Senior High - STEM Track" (a tutor's course/year level) instead of an actual
  tutored subject.
- 2026-08-13: Implemented the fix (subject computation + 6 `select_related` sites), added
  `test_booking_context_subject_is_the_booked_subject_not_the_tutors_course` and
  `test_booking_context_subject_falls_back_to_general_when_unset` to `ChatFeatureTests`.
  Ran `python manage.py test studybuddy.tests.ChatFeatureTests --keepdb`: 38/38 pass.
  Marked Done.

## Goal

Chat session cards (`ChatBanner.vue` / `BookingCard.vue`, fed by
`serialize_booking_context()` in `backend/studybuddy/chat/services.py`) show the tutor's
own **course** (e.g. "Senior High - STEM Track", the field added in the "collect course
and year level during tutor onboarding" work) as the card title, instead of the
**subject** actually being tutored (e.g. "Calculus 1"). Fix the field mix-up.

## Approach

`Booking` has its own `subject` FK to the `Subjects` catalog
(`backend/studybuddy/models.py:823`). `admin_views.py:639` already reads it correctly:

```python
'subject': booking.subject.subject_name if booking.subject else 'General',
```

`chat/services.py:140-144` instead does:

```python
subject = (
    representative.tutor.profile.course.course_name
    if representative.tutor.profile.course
    else 'General'
)
```

— reading the tutor's `course` relation, which has nothing to do with the session's
subject. Swap it to match the `admin_views.py` pattern, reading
`representative.subject.subject_name`.

The querysets that feed `representative` (via `get_booking_group` and
`get_booking_groups_for_contexts`) currently `select_related('availability', 'student',
'tutor__profile__course')` — `subject` isn't in that list, so reading
`representative.subject` would trigger an extra query per card. Add `'subject'` to each of
those `select_related()` calls alongside the existing fields, matching how
`tutor__profile__course` is already prefetched for the (now-removed) course read.

`get_partner_context()` (same file, ~line 486) falls back to
`[current_booking['subject']]` for the partner's "topics" list when the tutor has no
`TutorSubjects` entries — that fallback was silently listing the tutor's course as a topic
too; fixing the field naturally fixes this side effect as well, no separate change needed.

## Steps

1. In `backend/studybuddy/chat/services.py`, change `serialize_booking_context()`'s
   `subject` computation to read `representative.subject.subject_name if
   representative.subject else 'General'`.
2. Add `'subject'` to the `select_related()` calls that produce the `Booking` querysets
   feeding this function: `get_booking_group` (~line 74) and the four/five identical
   `.select_related('availability', 'student', 'tutor__profile__course')` call sites
   (~lines 192, 236, 259, 300, 430).
3. Run the backend test suite (`python manage.py test`), focusing on any chat/booking
   context tests, and add/adjust a test asserting the card shows the booking's actual
   subject rather than the tutor's course.
4. Manually sanity-check in dev: open a chat with an active or recently-terminal booking
   whose `subject` differs from the tutor's `course`, confirm the card now shows the
   subject.

## Risks

- Existing bookings with `subject` left `null` (nullable FK) will correctly fall back to
  `'General'` — same behavior as before for that case, no regression.
- `select_related('subject')` on a nullable FK is safe (Django handles `NULL` FKs fine in
  `select_related`).
- This does not touch `Booking.subject` data itself — if a specific booking's `subject`
  was actually saved with the wrong catalog entry at creation time (a separate, unrelated
  bug), this fix only corrects what the chat card *reads*, not what's stored. Worth a
  follow-up look if mislabeled subjects turn out to exist in the data itself.

## Checks to run

- `python manage.py test` (backend)
- Manual chat card check as described in Step 4.
