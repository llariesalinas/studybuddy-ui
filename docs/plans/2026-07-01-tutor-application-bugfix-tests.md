---
title: tutor-application-bugfix-tests
date: 2026-07-01
status: Approved
spec: 2026-07-01-tutor-application-bugfixes.md
---

# Tutor application bugfix tests

> Handoff target: **Codex**, running against branch `fix/tutor-application-bugfixes`. This plan is
> self-contained — no other context from this session should be required to execute it.

## Status & Progress Summary

**Status: Approved — not yet implemented.** The 4 code fixes this plan tests are already merged into
`fix/tutor-application-bugfixes` (see [`2026-07-01-tutor-application-bugfixes.md`](2026-07-01-tutor-application-bugfixes.md),
status Done). No test code has been written yet for them.

- [ ] Step 1 — resubmit gate tests (`pending` blocked, `rejected` allowed)
- [ ] Step 2 — resubmit/renewal oversized-file tests
- [ ] Step 3 — avatar/register oversized-file tests using the shared constant
- [ ] Step 4 — `login_view` exception-narrowing test

## Goal

Add regression coverage in `backend/studybuddy/tests.py` for the 4 fixes made to the tutor-application flow
on this branch, none of which currently have tests. Without this, a future change could silently reintroduce
any of the 4 original bugs.

## Background (what changed and why, so tests assert the right thing)

All in `backend/studybuddy/views.py` unless noted:

1. **`tutor_application_resubmit`** (~line 4436) now explicitly rejects resubmission when
   `application.application_status not in ('approved', 'rejected')` — i.e. a `pending` application gets a
   `400` instead of being silently reset. `approved` still routes to
   `create_tutor_document_renewal_submission` (pre-existing, already tested in `TutorDocumentRenewalTests`).
   `rejected` still falls through to the original resubmit-and-reset-to-pending behavior.
2. **Same function** gained a size check before the status branch: both `school_id` and `enrollment_proof`
   are rejected with `400` if either exceeds `settings.MAX_DOCUMENT_UPLOAD_SIZE`. This applies uniformly to
   both the `approved`-renewal path and the `rejected`-resubmit path.
3. **`register_user`** (~line 746), **`upload_tutee_avatar`** (~line 3123), and **`upload_tutor_avatar`**
   (~line 3147) all now compare against `settings.MAX_DOCUMENT_UPLOAD_SIZE` (defined in
   `backend/backend/settings.py`, value `5 * 1024 * 1024`) instead of separate inline literals. Behavior is
   unchanged (still 5 MB), only the source of truth moved — existing `rejects_non_image` /
   `rejects_missing_file` avatar tests already pass and don't need touching, but there is **no existing test
   for the oversized-file rejection path** on any of these three endpoints.
4. **`login_view`** (~line 879-887): the tutor-status lookup's exception handling was narrowed from
   `except Exception: logger.exception(...)` (which logged and let login proceed — fail-open) to
   `except TutorApplication.DoesNotExist: pass`. An unexpected exception during that lookup should now
   propagate (return 500), not silently allow login.

## Approach

Extend `backend/studybuddy/tests.py`. Two existing test classes are the natural homes:

- **`TutorDocumentRenewalTests`** (~line 1692) already has a working `setUp` with an approved tutor + admin
  fixtures and an `upload()`/`renewal_payload()` helper — reuse this fixture and its `self.application` for
  the resubmit-gate and oversized-file-on-resubmit tests. Note its `application_status="approved"` default;
  new tests need to flip `self.application.application_status` to `pending`/`rejected` as needed
  (`self.application.save(update_fields=["application_status"])`).
- **`TutorProfileTests`** (~line 1642) and **`TuteeProfileTests`** (~line 1582) already test avatar upload
  success/rejection paths — add the oversized-file case alongside `test_upload_avatar_rejects_non_image` /
  `test_upload_avatar_rejects_missing_file` in each.
- **`EmailAuthTests`** (~line 1913) is the existing home for login-flow tests — add the exception-narrowing
  test there, following its existing patterns for constructing a tutor user + `TutorApplication`.

Use `django.test.override_settings(MAX_DOCUMENT_UPLOAD_SIZE=<small value>)` to keep oversized-file test
payloads small and fast, rather than actually generating 5MB+ file content.

## Steps

1. **`TutorDocumentRenewalTests` — resubmit status gate**
   - `test_resubmit_rejected_application_succeeds`: set `self.application.application_status = "rejected"`,
     POST to `/api/tutor-application/resubmit/` with `renewal_payload()`. Assert `200`, and that
     `self.application.refresh_from_db()` shows `application_status == "pending"` (existing reset behavior,
     now reachable only via this path).
   - `test_resubmit_pending_application_rejected`: set `self.application.application_status = "pending"`,
     POST the same payload. Assert `400`, and that the application is unchanged in the DB (still `pending`,
     `school_id`/`enrollment_proof` unchanged from the value set in `setUp`).

