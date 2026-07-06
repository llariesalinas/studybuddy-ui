<template>
  <div class="booking-details session-details-page container py-2">
    <div v-if="bookingDetailsStore.isLoading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status"></div>
    </div>

    <div v-else-if="!bookingDetailsStore.booking">
      <div class="alert alert-warning">Booking not found.</div>
    </div>

    <section v-else class="session-alive-frame">
      <div v-if="showConfetti" class="session-confetti" aria-hidden="true">
        <i
          v-for="piece in confettiPieces"
          :key="piece"
          :style="{
            '--session-confetti-index': piece,
            '--session-confetti-x': `${(piece % 11) - 5}`,
            '--session-confetti-color': confettiColors[piece % confettiColors.length],
          }"
        ></i>
      </div>
      <SessionAurora />

      <div class="session-alive-stage">
        <div class="session-alive-grid">
          <div class="session-alive-column">
            <div class="session-anchor">
              <SessionHero
                :profile="counterpartProfile"
                :subject="bookingDetailsStore.sessionInfo?.subject"
                :status="normalizedStatus"
                :status-label="bookingDetailsStore.sessionInfo?.status || 'Session'"
                :is-ongoing="isOngoing"
                :clock="heroClock"
              />

              <SessionCountdownBar
                v-if="showDetailOrbit"
                :presentation="detailOrbitPresentation"
              />
            </div>

            <section v-if="isOngoing" class="session-progress-card glass-segment">
              <div class="session-progress-head">
                <div>
                  <h4>Tutee progress pulse</h4>
                  <p>Use this to check whether the learner is making progress while the session is still active.</p>
                </div>
                <span class="session-progress-chip">{{ heroClock.formattedElapsed }} elapsed</span>
              </div>

              <template v-if="midpointCheckIn">
                <div class="session-progress-status" :class="`is-${midpointCheckIn.response || 'saved'}`">
                  <strong>{{ midpointStatusTitle }}</strong>
                  <span>{{ midpointStatusCopy }}</span>
                </div>
              </template>

              <template v-else>
                <button class="session-progress-button session-progress-button-good sb-btn" @click="handleTutorCheckInPrompt">
                  <strong>Prompt progress check</strong>
                  <span>Ask the tutee to answer the mid-session popup from their live session screen.</span>
                </button>
              </template>
            </section>

            <section v-if="isOngoing" class="session-action-card glass-segment">
              <h4>Quick actions</h4>
              <div class="session-quick-grid">
                <button class="session-quick-button sb-btn" @click="handleTutorCheckInPrompt">
                  <i class="bi bi-geo-alt"></i>
                  Confirm venue
                </button>
                <button class="session-quick-button sb-btn" @click="handleLightAction(goToChat)">
                  <i class="bi bi-chat-dots"></i>
                  Message
                </button>
                <button class="session-quick-button sb-btn" @click="handleTutorCheckInPrompt">
                  <i class="bi bi-activity"></i>
                  Progress check
                </button>
                <button
                  class="session-quick-button sb-btn"
                  :disabled="!showDevReadyForPayment || isDevSubmitting"
                  @click="handleMediumAction(handleDevReadyForPayment)"
                >
                  <i class="bi bi-stop-circle"></i>
                  End
                </button>
              </div>
            </section>

            <div class="session-detail-pair">
              <SessionInfoGrid class="glass-segment" :items="sessionInfoItems" />

              <SessionTimeline
                v-if="!showDetailOrbit"
                class="glass-segment"
                :status="normalizedStatus"
                :is-ongoing="isOngoing"
                :date-label="formattedSessionDate"
                :time-label="formattedTimeRange"
                :live-caption="`${heroClock.formattedElapsed} elapsed`"
              />
            </div>
          </div>

          <div class="session-alive-column session-alive-rail">
            <section class="session-action-card session-next-action glass-segment">
              <div class="session-action-head">
                <h4>{{ actionTitle }}</h4>
                <span v-if="isOngoing" class="session-live-pill">
                  <span></span>
                  Live
                </span>
              </div>

              <template v-if="isOngoing">
                <p>Session is live. Keep your tutee in sync, then end the session when it is ready for payment.</p>
                <button
                  class="session-cta sb-btn btn-primary-action sb-elevated sb-elevated--brand"
                  @click="handleLightAction(goToChat)"
                >
                  <i class="bi bi-chat-dots"></i>
                  Open chat
                </button>
                <button
                  class="session-cta sb-btn btn-soft"
                  :disabled="!showDevReadyForPayment || isDevSubmitting"
                  @click="handleMediumAction(handleDevReadyForPayment)"
                >
                  <i class="bi bi-stop-circle"></i>
                  {{ isDevSubmitting ? 'Updating...' : 'End session now' }}
                </button>
                <p v-if="!showDevReadyForPayment" class="session-note">
                  Ending from this screen is available when the booking is confirmed and ready for the existing payment handoff.
                </p>
              </template>

              <template v-else-if="isAwaitingVerification">
                <p>The tutoring session has ended and the tutee has submitted payment for review.</p>
                <div class="summary-row">
                  <span class="summary-label">Amount paid</span>
                  <span class="summary-value">PHP {{ amountPaid }}</span>
                </div>
                <div class="summary-row">
                  <span class="summary-label">Method</span>
                  <span class="summary-value">{{ bookingDetailsStore.paymentInfo?.method || 'N/A' }}</span>
                </div>
                <div class="summary-row">
                  <span class="summary-label">Status</span>
                  <span class="summary-value">{{ bookingDetailsStore.paymentInfo?.status || 'Submitted' }}</span>
                </div>
                <button
                  class="session-cta sb-btn btn-primary-action sb-elevated sb-elevated--brand"
                  :disabled="isSubmitting"
                  @click="handleCelebrationAction(handleComplete)"
                >
                  <i class="bi bi-check2-circle"></i>
                  {{ isSubmitting ? 'Updating...' : 'Mark as Complete' }}
                </button>
              </template>

              <template v-else-if="showDevReadyForPayment">
                <p>Dev option: end this session now so the tutee can open the post-session payment flow.</p>
                <button
                  class="session-cta sb-btn btn-soft"
                  :disabled="isDevSubmitting"
                  @click="handleMediumAction(handleDevReadyForPayment)"
                >
                  {{ isDevSubmitting ? 'Updating...' : 'Dev: End Session Now' }}
                </button>
              </template>

              <template v-else-if="showCancelButton">
                <p>Confirmed. Coordinate with your tutee or cancel 2+ days ahead.</p>
                <button
                  class="session-cta sb-btn btn-primary-action sb-elevated sb-elevated--brand"
                  @click="handleLightAction(goToChat)"
                >
                  <i class="bi bi-chat-dots"></i>
                  Message tutee
                </button>
                <button
                  class="session-cta sb-btn btn-danger-soft"
                  :disabled="isCancelling || !canCancel"
                  @click="handleLightAction(() => { isCancelModalOpen = true })"
                >
                  {{ isCancelling ? 'Cancelling...' : 'Cancel Session' }}
                </button>
                <p v-if="!canCancel" class="session-note">
                  Sessions can only be cancelled at least two days before the session date.
                </p>
              </template>

              <template v-else>
                <div class="summary-row">
                  <span class="summary-label">Transaction ID</span>
                  <span class="summary-value">{{ bookingDetailsStore.paymentInfo?.transaction_id || 'N/A' }}</span>
                </div>
                <div class="summary-row">
                  <span class="summary-label">Payment</span>
                  <span class="summary-value">{{ bookingDetailsStore.paymentInfo?.status || 'Pending' }}</span>
                </div>
                <div class="summary-row">
                  <span class="summary-label">Amount paid</span>
                  <span class="summary-value">PHP {{ amountPaid }}</span>
                </div>
              </template>
            </section>

            <section v-if="bookingDetailsStore.paymentInfo?.receipt_image" class="session-action-card glass-segment">
              <h4>Receipt image</h4>
              <img
                :src="bookingDetailsStore.paymentInfo.receipt_image"
                alt="Payment Receipt"
                class="receipt-image"
              />
            </section>

            <section v-if="hasCheckInResponses" class="session-action-card glass-segment">
              <h4>Session check-ins</h4>

              <div v-if="venueCheckIn" class="check-in-row">
                <span class="summary-label">Venue confirmation</span>
                <span class="summary-value">{{ formatCheckInResponse(venueCheckIn.response) }}</span>
                <span class="check-in-time">{{ formatCheckInTime(venueCheckIn.responded_at) }}</span>
              </div>

              <div v-if="midpointCheckIn" class="check-in-row">
                <span class="summary-label">Mid-session check-in</span>
                <span class="summary-value">{{ formatCheckInResponse(midpointCheckIn.response) }}</span>
                <span class="check-in-time">{{ formatCheckInTime(midpointCheckIn.responded_at) }}</span>
              </div>
            </section>

            <section class="session-action-card glass-segment">
              <h4>Support</h4>
              <p>Something off with this session?</p>
              <button
                class="session-cta sb-btn btn-danger-soft"
                @click="handleLightAction(() => openSupport('Booking', bookingDetailsStore.booking?.id))"
              >
                <i class="bi bi-exclamation-circle"></i>
                Report issue
              </button>
            </section>

          </div>
        </div>
      </div>
    </section>

    <DevSessionQaPanel
      v-if="bookingDetailsStore.booking"
      class="mt-3"
      :booking-id="bookingDetailsStore.booking?.id"
      :session-mode="bookingDetailsStore.sessionInfo?.session_mode"
      :location="sessionLocationValue"
      @refresh="refreshBookingDetails"
    />

    <div
      v-if="isCancelModalOpen"
      class="modal fade show d-block"
      tabindex="-1"
      role="dialog"
      aria-modal="true"
    >
      <div class="modal-dialog modal-dialog-centered" role="document">
        <div class="modal-content border-0 shadow">
          <div class="modal-header">
            <h5 class="modal-title fw-bold">Cancel Session</h5>
            <button
              type="button"
              class="btn-close"
              aria-label="Close"
              :disabled="isCancelling"
              @click="closeCancelModal"
            ></button>
          </div>

          <div class="modal-body">
            <p class="mb-2">Are you sure you want to cancel this session?</p>
            <label class="form-label fw-semibold small">Reason (required)</label>
            <textarea
              v-model="cancelReason"
              class="form-control shadow-none sb-field"
              rows="3"
              placeholder="Let your tutee know why you're cancelling..."
              :disabled="isCancelling"
            ></textarea>
            <p class="small text-muted mt-2 mb-0">
              Please also
              <a href="#" @click.prevent="goToChat">message your tutee in Chat</a>
              to coordinate.
            </p>
          </div>

          <div class="modal-footer">
            <button
              type="button"
              class="btn btn-outline-secondary sb-btn"
              :disabled="isCancelling"
              @click="closeCancelModal"
            >
              Keep Session
            </button>
            <button
              type="button"
              class="btn btn-danger sb-btn"
              :disabled="isCancelling || !reasonValid"
              @click="handleCancel"
            >
              <span
                v-if="isCancelling"
                class="spinner-border spinner-border-sm me-2"
                role="status"
                aria-hidden="true"
              ></span>
              {{ isCancelling ? 'Cancelling...' : 'Yes, Cancel Session' }}
            </button>
          </div>
        </div>
      </div>
    </div>
    <div v-if="isCancelModalOpen" class="modal-backdrop fade show"></div>
    <SupportModal
      :open="isSupportModalOpen"
      :context-type="supportContextType"
      :context-id="supportContextId"
      @close="isSupportModalOpen = false"
    />
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useNotificationsStore } from '@/stores/notifications'
import { useTutorBookingDetailStore } from '@/stores/tutorBookingDetails'
import { useToastStore } from '@/stores/toast'
import { useHaptics } from '@/composables/useHaptics'
import { useOrbitStrip } from '@/composables/useOrbitStrip'
import { useSessionClock } from '@/composables/useSessionClock'
import { BOOKING_DEV_TOOLS_ENABLED } from '@/config.js'
import DevSessionQaPanel from '@/components/DevSessionQaPanel.vue'
import SupportModal from '@/components/SupportModal.vue'
import SessionCountdownBar from '@/components/session/SessionCountdownBar.vue'
import SessionAurora from '@/components/session/SessionAurora.vue'
import SessionHero from '@/components/session/SessionHero.vue'
import SessionInfoGrid from '@/components/session/SessionInfoGrid.vue'
import SessionTimeline from '@/components/session/SessionTimeline.vue'

