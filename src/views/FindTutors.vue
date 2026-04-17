<template>
    <div class="p-4">
        <form @submit.prevent="searchTutor">
            <div class="row mb-3 g-3 align-items-start">
                <div class="col-lg-3 col-md-5">
                    <label class="form-label fw-semibold small">Subject</label>
                    <select v-model="subjectModel" class="form-select">
                        <option disabled value="">Select Subject</option>
                        <option
                            v-for="subject in subjects"
                            :key="subject.subject_code"
                            :value="subject.subject_code"
                        >
                            {{ subject.subject_name }}
                        </option>
                    </select>
                </div>

                <div class="col-lg-2 col-md-3">
                    <label class="form-label fw-semibold small">Mode</label>
                    <select v-model="modeModel" class="form-select border-sb shadow-none py-2">
                        <option
                          v-for="mode in modes"
                          :key="mode"
                          :value="mode"
                        >
                          {{ mode }}
                        </option>
                    </select>
                </div>

                <div class="col-lg-2 col-md-4">
                    <label class="form-label fw-semibold small">Date</label>
                    <input type="date" v-model="dateModel" class="form-control border-sb shadow-none" required />
                </div>

                <div class="col-lg-2 col-md-3">
                    <label class="form-label fw-semibold small">From</label>
                    <button
                      type="button"
                      class="btn w-100 text-start border-sb shadow-none time-trigger"
                      :class="{ 'time-trigger-active': activePicker === 'start' }"
                      @click="openTimePicker('start')"
                    >
                      {{ selectedStartLabel }}
                    </button>
                </div>

                <div class="col-lg-2 col-md-3">
                    <label class="form-label fw-semibold small">To</label>
                    <button
                      type="button"
                      class="btn w-100 text-start border-sb shadow-none time-trigger"
                      :class="{ 'time-trigger-active': activePicker === 'end' }"
                      @click="openTimePicker('end')"
                    >
                      {{ selectedEndLabel }}
                    </button>
                </div>

                <div class="col-lg-1 col-md-2">
                    <label class="form-label fw-semibold small invisible">Search</label>
                    <button
                      type="submit"
                      class="btn bg-sb-primary text-white px-3 rounded-3 fw-semibold shadow-sm"
                      :disabled="isSubmitting"
                    >
                        Search
                    </button>
                </div>
            </div>

            <div class="row mb-5 g-3 align-items-start">
                <div class="col-lg-3 col-md-5">
                    <label class="form-label fw-semibold small">Location</label>
                    <input
                        v-model="locationModel"
                        type="text"
                        class="form-control border-sb shadow-none"
                        placeholder="e.g. Starbucks..."
                    />
                </div>

                <div class="col-lg-3 col-md-5 subject-filter-column">
                    <label class="form-label fw-semibold small">Budget</label>
                    <div class="budget-filter-wrap">
                        <button
                          type="button"
                          class="btn w-100 budget-toggle-btn shadow-none rounded-4"
                          :class="{ 'budget-toggle-btn-active': showBudgetFilter }"
                          @click="showBudgetFilter = !showBudgetFilter"
                        >
                          <span class="budget-toggle-inline">{{ budgetSummary }}</span>
                          <i class="bi" :class="showBudgetFilter ? 'bi-chevron-up' : 'bi-chevron-down'"></i>
                        </button>

                        <div v-if="showBudgetFilter" class="budget-dropdown-panel">
                          <BudgetRangeSlider
                            v-model:min-value="minRateModel"
                            v-model:max-value="maxRateModel"
                            :min-limit="INITIAL_BUDGET_MIN"
                            :max-limit="INITIAL_BUDGET_MAX"
                            variant="dropdown"
                          />
                        </div>
                    </div>
                </div>
            </div>
        </form>

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

        <div v-if="isLoading" class="text-center py-5">
            <div class="spinner-border text-sb-primary" role="status"></div>
            <p class="text-muted mt-2">Running matching algorithm...</p>
        </div>

        <div v-else-if="filteredTutors.length" class="row g-4">
            <div class="col-md-6" v-for="tutor in filteredTutors" :key="tutor.profile_id">
                <div class="card border-sb shadow-sm rounded-4 h-100">
                    <div class="card-body p-4">
                        <div class="d-flex justify-content-between align-items-start mb-3">
                            <div class="d-flex align-items-center gap-3">
                                <div
                                  class="bg-success bg-opacity-10 text-sb-primary fw-bold rounded-circle d-flex align-items-center justify-content-center"
                                  style="width: 48px; height: 48px;"
                                >
                                    {{ tutor.initials }}
                                </div>
                                <div>
                                    <h6 class="fw-bold mb-0 text-dark">{{ tutor.name }}</h6>
                                    <p class="text-muted small mb-0">{{ tutor.year_course }}</p>
                                </div>
                            </div>
                            <div class="text-end">
                                <span class="fw-bold text-warning d-flex align-items-center">
                                    <i class="bi bi-star-fill me-1"></i> {{ tutor.rating }}
                                </span>
                            </div>
                        </div>

                        <p class="small text-dark mb-3">{{ tutor.bio }}</p>

                        <div class="d-flex gap-2 mb-4 flex-wrap">
                            <span
                              v-for="subject in tutor.subjects"
                              :key="subject"
                              class="badge bg-light text-dark border border-sb"
                            >
                                {{ subject }}
                            </span>
                        </div>

                        <div class="d-flex justify-content-between align-items-center mt-auto">
                            <div class="small">
                                <span class="fw-bold text-dark">P{{ tutor.hourly_rate }}</span><span class="text-muted">/hr</span>
                                <span class="text-muted ms-2">. {{ tutor.total_sessions }} sessions</span>
                            </div>
                            <button
                                @click="toTutorDetails(tutor)"
                                class="btn bg-sb-primary text-white px-4 rounded-3 fw-semibold shadow-sm"
                            >
                                Book Session
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div v-else-if="isLoading" class="empty-state border-sb rounded-4 shadow-sm text-center py-5 px-4 bg-white">
          <h5 class="fw-bold text-dark mb-2">No tutors match this budget range</h5>
          <p class="text-muted mb-0">Try widening the slider range to see more tutor options.</p>
        </div>
    </div>
