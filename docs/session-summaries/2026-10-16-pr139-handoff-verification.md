# PR #139 handoff verification — 2026-10-16

Status: Done — approved shared-demo migrations and all eight browser checks are complete.
Full suites have no new failures. No application code changed during verification.

## Database and backup

The configured shared demo is `postgres` on
`aws-1-ap-southeast-1.pooler.supabase.com`. The user explicitly approved backing up and migrating
this shared demo on 2026-10-16. The earlier `tenant/user not found` connection failure is resolved.

Before any schema changes, pg_dump created the custom-format archive
`approved-before-0087-0088-20261016-012908.dump` under the local Codex `backups/studybuddy` folder.
It is 1,010,146 bytes. Both pg_restore's archive listing and a complete SQL extraction to the null
sink succeeded. SHA256:
`3649590d97e65f128312452d06c0b813f827eecc8637836321c6b6e743aed6b3`.
The backup stays outside the repository and has not been uploaded.

The migration plan contained only `0087_review_integrity` and
`0088_unique_system_subject_category`; both applied successfully. The database already recorded
an independent `0087_clamp_legacy_hourly_rates`, which was left untouched. Django identifies
migrations by full name, so that record did not conflict with these operations.

Post-migration spot checks:

- Exactly one system SubjectCategory.
- 177 established tutor profiles marked complete.
- Zero eligible profiles missing the completion marker. Eligibility is the migration's configured
  rate plus submitted application or explicit verification skip; first-time setup remains incomplete.
- `makemigrations --check --dry-run`: no changes detected.

## Dependency and suite checks

| Check | Result |
| --- | --- |
| Branch | claude/beautiful-archimedes-8fu8tm, application fixes at 94bf7f1 |
| npm ci | Pass |
| Virtual-environment pip install -r backend/requirements.txt | Pass |
| npm run lint | Pass, no application-file changes |
| npm run build | Pass |
| Full Vitest | 249 pass, 1 skip, 9 known failures; zero new failures versus 045cfe0 |
| Two clock-sensitive tests, TZ=Asia/Manila | 2 pass |
| Same two tests, TZ=UTC | 2 fail on this branch and 045cfe0 |
| Full Django suite against the separate remote test_postgres database | 556 run, 555 pass, 1 known failure |

The real-environment backend run used booking dev tools enabled and `--keepdb --noinput`.
Only outbound mail transport was redirected to in-memory delivery with dedicated SMTP credentials
cleared for that process. No live email was sent. The run completed in 2,162.288 seconds.

The single backend failure is
`ChatFeatureTests.test_location_update_rejected_inside_grace_cutoff`: 200 instead of 400.
The nine frontend failures remain six BookingTimeRangePicker cases and three CSS-token checks.
No pre-existing failure was fixed.

The two timezone-sensitive tests construct dates and wall-clock fixtures in the host timezone,
while parseSessionDateTime interprets session timestamps with an explicit Manila +08:00 offset.
The tests therefore describe different instants under UTC. A separate test-only change should
use offset-qualified instants and Manila-formatted fixtures, with a fixed clock for the composable
case, or standardize the test process timezone. No fix was made on this branch.

## Browser environment

The local application used the migrated shared demo with seven disposable accounts named
PR139 Review, isolated browser origins, and an isolated django-q worker queue
`studybuddy-pr139-review`. Scheduler processing and outbound mail were disabled for the temporary
local QA runtime. The shared demo's deployed configuration and existing queued jobs were untouched.
Temporary runtime scripts and fixture manifests are outside the repository.

For delayed preview testing, a temporary local HTTP proxy forwarded real requests to the local
Django server and held tutee A's completed preview responses for four seconds, while B's had a
0.1-second hold. This produced verified B-before-A delivery without changing application code.

## Browser checklist

| Step | Result and evidence |
| --- | --- |
| 1. Established tutor removes final subject | PASS: removed the only subject, saved, confirmed zero database relations, and reloaded the Tutor dashboard successfully. |
| 2. First tutee-to-tutor setup | PASS: carried verification still opened required rate setup. With an intermediate configured-rate fixture and no subjects, a dashboard request redirected to subject setup with Continue disabled. |
| 3. Deep link reaches commission terms | PASS: opened the Tutor dashboard URL from Tutee mode and reached /tutor-commission-terms. No agreement was accepted through the UI. |
| 4. Undo and navigation expiry | PASS: Undo restored /dashboard in Tutee mode. Navigating from an auto-switched dashboard to Wallet removed Undo after 1,184 ms, before its expiry timer. |
| 5. Cross-session synchronization and confirmation | PASS: two independent browser origins shared the same QA account. Normal refresh reloaded Tutee profile state and replaced the stale Tutor profile route with /dashboard. Browser Back toward the prior Tutor wallet route showed a native confirmation; cancelling retained /dashboard with Tutee checked. |
| 6. Empty categories and system rename | PASS: created an empty category as QA SuperAdmin through the real API, verified it in Tutor proposal options, verified Uncategorized absent, and received 400 for a system rename attempt. |
| 7. Review-panel edit category refresh | PASS: saved PR139 QA Edited Category on the disposable proposal, reopened Edit without reloading, and found the new category in the dropdown. |
| 8. Delayed preview and Save | PASS: proxy logs prove B responses preceded A; after all responses, the selected B retained its single distinct tutor and unchanged baseline. Saving during delayed A preview completed with Save disabled, zero Scoring messages and current ranking displayed. |

All eight original weight values and their audit fields were restored after the Save test, with
an actor check to avoid overwriting any concurrent external edit. No regression has been traced
to 94bf7f1 during this verification pass.

Passing screenshots are saved locally in the chat's visualization folder under
`pr139-verification/`: first-time-rate-required.jpg, first-time-subjects-required.jpg,
commission-gate.jpg, undo-toast.jpg, remote-mode-reroute.jpg, empty-category-options.jpg,
category-refresh-after-edit.jpg, preview-keeps-current-tutee.jpg, and
save-during-preview-settled.jpg. They have not been published to the repository.


## Cleanup and completion

All seven disposable QA users and profiles, both QA subject records, and both QA categories were
removed after ownership and booking-reference checks. The one system category remains. Weight
values and audit metadata were verified against the pre-Save snapshot before deleting the QA
administrator. Temporary QA browser tabs were closed, and no listeners remain on the QA ports
8000, 8001, 5173, 5174 or 5175.

The confirmation check used browser history to exercise a cross-mode SPA navigation without
reloading the page, preserving the in-memory remote-change flag. The mode remains account-wide;
this verification does not claim per-device isolation or persistence of that flag across reloads.

Additional screenshot: cancelled-remote-mode-switch.jpg. No application regression was found,
so no application code was changed. Existing frontend and backend failures are left untouched.
The handoff is complete with those documented baseline failures.
