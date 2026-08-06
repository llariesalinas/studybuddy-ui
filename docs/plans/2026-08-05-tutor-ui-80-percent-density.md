---
title: Tutor-side UI at 80% density
date: 2026-08-05
status: Done
spec:
---

# Tutor-side UI at 80% density

## Goal

Extend the density system introduced for the Tutee role in `2cc9981`
(`docs/plans/2026-08-04-tutee-ui-80-percent-density.md`) to the Tutor role, so Tutor screens render
at exactly what the browser gives at 80% zoom. Admin/SuperAdmin stay at 100%.

## Approach

No new mechanism — the whole system already exists. `:root[data-sb-density='compact']` sets
`--sb-density-scale: 0.8` and `zoom: var(--sb-density-scale)`, which scales the entire render tree
including `<Teleport to="body">` overlays and `SbBgWash`. `src/stores/density.js` toggles the
attribute from a `watch(userRole, …, { immediate: true })` in `App.vue`.

Two pieces of work:

1. Add `'tutor'` to the compact-role set in `density.js`.
2. Redo the **`vh` consumer audit** for the files that become reachable at compact density. Root
   `zoom` does not rescale the initial containing block, so `vh` still resolves against the unzoomed
   `window.innerHeight` and any `vh`-based rule renders 20% short. `main.css` compensates with
   `--sb-vh-fix: calc(100vh / var(--sb-density-scale))`.

Substitution shapes (both already in use in `main.css`):

- `100vh` → `var(--sb-vh-fix)` — e.g. `calc(100vh - 7rem)` → `calc(var(--sb-vh-fix) - 7rem)`
- other `Nvh` → `calc(Nvh / var(--sb-density-scale))`

`px` terms inside the same `calc()`/`min()` are left alone — ambient `zoom` already scales those
correctly, which is what real 80% browser zoom produces.

Compensation rules live in `src/assets/main.css` rather than each view's scoped `<style>`, so all
density behavior stays in one place — same as the Tutee pass.

### `vh` consumer audit (newly Tutor-reachable)

| File | Selector | Current | Compensation |
|---|---|---|---|
| `TutorPreferenceSetup.vue` | `.min-vh-100` (Bootstrap utility on the page root, `:2`) | `min-height: 100vh !important` | `min-height: var(--sb-vh-fix) !important` |
| `TutorSubjectSetup.vue`, `TutorVerificationSetup.vue` | `.onboarding-page` (same class name in both) | `min-height: 100vh` | `min-height: var(--sb-vh-fix)` |
| `TutorProfile.vue` | `.tutor-profile-shell` | `min-height: 100vh` | `min-height: var(--sb-vh-fix)` |
| `TutorProfile.vue` | `.tutor-profile-shell .glass-modal` | `max-height: min(86vh, 780px)` | `max-height: min(calc(86vh / var(--sb-density-scale)), 780px)` |
| `TutorSchedule.vue` | `.modal-box` | `max-height: 88vh` | `max-height: calc(88vh / var(--sb-density-scale))` |
| `TutorWallet.vue` | `.wallet-shell` | `min-height: calc(100vh - 7rem)` | `min-height: calc(var(--sb-vh-fix) - 7rem)` |
| `AuthShell.vue` | `.sb-auth-page` | `min-height: 100vh` | `min-height: var(--sb-vh-fix)` |

**`.glass-modal` collision.** `main.css` already carries a global
`[data-sb-density='compact'] .glass-modal { max-height: calc(var(--sb-vh-fix) - 2.5rem) }` written
for `TuteeProfile.vue`. `TutorProfile.vue` reuses the class name (`:378`, `:448`, styled at `:1912`)
with a deliberately different cap. The scoped rule (`.glass-modal[data-v-…]`, 0-2-0) and that global
rule (0-2-0) tie on specificity, so the winner would depend on stylesheet injection order. The tutor
rule is therefore qualified through the shell (`.tutor-profile-shell .glass-modal`, 0-3-0) so it
wins deterministically. TutorProfile's modals are plain in-tree markup under `.tutor-profile-shell`
(`:2`), not Teleported, so the descendant selector holds.

