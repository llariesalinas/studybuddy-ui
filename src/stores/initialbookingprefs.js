import { defineStore } from 'pinia';
import { ref } from 'vue'

export const INITIAL_BUDGET_MIN = 100
export const INITIAL_BUDGET_MAX = 1000

export const useInitialBookingPrefsStore = defineStore('initialBookingPrefs', () => {
    const selectedSubject = ref('')
    const selectedDate = ref(null)
    const selectedMode = ref('')
    const selectedStartTime = ref(null)
    const selectedEndTime = ref(null)
    const selectedBudgetMin = ref(INITIAL_BUDGET_MIN)
    const selectedBudgetMax = ref(INITIAL_BUDGET_MAX)

    const resetPreferences = () => {
        selectedSubject.value = ''
        selectedDate.value = null
        selectedMode.value = ''
        selectedStartTime.value = null
        selectedEndTime.value = null
        selectedBudgetMin.value = INITIAL_BUDGET_MIN
        selectedBudgetMax.value = INITIAL_BUDGET_MAX
    }

    return {
      selectedSubject,
      selectedDate,
      selectedMode,
      selectedStartTime,
      selectedEndTime,
      selectedBudgetMin,
      selectedBudgetMax,
      resetPreferences
    }
})
