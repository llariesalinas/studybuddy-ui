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

// Whether this application has ever had a renewal review at all.
//
// The server's document_renewal_status() reports 'verified' for *any* approved application, so
// "approved, never renewed" and "approved after renewing" are indistinguishable from the status
// alone. Without this a first-time applicant who just got approved is told "Renewal Approved".
// `has_document_renewal_history` is the authoritative flag; the timestamp keys are a fallback for
// payload shapes that predate it.
export const hasRenewalHistory = (application) => {
  if (application?.has_document_renewal_history !== undefined) {
    return readBoolean(application, ['has_document_renewal_history'])
  }

  // Fallbacks for payload shapes that predate the flag. A payload that is explicitly typed as a
  // renewal, or whose status is literally spelled 'renewal_*', is self-evidently one.
  const type = normalizeStatus(readFirst(application, [
    'review_type',
    'submission_type',
    'application_type',
    'document_review_type',
  ]))

  if (['renewal', 'document_renewal', 'reverification', 're_verification'].includes(type)) {
    return true
  }

  if (normalizeStatus(application?.application_status).includes('renewal')) {
    return true
  }

  return Boolean(readFirst(application, [
    'latest_document_renewal_submitted_at',
    'renewal_submitted_at',
    'document_renewal_submitted_at',
    'latest_document_renewal_id',
  ]))
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
    readBoolean(application, ['is_renewal', 'is_renewal_submission'])
  ) {
    return 'renewal'
  }

  const renewalStatus = getTutorRenewalStatus(application)
  if (['due', 'pending', 'rejected'].includes(renewalStatus)) {
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

  // Only call an approved state a *renewal* approval when a renewal was actually submitted at
  // some point. A never-renewed applicant reports renewalStatus 'approved' purely because the
  // server maps an approved application to 'verified', and falls through to the initial branch
  // below so they read "Approved", not "Renewal Approved".
  if (renewalStatus === 'approved' && hasRenewalHistory(application)) {
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

// Tutee-side booking-flow gate (closes the gap Phase 2 deliberately deferred to Phase 3, once
// /application-status was generalized for both roles). Mirrors the server's can_create_new_booking
// source of truth: gated only while tutee_verification_enforced is true, so a tutee with no
// application yet is never wrongly blocked during the grace period — see
// docs/plans/2026-07-01-tutee-verification-phase3-ui.md.
export const needsTuteeVerificationBlock = (snapshot) => {
  if (!snapshot?.tutee_verification_enforced) return false

  return !(
    snapshot?.application_status === 'approved' &&
    snapshot?.document_renewal_status === 'verified'
  )
}

// The other half of the server gate: 3 active late-cancellation strikes in the rolling window
// block new bookings regardless of verification state.
export const needsTuteeStrikeBlock = (snapshot) => Boolean(snapshot?.strike_blocked)

// Full mirror of the server's can_create_new_booking for a Tutee. The two causes are kept separate
// above because they need different remedies in the UI -- one is "verify", one is "wait it out".
export const needsTuteeBookingBlock = (snapshot) =>
  needsTuteeStrikeBlock(snapshot) || needsTuteeVerificationBlock(snapshot)
