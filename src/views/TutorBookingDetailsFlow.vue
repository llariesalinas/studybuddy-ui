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
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useNotificationsStore } from '@/stores/notifications'
import { useTutorBookingDetailStore } from '@/stores/tutorBookingDetails'

const route = useRoute()
const bookingDetailsStore = useTutorBookingDetailStore()
const notificationsStore = useNotificationsStore()
const isSubmitting = ref(false)
const isDevSubmitting = ref(false)
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

const amountPaid = computed(() => {
  const value = Number(bookingDetailsStore.paymentInfo?.amount_paid || 0)
  return value.toFixed(2)
})

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
    alert('Session marked as completed.')
  } catch (error) {
    alert(error.response?.data?.error || 'Failed to complete session.')
  } finally {
    isSubmitting.value = false
  }
}

const handleDevReadyForPayment = async () => {
  isDevSubmitting.value = true

  try {
    await bookingDetailsStore.devMarkReadyForPayment()
    await notificationsStore.fetchNotifications()
    alert('Dev: session is ready for tutee payment.')
  } catch (error) {
    alert(error.response?.data?.error || 'Failed to make session ready for payment.')
  } finally {
    isDevSubmitting.value = false
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

.receipt-image {
  width: 100%;
  border-radius: 16px;
  object-fit: cover;
}
</style>
