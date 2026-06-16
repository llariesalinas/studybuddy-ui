# Session Summary - Global aurora/blur performance cleanup

**Date:** 2026-06-07
**Scope:** All StudyBuddy frontend routes and shared UI surfaces

## What shipped

Removed the remaining compositor-heavy aurora and blur effects globally after confirming they were contributing to sluggish scrolling and GPU/DWM load.

- Removed aurora tokens, fixed full-viewport gradient layers, and no-op aurora pointer-motion hooks from the shared app shell.
- Removed `backdrop-filter`, `-webkit-backdrop-filter`, and `filter: blur(...)` from shared CSS, admin surfaces, chat banner, support/select modals, landing page, profile pages, tutor dashboard, tutor sessions reports, chat, and tutor wallet.
- Replaced glass/blur surfaces with cheaper solid or translucent backgrounds, borders, restrained shadows, and static gradients where useful.
- Kept functional fixed overlays for modals/popovers and kept transient loading indicators such as submit spinners and wallet refresh rotation.
- Kept Vue DevTools opt-in only with `VITE_ENABLE_VUE_DEVTOOLS=true`, so default localhost does not inject the devtools overlay.

## Verification

- Static scan: no `backdrop-filter`, `-webkit-backdrop-filter`, `filter: blur`, or word-boundary `aurora` matches remain in `src`.
- `npm run build` - PASS.
- Browser audits covered `/tch-dashboard`, `/tch-wallet`, `/tch-profile`, `/tutee-profile`, `/`, and a support modal flow:
  - no computed blur/backdrop-filter layers
  - no Vue DevTools nodes by default
  - no idle active animations
  - no console warnings/errors
- Focused dashboard scroll timing with the tab visible: median `17ms`, p95 `18ms`, max `22ms`.

## Notes

- The earlier static-gradient aurora fix reduced pointer-driven jank; this follow-up removes the aurora/blur design pattern globally.
- Visual depth is now carried by solid/tinted surfaces, borders, shadows, and static gradients rather than live blur compositing.
- Remaining infinite animation matches are expected transient indicators: auth submit spinners and the wallet refresh icon while loading.
