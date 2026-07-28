---
title: Tutor profile real-time reflection and avatar image compression
date: 2026-06-21
status: Done
spec: ../specs/2026-06-21-tutor-profile-realtime-image-compression-design.md
---

# Tutor Profile Real-Time Reflection + Avatar Image Compression

## Status & Progress Summary

**Status:** Done — all 5 tasks implemented and committed. Frontend `lint`
(scoped to changed files) and `build` pass. `compress_image` verified standalone
(1500x1000 RGBA PNG -> 512x341 WebP; corrupt input raises). Backend endpoint
tests are written but could NOT be executed via the Django test runner: the
remote Supabase-pooled `test_postgres` cannot be dropped/recreated (a pooled
session holds it) and has pre-existing inconsistent migration history. See
summary for details.

## Goal

Make a tutor's profile edits (name, photo) reflect instantly across their own
app shell without a refresh, and compress avatar uploads server-side (resize +
WebP) so full-size phone photos are no longer stored or served raw.

## Approach

- **Real-time (own UI):** route the current user's display identity through the
  existing `authStore.user` object (already consumed reactively by the shell).
  Add a `patchUserProfile` action; call it from `TutorProfile.vue` after save and
  after avatar upload. No WebSockets.
- **Compression:** a single Pillow helper `compress_image()` used by both avatar
  endpoints. Resize to max 512x512, re-encode to WebP @ quality 80, strip EXIF.

## Steps

### Task 1 — auth store: patchUserProfile
**Files:** `src/stores/auth.js`
1. Add `profile_picture_url: null` to the `user` object built in `completeLogin`.
2. Add `patchUserProfile(partial)` that merges only `fname`, `lname`,
   `profile_picture_url` into `user.value` when it exists; export it.
3. `npm run lint`.

### Task 2 — TutorProfile: push updates to the store
**Files:** `src/views/TutorProfile.vue`
1. Import `useAuthStore`; instantiate `authStore`.
2. In `saveProfile()` success path, call
   `authStore.patchUserProfile({ fname: names.fname, lname: names.lname })`.
3. In `handleAvatarUpload()` success path, call
   `authStore.patchUserProfile({ profile_picture_url: profile.value.profile_picture_url })`.
4. `npm run lint`.

### Task 3 — backend image compression helper
**Files:** `backend/studybuddy/image_utils.py` (create)
1. Implement `compress_image(uploaded_file, max_size, quality)` with PIL:
   `exif_transpose` -> RGB -> `thumbnail` -> WebP buffer -> `ContentFile`.
2. Module constants `AVATAR_MAX_SIZE = (512, 512)`, `AVATAR_QUALITY = 80`.

### Task 4 — wire compression into the avatar views
**Files:** `backend/studybuddy/views.py`
1. Import `compress_image` (and constants).
2. In `upload_tutor_avatar` and `upload_tutee_avatar`, after validation wrap the
   file: `try: compressed = compress_image(avatar) except Exception: return 400`.
3. Assign `compressed` to `profile.profile_picture`.

### Task 5 — tests + verify
**Files:** `backend/studybuddy/tests.py`
1. Test: POST oversized PNG to tutor avatar endpoint -> 200, stored name ends
   `.webp`, decoded longest side <= 512.
2. Test: POST unreadable "image" -> 400.
3. Run `python manage.py test studybuddy`, `npm run lint`, `npm run build`.

## Risks

- `update_fields`-style saves are not used here; the avatar endpoints call
  `profile.save()` fully, so no field-tracking pitfalls.
- WebP from palette/RGBA inputs must be flattened to RGB or Pillow errors.
- `thumbnail` never upscales — small avatars pass through (acceptable).
- Existing avatars stay in their original format; only new uploads are WebP.

## Checks to run

- `npm run lint` — clean.
- `npm run build` — succeeds.
- `python manage.py test studybuddy` — all pass, including the two new tests.

## Changelog

- 2026-06-21: Plan and spec authored; status set to In Progress; index row added.
- 2026-06-21: Implemented all 5 tasks (auth store `patchUserProfile`, TutorProfile
  wiring, `image_utils.compress_image`, avatar-view compression, tests). Frontend
  lint/build pass; compression verified standalone. Backend endpoint tests blocked
  by remote test-DB pooler. Committed; status set to Done.
- 2026-07-17: Frontmatter `status` was still `In Progress` despite the body
  already saying Done since 2026-06-21 — corrected to `Done` during a
  plan-vs-code implementation audit.
