<template>
  <div
    v-if="bannerContext && !dismissed"
    class="chat-banner"
    :class="`chat-banner--${bannerContext.status_intent}`"
  >
    <template v-if="bannerContext.status_intent === 'pending_location'">
      <div class="chat-banner__body">
        <i class="bi bi-geo-alt-fill chat-banner__icon"></i>
        <div class="chat-banner__text">
          <span class="chat-banner__label">Session Pending</span>
          <span class="chat-banner__sub">
            {{
              isTutor
                ? 'Set or confirm the meeting location.'
                : 'Suggest or confirm the meeting location.'
            }}
          </span>
        </div>
      </div>

      <div class="chat-banner__action">
        <div v-if="editing" class="chat-banner__location-row">
          <input
            v-model="locationDraft"
            class="chat-banner__location-input"
            placeholder="Enter location"
            :disabled="saving"
          />
          <button
            type="button"
            class="chat-banner__btn chat-banner__btn--primary"
            :disabled="saving"
            @click="saveLocation"
          >
            {{ saving ? 'Saving...' : 'Save' }}
          </button>
          <button type="button" class="chat-banner__btn" @click="editing = false">
            Cancel
          </button>
        </div>

        <div v-else class="chat-banner__location-display">
          <span class="chat-banner__location-value">
            {{ bannerContext.preferred_location || 'No location set' }}
          </span>
          <button
            type="button"
            class="chat-banner__btn chat-banner__btn--ghost"
            @click="startEditing"
          >
            {{ isTutor ? 'Edit' : 'Suggest change' }}
          </button>
        </div>

        <p v-if="locationError" class="chat-banner__error">{{ locationError }}</p>
      </div>
    </template>

    <template v-else-if="bannerContext.status_intent === 'pending'">
      <div class="chat-banner__body">
        <i class="bi bi-hourglass-split chat-banner__icon"></i>
        <div class="chat-banner__text">
          <span class="chat-banner__label">Session Request Pending</span>
          <span class="chat-banner__sub">Waiting for confirmation.</span>
        </div>
      </div>
    </template>

    <template v-else-if="bannerContext.status_intent === 'confirmed'">
      <div class="chat-banner__body">
        <i class="bi bi-calendar-check-fill chat-banner__icon"></i>
        <div class="chat-banner__text">
          <span class="chat-banner__label">Session Confirmed</span>
          <span class="chat-banner__sub">
            {{ bannerContext.date }} - {{ bannerContext.startTime }}-{{ bannerContext.endTime }}
          </span>
        </div>
      </div>

      <RouterLink
        v-if="detailsTarget"
        :to="detailsTarget"
        class="chat-banner__btn chat-banner__btn--ghost"
      >
        View Details
      </RouterLink>
    </template>

    <template v-else-if="bannerContext.status_intent === 'awaiting_payment'">
      <div class="chat-banner__body">
        <i class="bi bi-clock-history chat-banner__icon"></i>
        <div class="chat-banner__text">
          <span class="chat-banner__label">Payment Submitted</span>
          <span class="chat-banner__sub">Awaiting payment verification.</span>
        </div>
      </div>
    </template>

    <template v-else-if="bannerContext.status_intent === 'review_pending'">
      <div class="chat-banner__body">
        <i class="bi bi-star-fill chat-banner__icon"></i>
        <div class="chat-banner__text">
          <span class="chat-banner__label">Session Completed</span>
          <span v-if="!isTutor" class="chat-banner__sub">
            How was your session? Leave a rating.
          </span>
          <span v-else class="chat-banner__sub">Waiting for the student rating.</span>
        </div>
      </div>

      <button
        v-if="!isTutor"
        type="button"
        class="chat-banner__btn chat-banner__btn--primary"
        @click="emit('rate')"
      >
        Rate Session
      </button>
    </template>

    <template v-else-if="bannerContext.status_intent === 'rejected'">
      <div class="chat-banner__body">
        <i class="bi bi-x-circle-fill chat-banner__icon"></i>
        <div class="chat-banner__text">
          <span class="chat-banner__label">Booking Rejected</span>
          <span class="chat-banner__sub">This booking was not accepted.</span>
        </div>
      </div>

      <button
        type="button"
        class="chat-banner__dismiss"
        aria-label="Dismiss"
        @click="dismissed = true"
      >
        <i class="bi bi-x"></i>
      </button>
    </template>

    <template v-else-if="bannerContext.status_intent === 'cancelled'">
      <div class="chat-banner__body">
        <i class="bi bi-slash-circle-fill chat-banner__icon"></i>
        <div class="chat-banner__text">
          <span class="chat-banner__label">Session Cancelled</span>
          <span class="chat-banner__sub">This session was cancelled.</span>
        </div>
      </div>

      <button
        type="button"
        class="chat-banner__dismiss"
        aria-label="Dismiss"
        @click="dismissed = true"
      >
        <i class="bi bi-x"></i>
      </button>
    </template>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { useChatStore } from '@/stores/chat'

