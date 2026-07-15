---
title: Onboarding guided-rail redesign
date: 2026-07-07
status: Done
spec:
---

# Onboarding guided-rail redesign

<!-- LIVING SUMMARY: keep this section and the Changelog current on every edit -->
## Status & Progress Summary

**Status: Done — implemented and verified live in the browser (light/dark, desktop/mobile).**

Came out of the `feat/demo-data-reset` branch's `year_level` encoding fix, when reviewing the
onboarding wizard (`PreferenceSetup.vue`) surfaced how dated its emoji-driven card UI looked next
to the rest of the app. Three visual directions were mocked up live (Refined Wizard, Guided Rail,
Conversational full-bleed) using the real `--sb-*` tokens; Guided Rail was picked and implemented.
`SbStepBar.vue` was deleted as newly-orphaned. A pre-existing, unrelated bug was found during
verification (BSIT's subject filter map loosely permits BSCS-coded subjects like CS-211 that the
backend then rejects at submit time with a 400) — flagged as a separate follow-up task, not fixed
here since it predates this change and isn't part of the redesign's scope.

## Goal

Redesign `PreferenceSetup.vue` (the post-registration Tutee onboarding wizard) to match
StudyBuddy's visual language more closely and drop emoji from the UI, without changing any of
its underlying state, validation, or submission logic.

## Approach

Brainstormed three visual directions in a live HTML preview (Refined Wizard, Guided Rail,
Conversational full-bleed) using the app's real design tokens (`--sb-primary`, `--sb-card-bg`,
`--sb-card-border`, `--sb-text-main`, `--sb-text-muted`). **Guided Rail** was approved: a
persistent left-side step rail (Level → Grade/Strand/Program → Subjects) with checkmarks on
completed steps, main content to the right, replacing the current centered-card + thin progress
bar layout.

This is a template/styling-only change. `PreferenceSetup.vue`'s script block (`educationLevels`,
grade/strand/course refs, `computedFilterKey`, `card2Valid`, `finalYearLevel`, `finish()`, the
`year_level` offsets fixed on this branch, etc.) is untouched — only the markup and scoped CSS
change shape. No new component is introduced; the rail stays inline in this file since it has no
other consumer today (adding an abstraction for a single usage would be premature).

Emoji removal: the 4 education-level emoji (🏫📚🎓🏛️) become small inline SVG line icons (matching
the approved mockups), the "⚠️ No subjects found" warning drops its emoji prefix, and "Complete
Onboarding 🚀" becomes plain "Complete Onboarding".

Theming: the rail's tinted background must not be a hardcoded hex (would break dark mode) — use
`color-mix(in srgb, var(--sb-primary) 6%, var(--sb-card-bg))` so it adapts automatically, per the
project's "no hardcoded values" rule.

## Steps

1. Replace the `<SbStepBar>` progress bar with the rail: a fixed-width left column listing
   3 steps. Step 2's label is dynamic — "Grade" for elementary/JHS, "Strand" for SHS, "Program"
   for college — via a small computed. Completed steps get a solid checkmark, the current step
   is bolded/highlighted, matching the approved mockup states.
2. Confirm `SbStepBar.vue` has no other consumers; if it's now orphaned, stop importing it here
   (leave the component file itself unless grep confirms zero references anywhere).
3. Restyle Step 1 (education level) from the 2-column card grid to the rail's vertical option-row
   style, swapping each level's emoji for its inline SVG icon.
4. Restyle Step 2 content (elementary/JHS grade tiles, SHS strand + grade, college degree dropdown
   + year tiles) to the rail's thinner-border/smaller-radius tile treatment — no logic changes.
5. Restyle Step 3 (subjects) from large Bootstrap checkbox cards to the compact checklist-row
   style from the mockup; keep the real `<input type="checkbox">` for accessibility, just
   restyle the row. Drop the emoji from the empty-state warning text.
6. Update the final button label to "Complete Onboarding" (no emoji), and add a small-viewport
   fallback so the rail stacks above the content instead of squeezing it on mobile widths.
7. Run `npm run lint` and `npm run build`.
8. Manually verify in the browser preview: register a fresh account (or reuse
   `onboardfix.test@cpu.edu.ph` from the earlier `year_level` fix), walk all 3 steps for at least
   one non-college branch and the college branch, confirm rail checkmarks/labels update correctly,
   confirm `POST /api/profile/setup/` and `POST /api/preferences/` still fire with the same
   payloads as before, and check dark mode + a mobile viewport width.

## Risks

- The rail's step-2 label must stay in sync with `educationLevel` — a stale computed would show
  the wrong word (e.g. "Program" while looking at grade tiles).
- Dark-mode contrast on the rail's tinted background needs an actual visual check, not just a
  token substitution — `color-mix` percentages that look right in light mode can read too flat
  in dark mode.
- Narrow viewports: the current layout is desktop-first (`col-md-7` centered card); the rail adds
  a fixed-width column that needs an explicit responsive fallback or it will crush the content
  column on phones.
- Purely visual/template change — no API, store, or migration risk. The `year_level` encoding fix
  from earlier this session is unrelated and already shipped separately.

## Checks to run

- `npm run lint` — no new errors.
- `npm run build` — succeeds.
- Manual walkthrough in the live preview (steps above) — rail state, checkmarks, dark mode, and
  mobile width all confirmed by direct observation, not just code review.

## Changelog

- 2026-07-07: Plan written and approved after a live-HTML-mockup brainstorming session (three
  directions shown, Guided Rail picked). Implementation not yet started.
- 2026-07-07: Implemented. Rewrote `PreferenceSetup.vue`'s template/scoped CSS to the Guided Rail
  layout (step-2 label dynamic per education level, emoji replaced with inline SVG icons, subject
  list restyled to a compact checklist, mobile fallback stacks the rail). Script block (state,
  computeds, `finish()`) untouched. Deleted `SbStepBar.vue` (confirmed zero remaining references).
  `npm run lint`/`npm run build` pass. Verified live: registered a fresh account, walked the full
  Elementary and College branches, confirmed rail checkmarks/dynamic labels, `POST profile/setup/`
  + `POST preferences/` succeed end-to-end to `/dashboard`, dark-mode rail background resolves to
  the correct dark token via `color-mix` (no hardcoded hex), and the rail stacks correctly at a
  375px mobile width. Found and flagged (not fixed) a pre-existing, unrelated bug: BSIT's subject
  filter map admits BSCS-coded subjects the backend rejects at submit time.
