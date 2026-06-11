<template>
  <div class="booking-details container py-2">
    <div v-if="bookingDetailsStore.isLoading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status"></div>
    </div>

    <div v-else-if="!bookingDetailsStore.booking">
      <div class="alert alert-warning">Booking not found.</div>
    </div>

    <div v-else class="row g-4">
      <div class="col-12 col-lg-8">
        <div class="card shadow-sm p-4 h-100">
          <div class="d-flex gap-3 align-items-start">
            <div class="avatar-shell">
              <img
                v-if="bookingDetailsStore.tuteeProfile?.avatar"
                :src="bookingDetailsStore.tuteeProfile.avatar"
                alt="Tutee Avatar"
                class="avatar-image"
              />
              <div v-else class="avatar-fallback">
                {{ tuteeInitials }}
              </div>
            </div>

            <div class="flex-grow-1">
              <h3 class="fw-bold mb-2">{{ bookingDetailsStore.tuteeProfile?.name || 'N/A' }}</h3>
              <p class="text-muted mb-1">
                <strong>Email:</strong> {{ bookingDetailsStore.tuteeProfile?.email || 'N/A' }}
              </p>
              <p class="text-muted mb-1">
                <strong>Course:</strong> {{ bookingDetailsStore.tuteeProfile?.course || 'N/A' }}
              </p>
              <p class="text-muted mb-1">
                <strong>Year Level:</strong>
                {{ bookingDetailsStore.tuteeProfile?.year_level || 'N/A' }}
              </p>
              <p class="text-muted mb-0">
                <strong>Bio:</strong> {{ bookingDetailsStore.tuteeProfile?.bio || 'N/A' }}
              </p>
            </div>
          </div>

          <hr class="my-4" />

          <h5 class="fw-bold mb-3">Session Information</h5>
          <div class="row g-3">
            <div class="col-sm-6">
              <div class="info-card">
                <span class="info-label">Subject</span>
                <div class="info-value">
                  {{ bookingDetailsStore.sessionInfo?.subject || 'N/A' }}
                </div>
              </div>
            </div>
            <div class="col-sm-6">
              <div class="info-card">
                <span class="info-label">Date</span>
                <div class="info-value">{{ bookingDetailsStore.sessionInfo?.date || 'N/A' }}</div>
              </div>
            </div>
            <div class="col-sm-6">
              <div class="info-card">
                <span class="info-label">Time</span>
                <div class="info-value">
                  {{ bookingDetailsStore.sessionInfo?.start_time || 'N/A' }} -
                  {{ bookingDetailsStore.sessionInfo?.end_time || 'N/A' }}
                </div>
              </div>
            </div>
            <div class="col-sm-6">
              <div class="info-card">
                <span class="info-label">Status</span>
                <div class="info-value">
                  <span class="badge rounded-pill px-3 py-2" :class="statusClass">
                    {{ bookingDetailsStore.sessionInfo?.status || 'N/A' }}
                  </span>
                </div>
              </div>
            </div>
            <div class="col-sm-6">
              <div class="info-card">
                <span class="info-label">Session Mode</span>
                <div class="info-value">
                  {{ bookingDetailsStore.sessionInfo?.session_mode || 'N/A' }}
                </div>
              </div>
            </div>
            <div class="col-sm-6">
              <div class="info-card">
                <span class="info-label">Preferred Location</span>
                <div class="info-value">
                  {{
                    bookingDetailsStore.sessionInfo?.preferred_location ||
                    (bookingDetailsStore.sessionInfo?.session_mode === 'Online' ? 'Online' : 'N/A')
                  }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-12 col-lg-4">
        <div class="card shadow-sm p-4 h-100">
          <h5 class="fw-bold mb-3">Payment Summary</h5>

          <div class="summary-row">
            <span class="summary-label">Transaction ID</span>
            <span class="summary-value">{{
              bookingDetailsStore.paymentInfo?.transaction_id || 'N/A'
            }}</span>
          </div>

          <div class="summary-row">
            <span class="summary-label">Method</span>
            <span class="summary-value">{{
              bookingDetailsStore.paymentInfo?.method || 'N/A'
            }}</span>
          </div>

          <div class="summary-row">
            <span class="summary-label">Amount Paid</span>
            <span class="summary-value">PHP {{ amountPaid }}</span>
          </div>

          <div class="summary-row">
            <span class="summary-label">Payment Status</span>
            <span class="summary-value">{{
              bookingDetailsStore.paymentInfo?.status || 'Pending'
            }}</span>
          </div>

          <div v-if="bookingDetailsStore.paymentInfo?.receipt_image" class="mt-4">
            <h6 class="fw-bold mb-2">Receipt Image</h6>
            <img
              :src="bookingDetailsStore.paymentInfo.receipt_image"
              alt="Payment Receipt"
              class="receipt-image"
            />
          </div>

          <div v-if="isAwaitingVerification" class="alert alert-info mt-4 mb-3">
            The tutoring session has ended and the tutee has submitted payment for review.
          </div>

          <p v-if="isAwaitingVerification" class="small text-muted mb-3">
            If payment cannot be verified, contact support.
          </p>

          <div v-if="showDevReadyForPayment" class="alert alert-warning mt-4 mb-3">
            <div class="fw-bold mb-1">Dev option</div>
            <div class="small">
              End this session now so the tutee can open the post-session payment flow.
            </div>
          </div>

          <button
            v-if="showDevReadyForPayment"
            class="btn btn-warning fw-bold mb-3 sb-btn"
            :disabled="isDevSubmitting"
            @click="handleDevReadyForPayment"
          >
            {{ isDevSubmitting ? 'Updating...' : 'Dev: End Session Now' }}
          </button>

          <button
            v-if="isAwaitingVerification"
            class="btn btn-success mt-auto sb-btn"
            :disabled="isSubmitting"
            @click="handleComplete"
          >
            {{ isSubmitting ? 'Updating...' : 'Mark as Complete' }}
          </button>

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
        </div>

        <div v-if="hasCheckInResponses" class="card shadow-sm p-4 mt-4">
          <h5 class="fw-bold mb-3">Session Check-ins</h5>

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
        </div>
      </div>
    </div>

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
              class="form-control shadow-none"
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
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useNotificationsStore } from '@/stores/notifications'
import { useTutorBookingDetailStore } from '@/stores/tutorBookingDetails'
import { useToastStore } from '@/stores/toast'

