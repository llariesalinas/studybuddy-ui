---
title: Institution-Scoped Tutor Matching
date: 2026-06-26
status: Done
spec: ../specs/2026-06-26-institution-scoped-matching-design.md
---

## Status & Progress Summary

**Status:** Done — all tasks complete, final review approved  
**Tasks complete:** 4 / 4  
**Commits:** d54d1fb · 67ba7fe · 577637d · a70b6f3 · 19b7433  
**Tests:** 10 / 10 pass (`InstitutionScopedMatchingTests`)

# Institution-Scoped Tutor Matching Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add institution-scoping filters to all tutor recommendation and search surfaces so a tutee only ever sees tutors from their own institution.

**Architecture:** A single `filter_tutors_by_institution(queryset, student_profile)` helper in `backend/studybuddy/recommender/utils.py` is applied as the first operation at each of the three live API surfaces — `get_recommendation_candidate_tutors` in `views.py`, both the main candidate path and the fallback in `dashboard.py`, and `SearchTutorsView` in `views.py`. All infrastructure (`PartnerInstitution` model, `UserProfile.institution` FK, domain-enforced registration) already exists; this plan only adds filters.

**Tech Stack:** Django 6.0, Django REST Framework, PostgreSQL

## Global Constraints

- Backend only — no frontend changes
- Python 3.13+, Django 6.0, DRF
- No new migrations required (all model columns already exist)
- Test class name: `InstitutionScopedMatchingTests` in `backend/studybuddy/tests.py`
- Test runner: `cd backend && python manage.py test studybuddy.tests.InstitutionScopedMatchingTests`
- Full suite: `cd backend && python manage.py test`

---

## File Map

| File | Action | What changes |
|---|---|---|
| `backend/studybuddy/recommender/utils.py` | **Create** | `filter_tutors_by_institution` helper |
| `backend/studybuddy/views.py` | **Modify** | Import helper; add `student_profile` param to `get_recommendation_candidate_tutors`; update call in `recommend_tutors_view`; add `IsAuthenticated` + filter to `SearchTutorsView` |
| `backend/studybuddy/recommender/dashboard.py` | **Modify** | Import helper; add `tutee` param to `_fallback`; update `_fallback` call; filter `candidate_qs` |
| `backend/studybuddy/tests.py` | **Modify** | Add `InstitutionScopedMatchingTests` class (9 test methods) |

---

### Task 1: Core helper (`recommender/utils.py`)

**Files:**
- Create: `backend/studybuddy/recommender/utils.py`
- Test: `backend/studybuddy/tests.py` — add `InstitutionScopedMatchingTests` class with `setUp` and 2 unit tests

**Interfaces:**
- Produces: `filter_tutors_by_institution(queryset: QuerySet[Tutor], student_profile: UserProfile) -> QuerySet[Tutor]`
  - Returns `queryset.filter(profile__institution_id=institution_id)` when institution is set
  - Returns `queryset.none()` when `student_profile.institution_id` is `None`

- [ ] **Step 1: Write the failing tests**

Add at the bottom of `backend/studybuddy/tests.py`:

