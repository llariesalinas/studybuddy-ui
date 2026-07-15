<template>
  <section
    v-if="shouldShowBanner"
    class="wallet-debt-banner"
    role="button"
    tabindex="0"
    aria-live="polite"
    @click="emit('navigate')"
    @keydown.enter.prevent="emit('navigate')"
    @keydown.space.prevent="emit('navigate')"
  >
    <div class="wallet-debt-banner__body">
      <div class="wallet-debt-banner__icon" aria-hidden="true">
        <i class="bi bi-exclamation-octagon"></i>
      </div>

      <div class="wallet-debt-banner__copy">
        <p class="wallet-debt-banner__eyebrow">Wallet action required</p>
        <p class="wallet-debt-banner__title">
          Your wallet balance is negative. You can't accept new bookings until it's settled — visit your Wallet to top up.
        </p>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useProfileStore } from '@/stores/profile'

const emit = defineEmits(['navigate'])

const authStore = useAuthStore()
const profileStore = useProfileStore()

const normalizedUserRole = computed(() =>
  String(authStore.userRole || authStore.user?.role || '').trim().toLowerCase()
)

const shouldShowBanner = computed(() =>
  profileStore.loaded &&
  normalizedUserRole.value === 'tutor' &&
  Boolean(profileStore.walletNegative)
)
</script>

<style scoped>
.wallet-debt-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  width: 100%;
  padding: 1rem 1.1rem;
  margin-bottom: 1.25rem;
  border-radius: 20px;
  border: 1px solid color-mix(in srgb, var(--sb-danger) 25%, transparent);
  background: color-mix(in srgb, var(--sb-danger) 10%, #ffffff);
  box-shadow: 0 14px 30px rgba(15, 23, 42, 0.08);
  cursor: pointer;
}

.wallet-debt-banner:focus-visible {
  outline: 3px solid color-mix(in srgb, var(--sb-danger) 35%, transparent);
  outline-offset: 3px;
}

.wallet-debt-banner__body {
  display: flex;
  align-items: flex-start;
  gap: 0.9rem;
  min-width: 0;
}

.wallet-debt-banner__icon {
  width: 2.75rem;
  height: 2.75rem;
  border-radius: 16px;
  display: grid;
  place-items: center;
  font-size: 1.2rem;
  flex-shrink: 0;
  background: color-mix(in srgb, var(--sb-danger) 14%, transparent);
  color: var(--sb-danger);
}

.wallet-debt-banner__copy {
  min-width: 0;
}

.wallet-debt-banner__eyebrow,
.wallet-debt-banner__title {
  margin: 0;
}

.wallet-debt-banner__eyebrow {
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--sb-danger);
}

.wallet-debt-banner__title {
  margin-top: 0.2rem;
  color: color-mix(in srgb, var(--sb-danger) 75%, black);
  font-size: 1rem;
  font-weight: 700;
  line-height: 1.5;
}

@media (max-width: 575px) {
  .wallet-debt-banner__body {
    flex-direction: column;
  }
}
</style>
