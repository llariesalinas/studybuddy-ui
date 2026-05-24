<template>
  <div class="container py-2">
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

      <div class="row g-4">
        <div class="col-12 col-lg-8">
          <div class="card shadow-sm p-4 h-100">
          <div class="d-flex gap-3 align-items-start">
            <div class="avatar-shell">
              <img
                v-if="sessionDetail.tutor?.avatar"
                :src="sessionDetail.tutor.avatar"
                alt="Tutor Avatar"
                class="avatar-image"
              />
              <div v-else class="avatar-fallback">
                {{ tutorInitials }}
              </div>
            </div>

            <div class="flex-grow-1">
              <h3 class="fw-bold mb-1">{{ sessionDetail.tutor?.name || 'Tutor' }}</h3>
              <p class="text-muted mb-1"><strong>Email:</strong> {{ sessionDetail.tutor?.email || 'N/A' }}</p>
              <p class="text-muted mb-1"><strong>Course:</strong> {{ sessionDetail.tutor?.course || 'N/A' }}</p>
              <p class="text-muted mb-1"><strong>Rating:</strong> {{ sessionDetail.tutor?.rating ?? 'N/A' }}</p>

              <div class="mt-3">
                <span
                  v-for="subject in sessionDetail.tutor?.subjects_taught || []"
                  :key="subject"
                  class="badge bg-sb-primary me-2 mb-2"
                >
                  {{ subject }}
                </span>
              </div>
            </div>
          </div>

          <hr class="my-4">

          <h5 class="fw-bold mb-3">Session Information</h5>
          <div class="row g-3">
            <div class="col-sm-6">
              <div class="info-card">
                <span class="info-label">Subject</span>
                <div class="info-value">{{ sessionDetail.session?.subject || 'N/A' }}</div>
              </div>
            </div>
            <div class="col-sm-6">
              <div class="info-card">
                <span class="info-label">Date</span>
                <div class="info-value">{{ sessionDetail.session?.date || 'N/A' }}</div>
              </div>
            </div>
            <div class="col-sm-6">
              <div class="info-card">
                <span class="info-label">Time</span>
                <div class="info-value">{{ formattedTimeRange }}</div>
              </div>
            </div>
            <div class="col-sm-6">
              <div class="info-card">
                <span class="info-label">Status</span>
                <div class="info-value">
                  <span class="badge rounded-pill px-3 py-2" :class="statusClass">
                    {{ sessionDetail.session?.status }}
                  </span>
                </div>
              </div>
            </div>
            <div class="col-sm-6">
              <div class="info-card">
                <span class="info-label">Session Mode</span>
                <div class="info-value">{{ sessionDetail.session?.session_mode || 'N/A' }}</div>
              </div>
            </div>
            <div class="col-sm-6">
              <div class="info-card">
                <span class="info-label">Preferred Location</span>
                <div class="info-value">
                  {{ sessionDetail.session?.preferred_location || (sessionDetail.session?.session_mode === 'Online' ? 'Online' : 'N/A') }}
                </div>
              </div>
            </div>
          </div>
          </div>
        </div>

        <div class="col-12 col-lg-4">
          <div class="card shadow-sm p-4 h-100">
          <h5 class="fw-bold mb-3">Next Action</h5>

          <template v-if="canSubmitPayment">
            <p class="text-muted">
              Your session has ended. Submit your post-session payment details so your tutor can verify them.
            </p>
            <button class="btn bg-sb-primary text-white w-100" @click="goToPayment">
              Submit Payment
            </button>
          </template>

          <template v-else-if="isAwaitingPaymentVerification">
            <p class="text-muted mb-3">
              Waiting for your tutor to review the submitted payment.
            </p>
            <button class="btn btn-outline-secondary w-100" disabled>
              Waiting for tutor verification...
            </button>
          </template>

          <template v-else-if="isCompleted && !sessionDetail.rating_submitted">
            <p class="text-muted mb-3">
              Your session is complete. A rating is optional, but it helps improve StudyBuddy matches.
            </p>
            <button
              class="btn bg-sb-primary text-white w-100"
              @click="isRatingModalOpen = true"
            >
              Leave a Rating
            </button>
          </template>

          <template v-else-if="showCancelAction">
            <p class="text-muted mb-3">
              {{ cancelActionMessage }}
            </p>
            <button
              class="btn btn-outline-danger w-100"
              :disabled="isCancelling || !canCancelSession"
              @click="isCancelModalOpen = true"
            >
              {{ isCancelling ? 'Cancelling...' : 'Cancel Session' }}
            </button>
          </template>

          <template v-else>
            <p class="text-muted mb-0">
              No pending action for this session right now.
            </p>
          </template>
        </div>
      </div>
    </div>
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
            <p class="mb-0">Are you sure you want to cancel this session?</p>
          </div>

          <div class="modal-footer">
            <button
              type="button"
              class="btn btn-outline-secondary"
              :disabled="isCancelling"
              @click="closeCancelModal"
            >
              Keep Session
            </button>
            <button
              type="button"
              class="btn btn-danger"
              :disabled="isCancelling"
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
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useSessionsStore } from '@/stores/completedSessions'
import { useNotificationsStore } from '@/stores/notifications'
import RatingStackModal from '@/components/RatingStackModal.vue'

