---
title: Chat Accept / Reject pending sessions
date: 2026-06-14
status: Approved
spec: ../specs/2026-06-14-chat-accept-reject-design.md
---

# Chat Accept / Reject Pending Sessions — Implementation Plan

> **For agentic workers:** Use superpowers:subagent-driven-development to execute task-by-task.

**Goal:** Let a tutor accept or reject a pending session directly from the chat banner,
alongside the existing edit-location control (Option C — "Confirm & Accept").
**Stack:** Vue 3, Pinia, Django REST, Bootstrap 5
**Scope:** Frontend-only. Backend `approve`/`reject` endpoints already exist.

---

## Status / Progress Summary

- **Current status:** Approved — not started.
- **Tasks:** 0 / 2 complete.

## Changelog

- 2026-06-14: Plan created from approved spec.

---

## Task 1: Add `acceptBooking` / `rejectBooking` to the chat store

**Files:**
- Modify: `src/stores/chat.js`

- [ ] Step 1: Below `updatePendingLocation` (around `src/stores/chat.js:764`), add two
  functions mirroring its pattern (call endpoint via the authenticated `api` instance, then
  force-refresh rooms):
  ```js
  async function acceptBooking(bookingId) {
    const response = await api.post(`bookings/${bookingId}/approve/`)
    await fetchRooms({ force: true })
    return response.data
  }

  async function rejectBooking(bookingId) {
    const response = await api.post(`bookings/${bookingId}/reject/`)
    await fetchRooms({ force: true })
    return response.data
  }
  ```
- [ ] Step 2: Export both from the store's returned object, next to `updatePendingLocation`.
- [ ] Step 3: Verify — `npm run lint` passes clean.
- [ ] Step 4: Commit — `git commit -m "feat: add chat store accept/reject booking actions"`

## Task 2: Add tutor Accept / Reject controls to `ChatBanner.vue`

**Files:**
- Modify: `src/components/ChatBanner.vue`

- [ ] Step 1: In `<script setup>`, add `const accepting = ref(false)` and
  `const rejecting = ref(false)`. Reuse the existing `locationError`, `locationDraft`,
  and `editing` refs.
- [ ] Step 2: Add three handlers:
  - `confirmAndAccept()` (F2F): trim `locationDraft`; if empty set
    `locationError = 'Location is required.'` and return; if changed vs
    `bannerContext.preferred_location` call `chatStore.updatePendingLocation(id, loc)`;
    then `chatStore.acceptBooking(bannerContext.id)`. Wrap in try/finally toggling
    `accepting`; on error set `locationError = error?.response?.data?.error || 'Could not accept.'`.
  - `accept()` (online): toggle `accepting`, call `chatStore.acceptBooking(bannerContext.id)`,
    same error handling.
  - `reject()`: toggle `rejecting`, call `chatStore.rejectBooking(bannerContext.id)`,
    same error handling.
- [ ] Step 3: In the `pending_location` template, inside the existing tutor branch
  (`v-if="isTutor"` area, around `src/components/ChatBanner.vue:49-60`), render the Option C
  layout: the editable location chip (reuse existing Edit/Save flow), a
  `.chat-banner__btn--primary` button "Confirm & Accept" (`@click="confirmAndAccept"`,
  `:disabled="accepting"`, label `accepting ? 'Accepting…' : 'Confirm & Accept'`), and a
  `.chat-banner__btn--danger-text` button "Reject" (`@click="reject"`, `:disabled="rejecting"`).
  Leave the tutee branch (`Suggest change`) unchanged.
- [ ] Step 4: In the `pending` template (online, around `src/components/ChatBanner.vue:66-80`),
  add a tutor-only (`v-if="isTutor"`) action area with an "Accept" primary button
  (`@click="accept"`) and the "Reject" text button. Tutee keeps the "Waiting for confirmation"
  copy.
- [ ] Step 5: In `<style scoped>`, add `.chat-banner__btn--danger-text { color: var(--sb-danger-bs); font-weight: 600; }`
  and a `.chat-banner__loc-chip` rule using existing CSS variables only (no hardcoded hex).
- [ ] Step 6: Verify — `npm run lint` clean, `npm run build` succeeds, `npm run test` green.
- [ ] Step 7: Commit — `git commit -m "feat: tutor accept/reject pending session in chat banner"`

---

## Risks

- **Double-submit** if buttons aren't disabled during the request — mitigated by
  `accepting` / `rejecting` flags.
- **Stale booking** (accepted/rejected from another surface) returns a 400; surface
  `error.response.data.error` and let the forced `fetchRooms` reconcile the banner.
- **F2F approve without a location** is blocked client-side and server-side; the client check
  avoids a confusing round-trip.

## Checks to run

- `npm run lint` — clean.
- `npm run build` — succeeds.
- `npm run test` — existing suite green.
- Manual: tutor F2F → edit location → Confirm & Accept → banner flips to Confirmed; tutor
  online → Accept; tutor Reject → banner flips to Rejected; tutee sees no accept/reject.
