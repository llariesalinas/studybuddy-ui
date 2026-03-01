import { defineStore } from 'pinia'
import api from '@/services/api/api'

export const useTutorSchedStore = defineStore('tutorAvailability', {
  state: () => ({
    availabilities: [],
    isLoading: false
  }),

  actions: {
    // async fetchAvailability() {
    //   this.isLoading = true
    //   try {
    //     const res = await api.get('/availability/')
    //     this.availabilities = res.data
    //   } finally {
    //     this.isLoading = false
    //   }
    // },
    async fetchAvailability() {
        this.isLoading = true

        try {
            const today = new Date()

            // Get Monday of current week
            const monday = new Date(today)
            const dayOfWeek = monday.getDay()
            const diff = (dayOfWeek === 0 ? -6 : 1) - dayOfWeek
            monday.setDate(monday.getDate() + diff)

            monday.setHours(0,0,0,0)

            // Next week Monday
            const nextMonday = new Date(monday)
            nextMonday.setDate(monday.getDate() + 7)

            // Helper to format date
            const format = (date) => {
                const y = date.getFullYear()
                const m = String(date.getMonth() + 1).padStart(2, '0')
                const d = String(date.getDate()).padStart(2, '0')
                return `${y}-${m}-${d}`
            }

            this.availabilities = [
            // ===== CURRENT WEEK =====
            {
                availability_id: 1,
                day_of_week: 'Monday',
                date: format(new Date(monday)),
                start_time: '09:00',
                end_time: '10:00',
                is_active: true,
                is_booked: false
            },
            {
                availability_id: 6,
                day_of_week: 'Monday',
                date: format(new Date(monday)),
                start_time: '10:00',
                end_time: '11:00',
                is_active: true,
                is_booked: false
            },
            {
                availability_id: 2,
                day_of_week: 'Wednesday',
                date: format(new Date(monday.setDate(monday.getDate() + 2))),
                start_time: '13:00',
                end_time: '14:00',
                is_active: true,
                is_booked: false
            },

            // ===== NEXT WEEK =====
            {
                availability_id: 3,
                day_of_week: 'Tuesday',
                date: format(new Date(nextMonday)),
                start_time: '10:00',
                end_time: '11:00',
                is_active: true,
                is_booked: false
            },
            {
                availability_id: 4,
                day_of_week: 'Friday',
                date: format(new Date(nextMonday.setDate(nextMonday.getDate() + 3))),
                start_time: '15:00',
                end_time: '16:00',
                is_active: true,
                is_booked: false
            }
            ]

        } finally {
            this.isLoading = false
        }
    },

    async addSlot(slot) {
        const res = await api.post(
            '/availability/',
            slot
        )

        this.availabilities.push(res.data)
    },

    async updateSlot(slot) {
        const res = await api.patch(
            `/availability/${slot.availability_id}/`,
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
      await api.delete(`/availability/${id}/`)
      this.availabilities = this.availabilities.filter(
        s => s.availability_id !== id
      )
    }
  }
})