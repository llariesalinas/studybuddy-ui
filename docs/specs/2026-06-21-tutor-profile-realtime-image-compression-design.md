---
title: Tutor profile real-time reflection and avatar image compression
date: 2026-06-21
status: Approved
---

# Tutor Profile Real-Time Reflection + Avatar Image Compression

## Problem

1. **Stale identity in the app shell.** `authStore.user` is populated once at
   login (`completeLogin` in `src/stores/auth.js`) and never updated afterward.
   When a tutor edits their name in `TutorProfile.vue` and saves, the shell
   greetings that read `authStore.user.fname` (`Welcome back, {{ userFname }}`
   in `src/App.vue`, plus the tutor dashboard) keep showing the old name until
   the user logs out and back in. The profile page itself is fine — it calls
   `loadProfile()` after save — but the shared shell is not.

2. **Uncompressed avatar uploads.** `upload_tutor_avatar` and
   `upload_tutee_avatar` (`backend/studybuddy/views.py`) store the raw uploaded
   file on the local filesystem (`ImageField` -> `MEDIA_ROOT/profile_pics/`).
   The only safeguards are "must be an image" and "< 5 MB". A 4 MB phone photo
   is persisted and served to every viewer at full resolution. There is no
   resize, re-encode, or metadata stripping.

## How Supabase handles this (reference)

Supabase does **not** compress on upload. It stores the original and performs
on-the-fly transformation at the CDN edge (imgproxy): a request like
`/render/image/.../avatar.png?width=128&quality=75&format=webp` resizes and
re-encodes on demand and caches the derivative. This requires a CDN with an
image-transform layer. Studybuddy serves media from local Django filesystem
storage, so the practical equivalent is **compress-on-upload with Pillow**:
resize to a max dimension, re-encode to WebP at a fixed quality, strip EXIF.

## Decisions

- **Real-time scope:** own UI only, no WebSockets. The current user's display
  identity is propagated through the existing `authStore.user` object, which the
  shell already consumes reactively.
- **Compression:** server-side Pillow on upload — single source of truth, covers
  every avatar upload path, no client trust required.
- **Format/size:** WebP, max 512x512 (aspect preserved), quality 80.

## Part A — Real-time own-UI reflection

### auth store (`src/stores/auth.js`)
- Add `profile_picture_url: null` to the `user` object created in
  `completeLogin`.
- Add a `patchUserProfile(partial)` action that shallow-merges allowed display
  fields (`fname`, `lname`, `profile_picture_url`) into `user.value` when a user
  exists. Export it from the store's return object.

### TutorProfile (`src/views/TutorProfile.vue`)
- After a successful `saveProfile()`, call
  `authStore.patchUserProfile({ fname, lname })` using the split full name that
  was sent to the backend.
- After a successful `handleAvatarUpload()`, call
  `authStore.patchUserProfile({ profile_picture_url })` with the new URL.
- Import and instantiate `useAuthStore`.

### Shell (`src/App.vue`)
- No template change required for the name — `userFname` already reads
  `authStore.user.fname`, which now updates reactively. Verify the computed has
  no stale caching issues.

## Part B — Server-side image compression

### New helper (`backend/studybuddy/image_utils.py`)
```
compress_image(uploaded_file, max_size=AVATAR_MAX_SIZE, quality=AVATAR_QUALITY)
  -> ContentFile (.webp)
```
- Open with PIL, apply `ImageOps.exif_transpose` (honor camera orientation).
- Convert to RGB (drop alpha / palette modes onto white if needed).
- `thumbnail(max_size)` — preserves aspect ratio, never upscales.
- Save to an in-memory buffer as WebP at `quality`.
- Return a Django `ContentFile` with a `.webp` filename derived from the
  original stem.
- Raise/propagate a clear error on an unreadable image so the view can return
  400.
- Module-level constants: `AVATAR_MAX_SIZE = (512, 512)`, `AVATAR_QUALITY = 80`.

### Views (`backend/studybuddy/views.py`)
- In both `upload_tutor_avatar` and `upload_tutee_avatar`, after the existing
  image/size validation, wrap the file with `compress_image()` inside a
  try/except. On failure return `{'error': 'Invalid image file'}` 400. Assign
  the compressed result to `profile.profile_picture`.

## Tests (`backend/studybuddy/tests.py`)
- Upload an oversized (e.g. 1000x1000) PNG to the tutor avatar endpoint; assert
  the response is 200, the stored file ends in `.webp`, and the decoded image is
  <= 512 on its longest side.
- Upload a non-image / corrupt file already covered by the existing content-type
  guard; add a case for a file that claims `image/*` but is unreadable -> 400.

## Out of scope (YAGNI)
- WebSocket broadcast to other users viewing a tutor (the "broadcast" option was
  declined).
- Applying compression to receipts / school IDs / enrollment proofs (the helper
  is reusable for these later, but not wired now).
- Moving media to S3 / Supabase / a CDN transform layer.

## Checks
- `npm run lint`
- `npm run build`
- `python manage.py test studybuddy`
