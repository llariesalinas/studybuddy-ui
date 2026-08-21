import { defineStore } from 'pinia'
import { ref } from 'vue'
import { MAX_HOURLY_RATE, MIN_HOURLY_RATE } from '@/config'

// The tutee budget slider spans exactly the range a tutor rate can occupy -- see
// MIN_HOURLY_RATE / MAX_HOURLY_RATE in @/config. A wider range would offer budget bands that no
// tutor can ever fall into.
export const INITIAL_BUDGET_MIN = MIN_HOURLY_RATE
export const INITIAL_BUDGET_MAX = MAX_HOURLY_RATE

export const useInitialBookingPrefsStore = defineStore('initialbookingprefs', () => {
  const selectedSubject = ref('')
  const selectedDate = ref(null)
  const selectedMode = ref('Online')
  const selectedLocation = ref('')
  const selectedStartTime = ref(null)
  const selectedEndTime = ref(null)
  const selectedBudgetMin = ref(INITIAL_BUDGET_MIN)
  const selectedBudgetMax = ref(INITIAL_BUDGET_MAX)

  function $reset() {
    selectedSubject.value = ''
    selectedDate.value = null
    selectedMode.value = 'Online'
    selectedLocation.value = ''
    selectedStartTime.value = null
    selectedEndTime.value = null
    selectedBudgetMin.value = INITIAL_BUDGET_MIN
    selectedBudgetMax.value = INITIAL_BUDGET_MAX
  }

  return {
    selectedSubject,
    selectedDate,
    selectedMode,
    selectedLocation,
    selectedStartTime,
    selectedEndTime,
    selectedBudgetMin,
    selectedBudgetMax,
    $reset,
  }
}, {
  persist: {
    storage: sessionStorage,
    key: 'sb-initial-booking',
  }
})