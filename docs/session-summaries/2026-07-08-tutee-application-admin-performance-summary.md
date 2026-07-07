# Tutee/tutor application admin performance fix — Summary

**Plan:** none — ad-hoc bug diagnosis triggered by a production Daphne log line and a live user
report ("approving takes too long"), not a pre-planned feature.
**Status:** Done

## What triggered this

A production log line from Daphne:

```
WARNING daphne.server Application instance <Task cancelling ...> for connection <WebRequest ...
GET /api/admin/tutee-applications/ ...> took too long to shut down and was killed.
```

Initial read suggested a server-shutdown timing issue; reading the installed `daphne==4.1.2`
source (`daphne/server.py:263` `application_checker()`) showed this warning only fires when a
**client disconnects** while the view is still running, and the view then keeps running past
`application_close_timeout` (10s default) — i.e. the endpoint itself was slow enough that the
client (browser) gave up before the server responded.

## Root causes found

1. **N+1 query in the tutee/tutor application list endpoints.** `TuteeApplication` /
   `TutorApplication.latest_document_renewal_review()` (`backend/studybuddy/models.py:419`) hits
   the DB fresh on every call unless a `renewal_reviews_cache` attribute was prefetched.
   `TuteeApplicationSerializer` / `TutorApplicationSerializer` call it unconditionally in
   `get_review_type` plus 6 more times across the `get_latest_document_renewal_*` fields
   (`backend/studybuddy/serializers.py:713-784`) — 7+ queries per row, and the existing
   `Prefetch(..., to_attr='renewal_reviews_cache')` in `AdminTuteeApplicationListView` /
   `AdminTutorApplicationListView` only attached when `?status=approved` was passed, so the
   default (unfiltered) list — the exact endpoint in the log line — always hit the slow path.
   Also found the existing `.only()` on that Prefetch was missing `rejection_reason`,
   `school_id`, `enrollment_proof` — fields the serializer actually reads off the cached renewal —
   causing a second, hidden deferred-field N+1 even when the prefetch *was* attached.

2. **Synchronous SMTP send blocking admin approve/reject requests.** Surfaced by the user directly
   ("also fix when approving it takes too long"). `AdminTutee/TutorApplicationDetailView.patch()`
   and `AdminTutee/TutorDocumentRenewalDetailView.patch()` called
   `send_application_approved_email` / `send_application_rejected_email` /
   `send_document_renewal_result_email` in-request, each doing a live SMTP round-trip
   (`backend/studybuddy/email_utils.py`). Unlike password-reset/notice emails, which already route
   through Django-Q2 (`backend/studybuddy/mailer.py`), these had no async path.

## What shipped

- `backend/studybuddy/admin_views.py`: `AdminTuteeApplicationListView.get()` and
  `AdminTutorApplicationListView.get()` now attach the `document_renewal_reviews` Prefetch
  unconditionally (not just on `status=approved`), with the `.only()` field list completed.
- `backend/studybuddy/email_utils.py`: added `send_application_approved_email_task`,
  `send_application_rejected_email_task`, `send_document_renewal_result_email_task` (re-fetch the
  profile by id and call the existing sync sender — matches `mailer.py`'s established
  task/enqueue split) and `enqueue_application_approved_email`,
  `enqueue_application_rejected_email`, `enqueue_document_renewal_result_email`, each dispatching
  via `django_q.tasks.async_task` the same way `mailer.enqueue_document_renewal_reminder` does.
- The four real (non-dev-tool) approve/reject call sites in `admin_views.py`
  (`AdminTutee/TutorApplicationDetailView.patch`, `AdminTutee/TutorDocumentRenewalDetailView.patch`)
  now call the enqueue helpers instead of sending synchronously; the redundant outer
  `try/except` around them was dropped since the inner `send_*` functions already catch and log
  their own exceptions, and `async_task` in production only inserts a queue row (no exception to
  catch on the request thread).
- Left the `VERIFICATION_DEV_TOOLS_ENABLED`-gated debug endpoint's direct `send_application_*`
  calls untouched (`send_received`/`send_approved`/`send_rejected` actions) — it's a manual
  test-email trigger, not a real admin action, and out of scope for this fix.

## New regression test

`test_admin_tutee_application_list_query_count_does_not_scale_with_n`
(`backend/studybuddy/tests.py`, `TuteeVerificationPhase3Tests`) captures query count for 1 vs 5
tutee applications on the unfiltered list endpoint and asserts it stays flat (±1), rather than
scaling linearly — was red before the Prefetch fix, green after.

## Verification

- New regression test passes.
- `VerificationEmailWiringTests`, `EmailUtilsRoleLabelTests`, `VerificationDevToolsTests`,
  `VerificationDevToolsAdminEndpointTests`, `TutorDocumentRenewalTests`,
  `ApplicationVerificationSharedBaseTests`, `TuteeVerificationPhase3Tests`: 47 tests total, 2
  pre-existing failures (`test_enforcement_override_flips_gate`,
  `test_403_for_superadmin_when_flag_off`) confirmed present on unmodified code too (env/feature-flag
  defaults, unrelated to this change) — everything else passes.
- Updated 4 existing tests that mocked the old direct `send_application_*` /
  `send_document_renewal_result_email` calls to mock the new `enqueue_*` helpers instead, since the
  call sites changed.
- Did not run the full backend suite (large, slow locally); scoped to every test class touching
  the changed views/serializers/email paths.

## Notes / follow-ups not done

- Did not touch the dev-tools debug endpoint (`_verification_dev` / `SEND_ACTIONS`) — still sends
  synchronously, by design (manual one-off test trigger, not a real user-facing path).
- Running these tests locally sends real emails when `EMAIL_HOST_USER`/`EMAIL_HOST_PASSWORD` are
  configured in the environment — pre-existing behavior of these tests, not introduced by this
  change (they called the same sync senders directly before).
