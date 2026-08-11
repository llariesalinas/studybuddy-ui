---
title: Subjects "Not recognized" false-flag from stripped auth header
date: 2026-08-12
status: Approved
summary: subjects/ is listed as a public endpoint, so the request interceptor strips the JWT even for logged-in personalized calls, making every already-approved subject show "Not recognized".
spec:
---

# Subjects "Not recognized" false-flag from stripped auth header

## Status & Progress Summary

Root cause confirmed (backend-tested with/without JWT header). Plan approved, fix not yet
implemented — waiting to make the one-line interceptor change in the next session.

## Goal

Fix the bug where a tutee's (or tutor's) already-approved subjects (e.g. Python, Java) show
a "Not recognized" flag on their profile, even though the subjects are `status='approved'`
and correctly saved to their `Preference`/`TutorSubjects` rows.

## Approach

Confirmed via a live backend test (JWT header present vs. stripped) that this is a frontend
request-header bug, not a data problem:

- `src/services/api/api.js` keeps a `PUBLIC_ENDPOINTS` list (includes `subjects/`, `courses/`)
  so unauthenticated visitors (e.g. during registration) can browse the catalog.
- The request interceptor currently treats "public" as "never attach the token":
  `if (token && !isPublicEndpoint(config.url))`. This strips the `Authorization` header even
  when the user *is* logged in.
- `TuteeProfile.vue`'s `loadSubjects()` calls the same `subjects/` endpoint but with
  `recognized_only` / `include_current` / `course_code` params to get **personalized**
  `is_recognized` flags — this call needs the token to identify the profile.
- Backend (`SubjectListView.get_queryset()`, `backend/studybuddy/views.py:1979`) treats a
  request with no resolvable user as anonymous and returns the plain approved-subjects
  queryset **without** ever setting `self.recognized_codes`.
- `SubjectSerializer.get_is_recognized` (`backend/studybuddy/serializers.py:221`) then reads
  `context.get('recognized_codes')`, which defaults to `set()` (not `None`), so
  `obj.subject_code in recognized_codes` evaluates `False` for every subject — including ones
  the profile has already selected and that are approved.

Fix: "public" should mean *doesn't require* auth, not *must be sent without it*. Always attach
the bearer token when one exists; keep `isPublicEndpoint` gating only the 401-response
interceptor's forced-logout/refresh behavior, so a genuinely logged-out visit to a public page
still doesn't get bounced to `/login` on a 401.

This is a one-line interceptor change and fixes every screen that hits `subjects/`/`courses/`
while logged in (TuteeProfile, TutorProfile, PreferenceSetup, the subject picker modal), not
just this one screen.

## Steps

1. In `src/services/api/api.js`, change the request interceptor condition from
   `if (token && !isPublicEndpoint(config.url))` to `if (token)` so the token is attached
   whenever one exists, regardless of endpoint publicness.
2. Leave the response interceptor's `isPublicEndpoint` checks untouched (401 on a public
   endpoint should still not force logout/refresh for a logged-out visitor).
3. Manually verify in the browser: log in as a tutee with previously-selected subjects,
   open `/tutee-profile`, confirm the subject pills no longer show "Not recognized" and the
   Network tab shows `Authorization: Bearer ...` on the `subjects/` request.
4. Spot-check the still-anonymous path: hit a subjects-backed screen (e.g. registration) while
   logged out and confirm it still works without a token (no regression to the public-browsing
   case).
5. Run the frontend test suite and lint.

## Risks

- Any other call to a `PUBLIC_ENDPOINTS` URL (`courses/`, `partner-institutions/`, `login/`,
  etc.) will now also carry a bearer token when the user happens to be logged in. This should
  be harmless (`JWTAuthentication` just resolves the extra context), but worth a quick check
  that no public-endpoint view special-cases "must be anonymous" in a way that would reject an
  authenticated request.
- If any test mocks/asserts that public-endpoint requests carry no `Authorization` header, it
  will need updating.

## Checks to run

- `npm run lint`
- `npm run test`
- `npm run build`
- Manual browser check described in Steps 3–4.

## Changelog

- 2026-08-12: Plan created and approved. Root cause diagnosed and verified against a live
  backend run (JWT header present vs. stripped reproduced the bug exactly). Fix not yet
  implemented.
