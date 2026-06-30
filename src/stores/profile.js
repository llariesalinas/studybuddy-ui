import { defineStore } from 'pinia'
import api from '@/services/api/api'

export const useProfileStore = defineStore('profile', {

  state: () => ({
    profileCompleted: false,
    applicationStatus: null,
    tutorRenewalStatus: null,
    tutorRenewalRequired: false,
    loaded: false
  }),

  actions: {
    resetProfileState() {
      this.profileCompleted = false
      this.applicationStatus = null
      this.tutorRenewalStatus = null
      this.tutorRenewalRequired = false
      this.loaded = false
    },

    async checkProfileStatus() {

      const res = await api.get('/profile/status/')

      this.profileCompleted = res.data.profile_completed
      this.applicationStatus = res.data.application_status || null
      this.tutorRenewalStatus =
        res.data.tutor_renewal_status ||
        res.data.renewal_status ||
        res.data.document_renewal_status ||
        null
      this.tutorRenewalRequired = Boolean(
        res.data.tutor_renewal_required ||
        res.data.renewal_required ||
        res.data.document_renewal_required ||
        res.data.needs_document_renewal
      )
      this.loaded = true

      return res.data
    }

  }

})
