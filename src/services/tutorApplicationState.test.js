import { describe, expect, it } from 'vitest'
import {
  getApplicationReviewKind,
  getReviewStatus,
  getTutorApplicationFlow,
  hasRenewalHistory,
  needsTutorApplicationAttention,
  needsTutorApplicationLockout,
  needsTuteeBookingBlock,
  needsTuteeVerificationBlock,
} from './tutorApplicationState'

describe('tutor application state helpers', () => {
  it('keeps rejected first-time applications in the initial resubmission flow', () => {
    const application = {
      application_status: 'rejected',
      rejection_reason: 'Missing COR',
    }

    expect(getApplicationReviewKind(application)).toBe('initial')
    expect(getTutorApplicationFlow(application)).toEqual({
      kind: 'initial',
      status: 'rejected',
      needsUpload: true,
    })
    expect(needsTutorApplicationAttention(application)).toBe(true)
  })

  it('routes approved tutors with due renewal documents into the renewal upload flow', () => {
    const application = {
      application_status: 'approved',
      renewal_required: true,
    }

    expect(getApplicationReviewKind(application)).toBe('renewal')
    expect(getReviewStatus(application)).toBe('due')
    expect(getTutorApplicationFlow(application)).toEqual({
      kind: 'renewal',
      status: 'due',
      needsUpload: true,
    })
    expect(needsTutorApplicationAttention(application)).toBe(true)
  })

  it('keeps explicit initial admin rows from being treated as renewal reviews', () => {
    const application = {
      review_type: 'initial',
      application_status: 'approved',
      renewal_required: true,
    }

    expect(getApplicationReviewKind(application)).toBe('initial')
    expect(getReviewStatus(application)).toBe('approved')
  })

  it('keeps fully verified approved applications in the initial review bucket', () => {
    const application = {
      application_status: 'approved',
      document_renewal_status: 'verified',
    }

    expect(getApplicationReviewKind(application)).toBe('initial')
    expect(getReviewStatus(application)).toBe('approved')
  })

  it('treats pending renewal review as attention-worthy without requesting another upload', () => {
    const application = {
      application_status: 'approved',
      renewal_status: 'pending',
    }

    expect(getTutorApplicationFlow(application)).toEqual({
      kind: 'renewal',
      status: 'pending',
      needsUpload: false,
    })
    expect(needsTutorApplicationAttention(application)).toBe(true)
  })

  it('does not route approved renewal reviews back to the action-required page', () => {
    const application = {
      application_status: 'renewal_approved',
    }

    expect(getTutorApplicationFlow(application)).toEqual({
      kind: 'renewal',
      status: 'approved',
      needsUpload: false,
    })
    expect(needsTutorApplicationAttention(application)).toBe(false)
  })

  // The server reports document_renewal_status 'verified' for *any* approved application, so
  // without the renewal-history flag a first-time applicant was labelled "Renewal Approved".
  it('calls a freshly approved first-time application an initial approval, not a renewal', () => {
    const application = {
      application_status: 'approved',
      document_renewal_status: 'verified',
      has_document_renewal_history: false,
    }

    expect(hasRenewalHistory(application)).toBe(false)
    expect(getTutorApplicationFlow(application)).toEqual({
      kind: 'initial',
      status: 'approved',
      needsUpload: false,
    })
    expect(needsTutorApplicationAttention(application)).toBe(false)
  })

  it('still calls an approval a renewal once the tutor has actually renewed', () => {
    const application = {
      application_status: 'approved',
      document_renewal_status: 'verified',
      has_document_renewal_history: true,
    }

    expect(hasRenewalHistory(application)).toBe(true)
    expect(getTutorApplicationFlow(application)).toEqual({
      kind: 'renewal',
      status: 'approved',
      needsUpload: false,
    })
  })

  it('infers renewal history from a renewal timestamp when the flag is absent', () => {
    expect(hasRenewalHistory({
      application_status: 'approved',
      latest_document_renewal_submitted_at: '2026-05-01T00:00:00Z',
    })).toBe(true)
    expect(hasRenewalHistory({ application_status: 'approved' })).toBe(false)
  })

  // A renewal that has come due on a first application is still genuinely a renewal -- the
  // history gate must not swallow the due/pending/rejected branch.
  it('keeps a due renewal in the renewal flow even with no prior renewal history', () => {
    const application = {
      application_status: 'approved',
      document_renewal_status: 'due',
      has_document_renewal_history: false,
    }

    expect(getTutorApplicationFlow(application)).toEqual({
      kind: 'renewal',
      status: 'due',
      needsUpload: true,
    })
  })

  it('locks out a never-approved (pending) tutor globally', () => {
    const application = { application_status: 'pending' }

    expect(needsTutorApplicationLockout(application)).toBe(true)
  })

  it('locks out a never-approved (rejected) tutor globally', () => {
    const application = { application_status: 'rejected' }

    expect(needsTutorApplicationLockout(application)).toBe(true)
  })

  it('does not globally lock out a renewal-due approved tutor (forward-only)', () => {
    const application = {
      application_status: 'approved',
      renewal_required: true,
    }

    expect(needsTutorApplicationAttention(application)).toBe(true)
    expect(needsTutorApplicationLockout(application)).toBe(false)
  })

  it('does not globally lock out a renewal-pending or renewal-rejected approved tutor', () => {
    expect(needsTutorApplicationLockout({
      application_status: 'approved',
      renewal_status: 'pending',
    })).toBe(false)
    expect(needsTutorApplicationLockout({
      application_status: 'approved',
      renewal_status: 'rejected',
    })).toBe(false)
  })

  it('does not lock out a fully verified, approved tutor', () => {
    const application = { application_status: 'approved' }

    expect(needsTutorApplicationLockout(application)).toBe(false)
  })
})

