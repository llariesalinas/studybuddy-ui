# Session summary — Tutor-side UI at 80% density

**Date:** 2026-08-05
**Plan:** [2026-08-05-tutor-ui-80-percent-density.md](../plans/2026-08-05-tutor-ui-80-percent-density.md)
**Also closes:** [2026-08-04-tutee-ui-80-percent-density.md](../plans/2026-08-04-tutee-ui-80-percent-density.md)
**Branch:** `fix/Refactor-tutee-side-UI`
**Commits:** uncommitted at time of writing (working tree on the branch above)

## What shipped vs. planned

Shipped as planned, with no deviations.

The starting point mattered: commit `2cc9981` ("Refactored tutee side UI") restyled nothing — it
introduced a **density system**. `:root[data-sb-density='compact']` sets `--sb-density-scale: 0.8`
and `zoom: var(--sb-density-scale)`, which scales the whole render tree including the 13
`<Teleport to="body">` overlays and `SbBgWash` that no wrapper `div` could reach. So extending it to
Tutor was one line in the store; the actual work was redoing the `vh` compensation audit for the
newly-reachable files.

- `src/stores/density.js` — the hardcoded `'tutee'` check in `syncFromRole` replaced with a
  `COMPACT_ROLES = new Set(['tutee', 'tutor'])` module constant. `setDensity` and the
  `data-sb-density` attribute contract unchanged; the store stays unpersisted (role is the source of
  truth, so a persisted value would flash the wrong density after a role change).
- `src/assets/main.css` — `--sb-vh-fix` compensation for every newly-reachable `vh` consumer:
  `.min-vh-100` (TutorPreferenceSetup's Bootstrap page root), `.onboarding-page` (shared name across
  both setup views), `.tutor-profile-shell`, `.wallet-shell` (`- 7rem`), `.modal-box`
  (TutorSchedule, 88vh), and `.tutor-profile-shell .glass-modal` (`min(86vh, 780px)`).
- `src/stores/density.test.js` (new) — 6 Vitest cases. The store had no test and role→density is now
  branching logic: both compact roles, both comfortable roles, logged-out (`null`/`undefined`/`''`),
  and case-insensitivity.

Nothing needed changing in `TutorDashboard.vue`, `TutorPaymentScreen.vue`,
`TutorSessionsReports.vue`, `TutorBookingDetailsFlow.vue`, `TutorApplicationSubmitted.vue` or
`Chat.vue` — no `vh`/`dvh`/`svh` units and no `vh-100`-family utility classes. Admin/SuperAdmin stay
at 100%, so `admin.css`'s `.admin-route-shell`, `AdminTutorApplications.vue` and
`SuperAdminUserModal.vue` were left alone. `.vh-100`, `.sb-sidebar`, `.sb-select-dialog` and
`.subject-dialog` started matching Tutor pages for free — they were already global rules.

## Two findings worth keeping

**The `.glass-modal` specificity trap.** `main.css` already carried a global
`[data-sb-density='compact'] .glass-modal` rule written for `TuteeProfile.vue`.
`TutorProfile.vue` reuses the same class name with a deliberately different cap. The scoped rule
(`.glass-modal[data-v-…]`) and the global density rule both compute to 0-2-0, so the winner would
have depended on stylesheet injection order — silent, and only on one screen. The tutor rule is
therefore qualified through `.tutor-profile-shell` (0-3-0). Measured proof below.

**Two Tutee-reachable files misclassified by the 2026-08-04 audit.** `TutorDetails.vue` and
`AuthShell.vue` were filed as "Tutor/Admin-only, unreachable at compact density" by reading their
filenames rather than their routes — but `/tutor/:id` is `role: 'Tutee'` and `/application-status`
is `role: ['Tutor', 'Tutee']`. Both had been rendering 20% short for Tutees since `2cc9981`. Fixed
here and the audit table corrected in place. `AuthShell`'s rule stays inert on the public auth
screens: `userRole` is null there, so density is never `compact`.

## Checks run

- `npm run test` — 83 passing (77 pre-existing + 6 new).
- `npm run build` — clean. `npm run lint:eslint` — clean. `npm run lint` exits 1 on oxlint's
  `no-unused-vars` for `draftSubjectCodes` in `src/composables/useSubjectCatalog.js`, last touched
  in `d85aaa6` — pre-existing and unrelated.
- DOM measurement in Chrome (`localhost:5174`, no logged-in session), the method the Tutee pass
  used. At `window.innerHeight = 742`, every new selector landed within 0.4px of target:
  `.min-vh-100` / `.onboarding-page` / `.sb-auth-page` / `.tutor-profile-shell` / `.booking-page`
  742.4 (target 742); `.wallet-shell` 652.8 (652.4); `.modal-box` 653.3 (653.0);
  `.tutor-profile-shell .glass-modal` 624.0 (624.0); bare `.glass-modal` 710.4 (710.0). The last two
  are the specificity check — the shell-qualified tutor rule and the bare Tutee rule resolve to
  different, correct caps. All measured 0 with the attribute removed (except `.min-vh-100`, which
  keeps Bootstrap's baseline), confirming the rules are inert at `comfortable`.
- Visual: the user ran the logged-in walkthrough and confirmed the UI now renders identical to 80%
  browser zoom. This was the check left pending on the Tutee plan since `2cc9981`; it covered both
  passes, so both plans move to Done.
