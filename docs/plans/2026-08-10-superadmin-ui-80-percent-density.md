---
title: SuperAdmin-side UI at 80% density
date: 2026-08-10
status: In Progress
spec:
---

# SuperAdmin-side UI at 80% density

## Goal

Extend the density system introduced for Tutee (`2cc9981`,
`docs/plans/2026-08-04-tutee-ui-80-percent-density.md`) and Tutor
(`docs/plans/2026-08-05-tutor-ui-80-percent-density.md`) to the SuperAdmin role, so SuperAdmin
screens render at exactly what the browser gives at 80% zoom. Admin stays at 100%.

## Approach

No new mechanism — the system already exists end to end. `:root[data-sb-density='compact']` sets
`--sb-density-scale: 0.8` and `zoom: var(--sb-density-scale)`, which scales the entire render tree
including `<Teleport to="body">` overlays and `SbBgWash`. `src/stores/density.js` toggles the
attribute from a `watch(userRole, …, { immediate: true })` in `App.vue` (`:635`), so density is
driven by the authenticated role rather than the URL and flips on login/logout with no reload.

Two pieces of work, same as the Tutor pass:

1. Add `'superadmin'` to `COMPACT_ROLES` in `density.js`.
2. Redo the **`vh` consumer audit** for the files that become reachable at compact density. Root
   `zoom` does not rescale the initial containing block, so `vh` still resolves against the unzoomed
   `window.innerHeight` and any `vh`-based rule renders 20% short. `main.css` compensates with
   `--sb-vh-fix: calc(100vh / var(--sb-density-scale))`.

Substitution shapes (both already in use in `main.css`):

- `100vh` → `var(--sb-vh-fix)` — e.g. `calc(100vh - 48px)` → `calc(var(--sb-vh-fix) - 48px)`
- other `Nvh` → `calc(Nvh / var(--sb-density-scale))`

`px` terms inside the same `calc()`/`min()` are left alone — ambient `zoom` already scales those
correctly, which is what real 80% browser zoom produces.

Compensation rules live in `src/assets/main.css` rather than each view's scoped `<style>`, so all
density behavior stays in one place — same as the Tutee and Tutor passes.

**Scope: SuperAdmin only.** Admin remains at 100%. Views shared by both roles
(`AdminCourseCatalog.vue`, `AdminTutorApplications.vue`, `AdminSupport.vue`) therefore render at two
densities depending on who is logged in. Safe by construction: every compensation rule is gated on
the `data-sb-density='compact'` attribute, which is never set for Admin.

### `vh` consumer audit (newly SuperAdmin-reachable)

SuperAdmin routes (`src/router/index.js`, admin block `:178-227` + superadmin block `:229-259`):
`/superadmin/dashboard`, `/superadmin/institutions`, `/superadmin/users`, `/superadmin/reports`,
`/superadmin/support`, `/superadmin/algorithm-demo`, `/admin/course-catalog`,
`/admin/tutor-applications`, plus the shared `/chat`.

Only two `vh` consumers become reachable:

| File | Selector | Current | Compensation |
|---|---|---|---|
| `AdminTutorApplications.vue:590` | `.admin-applications` | `min-height: 100vh` | `min-height: var(--sb-vh-fix)` |
| `SuperAdminUserModal.vue:831` | `.superadmin-user-modal` | `max-height: min(760px, calc(100vh - 48px))` | `max-height: min(760px, calc(var(--sb-vh-fix) - 48px))` |

Both selectors were verified unique to their own file and free of any media-query override of the
compensated property (`SuperAdminUserModal.vue`'s one `@media (max-width: 640px)` block at `:1437`
touches alignment and grid columns only).

**Already covered, no new rules.** Global selectors already in `main.css` that start matching
SuperAdmin pages for free once the attribute is set: `.vh-100` (the authenticated shell,
`App.vue:12`), `.sb-sidebar` (`AppSidebar.vue:169`), `.sb-select-dialog` (`SbSelectModal`, used by
`SuperAdminAlgorithmDemo.vue`), `.subject-dialog` (`SubjectPickerModal`, used by
`AdminCourseCatalog.vue`), `html`/`body`, `body > #app`.

**Verified to need nothing** — no `vh`/`dvh`/`svh` units and no `vh-100`-family utility classes:
`SuperAdminDashboard.vue`, `SuperAdminUsers.vue`, `SuperAdminReports.vue`,
`SuperAdminAlgorithmDemo.vue` and `src/components/algorithm-demo/*`, `AdminInstitutions.vue`,
`AdminCourseCatalog.vue`, `AdminSupport.vue` (fixed `height: 520px` card), `SupportModal.vue`,
`Chat.vue`. Their root containers are `min-height: 100%` or Bootstrap `p-4`, which inherit correctly.

**Out of scope.** Admin stays at 100%, so `src/assets/admin.css` (`.admin-route-shell`,
`calc(100vh - 72px)`) is untouched — it is dead code besides: never imported by `main.js`, and
`.admin-route-shell` appears in no template. Deleting it is a separate cleanup.

## Steps

1. `src/stores/density.js` — add `'superadmin'` to the `COMPACT_ROLES` set; comment updated to
   "Admin stays at 100%." The store stays unpersisted (role remains the source of truth, so a
   persisted value would flash the wrong density after a role change).
