---
title: Tutee enrollment verification — Phase 1 (model & backend foundation)
date: 2026-07-01
status: Done
spec: 2026-07-01-tutee-verification-overview.md
---

# Phase 1 — Model & backend foundation

> Part of [Tutee enrollment verification — overview](2026-07-01-tutee-verification-overview.md). Do not
> start Phase 2 without explicit go-ahead once this phase is Done.

<!-- LIVING SUMMARY: keep this section and the Changelog current on every edit -->
## Status & Progress Summary

**Status: Done — steps 1-9 complete and verified; step 10 (serializers) cut, moved to Phase 3.**

- [x] Abstract `ApplicationVerificationBase` / `DocumentRenewalReviewBase`, `TutorApplication`/
      `TutorDocumentRenewalReview` refactored onto them, `TuteeApplication`/`TuteeDocumentRenewalReview`
      added (steps 1-5).
- [x] Regression tests (baseline `TutorDocumentRenewalTests`, 7/7 green) + new
      `ApplicationVerificationSharedBaseTests` (4/4 green) proving identical behavior for both roles
      (steps 6-7).
- [x] Migration generated and verified schema-neutral: `TutorApplication` gets only the 2 additive
      reminder fields, `TutorDocumentRenewalReview` untouched, 2 new tables created (step 8).
- [x] Generalized `get_document_review_context(application)` helper added, unit-tested, not wired into
      any view (step 9).
- [ ] ~~Step 10 — `TuteeApplicationSerializer`/`TuteeDocumentRenewalReviewSerializer`~~ — **cut**, see
      Changelog. Moved to Phase 3, where they'll be written alongside the admin views/tests that use
      them instead of sitting unreferenced.

This phase touches only models, migrations, and a new unwired helper function — no endpoint's
user-facing behavior changes in this phase (that starts in Phase 2).

## Goal

Give tutees the same document-verification data model and renewal-cadence logic tutors already have,
without duplicating it, and without disturbing `TutorApplication`'s existing schema or behavior.

## Approach

Two abstract Django base models, mirroring the existing concrete ones field-for-field:

- `ApplicationVerificationBase` (abstract) — carries everything currently on `TutorApplication` except the
  `profile` OneToOneField (its `related_name` differs per role): `DOCUMENT_RENEWAL_INTERVAL_DAYS`,
  `STATUS_CHOICES`, `school_id`, `enrollment_proof`, `reason_to_tutor`, `application_status`,
  `rejection_reason`, `reviewed_by`, `reviewed_at`, `submitted_at`, `updated_at`, plus two **new** dedup
  fields: `reminder_7day_sent_at`, `reminder_1day_sent_at` (both nullable, default null), and the 5 renewal
  methods (`latest_approved_document_review_at`, `document_renewal_due_at`, `latest_document_renewal_review`,
  `document_renewal_status`, `can_submit_document_renewal`).
- `DocumentRenewalReviewBase` (abstract) — carries everything currently on `TutorDocumentRenewalReview`
  except the `application` ForeignKey (target model differs per role): `STATUS_CHOICES`, `profile` FK,
  `school_id`, `enrollment_proof`, `reason_to_tutor`, `status`, `rejection_reason`, `reviewed_by`,
  `reviewed_at`.

`TutorApplication` and `TutorDocumentRenewalReview` are refactored to inherit these bases (field names,
`upload_to` paths, and `related_name`s unchanged, so existing migrations/data are untouched — see Risks).
`TuteeApplication` and `TuteeDocumentRenewalReview` are new concrete models inheriting the same bases, with
their own `upload_to` paths (`tutee_applications/...`) and `profile` `related_name='tutee_application'` /
FK `related_name='document_renewal_reviews'` (safe to reuse — related_name uniqueness is scoped per target
model, not global).

**Naming decision — `reason_to_tutor` field name kept as-is on the shared base.** The design doc doesn't
call for renaming this field, and doing so would ripple into the serializer, `AdminTutorApplications.vue`'s
`readFirst` fallback chain, `Register.vue`, and `TutorScreeningModal.vue`/`registrationinfo.js` — out of
scope for a "small, focused" Phase 1. The field already reads generically as free-text motivation in the
UI (labelled "Motivation" / "Renewal Note" via existing `selectedReviewNoteLabel` logic), so this is a
naming wart, not a functional gap. Flagged here rather than silently fixed.

