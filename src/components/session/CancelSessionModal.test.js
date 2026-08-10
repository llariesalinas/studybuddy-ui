import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import CancelSessionModal from './CancelSessionModal.vue'

const mountModal = (props = {}) => mount(CancelSessionModal, {
  props: {
    open: true,
    cutoffLabel: 'Jun 7, 9:00 PM',
    ...props,
  },
  global: {
    stubs: {
      Teleport: true,
    },
  },
})

const confirmButton = (wrapper) =>
  wrapper.findAll('button').find(button => button.text().includes('cancel session'))

const setReason = async (wrapper, value) => {
  const field = wrapper.find('#session-cancel-reason')
  await field.setValue(value)
}

describe('CancelSessionModal', () => {
  it('renders nothing while closed', () => {
    const wrapper = mountModal({ open: false })

    expect(wrapper.find('[role="dialog"]').exists()).toBe(false)
  })

  it('shows penalty-free copy with no strike block before the cutoff', () => {
    const wrapper = mountModal({ isLate: false, strikeCount: 2 })

    expect(wrapper.text()).toContain('Cancelling now is free')
    expect(wrapper.text()).toContain('Jun 7, 9:00 PM')
    expect(wrapper.text()).not.toContain('strikes from the last 14 days')
  })

  it('shows the strike count when the cancellation is late', () => {
    const wrapper = mountModal({ isLate: true, strikeCount: 2, strikeCap: 3 })

    expect(wrapper.text()).toContain('This cancellation is late.')
    expect(wrapper.text()).toContain('You have 2 of 3 strikes from the last 14 days')
  })

  it('only mentions tickets under review when some are provisional', () => {
    const clean = mountModal({ isLate: true, strikeCount: 2, strikeProvisionalCount: 0 })
    expect(clean.text()).not.toContain('under review')

    const provisional = mountModal({ isLate: true, strikeCount: 2, strikeProvisionalCount: 1 })
    expect(provisional.text()).toContain('(1 under review)')
  })

  it('escalates the consequence copy on the strike that reaches the cap', () => {
    const below = mountModal({ isLate: true, strikeCount: 1, strikeCap: 3 })
    expect(below.text()).toContain("At 3 strikes you can't book new sessions")

    const atCap = mountModal({ isLate: true, strikeCount: 2, strikeCap: 3 })
    expect(atCap.text()).toContain('This will be your 3rd strike')
  })

  it('keeps the late warning but drops the strike lines when the count is unavailable', () => {
    const wrapper = mountModal({ isLate: true, strikesUnavailable: true, strikeCount: 2 })

    expect(wrapper.text()).toContain('This cancellation is late.')
    expect(wrapper.text()).not.toContain('strikes from the last 14 days')
    expect(wrapper.text()).not.toContain("can't book new sessions")
  })

  it('shows a skeleton instead of a stale count while refreshing', () => {
    const wrapper = mountModal({ isLate: true, strikesLoading: true, strikeCount: 2 })

    expect(wrapper.find('.session-cancel-skeleton').exists()).toBe(true)
    expect(wrapper.text()).not.toContain('You have 2 of 3 strikes')
  })

  it('requires at least five characters of reason before confirming', async () => {
    const wrapper = mountModal()

    await setReason(wrapper, 'four')
    expect(confirmButton(wrapper).attributes('disabled')).toBeDefined()

    await setReason(wrapper, 'fives')
    expect(confirmButton(wrapper).attributes('disabled')).toBeUndefined()
  })

  it('emits the trimmed reason on confirm', async () => {
    const wrapper = mountModal()

    await setReason(wrapper, '  Something urgent came up.  ')
    await confirmButton(wrapper).trigger('click')

    expect(wrapper.emitted('confirm')[0]).toEqual(['Something urgent came up.'])
  })

  it('names the counterpart the canceller has to coordinate with', () => {
    const tuteeSide = mountModal()
    expect(tuteeSide.text()).toContain('message your tutor in Chat')

    const tutorSide = mountModal({ counterpartLabel: 'tutee' })
    expect(tutorSide.text()).toContain('message your tutee in Chat')
  })

  it('warns a tutor about the wallet deduction and the search consequence', () => {
    const wrapper = mountModal({ isLate: true, walletPenalty: true, strikeCount: 1 })

    expect(wrapper.text()).toContain('₱50 is deducted from your wallet')
    expect(wrapper.text()).toContain('you stop appearing in tutee search')
  })

  it('never mentions a wallet deduction to a tutee', () => {
    const wrapper = mountModal({ isLate: true, strikeCount: 1 })

    expect(wrapper.text()).not.toContain('₱50')
    expect(wrapper.text()).toContain("you can't book new sessions")
  })

  it('leaves the penalty copy off a pending withdrawal', () => {
    const wrapper = mountModal({ isPending: true, isLate: true, strikeCount: 2 })

    expect(wrapper.text()).toContain('You can withdraw this pending request.')
    expect(wrapper.text()).not.toContain('This cancellation is late.')
    expect(wrapper.text()).not.toContain('strikes from the last 14 days')
  })
})
