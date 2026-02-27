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

    return {bookedSessionTutorID, 
            bookedSessionTutorName, 
            bookedSessionSub, 
            bookedSessionTop, 
            bookedSessionMode, 
            bookedSessionDate, 
            bookedSessions}
})