const route = useRoute()
const router = useRouter()
const bookingDetailsStore = useTutorBookingDetailStore()
const notificationsStore = useNotificationsStore()
const toastStore = useToastStore()
const { vibrate, patterns } = useHaptics()
const isSubmitting = ref(false)
const isDevSubmitting = ref(false)
const isCancelling = ref(false)
const isCancelModalOpen = ref(false)
const isSupportModalOpen = ref(false)
const supportContextType = ref('Booking')
const supportContextId = ref(null)
const cancelReason = ref('')
const showConfetti = ref(false)
const isDev = import.meta.env.DEV || BOOKING_DEV_TOOLS_ENABLED

const confettiPieces = Array.from({ length: 26 }, (_, index) => index)
const confettiColors = [
  'var(--sb-primary)',
  'var(--sb-primary-mid)',
  'var(--sb-pop-yellow)',
  'var(--sb-pop-pink)',
  'var(--sb-pop-orange)',
  'var(--sb-aurora-violet)',
]

const normalizedStatus = computed(() =>
  String(bookingDetailsStore.sessionInfo?.status || '').toLowerCase(),
)
const normalizedRawStatus = computed(() =>
  String(bookingDetailsStore.sessionInfo?.raw_status || '').toLowerCase(),
)
const statusOngoing = computed(() => normalizedStatus.value === 'ongoing')
const isAwaitingVerification = computed(() => normalizedStatus.value === 'awaiting verification')
const isCompleted = computed(() => normalizedStatus.value === 'completed')
const showDevReadyForPayment = computed(
  () =>
    isDev &&
    normalizedRawStatus.value === 'confirmed' &&
    !bookingDetailsStore.booking?.tutor_confirmed,
)

