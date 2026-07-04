export const MIDPOINT_RESPONSE_GOOD = 'good'
export const MIDPOINT_RESPONSE_ISSUES = 'issues'

/**
 * The server keeps the first-ever midpoint response for a session
 * (get_or_create on the backend), so a later submit can come back with a
 * different value than what was just sent - e.g. a second tab, or a stale
 * reopened modal, submitting after someone already checked in. Callers must
 * branch on what the server actually saved, not on the request they made.
 */
export const resolveMidpointCheckInOutcome = (requestedResponse, savedResponse) => {
  if (savedResponse !== requestedResponse) {
    return {
      toastMessage: 'You already checked in earlier for this session; that answer is what was saved.',
      toastType: 'warning',
      openSupport: false,
    }
  }

  if (savedResponse === MIDPOINT_RESPONSE_ISSUES) {
    return {
      toastMessage: 'Check-in saved. We opened support so you can tell us what happened.',
      toastType: 'warning',
      openSupport: true,
    }
  }

  return {
    toastMessage: 'Check-in saved. Thanks for the update.',
    toastType: 'success',
    openSupport: false,
  }
}
