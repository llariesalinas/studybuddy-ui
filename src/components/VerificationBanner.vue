<template>
  <section
    v-if="shouldShowBanner"
    class="verification-banner"
    :class="`verification-banner--${bannerContent.tone}`"
    role="status"
    aria-live="polite"
  >
    <div class="verification-banner__body">
      <div class="verification-banner__icon" aria-hidden="true">
        <i :class="bannerContent.icon"></i>
      </div>

      <div class="verification-banner__copy">
        <p class="verification-banner__eyebrow">{{ bannerContent.eyebrow }}</p>
        <p class="verification-banner__title">{{ bannerContent.title }}</p>
        <p class="verification-banner__text">{{ bannerContent.text }}</p>
      </div>
    </div>

    <div class="verification-banner__actions">
      <button
        type="button"
        class="verification-banner__cta sb-btn"
        @click="emit('navigate')"
      >
        {{ bannerContent.cta }}
      </button>

      <button
        type="button"
        class="verification-banner__dismiss sb-btn"
        aria-label="Dismiss verification banner"
        @click="dismissBanner"
      >
        <i class="bi bi-x-lg"></i>
      </button>
    </div>
  </section>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useProfileStore } from '@/stores/profile'
import { needsTuteeVerificationBlock } from '@/services/tutorApplicationState'

const emit = defineEmits(['navigate'])

const authStore = useAuthStore()
const profileStore = useProfileStore()
const dismissed = ref(false)

const normalizedUserRole = computed(() =>
  String(authStore.userRole || authStore.user?.role || '').trim().toLowerCase()
)

const tuteeVerificationSnapshot = computed(() => ({
  application_status: profileStore.applicationStatus || null,
  document_renewal_status: profileStore.renewalStatus || null,
  tutee_verification_enforced: profileStore.tuteeVerificationEnforced,
}))

const showTuteeBanner = computed(() =>
  profileStore.loaded &&
  normalizedUserRole.value === 'tutee' &&
  needsTuteeVerificationBlock(tuteeVerificationSnapshot.value)
)

const showTutorBanner = computed(() =>
  profileStore.loaded &&
  normalizedUserRole.value === 'tutor' &&
  Boolean(profileStore.tutorRenewalRequired)
)

const bannerContent = computed(() => {
  if (showTuteeBanner.value) {
    return {
      tone: 'tutee',
      icon: 'bi bi-shield-exclamation',
      eyebrow: 'Verification required',
      title: 'Verify your enrollment before you book a session.',
      text: 'You can keep browsing tutors, but booking stays locked until your account is verified.',
      cta: 'Verify Now',
    }
  }

  if (showTutorBanner.value) {
    return {
      tone: 'tutor',
      icon: 'bi bi-arrow-repeat',
      eyebrow: 'Renewal required',
      title: 'Renew your verification before you accept new sessions.',
      text: 'Your dashboard stays available, but session acceptance is locked until your renewal is approved.',
      cta: 'Renew Now',
    }
  }

  return null
})

const dismissStorageKey = computed(() => {
  const userId = authStore.user?.id || 'anonymous'
  const role = normalizedUserRole.value || 'unknown'

  return `sb-verification-banner-dismissed:${role}:${userId}`
})

const syncDismissedState = () => {
  if (typeof window === 'undefined' || !window.sessionStorage || !bannerContent.value) {
    dismissed.value = false
    return
  }

  dismissed.value = window.sessionStorage.getItem(dismissStorageKey.value) === 'true'
}

watch([dismissStorageKey, bannerContent], syncDismissedState, { immediate: true })

const shouldShowBanner = computed(() => Boolean(bannerContent.value) && !dismissed.value)

const dismissBanner = () => {
  if (typeof window !== 'undefined' && window.sessionStorage) {
    window.sessionStorage.setItem(dismissStorageKey.value, 'true')
  }

  dismissed.value = true
}
</script>

<style scoped>
.verification-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem 1.1rem;
  margin-bottom: 1.25rem;
  border-radius: 20px;
  border: 1px solid transparent;
  box-shadow: 0 14px 30px rgba(15, 23, 42, 0.08);
}

.verification-banner--tutee {
  background: linear-gradient(135deg, #fff8e7 0%, #ffffff 85%);
  border-color: #f2dca1;
}

.verification-banner--tutor {
  background: linear-gradient(135deg, #f7f4ff 0%, #ffffff 85%);
  border-color: #d8cdf7;
}

.verification-banner__body {
  display: flex;
  align-items: flex-start;
  gap: 0.9rem;
  min-width: 0;
}

.verification-banner__icon {
  width: 2.75rem;
  height: 2.75rem;
  border-radius: 16px;
  display: grid;
  place-items: center;
  font-size: 1.2rem;
  flex-shrink: 0;
}

.verification-banner--tutee .verification-banner__icon {
  background: rgba(217, 119, 6, 0.12);
  color: #b45309;
}

.verification-banner--tutor .verification-banner__icon {
  background: rgba(109, 40, 217, 0.1);
  color: #6d28d9;
}

.verification-banner__copy {
  min-width: 0;
}

.verification-banner__eyebrow,
.verification-banner__title,
.verification-banner__text {
  margin: 0;
}

.verification-banner__eyebrow {
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.verification-banner--tutee .verification-banner__eyebrow {
  color: #b45309;
}

.verification-banner--tutor .verification-banner__eyebrow {
  color: #6d28d9;
}

.verification-banner__title {
  margin-top: 0.2rem;
  color: #163127;
  font-size: 1rem;
  font-weight: 700;
}

.verification-banner__text {
  margin-top: 0.3rem;
  color: #5d6d66;
  line-height: 1.5;
}

.verification-banner__actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-shrink: 0;
}

.verification-banner__cta {
  border: 0;
  border-radius: 999px;
  padding: 0.7rem 1rem;
  color: #ffffff;
  font-weight: 700;
}

.verification-banner--tutee .verification-banner__cta {
  background: #d97706;
}

.verification-banner--tutee .verification-banner__cta:hover {
  background: #b45309;
}

.verification-banner--tutor .verification-banner__cta {
  background: #6d28d9;
}

.verification-banner--tutor .verification-banner__cta:hover {
  background: #5b21b6;
}

.verification-banner__dismiss {
  width: 2.5rem;
  height: 2.5rem;
  border: 0;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.7);
  color: #5d6d66;
}

.verification-banner__dismiss:hover {
  background: rgba(255, 255, 255, 0.95);
}

@media (max-width: 991px) {
  .verification-banner {
    flex-direction: column;
    align-items: stretch;
  }

  .verification-banner__actions {
    justify-content: space-between;
  }
}

@media (max-width: 575px) {
  .verification-banner__body {
    flex-direction: column;
  }
}
</style>
