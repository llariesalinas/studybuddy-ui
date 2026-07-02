---
title: Tutor profile real-time reflection + avatar compression — session summary
date: 2026-06-21
plan: ../plans/2026-06-21-tutor-profile-realtime-image-compression.md
spec: ../specs/2026-06-21-tutor-profile-realtime-image-compression-design.md
status: Done
---

# Summary

## What shipped

### Part A — Real-time own-UI reflection (no WebSockets)
- `src/stores/auth.js`: added `profile_picture_url: null` to the `user` object
  built in `completeLogin`, and a new `patchUserProfile(partial)` action that
  shallow-merges only `fname`, `lname`, `profile_picture_url` into `user.value`.
  Exported from the store.
- `src/views/TutorProfile.vue`: imports `useAuthStore`; calls
  `patchUserProfile({ fname, lname })` after a successful `saveProfile()` and
  `patchUserProfile({ profile_picture_url })` after `handleAvatarUpload()`.
- `src/App.vue` needed no change — its `userFname` computed already reads
  `authStore.user.fname`, so shell greetings update reactively.

### Part B — Server-side avatar compression (Pillow)
- `backend/studybuddy/image_utils.py` (new): `compress_image(file, max_size,
  quality)` — `exif_transpose` -> flatten RGBA/LA/P to RGB on white -> `thumbnail`
  to 512x512 -> WebP @ quality 80 -> `ContentFile` named `<stem>.webp`.
  Constants `AVATAR_MAX_SIZE = (512, 512)`, `AVATAR_QUALITY = 80`.
- `backend/studybuddy/views.py`: both `upload_tutor_avatar` and
  `upload_tutee_avatar` now wrap the upload in `compress_image()` inside a
  try/except returning `{'error': 'Invalid image file'}` (400) on failure, and
  store the compressed result.
- `backend/studybuddy/tests.py`: `AvatarCompressionTests` — oversized PNG ->
  200 + stored `.webp` + longest side <= 512; unreadable "image" -> 400.

## Deviations from plan
- None in scope. Realtime routed through `authStore.user` (single source the
  shell already consumes) rather than a new store, as designed.

## Checks run
- `npx eslint src/stores/auth.js src/views/TutorProfile.vue` — clean (the
  repo-wide `npm run lint` reports many pre-existing issues in untouched files).
- `npm run build` — succeeds.
- `compress_image` verified standalone via a Django shell script: a 1500x1000
  RGBA PNG produced a 512x341 WebP (8218 -> 396 bytes); corrupt bytes raised
  `UnidentifiedImageError` (caught -> 400).

## Known caveat — backend endpoint tests not executed
The Django test runner could not create/recreate the test database:
- DB is remote Supabase (`aws-1-ap-southeast-1.pooler.supabase.com`). The pooler
  holds a session on `test_postgres`, so Django's drop fails with "database is
  being accessed by other users".
- `--keepdb` fails on pre-existing `InconsistentMigrationHistory`
  (0042 applied before 0041) in that persistent test DB — unrelated to this work.

The two new tests are written and the core logic is verified standalone. To run
the endpoint tests, either point `DB_*` at a local Postgres, or terminate the
pooled `test_postgres` session (a shared remote resource — left to the owner).

## Notes for the Supabase question
The project's **database** is Supabase-hosted Postgres, but **media/images are
not** in Supabase Storage — they live on local Django filesystem
(`MEDIA_ROOT/profile_pics/`). Supabase's on-the-fly CDN image transform was
therefore not applicable; compress-on-upload is the practical equivalent here.
