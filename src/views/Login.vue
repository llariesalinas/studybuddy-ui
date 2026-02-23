<template>
  <div class="min-vh-100 d-flex align-items-center justify-content-center py-5">
    <div class="card border-sb shadow-sm rounded-4" style="max-width: 400px; width: 100%">
      <div class="card-body p-4 p-md-5">
        <div class="text-center mb-4">
          <div
            class="d-inline-flex align-items-center justify-content-center bg-success bg-opacity-10 rounded-3 mb-3"
            style="width: 48px; height: 48px"
          >
            <i class="bi bi-box-arrow-in-right text-sb-primary fs-4"></i>
          </div>
          <h3 class="fw-bold text-dark">Welcome Back</h3>
          <p class="text-muted small">Log in to your StudyBuddy account</p>
        </div>

        <form @submit.prevent="handleLogin">
          <div class="mb-3">
            <label class="form-label fw-semibold small text-dark">University Email</label>
            <input
              type="email"
              v-model="email"
              class="form-control shadow-none"
              placeholder="you@university.edu"
              required
            />
          </div>

          <div class="mb-4">
            <div class="d-flex justify-content-between align-items-center">
              <label class="form-label fw-semibold small text-dark mb-0">Password</label>
              <a href="#" class="text-sb-primary small text-decoration-none fw-semibold">Forgot?</a>
            </div>
            <input
              type="password"
              v-model="password"
              class="form-control shadow-none mt-2"
              placeholder="••••••••"
              required
            />
          </div>

          <button
            type="submit"
            class="btn bg-sb-primary text-white w-100 py-2 rounded-3 fw-semibold shadow-sm d-flex justify-content-center align-items-center gap-2"
            :disabled="isSubmitting"
          >
            <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-2"></span>
            {{ isSubmitting ? 'Signing In...' : 'Sign In' }}
          </button>
        </form>

        <div class="text-center mt-4">
          <p class="text-muted small mb-0">
            No account?
            <router-link to="/register" class="text-sb-primary fw-bold text-decoration-none">
              Create one
            </router-link>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const isSubmitting = ref(false)

const handleLogin = async () => {
  isSubmitting.value = true

  try {
    // API_INTEGRATION_POINT: The actual axios call is delegated to the store
    await authStore.login({
      email: email.value,
      password: password.value
    })

    console.log('Login successful')

    // Route to dashboard on success
    router.push('/dashboard')

  } catch (error) {
    console.error('Login Error:', error)
    alert('Login failed. Please check your credentials.')
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped>
.form-control {
  border-color: var(--sb-card-border);
}
.form-control:focus {
  border-color: var(--sb-primary);
  box-shadow: 0 0 0 0.25rem rgba(0, 137, 90, 0.25);
}
</style>
