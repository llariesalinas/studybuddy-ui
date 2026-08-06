<template>
  <div class="initial-booking-content">
    <div class="card border-sb shadow-sm rounded-4 booking-fields-card">
      <div class="card-body p-4 p-md-5">
        <form @submit.prevent="findTutor">
          <div class="mb-3">
            <label class="form-label fw-semibold small">Subject</label>
            <SubjectPickerModal v-model="selectedSubjectCodes" :subjects="subjects" />
          </div>

          <div class="row g-3 mb-3">
            <div class="col-md-6">
              <label class="form-label fw-semibold small">Date</label>
              <BookingDatePicker v-model="selectedDateModel" />
            </div>

            <div class="col-md-6">
              <label class="form-label fw-semibold small">Preferred Mode</label>
              <div class="mode-button-group" role="radiogroup" aria-label="Preferred Mode">
                <button
                  v-for="mode in modes"
                  :key="mode.value"
                  type="button"
                  class="mode-button sb-btn sb-pill"
                  :class="{ 'mode-button-active': store.selectedMode === mode.value }"
                  role="radio"
                  :aria-checked="store.selectedMode === mode.value ? 'true' : 'false'"
                  @click="selectMode(mode.value)"
                >
                  <span class="mode-button-icon" aria-hidden="true">
                    <i class="bi" :class="mode.icon"></i>
                  </span>
                  <span>{{ mode.label }}</span>
                </button>
              </div>
            </div>
          </div>

          <div v-if="store.selectedMode === 'Face-to-face' && campusLocationType" class="mb-3">
            <div class="d-flex justify-content-between align-items-center mb-1">
              <label class="form-label fw-semibold small mb-0">
                Location ({{ campusLocationType === 'inside' ? 'Inside Campus' : 'Outside Campus' }})
              </label>
              <button
                type="button"
                class="btn btn-link btn-sm p-0"
                @click="showCampusModal = true"
              >
                Change
              </button>
            </div>
            <input
              type="text"
              v-model="store.selectedLocation"
              class="form-control border-sb shadow-none sb-field"
              placeholder="e.g. Library Room 3, Cafeteria..."
              required
            />
          </div>

          <div class="mb-4">
            <label class="form-label fw-semibold small">
              Time <span class="fw-normal sb-muted">(optional)</span>
            </label>
            <BookingTimeRangePicker
              v-model:start="selectedStartTimeModel"
              v-model:end="selectedEndTimeModel"
              :selected-date="store.selectedDate"
              title="Choose a time range"
            />
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

          <CampusLocationModal
            v-model:open="showCampusModal"
            anchor-selector=".booking-fields-card"
            @select="onCampusTypeSelected"
            @cancel="onCampusModalCancelled"
          />
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import BudgetRangeSlider from '@/components/BudgetRangeSlider.vue'
import BookingDatePicker from '@/components/BookingDatePicker.vue'
import BookingTimeRangePicker from '@/components/BookingTimeRangePicker.vue'
import CampusLocationModal from '@/components/CampusLocationModal.vue'
import SubjectPickerModal from '@/components/SubjectPickerModal.vue'
import { isPastDate, isPastTimeForDate } from '@/utils/time'
import {
  INITIAL_BUDGET_MAX,
  INITIAL_BUDGET_MIN,
  useInitialBookingPrefsStore,
} from '@/stores/initialbookingprefs'
import { useCatalogStore } from '@/stores/catalog'
import { useFindTutorsStore } from '@/stores/findTutors'
import { useToastStore } from '@/stores/toast'

const router = useRouter()
const store = useInitialBookingPrefsStore()
const catalogStore = useCatalogStore()
const findTutorsStore = useFindTutorsStore()
const toastStore = useToastStore()

const isSubmitting = ref(false)
const subjects = ref([])
const showCampusModal = ref(false)
const campusLocationType = ref(null)

const modes = [
  { label: 'Online', value: 'Online', icon: 'bi-camera-video-fill' },
  { label: 'Face-to-face', value: 'Face-to-face', icon: 'bi-geo-alt-fill' },
]

const selectedSubjectCodes = computed({
  get: () => (store.selectedSubject ? [store.selectedSubject] : []),
  set: (codes) => { store.selectedSubject = codes[0] || '' },
})

const selectMode = (value) => {
  store.selectedMode = value

  if (value === 'Face-to-face') {
    showCampusModal.value = true
  } else {
    store.selectedLocation = ''
    campusLocationType.value = null
  }
}