const reasonValid = computed(() => cancelReason.value.trim().length >= 5)
const tomorrowKey = computed(() => {
  const d = new Date()
  d.setDate(d.getDate() + 1)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
})
const showCancelButton = computed(() => normalizedStatus.value === 'upcoming')
const canCancel = computed(
  () =>
    normalizedStatus.value === 'upcoming' &&
    String(bookingDetailsStore.sessionInfo?.date || '') > tomorrowKey.value,
)

const amountPaid = computed(() => {
  const value = Number(bookingDetailsStore.paymentInfo?.amount_paid || 0)
  return value.toFixed(2)
})

const venueCheckIn = computed(() => bookingDetailsStore.booking?.check_ins?.venue_confirm || null)
const midpointCheckIn = computed(() => bookingDetailsStore.booking?.check_ins?.midpoint_checkin || null)
const hasCheckInResponses = computed(() => Boolean(venueCheckIn.value || midpointCheckIn.value))

const counterpartProfile = computed(() => ({
  avatar: bookingDetailsStore.tuteeProfile?.avatar || '',
  name: bookingDetailsStore.tuteeProfile?.name || 'Tutee',
  meta: [
    'Your tutee',
    bookingDetailsStore.tuteeProfile?.course,
    bookingDetailsStore.tuteeProfile?.year_level,
  ].filter(Boolean).join(' · '),
}))