</template>

<script setup>
import { useRoute, useRouter, onBeforeRouteUpdate } from 'vue-router'
import api from '@/services/api/api'
import { computed, ref, onMounted, watch } from 'vue'
import BudgetRangeSlider from '@/components/BudgetRangeSlider.vue'

import {
  INITIAL_BUDGET_MAX,
  INITIAL_BUDGET_MIN,
  useInitialBookingPrefsStore
} from '@/stores/initialbookingprefs'
import { useBookedSessionStore } from '@/stores/bookedSessionDetails'
import { useFindTutorsStore } from '@/stores/findTutors'

const route = useRoute()
const router = useRouter()

const initialbookStore = useInitialBookingPrefsStore()
const bookedSessionStore = useBookedSessionStore()
const findTutorsStore = useFindTutorsStore()

const isLoading = ref(false)
const isSubmitting = ref(false)
const activePicker = ref(null)
const activePeriod = ref('AM')
const showBudgetFilter = ref(false)

const subjects = ref([])
const matchedTutors = computed(() => findTutorsStore.results)

const filteredTutors = computed(() =>
  matchedTutors.value.filter((tutor) => {
    const rate = Number(tutor.hourly_rate || 0)
    return (
      rate >= findTutorsStore.filters.minRate &&
      rate <= findTutorsStore.filters.maxRate
    )
  })
)

const budgetSummary = computed(() => {
  const minLabel = Number(findTutorsStore.filters.minRate || 0).toLocaleString('en-PH')
  const maxRate = Number(findTutorsStore.filters.maxRate || 0)
  const maxLabel = maxRate >= INITIAL_BUDGET_MAX
    ? `${maxRate.toLocaleString('en-PH')}+`
    : maxRate.toLocaleString('en-PH')

  return `Budget: ${minLabel}-${maxLabel} per hour`
})

const syncInitialBookingPrefs = (fields) => {
  if (Object.prototype.hasOwnProperty.call(fields, 'subject')) {
    initialbookStore.selectedSubject = fields.subject
  }
  if (Object.prototype.hasOwnProperty.call(fields, 'location')) {
    initialbookStore.selectedLocation = fields.location
  }
  if (Object.prototype.hasOwnProperty.call(fields, 'mode')) {
    initialbookStore.selectedMode = fields.mode
  }
  if (Object.prototype.hasOwnProperty.call(fields, 'date')) {
    initialbookStore.selectedDate = fields.date
  }
  if (Object.prototype.hasOwnProperty.call(fields, 'startTime')) {
    initialbookStore.selectedStartTime = fields.startTime
  }
  if (Object.prototype.hasOwnProperty.call(fields, 'endTime')) {
    initialbookStore.selectedEndTime = fields.endTime
  }
  if (Object.prototype.hasOwnProperty.call(fields, 'minRate')) {
    initialbookStore.selectedBudgetMin = fields.minRate
  }
  if (Object.prototype.hasOwnProperty.call(fields, 'maxRate')) {
    initialbookStore.selectedBudgetMax = fields.maxRate
  }
}

const updateFindTutorsFilters = (fields) => {
  findTutorsStore.setFilters(fields)
  syncInitialBookingPrefs(fields)
}

