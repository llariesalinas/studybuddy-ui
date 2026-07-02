# Plan: Replace native selects with `SbSelectModal`

**Date:** 2026-06-03
**Branch:** feature-darkmode-toggle
**Spec:** Inline in this document
**Status:** Implemented - verification complete with one unrelated lint blocker noted.

---

## Overview

Replace native `<select>` dropdowns in the booking, onboarding, setup, schedule, registration,
and tutor wallet flows with a reusable, dark-mode-aware `SbSelectModal`. Admin filter selects are
intentionally out of scope for this pass.

Subject selection gets a richer picker: subjects grouped by department, a Recommended section
derived from the tutee profile course or strand, a General section for subjects that apply broadly,
and in-modal search. Existing subject filtering and recommendation behavior from `TuteeProfile.vue`
will be extracted into a shared composable so the app keeps one source of truth.

**Scope:** `InitialBooking.vue`, `FindTutors.vue`, `Register.vue`, `TutorSchedule.vue`,
`TutorPreferenceSetup.vue`, `PreferenceSetup.vue`, `TutorWallet.vue`, `TuteeProfile.vue`,
`SbSelectModal.vue`, and `useSubjectCatalog.js`.

---

## Parallel Workstreams

| Agent | Ownership | Responsibility |
|---|---|---|
| Agent A | `SbSelectModal.vue`, `useSubjectCatalog.js`, `TuteeProfile.vue` | Build the shared modal, extract subject catalog logic, and preserve TuteeProfile behavior. |
| Agent B | `InitialBooking.vue`, `FindTutors.vue` | Wire grouped subject pickers, mode pickers, JS validation, and empty-value "Any" filter behavior. |
| Agent C | `Register.vue`, `TutorSchedule.vue`, `TutorPreferenceSetup.vue`, `PreferenceSetup.vue` | Replace simple setup/auth/schedule selects while preserving existing values and side effects. |
| Agent D | `TutorWallet.vue` | Replace tutor-facing wallet dropdowns and preserve required validation. |
| Parent | Docs, integration, verification | Review patches, align component API usage, update docs, add session summary, and run checks. |

Workers must not edit outside their owned files. The parent resolves API drift and import issues
after worker patches return.

---

## Key Design Decisions

| Decision | Choice | Reason |
|---|---|---|
| Component API | Generic `SbSelectModal` with flat `options` or grouped `groups`, plus `searchable`, `clearable`, `clearLabel`, and `triggerClass` | One component serves simple dropdowns and grouped subject pickers. |
| Option contract | Callers pass explicit `{ label, value, description? }` | Avoids field guessing and undefined labels/values. |
| Subject grouping | Department first, category fallback | Matches current profile behavior and keeps subjects visible once. |
| Recommended section | Use existing course-token scoring from TuteeProfile | Surfaces relevant subjects without hiding other options. |
| General section | Prefer `is_general`/`applies_to_all`, fallback to frontend allow-list | Backend flag may not exist yet. |
| FindTutors "Any" | Empty string remains "any" for subject/mode | Preserves filter semantics and avoids phantom option values. |
| Native `required` | Replace with explicit JS validation | Modal triggers are buttons, so native select validation no longer applies. |
| Theming | Existing `data-sb-theme` tokens and `.sb-*` utilities | Supports light and dark mode without new dependencies. |
| Scope | Include tutor wallet; exclude admin filters | Wallet is tutor-facing product UI, admin filters can be deferred. |

---

## Implementation Details

### Shared modal and subject catalog

- Create `src/components/SbSelectModal.vue` with `modelValue`, `options`, `groups`, `title`,
  `placeholder`, `searchable`, `clearable`, `clearLabel`, and `triggerClass` props.
- Emit `update:modelValue`; close on selection, Escape, or backdrop click.
- Lock body scroll while open, restore previous overflow, restore focus to the trigger, and focus
  search or the active option on open.
- Use ARIA dialog/listbox semantics and `aria-expanded`/`aria-controls` on the trigger.
- Create `src/composables/useSubjectCatalog.js` and refactor `TuteeProfile.vue` to consume it
  without changing profile subject behavior.

### View wiring

- **InitialBooking:** grouped searchable subject picker; flat mode picker; validate subject, mode,
  date, and time before saving filters.
- **FindTutors:** grouped searchable subject picker with clear label `Any Subject`; mode picker with
  clear label `Any Mode`; empty subject/mode remain valid broad filters.
- **Register:** institution values stay `String(id)`; role values stay `Tutee` and `Tutor`; keep
  institution-domain validation.
- **TutorSchedule:** day values stay `Mon` through `Sun`.
- **TutorPreferenceSetup:** teaching-level values stay `Elementary`, `High School`, and `College`.
- **PreferenceSetup:** course values stay `course_code`; changing course still clears selected subjects.
- **TutorWallet:** replace payout rail, destination type, receiving institution, and saved payout
  destination dropdowns; preserve required checks in `saveAccount` and `handleCashout`.

---

## Verification

1. Run `npm run lint`.
2. Run `npm run build`.
3. Manually verify light and dark modal behavior across booking, setup, auth, schedule, and wallet screens.
4. Regression-check `TuteeProfile.vue` after composable extraction.
5. Confirm `FindTutors` broad search behavior when subject is empty. If the backend rejects empty
   subject, make the subject picker non-clearable there and document the API constraint.

---

## Documentation

- Keep this plan updated with the chosen parallel execution scope.
- Completion summary added under `docs/session-summaries/2026-06-03-sbselectmodal-completion.md`.

---

## Completion Notes

- Parallel workers completed the shared modal/composable, booking views, setup/auth/schedule views,
  and tutor wallet view.
- Parent integration added missing shared modal props, wallet payout-account options, and wallet
  trigger styling.
- `npm run build` passes.
- Direct non-mutating `oxlint` and `eslint` pass for all changed files.
- Full `npm run lint` is blocked by pre-existing `TutorProfile.vue` unused-expression errors at
  `openAccordionPanel` and `closeAccordionPanel`, outside this implementation scope.
