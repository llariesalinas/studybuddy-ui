<template>
  <article class="booking-card" :class="[statusAccent, { compact }]">
    <div class="booking-card-head">
      <span class="booking-card-avatar" :class="statusAccent" aria-hidden="true">
        <i class="bi" :class="statusIcon"></i>
      </span>
      <div class="booking-card-headtext">
        <h4>{{ booking.subject || 'Study session' }}</h4>
        <span class="booking-card-mode">{{ booking.session_mode }}</span>
      </div>
      <span class="booking-card-pill" :class="statusAccent">{{ booking.status }}</span>
    </div>

    <div class="booking-card-grid" :class="statusAccent">
      <span><i class="bi bi-calendar3"></i>{{ booking.date }}</span>
      <span><i class="bi bi-clock"></i>{{ booking.startTime }} - {{ booking.endTime }}</span>
      <span><i class="bi bi-hourglass-split"></i>{{ booking.duration_hours }}h</span>
      <span v-if="booking.session_mode === 'F2F'">
        <i class="bi bi-geo-alt"></i>{{ booking.preferred_location || 'No location' }}
      </span>
      <a
        v-if="booking.session_mode === 'Online' && booking.meeting_link"
        :href="booking.meeting_link"
        target="_blank"
        rel="noopener noreferrer"
        class="meeting-link"
      >
        <i class="bi bi-camera-video"></i>Join session
      </a>
    </div>

    <div v-if="canEditLocation || detailsTarget" class="booking-card-footer">
      <div v-if="canEditLocation" class="location-editor">
        <div v-if="editing" class="location-edit-row">
          <input v-model="location" :disabled="saving" />
          <button type="button" :disabled="saving" @click="saveLocation">
            {{ saving ? 'Saving' : 'Save' }}
          </button>
        </div>
        <button v-else type="button" class="text-action" @click="editing = true">
          Edit location
        </button>
        <p v-if="error" class="location-error">{{ error }}</p>
      </div>

      <RouterLink v-if="detailsTarget" :to="detailsTarget" class="details-link">
        <span>View session details</span>
        <i class="bi bi-arrow-right" aria-hidden="true"></i>
      </RouterLink>
    </div>
  </article>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { useChatStore } from '@/stores/chat'

