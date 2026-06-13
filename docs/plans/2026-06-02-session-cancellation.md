# Phase B — Session Cancellation (Both Roles) — Implementation Plan

> **For agentic workers:** Use superpowers:subagent-driven-development to execute task-by-task.

**Goal:** Both tutee and tutor can cancel Pending or Confirmed-upcoming sessions,
with a required reason and a "not today or tomorrow" cutoff; no payment is touched.
**Stack:** Vue 3, Pinia, Django REST, Bootstrap 5
**Spec:** `docs/specs/2026-06-02-session-cancellation-design.md`

> Execute in order. Tasks 1-3 (backend) must land before Tasks 4-7 (frontend),
> since the frontend depends on the extended endpoint and stored fields.

---

### Task 1: Add cancellation fields to Booking + migration

**Files:**
- Modify: `backend/studybuddy/models.py` (class `Booking`, after the `status` field ~line 435)
- Create: a new migration (generated)

- [ ] Step 1: Add two fields to `Booking` immediately after the `status` field:

  ```python
  cancellation_reason = models.TextField(blank=True, default='')
  cancelled_by_role = models.CharField(
      max_length=10,
      blank=True,
      default='',
      choices=[('tutee', 'Tutee'), ('tutor', 'Tutor')],
  )
  ```

- [ ] Step 2: From `backend/`, run `python manage.py makemigrations studybuddy`.
- [ ] Step 3: Run `python manage.py migrate` and `python manage.py check` — both pass.
- [ ] Step 4: Commit — `git commit -m "feat(booking): add cancellation_reason and cancelled_by_role fields"`

---

### Task 2: Carry reason + actor into the cancellation notification

**Files:**
- Modify: `backend/studybuddy/views.py` — `create_booking_status_notification` (~line 314)

- [ ] Step 1: Change the signature to accept two optional kwargs:

  ```python
  def create_booking_status_notification(recipient, status_key, bookings, recipient_role=None, actor_role=None, reason=None):
  ```

- [ ] Step 2: Replace the `if status_key == "cancelled":` block with actor-aware
  wording that also appends the reason:

  ```python
  if status_key == "cancelled":
      actor = actor_role or "tutee"
      if recipient_role == "tutor":
          if actor == "tutor":
              message = f"You cancelled your {context['subject']} session on {context['date']}."
          else:
              message = f"{context['tutee_name']} has cancelled your {context['subject']} session on {context['date']}."
      elif recipient_role == "tutee":
          if actor == "tutor":
              message = f"Your {context['subject']} session on {context['date']} was cancelled by {context['tutor_name']}."
          else:
              message = f"Your {context['subject']} session on {context['date']} has been successfully cancelled."
      else:
          message = None

      if message and reason:
          message = f"{message} Reason: {reason}"
  else:
      message = messages.get(status_key)
  ```

  (Existing non-cancel callers are unaffected — the new kwargs default to `None`.)

- [ ] Step 3: Verify — `python manage.py check` passes.
- [ ] Step 4: Commit — `git commit -m "feat(notifications): include canceller and reason in cancellation messages"`

---

### Task 3: Extend `cancel_booking` — both roles, pending + upcoming, cutoff, required reason

**Files:**
- Modify: `backend/studybuddy/views.py` — `cancel_booking` (~line 1812-1878)

