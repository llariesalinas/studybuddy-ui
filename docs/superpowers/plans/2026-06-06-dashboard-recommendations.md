# Dashboard Recommendations Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the tutee dashboard's "Try out these tutors" widget rank tutors with the existing hybrid recommender (course + profile subjects + ratings), cached in Redis, without slowing the dashboard.

**Architecture:** A single service function `get_dashboard_recommendations(tutee)` in `recommender/dashboard.py` is the one entry point. It hard-filters candidate tutors to those teaching the tutee's preference subjects, scores them with `recommend_tutors_hybrid`, caches the serialized result per tutee in Redis (cache-aside, ~10 min TTL), and the dashboard view returns it in the JSON shape the Vue widget already consumes. The CF neighbor computation is hoisted out of the per-tutor loop so the live (uncached) path is also fast.

**Tech Stack:** Django 6 REST, Django cache framework with the built-in `RedisCache` backend (LocMemCache fallback when `REDIS_URL` is unset), existing `recommender/` package (CBF + Pearson CF + hybrid).

---

## Status & Progress Summary

**Status:** Done — implemented via subagent-driven development, all 6 code tasks committed; verification green for this feature.
**Spec:** `docs/superpowers/specs/2026-06-06-dashboard-recommendations-design.md`
**Summary:** `docs/session-summaries/2026-06-06-dashboard-recommendations-summary.md`
**Tasks:** 7 (sequential, TDD; no parallel agents per author)

| # | Task | State | Commit |
|---|------|-------|--------|
| 1 | CF accepts precomputed neighbors | ☑ done | `4216032` |
| 2 | Hybrid computes neighbors once (+ no-ratings guard) | ☑ done | `82b7ef6` |
| 3 | Redis cache config + `REDIS_URL` (LocMem fallback) | ☑ done | `20f2905` |
| 4 | Dashboard recommendation service (cache-aside) | ☑ done | `367bfa8` |
| 5 | Wire `student_dashboard` to the service | ☑ done | `604ea6e` |
| 6 | Bust cache on preference change (both endpoints) | ☑ done | `63be320` |
| 7 | Full verification (check, tests, build) | ☑ done | — |

**Verification:** `manage.py check` PASS · `npm run build` PASS · full backend suite
76/78 (the 2 non-passing are pre-existing `EmailAuthTests` password-reset failures from
the separate `feat(email)` async refactor — `mail.outbox` empty; unrelated to this
feature). All recommendation/dashboard tests pass.

**Notes for the executor:**
- This plan's commit steps cover **code only**. Do NOT commit `docs/` — it is gitignored and the author chose to keep planning docs local.
- Commit messages use Conventional Commits with **no AI signature** (no `Co-Authored-By`, no "Generated with" footer) per the author's global instructions.
- The hybrid weights stay `0.70 / 0.30`. Do not change them — the paper-vs-code weight decision is explicitly out of scope.
- Run backend commands from the `backend/` directory (where `manage.py` lives).

---

### Task 1: Let CF accept precomputed neighbors

Hoist the student-only neighbor computation so it can be done once and reused. `compute_cf_score` gains an optional `neighbors` argument; when provided it skips `top_k`. Fully backward compatible (default `None` recomputes as before).

**Files:**
- Modify: `backend/studybuddy/recommender/CF.py`
- Test: `backend/studybuddy/tests.py`

- [ ] **Step 1: Write the failing test**

Add this class at the end of `backend/studybuddy/tests.py`:

```python
class RecommenderNeighborReuseTests(APITestCase):
    def setUp(self):
        # student 1 is our target; students 2 and 3 are potential neighbors.
        self.ratings = {
            1: {10: 5, 11: 4},
            2: {10: 4, 11: 5, 12: 3},
            3: {10: 2, 11: 1, 12: 5},
        }

    def test_compute_cf_score_uses_supplied_neighbors(self):
        from studybuddy.recommender import CF

        neighbors = CF.top_k(self.ratings, 1)

        with patch.object(CF, "top_k") as mocked_top_k:
            score = CF.compute_cf_score(
                self.ratings, 1, 12, neighbors=neighbors
            )

        mocked_top_k.assert_not_called()
        self.assertIsNotNone(score)

    def test_compute_cf_score_matches_with_and_without_neighbors(self):
        from studybuddy.recommender import CF

        neighbors = CF.top_k(self.ratings, 1)

        without = CF.compute_cf_score(self.ratings, 1, 12)
        with_neighbors = CF.compute_cf_score(self.ratings, 1, 12, neighbors=neighbors)

        self.assertEqual(without, with_neighbors)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python manage.py test studybuddy.tests.RecommenderNeighborReuseTests.test_compute_cf_score_uses_supplied_neighbors -v 2`
