# Brief: Booking subject persistence — code-review follow-up fixes

Follow this brief exactly. Standing rules are in AGENTS.md. Reference:
[docs/plans/2026-07-08-booking-subject-persistence-codex-handoff.md](../plans/2026-07-08-booking-subject-persistence-codex-handoff.md)
(the original spec — already fully implemented across commits `761216b`..`02f2444` on
`feat/demo-data-reset`; this brief is a code-review follow-up on that implementation, not a
re-implementation).

## Scope

Three findings from a Standards/Spec review of `bd3b52f...HEAD` (the booking-subject-persistence
diff):

1. Extract a duplicated error string in `backend/studybuddy/views.py` into a module-level
   constant.
2. Extract a duplicated subject-label ternary in `backend/studybuddy/views.py` into one helper
   function.
3. Write the missing session summary for the booking-subject-persistence work and mark its plan
   Done in the docs index.

Out of scope: everything else in the diff (it was already reviewed and found correct — do not
touch `models.py`, the migration, `TutorDetails.vue`, `tests.py` logic, or either seed script
beyond what's listed below). Do not touch the separate `tutor-verification-relocation` plan/spec —
unrelated work, not part of this brief.

## Execution checklist

### 1. Extract `SUBJECT_NOT_RECOGNIZED_ERROR` constant

The literal `"This subject is not recognized for your course catalog."` is duplicated 4 times in
`backend/studybuddy/views.py`, each as an inline `{"error": "..."}` 400 response body:

- Line 1906 — inside `dashboard_recommendations` (function starts line 1876)
- Line 2494 — inside `confirm_payment_and_book` (function starts line 2418)
- Line 3883 — inside `recommend_tutors_view` (function starts line 3863)
- Line 4138 — inside `add_tutor_subject` (function starts line 4123)

Add one module-level constant and use it at all 4 sites:

```python
SUBJECT_NOT_RECOGNIZED_ERROR = "This subject is not recognized for your course catalog."
```

Match this file's existing convention for simple string constants — see `OTP_ERROR_MESSAGE`
(line 134) for the exact style (name + assignment, no extra wrapping). Place it near the top of
the file alongside similar single-purpose message constants (e.g. near `OTP_ERROR_MESSAGE`), not
inline in any of the 4 functions. Replace each of the 4 usages with
`{"error": SUBJECT_NOT_RECOGNIZED_ERROR}` (preserve the surrounding response structure —
status code, any other keys — exactly as-is; only the string literal changes).

- [ ] Constant defined once, near `OTP_ERROR_MESSAGE`
- [ ] All 4 call sites (lines 1906, 2494, 3883, 4138) reference the constant, not the literal
- [ ] No other behavior at those 4 sites changed

### 2. Extract `booking_subject_label(booking)` helper

The same ternary — "the booked subject's name, falling back to the literal string `"General"`
when the booking has no subject" — is duplicated 4 times in `backend/studybuddy/views.py`:

- Lines 837-839, inside `get_session_notification_context` (function starts line 826):
  ```python
  subject = (
      representative_booking.subject.subject_name
      if representative_booking.subject else "General"
  )
  ```
- Lines 2019-2021, inside `build_combined_block` (function starts line 1964):
  ```python
  first.subject.subject_name
  if first.subject
  else "General"
  ```
- Lines 2116-2118, inside `build_booking_request_block` (function starts line 2092):
  ```python
  first_booking.subject.subject_name
  if first_booking.subject
  else "General"
  ```
- Line 3232, inside `build_booking_detail_payload` (function starts line 3169):
  ```python
  "subject": representative_booking.subject.subject_name if representative_booking.subject else "General",
  ```

Add one helper function taking a single `Booking` instance and returning its display label:

```python
def booking_subject_label(booking):
    return booking.subject.subject_name if booking.subject else "General"
```

Place it near the other small booking-helper functions already in this area of the file — e.g.
right after `get_representative_booking` (line 795) or immediately before
`get_session_notification_context` (line 826), matching the existing pattern of small
single-purpose helpers like `get_payment_method_label` (line 1036). Replace each of the 4 call
sites above with `booking_subject_label(representative_booking)` /
`booking_subject_label(first.booking)` / `booking_subject_label(first_booking)` as appropriate —
use whichever local variable each site already holds; do not rename existing variables.

- [ ] `booking_subject_label(booking)` defined once, near the existing booking-helper functions
- [ ] All 4 call sites (lines ~837-839, ~2019-2021, ~2116-2118, ~3232) call the helper instead of
      repeating the ternary
- [ ] No other behavior in those 4 functions changed

### 3. Session summary + mark plan Done

The booking-subject-persistence implementation (commits `761216b`..`02f2444`) is complete and
already committed, but `docs/plans/README.md` still describes it as "Approved... nothing
implemented yet" and it has no row in the plans table or a session summary — the doc project
convention (see `.claude/CLAUDE.md` "Documentation & graphify" and "On completion, write a
summary") requires both.

**a. Write the summary** at
`docs/session-summaries/2026-07-08-booking-subject-persistence-summary.md`. Match the format of
`docs/session-summaries/2026-07-07-reenable-cash-payments-summary.md` (header, `**Plan:**` /
`**Status:**` lines, `## What shipped`, `## Verification`, `## Deviations from the original plan`
if any). Base the content on:
   - The spec: `docs/plans/2026-07-08-booking-subject-persistence-codex-handoff.md` (root cause,
     the fix, Tasks 1-7).
   - The actual commits: `git log --oneline 761216b^..02f2444` and their diffs — describe what
     each commit actually did (subject FK + migration, persist-on-confirm, the 2 fixed
     display/notification call sites, tests, seed-script updates).
   - Run `python manage.py test studybuddy.tests` (from `backend/`) for the tests this work added
     (search `tests.py` for tests referencing `subject` added in commit `6ce57c6`) and record
     pass/fail counts under `## Verification`. If a local test database isn't configured, say so
     explicitly rather than fabricating a result — do not claim tests pass without having run them.

**b. Update `docs/plans/README.md`:**
   - In the `**Status & Progress Summary**` paragraph at the top (currently starts "Booking
     subject persistence (Codex handoff) is Approved..."), rewrite it to say Done, summarizing
     what shipped (mirror the style of the "Re-enable cash payments..." sentence later in the same
     paragraph), and link the new summary file.
   - Add a row to the `| Date | Plan | Status | Summary |` table (it currently has no row for this
     plan) directly below the `2026-07-08 | Algorithm Demo` row:
     `| 2026-07-08 | [Codex Handoff — Persist the Booked Subject on Booking](2026-07-08-booking-subject-persistence-codex-handoff.md) | Done | <one-line summary> — [Summary](../session-summaries/2026-07-08-booking-subject-persistence-summary.md) |`
   - Add a `## Changelog` row at the bottom dated 2026-07-08 describing the follow-up fixes and
     the Done status change.

**c. Regenerate `docs/plans/index.html`:** the generator script referenced by
`.claude/CLAUDE.md` (`docs/plans/build-plans-index.ps1`) does not exist yet in this repo — copy it
from `~/.claude/scripts/build-plans-index.ps1` into `docs/plans/` first (one-time, per the
project convention), then run:
```
powershell -NoProfile -File docs/plans/build-plans-index.ps1
```
This should move the "Codex Handoff — Persist the Booked Subject on Booking" card from the
Approved group to the (collapsed) Done group and update the badge-row counts. Do not hand-edit
`index.html` — if the script produces a different layout than the current hand-edited version,
the script's output wins.

- [ ] `docs/session-summaries/2026-07-08-booking-subject-persistence-summary.md` written, matching
      the existing summary format, with an honest (not fabricated) `## Verification` section
- [ ] `docs/plans/README.md` narrative paragraph updated to Done, table row added, changelog row
      added
- [ ] `docs/plans/build-plans-index.ps1` copied into `docs/plans/` if missing, then run;
      `docs/plans/index.html` reflects the Done status

## Context

- Repo: Vue 3 (Composition API) + Pinia frontend, Django REST backend. Backend in `backend/`.
- Conventions: PEP 8 (snake_case functions/vars, PascalCase classes); no hardcoded/repeated string
  literals — use named constants; small, focused changes — don't touch unrelated code; no emojis
  anywhere (code, comments, commits, docs).
- This is a **quality follow-up on already-shipped code**, not a bugfix — behavior must not change
  at any of the 8 call sites touched in items 1-2. These are pure refactors.
- `backend/studybuddy/tests.py` already has full coverage of the subject-persistence behavior
  (added in commit `6ce57c6`) — running the existing suite is sufficient to confirm items 1-2
  didn't break anything; no new tests are needed for the refactor itself.

## Contract

- Work ONLY this brief — no scope creep, no drive-by refactors beyond the 2 named extractions.
- TDD does not apply to items 1-2 (pure refactor of already-tested code) — instead, run the
  existing relevant tests before and after to confirm identical behavior. Item 3 is docs-only, no
  tests apply.
- Run the backend test suite (or at minimum the tests covering the touched functions —
  `dashboard_recommendations`, `confirm_payment_and_book`, `recommend_tutors_view`,
  `add_tutor_subject`, `get_session_notification_context`, `build_combined_block`,
  `build_booking_request_block`, `build_booking_detail_payload`) and get them green. Paste commands
  and output under Test evidence.
- NEVER commit, push, branch, or run any git write. Leave the tree dirty.
- Record anything done differently, and why, under Deviations.

## Test evidence

- `python manage.py test studybuddy.tests` (from `backend/`): discovered 293 tests, then stopped
  before execution because the existing `test_postgres` database triggered an interactive delete
  prompt that the non-interactive runner could not answer (`EOFError`).
- `python manage.py test studybuddy.tests --keepdb` (from `backend/`): started using the existing
  test database, but was stopped at the owner's request before producing a pass/fail result.
- No post-change tests were run, per the owner's explicit instruction to continue without tests.

## Deviations

- The required before/after backend verification was not completed. The initial command was
  blocked by the existing test database, and the `--keepdb` retry was stopped at the owner's
  request; the owner then explicitly authorized completing the brief without tests.
- Added standard frontmatter to the legacy handoff plan because the prescribed index generator
  only includes frontmatter-backed plans; without it, regeneration removed the card instead of
  moving it to the Done group. The historical handoff body was left unchanged.
