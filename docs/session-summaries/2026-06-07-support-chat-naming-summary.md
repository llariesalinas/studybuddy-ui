# Support chat naming summary

Implemented a frontend display fix so support-ticket chat rooms are labeled as
Customer Support instead of using the ticket reporter's name as the room title.

The sidebar now shows Customer Support with CS initials for support rooms. The support
ticket details panel shows `You (Reporter Name)` when the reporter is the logged-in
profile, while admins/support users still see the actual reporter name. Normal
tutor/tutee chats keep the existing partner naming and Stats together panel.

Verification:

- `npm run build` passed after rerunning outside the sandbox because Vite/esbuild hit
  `spawn EPERM` in the sandbox.
