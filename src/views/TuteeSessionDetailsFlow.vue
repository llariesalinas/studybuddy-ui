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

              <section v-if="isOngoing" class="session-progress-card glass-segment">
                <div class="session-progress-head">
                  <div>
                    <h4>Mid-session pulse</h4>
                    <p>
                      A quick check helps us understand whether you are making progress while the session is still live.
                    </p>
                  </div>
                  <span class="session-progress-chip">
                    {{ heroClock.formattedElapsed }} elapsed
                  </span>
                </div>

                <template v-if="midpointCheckIn">
                  <div class="session-progress-status" :class="`is-${midpointCheckIn.response || 'saved'}`">
                    <strong>{{ midpointStatusTitle }}</strong>
                    <span>{{ midpointStatusCopy }}</span>
                  </div>
                </template>

                <template v-else>
                  <button
                    class="session-progress-button session-progress-button-good sb-btn"
                    :disabled="isQuickSubmitting"
                    @click="openMidpointModal"
                  >
                    <strong>Answer progress check</strong>
                    <span>Opens the mid-session popup so you can confirm things are on track or ask for help.</span>
                  </button>
                </template>
              </section>

              <section v-if="isOngoing" class="session-action-card glass-segment">
                <h4>Quick actions</h4>
                <div class="session-quick-grid">
                  <button
                    class="session-quick-button sb-btn"
                    :disabled="isQuickSubmitting"
                    @click="handleVenueQuickAction"
                  >
                    <i class="bi bi-geo-alt"></i>
                    I've arrived
                  </button>
                  <button class="session-quick-button sb-btn" @click="handleLightAction(goToChat)">
                    <i class="bi bi-chat-dots"></i>
                    Message
                  </button>
                  <button
                    class="session-quick-button sb-btn"
                    :disabled="isQuickSubmitting"
                    @click="openMidpointModal"
                  >
                    <i class="bi bi-activity"></i>
                    Progress check
                  </button>
                  <button
                    class="session-quick-button sb-btn"
                    @click="handleLightAction(() => openSupport('Booking', sessionDetail?.session?.id))"
                  >
                    <i class="bi bi-flag"></i>
                    Report
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
                  <p>Your session is live. Use the progress pulse and quick actions to stay in sync.</p>
                  <button
                    class="session-cta sb-btn btn-primary-action sb-elevated sb-elevated--brand"
                    @click="handleLightAction(goToChat)"
                  >
                    <i class="bi bi-chat-dots"></i>
                    Open chat
                  </button>
                </template>

                <template v-else-if="canSubmitPayment">
                  <p>
                    Your session has ended. Submit your post-session payment details so your tutor can verify them.
                  </p>
                  <button
                    class="session-cta sb-btn btn-primary-action sb-elevated sb-elevated--brand"
                    @click="handleLightAction(goToPayment)"
                  >
                    Submit Payment
                  </button>
                </template>

                <template v-else-if="isAwaitingPaymentVerification">
                  <p>Waiting for your tutor to review the submitted payment.</p>
                  <button class="session-cta sb-btn btn-soft" disabled>
                    Waiting for tutor verification...
                  </button>
                </template>

                <template v-else-if="isCompleted && !sessionDetail.rating_submitted">
                  <p>Your session is complete. A rating is optional, but it helps improve StudyBuddy matches.</p>
                  <button
                    class="session-cta sb-btn btn-primary-action sb-elevated sb-elevated--brand"
                    @click="openRatingModal"
                  >
                    <i class="bi bi-star"></i>
                    Leave a Rating
                  </button>
                </template>

                <template v-else-if="showCancelAction">
                  <p>{{ cancelActionMessage }}</p>
                  <button
                    class="session-cta sb-btn btn-danger-soft"
                    :disabled="isCancelling || !canCancelSession"
                    @click="handleLightAction(() => { isCancelModalOpen = true })"
                  >
                    {{ isCancelling ? 'Cancelling...' : isPending ? 'Withdraw request' : 'Cancel Session' }}
                  </button>
                </template>

                <template v-else>
                  <p>No pending action for this session right now.</p>
                </template>
              </section>

              <section class="session-action-card glass-segment">
                <h4>Support</h4>
                <p>Something off with this session?</p>
                <button
                  class="session-cta sb-btn btn-danger-soft"
                  @click="handleLightAction(() => openSupport('Booking', sessionDetail?.session?.id))"
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
              class="form-control border-sb shadow-none sb-field"
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
              @click="handleCancelSession"
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

const actionTitle = computed(() => {
  if (isOngoing.value) return 'Happening now'
  if (canSubmitPayment.value) return 'Next action'
  if (isAwaitingPaymentVerification.value) return 'Payment review'
  if (isCompleted.value) return sessionDetail.value?.rating_submitted ? 'All done' : 'All done'
  return 'Next action'
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
  border: 1px solid var(--sb-card-border);
  border-radius: 12px;
  padding: 11px;
  background: color-mix(in srgb, var(--sb-card-bg) 72%, transparent);
  color: var(--sb-text-secondary);
  font: inherit;
  font-size: 0.72rem;
  font-weight: 700;
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
