import { defineStore } from 'pinia';
import {ref} from 'vue'

export const usePreferenceStore = defineStore('preferences', () => {
    const selectedSubjects = ref([])
    const selectedLevel = ref(null)
    const selectedTime = ref(null)

    const resetPreferences = () => {
        selectedSubjects = []
        selectedLevel = null
        selectedTime = null
    }
    return {selectedSubjects, selectedLevel, selectedTime, resetPreferences}
})