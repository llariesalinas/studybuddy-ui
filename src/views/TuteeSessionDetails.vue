<template>
  <div class="booking-details container py-2">

    <div v-if="isLoading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status"></div>
      <div class="mt-2 text-muted">Loading session details...</div>
    </div>

    <div v-else-if="errorMessage || !session" class="alert alert-warning">
      {{ errorMessage || 'Booking not found.' }}
    </div>

    <div v-else class="row g-4">

      <div class="col-12 col-md-8">
        <div class="card shadow-sm p-3 d-flex flex-row align-items-stretch h-100 gap-3">
          <div style="width: 35%; flex-shrink: 0;">
            <img
              v-if="session.tutor?.avatar"
              :src="session.tutor.avatar"
              style="width: 100%; height: 100%; object-fit: cover; border-radius: 10pt;"
              alt="Tutor Avatar"
            />
            <div v-else class="bg-secondary text-white d-flex justify-content-center align-items-center" style="width: 100%; height: 100%; border-radius: 10pt;">
              No Image
            </div>
          </div>

          <div class="flex-grow-1 py-2">
            <h3 class="fw-bold mb-1">{{ session.tutor?.name || 'TBD' }}</h3>
            <p class="text-muted mb-1">
              <strong>Rating:</strong> {{ session.tutor?.rating ? session.tutor.rating + '⭐' : 'No reviews yet' }}
            </p>
            <p class="text-muted mb-1">
              <strong>Course:</strong> {{ session.tutor?.course || 'N/A' }}
            </p>
            <p class="text-muted mb-1">
              <strong>Year Level:</strong> {{ session.tutor?.year_level || 'N/A' }}
            </p>
            <p class="text-muted mb-1">
              <strong>Email:</strong> {{ session.tutor?.email || 'N/A' }}
            </p>
            <p class="text-muted mb-1">
              <strong>Contact:</strong> {{ session.tutor?.contact_number || 'N/A' }}
            </p>
            <p class="text-muted mb-0 mt-2">
              <strong>Subjects Taught:</strong> 
              <span class="badge bg-sb-primary me-1" v-for="subject in session.tutor?.subjects_taught" :key="subject">
                {{ subject }}
              </span>
              <span v-if="!session.tutor?.subjects_taught?.length">N/A</span>
            </p>
          </div>
        </div>
      </div>

      <div class="col-12 col-md-4">
        <div class="card shadow-sm p-4 h-100 d-flex flex-column justify-content-between">
          <div>
            <h5 class="fw-bold mb-3">Tutor Remarks</h5>
            <div class="p-3 bg-light border rounded text-muted" style="min-height: 120px;">
              {{ session.tutor_remarks || 'No remarks provided for this session yet.' }}
            </div>
          </div>

          <div class="mt-4">
            <button
              class="btn bg-sb-primary text-white px-4 py-2 rounded-3 fw-semibold shadow-sm w-100"
              :disabled="isButtonDisabled"
              data-bs-toggle="modal"
              data-bs-target="#confirmationModal"
              @click="prepareConfirmation"
            >
              Confirm Session Completion
            </button>
          </div>
        </div>
      </div>

      <div class="col-12">
        <div class="card shadow-sm">
          <div class="card-body">
            <h5 class="fw-bold mb-3">Session Information</h5>

            <div class="row text-center fw-semibold mb-2">
              <div class="col">Subject</div>
              <div class="col">Date</div>
              <div class="col">Time</div>
              <div class="col">Status</div>
            </div>

            <div class="row text-center text-muted">
              <div class="col">{{ session.subject || 'N/A' }}</div>
              <div class="col">{{ session.date || 'N/A' }}</div>
              <div class="col">
                {{ formatTime(session.start_time) }} – {{ formatTime(session.end_time) }}
              </div>
              <div class="col">
                <span 
                  class="badge"
                  :class="{
                    'bg-warning text-dark': session.status?.toLowerCase() === 'pending',
                    'bg-primary': session.status?.toLowerCase() === 'confirmed',
                    'bg-info': session.status?.toLowerCase() === 'ongoing',
                    'bg-success': session.status?.toLowerCase() === 'completed'
                  }"
                >
                  {{ session.status || 'N/A' }}
                </span>
              </div>
            </div>

          </div>
        </div>
      </div>

    </div>

    <div class="modal fade" id="confirmationModal" tabindex="-1" aria-labelledby="confirmationModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content rounded-4">
          <div class="modal-header border-0">
            <h5 class="modal-title fw-bold" id="confirmationModalLabel">Confirm Session</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          
          <div class="modal-body border-0 text-center py-4">
            <h5 class="fw-bold mb-1">Rate your session</h5>
            <p class="text-muted mb-4">
              How was your {{ session?.subject }} session with {{ session?.tutor?.name || 'your tutor' }}?
            </p>
            
            <div class="d-flex justify-content-center gap-2 mb-2 text-warning fs-1">
              <i v-for="star in 5" :key="star"
                class="bi transition-all"
                :class="currentRating >= star ? 'bi-star-fill text-warning' : 'bi-star text-muted'"
                @click="currentRating = star"
                style="cursor: pointer; transition: 0.2s;">
              </i>
            </div>
            
            <div class="small text-muted fw-semibold" style="height: 20px;">
              <span v-if="currentRating === 1">Needs Improvement</span>
              <span v-if="currentRating === 2">Fair</span>
              <span v-if="currentRating === 3">Good</span>
              <span v-if="currentRating === 4">Great!</span>
              <span v-if="currentRating === 5">Excellent!</span>
            </div>
          </div>
          
          <div class="modal-footer border-0">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="button" class="btn bg-sb-primary text-white" 
              :disabled="currentRating === 0 || isSubmitting" 
              @click="executeConfirmation">
              <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
              {{ isSubmitting ? 'Submitting...' : 'Submit & Confirm' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showToast" class="position-fixed top-0 start-50 translate-middle-x p-3 mt-4" style="z-index: 1080;">
      <div class="toast show align-items-center text-white bg-success border-0 rounded-3 shadow-lg" role="alert">
        <div class="d-flex p-1 px-2">
          <div class="toast-body fw-semibold fs-6">
            <i class="bi bi-check-circle-fill me-2"></i> Session completed successfully!
          </div>
          <button type="button" class="btn-close btn-close-white me-2 m-auto" @click="showToast = false" aria-label="Close"></button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useSessionsStore } from '@/stores/sessionsStore'
import * as bootstrap from 'bootstrap'

const route = useRoute()
const sessionsStore = useSessionsStore()

const session = ref(null)
const isLoading = ref(true)
const errorMessage = ref('')

const currentRating = ref(0)
const showToast = ref(false)
const isSubmitting = ref(false)

onMounted(async () => {
  const sessionId = route.params.id 
  if (!sessionId) {
    errorMessage.value = "Invalid session ID."
    isLoading.value = false
    return
  }

  try {
    isLoading.value = true
    session.value = await sessionsStore.fetchSessionById(sessionId)
  } catch (error) {
    console.error("Failed to fetch session:", error)
    errorMessage.value = "Failed to load session details. Please try again later."
  } finally {
    isLoading.value = false
  }
})

const prepareConfirmation = () => {
  currentRating.value = 0
}

const executeConfirmation = async () => {
  if (!session.value || currentRating.value === 0) return

  isSubmitting.value = true

  try {
    await sessionsStore.completeSession(session.value.id, currentRating.value)
    
    session.value.status = 'Completed'
    session.value.rating = currentRating.value

    bootstrap.Modal.getInstance(document.getElementById('confirmationModal')).hide()
    showToast.value = true
    
    setTimeout(() => {
      showToast.value = false
    }, 3000)

  } catch (error) {
    console.error("Failed to complete session:", error)
    alert("Failed to submit rating. Please try again.")
  } finally {
    isSubmitting.value = false
  }
}

const isButtonDisabled = computed(() => {
  if (!session.value) return true
  return session.value.status?.toLowerCase() !== 'ongoing'
})

const formatTime = (timeString) => {
  if (!timeString) return 'N/A'
  
  try {
    const [hour, minute] = timeString.split(':')
    const h = parseInt(hour)
    const ampm = h >= 12 ? 'PM' : 'AM'
    const formattedHour = h % 12 || 12
    return `${formattedHour}:${minute} ${ampm}`
  } catch (e) {
    return timeString 
  }
}
</script>

<style scoped>
.card {
  border-radius: 12px;
}
.card-body {
  padding: 1.5rem;
}
</style>