**"Expose `document_renewal_status` broadly" (per the locked design) is scoped down for this phase**: add a
role-generic helper function, unit-tested, but **do not wire it into `login_view` or the router guard yet**
— that's a user-facing behavior change (the forward-only loosening) that belongs to Phase 2. This phase only
proves the helper works for both models.

**Reminder dedup fields**: added to the schema now (nullable, unused). Nothing sets or reads them yet —
resetting them on renewal approval is wired when the (generalized) approval endpoints are touched in
Phase 3; consuming them for reminders is Phase 4. Called out explicitly so it isn't mistaken for a gap in
this phase.

## Steps

1. **Add `ApplicationVerificationBase` and `DocumentRenewalReviewBase`** as abstract models in
   `backend/studybuddy/models.py`, placed just above `TutorApplication` (~line 240). Copy the existing
   field definitions and methods verbatim (plus the 2 new reminder fields on `ApplicationVerificationBase`).
2. **Refactor `TutorApplication(ApplicationVerificationBase)`** — keep only `profile = OneToOneField(...,
   related_name='tutor_application')` and `__str__`. Confirm every existing field name, `upload_to` path,
   and method stays byte-identical to today's definitions.
3. **Refactor `TutorDocumentRenewalReview(DocumentRenewalReviewBase)`** — keep only `application =
   ForeignKey(TutorApplication, ..., related_name='document_renewal_reviews')` and `__str__` if present.
4. **Add `TuteeApplication(ApplicationVerificationBase)`** — `profile = OneToOneField(UserProfile,
   on_delete=models.CASCADE, related_name='tutee_application')`, `school_id` /`enrollment_proof` upload
   paths under `tutee_applications/`, `__str__`.
5. **Add `TuteeDocumentRenewalReview(DocumentRenewalReviewBase)`** — `application = ForeignKey(
   TuteeApplication, on_delete=models.CASCADE, related_name='document_renewal_reviews')`, upload paths
   under `tutee_applications/renewal_...`.
6. **Regression tests first (TDD)** in `backend/studybuddy/tests.py`: before touching the model file, add
   tests that exercise `TutorApplication`'s renewal methods (status transitions verified/due/pending/
   rejected, `can_submit_document_renewal`) against the *current* concrete model, so they fail only if the
   refactor changes behavior — then re-run them unchanged after the refactor (see Checks to run).
7. **New tests for `TuteeApplication`** mirroring step 6, plus one for `TuteeDocumentRenewalReview` feeding
   `latest_approved_document_review_at()`, proving the shared base behaves identically for both roles.
8. **`makemigrations`** and inspect the generated migration by hand before applying (see Risks) — expect:
   no `AlterField`/no-op noise on `TutorApplication`/`TutorDocumentRenewalReview` beyond the 2 new nullable
   reminder fields; two new `CreateModel` migrations for `TuteeApplication` and
   `TuteeDocumentRenewalReview`.
9. **Add the generalized helper** `get_document_review_context(profile, role, application)` (or similar) in
   `views.py` near `get_tutor_document_review_context` (~line 140) — same shape of returned dict, but
   parameterized so it can be called for either a `tutor_application` or `tutee_application`. Do **not**
   call it from `build_login_response_payload` for tutees yet; add a unit test that calls it directly with
   a `TuteeApplication` fixture and asserts the same keys/values shape as the tutor path.
10. ~~**Serializers**~~ — **cut from this phase**, see Changelog. Moved to Phase 3.

## Risks

- **Migration schema-neutrality is the core risk.** Django abstract-base inheritance copies field
  definitions onto each concrete model rather than creating a shared table, so as long as every field's
  name, type, and options are unchanged on `TutorApplication`/`TutorDocumentRenewalReview`, Django should
  emit no `AlterField` for them. Must verify by reading the generated migration, not by assumption — if it
  emits unexpected alters, do not apply until understood.
- **`related_name='document_renewal_reviews'` reused across two FK targets** (`TutorDocumentRenewalReview
  .application` → `TutorApplication`, `TuteeDocumentRenewalReview.application` → `TuteeApplication`) is
  safe in Django (uniqueness is per-target-model), but worth a one-line comment in the model so a future
  reader doesn't assume it's a typo.
- **`reason_to_tutor` naming wart** carried forward (see Approach) — revisit only if it becomes confusing
  in Phase 3's generalized UI; not blocking.
