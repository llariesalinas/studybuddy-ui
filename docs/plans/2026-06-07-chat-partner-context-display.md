---
title: Chat partner context display
date: 2026-06-07
status: Done
spec:
---

# Chat partner context display

## Goal

Make normal chat context panels show the actual other participant for the logged-in
user, especially from the tutor side, while keeping support chats labeled as Customer
Support.

## Approach

Use profile-id based room partner selection in the chat store and use the backend
`partner_context` payload for the right-side non-support context panel. This avoids
stale role/localStorage display bugs.

## Steps

1. Keep support rooms labeled as Customer Support.
2. Select regular room partner names by comparing the logged-in profile id with
   `room.tutee` and `room.tutor`.
3. Render non-support context avatar/name/subtitle from `partner_context` when present.
4. Preserve Stats together from the existing backend counts.

## Risks

- If profile id is missing from auth/local storage, the store falls back to the old
  role-based behavior.
- Room list payloads may not include `partner_context`, so the store still needs a
  profile-id fallback for sidebar names.

## Checks to run

- `npm run build`
- Verify tutor-side chat context shows the tutee as the partner and retains Stats together.