Expected: FAIL with `TypeError: compute_cf_score() got an unexpected keyword argument 'neighbors'`.

- [ ] **Step 3: Add the `neighbors` parameter**

In `backend/studybuddy/recommender/CF.py`, replace the `compute_cf_score` definition (currently starting `def compute_cf_score(ratings, student_id, tutor_id, k=5):`) with:

```python
def compute_cf_score(ratings, student_id, tutor_id, k=5, neighbors=None):

    if student_id not in ratings:
        return None

    if neighbors is None:
        neighbors = top_k(ratings, student_id, k)

    numerator = 0
    denominator = 0

    student_avg = sum(ratings[student_id].values()) / len(ratings[student_id])

    for neighbor, similarity in neighbors:

        if tutor_id not in ratings.get(neighbor, {}):
            continue

        neighbor_avg = sum(ratings[neighbor].values()) / len(ratings[neighbor])

        numerator += similarity * (
            ratings[neighbor][tutor_id] - neighbor_avg
        )

        denominator += abs(similarity)

    if denominator == 0:
        return None

    return student_avg + (numerator / denominator)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python manage.py test studybuddy.tests.RecommenderNeighborReuseTests -v 2`
Expected: PASS (2 tests OK).

- [ ] **Step 5: Commit**

```bash
git add backend/studybuddy/recommender/CF.py backend/studybuddy/tests.py
git commit -m "refactor(recommender): let compute_cf_score accept precomputed neighbors"
```

---

### Task 2: Compute neighbors once in the hybrid loop

`recommend_tutors_hybrid` now computes the student's neighbors a single time and threads them through `hybrid_prediction` into `compute_cf_score`. Guard against the student not being in the ratings matrix (avoids a `ZeroDivisionError` from defaultdict key insertion).

**Files:**
- Modify: `backend/studybuddy/recommender/hybrid.py`
- Test: `backend/studybuddy/tests.py`

- [ ] **Step 1: Write the failing test**

Add these two methods inside `RecommenderNeighborReuseTests` (from Task 1):

```python
    def test_recommend_hybrid_computes_neighbors_once(self):
        from studybuddy.recommender import hybrid

        # three candidate tutors, but neighbors should be computed only once
        tutors = [Mock(profile_id=i, tutorsubjects_set=Mock()) for i in range(3)]
        for t in tutors:
            t.tutorsubjects_set.all.return_value = []

        student_profile = Mock(id=1, course=None, year_level=None)

        with patch.object(hybrid, "top_k", return_value=[]) as mocked_top_k, \
             patch.object(hybrid, "get_student_subject_codes", return_value=[]), \
             patch.object(hybrid, "compute_cbf_score", return_value=0.0), \
             patch.object(hybrid, "normalize_tutor_queryset", return_value=tutors):
            hybrid.recommend_tutors_hybrid(self.ratings, student_profile, None)

        self.assertEqual(mocked_top_k.call_count, 1)

    def test_recommend_hybrid_handles_student_with_no_ratings(self):
        from studybuddy.recommender import hybrid

        tutor = Mock(profile_id=99, tutorsubjects_set=Mock())
        tutor.tutorsubjects_set.all.return_value = []
        student_profile = Mock(id=4242, course=None, year_level=None)  # not in ratings

        with patch.object(hybrid, "get_student_subject_codes", return_value=[]), \
             patch.object(hybrid, "compute_cbf_score", return_value=0.5), \
             patch.object(hybrid, "normalize_tutor_queryset", return_value=[tutor]):
            results = hybrid.recommend_tutors_hybrid(self.ratings, student_profile, None)

        self.assertEqual(len(results), 1)  # did not raise
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python manage.py test studybuddy.tests.RecommenderNeighborReuseTests.test_recommend_hybrid_computes_neighbors_once -v 2`
Expected: FAIL with `AttributeError: <module 'studybuddy.recommender.hybrid'> does not have the attribute 'top_k'` (top_k is not yet imported into hybrid).