const formatSessionDate = (dateValue) => {
  if (!dateValue) {
    return 'N/A'
  }

  return new Intl.DateTimeFormat(undefined, {
    dateStyle: 'medium',
    timeZone: 'Asia/Manila',
  }).format(new Date(`${String(dateValue).slice(0, 10)}T00:00:00+08:00`))
}

const formatTime = (value) => {
  if (!value) {
    return 'N/A'
  }

  const [hour, minute] = String(value).split(':').map(Number)
  const suffix = hour >= 12 ? 'PM' : 'AM'
  const displayHour = hour % 12 || 12
  return `${displayHour}:${String(minute).padStart(2, '0')} ${suffix}`
}

const formattedSessionDate = computed(() => formatSessionDate(bookingDetailsStore.sessionInfo?.date))
const formattedTimeRange = computed(() => {
  const start = bookingDetailsStore.sessionInfo?.start_time
  const end = bookingDetailsStore.sessionInfo?.end_time

  if (!start || !end) {
    return 'N/A'
  }

  return `${formatTime(start)} - ${formatTime(end)}`
})

const sessionModeLabel = computed(() => String(bookingDetailsStore.sessionInfo?.session_mode || ''))

const isOnlineSession = computed(() => sessionModeLabel.value.toLowerCase() === 'online')

const sessionLocationValue = computed(() => {
  if (isOnlineSession.value) {
    return 'Online'
  }

  return bookingDetailsStore.sessionInfo?.preferred_location || 'N/A'
})

