---
title: Tutee-side UI at 80% density
date: 2026-08-04
status: Done
spec:
---

# Tutee-side UI at 80% density

## Goal

Tutee screens read as oversized. The target is exactly what the browser gives at 80% zoom,
scoped to the Tutee role only — Tutor/Admin/SuperAdmin rendering is untouched.

## Approach

Zoom lives on `:root`, gated by a `data-sb-density="compact"` attribute that
`src/stores/density.js` sets/removes from a `watch(userRole, ..., { immediate: true })` in
`App.vue`. This was evaluated against scaling a wrapper `<div>` inside `App.vue` instead
(`.app-scale-root` / `.app-scale-viewport`) and rejected before any wrapper code was written:
the 14 `<Teleport to="body">` overlays in the app render as children of `<body>`, outside any
non-root wrapper, and `SbBgWash` sits outside the wrapper by design — both would render
unscaled, out of proportion with the rest of the page. Root-level `zoom` covers both for free,
since `zoom`'s visual scaling cascades to the whole render tree under `:root` regardless of
where a node lives in the DOM (confirmed empirically — an unwrapped page element scaled
correctly alongside everything else). A wrapper using `transform: scale()` instead of `zoom`
was also considered and rejected for the same reason: `transform` doesn't apply to Teleported
siblings either, so it reintroduces the same escape problem `zoom`-on-`:root` avoids.

**`vh` needed a second pass.** The initial implementation assumed `zoom` on `:root` rescales
the initial containing block the way real browser zoom does, so `vh`/`vw` would "just work."
That's false in this Chrome build: setting `zoom: 0.8` on `:root` and measuring a
`height: 100vh` test element showed `window.innerHeight` unchanged and the element rendering
at exactly `innerHeight × 0.8` — 20% short of the visible viewport, the same failure mode the
wrapper approach had. (Neither `transform: scale()` fixes this either — no CSS transform
changes what `vh` resolves against.) This is the plan's own documented Fallback trigger, and
main.css now applies it directly: a `--sb-vh-fix: calc(100vh / var(--sb-density-scale))` custom
property, substituted into every Tutee-reachable `vh`-based rule found in the audit below, so
each nets out to the same visual size real 80% browser zoom would produce (px terms in the same
`calc()` are left alone since ambient `zoom` already scales those correctly). `<Teleport>`
overlays and `SbBgWash` needed no such fix — confirmed via the same empirical method.

`density.js` is a small Pinia store (`density` ref + `setDensity`/`syncFromRole`). It is
deliberately not persisted — role is the source of truth, so a persisted value would flash the
wrong density after a role change (e.g. an Admin impersonation flow or account switch).

### `vh` consumer audit (Tutee-reachable only)

| File | Selector | Compensated in `main.css` |
|---|---|---|
| `main.css` | `html, body`, `body > #app` | `min-height: var(--sb-vh-fix)` |
| `App.vue` | `.vh-100` (Bootstrap utility, authenticated shell root) | `height: var(--sb-vh-fix) !important` |
| `AppSidebar.vue` | `.sb-sidebar` | `height: var(--sb-vh-fix)` |
| `Dashboard.vue` | `.weekly-panel`, `.recommendation-panel` | `clamp(460px, calc(var(--sb-vh-fix) - 230px), 600px)` |
| `TuteeProfile.vue` | `.tutee-profile-shell` | `min-height: var(--sb-vh-fix)` |
| `TuteeProfile.vue`, `SbSelectModal.vue`, `SubjectPickerModal.vue` | `.glass-modal`, `.sb-select-dialog`, `.subject-dialog` | `max-height: calc(var(--sb-vh-fix) - 2.5rem)`, `- 1.5rem` at `<640px` |
| `BookingDatePicker.vue`, `BookingTimePicker.vue` | `.date-modal`, `.time-modal` | `max-height: calc(var(--sb-vh-fix) - 2rem)` |
| `RatingStackModal.vue` | `.rating-stack-modal` | `max-height: calc(98vh / var(--sb-density-scale))` |
| `TutorDetails.vue` | `.booking-page` | `min-height: var(--sb-vh-fix)` — added 2026-08-05, see below |
| `AuthShell.vue` | `.sb-auth-page` | `min-height: var(--sb-vh-fix)` — added 2026-08-05, see below |

The initial audit only searched `.vue` `<style>` blocks and missed a `vh`-based rule applied via
a *template* utility class: `App.vue`'s authenticated shell root (`<div class="d-flex vh-100
overflow-hidden">`) uses Bootstrap's `.vh-100` (`height: 100vh !important`), which wraps both
the sidebar and the main content column. The user caught this via a real logged-in session —
horizontally full width (the flex row fills its container fine), vertically capped at 80% with
blank space below (the container itself, one level above the already-fixed `.sb-sidebar`, was
still short). Re-verified the same way as the rest of the audit (DOM measurement in Chrome,
`.vh-100`-classed test element within 2px of `window.innerHeight` post-fix).

Tutor/Admin/SuperAdmin-only files with `vh` (`LandingPage.vue`, `TutorProfile.vue`,
`TutorSchedule.vue`, `TutorWallet.vue`, `TutorSubjectSetup.vue`, `TutorVerificationSetup.vue`,
`AdminTutorApplications.vue`, `SuperAdminUserModal.vue`) are unreachable with
`data-sb-density='compact'` set (only the Tutee role sets it), so they were left untouched.

