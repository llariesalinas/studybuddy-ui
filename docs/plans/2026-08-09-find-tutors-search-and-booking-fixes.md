---
title: Find Tutors search correctness and booking location fixes
date: 2026-08-09
status: In Progress
summary: Honest search results, one shared definition of a taken slot, and a restored tutor location edit.
spec: ../mockups/2026-08-09-find-tutors-fallback-banner.html
---

# Find Tutors search correctness and booking location fixes

## Status & Progress Summary

**In Progress — full suite cleared, ready for manual verification and commit.** All code written
and uncommitted on `fix/find-tutors-search-and-booking-location`.

- [x] Bug diagnosed and three follow-on defects found during the audit
- [x] Design chosen and mockup promoted
- [x] Backend: shared status constant, availability rule, stage return, date validation
- [x] Backend: location edit window
- [x] Frontend: banner, chips, location editor, dead accept/reject removed
- [x] Tests written and updated
- [x] **Full Django suite: confirmed pre-existing — baseline-vs-branch diff done 2026-08-09**
- [ ] Manual verification in the running app
- [ ] Commit (uncommitted; branch `fix/find-tutors-search-and-booking-location`)

### Resume here (resolved 2026-08-09)

Code is complete and uncommitted on `fix/find-tutors-search-and-booking-location`. Nothing is
stashed; the working tree holds everything.

**Resolved: the 8 full-suite failures are pre-existing at `HEAD`, not caused by this branch.**
Baseline (`HEAD`, throwaway worktree) and branch full-suite runs were diffed and produced the
identical 7 failures + 1 error, same tests, same symptoms:

| Test | Symptom |
| --- | --- |
| `SuperAdminRedesignApiTests.test_analytics_includes_completion_subject_popularity_and_csv` | ERROR: duplicate key on `PaymentMethod.code=online` |
| `DevWalletFundsTests.test_dev_wallet_funds_404s_when_debug_disabled` | 200 != 404 |
| `TuteeProfileTests.test_upload_avatar_success` | 400 != 200 |
| `TutorCashOutTests.test_cashout_sends_centavos_and_normalizes_provider_amounts` | 10.0 != 12.5 |
| `TutorCashOutTests.test_failed_callback_refunds_amount_and_fee_once` | 403 != 200 |
| `TutorProfileTests.test_upload_avatar_success` | 400 != 200 |
| `VerificationDevToolsAdminEndpointTests.test_403_for_superadmin_when_flag_off` | 404 != 403 |
| `VerificationDevToolsTests.test_enforcement_override_flips_gate` | env flag already set |

None touch search, availability, booking status, or the location edit. The branch run counted 392
tests against the baseline's 381 (this branch's own added tests, all passing); line numbers in
tracebacks shift accordingly but point at the same assertions. The worktree has been removed.

Also directly observed passing: `RecommendTutorsViewTests` 17/17, `ChatFeatureTests` 36/36,
`makemigrations --check` clean, `npm run lint` clean, `npm run build` clean, `npm run test` 136/136.

Remaining before commit: manual verification in the running app, then the commit plan below.

Gotchas that cost time getting here (kept for next time):
- **`manage.py test` exits 0 even when the suite fails here.** Read the log; never trust the exit
  code.
- Always pass `--keepdb`. The DB is remote (Supabase behind a Supavisor pooler) which holds an idle
  session open, so Django cannot drop and recreate `test_postgres` — it prompts and then dies on
  EOF. A full run is ~20-24 minutes.
- Only one run at a time; both share the same remote test database.

**Commit plan** (agreed: bundle the SuperAdmin work in). Two commits on this one branch, so the
unrelated features stay separately revertable — squash to one if preferred:
1. `fix: make tutor search report its match stage and share one booked-slot rule`
   — `models.py`, `views.py`, `chat/services.py`, `findTutors.js`, `chat.js`, `FindTutors.vue`,
   `ChatBanner.vue`, `BookingCard.vue`, this plan, the mockup, the regenerated dashboard, and the
   matching `tests.py` hunks.