- Adding two new serializers with no view wiring yet is inert but slightly ahead of need — acceptable
  per the plan's own reasoning (cheaper while context is loaded) but flag if it feels premature in review.

## Checks to run

- `python manage.py test studybuddy.tests` (or the narrower `TutorApplication`-related test classes) run
  once **before** the refactor (baseline) and once **after** (must be identical pass/fail set — proves no
  behavior regression).
- New tests for `TuteeApplication` / `TuteeDocumentRenewalReview` / the generalized helper, run green.
- `python manage.py makemigrations --check --dry-run` after migrations are committed (confirms nothing was
  left out of sync).
- Manual read of the generated migration file(s) before `migrate` is run against a real dev DB.
- `python manage.py migrate` on a dev/test DB, confirm no errors, confirm `TutorApplication` row data is
  intact (spot-check via `python manage.py shell` or existing seeded data).

## Changelog

- 2026-07-01: Phase 1 plan written in full detail from the locked design (handoff doc §3/§4). Status set to
  Approved. Not yet implemented.
- 2026-07-01: Implemented steps 1-9. Two refinements discovered during implementation:
  - **FK/upload-path boundary is wider than originally sketched.** `profile`, `reviewed_by`, `school_id`,
    `enrollment_proof` had to move out of both abstract bases and onto each concrete subclass instead of
    just `profile`/`application` as originally written. Reason: Django's `%(class)s` related-name
    interpolation only applies to `related_name`/`related_query_name`, not to plain FK `related_name`
    strings needing full customization or to `upload_to` paths — `reviewed_by`/`profile` FKs on the review
    base both target `UserProfile`, so an identical inherited `related_name` would collide between the
    Tutor and Tutee subclasses; `school_id`/`upload_to` needs a role-specific storage folder. The abstract
    bases still carry all the actual shared logic and status/renewal fields — this is a mechanical
    Django-inheritance detail, not a design change.
  - **Step 10 (serializers) cut.** Adding `TuteeApplicationSerializer`/`TuteeDocumentRenewalReviewSerializer`
    with no view or test wired to them was flagged as premature against this repo's "no half-finished
    implementations" convention. Moved to Phase 3, written alongside the admin views/tests that use them.
  - Verified: baseline `TutorDocumentRenewalTests` (7/7) unchanged; new
    `ApplicationVerificationSharedBaseTests` (4/4) proves identical renewal-cadence behavior for
    `TutorApplication` and `TuteeApplication`; migration inspected by hand — `TutorApplication` gets only
    the 2 additive reminder fields, `TutorDocumentRenewalReview` untouched, 2 new tables created;
    `makemigrations --check --dry-run` clean after applying.
- 2026-07-01: Ran the full backend suite (`python manage.py test`, 103 tests): 3 failures + 8 errors, all in
  `ChatFeatureTests`, `EmailAuthTests`, and `RecommendTutorsViewTests` — none touch
  `TutorApplication`/`TuteeApplication`/`ApplicationVerificationBase` or any file this phase changed.
  Confirmed pre-existing by stashing this phase's code changes (`git stash push -u`) and re-running the
  same failing tests against clean `HEAD`: identical failures/errors reproduce verbatim. Restored the
  stash. Status set to Done.
- 2026-07-01: Ran `/code-review` (8 finder angles + verify) on the Phase 1 diff. Most candidates were false
  positives (claimed `related_name` collisions that are actually fine since they target different models —
  refuted directly by the passing test suite exercising exactly those code paths; a claimed `None` deref in
  `get_document_review_context` that doesn't exist, the code already guards with `if latest_renewal and
  ...`; "hardcoded values" flags on string literals that are pre-existing `STATUS_CHOICES` values copied
  verbatim from the original code). Two findings were real and fixed:
  - `get_document_review_context()` and `get_tutor_document_review_context()` duplicated the same dict-
    building logic. Collapsed to one implementation: `get_tutor_document_review_context` now does the
    profile→application lookup and delegates to `get_document_review_context`; a shared
    `EMPTY_DOCUMENT_REVIEW_CONTEXT` constant covers the no-application case.
  - `reminder_7day_sent_at`/`reminder_1day_sent_at` had no `db_index`, and Phase 4 will filter on them for
    reminder dedup. Added `db_index=True` to both while the columns are new and empty, avoiding a later
    index-add migration under load. Migration regenerated; `makemigrations --check --dry-run` still clean;
    all 11 tests still pass.
