<template>
  <div class="p-4">
    <div class="mb-4">
      <h2 class="fw-bold text-dark">Find Tutors</h2>
      <p class="text-muted">Browse peer tutors matched to your learning needs.</p>
    </div>

    <div class="row mb-5 g-3">
      <div class="col-md-9">
        <div class="input-group">
          <span class="input-group-text bg-white border-sb border-end-0">
            <i class="bi bi-search text-muted"></i>
          </span>
          <input type="text" class="form-control border-sb border-start-0 shadow-none py-2" placeholder="Search by name or subject...">
        </div>
      </div>
      <div class="col-md-3">
        <select class="form-select border-sb shadow-none py-2">
          <option value="">All Subjects</option>
          <option value="Math">Mathematics</option>
          <option value="Programming">Programming</option>
        </select>
      </div>
    </div>

    <div v-if="isLoading" class="text-center py-5">
      <div class="spinner-border text-sb-primary" role="status"></div>
      <p class="text-muted mt-2">Running matching algorithm...</p>
    </div>

    <div v-else class="row g-4">
      <div class="col-md-6" v-for="tutor in matchedTutors" :key="tutor.profile_id">
        <div class="card border-sb shadow-sm rounded-4 h-100">
          <div class="card-body p-4">
            <div class="d-flex justify-content-between align-items-start mb-3">
              <div class="d-flex align-items-center gap-3">
                <div class="bg-success bg-opacity-10 text-sb-primary fw-bold rounded-circle d-flex align-items-center justify-content-center" style="width: 48px; height: 48px;">
                  {{ tutor.initials }}
                </div>
                <div>
                  <h6 class="fw-bold mb-0 text-dark">{{ tutor.name }}</h6>
                  <p class="text-muted small mb-0">{{ tutor.year_course }}</p>
                </div>
              </div>
              <div class="text-end">
                <span class="fw-bold text-warning d-flex align-items-center">
                  <i class="bi bi-star-fill me-1"></i> {{ tutor.rating }}
                </span>
              </div>
            </div>

            <p class="small text-dark mb-3">{{ tutor.bio }}</p>

            <div class="d-flex gap-2 mb-4 flex-wrap">
              <span v-for="subject in tutor.subjects" :key="subject" class="badge bg-light text-dark border border-sb">
                {{ subject }}
              </span>
            </div>

            <div class="d-flex justify-content-between align-items-center mt-auto">
              <div class="small">
                <span class="fw-bold text-dark">₱{{ tutor.hourly_rate }}</span><span class="text-muted">/hr</span>
                <span class="text-muted ms-2">· {{ tutor.total_sessions }} sessions</span>
              </div>
              <button
                @click="prepareBooking(tutor)"
                class="btn bg-sb-primary text-white px-4 rounded-3 fw-semibold shadow-sm"
                data-bs-toggle="modal"
                data-bs-target="#bookingModal"
              >
                Book Session
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" id="bookingModal" tabindex="-1" aria-labelledby="bookingModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border-0 rounded-4 shadow">
          <div class="modal-header border-bottom-0 pb-0">
            <h5 class="modal-title fw-bold" id="bookingModalLabel">Book {{ selectedTutor?.name }}</h5>
            <button type="button" class="btn-close shadow-none" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <p class="text-muted small mb-4">Fill out the session details below. The tutor will need to confirm this schedule.</p>

            <form @submit.prevent="submitBooking">
              <div class="mb-3">
                <label class="form-label fw-bold small text-muted">SESSION DATE</label>
                <input type="date" v-model="bookingPayload.booking_date" class="form-control border-sb shadow-none" required>
              </div>

              <div class="row g-3 mb-3">
                <div class="col-6">
                  <label class="form-label fw-bold small text-muted">START TIME</label>
                  <input type="time" v-model="bookingPayload.start_time" class="form-control border-sb shadow-none" required>
                </div>
                <div class="col-6">
                  <label class="form-label fw-bold small text-muted">END TIME</label>
                  <input type="time" v-model="bookingPayload.end_time" class="form-control border-sb shadow-none" required>
                </div>
              </div>

              <div class="mb-4">
                <label class="form-label fw-bold small text-muted">SESSION MODE</label>
                <select v-model="bookingPayload.session_mode" class="form-select border-sb shadow-none" required>
                  <option value="Online">Online (Zoom/GMeet)</option>
                  <option value="Face-to-Face">Face-to-Face (Campus)</option>
                </select>
              </div>

              <button type="submit" class="btn bg-sb-primary text-white w-100 py-2 rounded-3 fw-bold shadow-sm" :disabled="isSubmitting">
                <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-2"></span>
                {{ isSubmitting ? 'Sending Request...' : 'Confirm Booking' }}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import * as bootstrap from 'bootstrap' // FIX 2: Imports Bootstrap JS so ESLint recognizes it

const authStore = useAuthStore()
const isLoading = ref(true)
const isSubmitting = ref(false)

const matchedTutors = ref([])
const selectedTutor = ref(null)

// THIS EXACTLY MATCHES YOUR ERD'S 'BOOKINGS' TABLE
const bookingPayload = ref({
  tutor_Profile_id: null,
  student_Profile_id: null,
  booking_date: '',
  start_time: '',
  end_time: '',
  session_mode: 'Online'
})

onMounted(() => {
  // API_INTEGRATION_POINT: GET /api/v1/recommendations/
  setTimeout(() => {
    matchedTutors.value = [
      { profile_id: 101, initials: 'MS', name: 'Maria Santos', year_course: '3rd Year · Mathematics', rating: 4.9, bio: '3rd year Mathematics major passionate about making complex concepts accessible.', subjects: ['Calculus', 'Linear Algebra', 'Statistics'], hourly_rate: 150, total_sessions: 87 },
      { profile_id: 102, initials: 'JR', name: 'James Reyes', year_course: '4th Year · Engineering', rating: 4.7, bio: 'Engineering student who loves breaking down science problems step by step.', subjects: ['Physics', 'Chemistry', 'Thermodynamics'], hourly_rate: 140, total_sessions: 52 }
    ]
    isLoading.value = false
  }, 800)
})

const prepareBooking = (tutor) => {
  selectedTutor.value = tutor

  // Prep the payload with the FKs needed by Django
  bookingPayload.value.tutor_Profile_id = tutor.profile_id

  // FIX 1: We actively use the authStore to pull the logged-in student's ID.
  // (We use `|| 1` as a fallback just in case testing data is empty so the payload never breaks)
  bookingPayload.value.student_Profile_id = authStore.profile?.profile_id || 1
}

const submitBooking = async () => {
  isSubmitting.value = true

  // API_INTEGRATION_POINT: Ry & Nick -> POST /api/v1/bookings/
  console.log("Sending ERD Payload to Django:", bookingPayload.value)

  setTimeout(() => {
    isSubmitting.value = false

    // Close the bootstrap modal programmatically using the imported module
    const modalElement = document.getElementById('bookingModal')
    const modalInstance = bootstrap.Modal.getInstance(modalElement)
    if (modalInstance) {
      modalInstance.hide()
    }

    alert('Booking request sent successfully!')

    // Reset form
    bookingPayload.value = { tutor_Profile_id: null, student_Profile_id: null, booking_date: '', start_time: '', end_time: '', session_mode: 'Online' }
  }, 1000)
}
</script>

<style scoped>
.border-sb { border-color: var(--sb-card-border) !important; }
.text-sb-primary { color: var(--sb-primary) !important; }
.bg-sb-primary { background-color: var(--sb-primary) !important; }
</style>
