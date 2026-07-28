---
title: Subjects taxonomy reseed and recommender proof
date: 2026-07-16
status: Done
summary: Replace coded curriculum subjects with a Preply-style category taxonomy, wipe and reseed with curated + filler personas, and prove the rebalanced recommender via the algorithm demo tool.
spec: ../mockups/2026-07-16-subject-taxonomy-picker.html
---

# Subjects taxonomy reseed and recommender proof

**Status & Progress Summary** (2026-07-17): Done. After two Codex runs left the seed rewrite,
picker rollout, doc, and test items incomplete, the reviewer implemented Fix round 2 directly:
the full curated + filler seed (verified end-to-end against a real Postgres DB — S1's ranking
matches the scripted claim exactly), the remaining picker conversions, the code/department
strip, the cheat sheet and booking-flow doc, and the missing tests. A real regression was
found and fixed along the way (`SubjectListView` was silently stripping a tutor's own pending
proposed subject even with `include_current=True`). Final verification: 97 subjects-relevant
tests across 15 classes pass, with exactly 2 unrelated pre-existing failures (an avatar-upload
fixture using non-image bytes, and a `PaymentMethod` migration/test collision — both
confirmed via git blame to predate this branch). Frontend: build, lint, and 67/67 vitest all
green. See the session summary for the full breakdown.

## Goal

Answer the thesis panel's feedback: subjects must be generic (category) and specific (subject),
not institutional course codes. Reseed the platform with a Preply-inspired taxonomy and precise
personas (everyone has subjects, preferences, availability, bookings, ratings), and produce a
live-demo proof that the recommendation algorithm works.

## Decisions (from the 2026-07-16 grilling session)

1. **No schema migration ("A+").** `subject_code` stays the PK but becomes a name-derived slug
   (`organic-chemistry`). `category` holds the top-level taxonomy category; `department` quietly
   holds the Preply sub-group ("Chemistry") as internal metadata, displayed nowhere.
2. **Six categories** (SPED deliberately excluded — peer tutors cannot hold the required
   professional credentials): Math & Data Sciences, Natural Sciences, Technology & CS,
   Business & Economics, Humanities & Social Sciences, Hobbies & Arts. ~90–110 subjects total,
   covering the taxonomy as broadly as practical.
3. **Base branch:** new branch `feat/subjects-reseed` off `feat/instant-booking`, with
   `feat/recommender-weight-rebalance` merged in first (Specific 0.40 / General-by-category
   0.20 / Expertise 0.15 / Course 0.10 / Year 0.10 / Level 0.05, same-course CF peer neighbors).
4. **CBF level fix:** replace the dead `teaching_level == "SHS"` check with
   `TEACHING_LEVEL_MAX_YEAR = {'Elementary': 6, 'High School': 12, 'College': 16}` on the
   unified year scale; `s_level = 0` only when the student's year exceeds the tutor's ceiling;
   blank/unknown level is not penalized (no downward penalty by design).
5. **Course-based subject gating is retired.** `Subjects.category` currently stores a course
   code and `subject_recognition.py` gates selection by it. With the taxonomy, any student may
   select any approved subject; `UserProfile.course` keeps serving the CBF course/strand
   component and CF same-course neighborhoods only.
6. **Full wipe, admins survive:** extend `reset_demo_data` to purge all non-staff users and
   everything hanging off them plus the subject catalog; `is_staff`/`is_superuser` accounts are
   preserved.
7. **Seed population:** fixed random seed (reproducible). ~10 curated personas with realistic
   Filipino names (distinct surname initials) engineered so every formula component has a
   demonstrable pair: specific > general > unrelated ranking, expertise tiebreak, course/strand
   affinity, year proximity, level penalty, and a same-course CF lift story. Plus ~150 filler
   tutors and ~350 filler tutees via Faker + `bulk_create`, each guaranteed a course, year
   level, category-coherent subjects, availability, bookings, and ratings (every tutor >= 3
   received, every tutee >= 2 given). Expertise on a 1–5 scale (seed-only; no tutor-facing UI
   sets it — known gap, deliberately out of scope).
8. **Proof deliverable:** the superadmin algorithm demo tool is the exhibit, backed by a private
   cheat-sheet doc mapping each curated persona to what it demonstrates and its expected rank.
   (Automated known-answer ranking tests were considered and descoped by decision.)
