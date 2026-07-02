<template>
  <section v-if="profileStore.loaded" class="glass-segment verification-segment">
    <div class="segment-header">
      <span class="segment-icon" :class="toneClass"><i :class="iconClass"></i></span>
      <div>
        <h2 class="segment-title">Enrollment Verification</h2>
        <p class="segment-copy">{{ subtitle }}</p>
      </div>
    </div>
    <div class="verification-body">
      <span class="verification-badge" :class="toneClass">{{ badgeLabel }}</span>
      <router-link v-if="showAction" to="/application-status" class="verification-action-btn">
        {{ actionLabel }}
      </router-link>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { useProfileStore } from '@/stores/profile'

const profileStore = useProfileStore()

const daysUntilDue = computed(() => {
  if (!profileStore.renewalDueAt) return null
  const diffMs = new Date(profileStore.renewalDueAt).getTime() - Date.now()
  return Math.ceil(diffMs / (1000 * 60 * 60 * 24))
})

const state = computed(() => {
  if (profileStore.applicationStatus === 'approved') {
    switch (profileStore.renewalStatus) {
      case 'due': return 'renewal_due'
      case 'pending': return 'renewal_pending'
      case 'rejected': return 'renewal_rejected'
      default: return 'verified'
    }
  }

  switch (profileStore.applicationStatus) {
    case 'pending': return 'initial_pending'
    case 'rejected': return 'initial_rejected'
    default: return 'not_submitted'
  }
})

// One entry per state, grouping all four display properties together — keeps them in sync (a
// per-property lookup table risks silently missing a state in one of the four when a new state
// is added).
const STATE_CONFIG = {
  verified: {
    tone: 'tone-success',
    icon: 'bi bi-patch-check-fill',
    badge: 'Renewed ✓',
    showAction: false,
  },
  renewal_due: {
    tone: 'tone-warning',
    icon: 'bi bi-exclamation-circle-fill',
    badge: 'Renewal Required',
    subtitle: 'Upload updated documents to keep your access current.',
    showAction: true,
  },
  renewal_pending: {
    tone: 'tone-info',
    icon: 'bi bi-hourglass-split',
    badge: 'Renewal Pending Review',
    subtitle: 'An admin is reviewing your updated documents.',
    showAction: false,
  },
  renewal_rejected: {
    tone: 'tone-danger',
    icon: 'bi bi-exclamation-triangle-fill',
    badge: 'Renewal Not Approved',
    subtitle: 'Your renewal submission needs corrections.',
    showAction: true,
  },
  initial_pending: {
    tone: 'tone-info',
    icon: 'bi bi-hourglass-split',
    badge: 'Application Pending Review',
    subtitle: 'An admin is reviewing your submitted documents.',
    showAction: false,
  },
  initial_rejected: {
    tone: 'tone-danger',
    icon: 'bi bi-exclamation-triangle-fill',
    badge: 'Application Not Approved',
    subtitle: 'Your application needs corrections.',
    showAction: true,
  },
  not_submitted: {
    tone: 'tone-info',
    icon: 'bi bi-file-earmark-text',
    badge: 'Verification Needed',
    subtitle: 'Submit your School ID and proof of enrollment to get verified.',
    showAction: true,
  },
}

const currentConfig = computed(() => STATE_CONFIG[state.value])

const toneClass = computed(() => currentConfig.value.tone)
const iconClass = computed(() => currentConfig.value.icon)
const badgeLabel = computed(() => currentConfig.value.badge)

const subtitle = computed(() => {
  if (state.value === 'verified') {
    return daysUntilDue.value != null
      ? `Next renewal in ${daysUntilDue.value} day${daysUntilDue.value === 1 ? '' : 's'}.`
      : 'Your enrollment documents are current.'
  }

  return currentConfig.value.subtitle
})

const showAction = computed(() => currentConfig.value.showAction)
const actionLabel = computed(() => (state.value === 'not_submitted' ? 'Submit Documents' : 'Review Now'))
</script>

<style scoped>
.verification-body {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  margin-top: 0.75rem;
  flex-wrap: wrap;
}

.verification-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.35rem 0.85rem;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 700;
}

.verification-action-btn {
  display: inline-flex;
  align-items: center;
  padding: 0.5rem 1.1rem;
  border-radius: 999px;
  background: var(--sb-primary);
  color: var(--sb-primary-contrast);
  font-size: 0.85rem;
  font-weight: 700;
  text-decoration: none;
  transition: background-color 0.18s ease;
}

.verification-action-btn:hover {
  background: var(--sb-primary-hover);
}

.tone-success {
  background: color-mix(in srgb, var(--sb-primary) 16%, transparent);
  color: var(--sb-primary);
}

.tone-warning {
  background: color-mix(in srgb, var(--sb-warning-bg) 24%, transparent);
  color: var(--sb-warning-text);
}

.tone-danger {
  background: color-mix(in srgb, var(--sb-danger-bs) 16%, transparent);
  color: var(--sb-danger-bs);
}

.tone-info {
  background: var(--sb-primary-light);
  color: var(--sb-text-muted);
}

.segment-icon.tone-success {
  background: color-mix(in srgb, var(--sb-primary) 18%, transparent);
  color: var(--sb-primary);
}

.segment-icon.tone-warning {
  background: color-mix(in srgb, var(--sb-warning-bg) 24%, transparent);
  color: var(--sb-warning-text);
}

.segment-icon.tone-danger {
  background: color-mix(in srgb, var(--sb-danger-bs) 18%, transparent);
  color: var(--sb-danger-bs);
}

.segment-icon.tone-info {
  background: var(--sb-primary-light);
  color: var(--sb-primary);
}
</style>
