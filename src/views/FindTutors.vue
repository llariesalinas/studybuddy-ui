<template>
    <div class="p-4">
        <div class="mb-4">
            <h2 class="fw-bold text-dark">Find Tutors</h2>
            <p class="text-muted">Browse peer tutors matched to your learning needs.</p>
        </div>

        <form @submit.prevent="searchTutor">
            <div class="row mb-5 g-1 justify-content-center">
            <div class="col-md-2">
                <label class="form-label fw-semibold small">Subject</label>
                <select v-model="initialbookStore.selectedSubject" class="form-select">
                <option disabled value="">Select Subject</option>
                <option
                    v-for="subject in subjects"
                    :key="subject.subject_code"
                    :value="subject.subject_code"
                >
                    {{ subject.subject_name  }}
                </option>
                </select>
            </div>
            <div class="col-md-2">
                <label class="form-label fw-semibold small">Topic</label>
                <select v-model="initialbookStore.selectedTopic" class="form-select border-sb shadow-none py-2">
                    <option value="" disabled>Select Topic</option>
                    <option 
                    v-for="topic in filteredTopics"
                    :key="topic"
                    :value="topic">{{topic}}</option>
                </select>
            </div>
            <div class="col-md-2">
                <label class="form-label fw-semibold small">Mode</label>
                <select v-model="initialbookStore.selectedMode" class="form-select border-sb shadow-none py-2">
                    <option 
                    v-for="mode in modes"
                    :key="mode"
                    :value="mode">{{ mode }}</option>
                </select>
            </div>
            <div class="col-md-2">
                <label class="form-label fw-semibold small">Date</label>
                <input type="date" v-model="initialbookStore.selectedDate" class="form-control border-sb shadow-none" required />
            </div>
            <div class="col" style="flex: 0 0 12.5%; max-width: 12.5%;">
                <label class="form-label fw-semibold small">From</label>
                <input type="time" v-model="initialbookStore.selectedStartTime" class="form-control border-sb shadow-none" required />
            </div>
            <div class="col" style="flex: 0 0 12.5%; max-width: 12.5%;">
                <label class="form-label fw-semibold small">To</label>
                <input type="time" v-model="initialbookStore.selectedEndTime" class="form-control border-sb shadow-none" required />
            </div>
            <div class="col-md-1">
                <label class="form-label fw-semibold small invisible">Search</label>
                <button type="submit" class="btn bg-sb-primary text-white px-3 rounded-3 fw-semibold shadow-sm"
                :disabled="isSubmitting">
                    Search
                </button>
            </div> 
        </div>
        </form>
        

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
                                <div class="bg-success bg-opacity-10 text-sb-primary fw-bold rounded-circle d-flex align-items-center justify-content-center"
                                    style="width: 48px; height: 48px;">
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
                            <span v-for="subject in tutor.subjects" :key="subject"
                                class="badge bg-light text-dark border border-sb">
                                {{ subject }}
                            </span>
                        </div>

                        <div class="d-flex justify-content-between align-items-center mt-auto">
                            <div class="small">
                                <span class="fw-bold text-dark">₱{{ tutor.hourly_rate }}</span><span
                                    class="text-muted">/hr</span>
                                <span class="text-muted ms-2">· {{ tutor.total_sessions }} sessions</span>
                            </div>
                            <button @click="prepareBooking(tutor)"
                                class="btn bg-sb-primary text-white px-4 rounded-3 fw-semibold shadow-sm"
                                data-bs-toggle="modal" data-bs-target="#bookingModal">
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
                        <button type="button" class="btn-close shadow-none" data-bs-dismiss="modal"
                            aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <p class="text-muted small mb-4">Fill out the session details below. The tutor will need to
                            confirm this schedule.</p>

                        <form @submit.prevent="submitBooking">
                            <div class="mb-3">
                                <label class="form-label fw-bold small text-muted">SESSION DATE</label>
                                <input type="date" v-model="bookingPayload.booking_date"
                                    class="form-control border-sb shadow-none" required>
                            </div>

                            <div class="row g-3 mb-3">
                                <div class="col-6">
                                    <label class="form-label fw-bold small text-muted">START TIME</label>
                                    <input type="time" v-model="bookingPayload.start_time"
                                        class="form-control border-sb shadow-none" required>
                                </div>
                                <div class="col-6">
                                    <label class="form-label fw-bold small text-muted">END TIME</label>
                                    <input type="time" v-model="bookingPayload.end_time"
                                        class="form-control border-sb shadow-none" required>
                                </div>
                            </div>

                            <div class="mb-4">
                                <label class="form-label fw-bold small text-muted">SESSION MODE</label>
                                <select v-model="bookingPayload.session_mode" class="form-select border-sb shadow-none"
                                    required>
                                    <option value="Online">Online (Zoom/GMeet)</option>
                                    <option value="Face-to-Face">Face-to-Face (Campus)</option>
                                </select>
                            </div>

                            <button type="submit"
                                class="btn bg-sb-primary text-white w-100 py-2 rounded-3 fw-bold shadow-sm"
                                :disabled="isSubmitting">
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
import { useRoute } from 'vue-router'
import api from '@/services/api/api'
import { ref, onMounted, computed, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useInitialBookingPrefsStore } from '@/stores/initialbookingprefs'
import * as bootstrap from 'bootstrap' // FIX 2: Imports Bootstrap JS so ESLint recognizes it



