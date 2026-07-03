<template>
  <section v-if="isDev" class="dev-session-qa card shadow-sm p-4 mt-4">
    <div class="dev-session-qa-header">
      <div>
        <span class="dev-session-qa-eyebrow">Dev only</span>
        <h5 class="fw-bold mb-1">Session QA</h5>
        <p class="text-muted small mb-0">
          Force this booking into countdown states or preview the check-in modals.
        </p>
      </div>
      <span class="dev-session-qa-pill">
        <i class="bi bi-tools"></i>
        QA
      </span>
    </div>

    <div class="dev-session-qa-grid">
      <button
        type="button"
        class="btn btn-outline-warning fw-semibold sb-btn"
        :disabled="isBusy || !bookingId"
        @click="forceUpcoming"
      >
        Force upcoming (T-12min)
      </button>
      <button
        type="button"
        class="btn btn-warning fw-semibold sb-btn"
        :disabled="isBusy || !bookingId"
        @click="forceLive('start')"
      >
        Force live now
      </button>
      <button
        type="button"
        class="btn btn-outline-warning fw-semibold sb-btn"
        :disabled="isBusy || !bookingId"
        @click="forceLive('midpoint')"
      >
        Force midpoint now
      </button>
      <button
        type="button"
        class="btn btn-outline-warning fw-semibold sb-btn"
        :disabled="isBusy || !bookingId"
        @click="forceLive('ending')"
      >
        Force ending soon
      </button>
      <button
        type="button"
        class="btn btn-outline-warning fw-semibold sb-btn"
        :disabled="isBusy || !bookingId"
        @click="forceHandoff"
      >
        Force handoff (payment required)
      </button>
      <button
        type="button"
        class="btn btn-light fw-semibold sb-btn"
        :disabled="isBusy || !bookingId"
        @click="clearForcedLive"
      >
        Clear forced live
      </button>
    </div>

    <div class="dev-session-qa-preview">
      <button
        type="button"
        class="btn btn-outline-secondary fw-semibold sb-btn"
        :disabled="isBusy || !isFaceToFace"
        @click="isVenuePreviewOpen = true"
      >
        Preview venue modal
      </button>
      <button
        type="button"
        class="btn btn-outline-secondary fw-semibold sb-btn"
        :disabled="isBusy"
        @click="isMidpointPreviewOpen = true"
      >
        Preview mid-session modal
      </button>
    </div>

    <p v-if="!isFaceToFace" class="dev-session-qa-note mb-0">
      Venue preview is disabled for online sessions.
    </p>

    <VenueConfirmModal
      :open="isVenuePreviewOpen"
      :location="location"
      @close="isVenuePreviewOpen = false"
      @confirm="handleVenuePreview"
    />
    <SessionCheckInModal
      :open="isMidpointPreviewOpen"
      @close="isMidpointPreviewOpen = false"
      @confirm="handleMidpointPreview"
    />
  </section>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useActiveSessionStore } from '@/stores/activeSession'
import { useSessionsStore } from '@/stores/completedSessions'
import { useToastStore } from '@/stores/toast'
import VenueConfirmModal from '@/components/VenueConfirmModal.vue'
import SessionCheckInModal from '@/components/SessionCheckInModal.vue'

const DEV_LIVE_REFRESH_KEY = 'studybuddy_dev_live_refresh'

const props = defineProps({
  bookingId: { type: [Number, String], default: null },
  sessionMode: { type: String, default: '' },
  location: { type: String, default: '' },
})

const emit = defineEmits(['refresh'])

const sessionsStore = useSessionsStore()
const activeSession = useActiveSessionStore()
const toastStore = useToastStore()

const isDev = import.meta.env.DEV
const isSubmitting = ref(false)
const isVenuePreviewOpen = ref(false)
const isMidpointPreviewOpen = ref(false)

const isBusy = computed(() => isSubmitting.value)
const isFaceToFace = computed(() => String(props.sessionMode || '').toLowerCase() === 'f2f')