const props = defineProps({
  bannerContext: {
    type: Object,
    default: null,
  },
  isTutor: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['location-saved', 'rate'])
const chatStore = useChatStore()

const editing = ref(false)
const locationDraft = ref(props.bannerContext?.preferred_location || '')
const saving = ref(false)
const locationError = ref('')
const dismissed = ref(false)

watch(
  () => props.bannerContext?.booking_request_id,
  () => {
    dismissed.value = false
    editing.value = false
    locationError.value = ''
    locationDraft.value = props.bannerContext?.preferred_location || ''
  },
)

watch(
  () => props.bannerContext?.preferred_location,
  (value) => {
    if (!editing.value) {
      locationDraft.value = value || ''
    }
  },
)

const detailsTarget = computed(() => {
  if (!props.bannerContext) return ''
  return props.isTutor ? props.bannerContext.detail_url : props.bannerContext.tutee_detail_url
})

function startEditing() {
  locationDraft.value = props.bannerContext?.preferred_location || ''
  locationError.value = ''
  editing.value = true
}

async function saveLocation() {
  const trimmed = locationDraft.value.trim()

  if (!trimmed) {
    locationError.value = 'Location is required.'
    return
  }

  saving.value = true
  locationError.value = ''

  try {
    await chatStore.updatePendingLocation(props.bannerContext.booking_request_id, trimmed)
    editing.value = false
    emit('location-saved')
  } catch (error) {
    locationError.value = error?.response?.data?.error || 'Could not update location.'
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.chat-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px 20px;
  border-bottom: 1px solid #e8e8e8;
  background: #f8f9fa;
  flex-shrink: 0;
}

.chat-banner--review_pending {
  background: linear-gradient(90deg, #edf7f3 0%, #f0f4ff 100%);
}

.chat-banner--rejected,
.chat-banner--cancelled {
  background: #fff8f6;
}

.chat-banner--confirmed {
  background: #edf7f3;
}

.chat-banner__body {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.chat-banner__icon {
  color: var(--sb-primary, #00895a);
  flex-shrink: 0;
  font-size: 16px;
}

.chat-banner--rejected .chat-banner__icon,
.chat-banner--cancelled .chat-banner__icon {
  color: #dc3545;
}

.chat-banner__text {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.chat-banner__label {
  color: #163127;
  font-size: 13px;
  font-weight: 700;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.chat-banner__sub {
  color: #6c757d;
  font-size: 12px;
  margin-top: 1px;
}

.chat-banner__action {
  flex-shrink: 0;
}

.chat-banner__location-row,
.chat-banner__location-display {
  display: flex;
  align-items: center;
  gap: 8px;
}

.chat-banner__location-display {
  gap: 10px;
}

.chat-banner__location-value {
  color: #495057;
  font-size: 13px;
}

.chat-banner__location-input {
  border: 1px solid #dee2e6;
  border-radius: 8px;
  font-size: 13px;
  min-width: 160px;
  padding: 6px 10px;
}

.chat-banner__btn {
  background: transparent;
  border: 0;
  border-radius: 8px;
  color: #495057;
  cursor: pointer;
  font-size: 13px;
  font-weight: 600;
  padding: 7px 14px;
  text-decoration: none;
}

.chat-banner__btn--primary {
  background: var(--sb-primary, #00895a);
  color: #ffffff;
}

.chat-banner__btn--ghost {
  color: var(--sb-primary, #00895a);
  font-weight: 700;
}

.chat-banner__btn:disabled {
  cursor: not-allowed;
  opacity: 0.65;
}

.chat-banner__dismiss {
  background: transparent;
  border: 0;
  color: #adb5bd;
  cursor: pointer;
  flex-shrink: 0;
  font-size: 16px;
  line-height: 1;
  padding: 4px;
}

.chat-banner__error {
  color: #dc3545;
  font-size: 12px;
  margin: 4px 0 0;
}

@media (max-width: 700px) {
  .chat-banner,
  .chat-banner__location-row,
  .chat-banner__location-display {
    align-items: stretch;
    flex-direction: column;
  }

  .chat-banner__action {
    width: 100%;
  }

  .chat-banner__location-input {
    min-width: 0;
    width: 100%;
  }
}
</style>
