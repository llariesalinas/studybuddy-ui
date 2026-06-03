<template>
  <AuthShell>
    <template #icon>
      <i class="bi bi-shield-lock"></i>
    </template>
    <template #title>Choose New Password</template>
    <template #subtitle>Use a strong password for your StudyBuddy account</template>

    <div v-if="errorMessage" class="sb-auth-alert">{{ errorMessage }}</div>
    <div v-if="successMessage" class="sb-auth-alert sb-auth-alert-success">
      {{ successMessage }}
    </div>

    <form @submit.prevent="handleResetPassword">
      <div class="sb-auth-field">
        <label class="sb-auth-label">New Password</label>
        <input
          v-model="password"
          type="password"
          class="sb-auth-input"
          placeholder="********"
          required
        />
      </div>

      <div class="sb-auth-field">
        <label class="sb-auth-label">Confirm Password</label>
        <input
          v-model="passwordConfirm"
          type="password"
          class="sb-auth-input"
          placeholder="********"
          required
        />
      </div>

      <button type="submit" class="sb-btn-pill sb-auth-submit" :disabled="isSubmitting">
        <span v-if="isSubmitting" class="sb-spinner" aria-hidden="true"></span>
        {{ isSubmitting ? 'Updating...' : 'Update Password' }}
      </button>
    </form>

    <p class="sb-auth-footer-text">
      <router-link to="/login" class="sb-auth-link">Back to login</router-link>
    </p>
  </AuthShell>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/services/api/api'
import AuthShell from '@/components/AuthShell.vue'

const route = useRoute()
const router = useRouter()

const resetUid = () => route.params.uid || route.query.uid || route.query.uidb64
const resetToken = () => route.params.token || route.query.token

const password = ref('')
const passwordConfirm = ref('')
const isSubmitting = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

const getErrorMessage = (error) => {
  const data = error.response?.data

  return data?.error || data?.detail || data?.message || 'Unable to reset your password.'
}

const handleResetPassword = async () => {
  isSubmitting.value = true
  errorMessage.value = ''
  successMessage.value = ''

  if (password.value !== passwordConfirm.value) {
    errorMessage.value = 'Passwords do not match.'
    isSubmitting.value = false
    return
  }

  if (!resetUid() || !resetToken()) {
    errorMessage.value = 'This password reset link is missing required information.'
    isSubmitting.value = false
    return
  }

  try {
    const response = await api.post('password-reset/confirm/', {
      uid: resetUid(),
      token: resetToken(),
      password: password.value,
      password_confirm: passwordConfirm.value,
    })

    successMessage.value = response.data?.message || 'Your password has been reset.'
    window.setTimeout(() => {
      router.push({ path: '/login', query: { reset: 'success' } })
    }, 900)
  } catch (error) {
    errorMessage.value = getErrorMessage(error)
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
  color: var(--sb-text-main);
  margin-bottom: 6px;
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
  background: #f0fdf4;
  border-color: #bbf7d0;
  color: #166534;
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

.sb-auth-footer-text {
  text-align: center;
  font-size: 13px;
  color: var(--sb-text-muted);
  margin: 0;
}
</style>
