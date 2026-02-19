<template>
  <div class="min-vh-100 d-flex align-items-center justify-content-center py-5">
    <div class="card border-sb shadow-sm rounded-4" style="max-width: 450px; width: 100%;">
      <div class="card-body p-4 p-md-5">
        
        <div class="text-center mb-4">
          <div class="d-inline-flex align-items-center justify-content-center bg-success bg-opacity-10 rounded-3 mb-3" style="width: 48px; height: 48px;">
            <i class="bi bi-book text-sb-primary fs-4"></i>
          </div>
          <h3 class="fw-bold text-dark">Create Account</h3>
          <p class="text-muted small">Join the StudyBuddy tutoring network</p>
        </div>

        <form @submit.prevent="handleRegister">
          <div class="mb-3">
            <label class="form-label fw-semibold small text-dark">Full Name</label>
            <div class="input-group">
              <span class="input-group-text bg-white border-end-0 text-muted">
                <i class="bi bi-person"></i>
              </span>
              <input type="text" class="form-control border-start-0 ps-0 shadow-none" placeholder="Juan Dela Cruz" required>
            </div>
          </div>

          <div class="mb-3">
            <label class="form-label fw-semibold small text-dark">University Email</label>
            <div class="input-group">
              <span class="input-group-text bg-white border-end-0 text-muted">
                <i class="bi bi-envelope"></i>
              </span>
              <input type="email" class="form-control border-start-0 ps-0 shadow-none" placeholder="you@university.edu" required>
            </div>
          </div>

          <div class="mb-3">
            <label class="form-label fw-semibold small text-dark">Password</label>
            <div class="input-group">
              <span class="input-group-text bg-white border-end-0 text-muted">
                <i class="bi bi-lock"></i>
              </span>
              <input type="password" class="form-control border-start-0 ps-0 shadow-none" placeholder="••••••••" required>
            </div>
          </div>

          <div class="mb-4">
            <label class="form-label fw-semibold small text-dark">I want to</label>
            <select class="form-select shadow-none" required>
              <option value="" disabled selected>Select your role</option>
              <option value="tutee">Find a Tutor (Student)</option>
              <option value="tutor">Become a Tutor</option>
            </select>
          </div>

          <button type="submit" class="btn bg-sb-primary text-white w-100 py-2 rounded-3 fw-semibold shadow-sm d-flex justify-content-center align-items-center gap-2">
            Create Account <i class="bi bi-arrow-right"></i>
          </button>
        </form>

        <div class="text-center mt-4">
          <p class="text-muted small mb-0">
            Already have an account? 
            <router-link to="/login" class="text-sb-primary fw-bold text-decoration-none">Sign in</router-link>
          </p>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const handleRegister = () => {
  // Logic to save user to database will go here later
  // For now, immediately push them into the dashboard to simulate logging in
  router.push('/preferencesetup')
}
</script>

<style scoped>
/* Styling to ensure inputs match your exact mockup */
.form-control, .form-select, .input-group-text {
  border-color: var(--sb-card-border);
}
.form-control:focus, .form-select:focus {
  border-color: var(--sb-primary);
  box-shadow: 0 0 0 0.25rem rgba(0, 137, 90, 0.25);
}
.input-group:focus-within .input-group-text {
  border-color: var(--sb-primary);
}
</style>