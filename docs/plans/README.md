# Plans Index

Every finalized plan lives in this folder as its own dated file, created from [`_template.md`](_template.md).
Status moves Draft â†’ Approved â†’ In Progress â†’ Done. When a plan is complete, its summary is linked below.

**Status & Progress Summary** (2026-07-16): Subjects taxonomy reseed and recommender proof is
Approved — grilled end-to-end (12 decisions) from panel feedback: subjects become a Preply-style
generic/specific taxonomy (slug PKs, `category` repurposed from course linkage to the 6 taxonomy
categories, SPED deliberately excluded), course-based subject gating is retired, the demo DB gets
a full non-staff wipe and a curated + filler reseed (10 curated personas covering every formula
component, ~150/~350 Faker fillers with guaranteed ratings/preferences), built on top of a merge
of `feat/recommender-weight-rebalance`, with a CBF level-check fix and a two-level drilldown
subject picker (mockup decided via ui-preview) — [Plan](2026-07-16-subjects-taxonomy-reseed.md).
Previous (2026-07-15): Merged `origin/main` into
`feat/tutor-onboarding-verification-redesign`; main's "Remove Applicant Review from Super Admin"
work is superseded on this branch by the Admin-into-SuperAdmin role consolidation (its plan row
below is annotated accordingly), while main's migration-dependency fix was kept. Instant Booking is In Progress — a Codex brief (`docs/briefs/2026-07-16-instant-booking.md`) covering all 8 steps was compiled 2026-07-16 on `feat/instant-booking`; dispatch pending. Grilled end-to-end (11
decisions) via `/grill-with-docs` from panel feedback: Instant Booking becomes the only booking
model (request-to-book, approve/reject endpoints, and `TutorRequestedSessions.vue` removed);
tutor protection moves to a symmetric 12h Grace Cutoff with self-serve Late Cancellations that
auto-open system-opened Support Tickets for excused/counted admin review (Counted Strike: P50
tutor wallet deduction, shared 3-per-month cap suspending booking/search visibility); the three
accept-time tutor gates move to booking creation surfaced via search-visibility hiding; 14-day
Booking Horizon bounds stale recurring availability; auto-generated Jitsi Meeting Links for
Online sessions; full notification package with auto-opened chat —
[Plan](2026-07-15-instant-booking.md), ADR-0008, seven glossary terms. Recommender weight rebalance (CBF split + CF peer
ratings) is Approved — grilled end-to-end (10 decisions) via `/grill-with-docs`: CBF subject match
splits into Specific (0.40) / General (0.20, superset via `Subjects.category`, null-safe) with an
Expertise cascade (0.15) and squeezed course/year/level (0.10/0.10/0.05); CF neighbors filter to
same-course peers with per-tutor global fallback and a positive-similarity requirement; hybrid
0.7/0.3 untouched; one loose end (empty `requested_subject`) to resolve before implementation —
[Plan](2026-07-15-recommender-weight-rebalance.md). Booking subject persistence (Codex handoff) is Done —
added a nullable protected `Booking.subject` FK, persisted and displayed the tutee's selected
catalog subject across booking confirmation, notifications, dashboard/request payloads, and
session details, covered the behavior with backend tests, and updated both seed commands to give
demo bookings real tutor-taught subjects; the review follow-up centralized the shared error and
fallback-label logic — [Summary](../session-summaries/2026-07-08-booking-subject-persistence-summary.md).
Face-to-face campus location modal is Approved — grilled
end-to-end (9 decisions) via `/grill-with-docs`: selecting Face-to-face mode opens a popup modal for
Inside/Outside Campus, Outside Campus gates behind a liability-acknowledgment confirm modal before the
existing free-text location field appears, applies to both `InitialBooking.vue` and `FindTutors.vue`
via one shared component; the acknowledgment is UI-only and not persisted (see ADR-0007); glossary
updated with Preferred Mode, Campus Location Type, Off-Campus Liability Acknowledgment. Not yet
implemented. Re-enable cash payments + tutor debt banner is Done —
grilled end-to-end (16 decisions), implemented (Steps A–G), audited line-by-line against the plan,
and fully verified against a real local database. Steps A–F all matched the plan exactly. The
audit caught and fixed three real issues before anything ran: a hardcoded hex color in the new
banner (now `--sb-danger`-derived); Step G's negative-balance demo persona pick, which would have
plausibly failed silently (Isabel's PHP 55,000 top-up and Miguel's ~10 additional
randomly-PAYMONGO/CASH cluster-rating payments could both land positive) — replaced with a
deterministic correction; and a pre-existing test the new server-side enforcement silently broke,
now fixed. Resolved the "no isolated local database" gap (`.env`/`.env.dev` both pointed at the
same Supabase instance) by using the local PostgreSQL 18 server already on the machine, matching
this project's own CI config, with `.env` never modified. Verified for real: the 8 new tests plus
the fixed pre-existing test all pass (25/25); the full 278-test suite's 30 failures/5 errors are
all pre-existing and unrelated; `reset_demo_data` ran end-to-end and empirically confirmed
Miguel's wallet lands at exactly PHP -75.00 as designed. Seed data year_level scale fix is
Approved — a
code-review follow-up on the guided-rail redesign flagged the "college = +12 offset" convention
duplicated across three call sites; this plan fixes the fourth offender (`seed_data.py`, which
picks year_level independently of course) and extracts a shared `YEAR_RANGE_BY_COURSE` constant
used by both `seed_data.py` and `reset_demo_data.py`. Onboarding guided-rail redesign is Done — three
visual directions were mocked live against the app's real design tokens, Guided Rail was picked
and implemented in `PreferenceSetup.vue` (template/CSS only, no logic changes), verified live in
light/dark and desktop/mobile; a pre-existing unrelated bug (BSIT subject filter admitting
BSCS-only subjects the backend rejects) was found and flagged as a separate follow-up.
Remove Motivation field from Tutor/Tutee application flows is Done — grilled end-to-end;
removed `reason_to_tutor` entirely (model column, serializers, views, tests, demo data, all
frontend surfaces) while preserving the unrelated document-renewal "note" field. Full backend
suite (289 tests) plus 26 targeted application/renewal/verification tests pass, lint and build
clean, two-axis (Standards/Spec) review found zero hard findings on either axis.
Algorithm Demo live rating edit is In Progress — a dev-only feature letting a SuperAdmin
inline-edit a contributing neighbor's rating in Compare Pair's breakdown (new staff-only PATCH
endpoint, refetch-and-reanimate on save via `AlgorithmDemoPairPicker.vue`'s existing fetch
pattern); spec approved, implementation just starting.
Tutor onboarding & verification redesign is Approved — grilled end-to-end (13 decisions):
tutors get full app access immediately (no more router-wide lockout), gated only by exclusion
from `FindTutors` search until their application is approved; verification is folded into one
guided onboarding sequence (setup → subjects → verify-or-skip); tutors can propose subjects
missing from the just-globalized catalog, which land as `pending` tied to their application and
get approved/rejected per-subject alongside the admin's document review. `ui-preview` mocked both
onboarding screens on the real Guided Rail shell (3 directions each): Step 2 picked Direction B
(inline subject picker, separate from and not replacing the existing `TutorProfile.vue` modal),
Step 3 picked Direction C ("explain, then choose"); both promoted to
`docs/mockups/2026-07-13-tutor-onboarding-verification-redesign.html`. The reminder banner turned
out to need no new component — reuses the existing `VerificationBanner.vue` as a third content
variant. Compiled into `docs/briefs/2026-07-14-tutor-onboarding-verification-redesign.md` and
dispatched to Codex CLI on a dedicated `feat/tutor-onboarding-verification-redesign` branch.
`/codex-review` verified independently (17/17 new tests, full suite on a fresh DB — 28 failures + 5
errors, all root-cause-traced to pre-existing/unrelated issues, not assumed), reviewed Codex's one
disclosed deviation (account-only tutor registration, moving document upload to the new Step 3) as
justified and well-tested, cleaned up two pieces of dead code it left behind, and committed in
three stops. Done.
(2026-07-05): Mock receiving institutions + auto-processed payout activity is Done â€” extends the existing `PAYMONGO_CASHOUT_MOCK` seam to mock the bank/e-wallet dropdown (12 curated logo-matched institutions) and log auto-processed/failed cash-outs to the admin activity feed (new `withdrawal_processed` choice, migration `0069`), so the full cash-out flow runs locally without a KYB-approved PayMongo account; 3 mock cash-out tests pass and the 2 remaining `TutorCashOutTests` failures were confirmed pre-existing. Institution course catalog is Done â€” institution-owned Custom Subjects, Institution Course Catalog APIs, Admin/SuperAdmin UI, demo-data alignment, and glossary updates shipped with focused tests passing. Demo data reset (thesis defense seed) is Done â€” the `reset_demo_data` command shipped, ran clean against the local dev DB (446 users, 1,341 bookings, 940 ratings), and all three named CBF/CF recommender scenarios were empirically verified via shell (fixing one cluster-design bug along the way where identical anchor patterns made two rating clusters inseparable by Pearson similarity). Full backend suite stayed at the documented pre-existing baseline (259 tests, 14 failures + 2 errors, confirmed unrelated). SuperAdmin algorithm demo page is Done â€” moves the standalone live demo tool into the SuperAdmin panel as two tabs (Ranked List, Compare Pair) sharing one calculation-animation component, both using the app's `SbSelectModal` dropdown for tutee/tutor selection, plus an Institution filter added mid-implementation once live testing showed the demo needed to work across institutions by default. Recommendation algorithm live demo tool is Done â€” staff-gated debug endpoints + a standalone HTML tool that replay the real Hybrid Score (CBF+CF) calculation live for the thesis panel, with a two-step OTP login, tutee search, and a staged bar-cascade animation. Two bugs found and fixed during manual verification (multi-word tutee search, a mislabeled "no CF signal" state). Session details redesign (profile-page feel + animated status bar + mid-session pulse) is Done on `feat/verification-phase4-session-redesign`, with shared profile-style primitives, two-column tutee/tutor detail layouts, animated Orbit Strip presentation, and accessible Mid-session pulse. The 2026-07-03 session countdown (Orbit Strip) remains Done; verification dev tools remain Approved; the July 2 full-system integration merge remains Done. Verification document + receipt image compression (2026-07-06) is Done â€” extends the existing avatar `compress_image()` pipeline to tutor/tutee verification documents and payment receipts via a new `compress_if_image()` helper that skips non-image files; 50 existing tests pass with no regressions.

