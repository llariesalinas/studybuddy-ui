import { defineStore } from 'pinia';
import {ref} from 'vue'

export const useInitialBookingPrefsStore = defineStore ('preferences', () => {
    const selectedSubject = ref('')
    const selectedTopic = ref('')
    const selectedDate = ref(null)
    const selectedMode = ref('')
    const selectedStartTime = ref(null)
    const selectedEndTime = ref(null)

    const resetPreferences = () => {
        selectedSubject.value = ''
        selectedTopic.value = ''
        selectedDate.value = null
        selectedMode.value = ''
        selectedStartTime.value = null
        selectedEndTime.value = null

    }
    return {selectedSubject, selectedTopic, selectedDate, selectedMode, selectedStartTime, selectedEndTime, resetPreferences}
})