**Already covered, no new rules.** Global class selectors already in `main.css` that start matching
Tutor pages for free once the attribute is set: `.vh-100` (App.vue authenticated shell),
`.sb-sidebar` (`AppSidebar`), `.sb-select-dialog` (`SbSelectModal`, used in 11 non-Tutee places
including `TutorBookingDetailsFlow.vue`), `.subject-dialog` (`SubjectPickerModal`, used by tutor
subject setup), `html`/`body`, `body > #app`.

**Verified to need nothing.** `TutorDashboard.vue`, `TutorPaymentScreen.vue`,
`TutorSessionsReports.vue`, `TutorBookingDetailsFlow.vue`, `TutorApplicationSubmitted.vue`,
`Chat.vue` — no `vh`/`dvh`/`svh` units and no `vh-100`-family utility classes.

**Out of scope.** Admin/SuperAdmin remain at 100%, so `admin.css`'s `.admin-route-shell`
(`calc(100vh - 72px)`), `AdminTutorApplications.vue` and `SuperAdminUserModal.vue` are untouched.

### Tutee-side gaps fixed in the same pass

Both were filed as "Tutor/Admin-only, unreachable at compact density" by the 2026-08-04 audit. The
router says otherwise — the file names read Tutor/Auth, but the routes are Tutee-role — so both have
been rendering 20% short for Tutees since `2cc9981`.

| File | Selector | Route / role | Fix |
|---|---|---|---|
| `TutorDetails.vue` | `.booking-page` (`:854`) | `/tutor/:id` — `role: 'Tutee'` (`src/router/index.js:97`) | `min-height: var(--sb-vh-fix)` |
| `AuthShell.vue` | `.sb-auth-page` (`:50`) | `/application-status` — `role: ['Tutor','Tutee']` (`src/router/index.js:130`) | `min-height: var(--sb-vh-fix)` (same row as the table above) |

`AuthShell` is also used by `Login`/`Register`/`ForgotPassword`/`ResetPassword`, which are public —
`userRole` is null there, density is `comfortable`, so the rule doesn't match. No regression.

## Steps

1. `src/stores/density.js` — replace the hardcoded `'tutee'` check in `syncFromRole` with a
   `COMPACT_ROLES` module constant (`Set(['tutee', 'tutor'])`). `setDensity` and the
   `data-sb-density` attribute contract are unchanged, and the store stays unpersisted (role remains
   the source of truth, so a persisted value would flash the wrong density after a role change).
2. `src/assets/main.css` — append the compensation rules from both tables to the existing
   `[data-sb-density='compact']` block, under a `/* Tutor-reachable vh consumers */` comment so the
   Tutee and Tutor audits stay legible as separate passes.
3. `src/stores/density.test.js` (new) — role→density mapping is now branching logic and the store
   had no test. Follows the existing Pinia store test shape (`src/stores/sidebar.test.js`).
4. `docs/plans/2026-08-04-tutee-ui-80-percent-density.md` — correct its audit for the two
   misclassified Tutee-reachable files above.

## Risks

- **`.glass-modal` specificity** — the one place this change can silently break an existing Tutee
  screen if the descendant qualifier is dropped or the global rule is edited instead of added to.
- **Generic class names.** `.onboarding-page` and `.modal-box` are scoped-`<style>` names that
  become effectively global once targeted from `main.css`. Re-verified at implementation time:
  `.modal-box` appears only in `TutorSchedule.vue`, `.onboarding-page` only in the two setup views,
  and neither has a media-query override of the compensated property.
- **Media queries.** Root `zoom` shifts the effective viewport width breakpoints match against —
  the one place root zoom diverges from real browser zoom. Tutor screens with responsive grids
  (`/tch-dashboard`, `/tch-availability`, `/tch-wallet`) need spot-checking at 1280 / 1440 / 1920.