2. **`TutorDocumentRenewalTests` — oversized files on resubmit**
   Wrap with `@override_settings(MAX_DOCUMENT_UPLOAD_SIZE=10)` (10 bytes, smaller than the `upload()` helper's
   test content) so no real large-file generation is needed.
   - `test_resubmit_oversized_school_id_rejected`: `application_status = "rejected"`, POST with an oversized
     `school_id` (reuse `self.upload(...)` — its content already exceeds 10 bytes under the override) and a
     normal-size `enrollment_proof`. Assert `400` and that no `TutorApplication` fields changed.
   - `test_resubmit_oversized_enrollment_proof_rejected`: same, inverted (oversized `enrollment_proof`, normal
     `school_id`).
   - `test_renewal_oversized_file_rejected`: same two cases but against `/api/tutor-application/renewal/`
     (the `approved`-tutor path, `create_tutor_document_renewal_submission`), confirming the shared size check
     applies there too. Assert `400` and `TutorDocumentRenewalReview.objects.count() == 0`.

3. **Avatar / registration oversized-file checks**
   - In `TutorProfileTests` and `TuteeProfileTests`: add `test_upload_avatar_rejects_oversized_file`, wrapped
     with `@override_settings(MAX_DOCUMENT_UPLOAD_SIZE=10)`, POSTing an avatar file whose content exceeds 10
     bytes. Assert `400` and error message mentions size (matches the existing literal string in the view —
     check exact wording at `views.py:3123-3128` / `3147-3152` before asserting on message text, or just assert
     status code to avoid coupling to wording).
   - If `register_user` has no existing test class, skip adding one — the resubmit/renewal tests in step 2
     already exercise the shared `settings.MAX_DOCUMENT_UPLOAD_SIZE` constant end-to-end. Only add a
     `register_user` oversized-file test if an existing `RegisterUserTests`-style class is found; otherwise
     note it as a gap in this plan's Changelog rather than scaffolding a new fixture class for one test.

4. **`login_view` — exception narrowing**
   - `test_login_unexpected_tutor_status_error_fails_closed`: construct a `Tutor`-role user with a
     `tutor_application` present (approved or pending, doesn't matter), authenticate via
     `POST /api/login/` with valid credentials, but force the `application_status` lookup to raise something
     other than `TutorApplication.DoesNotExist` — easiest approach: `unittest.mock.patch` on
     `TutorApplication.application_status` (a `PropertyMock` raising e.g. `ValueError`) scoped to the request,
     or monkeypatch `hasattr`-guarded access some other way that's compatible with how `login_view` fetches
     it (`profile.tutor_application.application_status`, `views.py:881`). Assert the response is `500` (the
     unhandled exception propagates through DRF's default exception handling as an internal server error) —
     confirm this repo's `EXCEPTION_HANDLER`/`DEBUG` test settings actually produce a `500` rather than
     re-raising past the test client; adjust the assertion to whatever this repo's convention is for
     "unhandled view exception in tests" if `500` doesn't hold.
   - `test_login_pending_tutor_status_does_not_error` (sanity check the narrowed except doesn't break the
     normal not-yet-applied case): a `Tutor`-role profile with **no** `tutor_application` at all. Assert login
     proceeds normally (whatever status a valid login otherwise returns — likely `200` with the OTP-challenge
     payload), confirming `except TutorApplication.DoesNotExist: pass` still correctly no-ops for that case.

## Risks

- Mocking a model property to force an arbitrary exception (step 4) is the fiddliest part of this plan —
  if `PropertyMock` doesn't cleanly intercept `application_status` given how it's accessed
  (`profile.tutor_application.application_status`), an alternative is temporarily monkeypatching
  `TutorApplication.__getattribute__` or using `django.db.models.signals` is overkill — simplest fallback is
  patching `UserProfile.tutor_application` (the reverse-OneToOne descriptor) to raise, which will surface
  before `hasattr` masks it. Whoever implements this should verify `hasattr(profile, 'tutor_application')`
  at `views.py:881` doesn't silently swallow the forced exception the same way `except Exception` used to —
  `hasattr` in Python 3 only swallows `AttributeError`, so a `ValueError`/custom exception from the mock
  should still propagate past it and into the narrowed `except`.
- The `MAX_DOCUMENT_UPLOAD_SIZE=10` override must not be smaller than Django's own upload-handling minimums;
  confirm test file content in `upload()` (currently short strings like `b"initial-id"`, 10 bytes) is
  comfortably larger than the override value or tests will be flaky depending on exact byte counts. Use an
  override value like `5` if `upload()`'s default payloads are exactly 10 bytes.
- `test_legacy_resubmit_endpoint_creates_document_renewal_for_approved_tutor` (existing, line 1793) already
  covers the `approved` path — don't duplicate it in step 1.

## Checks to run

- `python manage.py test studybuddy.tests.TutorDocumentRenewalTests studybuddy.tests.TutorProfileTests studybuddy.tests.TuteeProfileTests studybuddy.tests.EmailAuthTests` —
  all new and existing tests in the touched classes pass.
- `python manage.py test` (full suite) — confirm no regressions elsewhere. Note: this environment has had a
  stale/out-of-sync `test_postgres` database cause unrelated failures (`relation ... does not exist`) —
  if that happens, recreate the test DB (`python manage.py test` and answer `yes` to the recreate prompt, or
  drop `test_postgres` manually) before trusting failure output.

## Changelog

- 2026-07-01: Plan written and handed off to Codex for implementation. No test code written yet.
