# Desktop UI and trust fixes — 2026-10-16

Implemented the approved critique priorities 1–4 plus desktop interface refinement. The work
preserves StudyBuddy's identity and existing layouts. No mobile-specific navigation, responsive
rules, backend policy, schema, deployment or external sends changed.

## Delivered

1. Tutor profiles no longer invent 4.7 ratings, 124 sessions, subjects, descriptions or biographies.
   Zero and unavailable data remain distinct. A failed profile load shows Retry, and an unavailable
   rate prevents booking rather than presenting a false price. Landing timing/match numbers were
   replaced with factual feature highlights; campus eligibility and payment FAQ copy now match
   partner-institution registration and the existing online/cash split.
2. Booking uses the existing cancellation-window composable and shared 12-hour cutoff. Selected
   slots show their cutoff in Manila time or explain the absence of a penalty-free window.
   Post-confirmation deadlines use the same Manila-time formatter. Enforcement is unchanged.
3. Login, registration and password-recovery/reset fields have real label associations and
   autocomplete purposes; booking/search controls and receipt upload are also labeled. Sessions
   provide native named detail links. Shared date, subject and select dialogs, Help, scheduling,
   cash-out and ticket-detail surfaces contain keyboard focus, dismiss with Escape and restore
   focus. Nested dialogs close in order. Visible keyboard outlines use the existing darker green.
4. Weekly deletion is named explicitly, describes recurrence and requires confirmation. Cancel
   does not delete; failed and partially completed batches keep remaining selections for retry.
   The availability store propagates deletion failures so the screen cannot announce false success.
5. Desktop-only shared refinements cover headings, explanatory text, field sizing, filters,
   tables, pill buttons and tabular numbers. Tutor results identify their next action as View tutor.
   Wallet earnings decoration recedes behind available balance and clearly aligned actions.
   Redundant dashboard labels were removed and Unrated styling is neutral.

## Validation

| Check | Result |
| --- | --- |
| Pre-change full frontend suite | 249 pass, one skip, nine failures |
| New regression tests | 15 pass |
| Focused seven-file run | 48 pass |
| Post-change full frontend suite | 264 pass, one skip, same nine failures |
| Lint | Pass |
| Production build | Pass |
| Diff whitespace check | Pass |
| Backend changes | None; no backend tests required |
| New desktop color pairs | Light primary control 6.15:1; dark primary control 10.24:1 |

The nine baseline failures remain six BookingTimeRangePicker cases and three CSS-token checks
(missing semantic status ramp, dangling token reads, and existing literal token overrides).
No failing test was hidden, skipped or rewritten to pass.

The 15 new tests cover zero/missing profile data, invalid-rate booking prevention, honest load
failure/retry, selected Manila cancellation deadlines, bookings inside the cutoff, account labels
and autofill, native session links, date-dialog focus/Tab/Escape, cancellation versus confirmation
of weekly deletion, failure retry and retrying only remaining slots after partial deletion.

## Desktop browser evidence

Inspected real public landing, login and registration pages, plus actual Vue components rendered
with in-memory fixture data for authenticated booking, schedule, wallet, sessions, student dashboard,
admin dashboard and support queue. Effective desktop CSS width was 1440px. Screenshots, accessible
trees and read-only DOM measurements were inspected. Screenshots were not saved as repo assets.

- Profile displays No ratings yet, zero sessions, no invented subjects and no invented bio.
- Selecting the sample Oct 17 16:00 slot displays Oct 17 04:00 cancellation cutoff, Manila time.
- Deletion opens a named dialog with safe initial focus and explicit every-Friday scope.
  Fixture request log contains only GET before confirmation and one DELETE after confirmation;
  the sample slot disappears afterward. No real availability was touched.
- Session detail is a native named link and responds to Enter; route change is also regression-tested.
- Wallet actions stay on one line. Cash-out focus enters the dialog; Escape closes it and restores
  the trigger. A nested institution picker closes independently before the parent cash-out dialog.
- Actual login and registration expose named fields and the appropriate autofill purposes.
- Shared desktop tables and filters were inspected in both student sessions and admin support.
- The first visual pass found cramped wallet buttons and a profile action overlap. Both were
  corrected together and confirmed in the second pass; no open-ended polish loop followed.

The actual local API was unavailable. Authenticated browser checks are fixture-based, not proof of
live server integration. Registration's institution-load failure is an environment artifact.
No credentials were entered, account created, payment initiated, message sent or email triggered.
Existing real authentication state was not cleared or overwritten by the fixture.

The final source audit caught pale dark-theme primary colors inheriting white control text.
Desktop booking and wallet controls now use the paired primary-contrast token. Profile headings,
summary text and cost panels also follow their surface tokens. Contrast was calculated from the
declared light/dark values; this is not a claim of a complete rendered dark-mode audit.

## Detector and cleanup

Manual scan once: 993 candidates across 84 files, 963 advisory and 30 warning. Warnings are
unchanged from the critique. The net four additional advisories concern typography, including
documented dense sizes and the sanctioned landing exception; no blanket fixes or ignores added.
The report does not claim a new critique score or a clean pre-existing design-token layer.

The local-only preview intercepted API calls in memory. Its root-level temporary files were
removed, review browser tab closed, viewport override reset, and Vite process 16496 stopped;
zero listeners remained on port 5173. Fixture sources and raw detector JSON were retained only
in the user's temporary folder. Unrelated existing files and plan-dashboard edits were preserved.

Repository feature-flow wrappers were unavailable; the available impeccable workflow and direct
tests/browser verification were used. No implementation delegation or unapproved external dispatch.
Graphify incremental AST refresh completed locally without LLM calls. Its installed skill-version
warnings were left for separate maintenance; no skill installation or semantic relabeling was run.
