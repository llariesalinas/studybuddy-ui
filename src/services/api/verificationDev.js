// Self-service verification dev tools. The backend endpoints 403 unless
// VERIFICATION_DEV_TOOLS_ENABLED is set, so these are inert outside dev environments.
// See docs/plans/2026-07-02-verification-dev-tools.md.
import api from './api'

export const VERIFICATION_STATES = [
  'not_submitted',
  'initial_pending',
  'initial_rejected',
  'verified',
  'renewal_due',
  'renewal_pending',
  'renewal_rejected',
]

export const getVerificationDevState = () => api.get('dev/verification/')

export const setVerificationDevState = (state) =>
  api.post('dev/verification/set-state/', { state })

export const setVerificationDevEnforcement = (mode) =>
  api.post('dev/verification/enforcement/', { mode })
