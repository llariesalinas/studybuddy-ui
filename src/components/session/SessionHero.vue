<template>
  <section class="session-card session-hero" :class="{ 'session-hero-live': isOngoing }">
    <div class="session-hero-top">
      <div class="session-avatar" aria-hidden="true">
        <img
          v-if="avatarUrl && !avatarLoadError"
          :src="avatarUrl"
          :alt="`${profile.name} avatar`"
          @error="avatarLoadError = true"
        />
        <span v-else>{{ initials }}</span>
      </div>

      <div class="session-hero-copy">
        <div class="session-hero-title-row">
          <div>
            <h3>{{ profile.name }}</h3>
            <p>{{ profile.meta }}</p>
          </div>
          <span class="session-status-badge" :class="statusClass">
            <span class="session-status-dot" :class="{ 'session-status-dot-live': isOngoing }"></span>
            {{ statusLabel }}
          </span>
        </div>

        <span class="session-subject-pill">{{ subject || 'Session' }}</span>
      </div>
    </div>

    <div v-if="isOngoing" class="session-live-panel">
      <div>
        <p class="session-live-label">Live · elapsed</p>
        <div class="session-live-timer">{{ clock.formattedElapsed }}</div>
      </div>
      <div class="session-live-progress">
        <div class="session-live-track">
          <span class="session-live-fill" :style="{ width: `${clock.progress}%` }"></span>
        </div>
        <p>
          Started {{ clock.startedLabel }} · ends {{ clock.endsLabel }} ·
          {{ clock.minutesLeft }} min left
        </p>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
  profile: {
    type: Object,
    required: true,
  },
  subject: {
    type: String,
    default: '',
  },
  status: {
    type: String,
    default: '',
  },
  statusLabel: {
    type: String,
    default: 'Session',
  },
  isOngoing: {
    type: Boolean,
    default: false,
  },
  clock: {
    type: Object,
    default: () => ({
      formattedElapsed: '00:00:00',
      progress: 0,
      startedLabel: 'N/A',
      endsLabel: 'N/A',
      minutesLeft: 0,
    }),
  },
})

const normalizedStatus = computed(() => String(props.status || '').toLowerCase())
const avatarLoadError = ref(false)
const avatarUrl = computed(() => String(props.profile.avatar || '').trim())

watch(
  avatarUrl,
  () => {
    avatarLoadError.value = false
  },
)

const initials = computed(() => {
  const parts = String(props.profile.name || '')
    .split(' ')
    .filter(Boolean)

  return parts
    .slice(0, 2)
    .map((part) => part[0])
    .join('')
    .toUpperCase() || 'SB'
})

const statusClass = computed(() => {
  if (props.isOngoing) {
    return 'session-status-ongoing'
  }

  if (['pending'].includes(normalizedStatus.value)) {
    return 'session-status-pending'
  }

  if (['upcoming'].includes(normalizedStatus.value)) {
    return 'session-status-upcoming'
  }

  if (['payment required', 'awaiting verification'].includes(normalizedStatus.value)) {
    return 'session-status-awaiting'
  }

  if (['completed'].includes(normalizedStatus.value)) {
    return 'session-status-completed'
  }

  if (['rejected', 'cancelled'].includes(normalizedStatus.value)) {
    return 'session-status-stopped'
  }

  return 'session-status-neutral'
})
</script>

<style scoped>
.session-card {
  position: relative;
  overflow: hidden;
  border: 0;
  border-radius: 0;
  background: transparent;
}

.session-card:hover {
  transform: none;
}

.session-hero {
  padding: 24px;
  /* Mode-invariant anchor: stays saturated green in light and dark themes. */
  background: linear-gradient(
    135deg,
    color-mix(in srgb, var(--sb-dark) 96%, transparent),
    color-mix(in srgb, var(--sb-green-anchor) 88%, var(--sb-dark))
  );
  color: #fff;
}

.session-hero-top,
.session-live-panel {
  position: relative;
  z-index: 1;
}

.session-hero-top {
  display: flex;
  gap: 18px;
  align-items: flex-start;
}

