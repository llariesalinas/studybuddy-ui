import { defineStore } from 'pinia'
import api from '@/services/api/api'

export const useTutorSchedStore = defineStore('tutorAvailability', {
  state: () => ({
    availabilities: [],
    overrides: [],
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

    async fetchOverrides(params = {}) {
      this.isLoading = true

      try {
        const res = await api.get('/availability-overrides/', {
          params,
        })
        this.overrides = res.data
      } catch (error) {
        console.error('Failed to fetch overrides:', error)
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
    },

    async createFullDayOverride(overrideDate) {
      const res = await api.post('/availability-overrides/', {
        override_date: overrideDate,
        is_full_day: true,
      })

      this.overrides.push(res.data)
      return res.data
    },

    async createSlotOverrides(overrideDate, availabilityIds) {
      const res = await api.post('/availability-overrides/', {
        override_date: overrideDate,
        is_full_day: false,
        availability_ids: availabilityIds,
      })

      this.overrides = [...this.overrides, ...res.data]
      return res.data
    },

    async deleteOverride(id) {
      await api.delete(`/availability-overrides/${id}/`)
      this.overrides = this.overrides.filter(override => override.id !== id)
    }
  }
})