- [ ] **Step 3: Import `top_k` and compute neighbors once**

In `backend/studybuddy/recommender/hybrid.py`, change the import line:

```python
from .CF import compute_cf_score
```

to:

```python
from .CF import compute_cf_score, top_k
```

Replace the `hybrid_prediction` function definition with this version (adds a `neighbors` parameter and passes it through):

```python
def hybrid_prediction(ratings, student_profile, tutor, requested_subject, student_subjects=None, neighbors=None):
    cbf_score = compute_cbf_score(
        student_profile,
        tutor,
        requested_subject,
        student_subjects=student_subjects,
        tutor_subjects=tutor.tutorsubjects_set.all(),
    )

    tutor_id = tutor.profile_id

    cf_score = compute_cf_score(
        ratings,
        student_profile.id,
        tutor_id,
        neighbors=neighbors,
    )

    if cf_score is None:
        cf_score = 0

    hybrid_score = (0.7 * cbf_score) + (0.3 * (cf_score / 5))

    logger.debug(
        "Hybrid score for tutor %s: CBF %.3f, CF %.3f, hybrid %.3f",
        tutor_id,
        cbf_score,
        cf_score,
        hybrid_score,
    )

    return hybrid_score
```

In `recommend_tutors_hybrid`, add the neighbor computation once before the loop and pass it in. Replace the body up to and including the loop with:

```python
def recommend_tutors_hybrid(ratings, student_profile, requested_subject, candidate_qs=None):
    tutors = normalize_tutor_queryset(candidate_qs)
    student_subjects = get_student_subject_codes(student_profile)

    student_id = student_profile.id
    neighbors = top_k(ratings, student_id) if student_id in ratings else []

    recommendations = []

    for tutor in tutors:
        score = hybrid_prediction(
            ratings,
            student_profile,
            tutor,
            requested_subject,
            student_subjects=student_subjects,
            neighbors=neighbors,
        )

        recommendations.append({
            "tutor": tutor,
            "score": score,
        })
```

Leave the rest of `recommend_tutors_hybrid` (the `sort`, the debug logging loop, the `return`) unchanged.

- [ ] **Step 4: Run tests to verify they pass**

Run: `python manage.py test studybuddy.tests.RecommenderNeighborReuseTests -v 2`
Expected: PASS (4 tests OK).

- [ ] **Step 5: Commit**

```bash
git add backend/studybuddy/recommender/hybrid.py backend/studybuddy/tests.py
git commit -m "perf(recommender): compute CF neighbors once per request, not per tutor"
```

---

### Task 3: Cache configuration (Redis with LocMem fallback)

Add a `CACHES` setting that uses Redis when `REDIS_URL` is set and an in-process cache otherwise, so dev/CI without Redis still works (degraded). Document the env var.

**Files:**
- Modify: `backend/backend/settings.py`
- Modify: `backend/.env.example`

- [ ] **Step 1: Add the `CACHES` block**

In `backend/backend/settings.py`, immediately after the `Q_CLUSTER = { ... }` block, add:

```python
# Cache backend. Redis when REDIS_URL is set (preferred: fast and shared across
# worker processes — required for correct invalidation in multi-worker prod).
# Without REDIS_URL we fall back to a per-process in-memory cache so local dev and
# CI run without a Redis server (degraded: not shared across processes).
REDIS_URL = os.getenv("REDIS_URL", "")

if REDIS_URL:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": REDIS_URL,
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        }
    }
```

- [ ] **Step 2: Document `REDIS_URL` in `.env.example`**

In `backend/.env.example`, append:

```
# Redis cache — used for dashboard recommendation caching. Optional in dev (the app
# falls back to a per-process in-memory cache when unset). Required in multi-worker
# production so the cache is shared and invalidation works across processes.
REDIS_URL=redis://127.0.0.1:6379/1
```

- [ ] **Step 3: Verify Django still boots**

Run: `python manage.py check`
Expected: `System check identified no issues (0 silenced).`

- [ ] **Step 4: Commit**

```bash
git add backend/backend/settings.py backend/.env.example
git commit -m "feat(cache): add Redis cache backend with in-memory fallback"
```

---

### Task 4: The dashboard recommendation service

The single entry point. Cache-aside read/write keyed per tutee, hard-filter to the tutee's preference subjects, hybrid-score, serialize to the widget's JSON shape, with a cold-start fallback and graceful degradation when the cache errors.