const onCampusTypeSelected = (type) => {
  campusLocationType.value = type
}

const onCampusModalCancelled = () => {
  store.selectedMode = null
  store.selectedLocation = ''
  campusLocationType.value = null
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

// The range picker commits both bounds together, so these are plain pass-throughs -- no
// auto-filled end time and no second modal to chain open.
const selectedStartTimeModel = computed({
  get: () => store.selectedStartTime,
  set: (value) => {
    store.selectedStartTime = value
  },
})

const selectedEndTimeModel = computed({
  get: () => store.selectedEndTime,
  set: (value) => {
    store.selectedEndTime = value
  },
})

// Load subjects from backend
onMounted(async () => {
  try {
    subjects.value = await catalogStore.fetchSubjects({
      params: { recognized_only: 1 },
    })
  } catch (error) {
    console.error('Failed to load subjects', error)
  }

  if (store.selectedMode === 'Face-to-face' && campusLocationType.value === null) {
    showCampusModal.value = true
  }
})

// FIND TUTOR (CBF CALL)
const findTutor = async () => {
  if (!store.selectedSubject) {
    toastStore.push('Please select a subject.', 'warning')
    return
  }

  if (!store.selectedMode) {
    toastStore.push('Please select a preferred mode.', 'warning')
    return
  }

  if (!store.selectedDate) {
    toastStore.push('Please select a session date.', 'warning')
    return
  }

  if (isPastDate(store.selectedDate)) {
    store.selectedDate = null
    toastStore.push('Please choose today or a future date.', 'warning')
    return
  }

  // The time range is optional -- no times means "any time that day", which the recommender
  // handles by falling back to its date-only candidate stage. A half-set range can only come
  // from stale sessionStorage (the picker always commits both bounds together); drop it and
  // search the whole day rather than blocking on it.
  if (!store.selectedStartTime || !store.selectedEndTime) {
    store.selectedStartTime = null
    store.selectedEndTime = null
  } else if (isPastTimeForDate(store.selectedDate, store.selectedStartTime)) {
    store.selectedStartTime = null
    store.selectedEndTime = null
    toastStore.push('Please choose a future start time.', 'warning')
    return
  } else if (store.selectedEndTime <= store.selectedStartTime) {
    store.selectedEndTime = null
    toastStore.push('Please choose an end time after the start time.', 'warning')
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
.initial-booking-content {
  display: flex;
  justify-content: center;
  width: 100%;
}

.booking-fields-card {
  width: min(100%, 600px);
}

.mode-button-group {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}

.mode-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 44px;
  border: 1px solid var(--sb-card-border);
  border-radius: 14px;
  background: var(--sb-card-bg);
  color: var(--sb-text-main);
  padding: 9px 10px;
  font-size: 14px;
  font-weight: 700;
  line-height: 1.2;
  transition: transform var(--sb-t-normal) var(--sb-spring);
}

.mode-button:hover,
.mode-button:focus-visible {
  border-color: var(--sb-primary);
  box-shadow: 0 0 0 4px color-mix(in srgb, var(--sb-primary) 12%, transparent);
  outline: none;
}

.mode-button:active {
  transform: scale(0.98);
}

.mode-button-active {
  border-color: var(--sb-primary);
  background: color-mix(in srgb, var(--sb-primary) 12%, var(--sb-card-bg));
  color: var(--sb-primary);
}

.mode-button-icon {
  display: inline-flex;
  flex: 0 0 auto;
}

.initial-booking-content :deep(.date-trigger:hover),
.initial-booking-content :deep(.date-trigger:focus-visible),
.initial-booking-content :deep(.date-trigger-active),
.initial-booking-content :deep(.time-trigger:hover:not(:disabled)),
.initial-booking-content :deep(.time-trigger:focus-visible),
.initial-booking-content :deep(.time-trigger-active) {
  border-color: var(--sb-primary) !important;
  box-shadow: 0 0 0 4px color-mix(in srgb, var(--sb-primary) 12%, transparent) !important;
  outline: none;
  transform: none !important;
}

.initial-booking-content :deep(.date-trigger:active:not(:disabled)),
.initial-booking-content :deep(.time-trigger:active:not(:disabled)) {
  box-shadow: 0 0 0 4px color-mix(in srgb, var(--sb-primary) 12%, transparent) !important;
  transform: none !important;
}

.budget-card {
  background: linear-gradient(180deg, rgba(248, 250, 252, 0.96), #ffffff);
}
</style>
