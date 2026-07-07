import { defineStore } from 'pinia'
import api from '@/services/api/api'

export const useProfileStore = defineStore('profile', {

  state: () => ({
    profileCompleted: false,
    applicationStatus: null,
    tutorRenewalStatus: null,
    tutorRenewalRequired: false,
    renewalStatus: null,
    renewalRequired: false,
    renewalDueAt: null,
    tuteeVerificationEnforced: false,
    walletNegative: false,
    loaded: false
  }),

  actions: {
    resetProfileState() {
      this.profileCompleted = false
      this.applicationStatus = null
      this.tutorRenewalStatus = null
      this.tutorRenewalRequired = false
      this.renewalStatus = null
      this.renewalRequired = false
      this.renewalDueAt = null
      this.tuteeVerificationEnforced = false
      this.walletNegative = false
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
      this.renewalStatus = res.data.document_renewal_status || null
      this.renewalRequired = Boolean(res.data.document_renewal_required)
      this.renewalDueAt = res.data.document_renewal_due_at || null
      this.tuteeVerificationEnforced = Boolean(res.data.tutee_verification_enforced)
      this.walletNegative = Boolean(res.data.wallet_negative)
      this.loaded = true

      return res.data
    }

  }

})
