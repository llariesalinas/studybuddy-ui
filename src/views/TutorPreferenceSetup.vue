<template>
  <div class="min-vh-100 bg-light py-5">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-md-7 col-lg-6">
          <div class="card border-0 shadow-sm rounded-4">
            <div class="card-body p-4 p-md-5">
              <div class="text-center mb-4">
                <h3 class="fw-bold text-dark">Tutor Profile Setup</h3>
                <p class="text-muted">Set your teaching preferences to start matching.</p>
              </div>

              <form @submit.prevent="handleCompleteSetup">
                <div class="mb-4">
                  <label class="form-label fw-bold small text-muted">TEACHING LEVEL</label>
                  <select v-model="form.teaching_level" class="form-select border-sb shadow-none" required>
                    <option value="" disabled>Select level</option>
                    <option value="High School">High School</option>
                    <option value="College">College</option>
                  </select>
                </div>

                <div class="mb-4">
                  <label class="form-label fw-bold small text-muted d-block">MODALITY</label>
                  <div class="form-check form-switch mb-2">
                    <input class="form-check-input" type="checkbox" v-model="form.can_online" id="on">
                    <label class="form-check-label" for="on">Online Sessions</label>
                  </div>
                  <div class="form-check form-switch">
                    <input class="form-check-input" type="checkbox" v-model="form.can_f2f" id="f2f">
                    <label class="form-check-label" for="f2f">Face-to-Face Sessions</label>
                  </div>
                </div>

                <!-- SUBJECTS SECTION -->
                <div class="mb-4">
                  <label class="form-label fw-bold small text-muted d-block">
                    SUBJECTS YOU CAN TEACH
                  </label>

                  <!-- Add Subject Input -->
                  <div class="d-flex gap-2 mb-3">
                    <input
                      type="text"
                      v-model="newSubject"
                      class="form-control border-sb shadow-none"
                      placeholder="Enter subject (e.g., Calculus)"
                      @keyup.enter="addSubject"
                    />
                    <button
                      type="button"
                      class="btn btn-outline-dark fw-semibold"
                      @click="addSubject"
                    >
                      Add
                    </button>
                  </div>

                  <div v-if="form.subjects.length" class="d-flex flex-wrap gap-2">
                    <span
                      v-for="(subject, index) in form.subjects"
                      :key="index"
                      class="badge bg-sb-primary text-white px-3 py-2 rounded-pill d-flex align-items-center gap-2"
                    >
                      {{ subject }}
                      <button
                        type="button"
                        class="btn-close btn-close-white btn-sm"
                        @click="removeSubject(index)"
                      ></button>
                    </span>
                  </div>

                  <p v-else class="text-muted small mb-0">
                    No subjects added yet.
                  </p>
                </div>

                <div class="mb-5">
                  <label class="form-label fw-bold small text-muted">HOURLY RATE (PHP)</label>
                  <input type="number" v-model="form.hourly_rate" class="form-control border-sb shadow-none" placeholder="₱ 0.00" required>
                </div>

                <button type="submit" class="btn bg-sb-primary text-white w-100 py-3 rounded-3 fw-bold shadow-sm">
                  Complete Profile
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
<<<<<<< HEAD
import { useProfileStore } from '@/stores/profile'
=======
>>>>>>> origin/main
import api from '@/services/api/api'

const router = useRouter()
const profileStore = useProfileStore()

const newSubject = ref('')

const form = ref({
  teaching_level: '',
<<<<<<< HEAD
  can_online: true,
  can_f2f: false,
  hourly_rate: null
})


/* LOAD EXISTING TUTOR DATA */
onMounted(async () => {

  try {

    const response = await api.get('/tutor-dashboard/')

    const tutor = response.data

    form.value.teaching_level = tutor.teaching_level
    form.value.can_online = tutor.can_online
    form.value.can_f2f = tutor.can_f2f
    form.value.hourly_rate = tutor.hourly_rate

  } catch (error) {

    console.log("New tutor setup")

  }

})


/* SUBMIT PROFILE SETUP */
const handleCompleteSetup = async () => {

  try {

    await api.post('/tutor/setup/', form.value)

    // update profile guard state
    profileStore.profileCompleted = true

    router.push({ name: 'tch-dashboard' })

  } catch (error) {

    console.error("Failed to save tutor profile", error)
    alert("Could not save tutor profile.")

=======
  subjects: [],
  can_Online: true,
  can_F2F: false,
  hourly_rate: null
})

const addSubject = () => {
  const subject = newSubject.value.trim()

  if (!subject) return

  if (!form.value.subjects.includes(subject)) {
    form.value.subjects.push(subject)
  }

  newSubject.value = ''
}

const removeSubject = (index) => {
  form.value.subjects.splice(index, 1)
}

const handleCompleteSetup = async() => {
  if (form.subjects.value.length === 0){
    alert('Please add at least one subject.')
    return
  }

  // API_INTEGRATION_POINT: Ry & Nick -> POST /api/v1/tutors/
  try {
    await api.post('/tutorPrefs', form.value)

    console.log('Preferences saved successfully')
    router.push('/tch-dashboard')
  } catch (error) {
    console.error('Failed to save preferences', error)
>>>>>>> origin/main
  }

}
</script>