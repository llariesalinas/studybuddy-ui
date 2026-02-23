import { defineStore } from 'pinia';
import {ref} from 'vue'

export const usePreferenceStore = defineStore('preferences', () => {
    const selectedSubjects = ref([])
    const selectedLevel = ref(null)
    const selectedTime = ref(null)

    const resetPreferences = () => {
        selectedSubjects.value = []
        selectedLevel.value = null
        selectedTime.value = null
    }
    return {selectedSubjects, selectedLevel, selectedTime, resetPreferences}
})
