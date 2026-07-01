import { describe, expect, it } from 'vitest'
import {
  getApplicationReviewKind,
  getReviewStatus,
  getTutorApplicationFlow,
  needsTutorApplicationAttention,
  needsTutorApplicationLockout,
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
