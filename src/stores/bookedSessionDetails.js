import { ref } from "vue";
import { defineStore } from "pinia";

export const useBookedSessionsStore = defineStore('bookedSessionDetails', () => {
    const bookedSessionTutorID = ref(null)
    const bookedSessionTutorName = ref('')
    const bookedSessionSub = ref('')
    const bookedSessionTop = ref('')
    const bookedSessionMode = ref('')
    const bookedSessionDate = ref(null)
    const bookedSessionStart = ref(null)
    const bookedSessionEnd = ref(null)

    return {bookedSessionTutorID, 
            bookedSessionTutorName, 
            bookedSessionSub, 
            bookedSessionTop, 
            bookedSessionMode, 
            bookedSessionDate, 
            bookedSessionStart, 
            bookedSessionEnd}
})