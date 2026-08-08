<template>
  <div class="session-details-page container py-2">
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-sb-primary" role="status"></div>
      <div class="mt-2 text-muted">Loading session details...</div>
    </div>

    <div v-else-if="errorMessage || !sessionDetail" class="alert alert-warning">
      {{ errorMessage || 'Booking not found.' }}
    </div>

    <template v-else>
      <div
        v-if="paymentReturnMessage"
        class="alert d-flex align-items-center gap-2"
        :class="paymentReturnAlertClass"
      >
        <span
          v-if="paymentSyncing"
          class="spinner-border spinner-border-sm"
          role="status"
          aria-hidden="true"
        ></span>
        <i v-else class="bi" :class="paymentReturnIcon"></i>
        <span>{{ paymentReturnMessage }}</span>
      </div>

      <section class="session-alive-frame">
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
                  :subject="sessionDetail.session?.subject"
                  :status="normalizedStatus"
                  :status-label="sessionDetail.session?.status || 'Session'"
                  :is-ongoing="isOngoing"
                  :clock="heroClock"
                />

                <SessionCountdownBar
                  v-if="showDetailOrbit"
                  :presentation="detailOrbitPresentation"
                />
              </div>

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
              <SessionActionRail
                :is-ongoing="isOngoing"
                :can-submit-payment="canSubmitPayment"
                :is-awaiting-payment-verification="isAwaitingPaymentVerification"
                :is-completed="isCompleted"
                :rating-submitted="!!sessionDetail.rating_submitted"
                :show-cancel-action="showCancelAction"
                :can-cancel-session="canCancelSession"
                :is-cancelling="isCancelling"
                :is-pending="isPending"
                :is-quick-submitting="isQuickSubmitting"
                :cancel-action-message="cancelActionMessage"
                :midpoint-check-in="midpointCheckIn"
                :midpoint-status-title="midpointStatusTitle"
                :midpoint-status-copy="midpointStatusCopy"
                @open-chat="handleLightAction(goToChat)"
                @open-progress="openMidpointModal"
                @venue-arrived="handleVenueQuickAction"
                @submit-payment="handleLightAction(goToPayment)"
                @open-rating="openRatingModal"
                @open-cancel="handleLightAction(() => { isCancelModalOpen = true })"
                @report="handleLightAction(() => openSupport('Booking', sessionDetail?.session?.id))"
              />
            </div>
          </div>
        </div>
      </section>

      <DevSessionQaPanel
        class="mt-3"
        :booking-id="sessionDetail?.id"
        :session-mode="sessionDetail?.session?.session_mode"
        :location="sessionLocationValue"
        @refresh="loadSession"
      />
    </template>

    <RatingStackModal
      :open="isRatingModalOpen"
      :sessions="sessionsStore.unratedCompletedSessions"
      :initial-session-id="route.params.id"
      @close="isRatingModalOpen = false"
      @rated="handleRated"
    />

    <div
      v-if="isCancelModalOpen"
      class="session-cancel-shell"
      role="dialog"
      aria-modal="true"
      aria-labelledby="session-cancel-title"
      @click.self="closeCancelModal"
    >
      <div class="session-cancel-card">
        <div class="session-cancel-header">
          <div>
            <span class="session-cancel-eyebrow">Cancel session</span>
            <h5 id="session-cancel-title" class="session-cancel-title">Are you sure?</h5>
          </div>
          <button
            type="button"
            class="session-cancel-close sb-btn"
            aria-label="Close"
            :disabled="isCancelling"
            @click="closeCancelModal"
          >
            <i class="bi bi-x-lg"></i>
          </button>
        </div>

        <div class="session-cancel-body">
          <p class="session-cancel-lead">{{ cancelActionMessage }}</p>
          <label class="session-cancel-label" for="session-cancel-reason">Reason (required)</label>
          <textarea
            id="session-cancel-reason"
            v-model="cancelReason"
            class="session-cancel-field"
            rows="3"
            placeholder="Let your tutor know why you're cancelling..."
            :disabled="isCancelling"
          ></textarea>
          <p class="session-cancel-hint">
            Please also
            <a href="#" @click.prevent="goToChat">message your tutor in Chat</a>
            to coordinate.
          </p>
        </div>

        <div class="session-cancel-footer">
          <button
            type="button"
            class="session-cancel-btn session-cancel-btn-soft sb-btn"
            :disabled="isCancelling"
            @click="closeCancelModal"
          >
            Keep session
          </button>
          <button
            type="button"
            class="session-cancel-btn session-cancel-btn-danger sb-btn"
            :disabled="isCancelling || !reasonValid"
            @click="handleCancelSession"
          >
            <span
              v-if="isCancelling"
              class="spinner-border spinner-border-sm"
              role="status"
              aria-hidden="true"
            ></span>
            {{ isCancelling ? 'Cancelling...' : 'Yes, cancel session' }}
          </button>
        </div>
      </div>
    </div>
    <SupportModal
      :open="isSupportModalOpen"
      :context-type="supportContextType"
      :context-id="supportContextId"
      @close="isSupportModalOpen = false"
    />
    <SessionCheckInModal
      :open="isProgressModalOpen"
      :submitting="isQuickSubmitting"
      @close="isProgressModalOpen = false"
      @confirm="handleMidpointQuickAction"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useSessionsStore } from '@/stores/completedSessions'
