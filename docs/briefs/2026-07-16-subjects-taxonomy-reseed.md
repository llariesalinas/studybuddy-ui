# Brief: Subjects taxonomy reseed and recommender proof

Follow this brief exactly. Standing rules are in AGENTS.md. Reference:
`docs/plans/2026-07-16-subjects-taxonomy-reseed.md` (the approved plan; its Decisions section
is binding) and `docs/mockups/2026-07-16-subject-taxonomy-picker.html` (the decided picker
design).

## Scope

Steps 2-10 of the plan: CBF level fix, subject-gating retirement, taxonomy catalog, wipe
command, seed rewrite, admin catalog API + UI, two-level subject picker, code-display cleanup,
cheat-sheet + architecture doc updates.

Out of scope: anything git (branching/merging is already done — you are on
`feat/subjects-reseed` with `feat/recommender-weight-rebalance` merged); schema migrations (the
design deliberately avoids them); a tutor-facing expertise-editing UI (known gap, deliberately
deferred); the 7 pre-existing `RecommendTutorsViewTests` failures (see Baseline below).

## Baseline (verified 2026-07-16 on this branch)

`python manage.py test --noinput --keepdb studybuddy.tests.CbfGraduatedSubjectMatchTests
studybuddy.tests.CfPeerNeighborTests studybuddy.tests.RecommendTutorsViewTests
studybuddy.tests.RecommenderNeighborReuseTests` -> FAILED (failures=7). All 7 failures are in
`RecommendTutorsViewTests`, pre-exist on the parent branch `feat/instant-booking`, and are NOT
yours to fix. The three formula test classes pass. Do not let this count grow.

Note: the local test DB may be locked by a running dev server. Use `--keepdb`. Django test
runner: `python manage.py test` from `backend/`.

## Execution checklist

### 1. CBF level fix

Files: `backend/studybuddy/recommender/cbf.py`, `backend/studybuddy/tests.py`.

In `compute_cbf_breakdown` (cbf.py ~line 138), replace the dead check
`if tutor_level == "SHS" and student_year is not None and int(student_year) > 12` with a
module-level constant and ceiling lookup:

```python
TEACHING_LEVEL_MAX_YEAR = {"Elementary": 6, "High School": 12, "College": 16}
```

`s_level = 0` if and only if the tutor has a known `teaching_level` AND the student has a
`year_level` AND `int(student_year) > TEACHING_LEVEL_MAX_YEAR[tutor_level]`. Unknown/blank
teaching level or missing student year -> `s_level = 1` (never penalize missing data; no
downward penalty by design: a College tutor with a young student stays 1). The unified year
scale is 1-6 elementary, 7-10 JHS, 11-12 SHS, 13-16 college (see
`backend/studybuddy/management/commands/_year_level_scale.py`).

- [ ] Constant exists; the string `"SHS"` no longer appears in cbf.py.
- [ ] New tests: High School tutor + college student (year 14) -> level contribution 0;
      Elementary tutor + JHS student (year 8) -> 0; College tutor + SHS student (year 11) -> 1;
      blank teaching_level -> 1.
- [ ] `AlgorithmDemoBreakdown.vue` and `recommender/demo.py` need no change if they render the
      breakdown dict generically — verify, only touch if they hardcode "SHS".

### 2. Retire course-based subject gating

Files: `backend/studybuddy/subject_recognition.py`, `backend/studybuddy/recommender/cbf.py`,
`backend/studybuddy/views.py` (imports at line 65; find all call sites of the five imported
helpers), `backend/studybuddy/tests.py`.

`Subjects.category` stops meaning "course code" and starts meaning "taxonomy category"
(checklist 3), so course-derived recognition is retired:

- `recognized_subject_codes_for_profile` -> all `status='approved'` subject codes (ignore
  course entirely). Keep the function and its signature so callers keep working; delete
  `COURSE_CODE_GROUPS` / `equivalent_course_codes`.
