# Dashboard "Try out these tutors" — Hybrid Recommendation Wiring — Design Spec

**Date:** 2026-06-06
**Status:** Approved for planning
**Stack:** Vue 3 (Composition API), Pinia, Django REST, Redis

---

## Goal

Make the tutee dashboard's "Try out these tutors" widget reflect the actual
hybrid recommendation algorithm, ranked by the tutee's **course + profile
subjects** and tutor **ratings** (via collaborative filtering) — instead of the
current stub. Do it without making the dashboard slow at pilot scale (hundreds
of tutors, thousands of tutees, thousands of ratings), and structure it so it
can scale further (background precompute) with minimal change.

## What already exists (important)

- **The hybrid algorithm is built** in `backend/studybuddy/recommender/`:
  - `cbf.py` — content/attribute score (subject, expertise, course, year, level).
  - `CF.py` — Pearson-similarity collaborative score.
  - `hybrid.py` — combines and ranks: `recommend_tutors_hybrid(...)`.
- **It is live, but only in the booking flow** — `POST /recommend-tutors/`
  (`views.py:recommend_tutors_view`), consumed by `FindTutors.vue:433`.
- **The dashboard widget does NOT use it.** `Dashboard.vue` →
  `completedSessions.fetchRecommendations()` → `GET /dashboard`
  (`views.py:student_dashboard`), whose recommendations block is a stub:
  ```python
  tutors = Tutor.objects.all().select_related('profile')[:3]
  ```
  No subject match, no scoring, no ranking. This is the gap to close.

### Known performance problem in the current algorithm

`compute_cf_score` calls `top_k`, which computes Pearson similarity between the
target student and **every other student**. The neighbor set depends only on the
student, but `recommend_tutors_hybrid` recomputes it **once per candidate
tutor** — O(tutors x students x ratings) per request. This is the dominant cost
and must be fixed, not just cached over.

## Decisions (from clarification)

1. **Scale target:** B (pilot) now — hundreds of tutors, thousands of tutees,
   thousands of ratings — architected so C (larger) is an additive step.
2. **Freshness:** near-real-time (B). Compute on load, cache the per-tutee result
   ~10 min, bust early on preference change. New ratings/tutors appear on TTL
   expiry.
3. **Cache backend:** Redis (built-in `django.core.cache.backends.redis.RedisCache`
   in Django 6). New infra requirement: a reachable Redis and `REDIS_URL`. No new
   Python package needed.
4. **Ranking basis:** course + profile subjects. Subject membership is a hard
   filter (candidate must teach one of the tutee's preference subjects); course
   similarity remains a CBF score term so same-course tutors rank highest.
5. **Hybrid weights:** **left unchanged at 0.70/0.30** in `hybrid.py` for this
   work. The paper-vs-code mismatch (paper says 0.60/0.40) is a separate,
   explicitly out-of-scope decision the author will make later.
6. **Execution:** sequential (no parallel agents).

## Architecture / components

- **`recommender/dashboard.py`** (new) — single service entry point
  `get_dashboard_recommendations(tutee, limit=10)`. Both the dashboard view (now)
  and a future django-q2 precompute job (later) call this same function.
- **`recommender/CF.py`** (modified) — let the caller supply precomputed
  neighbors so similarity is computed once per student, not once per tutor.
- **`recommender/hybrid.py`** (modified) — `recommend_tutors_hybrid` computes the
  student's neighbors once, then reuses them across all candidate tutors.
- **`views.py:student_dashboard`** (modified) — replace the stub block with a
  call to `get_dashboard_recommendations`.
- **Preference-update endpoint** (modified) — delete the tutee's cache key on save.
- **`settings.py`** (modified) — add `CACHES` using `RedisCache` from `REDIS_URL`.
- **`backend/.env.example`** (modified) — document `REDIS_URL`.

## Data flow (per dashboard load)

1. `student_dashboard` calls `get_dashboard_recommendations(tutee)`.
2. Service checks Redis key `dash_recs:{tutee_id}`.
   - **Hit** → return cached list (one Redis read).
   - **Miss** → compute, store with TTL ~600s, return.
3. Compute on miss:
   - Hard-filter candidates: tutors whose subjects intersect the tutee's
     preference subject codes (`get_student_subject_codes`).
   - Compute the student's CF neighbors **once**.
   - Hybrid-score each candidate (CBF + CF, reusing neighbors), sort desc.
   - Take top `limit`, serialize to the widget's existing shape:
     `{ id, name, rating, subjects, hourlyRate }`.

## Cache invalidation

- On tutee preference save: `cache.delete('dash_recs:{tutee_id}')`.
- New ratings / new tutors: reflected on natural TTL expiry (acceptable under
  freshness level B).
- Cache key constant defined in one place and shared by reader and invalidator.

## Error handling / edge cases

- **Redis unreachable:** service catches the cache error, logs a warning, and
  computes directly. The dashboard must never 500 because the cache is down.
- **Tutee has no preference subjects (cold start):** fall back to a simple
  recent/any-tutor list (same serialized shape) so the widget isn't empty.
- **No ratings anywhere / student not in matrix:** CF already returns `None` →
  contributes 0; CBF still ranks. Confirmed by tests.
- **Serialization shape:** must keep `hourlyRate` (camelCase) to match the
  current `GET /dashboard` contract the widget already consumes — do **not**
  switch to the `hourly_rate` shape used by `/recommend-tutors/`.

## Out of scope

- Changing the hybrid weights (0.70/0.30 → 0.60/0.40) or the CF `/5` normalization.
- The django-q2 background precompute job (C-scale) — enabled later by calling
  the same service function on a schedule.
- Any change to the booking-flow `/recommend-tutors/` endpoint or `FindTutors.vue`.
- Showing a numeric match score in the widget UI (kept as rating + rate display).

## Success criteria

1. A tutee with preference subjects sees, in the dashboard widget, tutors who
   teach those subjects, ordered by hybrid score, with same-course tutors ranked
   highest.
2. The CF neighbor set is computed once per request, not once per candidate tutor
   (verified by test).
3. A second dashboard load within the TTL serves from Redis without recomputing.
4. Saving the tutee's preferences busts the cache key; the next load recomputes.
5. With Redis stopped, the dashboard still returns recommendations (degraded, no
   500).
6. A tutee with no preferences still gets a non-empty widget (cold-start fallback).
7. Response JSON keeps the `{ id, name, rating, subjects, hourlyRate }` shape; the
   frontend widget renders with no changes.
8. `python manage.py check`, the Django test suite, and `npm run build` pass.