```python
class InstitutionScopedMatchingTests(APITestCase):
    def setUp(self):
        cache.clear()

        self.inst_a = PartnerInstitution.objects.create(
            institution_name="Central Philippine University",
            school_email_domain="cpu.edu.ph",
            is_active=True,
            contact_person="Registrar",
        )
        self.inst_b = PartnerInstitution.objects.create(
            institution_name="Western Visayas University",
            school_email_domain="wvu.edu.ph",
            is_active=True,
            contact_person="Registrar",
        )
        self.subject = Subjects.objects.create(
            subject_code="SCOPE101",
            subject_name="Scoping Test Subject",
            department="Test",
        )

        # Tutee from inst_a
        tutee_user = User.objects.create_user(
            username="scope_tutee_a", email="tutee@cpu.edu.ph", password="pass"
        )
        self.tutee = UserProfile.objects.create(
            user=tutee_user, fname="Ana", mname="", lname="Cruz",
            role="Tutee", institution=self.inst_a,
        )

        # Tutor from inst_a
        tutor_a_user = User.objects.create_user(
            username="scope_tutor_a", email="tutor_a@cpu.edu.ph", password="pass"
        )
        tutor_a_profile = UserProfile.objects.create(
            user=tutor_a_user, fname="Ben", mname="", lname="Santos",
            role="Tutor", institution=self.inst_a,
        )
        self.tutor_a = Tutor.objects.create(
            profile=tutor_a_profile, hourly_rate=250,
            can_online=True, can_f2f=True, teaching_level="SHS",
        )
        TutorSubjects.objects.create(
            tutor=self.tutor_a, subject=self.subject, expertise_level=5
        )

        # Tutor from inst_b
        tutor_b_user = User.objects.create_user(
            username="scope_tutor_b", email="tutor_b@wvu.edu.ph", password="pass"
        )
        tutor_b_profile = UserProfile.objects.create(
            user=tutor_b_user, fname="Cal", mname="", lname="Ramos",
            role="Tutor", institution=self.inst_b,
        )
        self.tutor_b = Tutor.objects.create(
            profile=tutor_b_profile, hourly_rate=250,
            can_online=True, can_f2f=True, teaching_level="SHS",
        )
        TutorSubjects.objects.create(
            tutor=self.tutor_b, subject=self.subject, expertise_level=5
        )

        # Tutor with no institution
        tutor_null_user = User.objects.create_user(
            username="scope_tutor_null", email="tutor_null@example.com", password="pass"
        )
        tutor_null_profile = UserProfile.objects.create(
            user=tutor_null_user, fname="Dan", mname="", lname="Lee",
            role="Tutor", institution=None,
        )
        self.tutor_null = Tutor.objects.create(
            profile=tutor_null_profile, hourly_rate=250,
            can_online=True, can_f2f=True, teaching_level="SHS",
        )
        TutorSubjects.objects.create(
            tutor=self.tutor_null, subject=self.subject, expertise_level=5
        )

    def _set_preferences(self, *subjects):
        pref, _ = Preference.objects.get_or_create(user=self.tutee)
        pref.subjects.set([s.subject_code for s in subjects])

    def test_helper_filters_by_institution(self):
        from .recommender.utils import filter_tutors_by_institution
        qs = filter_tutors_by_institution(Tutor.objects.all(), self.tutee)
        self.assertIn(self.tutor_a, qs)
        self.assertNotIn(self.tutor_b, qs)
        self.assertNotIn(self.tutor_null, qs)

    def test_helper_returns_empty_when_tutee_has_no_institution(self):
        from .recommender.utils import filter_tutors_by_institution
        no_inst_user = User.objects.create_user(
            username="scope_no_inst", email="noinst@test.com", password="pass"
        )
        no_inst_tutee = UserProfile.objects.create(
            user=no_inst_user, fname="No", mname="", lname="Inst",
            role="Tutee", institution=None,
        )
        qs = filter_tutors_by_institution(Tutor.objects.all(), no_inst_tutee)
        self.assertFalse(qs.exists())
```

- [ ] **Step 2: Run tests to confirm ImportError**

```
cd backend
python manage.py test studybuddy.tests.InstitutionScopedMatchingTests.test_helper_filters_by_institution studybuddy.tests.InstitutionScopedMatchingTests.test_helper_returns_empty_when_tutee_has_no_institution
```

Expected: `ImportError: cannot import name 'filter_tutors_by_institution'`

- [ ] **Step 3: Create `backend/studybuddy/recommender/utils.py`**

```python
def filter_tutors_by_institution(queryset, student_profile):
    institution_id = student_profile.institution_id
    if institution_id is None:
        return queryset.none()
    return queryset.filter(profile__institution_id=institution_id)
```

- [ ] **Step 4: Run tests to confirm they pass**

```
cd backend
python manage.py test studybuddy.tests.InstitutionScopedMatchingTests.test_helper_filters_by_institution studybuddy.tests.InstitutionScopedMatchingTests.test_helper_returns_empty_when_tutee_has_no_institution
```

Expected: `OK (2 tests)`

- [ ] **Step 5: Commit**