import { useNotificationsStore } from '@/stores/notifications'
import { useToastStore } from '@/stores/toast'
import { useHaptics } from '@/composables/useHaptics'
import { useOrbitStrip } from '@/composables/useOrbitStrip'
import { resolveMidpointCheckInOutcome } from '@/composables/useMidpointCheckIn'
import { useSessionClock } from '@/composables/useSessionClock'
import RatingStackModal from '@/components/RatingStackModal.vue'
import SupportModal from '@/components/SupportModal.vue'
import DevSessionQaPanel from '@/components/DevSessionQaPanel.vue'
import SessionCountdownBar from '@/components/session/SessionCountdownBar.vue'
import SessionAurora from '@/components/session/SessionAurora.vue'
import SessionHero from '@/components/session/SessionHero.vue'
import SessionInfoGrid from '@/components/session/SessionInfoGrid.vue'
import SessionTimeline from '@/components/session/SessionTimeline.vue'
import SessionActionRail from '@/components/session/SessionActionRail.vue'
import SessionCheckInModal from '@/components/SessionCheckInModal.vue'

const route = useRoute()
const router = useRouter()
const sessionsStore = useSessionsStore()
const notificationsStore = useNotificationsStore()
const toastStore = useToastStore()
const { vibrate, patterns } = useHaptics()

const sessionDetail = ref(null)
const loading = ref(true)
const errorMessage = ref('')
const isRatingModalOpen = ref(false)
const isCancelModalOpen = ref(false)
const isCancelling = ref(false)
const isQuickSubmitting = ref(false)
const cancelReason = ref('')
const paymentSyncing = ref(false)
const paymentReturnMessage = ref('')
const paymentReturnState = ref('info')
const showConfetti = ref(false)
const isProgressModalOpen = ref(false)

const isSupportModalOpen = ref(false)
const supportContextType = ref('Booking')
const supportContextId = ref(null)

const confettiPieces = Array.from({ length: 26 }, (_, index) => index)
const confettiColors = [
  'var(--sb-primary)',
  'var(--sb-primary-mid)',
  'var(--sb-pop-yellow)',
  'var(--sb-pop-pink)',
  'var(--sb-pop-orange)',
  'var(--sb-aurora-violet)',
]

const openSupport = (type, id) => {
  supportContextType.value = type
  supportContextId.value = id
  isSupportModalOpen.value = true
}

const normalizedStatus = computed(() => String(sessionDetail.value?.session?.status || '').toLowerCase())
const canSubmitPayment = computed(() => normalizedStatus.value === 'payment required')
const isAwaitingPaymentVerification = computed(() => normalizedStatus.value === 'awaiting verification')
const isCompleted = computed(() => normalizedStatus.value === 'completed')
const statusOngoing = computed(() => normalizedStatus.value === 'ongoing')
const isUpcoming = computed(() => normalizedStatus.value === 'upcoming')
const isPending = computed(() => normalizedStatus.value === 'pending')
const reasonValid = computed(() => cancelReason.value.trim().length >= 5)
const tomorrowKey = computed(() => {
  const d = new Date()
  d.setDate(d.getDate() + 1)
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
})
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
const paymentReturnAlertClass = computed(() => {
  if (paymentReturnState.value === 'success') return 'alert-success'
  if (paymentReturnState.value === 'warning') return 'alert-warning'
  return 'alert-info'
})
const paymentReturnIcon = computed(() => {
  if (paymentReturnState.value === 'success') return 'bi-check-circle-fill'
  if (paymentReturnState.value === 'warning') return 'bi-exclamation-triangle-fill'
  return 'bi-info-circle-fill'
})