const props = defineProps({
  booking: {
    type: Object,
    required: true,
  },
  isTutor: {
    type: Boolean,
    default: false,
  },
  compact: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['location-saved'])
const chatStore = useChatStore()
const editing = ref(false)
const location = ref(props.booking.preferred_location || '')
const saving = ref(false)
const error = ref('')

watch(
  () => props.booking.preferred_location,
  (value) => {
    location.value = value || ''
  },
)

// The window itself is decided server-side (live status + before the Grace Cutoff) so this card and
// the chat banner cannot drift apart. This used to require status === 'Pending', which Instant
// Booking stopped producing -- the edit had silently become unreachable.
const canEditLocation = computed(() => {
  return Boolean(
    props.isTutor &&
      props.booking.session_mode === 'F2F' &&
      props.booking.can_edit_location &&
      props.booking.booking_request_id,
  )
})

const detailsTarget = computed(() => {
  return props.isTutor ? props.booking.detail_url : props.booking.tutee_detail_url
})

const statusAccent = computed(() => {
  const map = {
    Pending: 'booking-card--warning',
    Confirmed: 'booking-card--primary',
    Completed: 'booking-card--info',
    'Awaiting Payment Verification': 'booking-card--info',
    Rejected: 'booking-card--danger',
    Cancelled: 'booking-card--danger',
  }
  return map[props.booking.status] || 'booking-card--neutral'
})

const statusIcon = computed(() => {
  const map = {
    Pending: 'bi-hourglass-split',
    Confirmed: 'bi-calendar-check-fill',
    Completed: 'bi-check2-circle',
    'Awaiting Payment Verification': 'bi-clock-history',
    Rejected: 'bi-x-circle-fill',
    Cancelled: 'bi-slash-circle-fill',
  }
  return map[props.booking.status] || 'bi-calendar3'
})

async function saveLocation() {
  const nextLocation = location.value.trim()
  if (!nextLocation) {
    error.value = 'Location is required.'
    return
  }

  saving.value = true
  error.value = ''

  try {
    await chatStore.updatePendingLocation(props.booking.booking_request_id, nextLocation)
    editing.value = false
    emit('location-saved')
  } catch (saveError) {
    error.value = saveError.response?.data?.error || 'Could not update location.'
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.booking-card {
  background: var(--sb-card-bg);
  border: 1px solid var(--sb-card-border);
  border-radius: 16px;
  padding: 16px;
  width: 100%;
}

.booking-card.booking-card--warning {
  border-color: color-mix(in srgb, var(--sb-warning-bg) 12%, transparent);
  box-shadow: 0 10px 26px color-mix(in srgb, var(--sb-warning-bg) 8%, transparent),
    0 2px 6px color-mix(in srgb, var(--sb-text-main) 5%, transparent);
}

.booking-card.booking-card--primary {
  border-color: color-mix(in srgb, var(--sb-primary) 12%, transparent);
  box-shadow: 0 10px 26px color-mix(in srgb, var(--sb-primary) 8%, transparent),
    0 2px 6px color-mix(in srgb, var(--sb-text-main) 5%, transparent);
}

.booking-card.booking-card--info {
  border-color: color-mix(in srgb, var(--sb-info-bg) 12%, transparent);
  box-shadow: 0 10px 26px color-mix(in srgb, var(--sb-info-bg) 8%, transparent),
    0 2px 6px color-mix(in srgb, var(--sb-text-main) 5%, transparent);
}

.booking-card.booking-card--danger {
  border-color: color-mix(in srgb, var(--sb-danger-bs) 12%, transparent);
  box-shadow: 0 10px 26px color-mix(in srgb, var(--sb-danger-bs) 8%, transparent),
    0 2px 6px color-mix(in srgb, var(--sb-text-main) 5%, transparent);
}

.booking-card.booking-card--neutral {
  box-shadow: 0 10px 26px color-mix(in srgb, var(--sb-text-muted) 6%, transparent),
    0 2px 6px color-mix(in srgb, var(--sb-text-main) 5%, transparent);
}

.booking-card.compact {
  margin-top: 10px;
}

.booking-card-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.booking-card-headtext {
  flex: 1 1 auto;
  min-width: 0;
}

.booking-card-avatar {
  align-items: center;
  background: linear-gradient(
    135deg,
    color-mix(in srgb, var(--sb-text-muted) 16%, transparent),
    color-mix(in srgb, var(--sb-text-muted) 6%, transparent)
  );
  border-radius: 13px;
  color: var(--sb-text-muted);
  display: inline-flex;
  flex: 0 0 40px;
  font-size: 17px;
  height: 40px;
  justify-content: center;
  width: 40px;
}

.booking-card-avatar.booking-card--warning {
  background: linear-gradient(
    135deg,
    color-mix(in srgb, var(--sb-warning-bg) 16%, transparent),
    color-mix(in srgb, var(--sb-warning-bg) 6%, transparent)
  );
  color: var(--sb-warning-text);
}

.booking-card-avatar.booking-card--primary {
  background: linear-gradient(
    135deg,
    color-mix(in srgb, var(--sb-primary) 16%, transparent),
    color-mix(in srgb, var(--sb-primary) 6%, transparent)
  );
  color: var(--sb-primary-dark);
}

.booking-card-avatar.booking-card--info {
  background: linear-gradient(
    135deg,
    color-mix(in srgb, var(--sb-info-bg) 16%, transparent),
    color-mix(in srgb, var(--sb-info-bg) 6%, transparent)
  );
  color: #0a58ca;
}

.booking-card-avatar.booking-card--danger {
  background: linear-gradient(
    135deg,
    color-mix(in srgb, var(--sb-danger-bs) 16%, transparent),
    color-mix(in srgb, var(--sb-danger-bs) 6%, transparent)
  );
  color: var(--sb-danger-bs);
}

.booking-card h4 {
  font-size: 16px;
  font-weight: 800;
  margin: 0;
  color: var(--sb-text-main);
}

.booking-card-mode {
  color: var(--sb-text-secondary);
  display: block;
  font-size: 11px;
  line-height: 1.4;
  margin-top: 2px;
}

.booking-card-pill {
  display: inline-flex;
  flex-shrink: 0;
  font-size: 11.5px;
  font-weight: 700;
  padding: 4px 11px;
  border-radius: 999px;
  background: var(--sb-bg);
  color: var(--sb-text-muted);
  white-space: nowrap;
}

.booking-card-pill.booking-card--warning {
  background: rgba(255, 193, 7, 0.16);
  color: var(--sb-warning-text);
}

.booking-card-pill.booking-card--primary {
  background: var(--sb-primary-light);
  color: var(--sb-primary-dark);
}

.booking-card-pill.booking-card--info {
  background: rgba(13, 202, 240, 0.16);
  color: #0a58ca;
}

.booking-card-pill.booking-card--danger {
  background: rgba(220, 53, 69, 0.1);
  color: var(--sb-danger-bs);
}

.booking-card-grid {
  background: color-mix(in srgb, var(--sb-text-main) 4%, var(--sb-card-bg));
  border: 1px solid color-mix(in srgb, var(--sb-text-main) 5%, transparent);
  border-radius: 12px;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px 14px;
  padding: 10px 12px;
}

.booking-card-grid span {
  color: var(--sb-text-secondary);
  font-size: 13px;
  display: flex;
  gap: 7px;
  align-items: center;
}

.booking-card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 12px;
  border-top: 1px solid var(--sb-card-border);
  padding-top: 10px;
}

.location-editor,
.details-link {
  margin-top: 0;
}

.location-edit-row {
  display: flex;
  gap: 8px;
}

.location-edit-row input {
  background: rgba(255, 255, 255, 0.82);
  border: 1px solid rgba(222, 226, 230, 0.82);
  border-radius: 18px;
  padding: 12px 16px;
  min-width: 0;
  flex: 1;
}

.location-edit-row button,
.text-action {
  border: 0;
  background: var(--sb-primary);
  color: #ffffff;
  border-radius: 8px;
  padding: 9px 12px;
  font-weight: 700;
}

.text-action {
  background: transparent;
  color: var(--sb-primary);
  padding: 0;
}

.location-error {
  color: var(--sb-danger-bs);
  font-size: 12px;
  margin: 6px 0 0;
}

.details-link {
  color: var(--sb-primary);
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 13px;
  font-weight: 700;
  margin-left: auto;
  text-decoration: none;
}

.meeting-link {
  color: var(--sb-primary);
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 13px;
  font-weight: 700;
  text-decoration: none;
}

@media (max-width: 900px) {
  .booking-card-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 700px) {
  .booking-card-head {
    flex-wrap: wrap;
  }

  .booking-card-headtext {
    flex: 1 1 180px;
  }

  .booking-card-pill {
    margin-left: auto;
  }
}
</style>
