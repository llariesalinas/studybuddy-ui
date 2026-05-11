<template>
  <div class="p-4">
    <form @submit.prevent="searchTutor" class="mb-5">
      <div class="row g-3 align-items-end">
        <!-- Subject -->
        <div class="col-lg-4 col-md-6">
          <label class="form-label fw-semibold small text-muted">Subject</label>
          <select v-model="subjectModel" class="form-select border-sb shadow-none py-2 rounded-3">
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

        <!-- Mode -->
        <div class="col-lg-2 col-md-3">
          <label class="form-label fw-semibold small text-muted">Mode</label>
          <select v-model="modeModel" class="form-select border-sb shadow-none py-2 rounded-3">
            <option v-for="mode in modes" :key="mode" :value="mode">
              {{ mode }}
            </option>
          </select>
        </div>

        <!-- Location -->
        <div v-if="modeModel === 'Face-to-face'" class="col-lg-3 col-md-3">
          <label class="form-label fw-semibold small text-muted">Location</label>
          <input
            type="text"
            v-model="locationModel"
            class="form-control border-sb shadow-none py-2 rounded-3"
            placeholder="e.g. Library"
          />
        </div>

        <!-- Date -->
        <div class="col-lg-3 col-md-6">
          <label class="form-label fw-semibold small text-muted">Date</label>
          <BookingDatePicker v-model="dateModel" />
        </div>

        <!-- Budget -->
        <div class="col-lg-3 col-md-6 subject-filter-column">
          <label class="form-label fw-semibold small text-muted">Budget Range</label>
          <div class="budget-filter-wrap">
            <button
              type="button"
              class="btn w-100 budget-toggle-btn shadow-none rounded-3"
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

        <!-- From -->
        <div class="col-lg-3 col-md-6">
          <label class="form-label fw-semibold small text-muted">Start Time</label>
          <BookingTimePicker
            v-model="startTimeModel"
            :selected-date="findTutorsStore.filters.date"
            title="Choose Start Time"
            placeholder="Select start time"
            empty-message="No available start times for this date."
          />
        </div>

        <!-- To -->
        <div class="col-lg-3 col-md-6">
          <label class="form-label fw-semibold small text-muted">End Time</label>
          <BookingTimePicker
            v-model="endTimeModel"
            ref="endTimePickerRef"
            :selected-date="findTutorsStore.filters.date"
            :min-time="findTutorsStore.filters.startTime"
            :disabled="!findTutorsStore.filters.startTime"
            title="Choose End Time"
            placeholder="Select end time"
            empty-message="Choose a later time for the session to end."
          />
        </div>

        <!-- Search Action -->
        <div class="col-lg-3 col-md-6">
          <button
            type="submit"
            class="btn bg-sb-primary text-white w-100 py-2 rounded-3 fw-bold shadow-sm"
            :disabled="isSubmitting"
          >
            <i class="bi bi-search me-2"></i>Search Tutors
          </button>
        </div>
      </div>
    </form>

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
                  style="width: 48px; height: 48px"
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
                <span class="fw-bold text-dark">P{{ tutor.hourly_rate }}</span
                ><span class="text-muted">/hr</span>
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

    <div v-else class="empty-state border-sb rounded-4 shadow-sm text-center py-5 px-4 bg-white">
      <h5 class="fw-bold text-dark mb-2">No tutors match this budget range</h5>
      <p class="text-muted mb-0">Try widening the slider range to see more tutor options.</p>
    </div>
  </div>
</template>

<script setup>
import { useRoute, useRouter, onBeforeRouteUpdate } from 'vue-router'
import api from '@/services/api/api'
import { computed, nextTick, ref, onMounted } from 'vue'
import BudgetRangeSlider from '@/components/BudgetRangeSlider.vue'
import BookingDatePicker from '@/components/BookingDatePicker.vue'
import BookingTimePicker from '@/components/BookingTimePicker.vue'

import {
  INITIAL_BUDGET_MAX,
  INITIAL_BUDGET_MIN,
  useInitialBookingPrefsStore,
} from '@/stores/initialbookingprefs'
import { useBookedSessionStore } from '@/stores/bookedSessionDetails'
import { useFindTutorsStore } from '@/stores/findTutors'

const route = useRoute()
const router = useRouter()

