<template>
  <AuthShell>
    <template #icon>
      <i class="bi bi-key"></i>
    </template>
    <template #title>Reset Password</template>
    <template #subtitle>We'll send reset instructions to your university email</template>

    <div v-if="errorMessage" class="sb-auth-alert">{{ errorMessage }}</div>
    <div v-if="successMessage" class="sb-auth-alert sb-auth-alert-success">
      {{ successMessage }}
    </div>

    <form @submit.prevent="handleRequestReset">
      <div class="sb-auth-field">
        <label class="sb-auth-label">University Email</label>
        <input
          v-model="email"
          type="email"
          class="sb-auth-input sb-field"
          placeholder="you@university.edu"
          required
        />
      </div>

      <button type="submit" class="sb-btn-pill sb-auth-submit sb-btn sb-elevated sb-elevated--brand" :disabled="isSubmitting">
        <span v-if="isSubmitting" class="sb-spinner" aria-hidden="true"></span>
        {{ isSubmitting ? 'Sending...' : 'Send Reset Link' }}
      </button>
    </form>

    <p class="sb-auth-footer-text">
      Remembered it?
      <router-link to="/login" class="sb-auth-link">Back to login</router-link>
    </p>
  </AuthShell>
</template>

<script setup>
import { ref } from 'vue'
import api from '@/services/api/api'
import AuthShell from '@/components/AuthShell.vue'

const email = ref('')
const isSubmitting = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

const genericSuccessMessage = 'If that email exists, reset instructions have been sent.'

const handleRequestReset = async () => {
  isSubmitting.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    const response = await api.post('password-reset/request/', {
      email: email.value,
    })

    successMessage.value = response.data?.message || genericSuccessMessage
  } catch (error) {
    if (error.response) {
      successMessage.value = genericSuccessMessage
      return
    }

    errorMessage.value = 'Unable to reach the server. Please try again later.'
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
  transition: none;
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
  transition: transform var(--sb-t-normal) var(--sb-spring);
}

.sb-btn-pill:hover:not(:disabled) {
  background: var(--sb-primary-hover);
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