9. **Frontend:** remove all visible subject codes and department groupings. Subject pickers
   become the decided two-level drilldown (category cards with tinted wash + serif monogram,
   category accent colors carried onto chips/tray — see spec mockup) across `PreferenceSetup`,
   `TutorSubjectSetup`, `InitialBooking`, and `FindTutors`.
10. **Admin catalog redesign:** the add/edit subject form becomes name + category select (6
    taxonomy values) + optional sub-group; the slug is auto-generated; the COURSE select and
    required department input are removed; the admin list's `?course=` filter becomes a
    category filter.

## Steps

1. Create `feat/subjects-reseed` off `feat/instant-booking`; merge
   `feat/recommender-weight-rebalance` and resolve conflicts (recommender, demo tool, docs).
2. Apply the CBF level fix (decision 4) in `recommender/cbf.py`, mirrored in the demo tool's
   breakdown; sync the recommender explainer docs.
3. Retire subject gating (decision 5): collapse `subject_recognition.py` to "all approved
   subjects selectable", drop the recognized-codes filter from `get_student_subject_codes`,
   and update its callers (views, serializers, admin views).
4. Author the taxonomy catalog as a data module (slug, name, category, sub-group) used by both
   the seed and any validation.
5. Extend `reset_demo_data` for the full wipe (decision 6).
6. Rewrite `seed_data`: catalog, curated personas, filler population, bookings, ratings,
   preferences, availability, aggregate recomputation — `bulk_create` throughout, seeded RNG.
7. Backend API adjustments: admin catalog endpoints (category filter, auto-slug on create),
   subject serializers/views that expose or expect codes.
8. Admin catalog UI redesign (decision 10).
9. Two-level picker component + rollout to the four picker screens; strip code/department
   display everywhere else (`TutorDetails`, profiles, application review, chat surfaces).
10. Write the demo cheat sheet (`docs/` private exhibit doc) and update
    `docs/architecture/booking-flow.md` for the picker changes.
11. Run all checks; update this plan's status and write the session summary.

## Risks

- The rebalance merge may conflict with instant-booking-era changes to views/serializers.
- Hidden dependents on `category`-as-course beyond `subject_recognition` and the admin catalog
  (search before repurposing; grep for `category` across backend and stores).
- `PreferenceSetup`'s education-level/grade/strand steps currently feed the gating; with gating
  gone they remain as profile data collection, but the subjects step must not regress the
  onboarding completion flow.
- Seed runtime at 500 users if `bulk_create` is skipped anywhere (target: under ~1 minute).
- Existing bookings/chat referencing deleted subjects after the wipe — the wipe must cascade
  cleanly (FK integrity), verified by clicking through booking history as an admin afterwards.

## Checks to run

- `python manage.py test` — backend suite passes (recommender tests updated for new weights
  and level fix).
- `python manage.py reset_demo_data && python manage.py seed_data` — completes, reruns
  idempotently, and finishes in reasonable time.
- Manual: superadmin algorithm demo shows curated tutees' expected rankings per the cheat
  sheet; booking flow end-to-end with a curated tutee; admin catalog add/edit round-trip.
- `npm run lint` and `npm run build` — clean.

## Changelog

- 2026-07-16: Plan created and approved from the grilling session; picker mockup decided and
  linked as spec.
- 2026-07-16: Step 1 executed (branch + clean rebalance merge, baseline test run recorded);
  steps 2-10 compiled into the Codex brief; status moved to In Progress.
- 2026-07-16: Codex run 1 reviewed. Verified independently (recommender classes: same 7
  baseline failures only, new level test passes; vitest 67 pass; build green). Reviewer fixed
  6 lint leftovers; Fix round 1 appended to the brief (8 findings, F1-F8).
- 2026-07-16: Reviewer fixed F6 (pending proposed subjects stay selectable) and F8 (wipe-only
  reset_demo_data, 1104 -> 38 lines); run-1 work committed in three stops.
- 2026-07-16: Codex fix-round run reviewed: only F7 + useSubjectCatalog rewrite delivered
  (verified: build green, 67 vitest pass, lint clean; committed). No evidence logged by
  Codex. Fix round 2 appended (R2-1 through R2-5).
- 2026-07-17: Fix round 2 implemented directly (seed rewrite, TutorSubjectSetup conversion,
  code/department strip, cheat sheet + booking-flow doc, missing tests); found and fixed a
  real regression in `SubjectListView`'s pending-subject handling; fixed a taxonomy-unrelated
  test broken by the earlier category-validation change; verified 97 relevant tests pass with
  only 2 confirmed-unrelated pre-existing failures; marked Done.
