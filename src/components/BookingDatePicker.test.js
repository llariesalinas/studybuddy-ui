import { flushPromises, mount } from '@vue/test-utils'
import { afterEach, describe, expect, it } from 'vitest'
import BookingDatePicker from './BookingDatePicker.vue'

let wrapper
afterEach(() => wrapper?.unmount())

describe('Booking date dialog keyboard access', () => {
  it('contains keyboard focus, closes with Escape, and restores the trigger', async () => {
    wrapper = mount(BookingDatePicker, { attachTo: document.body })
    const trigger = wrapper.get('.date-trigger')
    trigger.element.focus()
    await trigger.trigger('click')
    await flushPromises()
    const dialog = document.querySelector('[role="dialog"]')
    expect(dialog.contains(document.activeElement)).toBe(true)
    const first = dialog.querySelector('button:not(:disabled)')
    const last = dialog.querySelector('.date-today-btn')
    last.focus()
    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Tab', bubbles: true }))
    expect(document.activeElement).toBe(first)
    document.dispatchEvent(
      new KeyboardEvent('keydown', { key: 'Tab', shiftKey: true, bubbles: true }),
    )
    expect(document.activeElement).toBe(last)
    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }))
    await flushPromises()
    expect(document.querySelector('[role="dialog"]')).toBeNull()
    expect(document.activeElement).toBe(trigger.element)
  })
})