```
git add backend/studybuddy/recommender/utils.py backend/studybuddy/tests.py
git commit -m "feat: add filter_tutors_by_institution helper with unit tests"
```

---

### Task 2: FindTutors filter (`views.py`)

**Files:**
- Modify: `backend/studybuddy/views.py` — `get_recommendation_candidate_tutors` (~line 3252) and `recommend_tutors_view` call site (~line 3377)
- Test: `backend/studybuddy/tests.py` — add 4 test methods to `InstitutionScopedMatchingTests`

**Interfaces:**
- Consumes: `filter_tutors_by_institution` from `studybuddy.recommender.utils`
- `get_recommendation_candidate_tutors(subject, student_profile, preferred_mode=None, min_budget=None, max_budget=None, requested_date=None, start_time=None, end_time=None)` — `student_profile` added as the second positional parameter, before all keyword args
- `recommend_tutors_view` response: a flat JSON list; each item has `"id"` equal to `tutor.profile.id`

- [ ] **Step 1: Write the failing tests**

Add these 4 methods inside `InstitutionScopedMatchingTests`:

```python
def test_recommend_returns_same_institution_tutors(self):
    self.client.force_authenticate(user=self.tutee.user)
    resp = self.client.post(
        "/api/recommend-tutors/",
        {"subject": "SCOPE101"},
        format="json",
    )
    self.assertEqual(resp.status_code, 200)
    ids = {r["id"] for r in resp.data}
    self.assertIn(self.tutor_a.profile.id, ids)

def test_recommend_excludes_other_institution_tutor(self):
    self.client.force_authenticate(user=self.tutee.user)
    resp = self.client.post(
        "/api/recommend-tutors/",
        {"subject": "SCOPE101"},
        format="json",
    )
    self.assertEqual(resp.status_code, 200)
    ids = {r["id"] for r in resp.data}
    self.assertNotIn(self.tutor_b.profile.id, ids)

def test_recommend_tutee_no_institution_gets_empty_list(self):
    no_inst_user = User.objects.create_user(
        username="scope_no_inst2", email="noinst2@test.com", password="pass"
    )
    UserProfile.objects.create(
        user=no_inst_user, fname="No", mname="", lname="Inst",
        role="Tutee", institution=None,
    )
    self.client.force_authenticate(user=no_inst_user)
    resp = self.client.post(
        "/api/recommend-tutors/",
        {"subject": "SCOPE101"},
        format="json",
    )
    self.assertEqual(resp.status_code, 200)
    self.assertEqual(resp.data, [])

def test_recommend_null_institution_tutor_not_shown(self):
    self.client.force_authenticate(user=self.tutee.user)
    resp = self.client.post(
        "/api/recommend-tutors/",
        {"subject": "SCOPE101"},
        format="json",
    )
    self.assertEqual(resp.status_code, 200)
    ids = {r["id"] for r in resp.data}
    self.assertNotIn(self.tutor_null.profile.id, ids)
```

- [ ] **Step 2: Run a test to confirm current failure**

```
cd backend
python manage.py test studybuddy.tests.InstitutionScopedMatchingTests.test_recommend_excludes_other_institution_tutor
```

Expected: FAIL — `tutor_b` appears in results because no institution filter exists yet

- [ ] **Step 3: Add import to `views.py`**

In `backend/studybuddy/views.py`, find the existing recommender imports (around lines 45–52) and add:

```python
from .recommender.utils import filter_tutors_by_institution
```

- [ ] **Step 4: Update `get_recommendation_candidate_tutors` signature and first filter (views.py ~line 3252)**

Change the function definition — add `student_profile` as the second positional parameter and apply the institution filter as the first operation on `base_candidates`. Everything after `base_candidates` is unchanged:

```python
def get_recommendation_candidate_tutors(
    subject,
    student_profile,
    preferred_mode=None,
    min_budget=None,
    max_budget=None,
    requested_date=None,
    start_time=None,
    end_time=None,
):
    base_candidates = filter_tutors_by_institution(
        Tutor.objects.filter(tutorsubjects__subject__subject_code=subject),
        student_profile,
    )
    # the rest of the function body is unchanged
```

- [ ] **Step 5: Update `recommend_tutors_view` call site (views.py ~line 3377)**

