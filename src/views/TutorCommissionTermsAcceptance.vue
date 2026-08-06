<template>
  <div class="min-vh-100 py-5 tutor-setup-page">
    <div class="container-fluid px-4 mb-3 d-flex justify-content-between align-items-center">
      <span class="fw-bold sb-text">StudyBuddy</span>
      <SbThemeToggle />
    </div>

    <div class="container">
      <div class="row justify-content-center">
        <div class="col-md-7 col-lg-6">
          <div class="card border-0 sb-card-surface sb-text shadow-sm rounded-4">
            <div class="card-body p-4 p-md-5">
              <div class="text-center mb-4">
                <h3 class="fw-bold sb-text">Before You Continue</h3>
                <p class="sb-muted">
                  StudyBuddy deducts a {{ commissionRatePercent }}% platform fee from each
                  completed session's payout. Please acknowledge this to keep using your account.
                </p>
              </div>

              <button
                type="button"
                class="btn bg-sb-primary text-white w-100 py-3 rounded-3 fw-bold shadow-sm sb-btn"
                :disabled="submitting"
                @click="acceptTerms"
              >
                {{ submitting ? 'Saving...' : 'I Understand, Continue' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useProfileStore } from '@/stores/profile'
import { useToastStore } from '@/stores/toast'
import api from '@/services/api/api'
import { PLATFORM_COMMISSION_RATE_PERCENT } from '@/config'
import SbThemeToggle from '@/components/SbThemeToggle.vue'

const router = useRouter()
const profileStore = useProfileStore()
const toastStore = useToastStore()

const commissionRatePercent = PLATFORM_COMMISSION_RATE_PERCENT
const submitting = ref(false)

const acceptTerms = async () => {
  submitting.value = true
  try {
    await api.post('/tutor/accept-commission-terms/')
    profileStore.commissionTermsAccepted = true
    router.push('/tch-dashboard')
  } catch (error) {
    console.error('Failed to record commission terms acceptance', error)
    toastStore.push('Could not save your acknowledgement. Please try again.', 'error')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.tutor-setup-page {
  background-color: var(--sb-bg);
}
</style>
