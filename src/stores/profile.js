import { defineStore } from 'pinia'
import api from '@/services/api/api'

export const useProfileStore = defineStore('profile', {

  state: () => ({
    profileCompleted: false,
    applicationStatus: null,
    loaded: false
  }),

  actions: {
    resetProfileState() {
      this.profileCompleted = false
      this.applicationStatus = null
      this.loaded = false
    },

    async checkProfileStatus() {

      const res = await api.get('/profile/status/')

      this.profileCompleted = res.data.profile_completed
      this.applicationStatus = res.data.application_status || null
      this.loaded = true

      return res.data
    }

  }

})