const refreshSurfaces = async () => {
  activeSession.currentTime = new Date()
  await activeSession.refreshActive()
  emit('refresh')
}

const notifySharedRefresh = (action, phase = null) => {
  if (typeof window === 'undefined') {
    return
  }

  window.localStorage.setItem(
    DEV_LIVE_REFRESH_KEY,
    JSON.stringify({
      action,
      phase,
      bookingId: props.bookingId,
      refreshedAt: Date.now(),
    }),
  )
}

const forceLive = async (phase) => {
  if (!props.bookingId || isSubmitting.value) {
    return
  }

  isSubmitting.value = true

  try {
    await sessionsStore.devForceLive(props.bookingId, phase)
    notifySharedRefresh('force-live', phase)
    await refreshSurfaces()
    toastStore.push(`Dev: session forced to ${phase} for tutor and tutee.`)
  } catch (error) {
    toastStore.push(error.response?.data?.error || 'Failed to force the session live.', 'error')
  } finally {
    isSubmitting.value = false
  }
}

const forceUpcoming = async () => {
  if (!props.bookingId || isSubmitting.value) {
    return
  }

  isSubmitting.value = true

  try {
    await sessionsStore.devForceUpcoming(props.bookingId)
    notifySharedRefresh('force-upcoming', 'upcoming')
    await refreshSurfaces()
    toastStore.push('Dev: session forced to upcoming countdown.')
  } catch (error) {
    toastStore.push(error.response?.data?.error || 'Failed to force the session upcoming.', 'error')
  } finally {
    isSubmitting.value = false
  }
}

const forceHandoff = async () => {
  if (!props.bookingId || isSubmitting.value) {
    return
  }

  isSubmitting.value = true

  try {
    await sessionsStore.devForceHandoff(props.bookingId)
    notifySharedRefresh('force-handoff', 'handoff')
    await refreshSurfaces()
    toastStore.push('Dev: session forced to payment handoff.')
  } catch (error) {
    toastStore.push(error.response?.data?.error || 'Failed to force the session handoff.', 'error')
  } finally {
    isSubmitting.value = false
  }
}

const clearForcedLive = async () => {
  if (!props.bookingId || isSubmitting.value) {
    return
  }

  isSubmitting.value = true

  try {
    await sessionsStore.devClearForceLive(props.bookingId)
    notifySharedRefresh('clear-force-live')
    await refreshSurfaces()
    toastStore.push('Dev: forced live state cleared for tutor and tutee.')
  } catch (error) {
    toastStore.push(error.response?.data?.error || 'Failed to clear forced live state.', 'error')
  } finally {
    isSubmitting.value = false
  }
}

const handleVenuePreview = () => {
  isVenuePreviewOpen.value = false
  toastStore.push('Dev preview only. No venue response was saved.')
}

const handleMidpointPreview = () => {
  isMidpointPreviewOpen.value = false
  toastStore.push('Dev preview only. No check-in response was saved.')
}
</script>

<style scoped>
.dev-session-qa {
  border: 1px solid rgba(245, 158, 11, 0.32);
  background: linear-gradient(180deg, rgba(255, 251, 235, 0.92), var(--sb-card-bg));
}

.dev-session-qa-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
}

.dev-session-qa-eyebrow {
  display: block;
  margin-bottom: 4px;
  color: #92400e;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0;
  text-transform: uppercase;
}

.dev-session-qa-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 10px;
  border-radius: 999px;
  background: rgba(245, 158, 11, 0.16);
  color: #92400e;
  font-size: 12px;
  font-weight: 700;
}

.dev-session-qa-grid,
.dev-session-qa-preview {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.dev-session-qa-preview {
  margin-top: 10px;
}

.dev-session-qa-note {
  margin-top: 12px;
  color: #6b7280;
  font-size: 13px;
}

@media (max-width: 575px) {
  .dev-session-qa-header {
    flex-direction: column;
  }

  .dev-session-qa-grid,
  .dev-session-qa-preview {
    grid-template-columns: 1fr;
  }
}
</style>