**Files:**
- Create: `backend/studybuddy/recommender/dashboard.py`
- Test: `backend/studybuddy/tests.py`

- [ ] **Step 1: Write the failing test**

Add this class at the end of `backend/studybuddy/tests.py`:

```python
class DashboardRecommendationServiceTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.subject = Subjects.objects.create(
            subject_code="IT101",
            subject_name="Intro to IT",
            department="IT",
        )
        self.other_subject = Subjects.objects.create(
            subject_code="BIO101",
            subject_name="Biology",
            department="Science",
        )
        self.student_user = User.objects.create_user(
            username="dash-student", email="dash@example.com", password="password",
        )
        self.student = UserProfile.objects.create(
            user=self.student_user, fname="Dash", mname="", lname="Student",
            role="Tutee", year_level=11,
        )

    def _make_tutor(self, username, subject):
        user = User.objects.create_user(
            username=username, email=f"{username}@example.com", password="password",
        )
        profile = UserProfile.objects.create(
            user=user, fname=username.title(), mname="", lname="Tutor",
            role="Tutor", year_level=12,
        )
        tutor = Tutor.objects.create(
            profile=profile, hourly_rate=200, can_online=True, can_f2f=False,
            teaching_level="SHS",
        )
        TutorSubjects.objects.create(tutor=tutor, subject=subject, expertise_level=5)
        return tutor

    def _set_preferences(self, *subjects):
        pref, _ = Preference.objects.get_or_create(user=self.student)
        pref.subjects.set([s.subject_code for s in subjects])

    def test_returns_only_tutors_teaching_preference_subjects(self):
        from studybuddy.recommender.dashboard import get_dashboard_recommendations

        match = self._make_tutor("itmatch", self.subject)
        self._make_tutor("biomatch", self.other_subject)
        self._set_preferences(self.subject)

        data = get_dashboard_recommendations(self.student)

        ids = {row["id"] for row in data}
        self.assertEqual(ids, {match.profile.id})

    def test_response_shape_matches_widget_contract(self):
        from studybuddy.recommender.dashboard import get_dashboard_recommendations

        self._make_tutor("itmatch", self.subject)
        self._set_preferences(self.subject)

        row = get_dashboard_recommendations(self.student)[0]

        self.assertEqual(
            set(row.keys()), {"id", "name", "rating", "subjects", "hourlyRate"},
        )

    def test_cold_start_returns_fallback_when_no_preferences(self):
        from studybuddy.recommender.dashboard import get_dashboard_recommendations

        self._make_tutor("anytutor", self.subject)
        # no preferences set

        data = get_dashboard_recommendations(self.student)

        self.assertEqual(len(data), 1)

    def test_second_call_served_from_cache_without_recompute(self):
        from studybuddy.recommender import dashboard

        self._make_tutor("itmatch", self.subject)
        self._set_preferences(self.subject)

        dashboard.get_dashboard_recommendations(self.student)  # warms cache

        with patch.object(dashboard, "recommend_tutors_hybrid") as mocked:
            dashboard.get_dashboard_recommendations(self.student)

        mocked.assert_not_called()

    def test_degrades_gracefully_when_cache_read_fails(self):
        from studybuddy.recommender import dashboard

        match = self._make_tutor("itmatch", self.subject)
        self._set_preferences(self.subject)

        with patch.object(dashboard.cache, "get", side_effect=Exception("redis down")):
            data = dashboard.get_dashboard_recommendations(self.student)

        ids = {row["id"] for row in data}
        self.assertEqual(ids, {match.profile.id})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python manage.py test studybuddy.tests.DashboardRecommendationServiceTests -v 2`
Expected: FAIL with `ModuleNotFoundError: No module named 'studybuddy.recommender.dashboard'`.

- [ ] **Step 3: Create the service module**

Create `backend/studybuddy/recommender/dashboard.py`:

```python
import logging

from django.core.cache import cache

from ..models import Tutor
from .cbf import get_student_subject_codes
from .CF import build_rating_matrix
from .hybrid import recommend_tutors_hybrid

logger = logging.getLogger(__name__)

CACHE_TTL_SECONDS = 600
DEFAULT_LIMIT = 10


def dashboard_recs_cache_key(tutee):
    return f"dash_recs:{tutee.id}"


def _serialize(tutor):
    return {
        "id": tutor.profile.id,
        "name": f"{tutor.profile.fname} {tutor.profile.lname}",
        "rating": tutor.rating_average,
        "subjects": [ts.subject.subject_name for ts in tutor.tutorsubjects_set.all()],
        "hourlyRate": tutor.hourly_rate,
    }


def _fallback(limit):
    tutors = (
        Tutor.objects.select_related("profile")
        .prefetch_related("tutorsubjects_set__subject")[:limit]
    )
    return [_serialize(tutor) for tutor in tutors]


def _cache_get(key):
    try:
        return cache.get(key)
    except Exception:
        logger.warning("Dashboard recs cache read failed", exc_info=True)
        return None


def _cache_set(key, value):
    try:
        cache.set(key, value, CACHE_TTL_SECONDS)
    except Exception:
        logger.warning("Dashboard recs cache write failed", exc_info=True)


def get_dashboard_recommendations(tutee, limit=DEFAULT_LIMIT):
    key = dashboard_recs_cache_key(tutee)

    cached = _cache_get(key)
    if cached is not None:
        return cached

    subject_codes = get_student_subject_codes(tutee)
    if not subject_codes:
        return _fallback(limit)

    candidate_qs = Tutor.objects.filter(
        tutorsubjects__subject__subject_code__in=subject_codes
    ).distinct()

    ratings = build_rating_matrix()
    ranked = recommend_tutors_hybrid(
        ratings,
        tutee,
        None,
        candidate_qs=candidate_qs,
    )

    data = [_serialize(recommendation["tutor"]) for recommendation in ranked[:limit]]

    _cache_set(key, data)
    return data
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python manage.py test studybuddy.tests.DashboardRecommendationServiceTests -v 2`
Expected: PASS (5 tests OK).

- [ ] **Step 5: Commit**

```bash
git add backend/studybuddy/recommender/dashboard.py backend/studybuddy/tests.py
git commit -m "feat(recommender): add cached dashboard recommendation service"
```

---

### Task 5: Wire the dashboard view to the service

Replace the `Tutor.objects.all()[:3]` stub in `student_dashboard` with a call to the service, keeping the exact response shape the Vue widget already consumes.

**Files:**
- Modify: `backend/studybuddy/views.py` (imports; `student_dashboard` recommendations block ~lines 1164-1188)
- Test: `backend/studybuddy/tests.py`

- [ ] **Step 1: Write the failing test**

Add this class at the end of `backend/studybuddy/tests.py`:

```python
class StudentDashboardRecommendationTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.subject = Subjects.objects.create(
            subject_code="IT201", subject_name="Data Structures", department="IT",
        )
        self.other_subject = Subjects.objects.create(
            subject_code="HIST201", subject_name="History", department="Arts",
        )
        self.student_user = User.objects.create_user(
            username="dv-student", email="dv@example.com", password="password",
        )
        self.student = UserProfile.objects.create(
            user=self.student_user, fname="Dee", mname="", lname="Vee",
            role="Tutee", year_level=11,
        )
        self.client.force_authenticate(user=self.student_user)

    def _make_tutor(self, username, subject):
        user = User.objects.create_user(
            username=username, email=f"{username}@example.com", password="password",
        )
        profile = UserProfile.objects.create(
            user=user, fname=username.title(), mname="", lname="Tutor",
            role="Tutor", year_level=12,
        )
        tutor = Tutor.objects.create(
            profile=profile, hourly_rate=200, can_online=True, can_f2f=False,
            teaching_level="SHS",
        )
        TutorSubjects.objects.create(tutor=tutor, subject=subject, expertise_level=5)
        return tutor

    def test_dashboard_recommends_subject_matched_tutors(self):
        match = self._make_tutor("itone", self.subject)
        self._make_tutor("histone", self.other_subject)
        pref, _ = Preference.objects.get_or_create(user=self.student)
        pref.subjects.set([self.subject.subject_code])

        response = self.client.get("/api/dashboard/")

        self.assertEqual(response.status_code, 200)
        ids = {row["id"] for row in response.data["recommendations"]}
        self.assertEqual(ids, {match.profile.id})
        self.assertEqual(
            set(response.data["recommendations"][0].keys()),
            {"id", "name", "rating", "subjects", "hourlyRate"},
        )
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python manage.py test studybuddy.tests.StudentDashboardRecommendationTests -v 2`
Expected: FAIL — the assertion `ids == {match.profile.id}` fails because the stub returns the first 3 tutors regardless of subject (the history tutor leaks in).

