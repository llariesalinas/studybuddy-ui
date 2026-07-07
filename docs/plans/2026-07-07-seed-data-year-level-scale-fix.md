---
title: Seed data year_level scale fix (seed_data.py)
date: 2026-07-07
status: Done
spec:
---

# Seed data year_level scale fix (seed_data.py)

<!-- LIVING SUMMARY: keep this section and the Changelog current on every edit -->
## Status & Progress Summary

**Status: Done - implemented, audited, and verified. Two audit findings were fixed: a bare
`- 12` offset in `reset_demo_data.py` now sources from a named `COLLEGE_YEAR_OFFSET` constant,
and the claimed "35 failures + 6 errors" test-suite baseline was independently re-run and
confirmed (270 tests, 34 failures, 5 errors) — and confirmed structurally unrelated to this
change, since `tests.py` never imports `reset_demo_data.py`/`seed_data.py`/`_year_level_scale.py`.
The documented "14 failures + 2 errors" baseline elsewhere in this repo is now stale (predates
unrelated work merged since 2026-07-05), not something this fix broke.**

Follow-up to the `year_level` encoding fix already shipped on this branch (`reset_demo_data.py`
and `PreferenceSetup.vue`, see [2026-07-07-onboarding-guided-rail-redesign.md](2026-07-07-onboarding-guided-rail-redesign.md)).
A code review of that fix flagged that the "college years are 13-16" convention was now
duplicated across three call sites with no shared constant. This plan fixes the fourth,
previously-missed offender (`seed_data.py`, the generic `python manage.py seed_data` command)
and extracts a shared constant so the convention lives in exactly one place.

## Goal

Make `seed_data.py` assign `year_level` consistently with the app's unified scale (1-6
elementary, 7-10 JHS, 11-12 SHS, 13-16 college) and derived from the profile's actual `course`,
instead of an independent flat `[1,2,3,4]` pool applied regardless of course. Remove the
duplicated `YEAR_RANGE_BY_COURSE`-style convention by sharing one definition between
`seed_data.py` and `reset_demo_data.py`.

## Approach

Today, `seed_data.py` (lines 172-173, 202-203) does:

```python
'course': fake.random_element(courses),        # any of the 9 course codes
'year_level': fake.random_element([1, 2, 3, 4]),  # independent of course
```

This means a Junior High profile can get `year_level=2` (reads as "Elementary" on the profile
page), and a BSCS/BSIT/BSBA profile gets the same raw-1-4-instead-of-13-16 bug `reset_demo_data.py`
had before today's fix.

Rather than patch `seed_data.py` with its own copy of the range map (a third copy of the same
convention, which is exactly what the review comment warned against), extract a shared module:

- New file `backend/studybuddy/management/commands/_year_level_scale.py`:
  - `YEAR_RANGE_BY_COURSE` — the same 9-entry map currently defined in `reset_demo_data.py`
    (`ELEMENTARY: (1,6)`, `JUNIOR_HIGH: (7,10)`, four `SHS-*: (11,12)`, three college codes
    `(13,16)`).
  - `random_year_level(course_code)` — `random.randint(*YEAR_RANGE_BY_COURSE[course_code])`,
    used by both commands instead of ad hoc `random.randint(...)` calls.
- `reset_demo_data.py`: import `YEAR_RANGE_BY_COURSE` from the new module instead of defining it
  locally; `_course_year()` and the line-973 pending-applicant seeding both route through
  `random_year_level()`. No behavior change — same ranges, same course codes.
- `seed_data.py`: pick the course first, then derive `year_level` from it via
  `random_year_level(course.course_code)`, for both the Tutee and Tutor profile-creation loops.

This module is deliberately just a shared data constant + one helper — not a class, not a config
system. It's `management/commands/`-local since only these two commands need it.

Explicitly out of scope: `seed_data.py`'s `TutorSubjects`/`Preference` assignment already picks
subjects randomly across *all* seeded subjects regardless of course or year (no `_subjects_for`-
style filtering exists here). That's a separate, pre-existing realism gap, not an encoding bug —
not touched by this plan.

## Steps

1. Create `backend/studybuddy/management/commands/_year_level_scale.py` with `YEAR_RANGE_BY_COURSE`
   and `random_year_level(course_code)`.
2. Update `reset_demo_data.py`: replace its local `YEAR_RANGE_BY_COURSE` definition with an import
   from the new module; route `_course_year()` and the line-973 `random.randint(13, 16)` through
   `random_year_level()`. Verify the persona dict literals (`'year': 14`, etc.) are unaffected —
   they're already correct absolute values, not derived from this map.
