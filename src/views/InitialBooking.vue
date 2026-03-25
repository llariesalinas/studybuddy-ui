<template>
  <div class="initial-booking-content">
    <div class="mb-4">
      <h2 class="fw-bold text-dark">Book a Session</h2>
      <p class="text-muted">
        Tell us what you need help with, and we'll match you with the right tutor.
      </p>
    </div>

    <div class="card border-sb shadow-sm rounded-4" style="max-width: 600px;">
      <div class="card-body p-4 p-md-5">
        <form @submit.prevent="findTutor">

          <div class="mb-3">
            <label class="form-label fw-semibold small">Subject</label>
            <select v-model="store.selectedSubject" class="form-select border-sb shadow-none" required>
              <option v-for="subject in subjects" :key="subject.subject_code" :value="subject.subject_code">
                {{ subject.subject_name }}
              </option>
            </select>
          </div>

          <div class="mb-3">
            <label class="form-label fw-semibold small">Specific Topic</label>
            <input
              type="text"
              v-model="store.selectedTopic"
              class="form-control border-sb shadow-none"
              placeholder="e.g., Calculus, Thermodynamics"
              required
            />
          </div>

          <div class="row g-3 mb-3">
            <div class="col-md-6">
              <label class="form-label fw-semibold small">Date</label>
              <input
                type="date"
                v-model="store.selectedDate"
                class="form-control border-sb shadow-none"
                required
              />
            </div>

            <div class="col-md-6">
              <label class="form-label fw-semibold small">Preferred Mode</label>
              <select v-model="store.selectedMode" class="form-select border-sb shadow-none" required>
                <option v-for="mode in modes" :key="mode" :value="mode">
                  {{ mode }}
                </option>
              </select>
            </div>
          </div>

          <div class="row g-3 mb-4">
            <div class="col-6">
              <label class="form-label fw-semibold small">Time From</label>
              <input
                type="time"
                v-model="store.selectedStartTime"
                class="form-control border-sb shadow-none"
                required
              />
            </div>

            <div class="col-6">
              <label class="form-label fw-semibold small">Time To</label>
              <input
                type="time"
                v-model="store.selectedEndTime"
                class="form-control border-sb shadow-none"
                required
              />
            </div>
          </div>

          <div class="text-end mt-4">
            <button
              type="submit"
              class="btn bg-sb-primary text-white px-5 py-2 rounded-3 fw-semibold shadow-sm d-inline-flex justify-content-center align-items-center gap-2"
              :disabled="isSubmitting"
            >
              <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-2"></span>
              {{ isSubmitting ? 'Searching...' : 'Find Tutor' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useInitialBookingPrefsStore } from '@/stores/initialbookingprefs'
import api from '@/services/api/api'

const router = useRouter()
const store = useInitialBookingPrefsStore()

const isSubmitting = ref(false)
const subjects = ref([])
const tutors = ref([])

const modes = ['Online', 'Face-to-face']


// Load subjects from backend
onMounted(async () => {

  try {

    const response = await api.get('/subjects/')
    subjects.value = response.data

  } catch (error) {

    console.error("Failed to load subjects", error)

  }

})


// FIND TUTOR (CBF CALL)
const findTutor = async () => {

  isSubmitting.value = true

  try {

    const res = await api.post('/recommend-tutors/', {

      subject: store.selectedSubject,
      topic: store.selectedTopic,
      preferred_mode: store.selectedMode,
      date: store.selectedDate,
      start_time: store.selectedStartTime,
      end_time: store.selectedEndTime

    })

    tutors.value = res.data

    console.log("Recommended tutors:", tutors.value)

    // navigate to tutors page
    router.push({ name: 'tutors' })

  } catch (err) {

    console.error("Tutor recommendation failed", err)

  } finally {

    isSubmitting.value = false

  }

}
</script>