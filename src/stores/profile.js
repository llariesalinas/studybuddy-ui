import { defineStore } from 'pinia'
import api from '@/services/api/api'

export const useProfileStore = defineStore('profile', {

  state: () => ({
    profileCompleted: false,
    loaded: false
  }),

  actions: {
    resetProfileState() {
      this.profileCompleted = false
      this.loaded = false
    },

    async checkProfileStatus() {

      const res = await api.get('/profile/status/')

      this.profileCompleted = res.data.profile_completed
      this.loaded = true

      return res.data
    }

  }

})
