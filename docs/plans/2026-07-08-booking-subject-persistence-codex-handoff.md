# Codex Handoff — Persist the Booked Subject on Booking

## Status & Progress Summary
**Status:** Ready for Codex execution. Nothing implemented yet — root cause was diagnosed in-session (Claude), no code has been touched.
**Next step:** Give this document to Codex CLI. Execute Tasks 1–7 in order, committing after each (Task 6, the seed-data update, depends on Task 1's migration existing — do not reorder it earlier). Report back per the "Report back" section at the end.

---

## Context

Repo root: `C:\FIles\Studybuddy\FrontEnd\studybuddy-ui`
Stack: Vue 3 (Composition API) + Pinia frontend, Django REST backend. Backend lives in `backend/`, frontend in `src/`.
Current branch: `feat/demo-data-reset` (not main — fine to keep committing here unless told otherwise).

**The bug:** Session details for both tutee and tutor (`TuteeSessionDetailsFlow.vue`, `TutorBookingDetailsFlow.vue`) show a "Subject" field that actually displays the **tutor's course/academic program** (e.g. "BS Computer Science"), not the specific subject that was taught in that session (e.g. "CS101 - Data Structures"). Booking-status notification text has the same bug.

**Root cause:** `Booking` (`backend/studybuddy/models.py:830`) has no field recording which `Subjects` row was booked. The tutee does pick a subject during booking (`InitialBooking.vue` → `initialbookingprefs.selectedSubject`, holding a `Subjects.subject_code`), but that value is used only to filter tutor search results in `FindTutors.vue` — it is never sent to the backend on `POST bookings/confirm/` (`TutorDetails.vue:807`), and `confirm_payment_and_book` never persists it. Every place that later needs "the subject" for a booking has nothing to read, so it falls back to `tutor.profile.course.course_name` instead:
- `build_booking_detail_payload` (`backend/studybuddy/views.py:3222`) — feeds the session-details "Subject" field.
- `get_session_notification_context` (`backend/studybuddy/views.py:837-839`) — feeds notification copy like "Your booking for {subject} with {tutor_name}...".

**The fix:** add a real `subject` FK on `Booking`, populate it at booking-confirm time from what the tutee actually selected, and read it back instead of the course fallback. Kept backward-compatible: `subject` is nullable, so existing/historical bookings and any confirm request that omits it (pre-existing tests) keep working — they just fall back to `"General"` at display time, exactly like today.

---

## Relevant existing files (read before editing)

- `backend/studybuddy/models.py` — `class Booking(models.Model):` at line 830. `class Subjects(models.Model):` at line 696 (FK target).
- `backend/studybuddy/views.py`:
  - `confirm_payment_and_book` (line 2418) — the endpoint to change. The actual `Booking.objects.create(...)` call is at line 2575.
  - `build_booking_detail_payload` (line 3159) — `"subject"` key is set at line 3222.
  - `get_session_notification_context` (line 826) — `subject` computed at lines 837-839.
  - `subject_is_recognized_for_profile` is already imported (from `.subject_recognition`, see import block starting line 64) — reuse it for validation, don't write a new check.
- `backend/studybuddy/tests.py` — `post_confirm_booking` helper (line 3694) posts to `/api/bookings/confirm/` without a `subject` key; multiple tests reuse it. Do not make `subject` required server-side or all of these break.
- `src/views/TutorDetails.vue` — `confirmBooking()` (line 793), the POST call is at line 807.
- `src/stores/initialbookingprefs.js` — `selectedSubject` (line 8) is the tutee's chosen `Subjects.subject_code`.
- `src/views/TuteeSessionDetailsFlow.vue:502` and `src/views/TutorBookingDetailsFlow.vue:499` — both already correctly labeled `'Subject'`, reading `...session?.subject` / `...sessionInfo?.subject`. No changes needed here — once the backend returns the real subject, these render correctly for free.
- `backend/studybuddy/management/commands/reset_demo_data.py` — `_make_booking` helper (line 687), called from `_seed_bookings_and_ratings`, `_seed_cluster_scenarios`, `_seed_load_limit_scenarios`, `_seed_compensation`. `_seed_subjects_and_preferences` (line 609) builds `ts_rows` (list of unsaved `TutorSubjects(tutor=..., subject=...)`) before `bulk_create`-ing them at line 649.
- `backend/studybuddy/management/commands/seed_data.py` — booking-creation loop at lines 297–330; `TutorSubjects` seeded per-tutor at lines 233–244 but not currently kept in a lookup structure.

---

## Task 1 — Backend: add `subject` FK to `Booking`

**Files:**
- Modify: `backend/studybuddy/models.py`

1. In `class Booking(models.Model):`, add a new field directly after `availability` (before `session_date`):
   ```python
   subject = models.ForeignKey(
       Subjects,
       on_delete=models.PROTECT,
       null=True,
       blank=True,
       related_name="bookings",
   )
   ```
   Nullable/optional by design — historical bookings have no value, and this must not force every caller of `confirm_payment_and_book` to change at once. `PROTECT` (not `CASCADE`/`SET_NULL`) because a `Subjects` row backing real booking history should not be silently deletable; this matches how `Subjects` is treated elsewhere (e.g. `InstitutionCourseCatalog` uses `CASCADE` for catalog curation rows, but bookings are historical records worth protecting).
2. Run `cd backend && venv\Scripts\python.exe manage.py makemigrations studybuddy` — review the generated migration, confirm it only adds this one field.
3. Run `venv\Scripts\python.exe manage.py migrate` locally to confirm it applies cleanly.
4. Verify: `venv\Scripts\python.exe manage.py check` — clean, no errors.
5. Commit: `git add backend/studybuddy/models.py backend/studybuddy/migrations/ && git commit -m "feat: add subject field to Booking"`

---

## Task 2 — Backend: persist the chosen subject on booking confirm

**Files:**
- Modify: `backend/studybuddy/views.py` (`confirm_payment_and_book`, starting line 2418)

Depends on Task 1.

1. Near the top of `confirm_payment_and_book`, alongside the existing `tutor_id = request.data.get("tutor_id")` / `slots = request.data.get("slots")` lines (~2431-2434), add:
   ```python
   subject_code = request.data.get("subject")
   ```
2. After `tutor = get_object_or_404(Tutor, profile_id=tutor_id)` (line 2488), resolve it — optional, so only validate when present:
   ```python
   subject = None
   if subject_code:
       if not subject_is_recognized_for_profile(user_profile, subject_code):
           return Response(
               {"error": "This subject is not recognized for your course catalog."},
               status=400,
           )
       subject = Subjects.objects.filter(subject_code=subject_code).first()
   ```
   (`Subjects` is already imported in this file's model import block — confirm, don't duplicate the import if so.)
3. In the `Booking.objects.create(...)` call (line 2575), add `subject=subject,` alongside the existing kwargs.
4. Verify: `venv\Scripts\python.exe manage.py check` clean.
5. Commit: `git add backend/studybuddy/views.py && git commit -m "feat: persist chosen subject on booking confirm"`

---

## Task 3 — Backend: read the real subject instead of the tutor's course

**Files:**
- Modify: `backend/studybuddy/views.py`

Depends on Task 1 (needs the field to exist).

1. In `build_booking_detail_payload` (line 3159), change line 3222 from:
   ```python
   "subject": representative_booking.tutor.profile.course.course_name if representative_booking.tutor.profile.course else "General",
   ```
   to:
   ```python
   "subject": representative_booking.subject.subject_name if representative_booking.subject else "General",
   ```
2. In `get_session_notification_context` (line 826), change lines 837-840 from:
   ```python
   subject = (
       representative_booking.tutor.profile.course.course_name
       if representative_booking.tutor.profile.course else "General"
   )
   ```
   to:
   ```python
   subject = (
       representative_booking.subject.subject_name
       if representative_booking.subject else "General"
   )
   ```
3. Search `views.py` for any other occurrence of `tutor.profile.course.course_name` used as a stand-in for a session's subject (the two above are the ones found during diagnosis — confirm no third call site was missed, e.g. in a serializer or another `*_detail_payload`-style helper). Do not touch legitimate uses of `tutor.profile.course` / `student.course` that actually mean "this person's academic course" (e.g. the `"tutee": {"course": ...}` and `"tutor": {"course": ...}` keys a few lines above in the same function at 3200/3208 — those are correct as-is and must not change).
4. Verify: `venv\Scripts\python.exe manage.py check` clean.
5. Commit: `git add backend/studybuddy/views.py && git commit -m "fix: session subject reflects booked subject, not tutor's course"`

---

## Task 4 — Backend: tests

**Files:**
- Modify: `backend/studybuddy/tests.py`

Depends on Tasks 1-3.

Find the test class using `post_confirm_booking()` (search `post_confirm_booking` — the helper at line 3694) and the test class covering `booking_detail` / `build_booking_detail_payload` (search `build_booking_detail_payload` or the view name `booking_detail`). Add:

1. `test_confirm_booking_persists_subject`: call `post_confirm_booking` but extend the helper (or a local variant) to also send `"subject": <a real subject_code fixture>`. Assert response `200`, then fetch the created `Booking` (`Booking.objects.get(id=response.data["booking_ids"][0])`) and assert `booking.subject.subject_code == <that code>`.
2. `test_confirm_booking_without_subject_still_succeeds`: call the existing `post_confirm_booking()` unmodified (no `subject` key) — assert `200` and the created booking's `subject` is `None`. This is the regression guard proving the field stayed optional.
3. `test_confirm_booking_rejects_unrecognized_subject`: call with a `subject` code that is not recognized for the tutee's course catalog (reuse whatever fixture/pattern the existing `subject_is_recognized_for_profile`-gated views use for this negative case, e.g. in `get_tutor_recommendations` tests) — assert `400`.
4. `test_booking_detail_session_subject_reflects_booked_subject_not_course`: create a `Booking` directly with `subject=<Subjects fixture A>` where the tutor's `profile.course` is a *different* course/subject name than A's `subject_name`. Call whichever endpoint renders `build_booking_detail_payload` (e.g. `booking_detail`) and assert `response.data["session"]["subject"] == "<A's subject_name>"` — not the tutor's course name. This is the regression test for the actual bug.
5. `test_booking_detail_session_subject_falls_back_to_general_when_null`: same shape, `subject=None` on the booking — assert `"session"]["subject"] == "General"`.

Verify: `venv\Scripts\python.exe manage.py test studybuddy.tests` — confirm your 5 new tests pass and you have not introduced new failures beyond the repo's existing pre-existing baseline (there is a documented pre-existing baseline of unrelated failures in this suite — if unsure, run the suite once on the commit before Task 1 to compare).

Commit: `git add backend/studybuddy/tests.py && git commit -m "test: cover booking subject persistence and session-detail display"`

---

## Task 5 — Frontend: send the chosen subject on confirm

**Files:**
- Modify: `src/views/TutorDetails.vue`

Depends on Task 2 (backend now accepts the field).

1. In `confirmBooking()` (line 793), the `api.post('bookings/confirm/', {...})` call at line 807 currently sends `tutor_id`, `slots`, `preferred_location`. Add the subject:
   ```js
   await api.post('bookings/confirm/', {
     tutor_id: tutorID,
     slots: effectiveSelectedSlots.value,
     preferred_location: bookedSessionStore.bookedSessionLocation,
     subject: bookedSessionStore.bookedSessionSub
   })
   ```
   `bookedSessionStore.bookedSessionSub` is already set two lines above (line 804: `bookedSessionStore.bookedSessionSub = bookedSessionStore.bookedSessionSub || initialBookingStore.selectedSubject`), so it already holds the `subject_code` the tutee picked — this task only wires it into the request body, no new state needed.
2. Verify: `npm run lint` clean.
3. Commit: `git add src/views/TutorDetails.vue && git commit -m "feat: send chosen subject when confirming a booking"`

---

## Task 6 — Seed data: give demo bookings a real subject

**Files:**
- Modify: `backend/studybuddy/management/commands/reset_demo_data.py`
- Modify: `backend/studybuddy/management/commands/seed_data.py`

Depends on Task 1 (the `Booking.subject` field must exist — do not run either seed command against a database that hasn't had Task 1's migration applied).

Without this task, every demo/dev-seeded booking would have `subject=None` and display "General" everywhere — not wrong, but not a useful demo of the fix either.

### `reset_demo_data.py`

1. In `_seed_subjects_and_preferences` (line 609), immediately after `TutorSubjects.objects.bulk_create(ts_rows)` (line 649), add a lookup built from `ts_rows` (the unsaved objects still have `.subject` and `.tutor_id` set, no need to re-query):
   ```python
   self.subjects_by_tutor = {}
   for row in ts_rows:
       self.subjects_by_tutor.setdefault(row.tutor_id, []).append(row.subject)
   ```
2. In `_make_booking` (line 687), pick a subject when the caller doesn't force one:
   ```python
   def _make_booking(self, tutee, tutor, slot, session_date, status, **extra):
       session_mode = extra.pop('session_mode', 'Online' if tutor.can_online else 'F2F')
       subject = extra.pop('subject', None) or random.choice(
           self.subjects_by_tutor.get(tutor.pk) or [None]
       )
       return Booking(student=tutee, tutor=tutor, availability=slot,
                      session_date=session_date, subject=subject,
                      session_mode=session_mode,
                      status=status, session_group_id=uuid4(), booking_request_id=uuid4(),
                      tutee_confirmed=status in ('Confirmed', 'Completed'),
                      tutor_confirmed=status in ('Confirmed', 'Completed'), **extra)
   ```
   This is a random subject from whatever that specific tutor teaches (per `TutorSubjects`), which is the same "believable, not perfectly matched" fidelity the rest of this file already uses elsewhere (e.g. rating scores). Every call site of `_make_booking` (`_seed_bookings_and_ratings`, `_seed_cluster_scenarios`, `_seed_load_limit_scenarios`, `_seed_compensation`) picks this up automatically with no call-site changes, since none of them currently pass a `subject=` kwarg.
3. Confirm ordering: `_seed_subjects_and_preferences` already runs before `_seed_availability` and `_seed_bookings_and_ratings` in `handle()` (lines 287-289) — no reordering needed, `self.subjects_by_tutor` will be populated before any `_make_booking` call.

### `seed_data.py`

1. In the `# 7. Seed TutorSubjects` block (lines 233-244), track what got assigned per tutor instead of discarding it:
   ```python
   tutor_subjects_by_tutor = {}

   for tutor in tutors:
       assigned = fake.random_elements(all_seeded_subjects, length=fake.random_int(min=2, max=4), unique=True)
       for subject in assigned:
           TutorSubjects.objects.get_or_create(
               tutor=tutor,
               subject=subject,
               defaults={'expertise_level': fake.random_int(min=1, max=3)}
           )
       tutor_subjects_by_tutor[tutor.pk] = list(assigned)
       self.stdout.write(f"  - Subjects assigned to {tutor.profile.fname}: {[s.subject_code for s in assigned]}")
   ```
2. In the booking-creation loop (`# 10. Seed Bookings + Payments`, lines 297-330), pick a subject for each booking and pass it through:
   ```python
   subject = fake.random_element(tutor_subjects_by_tutor.get(tutor.pk) or [None])

   booking = Booking.objects.create(
       student=tutee,
       tutor=tutor,
       availability=slot,
       session_date=session_date,
       subject=subject,
       session_mode=session_mode,
       status=status_choice,
       tutee_confirmed=True,
       tutor_confirmed=True,
       session_group_id=uuid4(),
       booking_request_id=uuid4()
   )
   ```

### Verify both

3. `cd backend && venv\Scripts\python.exe manage.py reset_demo_data` — must complete without errors; spot-check via shell (`python manage.py shell`) that `Booking.objects.exclude(subject=None).count() > 0` and that a few sampled bookings have `booking.subject.subject_name` differing from `booking.tutor.profile.course.course_name`.
4. `venv\Scripts\python.exe manage.py seed_data` against a scratch/local DB — same spot-check.
5. Commit: `git add backend/studybuddy/management/commands/reset_demo_data.py backend/studybuddy/management/commands/seed_data.py && git commit -m "chore: seed a real subject on demo/dev bookings"`

---

## Task 7 — End-to-end manual verification

No files changed in this task — it's a live check.

1. `cd backend && venv\Scripts\python.exe manage.py migrate && venv\Scripts\python.exe manage.py reset_demo_data`
2. `venv\Scripts\python.exe manage.py runserver 8000` and, separately, `npm run dev`.
3. Log in as a seeded Tutee, book a new session end-to-end through `InitialBooking.vue` → `FindTutors.vue` → `TutorDetails.vue`, picking a specific subject.
4. Open that session's details (tutee side). Confirm the "Subject" field shows the subject you picked (e.g. "CS101 - Data Structures"), not the tutor's course/program.
5. Log in as that tutor, open the same booking's details. Confirm the same correct subject shows on the tutor side (`TutorBookingDetailsFlow.vue`).
6. Check a notification generated for this booking (e.g. the pending-request notification to the tutor) — confirm its text also references the real subject, not the course.
7. Spot-check a couple of pre-existing/seeded bookings created before this change conceptually existed (any booking whose `subject` is `None`, if any remain from an old DB) — confirm they gracefully show "General" rather than erroring.

---

## Risks / things to watch for

- `subject` is `on_delete=models.PROTECT`. If any future feature deletes `Subjects` rows (e.g. an admin "remove subject from catalog" action), deleting a `Subjects` row that has booking history will now raise `ProtectedError` instead of silently cascading. This is intentional (don't erase booking history), but if such an admin flow exists, confirm it already handles `ProtectedError`-style conflicts for other protected FKs, or surfaces a clear error instead of a 500.
- Do not make `subject` required at the API layer — `post_confirm_booking()` in `tests.py` and any real in-flight frontend clients that haven't deployed Task 5 yet must keep working with no `subject` key at all.
- Task 6's seed changes must not run against a database that hasn't had Task 1's migration applied — the `Booking(...)` / `Booking.objects.create(...)` calls will fail with "unexpected keyword argument" otherwise. Migrate first.
- `subject_is_recognized_for_profile` takes an optional `course_code` param (see `backend/studybuddy/subject_recognition.py:91`) — Task 2 calls it with just `(user_profile, subject_code)`, matching how it's already called elsewhere for tutee-facing recognition checks. Don't add a `course_code` override unless you find a reason another similar call site does.

---

## Report back

After completing all 7 tasks, write a short summary covering:
- Commits created (short SHA + one-line message) for each task.
- Migration name generated in Task 1.
- Backend test results: command run and pass/fail counts, separating your new tests from any pre-existing unrelated baseline failures.
- Lint/build results: `npm run lint` and `npm run build` output status.
- Manual verification (Task 7): confirm each step passed, flag anything that didn't behave as expected.
- Any deviations from this handoff and why.

If you get blocked or something in this handoff doesn't match what you find in the actual files (a line-number reference is stale, a function/field name has changed), stop and describe the mismatch rather than guessing — this handoff was written against the codebase state as of 2026-07-08.

---

## Changelog

- 2026-07-08: Created — root cause diagnosed via `systematic-debugging` (Booking has no subject FK; `build_booking_detail_payload` and `get_session_notification_context` both fall back to the tutor's course/program as a stand-in for "subject"). Transcribed directly into a self-contained Codex handoff, including a seed-data task, per explicit request — no in-session implementation.