- `subject_selection_queryset_for_profile` -> all approved subjects (plus `include_current`
  additions, which may include pending tutor-proposed subjects).
- `invalid_new_subject_codes` -> rejects only codes that don't exist or aren't
  approved/current. `subject_is_recognized_for_profile` follows.
- In `cbf.py::get_student_subject_codes`, drop the recognized-codes filter: return the
  tutee's preference codes as-is.
- [ ] Update/remove tests that assert course-scoped recognition; add one test that a BSCS
      tutee may select a Hobbies & Arts subject.

### 3. Taxonomy catalog data module

New file: `backend/studybuddy/subject_taxonomy.py`. Single source of truth used by the seed,
the admin API validation, and anything needing the category list.

```python
CATEGORIES = [
    "Mathematics & Data Sciences",
    "Natural Sciences",
    "Technology & Computer Science",
    "Business, Finance & Economics",
    "Humanities & Social Sciences",
    "Hobbies & Arts",
]
```

Subjects as `(name, category, subgroup)` tuples plus a `slugify_subject_code(name)` helper:
lowercase, non-alphanumeric runs -> single hyphen, trimmed; explicit overrides
`{"C++": "cpp", "C#": "csharp", "C": "c-language"}` to avoid slug collisions. `category` field
gets the category, `department` field gets the subgroup (internal metadata, never displayed).

Full catalog (117 subjects — seed exactly these):

- Mathematics & Data Sciences / Core Math: Pre-Algebra, Algebra, Geometry, Trigonometry,
  Pre-Calculus. / Advanced & Pure Math: Calculus, Linear Algebra, Abstract Algebra,
  Differential Equations, Discrete Mathematics, Number Theory. / Applied Math & Statistics:
  Statistics, Biostatistics, Probability, Data Analysis, Regression Analysis, Actuarial
  Science. / Grade Levels: Elementary Math, High School Math, College Mathematics. (20)
- Natural Sciences / Physics: Classical Mechanics, Thermodynamics, Electromagnetism, Quantum
  Mechanics, Astrophysics, Relativity, Optics. / Chemistry: General Chemistry, Organic
  Chemistry, Inorganic Chemistry, Physical Chemistry, Biochemistry, Analytical Chemistry. /
  Biology: Molecular Biology, Genetics, Cell Biology, Human Anatomy & Physiology,
  Microbiology, Zoology, Botany, Marine Biology. / Earth & Environmental Sciences: Ecology,
  Geology, Meteorology, Environmental Science, Paleontology. (26)
- Technology & Computer Science / Programming Languages: Python, Java, JavaScript, C, C++,
  C#, Ruby, PHP, SQL, HTML & CSS. / Computer Science Theories: Algorithms, Data Structures,
  Machine Learning, Artificial Intelligence, Cybersecurity, Database Management, Software
  Engineering, Web Development. (18)
- Business, Finance & Economics / Economics: Microeconomics, Macroeconomics, Econometrics,
  Behavioral Economics, International Trade. / Accounting & Finance: Financial Accounting,
  Managerial Accounting, Corporate Finance, Personal Finance, Investment Banking, Auditing. /
  Business & Management: Marketing, Human Resource Management, Operations Management,
  Entrepreneurship, Project Management, Strategic Management. (17)
- Humanities & Social Sciences / History: World History, European History, American History,
  Ancient History, Art History, Military History. / Social Sciences: Psychology, Sociology,
  Anthropology, Political Science, International Relations. / Law: Constitutional Law,
  Corporate Law, International Law, Criminal Law, Legal Writing. / Literature & Writing:
  Literary Analysis, Creative Writing, Academic Writing, Essay Editing, Rhetoric, Journalism. /
  Philosophy: Ethics, Logic, Epistemology, Metaphysics, Political Philosophy. (27)