const subjectModel = computed({
  get: () => findTutorsStore.filters.subject,
  set: (value) => updateFindTutorsFilters({ subject: value })
})

const locationModel = computed({
  get: () => findTutorsStore.filters.location,
  set: (value) => updateFindTutorsFilters({ location: value })
})

const modeModel = computed({
  get: () => findTutorsStore.filters.mode,
  set: (value) => updateFindTutorsFilters({ mode: value })
})

const dateModel = computed({
  get: () => findTutorsStore.filters.date,
  set: (value) => updateFindTutorsFilters({ date: value })
})

const minRateModel = computed({
  get: () => findTutorsStore.filters.minRate,
  set: (value) => updateFindTutorsFilters({ minRate: value })
})

const maxRateModel = computed({
  get: () => findTutorsStore.filters.maxRate,
  set: (value) => updateFindTutorsFilters({ maxRate: value })
})

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

const selectedStartLabel = computed(() => formatTimeLabel(findTutorsStore.filters.startTime, 'Select start time'))
const selectedEndLabel = computed(() => formatTimeLabel(findTutorsStore.filters.endTime, 'Select end time'))
const visibleTimeSlots = computed(() => {
  return timeSlotOptions.value.filter(slot => {
    const slotPeriod = Number(slot.value.slice(0, 2)) < 12 ? 'AM' : 'PM'

    if (slotPeriod !== activePeriod.value) {
      return false
    }

    if (activePicker.value === 'end' && findTutorsStore.filters.startTime) {
      return slot.value > findTutorsStore.filters.startTime
    }

    return true
  })
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
    return findTutorsStore.filters.startTime === value
  }

  return findTutorsStore.filters.endTime === value
}

function openTimePicker(picker) {
  activePicker.value = activePicker.value === picker ? null : picker

  const currentValue = picker === 'start'
    ? findTutorsStore.filters.startTime
    : findTutorsStore.filters.endTime

  if (currentValue) {
    activePeriod.value = Number(currentValue.slice(0, 2)) < 12 ? 'AM' : 'PM'
    return
  }

  if (picker === 'end' && findTutorsStore.filters.startTime) {
    activePeriod.value = Number(findTutorsStore.filters.startTime.slice(0, 2)) < 12 ? 'AM' : 'PM'
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
    updateFindTutorsFilters({ startTime: value })

    if (!findTutorsStore.filters.endTime || findTutorsStore.filters.endTime <= value) {
      updateFindTutorsFilters({ endTime: nextTimeSlot(value) })
    }

    activePicker.value = 'end'

    if (findTutorsStore.filters.endTime) {
      activePeriod.value = Number(findTutorsStore.filters.endTime.slice(0, 2)) < 12 ? 'AM' : 'PM'
    }

    return
  }

  updateFindTutorsFilters({ endTime: value })
  activePicker.value = null
}

const runRecommendation = async () => {
  const response = await api.post('/recommend-tutors/', {
    subject: findTutorsStore.filters.subject,
    preferred_mode: findTutorsStore.filters.mode,
    min_budget: findTutorsStore.filters.minRate,
    max_budget: findTutorsStore.filters.maxRate
  })

  const mappedTutors = response.data.map(tutor => ({
    profile_id: tutor.id,
    initials: tutor.name
      .split(' ')
      .map(namePart => namePart[0])
      .join(''),
    name: tutor.name,
    year_course: 'Tutor',
    rating: tutor.rating ?? 5.0,
    bio: 'Peer tutor available.',
    subjects: tutor.subjects ?? [],
    hourly_rate: tutor.hourly_rate ?? 150,
    total_sessions: tutor.total_sessions ?? 0,
    score: tutor.score
  }))

  findTutorsStore.setResults(mappedTutors)
}

const ensureFindTutorsData = async () => {
  if (!findTutorsStore.filters.subject) {
    return
  }

  if (findTutorsStore.hasFetched) {
    return
  }

  await runRecommendation()
}

const searchTutor = async () => {
  const currentFilters = {
    subject: findTutorsStore.filters.subject,
    location: findTutorsStore.filters.location,
    mode: findTutorsStore.filters.mode,
    date: findTutorsStore.filters.date,
    startTime: findTutorsStore.filters.startTime,
    endTime: findTutorsStore.filters.endTime,
    minRate: findTutorsStore.filters.minRate,
    maxRate: findTutorsStore.filters.maxRate,
  }

  // Explicit search invalidates old cache and refetches
  findTutorsStore.reset()
  updateFindTutorsFilters(currentFilters)

  isSubmitting.value = true
  isLoading.value = true

  try {
    await runRecommendation()
  } catch (error) {
    console.error('CBF search failed:', error)
  } finally {
    isSubmitting.value = false
    isLoading.value = false
  }
}

