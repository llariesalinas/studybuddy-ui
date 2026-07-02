<template>
  <Transition name="dock-rise">
    <div v-if="booking" class="ongoing-dock" role="status" aria-live="polite">
      <div class="ongoing-dock-card">
        <div class="ongoing-dock-avatar" :class="{ 'is-due': isCheckInDue }">
          <i class="bi" :class="isCheckInDue ? 'bi-bell-fill' : 'bi-broadcast'"></i>
        </div>

        <div class="ongoing-dock-info">
          <div class="ongoing-dock-heading">
            <span class="ongoing-dock-pill" :class="isCheckInDue ? 'is-due' : 'is-live'">
              <span class="ongoing-dock-dot"></span>
              {{ isCheckInDue ? 'Check-in due' : 'Ongoing' }}
            </span>
            <span class="ongoing-dock-subject">{{ subject }}</span>
          </div>

          <p class="ongoing-dock-partner">{{ partnerLabel }}</p>

          <div class="ongoing-dock-progress" :aria-label="`Session phase: ${sessionPhase}`">
            <template v-for="(step, index) in steps" :key="step.key">
              <span class="ongoing-dock-step" :class="{ done: step.reached }" :title="step.label"></span>
              <span
                v-if="index < steps.length - 1"
                class="ongoing-dock-line"
                :class="{ done: steps[index + 1].reached }"
              ></span>
            </template>
          </div>
        </div>

        <button type="button" class="btn bg-sb-primary text-white sb-btn ongoing-dock-open" @click="openSession">
          Open
          <i class="bi bi-arrow-right ms-1"></i>
        </button>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useActiveSessionStore } from '@/stores/activeSession'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const activeSession = useActiveSessionStore()
const authStore = useAuthStore()

const { activeBooking, activeDetail, sessionPhase, dueCheckIn } = storeToRefs(activeSession)

const booking = computed(() => activeBooking.value)
const role = computed(() => authStore.user?.role?.toLowerCase() || null)
const isTutor = computed(() => role.value === 'tutor')
const isCheckInDue = computed(() => Boolean(dueCheckIn.value))

const subject = computed(() => booking.value?.subject || 'Tutoring session')

const partnerLabel = computed(() => {
  if (isTutor.value) {
    const name = booking.value?.tuteeName || booking.value?.tutee || activeDetail.value?.tutee?.name
    return name ? `with ${name}` : 'Your session in progress'
  }

  const name = booking.value?.tutor || activeDetail.value?.tutor?.name
  return name ? `with ${name}` : 'Your session in progress'
})

const PHASE_ORDER = ['before', 'venue-window', 'midpoint', 'over']

const steps = computed(() => {
  const currentIndex = PHASE_ORDER.indexOf(sessionPhase.value)

  return [
    { key: 'booked', label: 'Booked', reached: true },
    { key: 'started', label: 'Started', reached: currentIndex >= 1 },
    { key: 'midpoint', label: 'Midpoint', reached: currentIndex >= 2 },
    { key: 'ending', label: 'Ending', reached: currentIndex >= 3 },
  ]
})

const openSession = () => {
  const id = booking.value?.id

  if (id == null) {
    return
  }

  if (isTutor.value) {
    router.push({ name: 'booking-details', params: { id } })
    return
  }

  router.push({ name: 'tuteeSessionDetails', params: { id } })
}
</script>

<style scoped>
.ongoing-dock {
  position: fixed;
  left: 50%;
  bottom: 20px;
  transform: translateX(-50%);
  z-index: 1150;
  width: min(640px, calc(100% - 48px));
}

.ongoing-dock-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 14px 18px;
  background: var(--sb-card-bg);
  border: 1px solid var(--sb-card-border);
  border-top: 3px solid var(--sb-primary);
  border-radius: 16px;
  box-shadow: 0 16px 40px rgba(15, 23, 42, 0.18);
}

.ongoing-dock-avatar {
  flex: none;
  width: 44px;
  height: 44px;
  display: grid;
  place-items: center;
  border-radius: 12px;
  background: rgba(0, 137, 90, 0.12);
  color: var(--sb-primary);
  font-size: 20px;
}

.ongoing-dock-avatar.is-due {
  background: rgba(234, 179, 8, 0.16);
  color: var(--sb-warning, #a16207);
}

.ongoing-dock-info {
  flex: 1;
  min-width: 0;
}

.ongoing-dock-heading {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 4px;
}

.ongoing-dock-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
}

.ongoing-dock-pill.is-live {
  background: rgba(0, 137, 90, 0.12);
  color: var(--sb-primary);
}

.ongoing-dock-pill.is-due {
  background: rgba(234, 179, 8, 0.16);
  color: var(--sb-warning, #a16207);
}

.ongoing-dock-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: currentColor;
}

.ongoing-dock-subject {
  font-size: 14px;
  font-weight: 600;
  color: var(--sb-text, #0f172a);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.ongoing-dock-partner {
  margin: 0 0 8px;
  font-size: 12px;
  color: var(--sb-text-muted, #64748b);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.ongoing-dock-progress {
  display: flex;
  align-items: center;
  gap: 4px;
}

.ongoing-dock-step {
  flex: none;
  width: 9px;
  height: 9px;
  border-radius: 50%;
  background: var(--sb-card-border);
}

.ongoing-dock-step.done {
  background: var(--sb-primary);
}

.ongoing-dock-line {
  height: 2px;
  flex: 1;
  background: var(--sb-card-border);
}

.ongoing-dock-line.done {
  background: var(--sb-primary);
}

.ongoing-dock-open {
  flex: none;
  border-radius: 999px;
  padding: 8px 18px;
  font-size: 13px;
  font-weight: 600;
}

.dock-rise-enter-active,
.dock-rise-leave-active {
  transition: transform 240ms ease, opacity 240ms ease;
}

.dock-rise-enter-from,
.dock-rise-leave-to {
  transform: translateX(-50%) translateY(16px);
  opacity: 0;
}

@media (max-width: 575px) {
  .ongoing-dock-card {
    flex-wrap: wrap;
  }

  .ongoing-dock-open {
    width: 100%;
  }
}
</style>
