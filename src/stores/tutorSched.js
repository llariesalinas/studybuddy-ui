import { defineStore } from 'pinia'
import api from '@/services/api/api'

export const useTutorSchedStore = defineStore('tutorAvailability', {
  state: () => ({
    availabilities: [],
    isLoading: false
  }),

  actions: {

    // ===============================
    // FETCH TEMPLATE SLOTS
    // ===============================
    async fetchAvailability() {
      this.isLoading = true

      try {
        const res = await api.get('/template-availability/')
        this.availabilities = res.data
      } catch (error) {
        console.error('Failed to fetch availability:', error)
      } finally {
        this.isLoading = false
      }
    },

    // ===============================
    // ADD TEMPLATE SLOT
    // ===============================
    async addSlot(slot) {
      try {
        const res = await api.post('/template-availability/', {
          day: slot.day,
          time_slot: slot.time_slot
        })

        this.availabilities.push(res.data)
      } catch (error) {
        console.error('Failed to add slot:', error)
      }
    },

    // ===============================
    // DELETE TEMPLATE SLOT
    // ===============================
    async deleteSlot(id) {
      try {
        await api.delete(`/template-availability/${id}/`)
        this.availabilities = this.availabilities.filter(
          s => s.availability_id !== id
        )
      } catch (error) {
        console.error('Failed to delete slot:', error)
      }
    }
  }
})