2. `feat: surface pending verifications in the SuperAdmin pending-actions queue`
   — `admin_views.py`, `AdminTutorApplications.vue`, `SuperAdminDashboard.vue`,
   `docs/plans/2026-08-09-superadmin-pending-verifications.md`, and its `tests.py` hunk
   (`test_pending_actions_includes_pending_verifications`). This work predates this session and was
   already in the tree; it has been read and contains no secrets.

`tests.py` carries hunks from both, so splitting needs `git add -p` on that file.

## Goal

Searching Python / Online / August 9 returned four tutors under the header "Tutors available any
time on August 9" when no tutor matched that date at all. Fixing that surfaced three more defects in
the same area, including a live crash. Fix them together.

## Approach

### 1. Search must say which stage produced its results

`get_recommendation_candidate_tutors` (`views.py:3813`) runs a three-stage cascade and returns only a
queryset, so the caller cannot tell an exact match from a fallback:

| Stage | Filter | Banner |
| --- | --- | --- |
| `exact` | date + every requested slot free | none, confident header |
| `date_only` | date matched, time range did not | "No tutors free 2:00-4:00 PM on August 9" |
| `subject_only` | date dropped entirely | "No tutors available on August 9" |

The function returns `(queryset, match_stage)`; the response becomes
`{ "match_stage": ..., "tutors": [...] }`. Only one caller exists, so the signature change is
contained.

Copy gives **no reason** for an empty date. `TutorAvailability.DAY_CHOICES` (`models.py:705`)
includes `'Sun'`, so "nobody works Sundays" is a seed-data artifact (`seed_data.py:50` stops at
`Sat`), not a rule, and `subject_only` also fires for full-day blocks and uncovered dates.

On `subject_only`, cards show the tutor's recurring weekdays labelled **"Usually teaches"** — these
come from the weekly pattern and do not account for one-off blocks or bookings, so hedged wording is
required. A concrete "next free date" is deliberately out of scope; getting it wrong would reproduce
the bug class being fixed.

### 2. One definition of a taken slot

Four places decide whether a booking blocks a slot. The database constraint (`models.py:859`) and
search agree on four statuses. The tutor's calendar (`views.py:2348`) and the booking guard
(`views.py:2624`) each omit **Awaiting Payment Verification**, and that gap is a live crash:

1. Tutee A books 2 PM and pays -> status `Awaiting Payment Verification`
2. Tutor has not checked the proof yet
3. Tutee B opens the tutor's calendar and sees 2 PM as free
4. Tutee B uploads a receipt and submits
5. The guard finds no conflict and lets it through
6. `Booking.objects.create` (`views.py:2676`) hits the database constraint -> unhandled
   `IntegrityError` -> 500, after Tutee B has already paid

Extract `ACTIVE_BOOKING_STATUSES` into `models.py` and have all four read it. Cancelled and Rejected
stay non-blocking — a cancelled booking must free the slot, and there is cleanup that deletes those
rows for exactly that reason (`views.py:2637-2641`).

### 3. A tutor is hidden only when nothing is left

A slot is unavailable when it is booked, blocked for the whole day, blocked individually, **or
already past** — the rule the tutor's calendar already applies (`views.py:2393`). Search never
considered past times at all, so a search for today at 8 PM returns tutors whose slots ended at 2 PM.

Applying it per stage:

- `exact` — every requested slot is available
- `date_only` — at least one slot is available
- `subject_only` — **no date filtering at all**, including no exclusions. The date was dropped, so
  filtering by it is incoherent; a tutor booked solid on the 9th may be ideal on the 10th.

### 4. A search requires a valid date

`parse_request_date` (`views.py:714`) returns `None` for anything unreadable, and the code treats
that as "no date given" — skipping both date stages and every exclusion, returning the widest
possible list with no signal. Not reachable from the UI today, but the endpoint should not depend on
that. Missing, unparseable, and out-of-window dates all get a 400. The window matches
`BookingDatePicker.vue:74` (today through +14 days), which also closes the tab-left-open-past-midnight
case that `FindTutors.vue:410` does not re-check.