- [ ] Step 1: Replace the entire `cancel_booking` function body with:

  ```python
  @api_view(['POST'])
  @permission_classes([IsAuthenticated])
  def cancel_booking(request, booking_id):

      profile = request.user.userprofile
      booking = get_object_or_404(
          Booking.objects.select_related(
              'student__course',
              'student__user',
              'tutor__profile__course',
              'tutor__profile__user',
              'availability'
          ),
          id=booking_id
      )

      # Either party may cancel.
      is_student = profile == booking.student
      is_tutor = profile == booking.tutor.profile
      if not (is_student or is_tutor):
          return Response({"error": "Unauthorized"}, status=403)

      actor_role = "tutee" if is_student else "tutor"

      # Reason is required.
      reason = str(request.data.get("reason", "")).strip()
      if len(reason) < 5:
          return Response(
              {"error": "Please provide a reason for cancelling (at least 5 characters)."},
              status=400
          )

      # Group lookup mirrors approve/reject.
      if booking.status == "Pending":
          session_group_bookings = get_booking_request_bookings(booking)
      else:
          session_group_bookings = get_session_group_bookings(booking)

      representative_booking = get_representative_booking(session_group_bookings)
      if not representative_booking:
          return Response({"error": "Booking not found."}, status=404)

      first_booking = session_group_bookings[0]
      last_booking = session_group_bookings[-1]
      start_time = first_booking.availability.time_slot
      end_time = (
          datetime.combine(first_booking.session_date, last_booking.availability.time_slot)
          + timedelta(minutes=SESSION_SLOT_MINUTES)
      ).time()

      raw_status = representative_booking.status
      display_status = get_display_status(
          raw_status,
          representative_booking.session_date,
          start_time,
          end_time
      )

      # Allowed: pending requests (withdraw) or confirmed-upcoming sessions.
      if raw_status != "Pending" and display_status != "Upcoming":
          return Response(
              {"error": "Only pending requests or upcoming sessions can be cancelled."},
              status=400
          )

      # Cutoff: cannot cancel the day of or the day before the session.
      if representative_booking.session_date <= timezone.localdate() + timedelta(days=1):
          return Response(
              {"error": "Sessions can only be cancelled at least two days before the session date."},
              status=400
          )

      with transaction.atomic():
          Booking.objects.filter(
              id__in=[group_booking.id for group_booking in session_group_bookings]
          ).update(
              status="Cancelled",
              tutee_confirmed=False,
              tutor_confirmed=False,
              cancellation_reason=reason,
              cancelled_by_role=actor_role,
          )

          create_booking_status_notification(
              representative_booking.tutor.profile,
              "cancelled",
              session_group_bookings,
              recipient_role="tutor",
              actor_role=actor_role,
              reason=reason,
          )
          create_booking_status_notification(
              representative_booking.student,
              "cancelled",
              session_group_bookings,
              recipient_role="tutee",
              actor_role=actor_role,
              reason=reason,
          )

          representative_booking.refresh_from_db()
          create_booking_event(
              representative_booking,
              request.user,
              f"Session cancelled by {actor_role}. Reason: {reason}",
              "booking_cancelled",
          )

      return Response({"message": "Session cancelled successfully."}, status=200)
  ```

- [ ] Step 2: Confirm imports already present in `views.py`: `datetime`, `timedelta`,
  `timezone`, `transaction`, `get_session_group_bookings`, `get_booking_request_bookings`,
  `get_representative_booking`, `get_display_status`, `create_booking_event`,
  `SESSION_SLOT_MINUTES`. (All are already used in this file — no new imports.)
- [ ] Step 3: Verify — `python manage.py check` passes.
- [ ] Step 4: Commit — `git commit -m "feat(cancel): allow tutor + tutee to cancel pending/upcoming with required reason and 2-day cutoff"`

---

### Task 4: Tutee store — send reason to the endpoint

**Files:**
- Modify: `src/stores/completedSessions.js` (`cancelSession`, ~line 167)

- [ ] Step 1: Change `cancelSession` to accept and send a reason:

  ```js
  const cancelSession = async (id, reason) => {
    await api.post(`/bookings/${id}/cancel/`, { reason })
    await fetchSessions()
    return fetchSessionById(id)
  }
  ```

- [ ] Step 2: Verify — `npm run build` succeeds.
- [ ] Step 3: Commit — `git commit -m "feat(sessions-store): pass cancellation reason to cancel endpoint"`

---

### Task 5: Tutee UI — cancel pending too, tighten cutoff, required reason + chat nudge

**Files:**
- Modify: `src/views/TuteeSessionDetailsFlow.vue` (script ~line 256-279, modal ~line 177-228, handler ~line 389)

- [ ] Step 1: Add `isPending`, `tomorrowKey`, a reason ref, and update the gating
  computeds. Near the existing status computeds (after `isUpcoming`, ~line 260):

  ```js
  const isPending = computed(() => normalizedStatus.value === 'pending')
  const cancelReason = ref('')
  const reasonValid = computed(() => cancelReason.value.trim().length >= 5)
  const tomorrowKey = computed(() => {
    const d = new Date()
    d.setDate(d.getDate() + 1)
    const year = d.getFullYear()
    const month = String(d.getMonth() + 1).padStart(2, '0')
    const day = String(d.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
  })
  ```

- [ ] Step 2: Replace `showCancelAction`, `canCancelSession`, and `cancelActionMessage`:

  ```js
  const showCancelAction = computed(() => isUpcoming.value || isPending.value)
  const canCancelSession = computed(() => (
    (isUpcoming.value || isPending.value)
    && String(sessionDetail.value?.session?.date || '') > tomorrowKey.value
  ))
  const cancelActionMessage = computed(() => {
    if (canCancelSession.value) {
      return isPending.value
        ? 'You can withdraw this pending request before it is confirmed.'
        : 'This upcoming session can still be cancelled.'
    }
    return 'Sessions can only be cancelled at least two days before the session date.'
  })
  ```