3. Update `seed_data.py`: for both the Tutee loop (~line 166-179) and Tutor loop (~line 196-209),
   pick `course = fake.random_element(courses)` first, then set
   `'year_level': random_year_level(course.course_code)`.
4. Run `python manage.py seed_data` against a scratch/dev DB and spot-check a handful of seeded
   profiles' `(course, year_level)` pairs land in the expected range for their course.
5. Run `python manage.py test` to confirm no regressions (this command isn't exercised by the
   test suite directly, but the shared module must not break `reset_demo_data.py`'s existing
   behavior, which some tests may depend on transitively).

## Risks

- `reset_demo_data.py`'s persona dicts use hardcoded years (e.g. `'year': 14`) that must stay
  within `YEAR_RANGE_BY_COURSE[course]` for the recommender's `int(student_year) > 12` check to
  keep working — the shared module doesn't change these, just verify they still make sense after
  the refactor (they will, since the range itself is unchanged).
- `seed_data.py` has no automated test coverage today; verification is manual (run the command,
  inspect output). Low risk since the change is isolated to two `UserProfile.objects.get_or_create`
  call sites.
- If any other file imports `YEAR_RANGE_BY_COURSE` directly from `reset_demo_data.py` (rather than
  going through the shared module), moving it would break that import — grep before deleting the
  local definition.

## Checks to run

- `grep -rn "YEAR_RANGE_BY_COURSE" backend/` before and after, to confirm no stray importers are
  missed.
- `python manage.py seed_data` on a scratch DB — no errors, and printed profiles show
  course-appropriate `year_level` (spot check via Django shell:
  `UserProfile.objects.values_list('course__course_code', 'year_level')`).
- `python manage.py test` — matches the documented pre-existing baseline (no new failures).

## Changelog

- 2026-07-07: Plan written and approved, following a code-review comment on the
  `reset_demo_data.py`/`PreferenceSetup.vue` year_level fix that flagged the same "college = +12
  offset" convention being duplicated across three call sites. Scoped to fixing `seed_data.py`
  (the fourth, previously-missed offender) while extracting a shared constant to prevent further
  drift. Implementation not yet started.
- 2026-07-07: Implemented as planned. Added shared helper module
  `backend/studybuddy/management/commands/_year_level_scale.py`, moved
  `reset_demo_data.py` to import/use it, and updated `seed_data.py` to derive `year_level` from
  the selected course via `random_year_level(course.course_code)`. Verification caught one real
  edge case: `seed_data.py` was drawing from all persisted `Course` rows, including `BA-POLSCI`
  from `reset_demo_data.py`, so the final implementation also narrows `seed_data.py`'s course
  pool to the helper's supported 9-course map. `python manage.py seed_data` now completes
  successfully; a Django shell spot-check over the 30 newly created CPU Tutee/Tutor profiles found
  `invalid_count = 0`. `python manage.py test` required `--keepdb --noinput` because the local
  `test_postgres` DB already existed, then finished with the current baseline of `35` failures and
  `6` errors in unrelated existing areas (recommendation endpoints, auth/mail, dev tools, wallet
  flows, institution-scoped matching, and some payments tests).
- 2026-07-07: Audited the implementation and fixed two findings. (1) `_subjects_for()`'s
  college-year rebase (`profile.year_level - 12`) used a bare magic number instead of the shared
  module — added `COLLEGE_YEAR_OFFSET = YEAR_RANGE_BY_COURSE['BSCS'][0] - 1` to
  `_year_level_scale.py` and pointed `reset_demo_data.py` at it. Sanity-checked via a Django shell
  one-liner asserting `random_year_level()` stays within range for all 9 course codes. (2) The
  changelog's "35 failures + 6 errors" claim wasn't reconciled against the documented pre-existing
  baseline of "14 failures + 2 errors" (from the 2026-07-05 demo-data-reset plan) — re-ran the full
  suite independently and got `270 tests, 34 failures, 5 errors` (close to the prior run; test
  order/flakiness accounts for the off-by-one). Confirmed this is unrelated drift, not a
  regression: `grep`ing `tests.py` shows it never imports `reset_demo_data.py`, `seed_data.py`, or
  `_year_level_scale.py` — those are standalone `manage.py` commands outside the test fixture
  code path, so this change cannot be the cause. The "14+2" baseline documented elsewhere in this
  repo is simply stale (predates other work merged onto the branch since 2026-07-05).
