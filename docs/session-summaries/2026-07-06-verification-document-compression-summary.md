---
title: Verification document + receipt image compression — session summary
date: 2026-07-06
plan: ../plans/2026-07-06-verification-document-compression.md
status: Done
---

# Summary

## What shipped

- `backend/studybuddy/image_utils.py`: added `DOCUMENT_MAX_SIZE = (1600, 1600)`,
  `DOCUMENT_QUALITY = 85`, and `compress_if_image(uploaded_file, max_size, quality)` — returns the
  file unchanged if `content_type` isn't `image/*` (so PDF `enrollment_proof` uploads pass through),
  otherwise calls the existing `compress_image()` and falls back to the original file (with a
  `seek(0)` reset) if PIL can't decode it, rather than raising.
- `backend/studybuddy/views.py`: wired `compress_if_image()` into all 6 places that assign
  `school_id`, `enrollment_proof`, or `receipt_image` from `request.FILES`:
  `register_user`, `tutor_application_resubmit`, `tutor_document_renewal_submit`,
  `tutee_application_resubmit`, `tutee_document_renewal_submit`, `submit_session_payment`.
  Each top-level entry point compresses exactly once, after its existing null/size-check guards;
  the two shared helpers (`create_tutor_document_renewal_submission`,
  `create_tutee_document_renewal_submission`) were left untouched since their callers already
  compress before calling them — avoids double-compressing the resubmit-while-approved path.

## Deviations from plan

- None. Implementation matched the plan's call-site list and compress-once-per-entry-point design.

## Checks run

- `python manage.py check` — no issues.
- `python manage.py test` (`--keepdb`, existing Supabase-pooled test DB) across
  `AvatarCompressionTests`, `TutorDocumentRenewalTests`, `OnlinePaymentInitiationTests`,
  `ApplicationVerificationSharedBaseTests`, `TuteeVerificationPhase3Tests`,
  `BookingVerificationGateTests` — 50 tests, all pass, no regressions.
- `register_user`'s tutor-registration path (call site 1) has no existing automated test coverage,
  so ran a standalone Django-shell script directly exercising `compress_if_image`:
  - A 3000x2000 JPEG (94,629 bytes) compressed to a 1600x1067 WebP (3,268 bytes) — ~97% smaller.
  - A PDF (`content_type='application/pdf'`) passed through byte-for-byte unchanged.
  - A corrupted file claiming `content_type='image/jpeg'` fell back to the original unchanged,
    rather than raising.

## Context

This grew out of a conversation about the demo deployment's media persistence problem (Render's
local disk is ephemeral across redeploys; Supabase's Postgres isn't). Two fixes were discussed —
storing files directly in Postgres vs. Supabase Storage (an S3-compatible object bucket in the same
project) — with Supabase Storage recommended as the better long-term fix, but **that migration was
not approved and is not part of this change**. Compression was identified as a no-downside win
regardless of which storage backend media eventually lives on, since it directly shrinks both
storage and egress footprint, and the underlying `compress_image()` utility already existed
(built for avatars in the 2026-06-21 session). Auto-deletion of documents after admin review was
discussed and explicitly deferred — it trades away audit history for a marginal storage saving that
isn't needed at this project's scale (a handful of demo accounts, nowhere near Supabase's 1 GB free
Storage tier).