2. `src/assets/main.css` — append the two compensation rules to the existing
   `[data-sb-density='compact']` block under a `/* SuperAdmin-reachable vh consumers … */` comment,
   before the trailing `@media (max-width: 640px)` block, so the three audit passes stay legible as
   separate sections.
3. `src/stores/density.test.js` — the existing cases asserted the opposite of the new behavior:
   `'superadmin'` added to the compact loop, the comfortable case narrowed to `'admin'` alone, and
   the case-insensitivity case flipped (`'SuperAdmin'` → compact, with `'Admin'` added to keep a
   comfortable-side assertion).

## Risks

- **Generic class name.** `.admin-applications` is a scoped-`<style>` name that becomes effectively
  global once targeted from `main.css`. Re-verified at implementation time: it appears only in
  `AdminTutorApplications.vue` (`:2` and `:590`).
- **Media queries.** Root `zoom` shifts the effective viewport width breakpoints match against — the
  one place root zoom diverges from real browser zoom. The SuperAdmin dashboard/reports grids and the
  `AdminUsers`/`AdminInstitutions` Bootstrap tables need spot-checking at 1280 / 1440 / 1920 for
  premature responsive collapse or horizontal scroll.
- **Shared components at three densities.** `SbSelectModal`, `SubjectPickerModal`, `SbToast`,
  `SupportModal` and the three shared Admin/SuperAdmin views now render compact under three roles and
  at 100% for Admin. Attribute gating makes this safe, but it adds a state to eyeball whenever those
  views are touched later.
- **Requires a full page reload to take effect in a running dev session.** `syncFromRole` runs from
  `watch(userRole, …, { immediate: true })` — once at `App.vue` setup, then only when the role
  *changes*. `density.js` has no `acceptHMRUpdate()` handler, so Vite HMR leaves the already-created
  Pinia store instance (closing over the old `COMPACT_ROLES`) alive for the rest of the session. An
  already-logged-in SuperAdmin therefore keeps seeing 100% until a hard refresh. Affects development
  only — real users load the new bundle from scratch. Confirmed as the cause of the first "no change"
  report on 2026-08-10.
- **Dead selector nearby** (informational): `main.css:81-84` targets
  `[data-sb-density='compact'] html, … body`. The attribute is set on `<html>` itself, so the `html`
  half can never match; only the `body` half does work, and `body > #app` (`:86`) covers the same
  ground. Harmless, but don't copy that shape.

## Checks to run

- Done — `npm run test`: 163 passing across 23 files.
- Done — `npm run build` and `npm run lint:eslint` clean. `npm run lint` still exits 1 on oxlint's
  pre-existing `no-undef` errors in `make_algo_pptx.*`, unrelated to this change.
- Done — **DOM measurement** in Chrome (`localhost:5173`, `npm run dev`, no logged-in session), the
  same method both prior passes used. With `data-sb-density="compact"` set and `window.innerHeight`
  at 720:

  | Selector | Target | Measured |
  |---|---|---|
  | `.admin-applications` | 720 | 720 |
  | `.superadmin-user-modal` | 608 | 608 |

  Note on the second row: `getBoundingClientRect()` returns **post-zoom** px, but the `760px` cap in
  `min()` is a CSS px value that root `zoom` then scales. `--sb-vh-fix` resolves to `720 / 0.8 = 900`,
  so the cap is `min(760px, 852px) = 760px` CSS → `760 × 0.8 = 608px` on screen. That is exactly what
  real 80% browser zoom produces, which is the whole point of leaving `px` terms uncompensated — do
  not "fix" this row to `innerHeight - 48`. Both selectors measured inert with the attribute removed
  (`min-height: 0px`, `max-height: none`).
- Pending — **manual walkthrough, logged in as SuperAdmin**: `/superadmin/dashboard`,
  `/superadmin/institutions`, `/superadmin/users`, `/superadmin/reports`, `/superadmin/support`,
  `/superadmin/algorithm-demo`, `/admin/course-catalog`, `/admin/tutor-applications`.
  - `AppSidebar` fills top to bottom with no gap at the bottom at several window heights — that gap
    is the signature failure mode of a missed `vh` rule, and how the `.vh-100` miss was caught in the
    Tutee round.
  - `SuperAdminUserModal` from `/superadmin/users`, the subject picker from `/admin/course-catalog`,
    and the `SbSelectModal` on `/superadmin/algorithm-demo` — each must scale with the page, stay
    centered, and scroll to the bottom without clipping.
  - `/admin/tutor-applications` leaves no dead space under the last card.
  - `/superadmin/dashboard`, `/superadmin/reports`, `/superadmin/users` at 1280 / 1440 / 1920.
  - Toggle light/dark — `data-sb-theme` and `data-sb-density` are independent and must not interact.
- Pending — regression / isolation:
  - As **Admin**: everything at 100%, `data-sb-density` absent from `<html>`; re-walk
    `/admin/dashboard`, `/admin/users`, `/admin/withdrawals`, `/admin/reports` and the three shared
    views to confirm they are unchanged.
  - As **Tutee** and **Tutor**: spot-check `/dashboard` and `/tch-dashboard` — unchanged.
  - Public `/login`, `/register` at 100%.
  - Log out from SuperAdmin and back in as Admin in the same tab with no hard refresh — density must
    flip immediately (what the `watch` on `userRole` buys).