const clock = useSessionClock({
  date: computed(() => bookingDetailsStore.sessionInfo?.date),
  startTime: computed(() => bookingDetailsStore.sessionInfo?.start_time),
  endTime: computed(() => bookingDetailsStore.sessionInfo?.end_time),
  isOngoing: statusOngoing,
})
const { presentation: detailOrbitPresentation, hasOrbit: showDetailOrbit } = useOrbitStrip({
  session: computed(() => bookingDetailsStore.booking),
  isTutor: true,
})

const isOngoing = computed(() => statusOngoing.value || clock.isLive.value)

const heroClock = computed(() => ({
  formattedElapsed: clock.formattedElapsed.value,
  progress: clock.progress.value,
  startedLabel: clock.startedLabel.value,
  endsLabel: clock.endsLabel.value,
  minutesLeft: clock.minutesLeft.value,
}))

const sessionInfoItems = computed(() => [
  { label: 'Subject', value: bookingDetailsStore.sessionInfo?.subject },
  { label: 'Date', value: formattedSessionDate.value },
  { label: 'Time', value: formattedTimeRange.value },
  { label: 'Mode', value: sessionModeLabel.value },
  ...(isOnlineSession.value ? [] : [{ label: 'Location', value: sessionLocationValue.value }]),
  { label: 'Status', value: bookingDetailsStore.sessionInfo?.status },
])

const midpointStatusTitle = computed(() => {
  if (midpointCheckIn.value?.response === 'issues') {
    return 'Tutee flagged an issue during the session'
  }

  return 'Tutee progress check received'
})

const midpointStatusCopy = computed(() => {
  if (midpointCheckIn.value?.response === 'issues') {
    return 'Open chat or support now so the problem can be resolved before the session ends.'
  }

  return 'The learner confirmed the session is going well.'
})

const actionTitle = computed(() => {
  if (isOngoing.value) return 'Happening now'
  if (isAwaitingVerification.value) return 'Verify payment'
  if (showDevReadyForPayment.value) return 'Next action'
  if (isCompleted.value) return 'Summary'
  return 'Payment summary'
})

const openSupport = (type = 'Booking', id = null) => {
  supportContextType.value = type
  supportContextId.value = id
  isSupportModalOpen.value = true
}

const prefersReducedMotion = () => (
  typeof window !== 'undefined'
  && window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
)

const fireConfetti = () => {
  if (prefersReducedMotion()) {
    return
  }

  showConfetti.value = false
  window.setTimeout(() => {
    showConfetti.value = true
    window.setTimeout(() => {
      showConfetti.value = false
    }, 1300)
  }, 0)
}

watch(isCompleted, (completed, wasCompleted) => {
  if (completed && !wasCompleted) {
    fireConfetti()
  }
})

watch(
  () => detailOrbitPresentation.value?.zone,
  (zone, previousZone) => {
    if (!zone || !previousZone || zone <= previousZone || !showDetailOrbit.value || prefersReducedMotion()) {
      return
    }

    vibrate(patterns.medium)
  },
)

const formatCheckInResponse = (response) => {
  const labels = {
    yes: 'Confirmed at venue',
    no: 'Not at venue',
    good: 'All good',
    issues: 'Having issues',
  }

  return labels[response] || 'Recorded'
}

const formatCheckInTime = (value) => {
  if (!value) {
    return ''
  }

  return new Intl.DateTimeFormat(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value))
}

const handleLightAction = (callback) => {
  vibrate(patterns.light)
  callback()
}

const handleMediumAction = (callback) => {
  vibrate(patterns.medium)
  callback()
}

const handleCelebrationAction = (callback) => {
  vibrate(patterns.celebratory)
  callback()
}

const handleTutorCheckInPrompt = () => {
  vibrate(patterns.light)
  toastStore.push('Ask your tutee to answer this check-in from their session screen.')
  goToChat()
}

const handleComplete = async () => {
  isSubmitting.value = true

  try {
    await bookingDetailsStore.confirmCompletion()
    await notificationsStore.fetchNotifications()
    toastStore.push('Session marked as completed.')
  } catch (error) {
    toastStore.push(error.response?.data?.error || 'Failed to complete session.', 'error')
  } finally {
    isSubmitting.value = false
  }
}

const handleDevReadyForPayment = async () => {
  if (!showDevReadyForPayment.value) {
    return
  }

  isDevSubmitting.value = true

  try {
    await bookingDetailsStore.devMarkReadyForPayment()
    await notificationsStore.fetchNotifications()
    toastStore.push('Dev: session is ready for tutee payment.')
  } catch (error) {
    toastStore.push(error.response?.data?.error || 'Failed to make session ready for payment.', 'error')
  } finally {
    isDevSubmitting.value = false
  }
}

