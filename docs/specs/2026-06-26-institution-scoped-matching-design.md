# Institution-Scoped Tutor Matching — Design Spec

**Date:** 2026-06-26
**Status:** Approved for planning
**Stack:** Django REST, PostgreSQL

---

## Goal

Ensure tutees are only recommended and shown tutors from their own institution.
A CPU tutee (`cpu.edu.ph`) must never see tutors registered under a different
institution, and vice versa. The filter is a hard exclusion — no cross-institution
leakage, no soft preference fallback.

---

## What already exists (important)

The infrastructure for this feature is already fully built. This is a filter
addition, not an infrastructure build.

- **`PartnerInstitution` model** (`backend/studybuddy/models.py:36`) — `institution_name`,
  `school_email_domain`, `is_active`. Supports many institutions, not just CPU.
- **`UserProfile.institution`** — nullable FK to `PartnerInstitution` (`models.py:79`).
  Set at registration; enforced by domain-match validation in `register_user`.
- **Registration already enforces domain matching** — `get_active_institution_by_domain`
  (`views.py:100`) and `register_user` (`views.py:857`) reject any email whose domain
  does not match the selected institution's `school_email_domain`. Both tutors and
  tutees go through this flow, so in practice all active accounts should have
  `institution` set.
- **`is_domain_exempt`** (`models.py:86`) — lets Admin/SuperAdmin accounts bypass domain
  checks. These accounts are not tutors or tutees, so they are not in the recommendation
  pool and no special handling is needed.

### Recommendation surfaces (all need the filter)

| Surface | Entry point | File |
|---|---|---|
| FindTutors (`POST /recommend-tutors/`) | `recommend_tutors_view` | `views.py:3358` |
| Dashboard widget (`GET /dashboard-recommendations/`) | `get_dashboard_recommendations` | `recommender/dashboard.py:90` |
| Search fallback (`GET /search-tutors/`) | `SearchTutorsView` | `views.py:1520` |

`SearchTutorsView` has no current frontend caller, but is a live authenticated
API endpoint and must be filtered to prevent cross-institution leakage via direct
API calls.

---

## Scalability: single database vs per-institution databases

**Keep the single-database multi-tenant model.** No per-institution databases.

The current architecture already achieves multi-tenancy correctly: `PartnerInstitution`
is a first-class table, every user carries an `institution_id` FK, and admin/reporting
tooling is already scoped to it (`AdminInstitutions.vue`, `SuperAdminReports.vue`,
`PlatformActivity.institution`). Adding more institutions means adding rows to
`partner_institutions`, not provisioning new infrastructure.

Per-institution databases would only make sense if:
- A legal or compliance requirement mandates that one institution's data must be
  physically isolated (e.g. data residency law, contractual data sovereignty clause).
- A single institution grew so large it caused measurable noisy-neighbour performance
  problems for others — not a concern at current or foreseeable pilot scale.
- Institutions needed fully independent backup/restore cycles.

None of these apply now. Re-evaluate if a contract ever requires data residency
isolation for a specific institution.

---

## Design

### Core helper

Add one helper function in a new file `backend/studybuddy/recommender/utils.py`.
Both `views.py` and `dashboard.py` import from there:

```python
def filter_tutors_by_institution(queryset, student_profile):
    institution_id = student_profile.institution_id
    if institution_id is None:
        return queryset.none()
    return queryset.filter(profile__institution_id=institution_id)
```

- Returns an empty queryset immediately when the tutee has no institution set,
  rather than returning all tutors or raising an error. The caller handles the
  empty result normally (empty response, no tutors shown).
- `profile__institution_id` uses the FK id directly to avoid an extra JOIN.
- No tutor with `profile__institution_id = None` can match any tutee (SQL
  `NULL = value` is never true), so null-institution tutors are automatically
  excluded without an extra condition.

### Call sites

**1. `get_recommendation_candidate_tutors` (views.py:3252)**

Import `filter_tutors_by_institution` from `studybuddy.recommender.utils`.
Add `student_profile` as a new parameter (currently takes only filter inputs).
Apply `filter_tutors_by_institution` as the first filter on `base_candidates`
before subject/mode/budget/availability filters.

```python
def get_recommendation_candidate_tutors(
    subject,
    student_profile,       # new
    preferred_mode=None,
    ...
):
    base_candidates = filter_tutors_by_institution(
        Tutor.objects.filter(tutorsubjects__subject__subject_code=subject),
        student_profile,
    )
    ...
```

**2. `recommend_tutors_view` (views.py:3377)**

Pass `student_profile` (already in scope at line 3360) to the candidate
function call.

**3. `dashboard.py::get_dashboard_recommendations` (recommender/dashboard.py:90)**

Two locations:

- `candidate_qs` (line 117): chain `filter_tutors_by_institution(candidate_qs, tutee)`
  after the subject filter.
- `_fallback` (line 74): apply the same filter on the fallback queryset. If the
  tutee has no institution, the fallback also returns empty — this is correct, as
  showing random cross-institution tutors would violate the goal.

Import `filter_tutors_by_institution` from `.utils` (`recommender/utils.py`).

**4. `SearchTutorsView` (views.py:1520)**

Apply `filter_tutors_by_institution` on the `tutors` queryset. The view has no
`request.user` reference currently — add it and resolve the profile:

```python
student_profile = request.user.userprofile
tutors = filter_tutors_by_institution(
    Tutor.objects.filter(...),
    student_profile,
)
```

Also confirm `IsAuthenticated` permission is set on this view (it currently has
no explicit `permission_classes` — add it to be explicit and safe).

---

## Null institution handling

| State | Outcome |
|---|---|
| Tutee has `institution = None` | `filter_tutors_by_institution` returns `.none()` — empty recommendation list. Admin must assign the tutee's institution before they can match. |
| Tutor has `profile__institution = None` | Never matched (SQL null-equality). Invisible to all tutees until an admin assigns their institution. |

An admin data-quality check is worth running before deploying: count
`UserProfile.objects.filter(role__in=['Tutee','Tutor'], institution=None)`.
If non-zero, coordinate with the institution admin to backfill before turning
the filter on — otherwise those users immediately get empty results.

---

## Dead code note

Both `cbf.py::recommend_tutors` (line 106) and `CF.py::recommend_tutors_cf`
(line 123) are standalone entry points with zero callers, superseded by the
hybrid pipeline. They do not need the institution filter (nothing calls them)
and are out of scope for this plan. Remove them in a separate cleanup.

---

## Tests to add (`backend/studybuddy/tests.py`)

New test class `InstitutionScopedMatchingTests`:

1. Tutee sees only same-institution tutors via `POST /recommend-tutors/`.
2. Tutor from a different institution does not appear in results.
3. Tutee with `institution=None` gets an empty list (not an error).
4. Tutor with `institution=None` never appears in any tutee's results.
5. Dashboard widget (`GET /dashboard-recommendations/`) respects institution.
6. Dashboard fallback (no subject prefs) also respects institution.
7. `GET /search-tutors/` returns only same-institution tutors.

---

## Verification

1. Run `python manage.py test studybuddy.tests.InstitutionScopedMatchingTests`
   — all 7 cases pass.
2. Run `python manage.py test` — full suite still green.
3. Start dev server (`python manage.py runserver`), log in as a CPU tutee,
   open FindTutors — confirm only CPU-affiliated tutors appear.
4. Confirm dashboard widget cards are also institution-scoped.
5. Check admin: `UserProfile.objects.filter(role__in=['Tutee','Tutor'], institution=None).count()`
   should be 0 (or known/accounted for).