- [ ] Step 3: In the cancel modal body (~line 197-199), replace the static paragraph
  with a required reason field and a chat nudge:

  ```html
  <div class="modal-body">
    <p class="mb-2">Are you sure you want to cancel this session?</p>
    <label class="form-label fw-semibold small">Reason (required)</label>
    <textarea
      v-model="cancelReason"
      class="form-control border-sb shadow-none"
      rows="3"
      placeholder="Let your tutor know why you're cancelling..."
      :disabled="isCancelling"
    ></textarea>
    <p class="small text-muted mt-2 mb-0">
      Please also
      <a href="#" @click.prevent="goToChat">message your tutor in Chat</a>
      to coordinate.
    </p>
  </div>
  ```

- [ ] Step 4: Disable the confirm button until the reason is valid (~line 210-214):

  ```html
  <button
    type="button"
    class="btn btn-danger sb-btn"
    :disabled="isCancelling || !reasonValid"
    @click="handleCancelSession"
  >
  ```

- [ ] Step 5: Add a `goToChat` method, pass the reason on cancel, and clear the reason
  when the modal closes. Update `handleCancelSession` and `closeCancelModal`:

  ```js
  const goToChat = () => {
    router.push({ name: 'chat' })
  }
  ```

  In `handleCancelSession`, change the guard and the call:
  ```js
  const handleCancelSession = async () => {
    if (!canCancelSession.value || !reasonValid.value) {
      return
    }
    isCancelling.value = true
    try {
      const updatedDetail = await sessionsStore.cancelSession(route.params.id, cancelReason.value.trim())
      sessionDetail.value = updatedDetail
      isCancelModalOpen.value = false
      cancelReason.value = ''
      await notificationsStore.fetchNotifications()
      toastStore.push('Session cancelled successfully.')
    } catch (error) {
      toastStore.push(error.response?.data?.error || 'Failed to cancel session.', 'error')
    } finally {
      isCancelling.value = false
    }
  }
  ```

  In `closeCancelModal`, also reset the reason:
  ```js
  const closeCancelModal = () => {
    if (isCancelling.value) {
      return
    }
    cancelReason.value = ''
    isCancelModalOpen.value = false
  }
  ```

- [ ] Step 6: Verify — `npm run build` succeeds. With a seeded DB: open a Pending
  session detail (date ≥ 2 days out) → Cancel button shows, confirm disabled until a
  reason is typed, cancellation succeeds, status flips to Cancelled. Repeat for a
  Confirmed-upcoming session. Confirm a session dated today/tomorrow shows the cutoff
  message and the button is disabled.
- [ ] Step 7: Commit — `git commit -m "feat(tutee-cancel): pending withdraw, 2-day cutoff, required reason + chat nudge"`

---

### Task 6: Tutor store — add a cancel action

**Files:**
- Modify: `src/stores/tutorBookingDetails.js`

