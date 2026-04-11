<template>
  <div class="container py-2">
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-sb-primary" role="status"></div>
      <div class="mt-2 text-muted">Loading session details...</div>
    </div>

    <div v-else-if="errorMessage || !sessionDetail" class="alert alert-warning">
      {{ errorMessage || 'Booking not found.' }}
    </div>

    <div v-else class="row g-4">
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

          <template v-else>
            <p class="text-muted mb-0">
              No pending action for this session right now.
            </p>
          </template>
        </div>
      </div>
    </div>

    <RatingStackModal
      :open="isRatingModalOpen"
      :sessions="sessionsStore.unratedCompletedSessions"
      :initial-session-id="route.params.id"
      @close="isRatingModalOpen = false"
      @rated="handleRated"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useSessionsStore } from '@/stores/completedSessions'
import RatingStackModal from '@/components/RatingStackModal.vue'

const route = useRoute()
const router = useRouter()
const sessionsStore = useSessionsStore()

const sessionDetail = ref(null)
const loading = ref(true)
const errorMessage = ref('')
const isRatingModalOpen = ref(false)

const normalizedStatus = computed(() => String(sessionDetail.value?.session?.status || '').toLowerCase())
const canSubmitPayment = computed(() => normalizedStatus.value === 'payment required')
const isAwaitingPaymentVerification = computed(() => normalizedStatus.value === 'awaiting verification')
const isCompleted = computed(() => normalizedStatus.value === 'completed')

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

const goToPayment = () => {
  router.push({ name: 'PaymentTutee', params: { bookingId: route.params.id } })
}

const handleRated = async () => {
  await loadSession()

  if (!sessionsStore.unratedCompletedSessions.length) {
    isRatingModalOpen.value = false
  }
}

onMounted(loadSession)
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