Pass `student_profile` (already in scope at line 3360) to the function:

```python
candidate_qs = get_recommendation_candidate_tutors(
    subject,
    student_profile,
    preferred_mode=preferred_mode,
    min_budget=min_budget,
    max_budget=max_budget,
    requested_date=requested_date,
    start_time=start_time,
    end_time=end_time,
)
```

- [ ] **Step 6: Run the 4 tests**

```
cd backend
python manage.py test studybuddy.tests.InstitutionScopedMatchingTests.test_recommend_returns_same_institution_tutors studybuddy.tests.InstitutionScopedMatchingTests.test_recommend_excludes_other_institution_tutor studybuddy.tests.InstitutionScopedMatchingTests.test_recommend_tutee_no_institution_gets_empty_list studybuddy.tests.InstitutionScopedMatchingTests.test_recommend_null_institution_tutor_not_shown
```

Expected: `OK (4 tests)`

- [ ] **Step 7: Commit**

```
git add backend/studybuddy/views.py backend/studybuddy/tests.py
git commit -m "feat: scope recommend-tutors endpoint by institution"
```

---

### Task 3: Dashboard filter (`dashboard.py`)

**Files:**
- Modify: `backend/studybuddy/recommender/dashboard.py` — `_fallback` (~line 74) and the main candidate path in `get_dashboard_recommendations` (~line 117)
- Test: `backend/studybuddy/tests.py` — add 2 test methods to `InstitutionScopedMatchingTests`

**Interfaces:**
- Consumes: `filter_tutors_by_institution` from `.utils`
- `_fallback(tutee, limit)` — `tutee` (a `UserProfile`) added as the first parameter; was `_fallback(limit)`
- Dashboard response rows have key `"id"` equal to `tutor.profile.id` (set by `_serialize`)

- [ ] **Step 1: Write the failing tests**

```python
def test_dashboard_widget_respects_institution(self):
    from studybuddy.recommender import dashboard
    self._set_preferences(self.subject)
    data = dashboard.get_dashboard_recommendations(self.tutee)
    ids = {row["id"] for row in data}
    self.assertNotIn(self.tutor_b.profile.id, ids)
    self.assertNotIn(self.tutor_null.profile.id, ids)

def test_dashboard_fallback_respects_institution(self):
    from studybuddy.recommender import dashboard
    # tutee has no preferences set, so get_student_subject_codes returns []
    # and the code falls through to _fallback
    data = dashboard.get_dashboard_recommendations(self.tutee)
    ids = {row["id"] for row in data}
    self.assertNotIn(self.tutor_b.profile.id, ids)
    self.assertNotIn(self.tutor_null.profile.id, ids)
```

- [ ] **Step 2: Run a test to confirm current failure**

```
cd backend
python manage.py test studybuddy.tests.InstitutionScopedMatchingTests.test_dashboard_fallback_respects_institution
```

Expected: FAIL — `tutor_b` or `tutor_null` appear via the unfiltered fallback

- [ ] **Step 3: Add import to `dashboard.py`**

In `backend/studybuddy/recommender/dashboard.py`, add:

```python
from .utils import filter_tutors_by_institution
```

- [ ] **Step 4: Update `_fallback` (~line 74)**

```python
def _fallback(tutee, limit):
    qs = filter_tutors_by_institution(
        Tutor.objects.select_related("profile").prefetch_related("tutorsubjects_set__subject"),
        tutee,
    )
    return [_serialize(tutor) for tutor in qs[:limit]]
```

- [ ] **Step 5: Update the `_fallback` call site (~line 107)**

```python
data = _fallback(tutee, limit)
```

(was `_fallback(limit)`)

- [ ] **Step 6: Filter `candidate_qs` in the main path (~line 117)**

```python
candidate_qs = filter_tutors_by_institution(
    Tutor.objects.filter(
        tutorsubjects__subject__subject_code__in=subject_codes
    ).distinct(),
    tutee,
)
```

- [ ] **Step 7: Run the 2 tests**

```
cd backend
python manage.py test studybuddy.tests.InstitutionScopedMatchingTests.test_dashboard_widget_respects_institution studybuddy.tests.InstitutionScopedMatchingTests.test_dashboard_fallback_respects_institution
```

