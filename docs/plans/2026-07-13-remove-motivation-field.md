---
title: Remove Motivation field from Tutor/Tutee application flows
date: 2026-07-13
status: Done
summary: Removed the "Motivation" (reason_to_tutor) free-text field from Tutor registration and Tutee verification submission entirely, including the backend model column, while preserving the unrelated "renewal note" field it shared UI/variable names with.
spec:
---

# Remove Motivation field from Tutor/Tutee application flows

## Status & Progress Summary

**Status:** Done · **Last updated:** 2026-07-13

Grilled end-to-end: confirmed the field (`reason_to_tutor`, labeled "Motivation") only appears in
the Tutor registration flow today, not Tutee registration — but is wired into the separate Tutee
verification-submission flow, and shares a UI/variable name (not a DB column) with the unrelated
document-renewal "note" field, which stays. User confirmed full removal including the backend
column and DB data loss on the local dev DB. Implemented all 8 steps, migrated the local dev DB,
ran the full backend suite plus 26 targeted application/renewal/verification tests (all pass),
lint and build clean, and a two-axis (Standards/Spec) review found zero hard findings on either
axis. See [Summary](../session-summaries/2026-07-13-remove-motivation-field-summary.md).

## Goal

Remove the optional "Motivation" / "Why do you want to become a tutor?" free-text field
(`reason_to_tutor` on `ApplicationVerificationBase`) from every place it appears — Tutor
registration, the Tutor/Tutee initial verification submission and resubmission screens, and the
admin application review screen — including dropping the backend DB column, since the user
confirmed data loss on the local dev DB is acceptable.

## Approach

Grilling surfaced that `reason_to_tutor` is not confined to "the registration flow" as originally
framed:

- It only appears in the **Tutor** signup flow today (`TutorScreeningModal.vue` → `Register.vue`);
  no Tutee-facing component renders it during registration.
- It is however wired into the **Tutee verification** flow (`TutorApplicationStatus.vue`'s shared
  `showInitialTuteeSubmission` block, and `tutee_application_resubmit` in `views.py`) — a separate
  feature (see `docs/plans/2026-07-01-tutee-verification-*`) where tutees submit School ID/proof of
  enrollment after registering, not during it.
- The same field name and the same `resubmitData.reasonToTutor` JS variable is also reused, with a
  different label ("Note to Reviewer" / "Renewal Note"), for the **document renewal** flow. On the
  backend this is a genuinely different column — `DocumentRenewalReviewBase.reason_to_tutor` on
  `TutorDocumentRenewalReview` / `TuteeDocumentRenewalReview` — which the user did **not** ask to
  remove.

So the fix is: delete `ApplicationVerificationBase.reason_to_tutor` (the column backing
`TutorApplication`/`TuteeApplication`) everywhere it is read or written for *initial
submission/resubmission*, but leave `DocumentRenewalReviewBase.reason_to_tutor` (the renewal note)
fully intact. Because both flow through the same request key (`reason_to_tutor` in the multipart
payload) and the same shared Vue component, the surgical change in `views.py` and
`TutorApplicationStatus.vue` is to keep reading/sending that key only on the renewal branch, and
stop writing it to `TutorApplication`/`TuteeApplication` — not to delete the key path outright.

## Steps

1. **Backend model** — remove `reason_to_tutor` from `ApplicationVerificationBase` in `models.py`;
   run `makemigrations` to drop the column from both `TutorApplication` and `TuteeApplication`.
2. **Backend serializers** — remove `'reason_to_tutor'` from `TutorApplicationSerializer` and
   `TuteeApplicationSerializer`'s `Meta.fields`. Leave `TutorDocumentRenewalReviewSerializer` /
   `TuteeDocumentRenewalReviewSerializer` untouched (different model, kept field).
