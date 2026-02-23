import { defineStore } from 'pinia';
import {ref} from 'vue'

export const useBookingPrefsStore = defineStore ('bookingPrefs', () => {
    const bookedSessions = ref([])

    const addBookings = (slots) => {
        bookedSessions.value = slots
    }

    return {bookedSessions, addBookings}
})