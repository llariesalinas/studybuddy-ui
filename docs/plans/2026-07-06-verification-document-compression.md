---
title: Verification document + receipt image compression
date: 2026-07-06
status: Done
spec:
---

# Verification document + receipt image compression

<!-- LIVING SUMMARY: keep this section and the Changelog current on every edit -->
## Status & Progress Summary

**Status: Done — implemented, standalone-verified, and existing test suites pass with no regressions.**

Came out of a conversation about the demo deployment's media persistence problem (Render's disk is
ephemeral, Supabase's Postgres isn't). A Supabase Storage migration was discussed as the real fix
for persistence but is a separate, not-yet-approved decision. This plan is scoped to compression
only — it's a no-downside win regardless of where media ends up living.

## Goal

Reduce the storage/egress footprint of uploaded media (tutor/tutee verification documents,
payment receipts) by reusing the existing avatar-compression pipeline, without touching non-image
files (e.g. PDF enrollment proofs). This came out of a discussion about media persistence on the
demo deployment (Render's disk is ephemeral; Supabase Storage migration is a separate, not-yet-
approved follow-up) — compression is a low-risk, no-downside win regardless of where media
eventually lives.

## Approach

`backend/studybuddy/image_utils.py` already has `compress_image()` (resize to a bounding box,
strip EXIF, re-encode to WebP), used today only by `upload_tutor_avatar`/`upload_tutee_avatar`.

Add a new `compress_if_image(uploaded_file, max_size, quality)` helper that:
- Returns the file unchanged if `content_type` isn't `image/*` (so PDF `enrollment_proof` uploads
  pass through untouched).
- Otherwise calls `compress_image()`, falling back to the original file (seek(0) reset) if PIL
  fails to decode it — preserves today's behavior where no image-validity check exists for these
  fields, so nothing that currently succeeds starts failing.

New constants `DOCUMENT_MAX_SIZE = (1600, 1600)` / `DOCUMENT_QUALITY = 85` — higher than the
avatar's 512x512/80, since these are admin-reviewed verification documents and receipts where
legibility (ID text, receipt amounts) matters more than for a decorative avatar.

Each top-level view that receives files directly from `request.FILES` compresses exactly once,
after its existing null/size-check guards, immediately before the file is attached to a model
instance. The two shared helpers (`create_tutor_document_renewal_submission`,
`create_tutee_document_renewal_submission`) do **not** compress internally — their callers already
do, so compressing there too would double-compress the resubmit-while-approved path.

## Steps

1. `image_utils.py`: add `DOCUMENT_MAX_SIZE`, `DOCUMENT_QUALITY`, `compress_if_image()`.
2. `views.py` — compress `school_id` + `enrollment_proof` in:
   - `register_user` (initial tutor registration)
   - `tutor_application_resubmit` (rejected-resubmit branch, before its own `application.save()`)
   - `tutor_document_renewal_submit` (before calling the shared renewal helper)
   - `tutee_application_resubmit` (covers create-via-`get_or_create` and rejected-resubmit)
   - `tutee_document_renewal_submit` (before calling the shared renewal helper)
3. `views.py` — compress `receipt_image` in `submit_session_payment` (the only path that actually
   persists it; `confirm_payment_and_book` validates presence but never saves it to a model —
   pre-existing, out of scope here).
4. Run the backend test suite and confirm no regression beyond the documented pre-existing
   baseline.

## Risks

- `enrollment_proof` can be a PDF or an image; `compress_if_image` must not corrupt PDFs — covered
  by the `content_type` early-return.
- Re-running `compress_image` on an already-compressed WebP (e.g. if a caller path changes later)
  would cause a small additional quality loss — mitigated by compressing exactly once per request
  path (see Approach).
- `MAX_DOCUMENT_UPLOAD_SIZE` checks stay pre-compression (guarding raw upload size), which is
  unchanged behavior, not a new risk.

## Checks to run

- `python manage.py test studybuddy.tests.AvatarCompressionTests` and any existing tutor/tutee
  application + payment tests, to confirm the documented pre-existing baseline is unaffected.
- Manual: submit a tutor application with a large JPEG school ID and confirm the stored file is a
  smaller WebP; submit a PDF enrollment proof and confirm it's stored unchanged.

## Changelog

- 2026-07-06: Plan written and approved. Traced all six call sites that assign `school_id`,
  `enrollment_proof`, or `receipt_image` from `request.FILES` (`register_user`,
  `tutor_application_resubmit`, `tutor_document_renewal_submit`, `tutee_application_resubmit`,
  `tutee_document_renewal_submit`, `submit_session_payment`) and decided to compress once per
  top-level entry point rather than inside the two shared renewal helpers, to avoid
  double-compressing the resubmit-while-approved path. Noted `confirm_payment_and_book` validates
  `receipt_image` presence but never persists it — pre-existing, left out of scope.
- 2026-07-06: Implemented. Added `DOCUMENT_MAX_SIZE`/`DOCUMENT_QUALITY`/`compress_if_image()` to
  `image_utils.py`; wired it into all 6 call sites in `views.py` exactly as planned. Verified with
  `python manage.py test` (`AvatarCompressionTests`, `TutorDocumentRenewalTests`,
  `OnlinePaymentInitiationTests`, `ApplicationVerificationSharedBaseTests`,
  `TuteeVerificationPhase3Tests`, `BookingVerificationGateTests` — 50 tests, all pass, `--keepdb`
  against the existing Supabase-pooled test DB). `register_user`'s tutor-registration path has no
  existing automated coverage, so also ran a standalone Django-shell script exercising
  `compress_if_image` directly: a 3000x2000 JPEG (94,629 bytes) compressed to a 1600x1067 WebP
  (3,268 bytes); a PDF passed through byte-for-byte unchanged; a corrupted "image/jpeg" fell back
  to the original file unchanged rather than raising.