- **Shared components at two densities.** `SbSelectModal`, `SubjectPickerModal`, `SbToast` and
  `SupportModal` now render under two compact roles and at 100% for Admin/SuperAdmin. The rules are
  all attribute-gated so this is safe by construction, but it doubles the states to eyeball when a
  shared overlay is touched later.

## Checks to run

- Done — `npm run test`: 83 passing (77 pre-existing + 6 new `density.test.js` cases).
- Done — `npm run build` and `npm run lint:eslint` clean. `npm run lint` still exits 1 on oxlint's
  `no-unused-vars` for `draftSubjectCodes` in `src/composables/useSubjectCatalog.js`, which was last
  touched in `d85aaa6` and is unrelated to this change.
- Done — DOM measurement in Chrome (`localhost:5174`, `npm run dev`, no logged-in session), the same
  method the Tutee pass used. With `data-sb-density="compact"` set and `window.innerHeight` at 742,
  every new selector landed within 0.4px of its target:

  | Selector | Target | Measured |
  |---|---|---|
  | `.min-vh-100`, `.onboarding-page`, `.sb-auth-page`, `.tutor-profile-shell`, `.booking-page` | 742 | 742.4 |
  | `.wallet-shell` (`- 7rem`) | 652.4 | 652.8 |
  | `.modal-box` (88vh) | 653.0 | 653.3 |
  | `.tutor-profile-shell .glass-modal` (`min(86vh, 780px)` → 780px wins) | 624.0 | 624.0 |
  | bare `.glass-modal` (Tutee rule, regression check) | 710.0 | 710.4 |

  The last two rows are the specificity check: the shell-qualified tutor rule and the bare Tutee
  rule resolve to different, correct caps. Every selector measured 0 with the attribute removed
  (except `.min-vh-100`, which keeps Bootstrap's own baseline), confirming the rules are inert at
  `comfortable`.
- Done — manual walkthrough, logged in, run by the user 2026-08-05: confirmed the UI now renders
  identical to 80% browser zoom. This is the check that was left pending on the Tutee plan since
  `2cc9981`; it now covers both passes. The list below is what was walked:
  - `/tch-dashboard`, `/tutor-profile`, `/tch-availability`, `/tch-payments`, `/tch-wallet`,
    `/booking-details/:id`, `/reports`, `/chat`, `/application-status`.
  - Onboarding chain `/tutor-setup` → `/tutor-setup/subjects` → `/tutor-setup/verification`.
  - `AppSidebar` fills top to bottom with no gap at the bottom at several window heights — that gap
    is the signature failure mode of a missed `vh` rule, and how the `.vh-100` miss was caught last
    round.
  - `TutorProfile`'s course/year and subject modals (the `.glass-modal` collision case) and
    `TutorSchedule`'s `.modal-box` time picker — each must scale with the page, stay centered, and
    not clip; scroll to the bottom of each to confirm the max-height.
  - `TutorWallet`'s `.wallet-shell` leaves no dead space under the last card.
  - `/tch-dashboard`, `/tch-availability`, `/tch-wallet` at 1280 / 1440 / 1920 for premature
    responsive collapse.
  - Toggle light/dark — `data-sb-theme` and `data-sb-density` are independent and must not interact.
- Regression / isolation:
  - As **Tutee**: `/tutor/:id` and `/application-status` now render full height; re-walk
    `/dashboard`, `/find-tutors`, `/book`.
  - As **Admin** and **SuperAdmin**: everything at 100%, `data-sb-density` absent from `<html>`.
  - Public `/login`, `/register` at 100% — confirms the `AuthShell` rule is inert when logged out.
  - Log out from Tutor and back in as Admin in the same tab with no hard refresh — density must flip
    immediately (what the `watch` on `userRole` buys).
- Fallback if a selector still measures short: same DOM-measurement method as the Tutee pass — in
  Chrome, apply the class to a test element with `data-sb-density="compact"` set and confirm
  `getBoundingClientRect().bottom` lands within ~2px of `window.innerHeight`.
