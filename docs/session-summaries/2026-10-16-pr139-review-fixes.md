# PR #139 review fixes — 2026-10-16

Implemented the four plans supplied in `pr139-review-plans.patch`, with the review refinements,
plus the patch's trusted-device cleanup addition. Work is uncommitted on
`claude/beautiful-archimedes-8fu8tm`, based on `045cfe0`. Existing reel and documentation work was
preserved. No remote database was migrated and nothing was published.

## Changes

- Mode routing: completed tutors can lose subjects without restarting onboarding. A durable
  completion marker keeps carried verification from skipping first-time tutor setup. Automatic
  switches rerun onboarding and commission gates; Undo returns to a compatible page and expires
  after navigation. Remote refresh reloads the new profile before routing, and subsequent
  automatic switches after a detected remote change require confirmation.
- Backend: verification carry-over uses the latest approved renewal's files, reviewer and date.
  Ranked and fallback recommendations exclude the requesting user, and a cache namespace change
  invalidates previously cached self-recommendations independently of the stored version counter.
- Categories: system rename is blocked, fallback and CBF use the system flag, duplicate system
  categories are merged before uniqueness is enforced, tutors get ordered empty categories from
  an authenticated endpoint, proposals reject the system category, and review-panel edit saves
  refresh category options. Migration 0085's seed data is frozen. Category counts use one query
  with explicit ordering.
- Weights: stale preview and baseline results are discarded, including during debounce and Save.
  Preview and Save merge raw stored weights consistently and reject zero-sum overrides. Existing
  stored-weight fallback behavior remains intact.
- Device trust: issuing a device purges that user's expired and revoked rows while keeping live
  devices. This implements only the cleanup addition; the older trusted-device frontend work is
  still tracked in its original plan.

## Database changes

Apply migrations 0087 and 0088 to the database used for manual testing before running the updated
backend. 0087 adds `tutor_setup_completed_at`, backfills existing configured tutors with submitted
applications or explicit skips, and merges duplicate system categories. 0088 adds the conditional
unique constraint in a separate transaction. Testing caught and resolved PostgreSQL's rejection
of index creation while deferred FK events from duplicate cleanup are pending.

Fresh migrations and the upgrade fixture were tested on an isolated local PostgreSQL 18 server.
The fixture verifies that duplicate categories' subjects move to the canonical row, an established
tutor with no subjects retains completion, and a switching user with no rate remains incomplete.

## Verification results

| Check | Result |
| --- | --- |
| `npm run lint` | Pass |
| `npm run build` | Pass |
| Focused frontend tests: router, auth, catalog, tutor subject setup, weight settings | 29 pass |
| Focused backend classes and migration test | 95 pass |
| Full frontend | 249 pass, 1 skip, 9 pre-existing failures |
| Original `045cfe0` frontend, same dependencies | 232 pass, 1 skip, the same 9 failures |
| Full backend | 555 pass, 1 pre-existing failure |
| Original `045cfe0` backend, matched settings | 540 pass, the same failure |
| `makemigrations --check --dry-run` | No changes detected |
| `git diff --check` | Pass |
| `graphify update .` | Code graph refreshed |

The existing frontend failures are six `BookingTimeRangePicker` cases and three token-layer
checks. The existing backend failure is
`ChatFeatureTests.test_location_update_rejected_inside_grace_cutoff` (200 instead of 400).
Original-commit comparisons ran from a separate temporary snapshot; the working tree was not
reset. Backend runs used local test databases, temporary media storage, a fast test password
hasher, and disabled SMTP credentials for the final runs.

Focused backend classes: `DualRoleModeSwitchTests`, `DashboardRecommendationServiceTests`,
`SubjectCategoryStorageTests`, `TutorSubjectProposalTests`, `AlgorithmWeightNormalizationTests`,
`AlgorithmWeightsPreviewValidationTests`, `TrustedDeviceLoginTests`, `TutorOnboardingStateTests`,
and `ReviewIntegrityMigrationTests`.

## Manual review checklist

These are review steps for the user; they have not been claimed as executed browser tests.

1. As an established tutor, remove the last subject and reload. The dashboard remains accessible.
2. Switch a verified tutee into Tutor for the first time. Rate and subject setup are still required.
3. Follow a tutor deep link from Tutee mode with commission terms unaccepted. The terms gate opens.
4. Follow a deep link that switches mode, then use Undo. The resulting page matches the restored
   mode. Navigate again before using Undo; its action should disappear.
5. Use two browser sessions for a dual-role user. Switch in one, allow the other to refresh, and
   verify its profile and incompatible page update. A subsequent opposite-mode deep link should
   ask before switching. Cancel should keep the current mode.
6. Create an empty category as SuperAdmin. Tutor proposal options include it in display order and
   omit Uncategorized. A system-category rename is rejected; reordering still works.
7. Create a category while editing a proposed subject in the review panel. Subsequent category
   pickers include it without a page reload.
8. With algorithm tools enabled and the network throttled, change tutees and sliders quickly.
   Only the current tutee's ranking and baseline should appear. Save during a pending preview;
   the preview should settle rather than remain stuck loading.

## Remaining limitations

Mode remains account-wide. Requests before a remote switch is detected can still see the other
device's mode; the confirmation reduces silent switching after detection and is not per-device
mode isolation. Existing carried applications are not automatically rewritten because there is
no reliable provenance marker separating them from independently reviewed applications. Pending
verification applications retain the existing product flow; this work adds no new approval gate.
