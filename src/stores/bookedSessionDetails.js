import { ref } from "vue";
import { defineStore } from "pinia";

export const useBookedSessionStore = defineStore('bookedSessionDetails', () => {

    const bookedSessionTutorID = ref(null)
    const bookedSessionTutorName = ref('')
    const bookedSessionSub = ref('')
    const bookedSessionTop = ref('')
    const bookedSessionMode = ref('')
    const bookedSessionDate = ref(null)
    const bookedSessions = ref([])

    const resetStore = () => {
        bookedSessionTutorID.value = null
        bookedSessionTutorName.value = ''
        bookedSessionSub.value = ''
        bookedSessionTop.value = ''
        bookedSessionMode.value = ''
        bookedSessionDate.value = null
        bookedSessions.value = []
    }

    return {
        bookedSessionTutorID,
        bookedSessionTutorName,
        bookedSessionSub,
        bookedSessionTop,
        bookedSessionMode,
        bookedSessionDate,
        bookedSessions,
        resetStore
    }
})