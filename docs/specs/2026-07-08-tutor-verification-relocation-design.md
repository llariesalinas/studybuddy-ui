# Tutor Verification Relocation — Design Spec

## Goal

Move tutor enrollment verification (School ID + proof of enrollment) off the registration/onboarding
flow so it works exactly like tutee verification: register free, verify later, and get gated only at
the specific action that requires it (accepting a booking) — never locked out of the whole app.

## Background

Today the two roles are asymmetric:

- **Tutee**: registers free. No documents required at signup. Verification is submitted later via
  `/application-status`, and only `confirm_payment_and_book` is gated on it
  (`can_create_new_booking`). The rest of the app (dashboard, browsing, profile) is always reachable.
  This was built deliberately across `docs/plans/2026-07-01-tutee-verification-phase1-model.md`
  through `phase4-email-devtools.md`.
- **Tutor**: must upload School ID + enrollment proof *during registration*, via
  `TutorScreeningModal.vue`. A `TutorApplication` is created immediately with `application_status:
  'pending'`. Until it's `approved`, the router's global guard
  (`needsTutorApplicationLockout` in `src/services/tutorApplicationState.js`) redirects every route
  to `/application-status` — the tutor cannot see their dashboard, schedule, or profile at all.

`approve_booking` (tutor accepting a session) already calls `can_create_new_booking`, the same
function `confirm_payment_and_book` uses for tutees — so the action-specific gate for tutors is
already implemented and working. The only thing keeping tutor verification "on the onboarding" is
(a) registration requiring documents up front, and (b) the router's full-app lockout for
never-approved tutors. Removing those two things is sufficient to make tutor verification behave
like tutee verification; no new gating logic is needed.

One backend gap: `tutor_application_resubmit` requires an existing `TutorApplication` (404s
otherwise), because until now a tutor always had one from registration. `tutee_application_resubmit`
already handles this via `get_or_create` (first submission and resubmission share one endpoint) —
the tutor endpoint needs the same treatment.

## Non-goals

- No grace-period/enforcement-date toggle for tutors (unlike `tutee_verification_enforced`).
  `can_create_new_booking` has never given tutors a grace period — this spec doesn't add one.
- No change to `approve_booking`, the renewal flow, `TutorApplicationSerializer`, or any model
  fields.
- No migration of existing `TutorApplication` rows — this only changes the flow for new
  registrations going forward.

## Backend changes

### `register_user` (`backend/studybuddy/views.py`)

Remove, for `role == "Tutor"`:
- The `school_id`/`enrollment_proof` requirement (`400` if missing).
- The `TutorApplication.objects.update_or_create(...)` block and its confirmation email.

Keep: `Tutor.objects.get_or_create(profile=profile)` (the Tutor row itself still needs to exist for
availability/wallet/etc. to work) and the `PlatformActivity` registration log.

Also remove the `is_rejected_tutor` recovery branch in the `existing_user` check — re-registering
with the same email should behave identically for both roles now ("User already exists"). A
rejected tutor resubmits via `/application-status`, same as a rejected tutee.

### `tutor_application_resubmit` (`views.py`)

Change the lookup from `TutorApplication.objects.select_for_update().get(...)` (404 if missing) to
`get_or_create`, mirroring `tutee_application_resubmit` exactly:

```python
application, created = TutorApplication.objects.select_for_update().get_or_create(
    profile=request.user.userprofile,
    defaults={
        'school_id': school_id,
        'enrollment_proof': enrollment_proof,
        'reason_to_tutor': reason_to_tutor,
        'application_status': 'pending',
    }
)

if created:
    PlatformActivity.objects.create(
        activity_type='tutor_application',
        message=f"Tutor application submitted: {request.user.userprofile.fname} {request.user.userprofile.lname}",
        institution=request.user.userprofile.institution
    )
    try:
        send_application_received_email(request.user.userprofile)
    except Exception:
        logger.exception(
            "Failed to send tutor application received email for profile_id=%s",
            request.user.userprofile.id,
        )
    return Response({"message": "Application submitted successfully. It is now under review."})
```

The existing pending/approved/rejected branches below stay as-is (they only run when `created` is
`False`).

### `tutor_application_status` (`views.py`)

No change — a 404 for "no application yet" is already the correct response; the frontend already
treats a tutee 404 as "not submitted yet, not an error" and will do the same for tutors.

## Frontend changes

### `src/services/tutorApplicationState.js`

- Delete `needsTutorApplicationLockout` (no longer used).
- Add `needsTutorVerificationBlock`, mirroring `needsTuteeVerificationBlock` minus the
  enforcement-flag check (tutors have never had a grace period):

```js
// Tutor-side action gate, mirroring needsTuteeVerificationBlock. Unlike tutees, tutors have no
// grace-period flag — can_create_new_booking has never given them one, so this doesn't either.
export const needsTutorVerificationBlock = (snapshot) => {
  return !(
    snapshot?.application_status === 'approved' &&
    snapshot?.document_renewal_status === 'verified'
  )
}
```

