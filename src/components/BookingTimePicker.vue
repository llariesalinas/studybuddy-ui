<template>
  <div class="time-picker-wrap">
    <button
      type="button"
      class="btn w-100 text-start border-sb shadow-none time-trigger"
      :class="{ 'time-trigger-active': isOpen }"
      :disabled="disabled"
      @click="openModal"
    >
      <span>{{ selectedTimeLabel }}</span>
      <i class="bi bi-clock"></i>
    </button>

    <Teleport to="body">
      <div v-if="isOpen" class="time-modal-backdrop" @click.self="closeModal">
        <section
          class="time-modal"
          role="dialog"
          aria-modal="true"
          aria-labelledby="booking-time-picker-title"
        >
          <header class="time-modal-header">
            <div>
              <p class="time-modal-kicker mb-1">Select Time</p>
              <h2 id="booking-time-picker-title" class="time-modal-title mb-0">
                {{ title }}
              </h2>
            </div>

            <button
              type="button"
              class="time-icon-btn"
              aria-label="Close time picker"
              @click="closeModal"
            >
              <i class="bi bi-x-lg"></i>
            </button>
          </header>

          <div class="time-segmented-control mb-3">
            <button
              v-for="period in periods"
              :key="period"
              type="button"
              class="time-segmented-option"
              :class="{ 'time-segmented-option-active': activePeriod === period }"
              @click="activePeriod = period"
            >
              {{ period }}
            </button>
          </div>

          <div class="time-grid">
            <button
              v-for="slot in visibleTimeSlots"
              :key="slot.value"
              type="button"
              class="time-chip"
              :class="{ 'time-chip-active': slot.value === modelValue }"
              :disabled="slot.disabled"
              @click="selectTime(slot.value)"
            >
              {{ slot.label }}
            </button>
          </div>

          <p v-if="!hasSelectableSlots" class="small text-muted mb-0 mt-3">
            {{ emptyMessage }}
          </p>
        </section>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: null,
  },
  selectedDate: {
    type: String,
    default: null,
  },
  minTime: {
    type: String,
    default: null,
  },
  placeholder: {
    type: String,
    default: 'Select time',
  },
  title: {
    type: String,
    default: 'Choose Time',
  },
  emptyMessage: {
    type: String,
    default: 'No available times for this selection.',
  },
  disabled: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:modelValue'])

const periods = ['AM', 'PM']
const isOpen = ref(false)
const activePeriod = ref('AM')

const padNumber = (value) => String(value).padStart(2, '0')

const todayKey = () => {
  const today = new Date()
  return `${today.getFullYear()}-${padNumber(today.getMonth() + 1)}-${padNumber(today.getDate())}`
}

const getCurrentComparableMinutes = () => {
  const now = new Date()
  return now.getHours() * 60 + now.getMinutes() + (now.getSeconds() > 0 ? 1 : 0)
}

const timeToMinutes = (time) => {
  const [hours = 0, minutes = 0] = String(time || '00:00')
    .split(':')
    .map(Number)
  return hours * 60 + minutes
}

const timeSlotOptions = computed(() => {
  const slots = []

  for (let hour = 0; hour < 24; hour += 1) {
    for (let minute = 0; minute < 60; minute += 30) {
      const value = `${padNumber(hour)}:${padNumber(minute)}`
      const period = hour >= 12 ? 'PM' : 'AM'
      const displayHour = hour % 12 || 12

      slots.push({
        value,
        period,
        label: `${displayHour}:${padNumber(minute)} ${period}`,
      })
    }
  }

  return slots
})

const selectedTimeLabel = computed(() => {
  const slot = timeSlotOptions.value.find((option) => option.value === props.modelValue)
  return slot ? slot.label : props.placeholder
})

const isPastSlot = (slotValue) => {
  if (props.selectedDate !== todayKey()) {
    return false
  }

  return timeToMinutes(slotValue) < getCurrentComparableMinutes()
}

const isBeforeMinimum = (slotValue) => {
  return Boolean(props.minTime) && timeToMinutes(slotValue) <= timeToMinutes(props.minTime)
}

