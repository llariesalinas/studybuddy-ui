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
              <div v-if="emailError" class="text-danger small mt-1">{{ emailError }}</div>
            </div>
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
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useRegistrationInfoStore } from '@/stores/registrationinfo'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'

const router = useRouter()
const store = useRegistrationInfoStore()
const authStore = useAuthStore()

const isSubmitting = ref(false)

const generalError = ref('')
const emailError = ref('')

const handleRegister = async () => {

  generalError.value = ''
  emailError.value = ''

  // 🔹 Basic validation
  if (!store.newUserFname ||
      !store.newUserLname ||
      !store.newUserEmail ||
      !store.newUserPassword) {

    generalError.value = "Please fill in all required fields."
    return
  }

  // 🔹 Role validation
  if (!store.newUserType) {
    generalError.value = "Please select your role."
    return
  }

  isSubmitting.value = true

  try {

    const role = store.newUserType

    // 🔹 REGISTER USER
    await axios.post('http://localhost:8000/api/register/', {
      fname: store.newUserFname,
      mname: store.newUserMname,
      lname: store.newUserLname,
      email: store.newUserEmail,
      password: store.newUserPassword,
      role: role
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

      if (data.email) {
        emailError.value = data.email[0]
      }

      else if (data.detail) {
        generalError.value = data.detail
      }

      else {
        generalError.value = "Registration failed. Please try again."
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
</script>