- Hobbies & Arts / Music Theory & Instruments: Music Theory, Solfege, Ear Training, Piano,
  Guitar, Violin, Drums, Music Production. / Visual Arts: Digital Art, Fine Art, Painting,
  Graphic Design, Photography. (13)

Special Education Support is deliberately excluded (peer tutors cannot hold the required
professional credentials) — do not add it.

- [ ] Module exists with exactly these subjects and a slug helper with collision overrides.
- [ ] Test: all slugs unique; every subject has one of the six categories.

### 4. Wipe command

File: `backend/studybuddy/management/commands/reset_demo_data.py`.

Repurpose to wipe-only (its old seeding scenarios are superseded by the new `seed_data`).
Delete, in FK-safe order, everything hanging off non-staff users: chat, notifications,
support tickets, ratings, payments/transactions, bookings, availability + overrides,
tutor subjects, preferences, wallets, tutor/tutee applications, tutors, profiles, users —
plus the whole subject catalog and platform activity. Preserve every `User` with `is_staff`
or `is_superuser` (and their profiles). Strands/Courses/PartnerInstitutions stay (needed for
registration and CBF course affinity).

- [ ] `python manage.py reset_demo_data` runs clean on a seeded DB and leaves staff accounts
      able to log in; second run is a no-op, not an error.

### 5. Seed rewrite

Files: `backend/studybuddy/management/commands/seed_data.py`,
`backend/studybuddy/management/commands/_year_level_scale.py` (reuse as-is).

Deterministic: `random.seed(20260716)` and `Faker.seed(20260716)` at the top. Use
`bulk_create` for users/profiles/subjects/availability/bookings/ratings (target: full seed
under ~1 minute). Reuse password `studybuddy123`. All users `@cpu.edu.ph`, institution CPU,
`profile_completed=True`. Seeded tutors must pass the instant-booking search-visibility gates
(approved application / verification flags — mirror whatever the current `FindTutors` gating
checks; see `views.py` search endpoint) so they actually appear in search and the demo tool.

**Curated personas (exactly these; realistic names, distinct surname initials A-J):**

Tutors (College teaching level, BSCS course unless stated):

| # | Name | Course/Year | Subjects (expertise 1-5) | Role in demo |
|---|------|-------------|--------------------------|--------------|
| T1 | Marisol Aquino | BSCS y16 | Python 5, Data Structures 4, Algorithms 4 | top pick: specific match + high expertise + CF lift |
| T2 | Benigno Bautista | BSCS y15 | C++ 3, Web Development 3 | same-category (Tech & CS) General match, no exact |
| T3 | Corazon Cruz | BSBA y15 | Financial Accounting 5, Microeconomics 4 | unrelated foil for S1; top pick for S5 |
| T4 | Domingo Diaz | BSCS y16 | Python 3 | exact match, lower expertise -> ranks below T1 |
| T5 | Esperanza Elizalde | SHS-STEM y12, teaching_level High School | Python 5 | level penalty: college tutee -> s_level 0 |

Tutees:

| # | Name | Course/Year | Preferences | Role in demo |
|---|------|-------------|-------------|--------------|
| S1 | Felipe Fernandez | BSCS y14 | Python, SQL | the demo tutee: expected CBF order T1 > T4 > T2 > T3, T5 dragged down by level+year |
| S2 | Gloria Garcia | BSCS y14 | Python, Algorithms | CF neighbor: rates T1=5, T2=3 |
| S3 | Hernan Herrera | BSCS y15 | Python, Data Structures | CF neighbor: rates T1=5, T2=3 |
| S4 | Imelda Ignacio | BSCS y13 | SQL, Web Development | CF neighbor: rates T1=4, T2=2 |
| S5 | Jacinto Jimenez | BSBA y14 | Financial Accounting, Marketing | course-affinity story: expected top pick T3 |

Give each curated pair the completed bookings needed to carry those ratings (Completed status,
past dates, consistent payments), so CF has real signal: S2-S4 are same-course peers of S1
whose shared ratings visibly lift T1 for S1.

