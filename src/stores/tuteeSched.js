// stores/useAvailabilityStore.js
import { defineStore } from 'pinia'
import axios from 'axios'

export const useTuteeSchedStore = defineStore('tutorAvailability', {
  state: () => ({
    availabilities: [],
    isLoading: false
  }),

  actions: {
    async fetchAvailability() {
      this.isLoading = true
      try {
        const res = await axios.get('/api/v1/tutors/availability/')
        this.availabilities = res.data
      } finally {
        this.isLoading = false
      }
    },

    async addSlot(slot) {
        const res = await axios.post(
            '/api/v1/tutors/availability/',
            slot
        )

        this.availabilities.push(res.data)
    },

    async updateSlot(slot) {
        const res = await axios.patch(
            `/api/v1/tutors/availability/${slot.availability_id}/`,
            {
            date: slot.date,
            start_time: slot.start_time,
            end_time: slot.end_time,
            is_active: slot.is_active
            }
        )

        const index = this.availabilities.findIndex(
            s => s.availability_id === slot.availability_id
        )

        if (index !== -1) {
            this.availabilities[index] = res.data
        }
    },

    async deleteSlot(id) {
      await axios.delete(`/api/v1/tutors/availability/${id}/`)
      this.availabilities = this.availabilities.filter(
        s => s.availability_id !== id
      )
    }
  }
})