const toTutorDetails = (tutor) => {
  bookedSessionStore.bookedSessionTutorID = tutor.profile_id
  bookedSessionStore.bookedSessionTutorName = tutor.name
  bookedSessionStore.bookedSessionSub = findTutorsStore.filters.subject
  bookedSessionStore.bookedSessionMode = findTutorsStore.filters.mode

  router.push(`/tutor/${tutor.profile_id}`)
}

// Save filters only (not results) to sessionStorage on every change
watch(() => findTutorsStore.filters, (newFilters) => {
  sessionStorage.setItem('find_tutors_filters', JSON.stringify(newFilters))
}, { deep: true })

// Save booking prefs when edited from this page
watch(() => initialbookStore.$state, (newState) => {
  sessionStorage.setItem('booking_prefs', JSON.stringify(newState))
}, { deep: true })

onMounted(async () => {
  // Restore filters from sessionStorage
  const savedFilters = sessionStorage.getItem('find_tutors_filters')
  if (savedFilters) {
    findTutorsStore.setFilters(JSON.parse(savedFilters))
  }

  // Fallback to booking prefs if no filters saved
  if (!findTutorsStore.filters.subject) {
    const savedPrefs = sessionStorage.getItem('booking_prefs')
    if (savedPrefs) {
      const parsed = JSON.parse(savedPrefs)
      findTutorsStore.setFilters({
        subject: parsed.selectedSubject,
        location: parsed.selectedLocation,
        mode: parsed.selectedMode,
        date: parsed.selectedDate,
        startTime: parsed.selectedStartTime,
        endTime: parsed.selectedEndTime,
        minRate: parsed.selectedBudgetMin,
        maxRate: parsed.selectedBudgetMax,
      })
    }
  }

  // Load subjects
  try {
    const res = await api.get('/subjects/')
    subjects.value = res.data
  } catch (error) {
    console.error('Failed to load subjects', error)
  }

  // Fetch tutors if we have a subject (ensureFindTutorsData already prevents duplicate fetches)
  if (findTutorsStore.filters.subject) {
    isLoading.value = true
    try {
      await ensureFindTutorsData()
    } catch (error) {
      console.error('CBF search failed:', error)
    } finally {
      isLoading.value = false
    }
  }
})

onBeforeRouteUpdate(async (to, from, next) => {
  if (to.name === 'tutors' && findTutorsStore.filters.subject && !findTutorsStore.hasFetched) {
    isLoading.value = true
    try {
      await ensureFindTutorsData()
    } catch (error) {
      console.error('CBF search failed:', error)
    } finally {
      isLoading.value = false
    }
  }

  next()
})
</script>

<style scoped>
.time-trigger {
  min-height: 42px;
  background: #fff;
  color: #212529;
}

.subject-filter-column {
  position: relative;
}

.budget-toggle-btn {
  min-height: 42px;
  background: #ffffff;
  border: 1px solid var(--sb-card-border, #eaeaea);
  color: #163127;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.5rem 0.85rem;
  text-align: left;
  transition: border-color 180ms ease, box-shadow 180ms ease, transform 180ms ease;
}

.budget-toggle-btn:hover {
  border-color: rgba(0, 137, 90, 0.28);
  box-shadow: 0 12px 24px rgba(10, 122, 81, 0.08);
  transform: translateY(-1px);
}

.budget-toggle-btn-active {
  border-color: var(--sb-primary, #00895a);
  box-shadow: 0 0 0 3px rgba(0, 137, 90, 0.12), 0 14px 28px rgba(10, 122, 81, 0.08);
}

.budget-toggle-inline {
  font-size: 0.95rem;
  line-height: 1.2;
  color: #163127;
  font-weight: 600;
}

.budget-toggle-btn i {
  color: var(--sb-primary, #00895a);
  font-size: 1.25rem;
}

.budget-dropdown-panel {
  position: absolute;
  top: calc(100% + 0.65rem);
  left: 0;
  width: min(520px, 92vw);
  background: linear-gradient(180deg, #ffffff, #fbfdfc);
  border: 1px solid var(--sb-card-border, #eaeaea);
  border-radius: 22px;
  box-shadow: 0 20px 44px rgba(10, 122, 81, 0.12);
  padding: 1.35rem 1.1rem 1rem;
  z-index: 25;
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

.empty-state {
  max-width: 720px;
  margin: 0 auto;
}

@media (max-width: 991px) {
  .budget-dropdown-panel {
    position: static;
    width: 100%;
    margin-top: 0.75rem;
  }
}
</style>