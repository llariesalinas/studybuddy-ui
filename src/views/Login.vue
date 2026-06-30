<template>
  <AuthShell>
    <template #icon>
      <i :class="step === 'otp' ? 'bi bi-envelope-check' : 'bi bi-box-arrow-in-right'"></i>
    </template>
    <template #title>{{ authTitle }}</template>
    <template #subtitle>{{ authSubtitle }}</template>

    <div v-if="loginError" class="sb-auth-alert">{{ loginError }}</div>
    <div v-if="successMessage" class="sb-auth-alert sb-auth-alert-success">
      {{ successMessage }}
    </div>
    <div v-if="debugOtpCode" class="sb-auth-alert sb-auth-alert-dev">
      Development code: <strong>{{ debugOtpCode }}</strong>
    </div>

    <form v-if="step === 'password'" @submit.prevent="handleLogin">
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
          <router-link to="/forgot-password" class="sb-auth-link sb-auth-link-sm">
            Forgot?
          </router-link>
        </div>
        <input
          type="password"
          v-model="password"
          class="sb-auth-input"
          placeholder="********"
          required
        />
      </div>

      <button type="submit" class="sb-btn-pill sb-auth-submit" :disabled="isSubmitting">
        <span v-if="isSubmitting" class="sb-spinner" aria-hidden="true"></span>
        {{ isSubmitting ? 'Signing In...' : 'Sign In' }}
      </button>
    </form>

    <form v-else @submit.prevent="handleVerifyOtp">
      <div class="sb-auth-field">
        <label class="sb-auth-label">Email verification code</label>
        <input
          type="text"
          v-model="otp"
          class="sb-auth-input sb-auth-otp-input"
          placeholder="Enter the code"
          autocomplete="one-time-code"
          inputmode="numeric"
          required
        />
      </div>

      <button type="submit" class="sb-btn-pill sb-auth-submit" :disabled="isSubmitting">
        <span v-if="isSubmitting" class="sb-spinner" aria-hidden="true"></span>
        {{ isSubmitting ? 'Verifying...' : 'Verify Code' }}
      </button>

      <div class="sb-auth-action-row">
        <button
          type="button"
          class="sb-auth-link sb-auth-link-button"
          :disabled="isResending"
          @click="handleResendOtp"
        >
          {{ isResending ? 'Sending...' : 'Resend code' }}
        </button>
        <button type="button" class="sb-auth-link sb-auth-link-button" @click="returnToPassword">
          Use a different login
        </button>
      </div>
    </form>

    <p v-if="step === 'password'" class="sb-auth-footer-text">
      No account?
      <router-link to="/register" class="sb-auth-link">Create one</router-link>
    </p>
  </AuthShell>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api/api'
import AuthShell from '@/components/AuthShell.vue'
import { needsTutorApplicationAttention } from '@/services/tutorApplicationState'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const email = ref(typeof route.query.email === 'string' ? route.query.email : '')
const password = ref('')
const otp = ref('')
const challengeId = ref('')
const debugOtpCode = ref('')
const step = ref('password')
const isSubmitting = ref(false)
const isResending = ref(false)
const loginError = ref('')
const successMessage = ref(
  route.query.reset === 'success'
    ? 'Your password has been reset. You can sign in now.'
    : route.query.registered === 'success'
      ? 'Your account has been created. Sign in to verify your email.'
      : '',
)

const authTitle = computed(() => (step.value === 'otp' ? 'Check Your Email' : 'Welcome Back'))
const authSubtitle = computed(() =>
  step.value === 'otp'
    ? 'Enter the verification code sent to your university email'
    : 'Log in to your StudyBuddy account',
)

const getErrorMessage = (error, fallback) => {
  const data = error.response?.data

  return data?.error || data?.detail || data?.message || fallback
}

const redirectForRole = (role) => {
  const normalizedRole = role?.toLowerCase()

  if (normalizedRole === 'tutor' && needsTutorApplicationAttention(authStore.user)) {
    router.push('/application-status')
  } else if (normalizedRole === 'tutor') router.push('/tch-dashboard')
  else if (normalizedRole === 'tutee') router.push('/dashboard')
  else if (normalizedRole === 'admin') router.push('/admin/dashboard')
  else if (normalizedRole === 'superadmin') router.push('/superadmin/dashboard')
  else router.push('/')
}

const handleLogin = async () => {
  isSubmitting.value = true
  loginError.value = ''
  successMessage.value = ''

  try {
    const result = await authStore.login({ email: email.value, password: password.value })

    if (result?.requires_2fa) {
      challengeId.value = result.challenge_id
      debugOtpCode.value = result.debug_code || ''
      password.value = ''
      otp.value = ''
      step.value = 'otp'
      successMessage.value = 'We sent a verification code to your university email.'
      return
    }

    redirectForRole(result)
  } catch (error) {
    loginError.value = getErrorMessage(error, 'Login failed. Please check your credentials.')
  } finally {
    isSubmitting.value = false
  }
}

const handleVerifyOtp = async () => {
  isSubmitting.value = true
  loginError.value = ''
  successMessage.value = ''

  try {
    const response = await api.post('login/verify-otp/', {
      challenge_id: challengeId.value,
      code: otp.value.trim(),
    })
    const role = await authStore.login(response.data, { completed: true })

    redirectForRole(role)
  } catch (error) {
    loginError.value = getErrorMessage(error, 'Verification failed. Please check the code.')
  } finally {
    isSubmitting.value = false
  }
}

const handleResendOtp = async () => {
  isResending.value = true
  loginError.value = ''
  successMessage.value = ''

  try {
    const response = await api.post('login/resend-otp/', {
      challenge_id: challengeId.value,
    })
    debugOtpCode.value = response.data?.debug_code || ''
    successMessage.value = 'A new verification code has been sent.'
  } catch (error) {
    loginError.value = getErrorMessage(error, 'Unable to resend the code right now.')
  } finally {
    isResending.value = false
  }
}

const returnToPassword = () => {
  step.value = 'password'
  challengeId.value = ''
  debugOtpCode.value = ''
  otp.value = ''
  loginError.value = ''
  successMessage.value = ''
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
  color: var(--sb-text-main);
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
  border: 1px solid var(--sb-card-border);
  border-radius: 12px;
  background: var(--sb-surface);
  color: var(--sb-text-main);
  outline: none;
  transition:
    border-color 0.15s ease,
    box-shadow 0.15s ease;
}

.sb-auth-input:focus {
  border-color: #00895a;
  box-shadow: 0 0 0 3px rgba(0, 137, 90, 0.12);
}

.sb-auth-input::placeholder {
  color: var(--sb-text-muted);
  opacity: 0.78;
}

.sb-auth-otp-input {
  text-align: center;
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

.sb-auth-alert-success {
  background: #edf7f3;
  border-color: #b8dece;
  color: #00704a;
}

.sb-auth-alert-dev {
  background: #eff6ff;
  border-color: #bfdbfe;
  color: #1d4ed8;
}

.sb-btn-pill {
  background: var(--sb-primary);
  color: var(--sb-primary-contrast);
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
  background: var(--sb-primary-hover);
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

.sb-auth-action-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-top: -4px;
  margin-bottom: 18px;
}

.sb-auth-link-button {
  background: none;
  border: 0;
  padding: 0;
  cursor: pointer;
}

.sb-auth-link-button:disabled {
  opacity: 0.65;
  cursor: not-allowed;
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
  color: var(--sb-primary);
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
  color: var(--sb-text-muted);
  margin: 0;
}

@media (max-width: 420px) {
  .sb-auth-action-row {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