.session-avatar {
  display: grid;
  flex: none;
  place-items: center;
  width: 104px;
  height: 104px;
  overflow: hidden;
  border: 4px solid rgba(255, 255, 255, 0.42);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.16);
  color: #fff;
  font-size: 1.7rem;
  font-weight: 850;
  box-shadow: 0 18px 36px rgba(0, 0, 0, 0.18);
  transition: transform var(--sb-t-normal) var(--sb-spring);
}

.session-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.session-hero-live .session-avatar {
  background: rgba(255, 255, 255, 0.18);
  box-shadow:
    0 18px 36px rgba(0, 0, 0, 0.18),
    0 0 0 6px rgba(142, 240, 192, 0.1);
}

.session-card:hover .session-avatar {
  transform: scale(1.03);
}

.session-hero-copy {
  min-width: 0;
  flex: 1;
}

.session-hero-title-row {
  display: flex;
  gap: 8px;
  align-items: flex-start;
  justify-content: space-between;
}

.session-hero h3 {
  margin: 0 0 2px;
  color: #fff;
  font-size: 2.3rem;
  font-weight: 850;
  letter-spacing: 0;
  line-height: 1;
}

.session-hero p {
  margin: 0;
  color: rgba(255, 255, 255, 0.74);
  font-size: 0.86rem;
}

.session-subject-pill {
  display: inline-flex;
  max-width: 100%;
  margin-top: 12px;
  padding: 6px 12px;
  overflow: hidden;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.24);
  background: rgba(255, 255, 255, 0.14);
  color: #fff;
  font-size: 0.78rem;
  font-weight: 800;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.session-status-badge {
  display: inline-flex;
  align-items: center;
  flex: none;
  gap: 6px;
  padding: 7px 12px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.24);
  background: rgba(255, 255, 255, 0.14);
  color: #fff;
  font-size: 0.74rem;
  font-weight: 850;
  line-height: 1;
  white-space: nowrap;
}

.session-status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: currentColor;
}

.session-status-dot-live {
  animation: session-status-beat 1.1s ease-in-out infinite;
}

.session-status-pending {
  color: #fff;
}

.session-status-upcoming {
  color: #fff;
}

.session-status-awaiting {
  color: #fff;
}

.session-status-completed {
  color: #fff;
}

.session-status-ongoing {
  color: #fff;
}

.session-status-stopped {
  color: #fff;
}

.session-status-neutral {
  color: #fff;
}

.session-live-panel {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  align-items: flex-end;
  margin-top: 26px;
  padding-top: 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.16);
}

.session-live-label {
  margin: 0 0 3px;
  color: rgba(255, 255, 255, 0.68);
  font-size: 0.62rem;
  font-weight: 850;
  letter-spacing: 0;
  text-transform: uppercase;
}

.session-live-timer {
  color: #fff;
  font-variant-numeric: tabular-nums;
  font-size: 3rem;
  font-weight: 800;
  letter-spacing: 0;
  line-height: 1;
}

.session-live-progress {
  min-width: 150px;
  flex: 1;
}

.session-live-track {
  height: 9px;
  overflow: hidden;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.16);
}

.session-live-fill {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, #8ef0c0, #fff2a8);
}

.session-live-progress p {
  margin-top: 7px;
  color: rgba(255, 255, 255, 0.68);
  font-size: 0.68rem;
}

@keyframes session-status-beat {
  50% {
    transform: scale(1.7);
    opacity: 0.4;
  }
}

@media (max-width: 575px) {
  .session-hero {
    padding: 18px;
  }

  .session-hero-title-row {
    flex-direction: column;
  }

  .session-avatar {
    width: 62px;
    height: 62px;
    border-width: 3px;
  }

  .session-hero h3 {
    font-size: 1.7rem;
  }

  .session-live-timer {
    font-size: 2.25rem;
  }
}

@media (prefers-reduced-motion: reduce) {
  .session-status-dot-live,
  .session-avatar {
    animation: none;
  }

  .session-card,
  .session-avatar {
    transition: none;
  }

  .session-card:hover,
  .session-card:hover .session-avatar {
    transform: none;
  }
}
</style>