### 5. Restore the tutor's location edit

`preferred_location` is the free-text meeting spot the tutee proposes, kept for auditing. Changes are
logged and pushed live to both parties (`create_booking_event`, `chat/services.py:692-700`). But
every edit path requires `Pending` — `BookingCard.vue:92`, `chat/services.py:200`, `views.py:4489` —
and instant booking creates bookings as `Confirmed` (`views.py:2686`). The edit is unreachable, so an
audited value can never be corrected.

New rule: editable while the booking is `Confirmed` or `Awaiting Payment Verification`, and more than
`GRACE_CUTOFF_HOURS` (12) before the session — the same Grace Cutoff as penalty-free cancellation.
Bookings created inside that window (`is_born_late`) stay frozen, consistent with having no
cancellation window. Tutor only.

**Do not reuse the `pending_location` intent.** It renders the location editor *and* the accept
button (`ChatBanner.vue:7`, `:411`), which calls `bookings/<id>/approve/` — a route that no longer
exists in `urls.py`. Instead the server computes one `can_edit_location` flag on the booking context;
`ChatBanner` renders the editor inside its existing `confirmed` branch and `BookingCard` reads the
same flag.

### 6. Dead code removed

- `acceptBooking` / `rejectBooking` (`chat.js:772-782`) call deleted routes.
- `location` is posted to `/recommend-tutors/` (`FindTutors.vue:423`) and never read.
- `total_sessions` is missing from the search payload, which is why every card reads "0 sessions"
  even for a 3.88-rated tutor.

Mockup: [docs/mockups/2026-08-09-find-tutors-fallback-banner.html](../mockups/2026-08-09-find-tutors-fallback-banner.html)

## Steps

1. `ACTIVE_BOOKING_STATUSES` in `models.py`; `Booking.Meta` constraint uses
   `list(ACTIVE_BOOKING_STATUSES)` so no migration is generated.
2. Point the calendar (`views.py:2348`) and the booking guard (`views.py:2627`) at it; drop
   `RECOMMENDATION_BLOCKING_STATUSES`.
3. Add match-stage constants and a canonical weekday order derived from `WEEKDAY_MAP`.
4. Add a bulk helper that maps tutor -> available slot times for a date, accounting for bookings,
   both override kinds, and past times.
5. Rewrite the cascade in `get_recommendation_candidate_tutors` around that helper; return
   `(queryset, stage)`.
6. `recommend_tutors_view`: require a valid in-window date; envelope the response; add
   `available_days` and `total_sessions`.
7. `can_edit_location` on the booking context; widen `update_booking_location`'s gate.
8. `ChatBanner` location editor in the `confirmed` branch; `BookingCard.canEditLocation` reads the
   flag; remove the dead accept/reject calls.
9. `FindTutors.vue`: read the envelope, drop `location` from the request, replace `searchScopeLabel`
   with the stage banner, add chips and the two banner actions.
10. Update the five tests that call the endpoint without a date; add stage, availability, and
    location-window coverage.

## Risks

- **Breaking response shape** — the envelope breaks any consumer reading `response.data` as a list.
  Known: `FindTutors.vue:426` and the tests.
- **Spurious migration** — changing the constraint condition's literal to a constant can alter its
  deconstruction. Verify with `makemigrations --check`.
- **Resurrecting the accept button** — covered above; the flag approach avoids the intent entirely.
- **Chips could mislead** — "Usually teaches" is load-bearing; do not tighten it to "Available"
  without making the data override-aware.
- **Performance** — the candidate loop already does per-tutor work (`views.py:3827-3835`). The
  availability helper must be bulk, not per-candidate.

## Out of scope

- `is_booked` on `TutorAvailability` (`models.py:719`) is a landmine: the only code setting it is
  commented out (`views.py:2431-2470`), and reviving it would permanently kill a tutor's recurring
  slot. Left alone, noted.