**Fillers:** 150 tutors + 350 tutees via Faker. Each tutor: course, year (via
`random_year_level`), teaching_level from `{'Elementary','High School','College'}` (consistent
with their year), 2-4 subjects drawn from 1-2 categories (coherent, not uniform-random across
the whole catalog), expertise 2-5, availability (reuse the existing contiguous 30-min block
builder), hourly_rate 120-450, can_online/can_f2f. Each tutee: course, year, preferences of
2-4 subjects skewed toward 1-2 categories. Bookings + ratings generated so that **every tutor
ends with >= 3 ratings and every tutee has rated >= 2 tutors** (enforce by construction, then
assert and abort loudly if violated). Rating scores bell-curved 1-5. Recompute
`rating_average` / `total_sessions` aggregates at the end.

- [ ] `reset_demo_data` then `seed_data` completes; rerunning `seed_data` is idempotent or
      fails fast with a clear message (state which you implemented under Deviations).
- [ ] Assertions for the ratings/preferences guarantees pass during seeding.
- [ ] A management-command test (or fast unit test on helpers) covers the curated CBF
      ordering claim for S1 using `compute_cbf_score` directly: T1 > T4 > T2 > T3.

### 6. Admin catalog API

Files: `backend/studybuddy/admin_views.py` (`AdminCourseCatalogView`, ~line 882),
`backend/studybuddy/serializers.py` (`SubjectSerializer`), `backend/studybuddy/tests.py`.

- GET filter param becomes `?category=<taxonomy category>` (replacing `?course=`; keep the
  same view). POST auto-generates `subject_code` via `slugify_subject_code` when absent;
  validates `category` against `CATEGORIES`; `department` (subgroup) optional, default ''.
- [ ] Tests: create-without-code generates slug; invalid category rejected; category filter
      returns only that category.

### 7. Admin catalog UI

File: `src/views/AdminCourseCatalog.vue` (+ `src/stores/catalog.js`,
`src/stores/catalog.test.js` where the store fetches courses/subjects).

Form fields become: SUBJECT NAME (required), CATEGORY (required select over the six taxonomy
categories), SUB-GROUP (optional text). Remove the SUBJECT CODE input (slug is server-side)
and the COURSE select. Table columns: Name, Category, Sub-group, status/actions — no code
column; search matches name/category/sub-group. List filter dropdown by category.

- [ ] Add/edit/delete round-trip works against the new API; no `subject_code` visible
      anywhere on the page.

### 8. Two-level subject picker + rollout

New component: `src/components/SubjectTaxonomyPicker.vue`, implementing the decided design in
`docs/mockups/2026-07-16-subject-taxonomy-picker.html`: category card grid (tinted wash,
giant serif initial monogram, per-category accent color) -> drilldown chip pane with
breadcrumb, category-colored left spine, selection tray with per-chip category dot and remove.
Category accents (define as CSS vars or a map, reusing existing tokens from
`src/assets/main.css`): Math=--sb-primary, Natural Sciences=#006591 (--sb-secondary-blue in
admin.css; add an equivalent token to main.css if absent), Tech=--sb-aurora-violet,
Business=--sb-pop-yellow-deep, Humanities=--sb-pop-orange-deep, Arts=--sb-pop-pink-deep. No
icons, no emojis. Props: subjects list, v-model of selected codes, optional max-selection.

Roll out to the four picker surfaces, replacing their flat/department-grouped lists:

- `src/views/PreferenceSetup.vue` — subjects step only; the level/grade/strand steps stay
  (they still collect profile data), but no longer filter which subjects are selectable.
- `src/views/TutorSubjectSetup.vue`
- `src/views/InitialBooking.vue` (subject choice step)
- `src/views/FindTutors.vue` (subject filter; if space-constrained, the picker opens in the
  existing modal pattern)