- [ ] Step 1: Add a `cancelBooking` action that posts to the shared endpoint and
  refreshes the loaded booking. Mirror the existing `confirmCompletion` pattern
  (it already holds the current booking id from `fetchBookingDetails`). Example:

  ```js
  const cancelBooking = async (reason) => {
    await api.post(`/bookings/${booking.value.id}/cancel/`, { reason })
    await fetchBookingDetails(booking.value.id)
  }
  ```

  (Use whatever the store already uses to reference the current booking id and to
  reload — match the existing `confirmCompletion` / `devMarkReadyForPayment`
  implementations in this file. Export `cancelBooking` from the store's return.)

- [ ] Step 2: Verify — `npm run build` succeeds.
- [ ] Step 3: Commit — `git commit -m "feat(tutor-booking-store): add cancelBooking action"`

---

### Task 7: Tutor UI — cancel a confirmed-upcoming session

**Files:**
- Modify: `src/views/TutorBookingDetailsFlow.vue`

- [ ] Step 1: Add state near the other refs (~line 193): `isCancelling`,
  `isCancelModalOpen`, `cancelReason`, and a `reasonValid` computed
  (`cancelReason.value.trim().length >= 5`). Import `useRouter` and create `router`.

- [ ] Step 2: Add a computed gate for showing the cancel button — confirmed-upcoming
  only, with the same cutoff (not today or tomorrow):

  ```js
  const tomorrowKey = computed(() => {
    const d = new Date()
    d.setDate(d.getDate() + 1)
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
  })
  const canCancel = computed(() =>
    normalizedStatus.value === 'upcoming'
    && String(bookingDetailsStore.sessionInfo?.date || '') > tomorrowKey.value,
  )
  const showCancelButton = computed(() => normalizedStatus.value === 'upcoming')
  ```

- [ ] Step 3: In the right-hand action card (after the "Mark as Complete" button,
  ~line 175), add the cancel trigger:

  ```html
  <button
    v-if="showCancelButton"
    class="btn btn-outline-danger mt-3 sb-btn"
    :disabled="isCancelling || !canCancel"
    @click="isCancelModalOpen = true"
  >
    {{ isCancelling ? 'Cancelling...' : 'Cancel Session' }}
  </button>
  <p v-if="showCancelButton && !canCancel" class="small text-muted mt-2 mb-0">
    Sessions can only be cancelled at least two days before the session date.
  </p>
  ```

- [ ] Step 4: Add a cancel modal (reuse the Bootstrap modal markup from
  `TuteeSessionDetailsFlow.vue` Task 5, Steps 3-4 — same structure) bound to
  `isCancelModalOpen` / `cancelReason`, with the chat nudge wording "message your
  tutee in Chat" and `goToChat` → `router.push({ name: 'chat' })`.

- [ ] Step 5: Add the handler:

  ```js
  const handleCancel = async () => {
    if (!canCancel.value || !reasonValid.value) {
      return
    }
    isCancelling.value = true
    try {
      await bookingDetailsStore.cancelBooking(cancelReason.value.trim())
      await notificationsStore.fetchNotifications()
      isCancelModalOpen.value = false
      cancelReason.value = ''
      toastStore.push('Session cancelled. Your tutee has been notified.')
    } catch (error) {
      toastStore.push(error.response?.data?.error || 'Failed to cancel session.', 'error')
    } finally {
      isCancelling.value = false
    }
  }
  ```

- [ ] Step 6: Verify — `npm run build` succeeds. As a tutor, open a confirmed-upcoming
  booking (date ≥ 2 days out) → Cancel Session → reason required → succeeds → the
  tutee receives a notification naming the tutor + reason.
- [ ] Step 7: Commit — `git commit -m "feat(tutor-cancel): cancel confirmed-upcoming session with required reason"`

---

### Task 8: End-to-end verification and completion report

**Files:**
- Create: `docs/session-summaries/2026-06-02-phaseB-session-cancellation-completion.md`

- [ ] Step 1: Run all spec success criteria against the running app
  (backend + `npm run dev`, seeded DB):
  1. Tutee withdraws a Pending request (≥2 days out) with a reason → tutor notified.
  2. Tutee cancels a Confirmed-upcoming session with a reason.
  3. Tutor cancels a Confirmed-upcoming session → tutee notified with tutor name + reason.
  4. Today/tomorrow sessions are blocked with the cutoff message.
  5. Empty/short reason is rejected client- and server-side.
  6. No `Payment` rows change on cancel.
- [ ] Step 2: Confirm `python manage.py check`, the migration, and `npm run build` all pass.
- [ ] Step 3: Write the completion report (template below) with the verification
  evidence (screenshots / notification text / network responses) and any deviations.
- [ ] Step 4: Commit — `git commit -m "docs: Phase B session-cancellation completion report"`

---

## Completion report template

```markdown
# Phase B Completion Report — Session Cancellation (Both Roles)
**Date completed:** <YYYY-MM-DD>
**Branch:** <branch>
**Plan:** docs/plans/2026-06-02-session-cancellation.md

## Summary
<what shipped: both roles can cancel pending/upcoming with reason + cutoff>

## Changes
| File | Change |
|---|---|
| backend/studybuddy/models.py | cancellation_reason, cancelled_by_role + migration |
| backend/studybuddy/views.py | cancel_booking rewrite; notification reason/actor |
| src/stores/completedSessions.js | cancelSession(id, reason) |
| src/views/TuteeSessionDetailsFlow.vue | pending cancel, cutoff, required reason, chat link |
| src/stores/tutorBookingDetails.js | cancelBooking(reason) |
| src/views/TutorBookingDetailsFlow.vue | tutor cancel button + modal |

## Verification (spec success criteria)
- [ ] 1 Tutee withdraws Pending (notified tutor)
- [ ] 2 Tutee cancels Confirmed-upcoming
- [ ] 3 Tutor cancels Confirmed-upcoming (tutee notified w/ name + reason)
- [ ] 4 Today/tomorrow blocked with cutoff message
- [ ] 5 Empty/short reason rejected (client + server)
- [ ] 6 No Payment rows altered
- [ ] makemigrations/migrate + manage.py check + npm run build pass

## Deviations
<none, or list — e.g. tutor Pending handled by existing Reject, per design note>
```
