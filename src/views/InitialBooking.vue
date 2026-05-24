<template>
  <div class="initial-booking-content">
    <div class="card border-sb shadow-sm rounded-4" style="max-width: 600px">
      <div class="card-body p-4 p-md-5">
        <form @submit.prevent="findTutor">
          <div class="mb-3">
            <label class="form-label fw-semibold small">Subject</label>
            <select
              v-model="store.selectedSubject"
              class="form-select border-sb shadow-none"
              required
            >
              <option
                v-for="subject in subjects"
                :key="subject.subject_code"
                :value="subject.subject_code"
              >
                {{ subject.subject_name }}
              </option>
            </select>
          </div>

          <div class="row g-3 mb-3">
            <div class="col-md-6">
              <label class="form-label fw-semibold small">Date</label>
              <BookingDatePicker v-model="selectedDateModel" />
            </div>

            <div class="col-md-6">
              <label class="form-label fw-semibold small">Preferred Mode</label>
              <select
                v-model="store.selectedMode"
                class="form-select border-sb shadow-none"
                required
              >
                <option v-for="mode in modes" :key="mode" :value="mode">
                  {{ mode }}
                </option>
              </select>
            </div>
          </div>

          <div v-if="store.selectedMode === 'Face-to-face'" class="mb-3">
            <label class="form-label fw-semibold small">Preferred Location</label>
            <input
              type="text"
              v-model="store.selectedLocation"
              class="form-control border-sb shadow-none"
              placeholder="e.g. Library Room 3, Cafeteria..."
              required
            />
          </div>

          <div class="row g-3 mb-4">
            <div class="col-6">
              <label class="form-label fw-semibold small">Time From</label>
              <BookingTimePicker
                v-model="selectedStartTimeModel"
                :selected-date="store.selectedDate"
                title="Choose Start Time"
                placeholder="Select start time"
                empty-message="No available start times for this date."
              />
            </div>

            <div class="col-6">
              <label class="form-label fw-semibold small">Time To</label>
              <BookingTimePicker
                v-model="selectedEndTimeModel"
                ref="endTimePickerRef"
                :selected-date="store.selectedDate"
                :min-time="store.selectedStartTime"
                :disabled="!store.selectedStartTime"
                title="Choose End Time"
                placeholder="Select end time"
                empty-message="Choose a later time for the session to end."
              />
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

          <div class="text-end mt-4">
            <button
              type="submit"
              class="btn bg-sb-primary text-white px-5 py-2 rounded-3 fw-semibold shadow-sm d-inline-flex justify-content-center align-items-center gap-2 sb-btn"
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
import { computed, nextTick, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import BudgetRangeSlider from '@/components/BudgetRangeSlider.vue'
import BookingDatePicker from '@/components/BookingDatePicker.vue'
import BookingTimePicker from '@/components/BookingTimePicker.vue'
import {
  INITIAL_BUDGET_MAX,
  INITIAL_BUDGET_MIN,
  useInitialBookingPrefsStore,
} from '@/stores/initialbookingprefs'
import { useFindTutorsStore } from '@/stores/findTutors'
import api from '@/services/api/api'

const router = useRouter()
const store = useInitialBookingPrefsStore()
const findTutorsStore = useFindTutorsStore()

const isSubmitting = ref(false)
const subjects = ref([])
const endTimePickerRef = ref(null)

const modes = ['Online', 'Face-to-face']
const padNumber = (value) => String(value).padStart(2, '0')
const todayKey = () => {
  const today = new Date()
  return `${today.getFullYear()}-${padNumber(today.getMonth() + 1)}-${padNumber(today.getDate())}`
}

const isPastDate = (date) => {
  return Boolean(date) && date < todayKey()
}

const timeToMinutes = (time) => {
  const [hours = 0, minutes = 0] = String(time || '00:00')
    .split(':')
    .map(Number)
  return hours * 60 + minutes
}

const currentComparableMinutes = () => {
  const now = new Date()
  return now.getHours() * 60 + now.getMinutes() + (now.getSeconds() > 0 ? 1 : 0)
}

const isPastTimeForDate = (date, time) => {
  return (
    Boolean(date && time) && date === todayKey() && timeToMinutes(time) < currentComparableMinutes()
  )
}

const nextTimeSlot = (value) => {
  const nextMinutes = timeToMinutes(value) + 30

  if (nextMinutes >= 24 * 60) {
    return null
  }

  const hours = Math.floor(nextMinutes / 60)
  const minutes = nextMinutes % 60
  return `${padNumber(hours)}:${padNumber(minutes)}`
}

const selectedDateModel = computed({
  get: () => store.selectedDate,
  set: (value) => {
    const previousDate = store.selectedDate
    store.selectedDate = value

    if (value !== previousDate) {
      store.selectedStartTime = null
      store.selectedEndTime = null
    }
  },
})

const selectedStartTimeModel = computed({
  get: () => store.selectedStartTime,
  set: (value) => {
    store.selectedStartTime = value

    if (!store.selectedEndTime || store.selectedEndTime <= value) {
      store.selectedEndTime = nextTimeSlot(value)
    }

    nextTick(() => {
      endTimePickerRef.value?.openModal()
    })
  },
})

const selectedEndTimeModel = computed({
  get: () => store.selectedEndTime,
  set: (value) => {
    if (store.selectedStartTime && value <= store.selectedStartTime) {
      return
    }

    store.selectedEndTime = value
  },
})

// Load subjects from backend
onMounted(async () => {
  try {
    const response = await api.get('/subjects/')
    subjects.value = response.data
  } catch (error) {
    console.error('Failed to load subjects', error)
  }
})

// FIND TUTOR (CBF CALL)
const findTutor = async () => {
  if (!store.selectedDate) {
    alert('Please select a session date.')
    return
  }

  if (isPastDate(store.selectedDate)) {
    store.selectedDate = null
    alert('Please choose today or a future date.')
    return
  }

  if (!store.selectedStartTime || !store.selectedEndTime) {
    return
  }

  if (isPastTimeForDate(store.selectedDate, store.selectedStartTime)) {
    store.selectedStartTime = null
    store.selectedEndTime = null
    alert('Please choose a future start time.')
    return
  }

  if (store.selectedEndTime <= store.selectedStartTime) {
    store.selectedEndTime = null
    alert('Please choose an end time after the start time.')
    return
  }

  isSubmitting.value = true

  try {
    // Explicit new search: clear old cached tutor results and persist fresh filters.
    findTutorsStore.reset()
    findTutorsStore.setFilters({
      subject: store.selectedSubject,
      mode: store.selectedMode,
      location: store.selectedLocation,
      date: store.selectedDate,
      startTime: store.selectedStartTime,
      endTime: store.selectedEndTime,
      minRate: store.selectedBudgetMin,
      maxRate: store.selectedBudgetMax,
    })

    // Navigate to the tutor results page after saving the current search inputs.
    await router.push('/find-tutors')
  } catch (err) {
    console.error('Tutor recommendation failed', err)
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
</style>