const counterpartProfile = computed(() => ({
  avatar: sessionDetail.value?.tutor?.avatar || '',
  name: sessionDetail.value?.tutor?.name || 'Tutor',
  meta: [
    'Your tutor',
    sessionDetail.value?.tutor?.course,
    sessionDetail.value?.tutor?.rating ? `Rating ${sessionDetail.value.tutor.rating}` : null,
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

const formattedSessionDate = computed(() => formatSessionDate(sessionDetail.value?.session?.date))

const formattedTimeRange = computed(() => {
  const start = sessionDetail.value?.session?.start_time
  const end = sessionDetail.value?.session?.end_time

  if (!start || !end) {
    return 'N/A'
  }

  return `${formatTime(start)} - ${formatTime(end)}`
})

const sessionModeLabel = computed(() => String(sessionDetail.value?.session?.session_mode || ''))

const isOnlineSession = computed(() => sessionModeLabel.value.toLowerCase() === 'online')

const sessionLocationValue = computed(() => {
  if (isOnlineSession.value) {
    return 'Online'
  }

  return sessionDetail.value?.session?.preferred_location || 'N/A'
})

const clock = useSessionClock({
  date: computed(() => sessionDetail.value?.session?.date),
  startTime: computed(() => sessionDetail.value?.session?.start_time),
  endTime: computed(() => sessionDetail.value?.session?.end_time),
  isOngoing: statusOngoing,
})
const { presentation: detailOrbitPresentation, hasOrbit: showDetailOrbit } = useOrbitStrip({
  session: sessionDetail,
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
  { label: 'Subject', value: sessionDetail.value?.session?.subject },
  { label: 'Date', value: formattedSessionDate.value },
  { label: 'Time', value: formattedTimeRange.value },
  { label: 'Mode', value: sessionModeLabel.value },
  ...(isOnlineSession.value ? [] : [{ label: 'Location', value: sessionLocationValue.value }]),
  { label: 'Status', value: sessionDetail.value?.session?.status },
])

const midpointCheckIn = computed(() => sessionDetail.value?.check_ins?.midpoint_checkin || null)
const midpointStatusTitle = computed(() => {
  if (midpointCheckIn.value?.response === 'issues') {
    return 'Issue flagged during the session'
  }

  return 'Progress check saved'
})

const midpointStatusCopy = computed(() => {
  if (midpointCheckIn.value?.response === 'issues') {
    return 'Support can step in while the session is still ongoing.'
  }

  return 'You already confirmed the session is going well.'
})

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

const handleLightAction = (callback) => {
  vibrate(patterns.light)
  callback()
}

const openRatingModal = () => {
  vibrate(patterns.celebratory)
  isRatingModalOpen.value = true
}

const openMidpointModal = () => {
  vibrate(patterns.light)
  isProgressModalOpen.value = true
}

const handleVenueQuickAction = async () => {
  if (isQuickSubmitting.value || !sessionDetail.value?.id) {
    return
  }

  vibrate(patterns.light)
  isQuickSubmitting.value = true

  try {
    sessionDetail.value = await sessionsStore.confirmVenue(sessionDetail.value.id, 'yes')
    toastStore.push('Arrival saved. Have a great session.')
  } catch (error) {
    toastStore.push(error.response?.data?.error || 'Failed to save your arrival.', 'error')
  } finally {
    isQuickSubmitting.value = false
  }
}

const handleMidpointQuickAction = async (response) => {
  if (isQuickSubmitting.value || !sessionDetail.value?.id) {
    return
  }

  vibrate(response === 'issues' ? patterns.medium : patterns.light)
  isQuickSubmitting.value = true

  try {
    sessionDetail.value = await sessionsStore.submitMidpointCheckIn(sessionDetail.value.id, response)
    isProgressModalOpen.value = false

    const savedResponse = sessionDetail.value?.check_ins?.midpoint_checkin?.response
    const outcome = resolveMidpointCheckInOutcome(response, savedResponse)

    toastStore.push(outcome.toastMessage, outcome.toastType)

    if (outcome.openSupport) {
      openSupport('Booking', sessionDetail.value?.session?.id)
    }
  } catch (error) {
    toastStore.push(error.response?.data?.error || 'Failed to save your check-in.', 'error')
  } finally {
    isQuickSubmitting.value = false
  }
}

const loadSession = async () => {
  try {
    loading.value = true
    const [detail] = await Promise.all([
      sessionsStore.fetchSessionById(route.params.id),
      sessionsStore.fetchSessions()
    ])
    sessionDetail.value = detail
  } catch (error) {
    console.error('Failed to load session detail:', error)
    errorMessage.value = 'Failed to load session details.'
  } finally {
    loading.value = false
  }
}

const syncReturnedOnlinePayment = async () => {
  if (route.query.payment !== 'success') {
    return
  }

  paymentSyncing.value = true
  paymentReturnState.value = 'info'
  paymentReturnMessage.value = 'Confirming your online payment...'

  try {
    sessionDetail.value = await sessionsStore.verifyOnlinePayment(route.params.id)
    await notificationsStore.fetchNotifications()
    paymentReturnState.value = 'success'
    paymentReturnMessage.value = 'Payment confirmed. Waiting for tutor verification.'
    router.replace({ name: 'tuteeSessionDetails', params: route.params, query: {} })
  } catch (error) {
    paymentReturnState.value = 'warning'
    paymentReturnMessage.value = error.response?.data?.error || 'Unable to confirm the online payment yet.'
  } finally {
    paymentSyncing.value = false
  }
}

const closeCancelModal = () => {
  if (isCancelling.value) {
    return
  }

  cancelReason.value = ''
  isCancelModalOpen.value = false
}

const goToPayment = () => {
  router.push({ name: 'PaymentTutee', params: { bookingId: route.params.id } })
}

const goToChat = () => {
  router.push({ name: 'chat' })
}

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

const handleRated = async () => {
  await loadSession()

  if (!sessionsStore.unratedCompletedSessions.length) {
    isRatingModalOpen.value = false
  }
}

onMounted(async () => {
  await loadSession()
  await syncReturnedOnlinePayment()

  if (isCompleted.value) {
    fireConfetti()
  }
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

.session-cancel-shell {
  position: fixed;
  inset: 0;
  z-index: 1200;
  display: grid;
  place-items: center;
  padding: 24px;
  background: rgba(15, 23, 42, 0.45);
}

.session-cancel-card {
  width: min(100%, 440px);
  padding: 26px;
  background:
    radial-gradient(circle at 12% 16%, color-mix(in srgb, var(--sb-primary) 12%, transparent), transparent 34%),
    radial-gradient(circle at 88% 84%, color-mix(in srgb, var(--sb-pop-orange) 12%, transparent), transparent 28%),
    var(--sb-card-bg);
  border: 1px solid var(--sb-card-border);
  border-radius: 24px;
  box-shadow: 0 24px 64px rgba(15, 23, 42, 0.16);
}

.session-cancel-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  padding-bottom: 14px;
  border-bottom: 1px solid var(--sb-card-border);
}

.session-cancel-eyebrow {
  display: block;
  margin-bottom: 4px;
  color: var(--sb-danger);
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0;
  text-transform: uppercase;
}

.session-cancel-title {
  margin: 0;
  color: var(--sb-text-main);
  font-size: 18px;
  font-weight: 800;
}

.session-cancel-close {
  display: grid;
  place-items: center;
  width: 32px;
  height: 32px;
  border: 0;
  border-radius: 50%;
  background: color-mix(in srgb, var(--sb-text-main) 8%, transparent);
  color: var(--sb-text-muted);
}

.session-cancel-body {
  padding: 18px 0;
}

.session-cancel-lead {
  margin: 0 0 14px;
  color: var(--sb-text-main);
  font-size: 14px;
  line-height: 1.5;
}

.session-cancel-label {
  display: block;
  margin-bottom: 6px;
  color: var(--sb-text-muted);
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0;
  text-transform: uppercase;
}

.session-cancel-field {
  width: 100%;
  padding: 12px 14px;
  border: 1px solid var(--sb-card-border);
  border-radius: 14px;
  background: color-mix(in srgb, var(--sb-card-bg) 96%, transparent);
  color: var(--sb-text-main);
  font: inherit;
  font-size: 14px;
  resize: vertical;
}

.session-cancel-field:focus {
  outline: 0;
  border-color: color-mix(in srgb, var(--sb-danger) 40%, var(--sb-card-border));
}

.session-cancel-hint {
  margin: 10px 0 0;
  color: var(--sb-text-muted);
  font-size: 12.5px;
}

.session-cancel-hint a {
  color: var(--sb-primary);
  font-weight: 700;
  text-decoration: none;
}

.session-cancel-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding-top: 16px;
  border-top: 1px solid var(--sb-card-border);
}

.session-cancel-btn {
  min-height: 42px;
  padding: 0 18px;
}

.session-cancel-btn-soft {
  border: 1px solid var(--sb-card-border);
  background: color-mix(in srgb, var(--sb-card-bg) 72%, transparent);
  color: var(--sb-text-main);
}

.session-cancel-btn-danger {
  border: 0;
  background: var(--sb-danger);
  color: #fff;
  box-shadow: 0 8px 18px rgba(239, 68, 68, 0.25);
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
  .session-alive-stage {
    padding: 12px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .session-confetti i {
    animation: none;
  }
}
</style>
