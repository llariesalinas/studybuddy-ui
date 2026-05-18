<template>
  <AuthShell>
    <template #icon>
      <i class="bi bi-box-arrow-in-right"></i>
    </template>
    <template #title>Welcome Back</template>
    <template #subtitle>Log in to your StudyBuddy account</template>

    <div v-if="loginError" class="sb-auth-alert">{{ loginError }}</div>

    <form @submit.prevent="handleLogin">
      <div class="sb-auth-field">
        <label class="sb-auth-label">University Email</label>
        <input
          type="email"
          v-model="email"
          class="sb-auth-input"
          placeholder="you@university.edu"
          required
        />
      </div>

      <div class="sb-auth-field">
        <div class="sb-auth-label-row">
          <label class="sb-auth-label">Password</label>
          <a href="#" class="sb-auth-link sb-auth-link-sm">Forgot?</a>
        </div>
        <input
          type="password"
          v-model="password"
          class="sb-auth-input"
          placeholder="••••••••"
          required
        />
      </div>

      <button type="submit" class="sb-btn-pill sb-auth-submit" :disabled="isSubmitting">
        <span v-if="isSubmitting" class="sb-spinner" aria-hidden="true"></span>
        {{ isSubmitting ? 'Signing In...' : 'Sign In' }}
      </button>
    </form>

    <p class="sb-auth-footer-text">
      No account?
      <router-link to="/register" class="sb-auth-link">Create one</router-link>
    </p>
  </AuthShell>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import AuthShell from '@/components/AuthShell.vue'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const isSubmitting = ref(false)
const loginError = ref('')

const handleLogin = async () => {
  isSubmitting.value = true
  loginError.value = ''

  try {
    const role = await authStore.login({ email: email.value, password: password.value })
    const normalizedRole = role?.toLowerCase()

    if (normalizedRole === 'tutor') router.push('/tch-dashboard')
    else if (normalizedRole === 'tutee') router.push('/dashboard')
    else if (normalizedRole === 'admin') router.push('/admin/dashboard')
    else router.push('/')
  } catch (error) {
    loginError.value = error.response?.data?.error || 'Login failed. Please check your credentials.'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped>
.sb-auth-field {
  margin-bottom: 16px;
}

.sb-auth-label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: #1d1d1f;
  margin-bottom: 6px;
}

.sb-auth-label-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.sb-auth-label-row .sb-auth-label {
  margin-bottom: 0;
}

.sb-auth-input {
  width: 100%;
  padding: 10px 14px;
  font-size: 14px;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  background: #fff;
  color: #1d1d1f;
  outline: none;
  transition:
    border-color 0.15s ease,
    box-shadow 0.15s ease;
}

.sb-auth-input:focus {
  border-color: #00895a;
  box-shadow: 0 0 0 3px rgba(0, 137, 90, 0.12);
}

.sb-auth-alert {
  background: #fff5f5;
  border: 1px solid #fecaca;
  color: #b91c1c;
  border-radius: 10px;
  padding: 10px 14px;
  font-size: 13px;
  margin-bottom: 18px;
}

.sb-btn-pill {
  background: #00895a;
  color: #fff;
  padding: 11px 28px;
  border-radius: 9999px;
  font-size: 14px;
  font-weight: 500;
  border: none;
  cursor: pointer;
  transition:
    background 0.15s ease,
    transform 0.15s ease;
}

.sb-btn-pill:hover:not(:disabled) {
  background: #00704a;
}

.sb-btn-pill:active:not(:disabled) {
  transform: scale(0.95);
}

.sb-btn-pill:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.sb-auth-submit {
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
  margin-bottom: 20px;
}

.sb-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.35);
  border-top-color: #fff;
  border-radius: 50%;
  animation: sb-spin 0.7s linear infinite;
  flex-shrink: 0;
}

@keyframes sb-spin {
  to {
    transform: rotate(360deg);
  }
}

.sb-auth-link {
  color: #00895a;
  font-weight: 600;
  text-decoration: none;
}

.sb-auth-link:hover {
  text-decoration: underline;
}

.sb-auth-link-sm {
  font-size: 13px;
  font-weight: 500;
}

.sb-auth-footer-text {
  text-align: center;
  font-size: 13px;
  color: #6e6e73;
  margin: 0;
}
</style>