const route = useRoute()
const router = useRouter()
const sessionsStore = useSessionsStore()
const notificationsStore = useNotificationsStore()

const sessionDetail = ref(null)
const loading = ref(true)
const errorMessage = ref('')
const isRatingModalOpen = ref(false)
const isCancelModalOpen = ref(false)
const isCancelling = ref(false)
const paymentSyncing = ref(false)
const paymentReturnMessage = ref('')
const paymentReturnState = ref('info')

const normalizedStatus = computed(() => String(sessionDetail.value?.session?.status || '').toLowerCase())
const canSubmitPayment = computed(() => normalizedStatus.value === 'payment required')
const isAwaitingPaymentVerification = computed(() => normalizedStatus.value === 'awaiting verification')
const isCompleted = computed(() => normalizedStatus.value === 'completed')
const isUpcoming = computed(() => normalizedStatus.value === 'upcoming')
const todayKey = computed(() => {
  const today = new Date()
  const year = today.getFullYear()
  const month = String(today.getMonth() + 1).padStart(2, '0')
  const day = String(today.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
})
const showCancelAction = computed(() => isUpcoming.value)
const canCancelSession = computed(() => (
  isUpcoming.value
  && String(sessionDetail.value?.session?.date || '') > todayKey.value
))
const cancelActionMessage = computed(() => {
  if (canCancelSession.value) {
    return 'This upcoming session can still be cancelled before the session date.'
  }

  return 'Cancellation is only available before the session date.'
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

const tutorInitials = computed(() => {
  const parts = String(sessionDetail.value?.tutor?.name || '')
    .split(' ')
    .filter(Boolean)
  return parts.slice(0, 2).map(part => part[0]).join('').toUpperCase() || 'SB'
})

const formattedTimeRange = computed(() => {
  const start = sessionDetail.value?.session?.start_time
  const end = sessionDetail.value?.session?.end_time

  if (!start || !end) {
    return 'N/A'
  }

  const formatTime = (value) => {
    const [hour, minute] = value.split(':').map(Number)
    const suffix = hour >= 12 ? 'PM' : 'AM'
    const displayHour = hour % 12 || 12
    return `${displayHour}:${String(minute).padStart(2, '0')} ${suffix}`
  }

  return `${formatTime(start)} - ${formatTime(end)}`
})

const statusClass = computed(() => {
  switch (normalizedStatus.value) {
    case 'pending':
      return 'bg-warning text-dark'
    case 'upcoming':
      return 'bg-primary text-white'
    case 'ongoing':
      return 'bg-info text-white'
    case 'payment required':
      return 'bg-warning-subtle text-dark'
    case 'awaiting verification':
      return 'bg-info text-dark'
    case 'completed':
      return 'bg-success text-white'
    case 'rejected':
    case 'cancelled':
      return 'bg-danger text-white'
    default:
      return 'bg-secondary text-white'
  }
})

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

  isCancelModalOpen.value = false
}

const goToPayment = () => {
  router.push({ name: 'PaymentTutee', params: { bookingId: route.params.id } })
}

const handleCancelSession = async () => {
  if (!canCancelSession.value) {
    return
  }

  isCancelling.value = true

  try {
    const updatedDetail = await sessionsStore.cancelSession(route.params.id)
    sessionDetail.value = updatedDetail
    isCancelModalOpen.value = false
    await notificationsStore.fetchNotifications()
    alert('Session cancelled successfully.')
  } catch (error) {
    alert(error.response?.data?.error || 'Failed to cancel session.')
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
})
</script>

<style scoped>
.avatar-shell {
  width: 108px;
  height: 108px;
  flex-shrink: 0;
}

.avatar-image,
.avatar-fallback {
  width: 100%;
  height: 100%;
  border-radius: 20px;
}

.avatar-image {
  object-fit: cover;
}

.avatar-fallback {
  display: grid;
  place-items: center;
  background: rgba(0, 137, 90, 0.1);
  color: var(--sb-primary);
  font-size: 1.75rem;
  font-weight: 700;
}

.info-card {
  border: 1px solid var(--sb-card-border);
  border-radius: 16px;
  padding: 16px;
  height: 100%;
}

.modal {
  background: rgba(17, 24, 39, 0.35);
}

.info-label {
  display: block;
  font-size: 0.78rem;
  font-weight: 700;
  text-transform: uppercase;
  color: #6b7280;
  margin-bottom: 4px;
}

.info-value {
  font-weight: 600;
  color: #1f2937;
}
</style>