- Real location matching (tutors declaring where they can meet) is a feature, not a fix.
- `rating ?? 5.0` (`FindTutors.vue:434`) invents a rating for unrated tutors.

## Checks to run

- `cd backend && python manage.py makemigrations --check --dry-run` — no new migrations.
- `cd backend && python manage.py test studybuddy` — all pass.
- `npm run lint` and `npm run build` — clean.
- Manual: search a date nobody covers (expect the `subject_only` banner and chips); a date with a
  time range nobody covers (expect `date_only`, no chips); a covered range (expect no banner).

## Changelog

- **2026-08-09** — Created from a grilling session that started with a misleading search header and
  uncovered three further defects. Decisions: hide a tutor only when nothing is left that day; one
  shared four-status list across the calendar, guard, and search; date required and range-checked;
  location editable by the tutor until the 12-hour Grace Cutoff, frozen for late-born bookings.
  Consolidated into one plan and one branch at the user's request, superseding the narrower
  fallback-banner plan.
- **2026-08-09** — Implemented on `fix/find-tutors-search-and-booking-location`. Notes from the
  build:
  - `GRACE_CUTOFF_HOURS` moved to `models.py` alongside `ACTIVE_BOOKING_STATUSES` and a new
    `LIVE_BOOKING_STATUSES`, so `Booking.tutor_can_edit_location()` is reachable from both `views.py`
    and `chat/services.py` without a circular import. `mailer.py`'s deliberate copy left alone.
  - The cascade was restructured rather than patched: one bulk
    `get_available_slot_times_by_tutor()` read backs all three stages, which removed the duplicated
    exclusion queries entirely.
  - `RecommendTutorsViewTests.search_date` was a hardcoded past date; now computed as the next
    Monday so date validation and past-time filtering cannot make it rot.
  - Two existing tests asserted the old behaviour and were rewritten, not patched around:
    `test_fallback_excludes_known_booking_conflicts` expected a partially-booked tutor to be hidden
    while a tutor with no availability that weekday was shown — the reverse of what is correct;
    `test_missing_date_time_fields_remain_supported` pinned the optional-date behaviour this plan
    deliberately removes.
  - `confirmAndAccept` / `accept` / `reject` deleted from `ChatBanner.vue` along with
    `acceptBooking` / `rejectBooking` in `chat.js`; the location editor moved into the `confirmed`
    branch behind the server's `can_edit_location` flag so the dead buttons could not come back.
  - Checks: `makemigrations --check` clean, `RecommendTutorsViewTests` 17/17,
    `ChatFeatureTests` 36/36, `npm run lint` clean (4 pre-existing `no-undef` in `make_algo_pptx.*`,
    confirmed present on a stashed tree), `npm run build` clean, `npm run test` 136/136.
- **2026-08-09** — Paused before committing. The full Django suite reported
  `FAILED (failures=7, errors=1)` across 392 tests while exiting 0, and the captured log held only
  4 of the 8. A clean-`HEAD` baseline run was started in a temporary worktree to establish
  provenance and was stopped partway (~64/381 tests, no verdict); the worktree has been removed and
  the working tree is untouched. Resume instructions and the commit plan are in the Status section
  above. An earlier full run that appeared to pass was the one terminated to free the test
  database — its exit 0 came from the kill, not a green suite, and it is not evidence of anything.
- **2026-08-09** — Resumed and closed out the baseline-vs-branch comparison. Ran the full suite at
  `HEAD` in a throwaway worktree (381 tests, `.env` copied in locally, not committed) and again on
  the branch (392 tests); both produced the same 7 failures + 1 error, same tests and symptoms
  (Redis-mock, stale env var, avatar-upload media config, PayMongo fee normalization — none in the
  touched areas). Confirmed pre-existing; worktree removed. Full findings and the failure table are
  in "Resume here" above. Remaining: manual verification in the running app, then commit per the
  plan below.