const initialbookStore = useInitialBookingPrefsStore()
const bookedSessionStore = useBookedSessionStore()
const findTutorsStore = useFindTutorsStore()

const isLoading = ref(true)
const isSubmitting = ref(false)
const showBudgetFilter = ref(false)
const endTimePickerRef = ref(null)

const subjects = ref([])
const matchedTutors = computed(() => findTutorsStore.results)
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

const normalizeFutureDate = (date) => {
  return isPastDate(date) ? null : date
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

const filteredTutors = computed(() =>
  matchedTutors.value.filter((tutor) => {
    const rate = Number(tutor.hourly_rate || 0)
    return rate >= findTutorsStore.filters.minRate && rate <= findTutorsStore.filters.maxRate
  }),
)

const budgetSummary = computed(() => {
  const minLabel = Number(findTutorsStore.filters.minRate || 0).toLocaleString('en-PH')
  const maxRate = Number(findTutorsStore.filters.maxRate || 0)
  const maxLabel =
    maxRate >= INITIAL_BUDGET_MAX
      ? `${maxRate.toLocaleString('en-PH')}+`
      : maxRate.toLocaleString('en-PH')

  return `₱${minLabel} - ₱${maxLabel}`
})

const syncInitialBookingPrefs = (fields) => {
  if (Object.prototype.hasOwnProperty.call(fields, 'subject')) {
    initialbookStore.selectedSubject = fields.subject
  }
  if (Object.prototype.hasOwnProperty.call(fields, 'mode')) {
    initialbookStore.selectedMode = fields.mode
  }
  if (Object.prototype.hasOwnProperty.call(fields, 'location')) {
    initialbookStore.selectedLocation = fields.location
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
  set: (value) => updateFindTutorsFilters({ subject: value }),
})

const modeModel = computed({
  get: () => findTutorsStore.filters.mode,
  set: (value) => updateFindTutorsFilters({ mode: value }),
})

const locationModel = computed({
  get: () => findTutorsStore.filters.location,
  set: (value) => updateFindTutorsFilters({ location: value }),
})

const dateModel = computed({
  get: () => findTutorsStore.filters.date,
  set: (value) => {
    const date = normalizeFutureDate(value)
    const fields = { date }

    if (date !== findTutorsStore.filters.date) {
      fields.startTime = null
      fields.endTime = null
    }

    updateFindTutorsFilters(fields)
  },
})

const minRateModel = computed({
  get: () => findTutorsStore.filters.minRate,
  set: (value) => updateFindTutorsFilters({ minRate: value }),
})

const maxRateModel = computed({
  get: () => findTutorsStore.filters.maxRate,
  set: (value) => updateFindTutorsFilters({ maxRate: value }),
})

const modes = ['Online', 'Face-to-face']
const startTimeModel = computed({
  get: () => findTutorsStore.filters.startTime,
  set: (value) => {
    updateFindTutorsFilters({ startTime: value })

    if (!findTutorsStore.filters.endTime || findTutorsStore.filters.endTime <= value) {
      updateFindTutorsFilters({ endTime: nextTimeSlot(value) })
    }

    nextTick(() => {
      endTimePickerRef.value?.openModal()
    })
  },
})

const endTimeModel = computed({
  get: () => findTutorsStore.filters.endTime,
  set: (value) => {
    if (findTutorsStore.filters.startTime && value <= findTutorsStore.filters.startTime) {
      return
    }

    updateFindTutorsFilters({ endTime: value })
  },
})

const runRecommendation = async () => {
  const response = await api.post('/recommend-tutors/', {
    subject: findTutorsStore.filters.subject,
    preferred_mode: findTutorsStore.filters.mode,
    min_budget: findTutorsStore.filters.minRate,
    max_budget: findTutorsStore.filters.maxRate,
    date: findTutorsStore.filters.date,
    start_time: findTutorsStore.filters.startTime,
    end_time: findTutorsStore.filters.endTime,
    location: findTutorsStore.filters.location,
  })

  const mappedTutors = response.data.map((tutor) => ({
    profile_id: tutor.id,
    initials: tutor.name
      .split(' ')
      .map((namePart) => namePart[0])
      .join(''),
    name: tutor.name,
    year_course: 'Tutor',
    rating: tutor.rating ?? 5.0,
    bio: 'Peer tutor available.',
    subjects: tutor.subjects ?? [],
    hourly_rate: tutor.hourly_rate ?? 150,
    total_sessions: tutor.total_sessions ?? 0,
    score: tutor.score,
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

const getNavigationFilters = (routeLike) => ({
  subject: String(
    routeLike.query.subject ||
      initialbookStore.selectedSubject ||
      findTutorsStore.filters.subject ||
      '',
  ),
  mode: initialbookStore.selectedMode || findTutorsStore.filters.mode || '',
  location: initialbookStore.selectedLocation || findTutorsStore.filters.location || '',
  date: normalizeFutureDate(initialbookStore.selectedDate || findTutorsStore.filters.date || null),
  startTime: initialbookStore.selectedStartTime || findTutorsStore.filters.startTime || null,
  endTime: initialbookStore.selectedEndTime || findTutorsStore.filters.endTime || null,
  minRate:
    initialbookStore.selectedBudgetMin ?? findTutorsStore.filters.minRate ?? INITIAL_BUDGET_MIN,
  maxRate:
    initialbookStore.selectedBudgetMax ?? findTutorsStore.filters.maxRate ?? INITIAL_BUDGET_MAX,
})

const searchTutor = async () => {
  if (!findTutorsStore.filters.date) {
    alert('Please select a session date.')
    return
  }

  if (isPastDate(findTutorsStore.filters.date)) {
    updateFindTutorsFilters({ date: null })
    alert('Please choose today or a future date.')
    return
  }

  if (!findTutorsStore.filters.startTime || !findTutorsStore.filters.endTime) {
    alert('Please select a start and end time.')
    return
  }

  if (isPastTimeForDate(findTutorsStore.filters.date, findTutorsStore.filters.startTime)) {
    updateFindTutorsFilters({ startTime: null, endTime: null })
    alert('Please choose a future start time.')
    return
  }

  if (findTutorsStore.filters.endTime <= findTutorsStore.filters.startTime) {
    updateFindTutorsFilters({ endTime: null })
    alert('Please choose an end time after the start time.')
    return
  }

  const currentFilters = {
    subject: findTutorsStore.filters.subject,
    mode: findTutorsStore.filters.mode,
    location: findTutorsStore.filters.location,
    date: findTutorsStore.filters.date,
    startTime: findTutorsStore.filters.startTime,
    endTime: findTutorsStore.filters.endTime,
    minRate: findTutorsStore.filters.minRate,
    maxRate: findTutorsStore.filters.maxRate,
  }

  // Explicit search should invalidate old cache and refetch.
  findTutorsStore.reset()
  updateFindTutorsFilters(currentFilters)

  isSubmitting.value = true
  isLoading.value = true

  try {
    await ensureFindTutorsData()
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
  bookedSessionStore.bookedSessionLocation = findTutorsStore.filters.location

  router.push(`/tutor/${tutor.profile_id}`)
}

onMounted(async () => {
  if (!findTutorsStore.hasFetched) {
    updateFindTutorsFilters(getNavigationFilters(route))
  }

  try {
    const res = await api.get('/subjects/')
    subjects.value = res.data
  } catch (error) {
    console.error('Failed to load subjects', error)
  }

  if (findTutorsStore.filters.subject) {
    try {
      await ensureFindTutorsData()
    } catch (error) {
      console.error('CBF search failed:', error)
    }
    isLoading.value = false
  } else {
    isLoading.value = false
  }
})

onBeforeRouteUpdate(async (to, from, next) => {
  if (to.name === 'tutors') {
    if (!findTutorsStore.hasFetched) {
      updateFindTutorsFilters(getNavigationFilters(to))
    }
  }

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
  transition:
    border-color 180ms ease,
    box-shadow 180ms ease,
    transform 180ms ease;
}

.budget-toggle-btn:hover {
  border-color: rgba(0, 137, 90, 0.28);
  box-shadow: 0 12px 24px rgba(10, 122, 81, 0.08);
  transform: translateY(-1px);
}

.budget-toggle-btn-active {
  border-color: var(--sb-primary, #00895a);
  box-shadow:
    0 0 0 3px rgba(0, 137, 90, 0.12),
    0 14px 28px rgba(10, 122, 81, 0.08);
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