| Date | Plan | Status | Summary |
|------|------|--------|---------|
| 2026-07-16 | [Subjects taxonomy reseed and recommender proof](2026-07-16-subjects-taxonomy-reseed.md) | Approved | Preply-style category taxonomy (slug codes, no visible codes, SPED excluded), full wipe + curated/filler reseed with guaranteed ratings/preferences, rebalance-branch merge, CBF level fix, course-gating retirement, two-level drilldown picker ([mockup](../mockups/2026-07-16-subject-taxonomy-picker.html)), demo-tool proof with cheat sheet |
| 2026-07-13 | [Tutor onboarding & verification redesign](2026-07-13-tutor-onboarding-verification-redesign.md) | Done | Removes the tutor route-lockout for a tutee-style search-visibility gate, folds verification into one guided onboarding sequence with a skip option, and lets tutors propose subjects missing from the catalog for admin review alongside their application; implemented via Codex, independently verified (full suite failures confirmed pre-existing/unrelated by root-cause tracing) — [Summary](../session-summaries/2026-07-14-tutor-onboarding-verification-redesign-summary.md) |
| 2026-07-13 | [Remove Motivation field from Tutor/Tutee application flows](2026-07-13-remove-motivation-field.md) | Done | Removed `reason_to_tutor` ("Motivation") entirely — model, serializers, views, tests, demo data, and every frontend surface — while preserving the unrelated document-renewal "note" field it shared UI/variable names with; full backend suite + 26 targeted tests pass, lint/build clean, two-axis review clean — [Summary](../session-summaries/2026-07-13-remove-motivation-field-summary.md) |
| 2026-07-08 | [Algorithm Demo — Live Rating Edit](2026-07-08-algorithm-demo-live-rating-edit.md) | In Progress | Dev-only inline rating edit in Compare Pair's neighbor list, new staff-only PATCH endpoint, refetch-and-reanimate on save — [Spec](../specs/2026-07-08-algorithm-demo-live-rating-edit-design.md) |
| 2026-07-08 | [Codex Handoff — Persist the Booked Subject on Booking](2026-07-08-booking-subject-persistence-codex-handoff.md) | Done | Persists the selected catalog subject on each booking, displays it across session surfaces with a `General` fallback, and seeds realistic demo subjects; follow-up centralized duplicated error and label logic — [Summary](../session-summaries/2026-07-08-booking-subject-persistence-summary.md) |
| 2026-07-07 | [Face-to-face campus location modal](2026-07-07-face-to-face-campus-location-modal.md) | Approved | Grilled Inside/Outside Campus choice + off-campus liability confirm modal for `InitialBooking.vue` and `FindTutors.vue`; not yet implemented — [ADR-0007](../adr/0007-off-campus-liability-acknowledgment-not-persisted.md) |
| 2026-07-07 | [Re-enable cash payments + tutor debt banner](2026-07-07-reenable-cash-payments.md) | Done | Implemented (Steps A–G), audited, and verified against local PostgreSQL (not Supabase); fixed a hardcoded color, a broken negative-balance demo persona, and a pre-existing test the new enforcement silently broke; 25/25 relevant tests pass, `reset_demo_data` confirmed Miguel lands at exactly PHP -75.00 — [Summary](../session-summaries/2026-07-07-reenable-cash-payments-summary.md) |
| 2026-07-07 | [Seed data year_level scale fix](2026-07-07-seed-data-year-level-scale-fix.md) | Approved | Pending |
| 2026-07-07 | [Onboarding guided-rail redesign](2026-07-07-onboarding-guided-rail-redesign.md) | Done | Guided-rail wizard redesign for `PreferenceSetup.vue`; emoji removed, real `--sb-*` tokens, verified live in light/dark and desktop/mobile |
| 2026-07-06 | [Verification document + receipt image compression](2026-07-06-verification-document-compression.md) | Done | Extends the existing avatar `compress_image()` pipeline to `school_id`/`enrollment_proof`/`receipt_image` uploads via a new `compress_if_image()` helper that skips non-image files (PDFs); 50 existing tests pass, standalone verification confirms compression, PDF passthrough, and corrupt-file fallback — [Summary](../session-summaries/2026-07-06-verification-document-compression-summary.md) |
| 2026-07-05 | [Mock receiving institutions + auto-processed payout activity](2026-07-05-mock-receiving-institutions-and-payout-activity.md) | Done | Mocks `list_receiving_institutions` under the existing `PAYMONGO_CASHOUT_MOCK` flag (curated ~12 logo-matched institutions) so the full cash-out flow runs locally, plus activity-feed logging for auto-processed/failed cash-outs and a declared `withdrawal_processed` choice (migration `0069`) â€” [Summary](../session-summaries/2026-07-05-mock-receiving-institutions-and-payout-activity-summary.md) |
| 2026-07-05 | [Institution course catalog](2026-07-05-institution-course-catalog.md) | Done | [Spec](../specs/2026-07-05-institution-course-catalog-design.md) Â· [Summary](../session-summaries/2026-07-05-institution-course-catalog-summary.md) |
| 2026-07-05 | [Demo data reset (thesis defense seed)](2026-07-05-demo-data-reset.md) | Done | New `reset_demo_data` command clears local dev data and reseeds it around the thesis's 5 objectives â€” multi-institution, named CBF/CF personas with engineered rating clusters, scheduling load-limit demo, wallet/withdrawal compensation data, growth-shaped ~60-day backdating; verified via shell against real recommender output, full backend suite unaffected (14 failures + 2 errors, matches documented pre-existing baseline) â€” [Summary](../session-summaries/2026-07-05-demo-data-reset-summary.md) |
| 2026-07-04 | [SuperAdmin algorithm demo page](2026-07-04-superadmin-algorithm-demo.md) | Done | Moves the standalone live demo tool into the SuperAdmin panel as two tabs (Ranked List, Compare Pair) using the app's `SbSelectModal` dropdown; backend gains tutor subjects + rating stats per row plus an optional institution filter (added mid-implementation, no new endpoints) â€” [Summary](../session-summaries/2026-07-04-superadmin-algorithm-demo-summary.md) |
| 2026-07-04 | [Recommendation algorithm live demo tool](2026-07-04-recommendation-algorithm-demo-tool.md) | Done | Staff-only debug endpoints + standalone HTML tool replaying the real Hybrid Score (CBF+CF) breakdown live; fixed a multi-word tutee-search bug and a mislabeled CF "no signal" state found during manual verification â€” [Summary](../session-summaries/2026-07-04-recommendation-algorithm-demo-tool-summary.md) |
| 2026-07-04 | [Session details redesign (profile feel + animated status bar + pulse)](2026-07-04-session-details-profile-redesign.md) | Done | Two-column glass layout, saturated green hero, Level 3 animated Orbit Strip, accessible hold-to-confirm mid-session pulse, and profile-style action tiers for both tutee/tutor detail pages - [Summary](../session-summaries/2026-07-04-session-details-profile-redesign-summary.md) |
| 2026-07-03 | [Session countdown implementation (Orbit Strip)](2026-07-03-session-countdown-prototype-plan.md) | Done | Verified all 13 decisions against real data; fixed a Decision 8 bug (detail bar leaking global queue state) and a pre-existing `SessionHero.vue` layout bug â€” [Summary](../session-summaries/2026-07-03-session-countdown-summary.md) |
| 2026-07-03 | [Remove Applicant Review from Super Admin](2026-07-03-remove-superadmin-applicant-review.md) | Done | Superseded on this branch by the 2026-07-13 tutor onboarding redesign, which consolidates the institutional Admin role into SuperAdmin — [Summary](../session-summaries/2026-07-03-remove-superadmin-applicant-review-summary.md) |
| 2026-07-02 | [Verification dev tools (self-service profile panel)](2026-07-02-verification-dev-tools.md) | Approved | Pending |
| 2026-07-02 | [Full-system integration merge](2026-07-02-full-system-integration-merge.md) | Done | [Summary](../session-summaries/2026-07-02-full-system-integration-merge-summary.md) |
| 2026-07-01 | [Tutee verification â€” overview](2026-07-01-tutee-verification-overview.md) | In Progress | Pending |
| 2026-07-01 | [Tutee verification â€” Phase 1 (model)](2026-07-01-tutee-verification-phase1-model.md) | Done | Pending |
| 2026-07-01 | [Tutee verification â€” Phase 2 (gate)](2026-07-01-tutee-verification-phase2-gate.md) | Done | Pending |
| 2026-07-01 | [Tutee verification â€” Phase 3 (UI)](2026-07-01-tutee-verification-phase3-ui.md) | Done | Pending |
| 2026-07-01 | [Tutee verification â€” Phase 4 (email & dev tools)](2026-07-01-tutee-verification-phase4-email-devtools.md) | Draft | Pending |
| 2026-07-01 | [Tutor application bugfixes](2026-07-01-tutor-application-bugfixes.md) | Done | [Summary](../session-summaries/2026-07-01-tutor-application-handoff.md) |
| 2026-07-01 | [Tutor application bugfix tests](2026-07-01-tutor-application-bugfix-tests.md) | Approved | Pending |
| 2026-07-01 | [Tutor document renewal review](2026-07-01-tutor-document-renewal-review.md) | Done | [Summary](../session-summaries/2026-07-01-tutor-application-handoff.md) |
| 2026-07-01 | [Local cash-out dev stub (PayMongo Money Movement)](2026-07-01-local-cashout-dev-stub.md) | Done | [Summary](../session-summaries/2026-07-01-local-cashout-dev-stub-summary.md) |
| 2026-06-30 | [Support ticket escalation](2026-06-30-support-ticket-escalation.md) | Done | [Summary](../session-summaries/2026-06-30-support-ticket-escalation-summary.md) Â· [Issue #95](https://github.com/llariesalinas/studybuddy-ui/issues/95) |
| 2026-06-29 | [Cash-out recent transactions (remove standalone destinations)](2026-06-29-cashout-recent-transactions.md) | Done | [Summary](../session-summaries/2026-06-29-cashout-recent-transactions-summary.md) Â· [Spec](../specs/2026-06-29-cashout-recent-transactions.md) |
| 2026-06-28 | [Payout destination rail removal and Receiving Institution logos](2026-06-28-payout-destination-rail-removal-and-logos.md) | Done | [Summary](../session-summaries/2026-06-28-payout-destination-rail-removal-and-logos-summary.md) Â· [ADR-0001](../adr/0001-instapay-only-cashouts.md) Â· [ADR-0002](../adr/0002-logodev-for-institution-logos.md) |
| 2026-06-26 | [Institution-scoped tutor matching](2026-06-26-institution-scoped-matching.md) | Done | [Spec](../specs/2026-06-26-institution-scoped-matching-design.md) Â· [Handoff](../artifacts/2026-06-26-institution-scoped-matching-handoff.html) |
| 2026-06-22 | [Booking card glow-avatar redesign](2026-06-22-booking-card-glow-avatar-redesign.md) | Done | [Summary](../session-summaries/2026-06-22-booking-card-glow-avatar-redesign-summary.md) Â· [Spec](../specs/2026-06-22-booking-card-glow-avatar-redesign-design.md) |
| 2026-06-21 | [Unified feel & haptics (Balanced calibration)](2026-06-21-feel-haptics-unification.md) | Done | [Summary](../session-summaries/2026-06-21-feel-haptics-unification-summary.md) Â· [Spec](../specs/2026-06-21-feel-haptics-unification-design.md) Â· [Reference](../artifacts/2026-06-21-feel-haptics-calibrations-reference.html) |
| 2026-06-22 | [System background unification](2026-06-22-system-background-unification.md) | Done | [Summary](../session-summaries/2026-06-22-system-background-unification-summary.md) Â· [Spec](../specs/2026-06-22-system-background-unification-design.md) Â· [Preview](../artifacts/2026-06-22-system-background-preview.html) |
| 2026-06-21 | [Institutional Admin dashboard redesign (Phase 1)](2026-06-21-admin-dashboard-redesign.md) | Done | [Summary](../session-summaries/2026-06-21-admin-dashboard-redesign-summary.md) Â· [Spec](../specs/2026-06-21-admin-dashboard-redesign-design.md) Â· [Preview](../artifacts/2026-06-21-admin-dashboard-redesign-preview.html) |
| 2026-06-21 | [Tutor profile real-time reflection + avatar compression](2026-06-21-tutor-profile-realtime-image-compression.md) | Done | [Summary](../session-summaries/2026-06-21-tutor-profile-realtime-image-compression-summary.md) Â· [Spec](../specs/2026-06-21-tutor-profile-realtime-image-compression-design.md) |
| 2026-06-17 | [Super Admin Redesign](2026-06-17-superadmin-redesign.md) | Approved | [Spec](../specs/2026-06-17-superadmin-redesign-design.md) Â· [Artifact](../artifacts/2026-06-17-superadmin-redesign-preview.html) |
| 2026-06-15 | [Session Details "alive" redesign (tutee + tutor)](2026-06-15-session-details-alive-redesign.md) | Done | [Summary](../session-summaries/2026-06-15-session-details-alive-redesign-summary.md) Â· [Reference](../artifacts/2026-06-15-session-details-alive-redesign-preview.html) |
| 2026-06-15 | [Chat banner & booking card compact-timeline redesign](2026-06-15-chat-banner-card-redesign.md) | Approved | |
| 2026-06-15 | [Tutor details slot range clarity](2026-06-15-tutor-details-slot-clarity.md) | Implemented (pending preview) | |
| 2026-06-15 | [Tutor schedule AM/PM period rail](2026-06-15-schedule-am-pm-rail.md) | Done | [Summary](../session-summaries/2026-06-15-schedule-am-pm-rail-summary.md) |
| 2026-06-14 | [Tutor wallet cash-in (top-up)](2026-06-14-tutor-wallet-cash-in.md) | Done | [Summary](../session-summaries/2026-06-14-tutor-wallet-cash-in-summary.md) |
| 2026-06-14 | [Antigravity Edge-Case Scan](2026-06-14-antigravity-edgecase-scan.md) | In Progress | [Summary](../session-summaries/2026-06-14-antigravity-edgecase-scan-summary.md) |
| 2026-06-14 | [Ongoing-booking live status surface](2026-06-14-ongoing-booking-live-status.md) | In Progress | [Spec](../specs/2026-06-14-ongoing-booking-live-status-design.md) |
| 2026-06-14 | [Chat accept/reject pending sessions](2026-06-14-chat-accept-reject.md) | Done | [Summary](../session-summaries/2026-06-15-chat-accept-reject-summary.md) |
| 2026-06-11 | [Landing page redesign â€” Studio Motion](2026-06-11-landing-page-redesign.md) | Done | [Summary](../session-summaries/2026-06-11-landing-page-redesign-summary.md) |
| 2026-06-08 | [Online-only payments + proof of payment](2026-06-08-online-only-payments.md) | Done | [Summary](../session-summaries/2026-06-11-online-only-payments-summary.md) |
| 2026-06-11 | [PayMongo proof-of-payment validation](2026-06-11-paymongo-proof-of-payment-validation.md) | Draft | Pending |
| 2026-06-08 | [SuperAdmin role + per-institution admin scoping](2026-06-08-superadmin-institution-hierarchy.md) | Approved | Pending |
| 2026-06-08 | [Venue confirmation + mid-session check-in modals](2026-06-08-venue-session-checkin-modals.md) | Done | Implemented session check-in tracking + tutee/tutor UI |
| 2026-06-07 | [Dashboard load performance (backend)](2026-06-07-dashboard-load-performance.md) | Done | [Summary](../session-summaries/2026-06-07-dashboard-load-performance-summary.md) |
| 2026-06-07 | [Chat partner context display](2026-06-07-chat-partner-context-display.md) | Done | [Summary](../session-summaries/2026-06-07-chat-partner-context-display-summary.md) |
| 2026-06-07 | [Support chat naming](2026-06-07-support-chat-naming.md) | Done | [Summary](../session-summaries/2026-06-07-support-chat-naming-summary.md) |
| 2026-06-07 | [Dashboard card stability](2026-06-07-dashboard-card-stability.md) | Done | [Summary](../session-summaries/2026-06-07-dashboard-card-stability-summary.md) |
| 2026-06-07 | [Notifications timeout fix](2026-06-07-notifications-timeout-fix.md) | Done | [Summary](../session-summaries/2026-06-07-notifications-timeout-fix-summary.md) |
| 2026-06-07 | [Dashboard top 5 Redis cache](2026-06-07-dashboard-top5-redis-cache.md) | Done | [Summary](../session-summaries/2026-06-07-dashboard-top5-redis-cache-summary.md) |
| 2026-06-07 | Global aurora/blur performance cleanup | Done | [Summary](../session-summaries/2026-06-07-global-aurora-blur-performance-cleanup-summary.md) |
| 2026-06-07 | [Aurora performance fix â€” static gradient](2026-06-07-aurora-performance-fix.md) | Done | [Summary](../session-summaries/2026-06-07-aurora-performance-fix-summary.md) |
| 2026-06-07 | [Aurora hue restoration (performant)](2026-06-07-aurora-hue-restoration.md) | Done | [Summary](../session-summaries/2026-06-07-aurora-hue-restoration-summary.md) |
| 2026-06-06 | [Frontend and chat caching](2026-06-06-frontend-chat-caching.md) | Approved | Pending |
| 2026-06-06 | [Resend email integration](2026-06-06-resend-email-integration.md) | Done | [Summary](../session-summaries/2026-06-06-resend-email-integration-summary.md) |
| 2026-06-06 | [Email system hardening (async queue + resilience)](2026-06-06-email-async-hardening.md) | Done | [Summary](../session-summaries/2026-06-06-email-async-hardening-summary.md) |

## Migrated plans (pre-convention)

Moved from `docs/superpowers/plans/` on 2026-06-14 when the docs convention was consolidated under `/docs`.
Entries marked Done&ast; predate the session-summary convention; their status is inferred from shipped code rather than a summary doc.

| Date | Plan | Status | Summary |
|------|------|--------|---------|
| 2026-06-06 | [Dashboard recommendations](2026-06-06-dashboard-recommendations.md) | Done | [Summary](../session-summaries/2026-06-06-dashboard-recommendations-summary.md) |
| 2026-06-03 | [Replace native selects with SbSelectModal](2026-06-03-replace-selects-with-sbselectmodal.md) | Done | [Summary](../session-summaries/2026-06-03-sbselectmodal-completion.md) |
| 2026-06-02 | [Phase B â€” Session cancellation (both roles)](2026-06-02-session-cancellation.md) | Done | [Summary](../session-summaries/2026-06-02-phaseB-session-cancellation-completion.md) |
| 2026-06-02 | [Phase A â€” Booking "tutors won't load" fix](2026-06-02-booking-tutor-load-fix.md) | Done | [Summary](../session-summaries/2026-06-02-phaseA-booking-load-fix-completion.md) |
| 2026-05-26 | [System-wide dark mode toggle](2026-05-26-system-wide-darkmode-toggle.md) | Done&ast; | Pending |
| 2026-05-25 | [Tutor profile redesign](2026-05-25-tutor-profile-redesign.md) | Done&ast; | Pending |
| 2026-05-25 | [Tutee profile redesign](2026-05-25-tutee-profile-redesign.md) | Done&ast; | Pending |
| 2026-05-25 | [Tutee profile avatar URL (backend)](2026-05-25-tutee-profile-avatar-url.md) | Done&ast; | Pending |
| 2026-05-25 | [Feel & haptics rollout](2026-05-25-haptics-rollout.md) | Done&ast; | Pending |
| 2026-05-25 | [Animation system expansion](2026-05-25-animation-system-expansion.md) | Done&ast; | Pending |
| 2026-05-23 | [Sidebar notification count badge](2026-05-23-sidebar-notification-badge.md) | Done&ast; | Pending |
| 2026-05-08 | [Auth pages redesign](2026-05-08-auth-pages-redesign.md) | Done&ast; | Pending |

---

## Changelog

| Date | Change |
|------|--------|
| 2026-07-16 | Grilled the subjects taxonomy reseed end-to-end (12 decisions, including retiring course-based subject gating discovered mid-interview); ran a ui-preview session for the two-level picker (drilldown cards V1 chosen, promoted to `docs/mockups/2026-07-16-subject-taxonomy-picker.html`); added the Approved plan |
| 2026-07-13 | Grilled removing the Motivation field end-to-end (scope expanded twice: also drop the backend column, also touch the Tutee-verification endpoints it's wired into); added the Approved plan |
| 2026-07-13 | Implemented the Motivation field removal (8 steps), applied migration 0075, ran full backend suite + 26 targeted tests (all pass), lint/build clean, two-axis review clean; marked Done and linked summary |
| 2026-07-08 | Completed booking-subject-persistence review follow-ups by extracting the shared subject error and display-label helper; added the session summary and marked the plan Done |
| 2026-07-05 | Added institution course catalog plan (Approved) from spec `2026-07-05-institution-course-catalog-design.md` so the work can be tracked before implementation |`n| 2026-07-05 | Implemented institution course catalog; marked plan Done and linked summary |
| 2026-07-05 | Grilled the demo data reset end-to-end (19 decisions, plus domain-modeling pass over CONTEXT.md and code cross-reference); added the Approved plan and corrected the stale Payout Destination/TutorPayoutAccount glossary entry |
| 2026-07-05 | Implemented and verified the demo data reset; fixed a cluster-design bug found during manual verification; full backend suite matched the documented pre-existing baseline; marked the plan Done and linked the summary |
| 2026-06-26 | Added handoff artifact link to institution-scoped matching row |
| 2026-06-28 | Added payout-destination rail removal + Receiving Institution logos plan (Approved) |
| 2026-06-28 | Marked payout-destination rail removal + Receiving Institution logos plan Done; linked summary |
| 2026-06-29 | Added cash-out recent transactions plan (Draft) |
| 2026-06-29 | Marked cash-out recent transactions plan Done; linked summary |
| 2026-06-30 | Added support ticket escalation PRD (Approved) |
| 2026-06-30 | Marked support ticket escalation Done; linked summary |
| 2026-07-01 | Added local cash-out dev stub plan (Approved) |
| 2026-07-01 | Marked local cash-out dev stub Done; linked summary |
| 2026-07-02 | Merged both branches' plan tables; added full-system integration merge row (In Progress) |
| 2026-07-02 | Marked full-system integration merge Done; linked summary (branch verified, push deferred) |
| 2026-07-02 | Added verification dev tools plan (Approved) from grilling session |
| 2026-07-03 | Added session countdown implementation plan (Approved) with Orbit Strip direction |
| 2026-07-03 | Grilled session countdown plan end-to-end; resolved 13 open decisions, updated summary row |
| 2026-07-03 | Linked session-countdown-concepts.html preview to the session countdown plan row |
| 2026-07-03 | Removed duplicate preview link from this row; moved the file to docs/artifacts/ and kept the single canonical link in the plan file itself |
| 2026-07-03 | Discovered implementation already committed outside the grilling session (`df994ca`); moved row Approved -> In Progress and linked the handoff doc |
| 2026-07-03 | Ran full verification (lint/build/tests/browser); found and fixed a Decision 8 bug in `useOrbitStrip.js`; moved row In Progress -> Done and linked the summary |
| 2026-07-03 | User caught a second, pre-existing layout bug via screenshot (`SessionHero.vue` oversized blank block) that the first verification pass missed; fixed and re-verified; updated row summary |
| 2026-07-04 | Grilled the session details redesign end-to-end (7 decisions, interactive previews); added the Approved plan and glossary term Midpoint Check-in |
| 2026-07-04 | Started execution of the session details redesign; moved row Approved -> In Progress |
| 2026-07-04 | Marked session details redesign Done; linked summary and updated dashboard/index status |
| 2026-07-04 | Grilled the recommendation algorithm live demo tool end-to-end (10+ decisions, Visual Companion mockups for layout + calculation animation); added the Approved plan and glossary terms Hybrid Score, CBF Score, CF Score, Top-K Neighbor, Cold-Start Tutee |
| 2026-07-04 | Implemented the recommendation algorithm live demo tool (TDD backend + standalone HTML tool); found and fixed two bugs during manual verification; ran a two-axis (Standards/Spec) review; marked the plan Done and linked the summary |
| 2026-07-04 | Designed and mocked up (interactive HTML preview) the SuperAdmin algorithm demo page; wrote design spec and added the Approved implementation plan for moving the standalone demo into the SuperAdmin panel |
| 2026-07-04 | Implemented the SuperAdmin algorithm demo page (TDD backend row augmentation + 3 Vue components + route/nav); added an unplanned institution filter after live testing showed institution-scoped matching made the demo unusable against seeded data; ran a two-axis (Standards/Spec) review and fixed all findings; marked the plan Done and linked the summary |
| 2026-07-07 | Grilled re-enabling cash payments end-to-end (16 decisions: motivation, session_mode-derived payment method with server-side enforcement, CASH receipt-only requirement, folding in the PAYMONGO proof-of-payment gap fix, tutor debt banner design, demo-data scope); added the Approved plan |
| 2026-07-07 | Implemented and audited re-enabling cash payments (Steps A–G); audit caught and fixed a hardcoded color, a broken negative-balance demo persona pick, and a pre-existing test silently broken by the new server-side enforcement; added 3 new test classes; moved plan Approved -> In Progress pending a local-vs-Supabase database decision before tests/migrations can actually be run |
| 2026-07-07 | Resolved the local-database gap using the local PostgreSQL 18 server already on the machine (matching this project's CI config), `.env` never modified; ran the 8 new tests (1 self-inflicted test bug found and fixed), the 17 tests in the class containing the fixed pre-existing test, and the full 278-test suite (30 failures/5 errors, all pre-existing and unrelated); ran `migrate` then `reset_demo_data` end-to-end and empirically confirmed Miguel's wallet lands at exactly PHP -75.00 as designed; marked the plan Done |
| 2026-07-07 | Grilled the Face-to-face campus location modal end-to-end (9 decisions) via `/grill-with-docs`; added the Approved plan, glossary terms Preferred Mode/Campus Location Type/Off-Campus Liability Acknowledgment, and ADR-0007 for the not-persisted acknowledgment decision |
| 2026-07-08 | Designed and specced the Algorithm Demo live rating-edit dev feature; added the In Progress implementation plan and updated the dashboard |
| 2026-07-13 | Grilled the tutor onboarding & verification redesign end-to-end (13 decisions) via `/grill-with-docs`, reviewed with the team through an interactive HTML explainer (including a follow-up subject-picker storyboard); added the Approved plan with onboarding screen visuals explicitly deferred to a `ui-preview` mockup pass |
| 2026-07-13 | Ran `ui-preview` for the tutor onboarding Step 3 (Verification) screen; Direction C picked and promoted to `docs/mockups/2026-07-13-tutor-onboarding-verification-redesign.html`; found the reminder banner can reuse the existing `VerificationBanner.vue` component instead of needing new UI |
| 2026-07-13 | Ran `ui-preview` for the tutor onboarding Step 2 (Subjects) screen; Direction B (inline picker, no modal) picked and added to the same promoted mockup; onboarding screen visual design now fully decided |
| 2026-07-14 | Created dedicated `feat/tutor-onboarding-verification-redesign` branch and committed the plan/mockup docs (previously uncommitted on the unrelated `feat/admin-role-consolidation` branch); compiled the plan into a Codex brief via `/codex-brief`, instructed per user request to skip the long-running full backend test suite; moved plan Approved -> In Progress |
| 2026-07-15 | Grilled Instant Booking end-to-end (11 decisions) via `/grill-with-docs` from panel feedback ("cut the manual tutor confirmation layer"); added the Approved plan, ADR-0008 (instant booking replaces request-to-book), and glossary terms Instant Booking, Grace Cutoff, Late Cancellation, Counted Strike, Monthly Strike Cap, Booking Horizon, Meeting Link (plus a Support Ticket amendment for system-opened tickets) |
| 2026-07-14 | `/codex-review` verified the implementation independently (targeted + full-suite backend tests on a fresh database, root-cause-traced all 33 pre-existing failures rather than assuming, frontend build/test green); reviewed and accepted Codex's one disclosed deviation; cleaned up two pieces of dead code directly; committed in three stops; added the session summary and moved the plan In Progress -> Done |
| 2026-07-15 | Merged `origin/main` (5 commits) into `feat/tutor-onboarding-verification-redesign` ahead of the PR; resolved 4 conflicts in favor of this branch's Admin-into-SuperAdmin consolidation (main's SuperAdmin applicant-review ban and its tests dropped as superseded), kept main's 0057 migration-dependency fix, restored SuperAdmin access to `/admin/tutor-applications`, and annotated main's plan row as superseded |