**Correction (2026-08-05).** Two files were misclassified into that list by filename rather than by
route: `TutorDetails.vue` backs `/tutor/:id`, which is `role: 'Tutee'` (`src/router/index.js:97`),
and `AuthShell.vue` backs `/application-status`, which is `role: ['Tutor', 'Tutee']`
(`src/router/index.js:130`) alongside the public auth screens. Both are Tutee-reachable and had been
rendering 20% short since `2cc9981`; their compensation rules were added in
`2026-08-05-tutor-ui-80-percent-density.md` and are listed in the table above. `AuthShell`'s rule
stays inert on `/login`, `/register`, `/forgot-password` and `/reset-password` — `userRole` is null
there, so density is `comfortable` and the selector never matches. `SbBgWash.vue`'s `vh`-positioned blobs need no
compensation: `.sb-bg-wash` itself covers the viewport via `inset: 0`, not `vh`, and slight
imprecision in decorative blob placement isn't visually load-bearing.

## Steps

1. `src/assets/main.css` — add `--sb-density-scale: 1` to `:root`, then a
   `:root[data-sb-density='compact']` rule setting `--sb-density-scale: 0.8`,
   `--sb-vh-fix: calc(100vh / var(--sb-density-scale))`, and `zoom: var(--sb-density-scale)`.
2. `src/assets/main.css` — add the `[data-sb-density='compact'] <selector> { ... }` compensation
   rules from the `vh` consumer audit table above.
3. `src/stores/density.js` — Pinia store holding `density` and exposing `setDensity(value)` /
   `syncFromRole(role)`, which set/remove `data-sb-density` on `document.documentElement`.
4. `src/App.vue` — import `useDensityStore`, instantiate it, and add
   `watch(userRole, (role) => densityStore.syncFromRole(role), { immediate: true })` once
   `userRole` is defined. No wrapper markup needed.

## Risks

- Media queries: root `zoom` shifts the effective viewport width used for breakpoint matching,
  which is the one place root zoom can diverge from real browser zoom. `/dashboard` and
  `/find-tutors` have breakpoints that need spot-checking at 1280 / 1440 / 1920 for premature
  responsive collapse.
- 14 `<Teleport to="body">` overlays (`SbSelectModal`, `SupportModal`, `SessionCheckInModal`,
  `VenueConfirmModal`, `BookingDatePicker`, `BookingTimePicker`, `SubjectPickerModal`,
  `CampusLocationModal`, `RatingStackModal`, `SbToast`, others) must scale, stay centered, and
  not clip — verify each individually.
- Role isolation: `TutorBookingDetailsFlow.vue` and other non-tutee consumers of
  `SbSelectModal.vue` (11 total) must render at 100% since they don't route through the Tutee
  role check.
- Switching roles without a hard refresh (e.g. logout/login as a different role in the same tab)
  must flip density immediately — covered by the `watch` on `userRole` rather than a one-time
  mount check.

## Checks to run

- `npm run build`, `npm run test` (77 expected), `npm run lint` — all ran clean; the one
  `no-unused-vars` on `draftSubjectCodes` in `src/composables/useSubjectCatalog.js` pre-dates
  this change (last touched in `d85aaa6`) and is unrelated.
- Done — DOM-level verification via Chrome (`localhost:5174`, `npm run dev`), without a logged-in
  session (local demo data isn't seeded in this DB — `bea.santos@cpu.edu.ph` /
  `studybuddy123` returned "Invalid credentials"; unrelated to this change, not chased further):
  - Confirmed empirically that `zoom` on `:root` does **not** rescale the `vh` viewport
    (`window.innerHeight` unchanged; a `height: 100vh` test element rendered 20% short) —
    this is what drove the `vh` consumer audit and compensation pass above.
  - Confirmed the `--sb-vh-fix` compensation is correct: a `.sb-sidebar`-classed test element
    with `data-sb-density="compact"` set rendered its `getBoundingClientRect().bottom` within
    2px of `window.innerHeight` (742.4 vs 742).
- Done (2026-08-05) — full manual walkthrough, run by the user against a logged-in session and
  confirmed identical to 80% browser zoom. It was run as part of the Tutor pass
  ([2026-08-05-tutor-ui-80-percent-density.md](2026-08-05-tutor-ui-80-percent-density.md)), which
  also added the two Tutee-reachable rules this plan's audit had missed (see the correction above),
  so the two passes were confirmed together. What was walked:
  - Logged in as Tutee, confirm `AppSidebar` fills top to bottom with no gap at any window
    height.
  - Walk `/dashboard`, `/tutee-profile`, `/tuteeSessions`, `/tuteeSessionDetails/:id`, `/book`,
    `/find-tutors`, `/payment-tutee/:bookingId`, `/chat`.
  - Open each Teleported overlay listed above; each must scale with the page, stay centered,
    cover the viewport, and not clip.
  - `Dashboard.vue`'s hero clamp sizes sanely.
  - `SbBgWash` covers edge to edge with no seam.
  - Check `/dashboard` and `/find-tutors` at 1280 / 1440 / 1920 for premature responsive
    collapse.
  - Toggle light/dark — `data-sb-theme` and `data-sb-density` are independent and must not
    interact.
  - Log in as Tutor and Admin, confirm 100% rendering; log back in as Tutee without a hard
    refresh and confirm the switch applies.