- [ ] **Step 3: Add imports**

In `backend/studybuddy/views.py`, add near the other `from .recommender...` imports (around lines 44-47):

```python
from .recommender.dashboard import get_dashboard_recommendations, dashboard_recs_cache_key
```

And ensure the Django cache is imported (add near the top imports if not already present):

```python
from django.core.cache import cache
```

- [ ] **Step 4: Replace the stub recommendations block**

In `student_dashboard` (`backend/studybuddy/views.py`), replace this block:

```python
    # -----------------------
    # RECOMMENDED TUTORS
    # -----------------------
    tutors = Tutor.objects.all().select_related('profile')[:3]

    recommendations = []

    for tutor in tutors:

        tutor_subjects = TutorSubjects.objects.filter(
            tutor=tutor
        ).select_related('subject')

        recommendations.append({
            "id": tutor.profile.id,
            "name": f"{tutor.profile.fname} {tutor.profile.lname}",
            "rating": tutor.rating_average,
            "subjects": [ts.subject.subject_name for ts in tutor_subjects],
            "hourlyRate": tutor.hourly_rate
        })
```

with:

```python
    # -----------------------
    # RECOMMENDED TUTORS (hybrid algorithm, cached per tutee)
    # -----------------------
    recommendations = get_dashboard_recommendations(user_profile)
```

Leave the `return Response({ "upcoming": upcoming, "completed": completed, "recommendations": recommendations })` unchanged.

- [ ] **Step 5: Run tests to verify they pass**

Run: `python manage.py test studybuddy.tests.StudentDashboardRecommendationTests -v 2`
Expected: PASS (1 test OK).

- [ ] **Step 6: Commit**

```bash
git add backend/studybuddy/views.py backend/studybuddy/tests.py
git commit -m "feat(dashboard): rank 'Try out these tutors' with the hybrid recommender"
```

---

### Task 6: Invalidate the cache when preferences change

Both preference-writing endpoints (`save_preferences` and `update_tutee_profile`) delete the tutee's cache key so the next dashboard load recomputes with the new subjects instead of waiting out the TTL.

**Files:**
- Modify: `backend/studybuddy/views.py` (`save_preferences` ~line 2643; `update_tutee_profile` ~line 2926)
- Test: `backend/studybuddy/tests.py`

- [ ] **Step 1: Write the failing test**

Add this method to `StudentDashboardRecommendationTests` (from Task 5):

```python
    def test_saving_preferences_busts_dashboard_cache(self):
        from studybuddy.recommender.dashboard import dashboard_recs_cache_key

        self._make_tutor("itone", self.subject)
        pref, _ = Preference.objects.get_or_create(user=self.student)
        pref.subjects.set([self.subject.subject_code])

        # warm the cache
        self.client.get("/api/dashboard/")
        self.assertIsNotNone(cache.get(dashboard_recs_cache_key(self.student)))

        # changing preferences must clear it
        response = self.client.post(
            "/api/preferences/", {"subjects": [self.subject.subject_code]},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(cache.get(dashboard_recs_cache_key(self.student)))
```

Route confirmed: `save_preferences` is registered at `preferences/` (`backend/studybuddy/urls.py:62`), so the test posts to `/api/preferences/`.

- [ ] **Step 2: Run test to verify it fails**

Run: `python manage.py test studybuddy.tests.StudentDashboardRecommendationTests.test_saving_preferences_busts_dashboard_cache -v 2`
Expected: FAIL — `cache.get(...)` is still non-None after saving preferences (no invalidation yet).

- [ ] **Step 3: Bust the cache in `save_preferences`**

In `backend/studybuddy/views.py`, in `save_preferences`, replace the return block:

```python
    if subject_ids:
        pref.subjects.set(subject_ids)

    return Response({
        "message": "Preferences saved successfully"
    })
```

with:

```python
    if subject_ids:
        pref.subjects.set(subject_ids)

    cache.delete(dashboard_recs_cache_key(profile))

    return Response({
        "message": "Preferences saved successfully"
    })
```

- [ ] **Step 4: Bust the cache in `update_tutee_profile`**

