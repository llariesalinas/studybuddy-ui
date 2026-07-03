<template>
  <section class="session-card session-timeline-card">
    <h4>{{ isOngoing ? 'Live progress' : 'Session progress' }}</h4>
    <div class="session-timeline">
      <article
        v-for="(step, index) in steps"
        :key="step.title"
        class="session-timeline-step"
        :class="{
          'session-timeline-step-done': index < currentIndex,
          'session-timeline-step-now': index === currentIndex,
        }"
      >
        <span class="session-timeline-line"></span>
        <span class="session-timeline-node"></span>
        <div>
          <strong>{{ step.title }}</strong>
          <p>{{ step.caption }}</p>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: {
    type: String,
    default: '',
  },
  isOngoing: {
    type: Boolean,
    default: false,
  },
  dateLabel: {
    type: String,
    default: '',
  },
  timeLabel: {
    type: String,
    default: '',
  },
  liveCaption: {
    type: String,
    default: '',
  },
})

const normalizedStatus = computed(() => String(props.status || '').toLowerCase())

const currentIndex = computed(() => {
  if (props.isOngoing || normalizedStatus.value === 'ongoing') {
    return 2
  }

  if (normalizedStatus.value === 'completed') {
    return 4
  }

  if (['payment required', 'awaiting verification'].includes(normalizedStatus.value)) {
    return 3
  }

  if (normalizedStatus.value === 'upcoming') {
    return 1
  }

  return 0
})

const steps = computed(() => [
  {
    title: 'Requested',
    caption: normalizedStatus.value === 'pending' ? 'Waiting for confirmation' : 'Request received',
  },
  {
    title: 'Confirmed',
    caption: normalizedStatus.value === 'pending' ? 'Next step' : 'Session accepted',
  },
  {
    title: props.isOngoing ? 'In session now' : 'Session day',
    caption: props.isOngoing
      ? props.liveCaption || 'Live now'
      : [props.dateLabel, props.timeLabel].filter(Boolean).join(' · ') || 'Scheduled',
  },
  {
    title: normalizedStatus.value === 'payment required' ? 'Payment needed' : 'Completed',
    caption: normalizedStatus.value === 'awaiting verification' ? 'Payment under review' : 'Paid and wrapped',
  },
])
</script>

<style scoped>
.session-card {
  border: 0;
  border-radius: 0;
  background: transparent;
}

.session-card:hover {
  transform: none;
}

.session-timeline-card {
  padding: 28px;
}

.session-timeline-card h4 {
  margin: 0 0 22px;
  color: var(--sb-text-main);
  font-size: 1.08rem;
  font-weight: 850;
  letter-spacing: 0;
}

.session-timeline {
  padding-left: 6px;
}

.session-timeline-step {
  position: relative;
  display: flex;
  gap: 16px;
  min-height: 76px;
  padding-bottom: 0;
  transition: transform var(--sb-t-normal) var(--sb-spring);
}

.session-timeline-step:hover {
  transform: translateX(3px);
}

.session-timeline-step:last-child {
  padding-bottom: 0;
}

.session-timeline-line {
  position: absolute;
  top: 18px;
  bottom: 0;
  left: 7px;
  width: 2px;
  background: var(--sb-border-light);
}

.session-timeline-step:last-child .session-timeline-line {
  display: none;
}

.session-timeline-node {
  position: relative;
  z-index: 1;
  flex: none;
  width: 16px;
  height: 16px;
  margin-top: 2px;
  border: 2px solid var(--sb-border-light);
  border-radius: 50%;
  background: var(--sb-card-bg);
  box-shadow: 0 0 0 4px color-mix(in srgb, var(--sb-border-light) 36%, transparent);
}

.session-timeline-step-done .session-timeline-node,
.session-timeline-step-done .session-timeline-line {
  border-color: var(--sb-primary);
  background: var(--sb-primary);
}

.session-timeline-step-now .session-timeline-node {
  border-color: var(--sb-primary);
  background: var(--sb-primary);
}

.session-timeline-step-now .session-timeline-node::after {
  content: '';
  position: absolute;
  inset: -6px;
  border: 2px solid color-mix(in srgb, var(--sb-primary) 50%, transparent);
  border-radius: inherit;
  opacity: 0;
  pointer-events: none;
  animation: session-timeline-ring 1.6s var(--sb-spring) infinite;
}

.session-timeline-step strong {
  display: block;
  color: var(--sb-text-dark);
  font-size: 0.98rem;
  font-weight: 850;
  line-height: 1.2;
}

.session-timeline-step p {
  margin: 3px 0 0;
  color: var(--sb-text-muted);
  font-size: 0.8rem;
}

.session-timeline-step-now strong {
  color: var(--sb-primary);
}

@keyframes session-timeline-ring {
  from {
    opacity: 0.8;
    transform: scale(0.65);
  }
  to {
    opacity: 0;
    transform: scale(1.45);
  }
}

@media (prefers-reduced-motion: reduce) {
  .session-timeline-step-now .session-timeline-node::after {
    animation: none;
  }

  .session-card,
  .session-timeline-step {
    transition: none;
  }

  .session-card:hover,
  .session-timeline-step:hover {
    transform: none;
  }
}

@media (max-width: 575px) {
  .session-timeline-card {
    padding: 18px;
  }
}
</style>
