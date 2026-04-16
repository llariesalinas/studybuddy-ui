<template>
  <div class="initial-booking-content">
    <div class="card border-sb shadow-sm rounded-4" style="max-width: 600px;">
      <div class="card-body p-4 p-md-5">
        <form @submit.prevent="findTutor">

          <div class="mb-3">
            <label class="form-label fw-semibold small">Subject</label>
            <select v-model="store.selectedSubject" class="form-select border-sb shadow-none" required>
              <option v-for="subject in subjects" :key="subject.subject_code" :value="subject.subject_code">
                {{ subject.subject_name }}
              </option>
            </select>
          </div>

          <div class="row g-3 mb-3">
            <div class="col-md-6">
              <label class="form-label fw-semibold small">Date</label>
              <input
                type="date"
                v-model="store.selectedDate"
                class="form-control border-sb shadow-none"
                required
              />
            </div>

            <div class="col-md-6">
              <label class="form-label fw-semibold small">Preferred Mode</label>
              <select v-model="store.selectedMode" class="form-select border-sb shadow-none" required>
                <option v-for="mode in modes" :key="mode" :value="mode">
                  {{ mode }}
                </option>
              </select>
            </div>
          </div>

          <div class="row g-3 mb-4">
            <div class="col-6">
              <label class="form-label fw-semibold small">Time From</label>
              <button
                type="button"
                class="btn w-100 text-start border-sb shadow-none time-trigger"
                :class="{ 'time-trigger-active': activePicker === 'start' }"
                @click="openTimePicker('start')"
              >
                {{ selectedStartLabel }}
              </button>
            </div>

            <div class="col-6">
              <label class="form-label fw-semibold small">Time To</label>
              <button
                type="button"
                class="btn w-100 text-start border-sb shadow-none time-trigger"
                :class="{ 'time-trigger-active': activePicker === 'end' }"
                @click="openTimePicker('end')"
              >
                {{ selectedEndLabel }}
              </button>
            </div>
          </div>

          <div class="budget-card border-sb rounded-4 p-3 p-md-4 mb-4">
            <BudgetRangeSlider
              v-model:min-value="store.selectedBudgetMin"
              v-model:max-value="store.selectedBudgetMax"
              :min-limit="INITIAL_BUDGET_MIN"
              :max-limit="INITIAL_BUDGET_MAX"
            />
          </div>

          <div v-if="activePicker" class="time-grid-panel border-sb rounded-4 p-3 mb-4">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <div>
                <div class="fw-semibold text-dark">
                  {{ activePicker === 'start' ? 'Choose Start Time' : 'Choose End Time' }}
                </div>
                <div class="small text-muted">
                  {{ activePicker === 'start' ? 'Pick when the session begins.' : 'Pick when the session ends.' }}
                </div>
              </div>
              <button
                type="button"
                class="btn btn-sm btn-link text-decoration-none text-muted"
                @click="activePicker = null"
              >
                Close
              </button>
            </div>

            <div class="segmented-control mb-3">
              <button
                v-for="period in ['AM', 'PM']"
                :key="period"
                type="button"
                class="segmented-option"
                :class="{ 'segmented-option-active': activePeriod === period }"
                @click="activePeriod = period"
              >
                {{ period }}
              </button>
            </div>

            <div class="time-grid">
              <button
                v-for="slot in visibleTimeSlots"
                :key="`${activePicker}-${slot.value}`"
                type="button"
                class="time-chip"
                :class="{ 'time-chip-active': isSelectedTime(slot.value) }"
                @click="selectTime(slot.value)"
              >
                {{ slot.label }}
              </button>
            </div>

            <p v-if="activePicker === 'end' && !visibleTimeSlots.length" class="small text-muted mb-0 mt-3">
              Choose a start time first to see valid end times.
            </p>
          </div>

          <div class="text-end mt-4">
            <button
              type="submit"
              class="btn bg-sb-primary text-white px-5 py-2 rounded-3 fw-semibold shadow-sm d-inline-flex justify-content-center align-items-center gap-2"
              :disabled="isSubmitting"
            >
              <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-2"></span>
              {{ isSubmitting ? 'Searching...' : 'Find Tutor' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import BudgetRangeSlider from '@/components/BudgetRangeSlider.vue'
import {
  INITIAL_BUDGET_MAX,
  INITIAL_BUDGET_MIN,
  useInitialBookingPrefsStore
} from '@/stores/initialbookingprefs'
import { useFindTutorsStore } from '@/stores/findTutors'
import api from '@/services/api/api'

const router = useRouter()
const store = useInitialBookingPrefsStore()
const findTutorsStore = useFindTutorsStore()

const isSubmitting = ref(false)
const subjects = ref([])
const activePicker = ref(null)
const activePeriod = ref('AM')

const modes = ['Online', 'Face-to-face']
const timeSlotOptions = computed(() => {
  const slots = []

  for (let hour = 0; hour < 24; hour += 1) {
    for (let minute = 0; minute < 60; minute += 30) {
      const value = `${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}`
      const period = hour >= 12 ? 'PM' : 'AM'
      const displayHour = hour % 12 || 12
      const displayMinute = String(minute).padStart(2, '0')

      slots.push({
        value,
        label: `${displayHour}:${displayMinute} ${period}`
      })
    }
  }

  return slots
})
const selectedStartLabel = computed(() => formatTimeLabel(store.selectedStartTime, 'Select start time'))
const selectedEndLabel = computed(() => formatTimeLabel(store.selectedEndTime, 'Select end time'))
const visibleTimeSlots = computed(() => {
  const slots = timeSlotOptions.value.filter(slot => {
    const slotPeriod = Number(slot.value.slice(0, 2)) < 12 ? 'AM' : 'PM'

    if (slotPeriod !== activePeriod.value) {
      return false
    }

    if (activePicker.value === 'end' && store.selectedStartTime) {
      return slot.value > store.selectedStartTime
    }

    return true
  })

  return slots
})

function formatTimeLabel(value, fallback) {
  if (!value) {
    return fallback
  }

  const slot = timeSlotOptions.value.find(option => option.value === value)
  return slot ? slot.label : fallback
}

function isSelectedTime(value) {
  if (activePicker.value === 'start') {
    return store.selectedStartTime === value
  }

  return store.selectedEndTime === value
}

function openTimePicker(picker) {
  activePicker.value = activePicker.value === picker ? null : picker

  const currentValue = picker === 'start' ? store.selectedStartTime : store.selectedEndTime

  if (currentValue) {
    activePeriod.value = Number(currentValue.slice(0, 2)) < 12 ? 'AM' : 'PM'
    return
  }

  if (picker === 'end' && store.selectedStartTime) {
    activePeriod.value = Number(store.selectedStartTime.slice(0, 2)) < 12 ? 'AM' : 'PM'
    return
  }

  activePeriod.value = 'AM'
}

function nextTimeSlot(value) {
  const index = timeSlotOptions.value.findIndex(slot => slot.value === value)

  if (index === -1 || index === timeSlotOptions.value.length - 1) {
    return null
  }

  return timeSlotOptions.value[index + 1].value
}

function selectTime(value) {
  if (activePicker.value === 'start') {
    store.selectedStartTime = value

    if (!store.selectedEndTime || store.selectedEndTime <= value) {
      store.selectedEndTime = nextTimeSlot(value)
    }

    activePicker.value = 'end'

    if (store.selectedEndTime) {
      activePeriod.value = Number(store.selectedEndTime.slice(0, 2)) < 12 ? 'AM' : 'PM'
    }

    return
  }

  store.selectedEndTime = value
  activePicker.value = null
}


// Load subjects from backend
onMounted(async () => {

  try {

    const response = await api.get('/subjects/')
    subjects.value = response.data

  } catch (error) {

    console.error("Failed to load subjects", error)

  }

})


// FIND TUTOR (CBF CALL)
const findTutor = async () => {

  if (!store.selectedStartTime || !store.selectedEndTime) {
    return
  }

  isSubmitting.value = true

  try {
    // Explicit new search: clear old cached tutor results and persist fresh filters.
    findTutorsStore.reset()
    findTutorsStore.setFilters({
      subject: store.selectedSubject,
      mode: store.selectedMode,
      date: store.selectedDate,
      startTime: store.selectedStartTime,
      endTime: store.selectedEndTime,
      minRate: store.selectedBudgetMin,
      maxRate: store.selectedBudgetMax,
    })

    // Navigate to the tutor results page after saving the current search inputs.
    await router.push('/find-tutors')

  } catch (err) {

    console.error("Tutor recommendation failed", err)

  } finally {

    isSubmitting.value = false

  }

}
</script>

<style scoped>
.time-trigger {
  min-height: 42px;
  background: #fff;
  color: #212529;
}

.budget-card {
  background: linear-gradient(180deg, rgba(248, 250, 252, 0.96), #ffffff);
}

.time-trigger-active {
  border-color: var(--sb-primary, #00895a);
  box-shadow: 0 0 0 0.15rem rgba(0, 137, 90, 0.12);
}

.time-grid-panel {
  background: linear-gradient(180deg, rgba(248, 250, 252, 0.95), rgba(255, 255, 255, 1));
}

.segmented-control {
  display: inline-grid;
  grid-template-columns: repeat(2, minmax(80px, 1fr));
  padding: 4px;
  border-radius: 999px;
  background: #edf2f7;
  gap: 4px;
}

.segmented-option {
  border: 0;
  background: transparent;
  border-radius: 999px;
  padding: 0.5rem 1rem;
  font-weight: 600;
  color: #4a5568;
}

.segmented-option-active {
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
  border: 1px solid #d7dee7;
  background: #fff;
  border-radius: 14px;
  padding: 0.7rem 0.5rem;
  font-weight: 600;
  color: #243142;
}

.time-chip-active {
  border-color: var(--sb-primary, #00895a);
  background: rgba(0, 137, 90, 0.1);
  color: var(--sb-primary, #00895a);
}
</style>
