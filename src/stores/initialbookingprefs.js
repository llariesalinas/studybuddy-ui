import { defineStore } from 'pinia'
import { ref } from 'vue'

export const INITIAL_BUDGET_MIN = 100
export const INITIAL_BUDGET_MAX = 1000

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