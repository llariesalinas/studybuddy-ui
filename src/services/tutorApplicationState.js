const normalizeStatus = (value) => String(value || '').trim().toLowerCase().replace(/\s+/g, '_')

const readFirst = (source, keys) => {
  if (!source) return null

  for (const key of keys) {
    if (source[key] !== undefined && source[key] !== null && source[key] !== '') {
      return source[key]
    }
  }

  return null
}

const readBoolean = (source, keys) => {
  const value = readFirst(source, keys)

  if (typeof value === 'boolean') return value
  if (typeof value === 'string') return ['true', '1', 'yes'].includes(value.toLowerCase())

  return Boolean(value)
}

const mapRenewalStatus = (value) => {
  const status = normalizeStatus(value)

  if (['due', 'expired', 'required', 'needs_renewal', 'action_required'].includes(status)) {
    return 'due'
  }

  if (['pending', 'submitted', 'under_review', 'review_pending'].includes(status)) {
    return 'pending'
  }

  if (['rejected', 'declined', 'needs_correction'].includes(status)) {
    return 'rejected'
  }

  if (['approved', 'current', 'valid', 'verified', 'not_due', 'none'].includes(status)) {
    return 'approved'
  }

  if (status.startsWith('renewal_')) {
    return mapRenewalStatus(status.replace('renewal_', ''))
  }

  if (status.startsWith('document_renewal_')) {
    return mapRenewalStatus(status.replace('document_renewal_', ''))
  }

  return null
}

export const getTutorRenewalStatus = (application) => {
  const explicitStatus = readFirst(application, [
    'renewal_status',
    'document_renewal_status',
    'tutor_renewal_status',
    'enrollment_renewal_status',
    'verification_renewal_status',
  ])
  const mappedExplicitStatus = mapRenewalStatus(explicitStatus)

  if (mappedExplicitStatus) return mappedExplicitStatus

  const mappedApplicationStatus = mapRenewalStatus(application?.application_status)

  if (
    mappedApplicationStatus &&
    normalizeStatus(application?.application_status).includes('renewal')
  ) {
    return mappedApplicationStatus
  }

  if (readBoolean(application, [
    'renewal_required',
    'document_renewal_required',
    'needs_document_renewal',
    'requires_document_renewal',
  ])) {
    return 'due'
  }

  if (readBoolean(application, ['renewal_pending_review', 'document_renewal_pending'])) {
    return 'pending'
  }

  if (readBoolean(application, ['renewal_rejected', 'document_renewal_rejected'])) {
    return 'rejected'
  }

  return null
}

export const getApplicationReviewKind = (application) => {
  const type = normalizeStatus(readFirst(application, [
    'review_type',
    'submission_type',
    'application_type',
    'document_review_type',
  ]))

  if (['initial', 'first_time', 'first-time'].includes(type)) {
    return 'initial'
  }

  if (
    ['renewal', 'document_renewal', 'reverification', 're_verification'].includes(type) ||
    readBoolean(application, ['is_renewal', 'is_renewal_submission']) ||
    getTutorRenewalStatus(application)
  ) {
    return 'renewal'
  }

  return 'initial'
}

export const getReviewStatus = (application) => {
  if (getApplicationReviewKind(application) === 'renewal') {
    return getTutorRenewalStatus(application) || normalizeStatus(application?.application_status)
  }

  return normalizeStatus(application?.application_status)
}

export const getReviewSubmittedAt = (application) => {
  if (getApplicationReviewKind(application) === 'renewal') {
    return readFirst(application, [
      'renewal_submitted_at',
      'document_renewal_submitted_at',
      'renewal_requested_at',
      'submitted_at',
    ])
  }

  return application?.submitted_at
}

export const getReviewReviewedAt = (application) => {
  if (getApplicationReviewKind(application) === 'renewal') {
    return readFirst(application, [
      'renewal_reviewed_at',
      'document_renewal_reviewed_at',
      'reviewed_at',
    ])
  }

  return application?.reviewed_at
}

export const getReviewRejectionReason = (application) => {
  if (getApplicationReviewKind(application) === 'renewal') {
    return readFirst(application, [
      'renewal_rejection_reason',
      'document_renewal_rejection_reason',
      'rejection_reason',
    ])
  }

  return application?.rejection_reason
}

export const getTutorApplicationFlow = (application) => {
  const renewalStatus = getTutorRenewalStatus(application)
  const initialStatus = normalizeStatus(application?.application_status)

  if (['due', 'pending', 'rejected'].includes(renewalStatus)) {
    return {
      kind: 'renewal',
      status: renewalStatus,
      needsUpload: ['due', 'rejected'].includes(renewalStatus),
    }
  }

  if (renewalStatus === 'approved') {
    return {
      kind: 'renewal',
      status: 'approved',
      needsUpload: false,
    }
  }

  if (['pending', 'approved', 'rejected'].includes(initialStatus)) {
    return {
      kind: 'initial',
      status: initialStatus,
      needsUpload: initialStatus === 'rejected',
    }
  }

  return {
    kind: getApplicationReviewKind(application),
    status: initialStatus || renewalStatus || '',
    needsUpload: false,
  }
}

export const needsTutorApplicationAttention = (application) => {
  const flow = getTutorApplicationFlow(application)

  return (
    (flow.kind === 'initial' && ['pending', 'rejected'].includes(flow.status)) ||
    (flow.kind === 'renewal' && ['due', 'pending', 'rejected'].includes(flow.status))
  )
}

// Narrower than needsTutorApplicationAttention: true only for a never-approved (initial) tutor.
// Used by the router's global lockout — a renewal-due/pending/rejected tutor is forward-only
// (blocked only from booking/accept surfaces, not the whole app) per
// docs/plans/2026-07-01-tutee-verification-phase2-gate.md.
export const needsTutorApplicationLockout = (application) => {
  const flow = getTutorApplicationFlow(application)

  return flow.kind === 'initial' && ['pending', 'rejected'].includes(flow.status)
}