Expected: `OK (2 tests)`

- [ ] **Step 8: Commit**

```
git add backend/studybuddy/recommender/dashboard.py backend/studybuddy/tests.py
git commit -m "feat: scope dashboard recommendations by institution"
```

---

### Task 4: Search filter + auth hardening (`SearchTutorsView`)

**Files:**
- Modify: `backend/studybuddy/views.py` — `SearchTutorsView` (~line 1520)
- Test: `backend/studybuddy/tests.py` — add 1 test method to `InstitutionScopedMatchingTests`

**Interfaces:**
- Consumes: `filter_tutors_by_institution` (already imported in Task 2)
- Consumes: `IsAuthenticated` (already used throughout `views.py`, already imported)
- `SearchTutorsView` response: serialized by `TutorSearchSerializer` — each item has `"profile_id"` equal to `tutor.profile.id`

- [ ] **Step 1: Write the failing test**

```python
def test_search_tutors_respects_institution(self):
    self.client.force_authenticate(user=self.tutee.user)
    resp = self.client.get("/api/search-tutors/", {"subject": "SCOPE101"})
    self.assertEqual(resp.status_code, 200)
    ids = {r["profile_id"] for r in resp.data}
    self.assertIn(self.tutor_a.profile.id, ids)
    self.assertNotIn(self.tutor_b.profile.id, ids)
    self.assertNotIn(self.tutor_null.profile.id, ids)
```

- [ ] **Step 2: Run test to confirm failure**

```
cd backend
python manage.py test studybuddy.tests.InstitutionScopedMatchingTests.test_search_tutors_respects_institution
```

Expected: FAIL — `tutor_b` and `tutor_null` appear in results

- [ ] **Step 3: Update `SearchTutorsView` (views.py ~line 1520)**

Replace the entire class body:

```python
class SearchTutorsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        subject_code = request.query_params.get('subject')

        if not subject_code:
            return Response(
                {"error": "Subject is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        student_profile = request.user.userprofile
        tutors = filter_tutors_by_institution(
            Tutor.objects.filter(
                tutorsubjects__subject__subject_code=subject_code
            ).select_related('profile').distinct(),
            student_profile,
        )

        serializer = TutorSearchSerializer(tutors, many=True)
        return Response(serializer.data)
```

- [ ] **Step 4: Run the test**

```
cd backend
python manage.py test studybuddy.tests.InstitutionScopedMatchingTests.test_search_tutors_respects_institution
```

Expected: `OK (1 test)`

- [ ] **Step 5: Run all 9 institution tests**

```
cd backend
python manage.py test studybuddy.tests.InstitutionScopedMatchingTests
```

Expected: `OK (9 tests)`

- [ ] **Step 6: Run the full suite**

```
cd backend
python manage.py test
```

Expected: all tests pass, no regressions

- [ ] **Step 7: Commit**

```
git add backend/studybuddy/views.py backend/studybuddy/tests.py
git commit -m "feat: scope search-tutors endpoint by institution, add IsAuthenticated"
```

---

## Verification

1. `cd backend && python manage.py test studybuddy.tests.InstitutionScopedMatchingTests` — 9 tests, all pass
2. `cd backend && python manage.py test` — full suite green
3. Start dev server, log in as a CPU tutee, open FindTutors — only CPU-affiliated tutors appear
4. Confirm dashboard widget cards are also institution-scoped
5. Data-quality check before live deploy:
   ```python
   UserProfile.objects.filter(role__in=['Tutee', 'Tutor'], institution=None).count()
   ```
   Should be 0 or a known/accounted-for number. If non-zero, coordinate with the institution admin to backfill before deploying, or those accounts will immediately receive empty results.

---

## Changelog

- **2026-06-26** — Plan created from spec `2026-06-26-institution-scoped-matching-design.md`. Status set to Approved.
- **2026-06-26** — All 4 tasks implemented and reviewed via subagent-driven development. Final whole-branch review approved. Added auth regression test (10th test) and removed `tests.py.full_backup` artifact in post-review fix. Status set to Done.