In `backend/studybuddy/views.py`, in `update_tutee_profile`, replace the return block:

```python
    if "subjects" in request.data:
        pref.subjects.set(subject_ids)

    pref.save()

    return Response({"message": "Profile updated successfully"})
```

with:

```python
    if "subjects" in request.data:
        pref.subjects.set(subject_ids)

    pref.save()

    cache.delete(dashboard_recs_cache_key(profile))

    return Response({"message": "Profile updated successfully"})
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python manage.py test studybuddy.tests.StudentDashboardRecommendationTests -v 2`
Expected: PASS (2 tests OK).

- [ ] **Step 6: Commit**

```bash
git add backend/studybuddy/views.py backend/studybuddy/tests.py
git commit -m "feat(dashboard): bust recommendation cache when tutee preferences change"
```

---

### Task 7: Full verification

Run the whole backend suite and the frontend build to confirm nothing regressed and the JSON contract still satisfies the Vue widget.

**Files:** none (verification only)

- [ ] **Step 1: Django system check**

Run (from `backend/`): `python manage.py check`
Expected: `System check identified no issues`.

- [ ] **Step 2: Full backend test suite**

Run (from `backend/`): `python manage.py test studybuddy -v 2`
Expected: all tests PASS (including the pre-existing `RecommendTutorsViewTests` and `ChatFeatureTests`), no failures or errors.

- [ ] **Step 3: Frontend build**

Run (from repo root): `npm run build`
Expected: build completes with no errors. (No frontend files changed; this confirms the dashboard widget still compiles against the unchanged `GET /dashboard` contract.)

- [ ] **Step 4: Manual smoke (optional but recommended)**

With Redis running and `REDIS_URL` set, start the backend and frontend, log in as a tutee who has preference subjects, and confirm the dashboard "Try out these tutors" widget shows subject/course-matched tutors. Change preferences and confirm the list updates on the next load.

---

## Self-Review

**Spec coverage:**
- Service entry point `get_dashboard_recommendations` → Task 4. ✓
- Neighbor-once fix in CF/hybrid → Tasks 1-2. ✓
- Redis cache backend + `REDIS_URL` env → Task 3. ✓
- Dashboard view wired, JSON shape preserved → Task 5. ✓
- Cache invalidation on preference save (both endpoints) → Task 6. ✓
- Cold-start fallback, Redis-down degradation, no-ratings safety → Tasks 2 & 4 tests. ✓
- Weights unchanged at 0.70/0.30 → preserved verbatim in Task 2. ✓
- Verification (check, tests, build) → Task 7. ✓

**Placeholder scan:** No TBD/TODO; every code step shows complete code; every command has expected output. ✓

**Type/name consistency:** `dashboard_recs_cache_key`, `get_dashboard_recommendations`, `CACHE_TTL_SECONDS`, and the `{id,name,rating,subjects,hourlyRate}` shape are used identically across Tasks 4-6. `compute_cf_score(..., neighbors=...)` and `top_k` signatures match between Tasks 1 and 2. ✓

**URL paths verified** against `backend/studybuddy/urls.py`: dashboard is `dashboard/` → `/api/dashboard/` (line 64); save_preferences is `preferences/` → `/api/preferences/` (line 62). Tests use these paths.

---

## Changelog

- **2026-06-06** — Plan created from spec `docs/superpowers/specs/2026-06-06-dashboard-recommendations-design.md`. 7 tasks (TDD, sequential). Verified URL paths against `urls.py` and corrected the preference-save test path from `/api/save-preferences/` to `/api/preferences/`. Status: Approved, ready for execution.
- **2026-06-06** — Executed via subagent-driven development. Tasks 1–6 implemented and committed (`4216032`, `82b7ef6`, `20f2905`, `367bfa8`, `604ea6e`, `63be320`); each task's TDD tests pass. Task 7 verification: `manage.py check` PASS, `npm run build` PASS, full backend suite 76/78 (the 2 failures are pre-existing `EmailAuthTests` password-reset cases from the separate email async refactor, not this feature). Prereq cleanup before execution: committed existing email/chat work as `feat(email)`/`feat(chat)`; installed `anymail`/`django-q2`/`django-picklefield` so the backend boots. Status → Done. Summary written to `docs/session-summaries/2026-06-06-dashboard-recommendations-summary.md`.
