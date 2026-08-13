---
title: Corrupt auth session guard fix
date: 2026-08-13
plan: ../plans/2026-08-13-corrupt-auth-session-guard-fix.md
---

# Corrupt auth session guard fix — summary

## What was reported

"I can't click the buttons, I can't log in, it won't let me" on
`https://studybuddy-peertutoring.vercel.app/`.

## Diagnosis (Claude in Chrome)

Reproduced live: clicking "Log in" / "Get started" on the landing page did nothing — no
navigation, no console error, no failed network request.

Root cause traced to `localStorage`: an `access_token` / `refresh_token` pair was present
without the matching `user_role` key. `authStore.isAuthenticated` is `computed(() =>
!!token.value)`, so the app believed the session was valid, but `user`/`userRole` never
hydrated. The router's `GUEST_ONLY_ROUTE_NAMES` guard (`src/router/index.js`) redirects an
authenticated user away from `/login` based on role — with no role to branch on, it fell
through to `return '/'`. Pushing `/login` while already on `/` resolved as a same-location
no-op in Vue Router, so the buttons looked dead with zero signal of why.

Confirmed by clearing the two stale keys and reloading: "Log in" worked immediately.

## What shipped

- `src/router/index.js`: added a self-heal branch in the global nav guard — if
  `authStore.isAuthenticated` is true but the role never resolved, call
  `authStore.logout()` before the existing checks run, so the rest of the guard (which
  already handles the logged-out case correctly) takes over instead of looping back to the
  same page.
- `src/router/index.test.js` (new): 3 regression cases — guest-only route self-heals and
  lands on `/login`, a `requiresAuth` route self-heals and redirects to `/login`, and a
  real resolved-role session is left untouched.

## Deviations from the plan

None. Implemented as designed (self-heal at the guard, not a special-cased redirect
target) — the plan's "alternative considered" section explains why the special-case
approach was rejected.

## Checks run

- `npm run lint` — clean (2 pre-existing errors in `make_algo_pptx.cjs`/`.js`, untouched
  by this change).
- `npm run build` — succeeds.
- `npx vitest run` — 212 passed, 3 pre-existing failures in `src/assets/tokens.test.js`
  (untouched by this change), all 3 new router tests pass.
- Manual verification against the live deployed site via Claude in Chrome: seeded the
  corrupt localStorage state, confirmed "Log in" no-ops before the fix and reaches
  `/login` after clearing the stale keys (the fix's effective end state).

## Not pushed

Changes are local only (uncommitted, on `admin-review-panel-catalog-fixes` branch pending
this being reviewed) — no push happened without confirmation, per project rules.
