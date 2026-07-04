import { describe, expect, it } from 'vitest'
import { resolveMidpointCheckInOutcome } from './useMidpointCheckIn'

describe('resolveMidpointCheckInOutcome', () => {
  it('opens support and warns when the saved response is issues', () => {
    expect(resolveMidpointCheckInOutcome('issues', 'issues')).toEqual({
      toastMessage: 'Check-in saved. We opened support so you can tell us what happened.',
      toastType: 'warning',
      openSupport: true,
    })
  })

  it('confirms without opening support when the saved response is good', () => {
    expect(resolveMidpointCheckInOutcome('good', 'good')).toEqual({
      toastMessage: 'Check-in saved. Thanks for the update.',
      toastType: 'success',
      openSupport: false,
    })
  })

  it('flags a mismatch instead of trusting the request when the server already had a different answer', () => {
    // Regression: the backend keeps the first-ever response (get_or_create) and
    // returns it unchanged on a later submit. A caller that branched on the
    // locally-requested value would show an "issues" toast and open support even
    // though the session's saved answer stayed "good".
    expect(resolveMidpointCheckInOutcome('issues', 'good')).toEqual({
      toastMessage: 'You already checked in earlier for this session; that answer is what was saved.',
      toastType: 'warning',
      openSupport: false,
    })

    expect(resolveMidpointCheckInOutcome('good', 'issues')).toMatchObject({
      openSupport: false,
    })
  })
})
