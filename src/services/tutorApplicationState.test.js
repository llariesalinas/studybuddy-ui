import { describe, expect, it } from 'vitest'
import {
  getApplicationReviewKind,
  getReviewStatus,
  getTutorApplicationFlow,
  needsTutorApplicationAttention,
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
})
