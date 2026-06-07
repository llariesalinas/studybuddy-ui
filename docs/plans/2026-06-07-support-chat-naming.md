---
title: Support chat naming
date: 2026-06-07
status: Done
spec:
---

# Support chat naming

## Goal

Make support-ticket chat rooms display as Customer Support instead of showing the
reporter's own name, while preserving normal tutor/tutee chat partner names and
Stats together.

## Approach

Keep this as a frontend display fix. Support rooms will use support-specific labels
and initials in the chat store/view, while regular rooms keep the existing role-based
partner naming and context panel behavior.

## Steps

1. Return `Customer Support` from `getRoomPartnerName` for support rooms.
2. Return `CS` initials for support rooms.
3. Show `You (Name)` as reporter when the logged-in profile created the support ticket.
4. Leave non-support room naming and Stats together unchanged.

## Risks

- The support ticket still stores the reporter internally; only display labels change.
- If `profile_id` is missing from auth/local storage, reporter falls back to the stored
  reporter name.

## Checks to run

- `npm run build`
- Verify a reporter sees Customer Support in the sidebar and You (Name) in ticket details.
- Verify normal tutor/tutee chats still show Stats together.
