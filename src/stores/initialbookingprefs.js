import { defineStore } from 'pinia';
import { ref } from 'vue'

export const useInitialBookingPrefsStore = defineStore('initialBookingPrefs', () => {
    const selectedSubject = ref('')
    const selectedDate = ref(null)
    const selectedMode = ref('')
    const selectedStartTime = ref(null)
    const selectedEndTime = ref(null)

    const resetPreferences = () => {
        selectedSubject.value = ''
        selectedDate.value = null
        selectedMode.value = ''
        selectedStartTime.value = null
        selectedEndTime.value = null
    }

    return {
      selectedSubject,
      selectedDate,
      selectedMode,
      selectedStartTime,
      selectedEndTime,
      resetPreferences
    }
})
