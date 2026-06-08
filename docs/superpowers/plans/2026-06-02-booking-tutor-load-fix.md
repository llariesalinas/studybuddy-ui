# Phase A — Booking "tutors won't load" Fix — Implementation Plan

> **For agentic workers:** Use superpowers:subagent-driven-development to execute task-by-task.

**Goal:** Make tutor searches return results by seeding realistic contiguous
30-minute availability, and make the results empty state explain the real reason.
**Stack:** Vue 3, Pinia, Django REST, Bootstrap 5
**Spec:** `docs/superpowers/specs/2026-06-02-booking-tutor-load-fix-design.md`

---

### Task 1: Seed contiguous 30-minute availability blocks

**Files:**
- Modify: `backend/studybuddy/management/commands/seed_data.py` (section "8. Seed TutorAvailability", ~line 243-265)

- [ ] Step 1: Replace the sparse `TIME_SLOTS` loop with a contiguous-block generator.
  Replace the existing block (from `DAY_CHOICES = [...]` through the
  `availability_pool.append(slot)` loop) with:

  ```python
  # 8. Seed TutorAvailability (contiguous 30-min blocks so multi-slot searches match)
  DAY_CHOICES = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

  def build_contiguous_slots(start_hour, block_hours):
      slots = []
      current = datetime.datetime.combine(
          datetime.date.today(), datetime.time(start_hour, 0)
      )
      end = current + datetime.timedelta(hours=block_hours)
      while current < end:
          slots.append(current.time())
          current += datetime.timedelta(minutes=30)
      return slots

  availability_pool = []

  for tutor in tutors:
      assigned_days = fake.random_elements(DAY_CHOICES, length=3, unique=True)
      for day in assigned_days:
          start_hour = fake.random_int(min=8, max=13)   # block starts 8am-1pm
          block_hours = fake.random_int(min=4, max=6)    # 4-6 hour contiguous block
          for time_slot in build_contiguous_slots(start_hour, block_hours):
              slot, created = TutorAvailability.objects.get_or_create(
                  tutor=tutor,
                  day=day,
                  time_slot=time_slot,
                  defaults={'is_active': True, 'is_booked': False},
              )
              availability_pool.append(slot)
  ```

- [ ] Step 2: Confirm `datetime` is imported at the top of the file as `import datetime`
  (it is already used as `datetime.time(...)`). Do not change the import style.
- [ ] Step 3: Verify — run `python manage.py seed_data` from `backend/`. It must
  finish without error. Then in `python manage.py shell`:
  ```python
  from studybuddy.models import TutorAvailability
  from datetime import time
  # there should now be :30 slots and adjacent slots
  print(TutorAvailability.objects.filter(time_slot=time(8, 30)).exists())  # True
  ```
- [ ] Step 4: Commit — `git commit -m "fix(seed): generate contiguous 30-min tutor availability so searches match"`

---

### Task 2: Context-aware empty state on the results page

**Files:**
- Modify: `src/views/FindTutors.vue` (template empty state ~line 172-175; script ~line 255-260)

- [ ] Step 1: Add a computed that distinguishes "API returned nothing" from
  "budget filter removed everything". After the `filteredTutors` computed
  (around line 260), add:

  ```js
  const noBackendResults = computed(() => matchedTutors.value.length === 0)
  const emptyStateTitle = computed(() =>
    noBackendResults.value
      ? 'No tutors available for this search'
      : 'No tutors match this budget range',
  )
  const emptyStateMessage = computed(() =>
    noBackendResults.value
      ? 'No tutors are available for the selected subject, date and time. Try a different date, time, or subject.'
      : 'Try widening the slider range to see more tutor options.',
  )
  ```

- [ ] Step 2: Replace the hardcoded empty-state markup (lines ~172-175) with:

  ```html
  <div v-else class="empty-state sb-card-surface rounded-4 shadow-sm text-center py-5 px-4">
    <h5 class="fw-bold sb-text mb-2">{{ emptyStateTitle }}</h5>
    <p class="sb-muted mb-0">{{ emptyStateMessage }}</p>
  </div>
  ```

- [ ] Step 3: Verify — `npm run build` succeeds. With the dev server running and a
  freshly seeded DB, run a search that matches (expect cards) and a search for an
  impossible time (expect the availability-worded empty state).
- [ ] Step 4: Commit — `git commit -m "fix(find-tutors): context-aware empty state messaging"`

---

### Task 3: Verify end-to-end and write the completion report

**Files:**
- Create: `docs/session-summaries/2026-06-02-phaseA-booking-load-fix-completion.md`

- [ ] Step 1: Run the full happy path against the running app (backend + `npm run dev`):
  log in as a seeded tutee → `/book` → pick a seeded subject, a future weekday,
  a time inside a seeded block → Find Tutor → confirm tutor cards render on
  `/find-tutors`.
- [ ] Step 2: Capture evidence — the `/recommend-tutors/` network response now
  contains tutors, and a screenshot of the populated results grid.
- [ ] Step 3: Write the completion report documenting: the root cause, the two
  changes made (with file paths), verification evidence (build output + the
  successful search), and any deviations from this plan. Use the report template
  in the "Completion report" section below.
- [ ] Step 4: Commit — `git commit -m "docs: Phase A booking-load fix completion report"`

---

## Completion report template

```markdown
# Phase A Completion Report — Booking "tutors won't load" Fix
**Date completed:** <YYYY-MM-DD>
**Branch:** <branch>
**Plan:** docs/superpowers/plans/2026-06-02-booking-tutor-load-fix.md

## Summary
<1-2 sentences: what was broken and what fixed it>

## Root cause
<the all-slots-required vs sparse-seed mismatch>

## Changes
| File | Change |
|---|---|
| backend/.../seed_data.py | contiguous 30-min availability blocks |
| src/views/FindTutors.vue | context-aware empty state |

## Verification
- [ ] python manage.py seed_data — ran clean
- [ ] python manage.py check — passed
- [ ] npm run build — passed
- [ ] Manual search returns tutors (evidence: <network/screenshot>)
- [ ] Impossible-time search shows availability-worded empty state

## Deviations
<none, or list>
```
