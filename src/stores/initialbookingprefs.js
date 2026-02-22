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
        selectedSubject = ''
        selectedTopic = ''
        selectedDate = null
        selectedMode = ''
        selectedStartTime = null
        selectedEndTime = null

    }
    return {selectedSubject, selectedTopic, selectedDate, selectedMode, selectedStartTime, selectedEndTime, resetPreferences}
})