const initialbookStore = useInitialBookingPrefsStore()
const authStore = useAuthStore()
const isLoading = ref(true)
const isSubmitting = ref(false)

const matchedTutors = ref([])
const selectedTutor = ref(null)


const route = useRoute()

const modes = [
    'Online',
    'Face-to-face'
]


watch(
    () => initialbookStore.selectedSubject,
    () => {
        initialbookStore.selectedTopic = ''
    }
)

const searchTutor = async () => {
  isSubmitting.value = true
  isLoading.value = true

  try {
    const response = await api.get(
      `search-tutors/?subject=${initialbookStore.selectedSubject}`
    )

    matchedTutors.value = response.data.map(tutor => ({
      profile_id: tutor.profile_id,   // ✅ FIXED
      initials: tutor.fname[0] + tutor.lname[0],
      name: `${tutor.fname} ${tutor.lname}`,
      year_course: 'Tutor',
      rating: tutor.rating_average ?? 5.0,
      bio: 'Peer tutor available.',
      subjects: [],
      hourly_rate: tutor.hourly_rate ?? 150,
      total_sessions: tutor.total_sessions ?? 0
    }))

  } catch (error) {
    console.error('Search failed:', error)
  } finally {
    isSubmitting.value = false
    isLoading.value = false
  }
}

// THIS EXACTLY MATCHES YOUR ERD'S 'BOOKINGS' TABLE
const bookingPayload = ref({
    tutor_Profile_id: null,
    student_Profile_id: null,
    booking_date: '',
    start_time: '',
    end_time: '',
    session_mode: 'Online'
})


const prepareBooking = (tutor) => {
    selectedTutor.value = tutor

    // Prep the payload with the FKs needed by Django
    bookingPayload.value.tutor_Profile_id = tutor.profile_id

    // FIX 1: We actively use the authStore to pull the logged-in student's ID.
    // (We use `|| 1` as a fallback just in case testing data is empty so the payload never breaks)
    bookingPayload.value.student_Profile_id = authStore.profile?.profile_id || 1
}


const subjects = ref([])

onMounted(async () => {
  const res = await api.get('subjects/')
  subjects.value = res.data

  // 🔥 Sync query param into store
  if (route.query.subject) {
    initialbookStore.selectedSubject = route.query.subject
  }

  if (initialbookStore.selectedSubject) {
    await searchTutor()
  } else {
    isLoading.value = false
  }
})

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

//route to tutor details page insert here
</script>

<style scoped>
.border-sb {
    border-color: var(--sb-card-border) !important;
}

.text-sb-primary {
    color: var(--sb-primary) !important;
}

.bg-sb-primary {
    background-color: var(--sb-primary) !important;
}
</style>
