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
                    <option value="Elementary">Elementary</option>
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

                <div class="mb-5">
                  <label class="form-label fw-bold small text-muted">HOURLY RATE (PHP)</label>
                  <input type="number" v-model="form.hourly_rate" class="form-control border-sb shadow-none" placeholder="₱ 0.00" required>
                </div>

                <button type="submit" class="btn bg-sb-primary text-white w-100 py-3 rounded-3 fw-bold shadow-sm sb-btn">
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
import { useProfileStore } from '@/stores/profile'
import { useToastStore } from '@/stores/toast'
import api from '@/services/api/api'

const router = useRouter()
const profileStore = useProfileStore()
const toastStore = useToastStore()

const form = ref({
  teaching_level: '',
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
    toastStore.push("Could not save tutor profile.", 'error')

  }

}
</script>
