import { defineStore } from 'pinia'
import api from '@/services/api/api'

export const useProfileStore = defineStore('profile', {

  state: () => ({
    profileCompleted: false,
    // Modes this account is provisioned for, derived server-side. False is what makes the
    // "you don't have a {role} account" modal fire instead of an auto-switch.
    canTutor: false,
    canTutee: false,
    applicationStatus: null,
    tutorRenewalStatus: null,
    tutorRenewalRequired: false,
    renewalStatus: null,
    renewalRequired: false,
    renewalDueAt: null,
    tuteeVerificationEnforced: false,
    tutorOnboardingSkippedAt: null,
    tutorOnboardingComplete: false,
    tutorSubjectCount: 0,
    tutorSubjectsCompleted: false,
    tutorRateSet: false,
    walletNegative: false,
    commissionTermsAccepted: true,
    strikeCount: 0,
    strikeCap: 3,
    strikeProvisionalCount: 0,
    strikeBlocked: false,
    strikeExpiresAt: null,
    loaded: false
  }),

  actions: {
    resetProfileState() {
      this.profileCompleted = false
      this.canTutor = false
      this.canTutee = false
      this.applicationStatus = null
      this.tutorRenewalStatus = null
      this.tutorRenewalRequired = false
      this.renewalStatus = null
      this.renewalRequired = false
      this.renewalDueAt = null
      this.tuteeVerificationEnforced = false
      this.tutorOnboardingSkippedAt = null
      this.tutorOnboardingComplete = false
      this.tutorSubjectCount = 0
      this.tutorSubjectsCompleted = false
      this.tutorRateSet = false
      this.walletNegative = false
      this.commissionTermsAccepted = true
      this.strikeCount = 0
      this.strikeCap = 3
      this.strikeProvisionalCount = 0
      this.strikeBlocked = false
      this.strikeExpiresAt = null
      this.loaded = false
    },

    async checkProfileStatus() {

      const res = await api.get('/profile/status/')

      this.profileCompleted = res.data.profile_completed
      this.canTutor = Boolean(res.data.can_tutor)
      this.canTutee = Boolean(res.data.can_tutee)
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
      this.tutorOnboardingSkippedAt = res.data.tutor_onboarding_skipped_at || null
      this.tutorOnboardingComplete = Boolean(res.data.tutor_onboarding_complete)
      this.tutorSubjectCount = res.data.tutor_subject_count || 0
      this.tutorSubjectsCompleted = Boolean(res.data.tutor_subjects_completed)
      this.tutorRateSet = Boolean(res.data.tutor_rate_set)
      this.walletNegative = Boolean(res.data.wallet_negative)
      this.commissionTermsAccepted = res.data.commission_terms_accepted !== false
      // Defaulted per field so a backend that predates late_cancellation_strikes can't NaN the UI.
      const strikes = res.data.late_cancellation_strikes || {}
      this.strikeCount = strikes.count || 0
      this.strikeCap = strikes.cap || 3
      this.strikeProvisionalCount = strikes.provisional_count || 0
      this.strikeBlocked = Boolean(strikes.blocked)
      this.strikeExpiresAt = strikes.expires_at || null
      this.loaded = true

      return res.data
    }

  }

})
