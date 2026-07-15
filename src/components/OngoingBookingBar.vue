<template>
  <Transition name="dock-rise" mode="out-in">
    <div v-if="showFullDock" class="ongoing-dock" role="status" aria-live="polite">
      <div class="ongoing-dock-card" :class="`is-${presentation.state}`">
        <div class="ongoing-dock-copy">
          <div class="ongoing-dock-heading">
            <span class="ongoing-dock-pill">
              <span class="ongoing-dock-dot"></span>
              {{ presentation.stateLabel }}
            </span>
            <strong>{{ presentation.timerText }}</strong>
          </div>

          <p>{{ presentation.primaryText }}</p>
          <span v-if="presentation.upNextHint" class="ongoing-dock-upnext">
            {{ presentation.upNextHint }}
          </span>
        </div>

        <div
          class="ongoing-dock-orbit"
          :style="{ '--orbit-progress': `${presentation.progress}%` }"
          :aria-label="`${presentation.zoneLabel}, ${presentation.timerText}`"
        >
          <span
            v-for="zone in 4"
            :key="zone"
            class="ongoing-dock-zone"
            :class="{ active: presentation.zone >= zone }"
          ></span>
          <span class="ongoing-dock-fill"></span>
          <span class="ongoing-dock-bead"></span>
        </div>

        <button type="button" class="ongoing-dock-open sb-btn" @click="openSession">
          <span>Open</span>
          <i class="bi bi-arrow-right" aria-hidden="true"></i>
        </button>

        <button
          type="button"
          class="ongoing-dock-hide sb-btn"
          :aria-label="`Hide ${presentation.stateLabel.toLowerCase()} dock`"
          @click="hideDock"
        >
          <i class="bi bi-dash-lg" aria-hidden="true"></i>
        </button>
      </div>
    </div>

    <button
      v-else-if="showRestoreChip"
      type="button"
      class="ongoing-dock-chip sb-btn"
      @click="restoreDock"
    >
      <span class="ongoing-dock-chip-dot"></span>
      <span class="ongoing-dock-chip-copy">
        <strong>{{ presentation.stateLabel }}</strong>
        <span>Restore handoff</span>
      </span>
    </button>
  </Transition>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useOrbitStrip } from '@/composables/useOrbitStrip'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const hiddenDockId = ref(null)

const role = computed(() => authStore.user?.role?.toLowerCase() || null)
const isTutor = computed(() => role.value === 'tutor')
const { presentation, hasOrbit } = useOrbitStrip({ isTutor })

const isMatchingDetailRoute = computed(() => (
  ['tuteeSessionDetails', 'booking-details'].includes(route.name)
  && String(route.params.id || '') === String(presentation.value.id || '')
))

const hasDock = computed(() => hasOrbit.value && !isMatchingDetailRoute.value)
const showFullDock = computed(() => hasDock.value && hiddenDockId.value !== presentation.value.id)
const showRestoreChip = computed(() => hasDock.value && hiddenDockId.value === presentation.value.id)

watch(
  () => presentation.value.id,
  (id, previousId) => {
    if (id !== previousId) {
      hiddenDockId.value = null
    }
  },
)

const hideDock = () => {
  if (presentation.value.id == null) {
    return
  }

  hiddenDockId.value = presentation.value.id
}

const restoreDock = () => {
  hiddenDockId.value = null
}

const openSession = () => {
  const id = presentation.value.id

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
  position: relative;
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(180px, 0.42fr) auto auto;
  align-items: center;
  gap: 14px;
  overflow: hidden;
  padding: 14px 16px;
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 8px;
  background:
    radial-gradient(circle at 18% 0%, rgba(21, 184, 143, 0.32), transparent 34%),
    radial-gradient(circle at 86% 100%, rgba(244, 171, 60, 0.22), transparent 30%),
    linear-gradient(135deg, #071914, #0f2f28 54%, #13201d);
  box-shadow: 0 18px 44px rgba(6, 18, 14, 0.3);
  color: #ffffff;
}

.ongoing-dock-card::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.08), transparent);
  opacity: 0.7;
  pointer-events: none;
}

