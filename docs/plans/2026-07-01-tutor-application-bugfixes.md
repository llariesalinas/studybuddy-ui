---
title: tutor-application-bugfixes
date: 2026-07-01
status: In Progress
spec:
---

# Tutor application bugfixes

> Handoff: see [`docs/session-summaries/2026-07-01-tutor-application-handoff.md`](../session-summaries/2026-07-01-tutor-application-handoff.md)
> for the full context this plan grew out of (the `/review` findings, decisions made during grilling, and the
> deferred tutee-enrollment-checker feature to pick up after this ships).

<!-- LIVING SUMMARY: keep this section and the Changelog current on every edit -->
## Status & Progress Summary

**Status: In Progress — 1 of 5 done, 4 revised and in flight.**

An unplanned commit, `66c1441` ("Add tutor document renewal review flow"), landed on this branch between
sessions and shipped a large chunk of the deferred tutee/tutor renewal feature (see
[`docs/plans/2026-07-01-tutor-document-renewal-review.md`](2026-07-01-tutor-document-renewal-review.md),
retro-documented). It incidentally touched two of these bugs, so steps 1 and 3 below are revised from their
original form to match current code instead of being implemented as originally written.

- [x] Step 2 — model/migration drift (`db_index=True` already present — done by the renewal commit)
- [ ] Step 1 — resubmission gate (**revised**: renewal commit already redirects `approved` apps to the new
      renewal flow instead of reverting them to pending, which fixed the worst case. Remaining gap: `pending`
      apps can still freely resubmit via the same fallthrough. Add an explicit `rejected`-only gate.)
- [ ] Step 3 — centralize `MAX_UPLOAD_SIZE` (**revised**: frontend half already done by the renewal commit —
      `MAX_DOCUMENT_UPLOAD_SIZE_BYTES` in `src/config.js`, used by `TutorScreeningModal.vue` and
      `TutorApplicationStatus.vue`. Backend half remains: no `settings.py` constant, and `register_user` /
      `upload_tutee_avatar` still have separate inline literals.)
- [ ] Step 4 — resubmit size check (unchanged from original plan)
- [ ] Step 5 — `login_view` exception narrowing (unchanged from original plan; still fail-open at
      `views.py:886-887`)

No other deviations. No open questions blocking implementation.

## Goal

Fix 5 defects found during a `/review` of commit `f23b423` ("Fix/revise tutor registration sync main (#92)")
on `main`, before starting the larger tutee-side enrollment-verification feature.

## Approach

Branch: **`fix/tutor-application-bugfixes`**, created off `origin/main` (at `f23b423`) — **not** off
`feature-cashout-recent-transactions`, since that branch diverged from `main` at `b773afd`, before `f23b423`
landed, and doesn't contain 4 of these 5 bugs. Confirmed by direct inspection: this branch has
`MAX_UPLOAD_SIZE` at `views.py:746`, migration `0054_tutorapplication_application_status_idx.py`, and the
broadened `except Exception` in `login_view` — all absent from the cashout branch.

Each fix is a small, targeted change; all 5 land in one PR since they're all fallout from the same source
commit and none depend on the tutee feature.

## Steps

1. **Resubmission gate** (`backend/studybuddy/views.py`, `tutor_application_resubmit`, ~line 4436) — **revised**
   The renewal commit (`66c1441`) already redirects `approved` applications to
   `create_tutor_document_renewal_submission` instead of reverting them to pending, which fixes the original
   bug's worst case. `TutorApplication.STATUS_CHOICES` is only `pending`/`approved`/`rejected`, so the only
   remaining gap is `pending`: it still falls through to the reset-to-pending block, an implicit no-op today
   but not an explicit one. Add an explicit check after the `approved` branch: return 400 unless
   `application.application_status == 'rejected'`.

2. **Model/migration drift** (`backend/studybuddy/models.py`, `TutorApplication.application_status`, ~line 266)
   — **done**. `db_index=True` is already present, applied by the renewal commit's migrations. No action needed.

3. **Centralize `MAX_UPLOAD_SIZE`** — **revised, backend half only**
   - Frontend: **already done** by the renewal commit — `MAX_DOCUMENT_UPLOAD_SIZE_BYTES` in `src/config.js`,
     used by `TutorScreeningModal.vue` and `TutorApplicationStatus.vue`.
   - Backend: still needed — add `MAX_DOCUMENT_UPLOAD_SIZE` to `backend/backend/settings.py`; replace the
     local `MAX_UPLOAD_SIZE = 5 * 1024 * 1024` literal in `register_user` (`views.py:778`) and the inline
     `5 * 1024 * 1024` in `upload_tutee_avatar` (`views.py:3126`) with it.

4. **Resubmit missing size check** (`tutor_application_resubmit`, ~line 4436)
   Add the same size check `register_user` has (`school_id.size > MAX_DOCUMENT_UPLOAD_SIZE or
   enrollment_proof.size > MAX_DOCUMENT_UPLOAD_SIZE`), using the new shared constant from step 3.

5. **`login_view` exception narrowing** (`views.py:886-887` on this branch)
   Narrow `except Exception: logger.exception(...)` back to `except TutorApplication.DoesNotExist: pass`.
   Login must fail closed (propagate/500) on unexpected errors during the tutor-status check, not silently
   let the user through.

## Rejected alternative

For step 3, considered a runtime config endpoint so the frontend fetches the upload limit from the backend
instead of mirroring a constant. Rejected: adds a network call and a failure mode for a value that changes
rarely; a documented mirrored constant is simpler and sufficient at this scale.

## Risks

- None of these changes touch the tutee side or the re-verification feature — should be a clean, isolated PR.
- `db_index=True` on an existing table triggers an index build; on Postgres for the `TutorApplication` table
  size expected in this project, this is not a concern, but worth a sanity check if the table has grown large.
- Narrowing the `login_view` except means genuinely unexpected errors during the tutor-status check will now
  surface as 500s instead of silently letting login through — this is the intended, safer behavior, but means
  any latent data issue (e.g. a `TutorApplication` row in a bad state) will now be visible instead of masked.

## Checks to run

- `python manage.py makemigrations --check --dry-run` (confirm step 2 didn't leave the model/migration out of
  sync in the other direction)
- `python manage.py test` (backend test suite)
- `npm run lint` and `npm run build` (frontend)
- Manual/APIRequestFactory checks: resubmit attempted on `pending` and `approved` applications returns an
  error; resubmit on `rejected` succeeds; oversized file on resubmit is rejected; login with a forced
  exception in the tutor-status lookup now 500s instead of proceeding.

## Changelog

- 2026-07-01: Plan created and approved. Branch `fix/tutor-application-bugfixes` cut from `origin/main`
  (contains `f23b423`, unlike `feature-cashout-recent-transactions`). All 5 fixes designed via grilling;
  none implemented yet.
- 2026-07-01: Resumed session found an unplanned commit `66c1441` ("Add tutor document renewal review flow")
  already on this branch, not covered by any plan. It incidentally completed step 2 in full and half of step
  3 (frontend), and changed the shape of step 1 (the `approved` case is now handled via a new renewal flow
  instead of the original blanket gate). Retro-documented that commit in
  [`docs/plans/2026-07-01-tutor-document-renewal-review.md`](2026-07-01-tutor-document-renewal-review.md) and
  revised steps 1 and 3 above to match current code. User confirmed this approach. Status moved to In Progress;
  implementing the 4 remaining gaps (steps 1, 3-backend, 4, 5) now.