const visibleTimeSlots = computed(() =>
  timeSlotOptions.value
    .filter((slot) => slot.period === activePeriod.value)
    .map((slot) => ({
      ...slot,
      disabled: isPastSlot(slot.value) || isBeforeMinimum(slot.value),
    })),
)

const hasSelectableSlots = computed(() => visibleTimeSlots.value.some((slot) => !slot.disabled))

const openModal = () => {
  if (props.disabled) {
    return
  }

  const currentValue = props.modelValue || props.minTime

  if (currentValue) {
    activePeriod.value = Number(currentValue.slice(0, 2)) < 12 ? 'AM' : 'PM'
  } else {
    activePeriod.value = 'AM'
  }

  isOpen.value = true
}

const closeModal = () => {
  isOpen.value = false
}

const selectTime = (value) => {
  if (isPastSlot(value) || isBeforeMinimum(value)) {
    return
  }

  emit('update:modelValue', value)
  closeModal()
}

defineExpose({
  openModal,
})
</script>

<style scoped>
.time-picker-wrap {
  min-width: 0;
}

.time-trigger {
  min-height: 42px;
  background: #ffffff;
  color: #212529;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.time-trigger i {
  color: #6b7280;
  flex-shrink: 0;
}

.time-trigger:disabled {
  color: #9aa7b3;
  background: #f8faf9;
  cursor: not-allowed;
}

.time-trigger-active {
  border-color: var(--sb-primary, #00895a);
  box-shadow: 0 0 0 0.15rem rgba(0, 137, 90, 0.12);
}

.time-modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 1060;
  display: grid;
  place-items: center;
  padding: 1rem;
  background: rgba(15, 23, 42, 0.44);
}

.time-modal {
  width: min(480px, 100%);
  max-height: calc(100vh - 2rem);
  overflow-y: auto;
  border-radius: 18px;
  background: #ffffff;
  box-shadow: 0 24px 60px rgba(15, 23, 42, 0.22);
  padding: 1.25rem;
}

.time-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1rem;
}

.time-modal-kicker {
  color: #6b7d74;
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.time-modal-title {
  color: #163127;
  font-size: 1.15rem;
  font-weight: 800;
}

.time-icon-btn {
  width: 36px;
  height: 36px;
  border: 0;
  border-radius: 10px;
  background: #edf6f1;
  color: #0a7a51;
  display: inline-grid;
  place-items: center;
  flex-shrink: 0;
}

.time-icon-btn:hover {
  background: #dff1e8;
}

.time-segmented-control {
  display: inline-grid;
  grid-template-columns: repeat(2, minmax(80px, 1fr));
  padding: 4px;
  border-radius: 999px;
  background: #edf2f7;
  gap: 4px;
}

.time-segmented-option {
  border: 0;
  background: transparent;
  border-radius: 999px;
  padding: 0.5rem 1rem;
  font-weight: 700;
  color: #4a5568;
}

.time-segmented-option-active {
  background: #ffffff;
  color: var(--sb-primary, #00895a);
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08);
}

.time-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(96px, 1fr));
  gap: 0.65rem;
}

.time-chip {
  min-height: 44px;
  border: 1px solid #d7dee7;
  background: #ffffff;
  border-radius: 12px;
  padding: 0.7rem 0.5rem;
  font-weight: 700;
  color: #243142;
  transition:
    background-color 150ms ease,
    border-color 150ms ease,
    color 150ms ease,
    box-shadow 150ms ease;
}

.time-chip:hover:not(:disabled) {
  border-color: rgba(0, 137, 90, 0.36);
  background: #edf7f2;
  color: #0a7a51;
}

.time-chip:disabled {
  color: #a0acb8;
  background: #f8faf9;
  cursor: not-allowed;
}

.time-chip-active {
  border-color: var(--sb-primary, #00895a);
  background: rgba(0, 137, 90, 0.1);
  color: var(--sb-primary, #00895a);
  box-shadow: 0 8px 18px rgba(0, 137, 90, 0.12);
}
</style>
