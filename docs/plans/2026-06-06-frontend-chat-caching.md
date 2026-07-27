---
title: Frontend and chat caching
date: 2026-06-06
status: Done
spec:
---

# Frontend and chat caching

## Status & Progress Summary

**Status (2026-07-17): Done.** This plan predates the living-plan convention and never had a
tracked summary. Verified against the codebase during a plan-vs-code implementation audit:
`src/services/api/cache.js` implements the cached-GET helper (`cachedGet`, TTL constants),
`src/stores/catalog.js` consumes it, `src/stores/chat.js` has `cachedAt`/`readChatCache`/
`getRoomsCacheKey`, `after_id` is implemented in `backend/studybuddy/chat/views.py`, and
`package.json` has the `"test": "vitest run"` script the plan's Step 0 required. Frontmatter
status was never flipped from Approved.

## Goal

Improve load speed for stable reference data and slow messaging views while keeping
freshness-sensitive chat behavior accurate.

## Approach

Frontend-first caching for the fastest perceived improvement. Stable catalog data uses
short-TTL caching; messaging uses session-only stale-while-revalidate so recent rooms and
messages render immediately before syncing with REST + WebSocket. A small backend change
(`after_id`) enables incremental history sync.

A custom cache helper is used rather than the project's existing
`pinia-plugin-persistedstate` because we need TTL, force-refresh, in-flight request dedup,
and user-scoped keys the plugin doesn't provide. Cache keys follow the existing `sb-*`
sessionStorage convention already used in stores like `stores/initialbookingprefs.js`.

The Django backend is in-tree at `backend/studybuddy/chat/`.

## Steps

0. **Prerequisite — frontend test harness.** Add `vitest`, `@vue/test-utils`, and `jsdom`
   as devDependencies, a `vitest.config.js` (or test block in the Vite config), and a
   `"test": "vitest run"` script in `package.json`. Verify with one trivial passing test.
   (No test runner exists today.)

1. **Shared cached GET helper** around the Axios client (`src/services/api/api.js`): TTL,
   force-refresh flag, `sessionStorage` backing, user-scoped keys (user id from the auth
   store / `localStorage` `user_id`), path normalization via the existing `getApiPath()`
   (`api.js:28`), and in-flight request dedup. Expose `clearCache(scope)` for logout. Add
   TTL constants to `src/config.js` following the existing `*_MS` style (no magic numbers).

2. **Catalog/reference store** for stable endpoints: `subjects/`, `courses/`,
   `partner-institutions/`, `payment-methods/`. Treat `wallet/receiving-institutions/` as
   provider-keyed (cache per `provider`). Exclude `/tutor/subjects/` — it is per-tutor and
   mutable, not catalog.

3. **Replace duplicate direct catalog calls** with the store/helper at these sites:
   `Register.vue:153`, `PreferenceSetup.vue:390-391`, `FindTutors.vue:564`,
   `InitialBooking.vue:267`, `TuteeProfile.vue:850,862`, `TutorProfile.vue:1019,1031`
   (NOT `:992`, which is the per-tutor `/tutor/subjects/`), `PaymentScreenTutee.vue:210`,
   `PostSessionPaymentView.vue:255`, `wallet.js:67`.

4. **Session-only chat caching** in `src/stores/chat.js`: cache the first room-list page
   (`fetchRooms`) and each room's recent history (`fetchHistory`), keyed per user with
   `sb-` keys. Persist only confirmed, non-pending messages (strip
   `pending`/`failed`/`temp_id`).

5. **On room select** (`selectRoom`, `chat.js:270`): render cached messages immediately,
   connect the WebSocket, mark the room read, then sync fresh data in the background.
   `fetchHistory` currently wipes `messages` first (`chat.js:254`) — change it to reconcile
   against the cache instead.

6. **Backend: optional `after_id` on history.** In
   `backend/studybuddy/chat/views.py:150` `get_message_history`, accept `?after_id=` and,
   when present, return `room.messages.filter(id__gt=after_id).order_by('created_at')[:50]`.
   Preserve the existing array response shape (frontend does `response.data.map(...)`). No
   URL change needed (`chat/urls.py:7`). Frontend passes `after_id` only when a cached
   high-water mark exists.

7. **Cache reconciliation** after WebSocket events, send/retry (`sendViaRest`), read
   receipts, `room_updated`/`booking_context_updated`, `updatePendingLocation`, and logout.
   Explicitly wire `auth.js:175` `logout()` (and the login/user-switch path) to call the
   helper's `clearCache()` and the chat store's `disconnectAll()` so no prior-user data
   lingers or flashes on a shared device.

8. **Tests.** Frontend (vitest): cache hit, TTL expiry, stale-while-revalidate, dedup,
   malformed-cache recovery, pending-message exclusion. Backend (pytest, append to
   `studybuddy/tests.py::ChatFeatureTests`): normal history load,
   `history/?after_id=...` incremental, unauthorized history access (403), and
   system-message serialization with a null sender.

## Risks

- Chat read state can briefly look stale until the background refresh reconciles exact
  unread counts.
- SessionStorage still stores recent message content until the browser session ends, so
  logout and user-switch cache clearing must be reliable (Step 7).
- Incremental history sync can create duplicate messages if message identity and
  pending-message replacement are not handled consistently (reuse `addOrReplaceMessage`,
  `chat.js:144`).
- Catalog data can be stale within the selected TTL if admin changes happen immediately
  before a user loads a page.
- Cache invalidation after mutations must stay explicit so updates do not leave old data
  visible.
- Optimistic/pending messages must be excluded from the cache or they resurrect as
  permanently pending/failed on reload (`sendMessage`, `chat.js:464`).
- Incremental `after_id` sync will not reflect edits/deletes to messages below the cached
  high-water mark until a full refresh.

## Checks to run

- `npm run lint` should pass without new lint errors.
- `npm run build` should complete successfully.
- `npm run test` (new vitest) — cache unit tests pass.
- `pytest studybuddy/tests.py::ChatFeatureTests` (from `backend/`) should pass, including
  new coverage for normal history loading, `history/?after_id=...`, unauthorized history
  access, and system-message serialization.

## Changelog

- 2026-06-06: Plan written and approved.
- 2026-07-17: Verified implemented during a plan-vs-code implementation audit; frontmatter
  status corrected from Approved to Done. Added this Status & Progress Summary/Changelog
  retroactively per the living-plan convention.