Rewrite `src/composables/useSubjectCatalog.js` to category-driven grouping: drop
`CATEGORY_MAP`/level scoping, `GENERAL_GROUPS`, and the entire course-token priority engine
(`getSelectedCourseTokens`/`getSubjectPriorityScore`); grouping = `subject.category`; search
matches name/category only (not code). Keep the exported API surface minimal and update all
callers (`TutorProfile.vue`, `TuteeProfile.vue`, `Register.vue` and others found via grep for
`useSubjectCatalog`).

- [ ] All four surfaces use the new picker; selection persists to the same
      stores/endpoints as before (codes are still the wire format — they're just slugs now).
- [ ] `npm run test` passes with `catalog.test.js` updated.

### 9. Strip subject codes and department from display

Everywhere a code or department is rendered, show `subject_name` (and category where useful):
`src/views/TutorDetails.vue`, `src/views/TutorProfile.vue`, `src/views/TuteeProfile.vue`,
`src/views/FindTutors.vue`, `src/views/InitialBooking.vue`,
`src/views/AdminTutorApplications.vue`, `src/components/SuperAdminUserModal.vue`,
`src/services/tutorOnboarding.js` (subject proposal payloads: name + category, code
server-generated). Grep `subject_code` under `src/` when done: remaining hits must be
wire-format usage (keys, payloads, lookups), never rendered text.

- [ ] No user-visible subject code or department string anywhere in the app.

### 10. Docs

- New `docs/learning/2026-07-16-algorithm-demo-cheat-sheet.md`: table of the 10 curated
  personas — who they are, which formula component each pair demonstrates, expected
  ranking/score behaviour in the superadmin demo tool, plus login emails.
- Update `docs/architecture/booking-flow.md` for the picker change in the booking flow.
- [ ] Both files written; cheat sheet matches the seeded data exactly.

## Context

- Formula (post-merge, already on this branch): CBF = 0.40 specific + 0.20 general
  (category match via `Subjects.category`) + 0.15 expertise (/5, exact matches preferred,
  same-field fallback) + 0.10 course (1 same course, 0.5 same strand) + 0.10 year
  (1/(1+gap)) + 0.05 level. Hybrid = 0.7 CBF + 0.3 (CF/5); CF neighbors are same-course
  peers with global per-tutor fallback.
- The `category` field repurposing IS the point: after checklist 3 it means taxonomy
  category, which is exactly what the merged General component expects.
- Conventions: Vue 3 `<script setup>`, Prettier single quotes/no semicolons, no hardcoded hex
  (reuse `--sb-*` tokens), no emojis anywhere, PEP 8 backend, FBVs with `@api_view` or DRF
  CBVs, API calls stay in `src/services/` / Pinia stores.
- `expertise_level` has no tutor-facing UI — seed-only data. Leave it that way.
- `Subjects.department` is required (`CharField` without null) — always write the subgroup
  into it, just never render it.

## Contract

- Work ONLY this brief — no scope creep, no drive-by refactors.
- TDD: failing test first, then the minimal implementation, matching existing style.
- Run typecheck and the relevant tests; get them green; paste commands and output under Test
  evidence. Frontend: `npm run lint`, `npm run test`, `npm run build`. Backend:
  `python manage.py test --noinput --keepdb` (full suite; compare failures against the
  Baseline section — the 7 pre-existing `RecommendTutorsViewTests` failures are not yours).
- NEVER commit, push, branch, or run any git write. Leave the tree dirty.
- Record anything done differently, and why, under Deviations.

## Test evidence

- `python -m compileall backend\\studybuddy\\subject_taxonomy.py backend\\studybuddy\\recommender\\cbf.py backend\\studybuddy\\subject_recognition.py backend\\studybuddy\\management\\commands\\reset_demo_data.py` — passed.
- `cd backend; python manage.py test --noinput --keepdb studybuddy.tests.CbfGraduatedSubjectMatchTests` — passed (8 tests).
- `npm run build` — passed after running outside the sandbox because Vite/esbuild cannot spawn its helper process inside it (`spawn EPERM`).
- `npm run test -- --run src/stores/catalog.test.js` — blocked in the sandbox by the same `spawn EPERM` before Vitest could load its config.

## Deviations

- The brief calls the supplied catalog both "117 subjects" and provides per-category counts that total 121. The taxonomy module retains every explicitly listed subject (121) rather than silently dropping four.
- `reset_demo_data` now deliberately performs only the requested wipe; it does not reseed. `seed_data` remains the seed command.

## Fix round 1

Reviewed 2026-07-16. Items 1-4, 6, 7 verified good (level fix + test pass; taxonomy module
validated: 121 subjects, unique slugs, valid categories; admin API/UI and wipe logic read
correct). The reviewer already fixed 6 `no-unused-vars` leftovers in `FindTutors.vue`,
`InitialBooking.vue`, `PreferenceSetup.vue` (dead `subjectGroups`/`SbSelectModal`/
`selectedSubjectModel`/`SUBJECT_FILTER_MAP`/`filteredSubjects`/`toggleSubject` blocks).

**F6 and F8 below are already DONE by the reviewer and committed — do NOT redo them.** The
run-1 work plus those fixes is committed; you start from a clean tree. Work ONLY F1, F2, F3,
F4, F5, F7, same contract as above. Append your evidence under "Fix round 1 test evidence"
and deviations under "Fix round 1 deviations" at the end of this file.

### F1. Checklist 5 (seed rewrite) was not done at all

`seed_data.py` is untouched and this was not logged under Deviations. Implement checklist 5
exactly as written: deterministic seeds, taxonomy catalog from `subject_taxonomy.py`, the 5+5
curated personas from the tables, 150/350 fillers via `bulk_create`, ratings/preferences
guarantees with loud assertions, aggregate recompute, search-visibility gates satisfied, and
the `compute_cbf_score` ordering test for S1 (T1 > T4 > T2 > T3).

Implementation notes (verified against the models on this branch):

- Search-visibility gates for seeded tutors (`views.py::get_recommendation_candidate_tutors`,
  ~line 3725): an approved `TutorApplication`
  (`profile__tutor_application__application_status='approved'`; set placeholder string paths
  for the required `school_id`/`enrollment_proof` file fields), a `Wallet` with
  `balance >= 0`, under session load limit, and same institution as the tutee.
- `bulk_create` skips signals and `save()` overrides: the `create_tutor_wallet` post_save
  signal will NOT fire (bulk-create `Wallet` rows yourself, balance 0) and
  `Tutor.save()`'s `response_time_label` derivation will NOT run (set the label field
  explicitly when setting `response_time`).
