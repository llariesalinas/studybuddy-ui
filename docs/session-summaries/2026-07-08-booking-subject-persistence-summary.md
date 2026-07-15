# Booking subject persistence

**Plan:** [Codex Handoff — Persist the Booked Subject on Booking](../plans/2026-07-08-booking-subject-persistence-codex-handoff.md)
**Status:** Done

## What shipped

- Added nullable `Booking.subject` history using a protected foreign key and migration
  `0071_booking_subject.py`, preserving compatibility with historical bookings.
- Persisted an optional, course-catalog-recognized subject during booking confirmation and sent
  the selected subject from `TutorDetails.vue`.
- Changed session notifications, combined dashboard blocks, pending booking-request blocks, and
  booking-detail payloads to display the booked subject, with `"General"` retained as the null
  fallback.
- Added coverage for subject persistence, omitted and unrecognized subjects, both dashboard
  payload shapes, and booking-detail subject display and fallback behavior.
- Updated `seed_data.py` and `reset_demo_data.py` so demo and development bookings use a subject
  taught by their assigned tutor when one is available.
- Follow-up review extracted the shared unrecognized-subject error message and booking subject
  label into one constant and one helper without changing response or display behavior.

## Verification

- `python manage.py test studybuddy.tests` discovered 293 tests but could not create its test
  database because `test_postgres` already existed; Django then requested interactive deletion,
  which was unavailable in the non-interactive runner.
- `python manage.py test studybuddy.tests --keepdb` was started against the existing test database
  but was stopped at the owner's request before it produced a pass/fail result.
- No passing test count is claimed for this follow-up.

## Deviations from the original plan

- The implementation was already complete across commits `761216b` through `02f2444` before this
  review follow-up; this session only completed the two requested extractions and documentation.
- Verification was not completed because the owner explicitly chose to continue without tests
  after stopping the long-running suite.
