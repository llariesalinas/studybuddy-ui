<template>
  <section class="session-card session-hero" :class="{ 'session-hero-live': isOngoing }">
    <div v-if="isOngoing" class="session-hero-glow" aria-hidden="true"></div>
    <i v-if="isOngoing" class="session-hero-orb session-hero-orb-primary" aria-hidden="true"></i>
    <i v-if="isOngoing" class="session-hero-orb session-hero-orb-yellow" aria-hidden="true"></i>
    <i v-if="isOngoing" class="session-hero-orb session-hero-orb-pink" aria-hidden="true"></i>

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
  border: 1px solid color-mix(in srgb, var(--sb-card-border) 70%, transparent);
  border-radius: 18px;
  background: color-mix(in srgb, var(--sb-card-bg) 88%, transparent);
  box-shadow: 0 14px 36px var(--sb-shadow-soft);
  backdrop-filter: blur(10px);
  transition:
    transform var(--sb-t-normal) var(--sb-spring),
    box-shadow var(--sb-t-normal) var(--sb-spring),
    border-color var(--sb-t-normal) var(--sb-spring),
    background-color var(--sb-t-normal) var(--sb-spring);
}

.session-card:hover {
  border-color: color-mix(in srgb, var(--sb-primary) 22%, var(--sb-card-border));
  background: color-mix(in srgb, var(--sb-card-bg) 94%, transparent);
  box-shadow: 0 22px 54px color-mix(in srgb, var(--sb-shadow-soft) 74%, rgba(15, 23, 42, 0.12));
  transform: translateY(-3px);
}

.session-hero {
  padding: 24px;
}

.session-hero-live {
  border-color: var(--sb-live-hero-border);
  background: linear-gradient(
    135deg,
    var(--sb-live-hero-start),
    var(--sb-live-hero-mid) 55%,
    var(--sb-live-hero-end)
  );
}

.session-hero-glow {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(420px 240px at 82% -10%, color-mix(in srgb, var(--sb-primary-mid) 22%, transparent), transparent 70%),
    radial-gradient(300px 200px at 6% 120%, color-mix(in srgb, var(--sb-pop-yellow) 18%, transparent), transparent 70%);
  pointer-events: none;
}

.session-hero-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(9px);
  opacity: 0.4;
  pointer-events: none;
}

.session-hero-orb-primary {
  left: 62%;
  top: -8%;
  width: 40px;
  height: 40px;
  background: var(--sb-primary-mid);
  animation: session-hero-float-one 9s ease-in-out infinite alternate;
}

.session-hero-orb-yellow {
  left: 75%;
  top: 22%;
  width: 62px;
  height: 62px;
  background: var(--sb-pop-yellow);
  animation: session-hero-float-two 12s ease-in-out infinite alternate;
}

.session-hero-orb-pink {
  left: 88%;
  top: 52%;
  width: 84px;
  height: 84px;
  background: var(--sb-pop-pink);
  animation: session-hero-float-three 15s ease-in-out infinite alternate;
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
  width: 74px;
  height: 74px;
  overflow: hidden;
  border: 1px solid color-mix(in srgb, var(--sb-card-bg) 70%, transparent);
  border-radius: 18px;
  background: color-mix(in srgb, var(--sb-primary) 12%, transparent);
  color: var(--sb-primary);
  font-size: 1.25rem;
  font-weight: 800;
  box-shadow: 0 12px 28px color-mix(in srgb, var(--sb-shadow-soft) 78%, transparent);
  transition: transform var(--sb-t-normal) var(--sb-spring);
}

.session-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.session-hero-live .session-avatar {
  background: color-mix(in srgb, var(--sb-primary) 14%, transparent);
  box-shadow: 0 0 0 1px color-mix(in srgb, var(--sb-primary) 18%, transparent);
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
  color: var(--sb-text-main);
  font-size: 1.16rem;
  font-weight: 800;
  letter-spacing: 0;
  line-height: 1.18;
}

.session-hero p {
  margin: 0;
  color: var(--sb-text-muted);
  font-size: 0.8rem;
}

.session-subject-pill {
  display: inline-flex;
  max-width: 100%;
  margin-top: 7px;
  padding: 4px 11px;
  overflow: hidden;
  border-radius: 999px;
  background: color-mix(in srgb, var(--sb-primary) 10%, transparent);
  color: var(--sb-primary-dark);
  font-size: 0.72rem;
  font-weight: 700;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.session-status-badge {
  display: inline-flex;
  align-items: center;
  flex: none;
  gap: 6px;
  padding: 5px 11px;
  border-radius: 999px;
  font-size: 0.7rem;
  font-weight: 700;
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
  background: color-mix(in srgb, var(--sb-pop-yellow) 24%, var(--sb-card-bg));
  color: var(--sb-pop-yellow-deep);
}

.session-status-upcoming {
  background: color-mix(in srgb, var(--sb-info-bg) 16%, var(--sb-card-bg));
  color: var(--sb-link);
}

.session-status-awaiting {
  background: color-mix(in srgb, var(--sb-info-bg) 20%, var(--sb-card-bg));
  color: var(--sb-text-secondary);
}

.session-status-completed {
  background: color-mix(in srgb, var(--sb-primary) 16%, var(--sb-card-bg));
  color: var(--sb-primary-dark);
}

.session-status-ongoing {
  background: var(--sb-card-bg);
  color: var(--sb-primary);
  box-shadow: 0 0 0 1px color-mix(in srgb, var(--sb-primary) 40%, transparent);
}

.session-status-stopped {
  background: color-mix(in srgb, var(--sb-danger) 12%, var(--sb-card-bg));
  color: var(--sb-danger);
}

.session-status-neutral {
  background: color-mix(in srgb, var(--sb-text-muted) 12%, var(--sb-card-bg));
  color: var(--sb-text-secondary);
}

.session-live-panel {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  align-items: flex-end;
  margin-top: 26px;
  padding-top: 24px;
  border-top: 1px solid color-mix(in srgb, var(--sb-primary) 18%, var(--sb-card-border));
}

.session-live-label {
  margin: 0 0 3px;
  color: var(--sb-text-muted-green);
  font-size: 0.62rem;
  font-weight: 700;
  letter-spacing: 0;
  text-transform: uppercase;
}

.session-live-timer {
  color: var(--sb-primary);
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
  background: var(--sb-live-track);
}

.session-live-fill {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, var(--sb-primary), var(--sb-primary-mid), var(--sb-pop-yellow));
}

.session-live-progress p {
  margin-top: 7px;
  color: var(--sb-text-muted-green);
  font-size: 0.68rem;
}

@keyframes session-status-beat {
  50% {
    transform: scale(1.7);
    opacity: 0.4;
  }
}

@keyframes session-hero-float-one {
  to {
    transform: translate(8%, 6%) scale(1.15);
  }
}

@keyframes session-hero-float-two {
  to {
    transform: translate(-7%, 8%) scale(1.2);
  }
}

@keyframes session-hero-float-three {
  to {
    transform: translate(6%, -7%) scale(1.12);
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
  }

  .session-live-timer {
    font-size: 2.25rem;
  }
}

@media (prefers-reduced-motion: reduce) {
  .session-status-dot-live,
  .session-hero-orb {
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
