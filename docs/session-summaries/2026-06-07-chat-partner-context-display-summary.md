# Chat partner context display summary

Updated chat partner display so regular chat sidebars choose the other participant by
profile id instead of relying only on role/localStorage. The non-support right panel now
uses the backend `partner_context` values for avatar initials, partner name, and
subtitle, preserving Stats together from the same request-aware context.

Support rooms remain labeled as Customer Support with CS initials and reporter-aware
ticket details.

Verification:

- `npm run build` passed after rerunning outside the sandbox because Vite/esbuild hit
  `spawn EPERM` in the sandbox.