### `src/router/index.js`

Remove the `hasTutorApplicationLockout` block entirely (the `needsTutorApplicationLockout` import
and the `if (hasTutorApplicationLockout && ...) return '/application-status'` check). Tutors are
governed by the same router rules as tutees from here on: authentication, profile-completion
(`/tutor-setup`), and role protection. Nothing else routes through `/application-status`
automatically.

### `src/components/VerificationBanner.vue`

Replace `showTutorBanner`'s renewal-only condition with `needsTutorVerificationBlock`, and branch
the copy on whether the tutor has ever submitted (`profileStore.applicationStatus === null`) vs.
renewal-due, mirroring the two-state distinction tutees already show:

```js
const showTutorBanner = computed(() =>
  profileStore.loaded &&
  normalizedUserRole.value === 'tutor' &&
  needsTutorVerificationBlock({
    application_status: profileStore.applicationStatus,
    document_renewal_status: profileStore.renewalStatus,
  })
)
```

```js
if (showTutorBanner.value) {
  const isRenewal = profileStore.applicationStatus === 'approved'
  return {
    tone: 'tutor',
    icon: isRenewal ? 'bi bi-arrow-repeat' : 'bi bi-shield-exclamation',
    eyebrow: isRenewal ? 'Renewal required' : 'Verification required',
    title: isRenewal
      ? 'Renew your verification before you accept new sessions.'
      : 'Verify your enrollment before you accept sessions.',
    text: isRenewal
      ? 'Your dashboard stays available, but session acceptance is locked until your renewal is approved.'
      : 'You can keep setting up your profile and availability, but accepting sessions stays locked until you\'re verified.',
    cta: isRenewal ? 'Renew Now' : 'Verify Now',
  }
}
```

### `src/views/TutorApplicationStatus.vue`

Generalize `showInitialTuteeSubmission` → `showInitialSubmission`, dropping the `isTutee.value &&`
restriction so a tutor with no application also lands on the upload form instead of "No application
found. Please register first.":

```js
const showInitialSubmission = computed(
  () => !loading.value && !error.value && !application.value
)
```

Adjust the two copy strings that currently hardcode "booking" language
(`pageTitle`/`statusSubtitle`/the form's intro paragraph) to be role-neutral ("get verified" instead
of "before you book your first session"), since the same branch now serves both roles.

### `src/views/Register.vue`

Remove `TutorScreeningModal` usage entirely. `handleRegister` calls `submitRegistration()` directly
regardless of role (no `showScreeningModal` branch). `buildRegistrationPayload` drops the
`FormData`/file-upload branch for `role === 'Tutor'` — tutor registration becomes a plain JSON POST
identical in shape to tutee's. The post-submit redirect drops the
`role === 'Tutor' ? 'tutor-application-submitted' : 'login'` branch — both roles go to
`{ name: 'login', query: { registered: 'success', email } }`.

### Deletions

- `src/components/TutorScreeningModal.vue`
- `src/views/TutorApplicationSubmitted.vue`
- Its route in `src/router/index.js` (`/tutor-application-submitted`)

### Unchanged (already correct)

- `src/views/TutorProfile.vue` already renders `<VerificationStatusCard />` +
  `<VerificationDevPanel v-if="isDev" role="tutor" />` — no change needed.
- `src/views/TutorPreferenceSetup.vue` (the `/tutor-setup` teaching-level/rate form) is unrelated to
  verification and stays as-is.
- `approve_booking`'s `can_create_new_booking` check is unchanged.

## User-facing flow after this change

1. Tutor registers with the same fields as a tutee (no file upload, no modal).
2. Logs in, lands on `/tutor-setup` (profile completion, unrelated to verification), then the
   dashboard — full access, same as a tutee.
3. `VerificationStatusCard` on their profile and the dashboard banner both nudge them to verify.
4. They submit documents via `/application-status` whenever they choose.
5. The only thing actually blocked before approval: accepting a booking request
   (`approve_booking` → 403 `verification_required`, already implemented).

## Testing

- `backend/studybuddy/tests.py`: update/add tests for `register_user` (Tutor registration no longer
  requires/accepts files, no `TutorApplication` created), `tutor_application_resubmit` (creates on
  first call, same as the existing `tutee_application_resubmit` tests), and remove tests asserting
  the old "must provide School ID" 400 response.
- Existing `BookingVerificationGateTests` (`approve_booking` gate) should need no changes — it
  already exercises the case of a tutor without an approved application.
- Frontend: no dedicated test suite beyond `npm run lint` / `npm run build`; manually verify the
  registration → dashboard → `/application-status` → banner flow in the browser per this project's
  UI verification convention.