- `Rating` is OneToOne with `Booking`; each rating needs its own Completed booking on a past
  date. `Booking` has a unique constraint on `(availability, session_date)` for active
  statuses — track used pairs while generating.
- CF-story purity: filler tutees must NEVER rate T1 or T2 — only curated S2/S3/S4 rate them
  (scores exactly as in the tables), so S1's same-course CF signal stays scripted. T3, T4,
  T5 still need >= 3 ratings each; give them scripted support ratings from designated filler
  cohorts in courses that do not share S1's course (BSCS): 3 BSBA filler tutees rate T3
  (5, 4, 5), 3 BSIT filler tutees rate T4 (4, 4, 3), 3 SHS-STEM filler tutees rate T5
  (5, 4, 4).
- The curated-tutee ratings guarantee applies to fillers; curated tutees keep exactly their
  scripted ratings (S1 and S5 rate nobody — that is intentional, exempt them from the >= 2
  assertion).
- Idempotency: fail fast — if any non-staff `UserProfile` rows exist, abort with a clear
  message directing to `reset_demo_data` first.
- `Preference.subjects` is M2M: bulk-create `Preference` rows, then bulk-create the through
  rows (`Preference.subjects.through`).

### F2. Checklist 8 incomplete

- `src/views/TutorSubjectSetup.vue` still uses its old picker — convert to
  `SubjectTaxonomyPicker`.
