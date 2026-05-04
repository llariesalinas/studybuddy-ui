<template>
  <div class="min-vh-100 d-flex align-items-center justify-content-center py-5">
    <div class="card border-sb shadow-sm rounded-4" style="max-width: 450px; width: 100%;">
      <div class="card-body p-4 p-md-5">
        <div class="text-center mb-4">
          <div class="d-inline-flex align-items-center justify-content-center bg-success bg-opacity-10 rounded-3 mb-3" style="width: 48px; height: 48px;">
            <i class="bi bi-book text-sb-primary fs-4"></i>
          </div>
          <h3 class="fw-bold text-dark">Create Account</h3>
          <p class="text-muted small">Join the StudyBuddy network</p>
        </div>

        <div v-if="generalError" class="alert alert-danger">
          {{ generalError }}
        </div>

        <form @submit.prevent="handleRegister">
          <div class="mb-3">
            <label class="form-label fw-semibold small text-dark">First Name</label>
            <div class="input-group">
              <span class="input-group-text bg-white border-end-0 text-muted"><i class="bi bi-person"></i></span>
              <input type="text" v-model="store.newUserFname" class="form-control border-start-0 ps-0 shadow-none" placeholder="Juan Dela Cruz" required>
            </div>
          </div>

          <div class="mb-3">
            <label class="form-label fw-semibold small text-dark">Middle Name</label>
            <div class="input-group">
              <span class="input-group-text bg-white border-end-0 text-muted"><i class="bi bi-person"></i></span>
              <input type="text" v-model="store.newUserMname" class="form-control border-start-0 ps-0 shadow-none" placeholder="Juan Dela Cruz" required>
            </div>
          </div>

          <div class="mb-3">
            <label class="form-label fw-semibold small text-dark">Last Name</label>
            <div class="input-group">
              <span class="input-group-text bg-white border-end-0 text-muted"><i class="bi bi-person"></i></span>
              <input type="text" v-model="store.newUserLname" class="form-control border-start-0 ps-0 shadow-none" placeholder="Juan Dela Cruz" required>
            </div>
          </div>

          <div class="mb-3">
            <label class="form-label fw-semibold small text-dark">University Email</label>
            <div class="input-group">
              <span class="input-group-text bg-white border-end-0 text-muted"><i class="bi bi-envelope"></i></span>
              <input type="email" v-model="store.newUserEmail" class="form-control border-start-0 ps-0 shadow-none" placeholder="you@university.edu" required>
            </div>
            <div v-if="emailError" class="text-danger small mt-1">{{ emailError }}</div>
          </div>

          <div class="mb-3">
            <label class="form-label fw-semibold small text-dark">Institution</label>
            <select v-model="store.selectedInstitutionId" class="form-select shadow-none" required>
              <option value="" disabled>Select your institution</option>
              <option
                v-for="institution in institutions"
                :key="institution.id"
                :value="String(institution.id)"
              >
                {{ institution.institution_name }} ({{ institution.school_email_domain }})
              </option>
            </select>
            <div v-if="selectedInstitutionDomain" class="form-text small">
              Allowed email domain: {{ selectedInstitutionDomain }}
            </div>
            <div v-if="institutionError" class="text-danger small mt-1">{{ institutionError }}</div>
          </div>

          <div class="mb-3">
            <label class="form-label fw-semibold small text-dark">Password</label>
            <div class="input-group">
              <span class="input-group-text bg-white border-end-0 text-muted"><i class="bi bi-lock"></i></span>
              <input type="password" v-model="store.newUserPassword" class="form-control border-start-0 ps-0 shadow-none" placeholder="••••••••" required>
            </div>
          </div>

          <div class="mb-4">
            <label class="form-label fw-semibold small text-dark">I want to</label>
            <select v-model="store.newUserType" class="form-select shadow-none" required>
              <option value="" disabled selected>Select your role</option>
              <option value="Tutee">Find a Tutor (Student)</option>
              <option value="Tutor">Become a Tutor</option>
            </select>
          </div>

          <button type="submit" class="btn bg-sb-primary text-white w-100 py-2 rounded-3 fw-semibold shadow-sm d-flex justify-content-center align-items-center gap-2" :disabled="isSubmitting">
            <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-2"></span>
            {{ isSubmitting ? 'Processing...' : 'Create Account' }}
            <i v-if="!isSubmitting" class="bi bi-arrow-right"></i>
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useRegistrationInfoStore } from '@/stores/registrationinfo'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/'
const router = useRouter()
const store = useRegistrationInfoStore()
const authStore = useAuthStore()

const isSubmitting = ref(false)
const institutions = ref([])

const generalError = ref('')
const emailError = ref('')
const institutionError = ref('')

const selectedInstitution = computed(() => {
  return institutions.value.find(
    (institution) => String(institution.id) === String(store.selectedInstitutionId)
  ) || null
})

const selectedInstitutionDomain = computed(() => {
  return selectedInstitution.value?.school_email_domain || ''
})

const emailDomainMatchesInstitution = computed(() => {
  if (!store.newUserEmail || !selectedInstitutionDomain.value) {
    return true
  }

  const parts = store.newUserEmail.split('@')

  if (parts.length !== 2) {
    return false
  }

  return parts[1].trim().toLowerCase() === selectedInstitutionDomain.value.toLowerCase()
})

const loadInstitutions = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}partner-institutions/`)
    institutions.value = response.data
  } catch (error) {
    console.error('Failed to load partner institutions:', error)
    generalError.value = 'Unable to load partner institutions right now. Please try again later.'
  }
}

const handleRegister = async () => {

  generalError.value = ''
  emailError.value = ''
  institutionError.value = ''

  // 🔹 Basic validation
  if (!store.newUserFname ||
      !store.newUserLname ||
      !store.newUserEmail ||
      !store.newUserPassword ||
      !store.selectedInstitutionId) {

    generalError.value = "Please fill in all required fields."
    return
  }

  // 🔹 Role validation
  if (!store.newUserType) {
    generalError.value = "Please select your role."
    return
  }

  if (!emailDomainMatchesInstitution.value) {
    institutionError.value = 'Your email domain does not match the selected institution. Please check and try again.'
    return
  }

  isSubmitting.value = true

  try {

    const role = store.newUserType

    // 🔹 REGISTER USER
    await axios.post(`${API_BASE_URL}register/`, {
      fname: store.newUserFname,
      mname: store.newUserMname,
      lname: store.newUserLname,
      email: store.newUserEmail,
      password: store.newUserPassword,
      role: role,
      institution_id: store.selectedInstitutionId
    })

    // 🔹 AUTO LOGIN
    await authStore.login({
      email: store.newUserEmail,
      password: store.newUserPassword
    })

    // 🔹 ROLE BASED REDIRECT
    if (role === 'Tutor') {
      router.push('/tutor-setup')
    } else {
      router.push('/preferencesetup')
    }

  } catch (error) {

    console.error('Registration Error:', error)

    if (error.response) {

      const data = error.response.data

      const message = data.error || data.detail || "Registration failed. Please try again."

      if (message.toLowerCase().includes('email')) {
        emailError.value = message
      } else if (message.toLowerCase().includes('institution')) {
        institutionError.value = message
      } else {
        generalError.value = message
      }

    }

    else if (error.request) {
      generalError.value = "Server not responding. Please try again later."
    }

    else {
      generalError.value = "An unexpected error occurred."
    }

  } finally {
    isSubmitting.value = false
  }
}

onMounted(() => {
  loadInstitutions()
})
</script>