const refreshBookingDetails = () => {
  bookingDetailsStore.fetchBookingDetails(route.params.id)
}

const goToChat = () => {
  router.push({ name: 'chat' })
}

const closeCancelModal = () => {
  if (isCancelling.value) {
    return
  }

  cancelReason.value = ''
  isCancelModalOpen.value = false
}

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

onMounted(() => {
  bookingDetailsStore.fetchBookingDetails(route.params.id)

  if (isCompleted.value) {
    fireConfetti()
  }
})

onBeforeUnmount(() => {
  bookingDetailsStore.resetStore()
})
</script>

<style scoped>
.session-details-page {
  color: var(--sb-text-main);
}

.session-alive-frame {
  position: relative;
  overflow: hidden;
  border: 1px solid color-mix(in srgb, var(--sb-card-border) 86%, transparent);
  border-radius: 28px;
  background: color-mix(in srgb, var(--sb-card-bg) 84%, transparent);
  box-shadow: 0 24px 70px rgba(15, 23, 42, 0.1);
}

.session-alive-stage {
  position: relative;
  z-index: 1;
  padding: 20px;
}

.session-alive-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(300px, 0.38fr);
  gap: 16px;
  align-items: start;
}

.session-alive-column {
  display: flex;
  min-width: 0;
  flex-direction: column;
  gap: 16px;
}

/* Hero + countdown fused into the page's single saturated anchor. */
.session-anchor {
  overflow: hidden;
  border-radius: 24px;
  box-shadow: 0 18px 44px rgba(6, 24, 20, 0.28);
}

.session-detail-pair {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 16px;
}

.session-action-card {
  display: grid;
  align-content: start;
  gap: 0;
}

.session-progress-card {
  display: grid;
  gap: 14px;
}

.session-progress-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.session-progress-head h4 {
  margin: 0 0 6px;
  color: var(--sb-text-main);
  font-size: 1rem;
  font-weight: 850;
}

.session-progress-head p {
  margin: 0;
  color: var(--sb-text-muted);
  font-size: 0.8rem;
  line-height: 1.5;
}

.session-progress-chip {
  display: inline-flex;
  align-items: center;
  min-height: 32px;
  padding: 0 12px;
  border-radius: 999px;
  background: color-mix(in srgb, var(--sb-card-bg) 72%, transparent);
  border: 1px solid color-mix(in srgb, var(--sb-card-border) 84%, transparent);
  color: var(--sb-text-main);
  font-size: 0.74rem;
  font-weight: 800;
  white-space: nowrap;
}

.session-progress-button,
.session-progress-status {
  position: relative;
  display: grid;
  gap: 5px;
  padding: 16px 18px;
  border-radius: 20px;
  border: 1px solid color-mix(in srgb, var(--sb-card-border) 82%, transparent);
  background: color-mix(in srgb, var(--sb-card-bg) 82%, transparent);
}

.session-progress-button {
  text-align: left;
  cursor: pointer;
}

.session-progress-button:hover {
  box-shadow: 0 16px 30px rgba(15, 23, 42, 0.08);
}

.session-progress-button::after,
.session-progress-status::after {
  content: '';
  position: absolute;
  inset: auto 0 0;
  height: 3px;
  border-radius: 999px;
}

.session-progress-button-good::after,
.session-progress-status.is-good::after {
  background: linear-gradient(90deg, var(--sb-primary), var(--sb-primary-mid));
}

.session-progress-status.is-issues::after {
  background: linear-gradient(90deg, var(--sb-pop-yellow), var(--sb-pop-orange));
}

.session-progress-button strong,
.session-progress-status strong {
  color: var(--sb-text-dark);
  font-size: 0.94rem;
  font-weight: 850;
}

.session-progress-button span,
.session-progress-status span {
  color: var(--sb-text-muted);
  font-size: 0.8rem;
  line-height: 1.45;
}

.session-action-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 11px;
}

.session-action-card h4 {
  margin: 0 0 11px;
  color: var(--sb-text-main);
  font-size: 0.96rem;
  font-weight: 850;
  letter-spacing: 0;
}

.session-action-head h4 {
  margin: 0;
}

