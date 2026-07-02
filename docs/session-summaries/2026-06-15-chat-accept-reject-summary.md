# Chat accept/reject pending sessions

## Summary

Implemented tutor-only accept/reject controls in the chat banner for pending booking requests.
Tutors can now approve or reject online requests from chat, and can confirm the F2F location before
accepting an in-person request.

## Changed

- Added `acceptBooking` and `rejectBooking` actions to `src/stores/chat.js`.
- Updated `src/components/ChatBanner.vue` with tutor-only pending request actions.
- Kept tutee behavior unchanged: waiting copy for online pending requests and suggest-change for
  F2F location.
- Added loading/disabled states and shared error handling for accept/reject failures.
- Added a preview artifact at `docs/artifacts/2026-06-15-chat-accept-reject-preview.html`.
- Refined the pending-request banner into a softer decision-card design with clearer hierarchy,
  contained action panels, and improved mobile stacking.

## Verification

- `npx eslint src/components/ChatBanner.vue src/stores/chat.js`
- `npm run build`
- `npm run test`

## Notes

- The implementation is frontend-only and uses the existing backend `approve` and `reject`
  endpoints from the approved plan.