3. **Backend views** (`views.py`):
   - Registration view (`role == "Tutor"` branch): remove the `reason_to_tutor` read and its key
     in the `TutorApplication.objects.update_or_create` defaults.
   - `tutor_application_resubmit` / `tutee_application_resubmit`: remove the
     `application.reason_to_tutor = reason_to_tutor` write (rejected-resubmit path) and the
     `'reason_to_tutor': reason_to_tutor` key in the initial `get_or_create` defaults (tutee only).
     Keep the `reason_to_tutor = request.data.get(...)` read and its pass-through into
     `create_tutor_/tutee_document_renewal_submission` untouched — the renewal branch still needs it.
   - `tutor_document_renewal_submit` / `tutee_document_renewal_submit` /
     `create_tutor_/tutee_document_renewal_submission`: no changes (pure renewal path).
4. **Frontend registration** — remove the Motivation textarea from `TutorScreeningModal.vue`
   (`localReason`, `store.reasonToTutor` write), the `reasonToTutor` state from
   `stores/registrationinfo.js`, and the `formData.append('reason_to_tutor', ...)` line from
   `Register.vue`.
5. **Frontend application status** (`TutorApplicationStatus.vue`):
   - Remove the "Motivation (Optional)" field entirely from the initial-tutee-submission block
     (`showInitialTuteeSubmission`).
   - Gate the shared resubmit-form's note field with `v-if="flow.kind === 'renewal'"` so it only
     renders for renewals; drop the now-dead non-renewal half of the `notesLabel`/`notesPlaceholder`
     ternaries.
   - Drop the `application.value.reason_to_tutor` fallback when prefilling `resubmitData.reasonToTutor`
     (that source no longer exists in the API response).
   - Only send `formData.append('reason_to_tutor', ...)` on the renewal branch.
6. **Admin review** (`AdminTutorApplications.vue`): simplify `selectedReviewNoteLabel` to always
   read "Renewal Note" (the non-renewal branch becomes unreachable once the application serializers
   stop returning `reason_to_tutor`, since `selectedReviewNote`'s `v-if` already hides the block
   when empty). Leave the `readFirst([...])` key list untouched — `reason_to_tutor` is still the
   real key the renewal-review serializers use.
7. **Backend tests** (`tests.py`): drop the `"reason_to_tutor"` key from the non-renewal payloads
   (initial tutee submission, resubmit-after-rejection, the two email-label tests). Keep it in the
   two renewal-payload tests unchanged.
8. **Demo data** (`reset_demo_data.py`): remove the `reason_to_tutor=self.fake.sentence(...)` kwargs
   from the two direct `TutorApplication`/`TuteeApplication` creations.

## Risks

- Missing a reference to `application.reason_to_tutor` anywhere would break at runtime once the
  column is dropped — mitigated by having grepped every occurrence across backend and frontend
  before editing.
- The renewal-note prefill (`resubmitData.reasonToTutor` sourced from `application.value.renewal_note`)
  was already effectively broken pre-existing (the main status serializer never actually exposed a
  `renewal_note` key), so removing the `reason_to_tutor` half of that fallback just means the box
  starts empty for renewals too — a pre-existing gap, not a new regression, and out of scope to fix.
- Local dev DB will lose any existing `reason_to_tutor` data on migration — confirmed acceptable.

## Checks to run

- `python manage.py makemigrations` (review the generated migration touches only the two
  `RemoveField` operations expected) then `python manage.py migrate`.
- `python manage.py test studybuddy.tests` — full backend suite; compare failures against the
  known pre-existing baseline.
- `npm run lint` and `npm run build`.
- Manual/browser check: Tutor registration flow, Tutee initial verification submission, a rejected
  resubmit, and a document renewal submission (the note field should still work there), plus the
  admin application review panel for both a plain application and a renewal.

## Changelog

| Date | Change |
|------|--------|
| 2026-07-13 | Grilled and wrote the plan (Approved); implementation not yet started |
| 2026-07-13 | Implemented all 8 steps, generated and applied migration 0075, ran full backend suite (289 tests; 28 failures/5 errors all pre-existing and unrelated) plus 26 targeted tests (all pass), lint and build clean; two-axis review found zero hard findings; marked Done and linked summary |