const route = useRoute()
const router = useRouter()
const bookingDetailsStore = useTutorBookingDetailStore()
const notificationsStore = useNotificationsStore()
const toastStore = useToastStore()
const isSubmitting = ref(false)
const isDevSubmitting = ref(false)
const isCancelling = ref(false)
const isCancelModalOpen = ref(false)
const cancelReason = ref('')
const isDev = import.meta.env.DEV

const normalizedStatus = computed(() =>
  String(bookingDetailsStore.sessionInfo?.status || '').toLowerCase(),
)
const normalizedRawStatus = computed(() =>
  String(bookingDetailsStore.sessionInfo?.raw_status || '').toLowerCase(),
)
const isAwaitingVerification = computed(() => normalizedStatus.value === 'awaiting verification')
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

const tuteeInitials = computed(() => {
  const parts = String(bookingDetailsStore.tuteeProfile?.name || '')
    .split(' ')
    .filter(Boolean)
  return (
    parts
      .slice(0, 2)
      .map((part) => part[0])
      .join('')
      .toUpperCase() || 'SB'
  )
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
})

onBeforeUnmount(() => {
  bookingDetailsStore.resetStore()
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

.info-label,
.summary-label {
  display: block;
  font-size: 0.78rem;
  font-weight: 700;
  text-transform: uppercase;
  color: #6b7280;
  margin-bottom: 4px;
}

.info-value,
.summary-value {
  font-weight: 600;
  color: #1f2937;
}

.summary-row + .summary-row {
  margin-top: 12px;
}

.check-in-row + .check-in-row {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--sb-card-border);
}

.check-in-time {
  display: block;
  margin-top: 2px;
  color: #6b7280;
  font-size: 0.82rem;
}

.receipt-image {
  width: 100%;
  border-radius: 16px;
  object-fit: cover;
}
</style>