describe('needsTuteeVerificationBlock', () => {
  it('never blocks during the grace period, regardless of application state', () => {
    expect(needsTuteeVerificationBlock({
      tutee_verification_enforced: false,
      application_status: null,
      document_renewal_status: null,
    })).toBe(false)
  })

  it('blocks a tutee with no application once enforcement is active', () => {
    expect(needsTuteeVerificationBlock({
      tutee_verification_enforced: true,
      application_status: null,
      document_renewal_status: null,
    })).toBe(true)
  })

  it('blocks a tutee whose renewal is due once enforcement is active', () => {
    expect(needsTuteeVerificationBlock({
      tutee_verification_enforced: true,
      application_status: 'approved',
      document_renewal_status: 'due',
    })).toBe(true)
  })

  it('does not block a fully verified tutee once enforcement is active', () => {
    expect(needsTuteeVerificationBlock({
      tutee_verification_enforced: true,
      application_status: 'approved',
      document_renewal_status: 'verified',
    })).toBe(false)
  })
})

describe('needsTuteeBookingBlock', () => {
  it('blocks a fully verified tutee who is at the strike cap', () => {
    expect(needsTuteeBookingBlock({
      tutee_verification_enforced: true,
      application_status: 'approved',
      document_renewal_status: 'verified',
      strike_blocked: true,
    })).toBe(true)
  })

  it('blocks a strike-free tutee who is unverified', () => {
    expect(needsTuteeBookingBlock({
      tutee_verification_enforced: true,
      application_status: null,
      document_renewal_status: null,
      strike_blocked: false,
    })).toBe(true)
  })

  it('does not block when neither cause applies', () => {
    expect(needsTuteeBookingBlock({
      tutee_verification_enforced: true,
      application_status: 'approved',
      document_renewal_status: 'verified',
      strike_blocked: false,
    })).toBe(false)
  })

  it('blocks on strikes even during the verification grace period', () => {
    expect(needsTuteeBookingBlock({
      tutee_verification_enforced: false,
      application_status: null,
      document_renewal_status: null,
      strike_blocked: true,
    })).toBe(true)
  })
})
