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

          <template v-if="isConfirmed">
            <p class="text-muted">
              Confirm the session by submitting your post-session payment details.
            </p>
            <button class="btn bg-sb-primary text-white w-100" @click="goToPayment">
              Confirm Session
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
              data-bs-toggle="modal"
              data-bs-target="#ratingModal"
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

    <div ref="ratingModalRef" class="modal fade" id="ratingModal" tabindex="-1" aria-hidden="true">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content rounded-4">
          <div class="modal-header border-0">
            <h5 class="modal-title fw-bold">Rate Your Session</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>

          <div class="modal-body text-center py-4">
            <p class="text-muted mb-4">
              How was your session with {{ sessionDetail?.tutor?.name || 'your tutor' }}?
            </p>

            <div class="d-flex justify-content-center gap-2 mb-3 text-warning fs-1">
              <i
                v-for="star in 5"
                :key="star"
                class="bi"
                :class="currentRating >= star ? 'bi-star-fill' : 'bi-star'"
                style="cursor: pointer;"
                @click="currentRating = star"
              ></i>
            </div>

            <textarea
              v-model="ratingComment"
              class="form-control"
              rows="3"
              placeholder="Add an optional comment"
            ></textarea>
          </div>

          <div class="modal-footer border-0">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Skip for Now</button>
            <button
              type="button"
              class="btn bg-sb-primary text-white"
              :disabled="currentRating === 0 || isSubmittingRating"
              @click="submitRating"
            >
              {{ isSubmittingRating ? 'Submitting...' : 'Submit Rating' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import * as bootstrap from 'bootstrap'
import { useSessionsStore } from '@/stores/completedSessions'

const route = useRoute()
const router = useRouter()
const sessionsStore = useSessionsStore()

const sessionDetail = ref(null)
const loading = ref(true)
const errorMessage = ref('')
const currentRating = ref(0)
const ratingComment = ref('')
const isSubmittingRating = ref(false)
const ratingModalRef = ref(null)

const normalizedStatus = computed(() => String(sessionDetail.value?.session?.status || '').toLowerCase())
const isConfirmed = computed(() => normalizedStatus.value === 'confirmed')
const isAwaitingPaymentVerification = computed(() => normalizedStatus.value === 'awaiting payment verification')
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
    case 'confirmed':
      return 'bg-primary text-white'
    case 'awaiting payment verification':
      return 'bg-info text-dark'
    case 'completed':
      return 'bg-success text-white'
    default:
      return 'bg-secondary text-white'
  }
})

const loadSession = async () => {
  try {
    loading.value = true
    sessionDetail.value = await sessionsStore.fetchSessionById(route.params.id)
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

const cleanupRatingModalArtifacts = () => {
  document.body.classList.remove('modal-open')
  document.body.style.removeProperty('padding-right')

  document.querySelectorAll('.modal-backdrop').forEach((backdrop) => {
    backdrop.remove()
  })
}

const hideRatingModal = () => {
  const modalElement = ratingModalRef.value

  if (!modalElement) {
    cleanupRatingModalArtifacts()
    return
  }

  const modalInstance = bootstrap.Modal.getInstance(modalElement) || bootstrap.Modal.getOrCreateInstance(modalElement)
  modalInstance.hide()

  window.setTimeout(() => {
    cleanupRatingModalArtifacts()
  }, 200)
}

const submitRating = async () => {
  if (!currentRating.value) {
    return
  }

  isSubmittingRating.value = true

  try {
    sessionDetail.value = await sessionsStore.submitRating(
      route.params.id,
      currentRating.value,
      ratingComment.value
    )
    hideRatingModal()
    currentRating.value = 0
    ratingComment.value = ''
  } catch (error) {
    console.error('Failed to submit rating:', error)
    alert(error.response?.data?.error || 'Failed to submit rating.')
  } finally {
    isSubmittingRating.value = false
  }
}

onMounted(loadSession)
onBeforeUnmount(cleanupRatingModalArtifacts)
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
