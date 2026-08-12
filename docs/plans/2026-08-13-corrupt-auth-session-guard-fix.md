---
title: Corrupt auth session guard fix
date: 2026-08-13
status: Done
summary: Router guard self-heals when a token survives in localStorage without its role, instead of silently no-oping Log in/Get started.
spec:
---

# Corrupt auth session guard fix

## Status/Progress Summary

Done. The self-heal branch is in `src/router/index.js`, covered by
`src/router/index.test.js`, and verified against the live deployment.

## Changelog

- 2026-08-13: Plan written after diagnosing via Claude in Chrome (see
  `docs/session-summaries/2026-08-13-cant-login-diagnosis-summary.md`).
- 2026-08-13: Implemented the self-heal branch, added `src/router/index.test.js`
  (3 cases), ran `npm run lint` / `npm run build` / `npx vitest run` clean (3 pre-existing
  unrelated failures in `tokens.test.js`, not touched by this change). Marked Done.

## Goal

A partial/corrupt auth session (an `access_token`/`refresh_token` pair sitting in
`localStorage` with no matching `user_role`) makes the "Log in" and "Get started" buttons
on the landing page look completely dead — no error, no redirect, nothing. Fix the router
guard so this state self-heals instead of silently trapping the user on the landing page.

## Approach

Root cause, confirmed live against the deployed app
(`https://studybuddy-peertutoring.vercel.app/`):

1. `authStore.isAuthenticated` is `computed(() => !!token.value)` — true whenever a token
   exists, regardless of whether `user` is populated.
2. `authStore.initializeAuth()` (`src/stores/auth.js:293`) hydrates `user` from a separate
   `localStorage['user_role']` key. If that key is missing while `access_token` /
   `refresh_token` survive, `user` stays `null` and `userRole` stays `null`.
3. The global nav guard's `GUEST_ONLY_ROUTE_NAMES` branch
   (`src/router/index.js:319-325`) redirects an authenticated user away from
   `/login`/`/register` based on role — tutor/tutee/admin/superadmin each get a real
   destination, but the `null`-role case falls through to `return '/'`.
4. Clicking "Log in" while on `/` pushes to `/login`, the guard redirects back to `/`, and
   Vue Router treats "navigate to the current location" as a no-op — no visible change, no
   console error. It reads as a dead button.

In every normal flow (`completeLogin`, `initializeAuth`) the token and role are written
together, so this state shouldn't occur from ordinary use — but nothing currently prevents
or recovers from it (storage eviction, an extension clearing one key, manual devtools
edits, or a future code path that writes tokens without the role). The guard should not
assume `isAuthenticated` implies a resolved role.

Fix at the source: self-heal in the guard. If a token exists but the role never hydrated,
treat it as an invalid session — log out (clears the inconsistent localStorage keys) and
let the rest of the existing guard logic run against the now-consistent "logged out"
state. This is a ~5 line addition, no new state machine, and every downstream branch
(`requiresAuth` redirect, `GUEST_ONLY` redirect, fall-through `return true`) already does
the right thing once `isAuthenticated` is honestly `false`.

Alternative considered: special-case the `GUEST_ONLY` fallback to redirect to `/login`
instead of `/`. Rejected — it papers over the symptom on one branch only; a corrupt
session would still silently pass every other guard check pretending to be a valid
authenticated user (e.g. hitting a `requiresAuth` route would sail through the `1️⃣`
check with a `null` role and hit unrelated role-comparison bugs downstream).

## Steps

1. In `src/router/index.js`, right after `normalizedUserRole` is computed and before the
   `1️⃣` `requiresAuth` check, add a self-heal branch: if `authStore.isAuthenticated` is
   true but `normalizedUserRole` is `null`, call `authStore.logout()`. Comment explains why
   (token survived without its role — see this plan).
2. Confirm the existing checks below now behave correctly off the corrected state: no
   change needed to `1️⃣`, `GUEST_ONLY`, or the big authenticated block — they already read
   `authStore.isAuthenticated` live.
3. Manually verify in the deployed app (or local dev) by seeding the exact corrupt state
   (`localStorage.setItem('access_token', ...); localStorage.setItem('refresh_token', ...)`
   without `user_role`) and confirming "Log in" now reaches `/login` instead of no-oping.
4. Add a regression test in the router's test suite (create one if none exists) covering:
   token present + `user_role` absent + navigating to `/login` → lands on `/login`, and
   token present + `user_role` absent + navigating to a `requiresAuth` route → redirects to
   `/login`.

## Risks

- `authStore.logout()` makes a best-effort server-side revocation call
  (`POST logout/`) using whatever access token is present; if that token is only
  half-valid this call may 401/fail — it's wrapped in `.catch(() => {})` already, so it's
  silent and non-blocking either way.
- Any other code reading `authStore.token` directly without going through
  `isAuthenticated`/the guard (e.g. `services/api/api.js`, `stores/chat.js` read
  `localStorage.getItem('access_token')` directly as a fallback) won't be touched by this
  fix until the next navigation runs the guard. Acceptable — those reads are for attaching
  an `Authorization` header to a request that will simply 401 and hit the existing refresh
  path, not a silent dead end.

## Checks to run

- `npm run lint`
- `npm run build`
- `npx vitest run` (router test file, once added)
- Manual repro in a browser: seed the corrupt localStorage state described in Step 3,
  reload, click "Log in", confirm it lands on `/login`.