.session-action-card p {
  margin: 0 0 11px;
  color: var(--sb-text-muted);
  font-size: 0.8rem;
  line-height: 1.5;
}

.session-note {
  margin-top: 9px;
  font-size: 0.72rem;
}

.session-live-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border-radius: 999px;
  background: color-mix(in srgb, var(--sb-pop-pink) 16%, var(--sb-card-bg));
  color: var(--sb-pop-pink-deep);
  padding: 4px 10px;
  font-size: 0.64rem;
  font-weight: 800;
  text-transform: uppercase;
}

.session-live-pill span {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: currentColor;
  animation: session-live-beat 1.1s ease-in-out infinite;
}

/* Layout-only helper: the shared sb-btn tiers own the visuals. */
.session-cta {
  width: 100%;
  font-size: 0.86rem;
}

.session-cta + .session-cta {
  margin-top: 9px;
}

.session-cta:focus-visible {
  outline: 0;
  box-shadow:
    0 0 0 4px color-mix(in srgb, var(--sb-primary) 18%, transparent),
    0 10px 24px var(--sb-shadow-soft);
}

.session-quick-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}

.session-quick-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  gap: 7px;
  width: 100%;
  min-height: 78px;
  border-radius: 12px;
  padding: 11px;
  font: inherit;
  font-size: 0.72rem;
  font-weight: 700;
  border: 1px solid var(--sb-card-border);
  background: color-mix(in srgb, var(--sb-card-bg) 72%, transparent);
  color: var(--sb-text-secondary);
  line-height: 1.1;
}

.session-quick-button:focus-visible {
  outline: 0;
  box-shadow:
    0 0 0 4px color-mix(in srgb, var(--sb-primary) 18%, transparent),
    0 10px 24px var(--sb-shadow-soft);
}

.session-quick-button:hover:not(:disabled) {
  border-color: color-mix(in srgb, var(--sb-primary) 34%, var(--sb-card-border));
  background: color-mix(in srgb, var(--sb-card-bg) 96%, transparent);
  box-shadow: 0 16px 34px color-mix(in srgb, var(--sb-shadow-soft) 78%, rgba(15, 23, 42, 0.1));
}

.session-quick-button i {
  color: var(--sb-primary);
  font-size: 21px;
  transition: transform var(--sb-t-normal) var(--sb-spring);
}

.session-quick-button:hover:not(:disabled) i {
  transform: scale(1.12);
}

.summary-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 7px 0;
  border-bottom: 1px dashed var(--sb-card-border);
  font-size: 0.79rem;
}

.summary-row:last-of-type {
  border-bottom: 0;
}

.summary-label {
  color: var(--sb-text-muted);
}

.summary-value {
  color: var(--sb-text-dark);
  font-weight: 700;
  text-align: right;
}

.check-in-row + .check-in-row {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--sb-card-border);
}

.check-in-time {
  display: block;
  margin-top: 2px;
  color: var(--sb-text-muted);
  font-size: 0.82rem;
}

.receipt-image {
  width: 100%;
  border-radius: 16px;
  object-fit: cover;
}

.session-confetti {
  position: absolute;
  inset: 0;
  z-index: 5;
  overflow: hidden;
  pointer-events: none;
}

.session-confetti i {
  position: absolute;
  top: 26%;
  left: 50%;
  width: 9px;
  height: 5px;
  border-radius: 2px;
  background: var(--session-confetti-color);
  animation: session-confetti-burst 1.2s ease-out forwards;
  animation-delay: calc(var(--session-confetti-index) * 14ms);
}

.modal {
  background: rgba(17, 24, 39, 0.35);
}

@keyframes session-live-beat {
  50% {
    transform: scale(1.7);
    opacity: 0.4;
  }
}

@keyframes session-confetti-burst {
  to {
    transform:
      translate(
        calc(var(--session-confetti-x) * 34px),
        calc(260px + (var(--session-confetti-index) % 5) * 24px)
      )
      rotate(calc(var(--session-confetti-index) * 28deg));
    opacity: 0;
  }
}

@media (max-width: 900px) {
  .session-alive-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 575px) {
  .session-quick-grid {
    grid-template-columns: 1fr;
  }

  .session-alive-stage {
    padding: 12px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .session-live-pill span,
  .session-confetti i {
    animation: none;
  }

  .session-quick-button i {
    transition: none;
  }

  .session-quick-button:hover:not(:disabled) i {
    transform: none;
  }
}
</style>