.ongoing-dock-copy {
  position: relative;
  z-index: 1;
  min-width: 0;
}

.ongoing-dock-heading {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
  margin-bottom: 5px;
}

.ongoing-dock-heading strong {
  color: rgba(255, 255, 255, 0.96);
  font-size: 13px;
  font-weight: 800;
  white-space: nowrap;
}

.ongoing-dock-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  flex: none;
  padding: 4px 9px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
  background: rgba(255, 255, 255, 0.12);
  color: #d9fff2;
}

.ongoing-dock-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #45f0bd;
  box-shadow: 0 0 12px rgba(69, 240, 189, 0.8);
}

.ongoing-dock-copy p,
.ongoing-dock-upnext {
  display: block;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.ongoing-dock-copy p {
  color: rgba(255, 255, 255, 0.86);
  font-size: 13px;
}

.ongoing-dock-upnext {
  margin-top: 3px;
  color: rgba(206, 255, 237, 0.74);
  font-size: 11px;
}

.ongoing-dock-orbit {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 5px;
  min-width: 0;
  height: 24px;
  align-items: center;
}

.ongoing-dock-zone {
  height: 6px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.14);
}

.ongoing-dock-zone.active {
  background: rgba(118, 255, 213, 0.5);
}

.ongoing-dock-fill {
  position: absolute;
  left: 0;
  top: 50%;
  width: var(--orbit-progress);
  max-width: 100%;
  height: 2px;
  border-radius: 999px;
  background: linear-gradient(90deg, #5ff0c2, #f8d47a);
  transform: translateY(-50%);
}

.ongoing-dock-bead {
  position: absolute;
  left: var(--orbit-progress);
  top: 50%;
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.82);
  border-radius: 50%;
  background: #f9fefb;
  box-shadow:
    0 0 0 5px rgba(95, 240, 194, 0.16),
    0 0 18px rgba(248, 212, 122, 0.55);
  transform: translate(-50%, -50%);
}

.ongoing-dock-open {
  position: relative;
  z-index: 1;
  flex: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  border: 1px solid rgba(255, 255, 255, 0.24);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.96);
  color: #10231d;
  padding: 8px 14px;
  font-size: 13px;
  font-weight: 800;
}

.ongoing-dock-hide {
  position: relative;
  z-index: 1;
  flex: none;
  display: inline-grid;
  place-items: center;
  width: 42px;
  height: 42px;
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
}

.ongoing-dock-chip {
  position: fixed;
  right: 24px;
  bottom: 20px;
  z-index: 1150;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border: 1px solid rgba(255, 255, 255, 0.16);
  border-radius: 999px;
  background: rgba(8, 24, 19, 0.94);
  box-shadow: 0 18px 44px rgba(6, 18, 14, 0.28);
  color: #e8fff7;
}

.ongoing-dock-chip-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #45f0bd;
  box-shadow: 0 0 12px rgba(69, 240, 189, 0.8);
  flex: none;
}

.ongoing-dock-chip-copy {
  display: flex;
  flex-direction: column;
  min-width: 0;
  text-align: left;
}

.ongoing-dock-chip-copy strong,
.ongoing-dock-chip-copy span {
  display: block;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.ongoing-dock-chip-copy strong {
  font-size: 11px;
  font-weight: 800;
  color: #d7fff1;
}

.ongoing-dock-chip-copy span {
  color: rgba(214, 255, 239, 0.72);
  font-size: 11px;
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
    grid-template-columns: 1fr;
  }

  .ongoing-dock-open {
    width: 100%;
  }

  .ongoing-dock-hide {
    width: 100%;
  }

  .ongoing-dock-heading {
    align-items: flex-start;
    flex-direction: column;
  }

  .ongoing-dock-chip {
    right: 16px;
    bottom: 16px;
    max-width: calc(100% - 32px);
  }
}
</style>