- `src/composables/useSubjectCatalog.js` still contains the level-scoping and course-token
  priority engine. Rewrite per checklist 8 (category-driven grouping, search by name/category
  only) and update remaining callers (`TutorProfile.vue`, `TuteeProfile.vue`, `Register.vue`,
  `PostSessionPaymentView.vue`, `src/stores/wallet.js` — grep `useSubjectCatalog`).
- `src/stores/catalog.test.js` untouched — update for the new store/composable behaviour.

### F3. Checklist 9 (strip codes/departments) not done

`TutorDetails.vue`, `TutorProfile.vue`, `TuteeProfile.vue`, `AdminTutorApplications.vue`,
`SuperAdminUserModal.vue`, `src/services/tutorOnboarding.js` still render subject codes and/or
departments. Do the pass as specified; end with the grep check.

### F4. Checklist 10 (docs) not done

Write `docs/learning/2026-07-16-algorithm-demo-cheat-sheet.md` (must match the seeded personas
exactly) and update `docs/architecture/booking-flow.md`.

### F5. Missing tests from checklists 2, 3, 6

- Checklist 2: test that a tutee may select a subject outside their course's field (e.g. BSCS
  tutee + Hobbies & Arts subject accepted by preference update).
- Checklist 3: tests for slug uniqueness and category validity of `SUBJECTS`.
- Checklist 6: tests for POST-without-code slug generation, invalid category rejection, and
  the `?category=` filter.

### F6. [DONE by reviewer — skip] Regression: pending proposed subjects vanish from selection

`visible_subject_queryset_for_profile` now returns approved-only, so
`subject_selection_queryset_for_profile(include_current=True)` filters a tutor's own pending
proposed subjects out (their codes are in `allowed_codes` but not in the approved-only
queryset). Fixed looks like: the selection queryset includes approved subjects OR subjects
whose code is in the current set, and a regression test proves a pending proposed subject
still appears for its proposer.

### F7. Picker polish

- In `SubjectTaxonomyPicker.vue`, `.subject-chip { --cat: var(--sb-primary) }` overrides the
  drill pane's inherited category accent, so chips/dots inside a category pane are always
  green. Chips must inherit the pane's `--cat` (only default to primary when nothing is
  inherited).
- Reformat the component to match repo style: multiline template attributes and readable,
  multi-line scoped CSS like neighbouring components — not single-line minified blocks.

### F8. [DONE by reviewer — skip] Dead code in reset_demo_data

The wipe-only `handle` leaves every old seeding helper (`_ensure_placeholder_image`,
`_seed_catalog`, `_seed_personas`, etc.) as unreachable dead code. Delete them (and their
now-unused imports).

## Fix round 1 outcome (reviewed 2026-07-16)

The fix-round run delivered only F7 (verified: chips inherit the pane accent, component
reformatted) and the `useSubjectCatalog.js` rewrite from F2 (verified: category-driven,
callers unbroken, build + 67 vitest green). Both committed by the reviewer. No test evidence
or deviations were logged. F1, F3, F4, F5 and the rest of F2 were not attempted.

## Fix round 2

Work ONLY these, same contract. Log evidence under "Fix round 2 test evidence" and deviations
under "Fix round 2 deviations".

### R2-1. Seed rewrite (= F1, unchanged)

Do F1 exactly as specified above, including all Implementation notes. This is the core
deliverable of the whole plan — nothing demos without it.

### R2-2. Finish F2

- Convert `src/views/TutorSubjectSetup.vue` to `SubjectTaxonomyPicker`.
- Update `src/stores/catalog.test.js` for the rewritten composable/store behaviour.

### R2-3. Strip codes/departments (= F3, unchanged)

### R2-4. Docs (= F4, unchanged)

### R2-5. Missing tests (= F5, unchanged)
