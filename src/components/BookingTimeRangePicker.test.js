import { mount } from '@vue/test-utils'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import BookingTimeRangePicker from './BookingTimeRangePicker.vue'

const mountPicker = (props = {}, options = {}) =>
  mount(BookingTimeRangePicker, {
    props: { start: null, end: null, ...props },
    ...options,
  })

const openPanel = async (wrapper) => {
  await wrapper.find('.time-trigger').trigger('click')
  return wrapper
}

const startOption = (wrapper, time) => wrapper.find(`[data-testid="time-start-${time}"]`)
const endOption = (wrapper, time) => wrapper.find(`[data-testid="time-end-${time}"]`)

describe('BookingTimeRangePicker', () => {
  describe('trigger', () => {
    it('shows the placeholder when no range is set', () => {
      const wrapper = mountPicker()
      expect(wrapper.find('.time-trigger').text()).toContain('Any time')
    })

    it('shows a collapsed range label when both bounds are set', () => {
      const wrapper = mountPicker({ start: '09:00', end: '11:00' })
      expect(wrapper.find('.time-trigger').text()).toContain('9:00 - 11:00 AM')
    })

    it('falls back to the placeholder when only one bound survives (stale storage)', () => {
      const wrapper = mountPicker({ start: '09:00', end: null })
      expect(wrapper.find('.time-trigger').text()).toContain('Any time')
    })

    it('clears both bounds without opening the dropdown', async () => {
      const wrapper = mountPicker({ start: '09:00', end: '11:00' })
      await wrapper.find('[data-testid="time-clear"]').trigger('click')

      expect(wrapper.emitted('update:start')).toEqual([[null]])
      expect(wrapper.emitted('update:end')).toEqual([[null]])
      expect(wrapper.find('.time-dropdown').exists()).toBe(false)
    })

    it('offers no clear affordance when there is nothing to clear', () => {
      const wrapper = mountPicker()
      expect(wrapper.find('[data-testid="time-clear"]').exists()).toBe(false)
    })

    it('does not open when disabled', async () => {
      const wrapper = await openPanel(mountPicker({ disabled: true }))
      expect(wrapper.find('.time-dropdown').exists()).toBe(false)
    })

    it('toggles the dropdown closed on a second click', async () => {
      const wrapper = await openPanel(mountPicker())
      expect(wrapper.find('.time-dropdown').exists()).toBe(true)

      await wrapper.find('.time-trigger').trigger('click')
      expect(wrapper.find('.time-dropdown').exists()).toBe(false)
    })
  })

  describe('start and end columns', () => {
    it('lists every hour of the day as a start option', async () => {
      const wrapper = await openPanel(mountPicker())
      expect(wrapper.findAll('[data-testid^="time-start-"]')).toHaveLength(24)
    })

    it('disables every end option until a start is chosen', async () => {
      const wrapper = await openPanel(mountPicker())

      expect(endOption(wrapper, '10:00').attributes('disabled')).toBeDefined()
      expect(endOption(wrapper, '23:00').attributes('disabled')).toBeDefined()
    })

    it('enables only later hours as ends once a start is chosen', async () => {
      const wrapper = await openPanel(mountPicker())
      await startOption(wrapper, '09:00').trigger('click')

      expect(endOption(wrapper, '08:00').attributes('disabled')).toBeDefined()
      expect(endOption(wrapper, '09:00').attributes('disabled')).toBeDefined()
      expect(endOption(wrapper, '10:00').attributes('disabled')).toBeUndefined()
    })

    it('annotates end options with the resulting duration', async () => {
      const wrapper = await openPanel(mountPicker())
      await startOption(wrapper, '09:00').trigger('click')

      expect(endOption(wrapper, '10:00').text()).toContain('1 hr')
      expect(endOption(wrapper, '12:00').text()).toContain('3 hrs')
    })

    it('cannot start a range on the last hour of the day', async () => {
      const wrapper = await openPanel(mountPicker())
      expect(startOption(wrapper, '23:00').attributes('disabled')).toBeDefined()
    })

    it('allows the last hour of the day as an end', async () => {
      const wrapper = await openPanel(mountPicker())
      await startOption(wrapper, '22:00').trigger('click')

      expect(endOption(wrapper, '23:00').attributes('disabled')).toBeUndefined()
    })
  })

  describe('committing a range', () => {
    it('commits nothing when only a start is picked', async () => {
      const wrapper = await openPanel(mountPicker())
      await startOption(wrapper, '09:00').trigger('click')

      expect(wrapper.emitted('update:start')).toBeUndefined()
      expect(wrapper.emitted('update:end')).toBeUndefined()
      expect(wrapper.find('.time-dropdown').exists()).toBe(true)
    })

    it('commits both bounds when the end is picked, then closes', async () => {
      const wrapper = await openPanel(mountPicker())
      await startOption(wrapper, '09:00').trigger('click')
      await endOption(wrapper, '11:00').trigger('click')

      expect(wrapper.emitted('update:start')).toEqual([['09:00']])
      expect(wrapper.emitted('update:end')).toEqual([['11:00']])
      expect(wrapper.find('.time-dropdown').exists()).toBe(false)
    })

    it('restarts cleanly when a new start is picked after an existing range', async () => {
      const wrapper = await openPanel(mountPicker({ start: '09:00', end: '11:00' }))
      await startOption(wrapper, '14:00').trigger('click')

      expect(wrapper.emitted('update:start')).toBeUndefined()

      await endOption(wrapper, '16:00').trigger('click')
      expect(wrapper.emitted('update:start')).toEqual([['14:00']])
      expect(wrapper.emitted('update:end')).toEqual([['16:00']])
    })

    it('clears the range from the "any time" action', async () => {
      const wrapper = await openPanel(mountPicker({ start: '09:00', end: '11:00' }))
      await wrapper.find('[data-testid="time-any"]').trigger('click')

      expect(wrapper.emitted('update:start')).toEqual([[null]])
      expect(wrapper.emitted('update:end')).toEqual([[null]])
      expect(wrapper.find('.time-dropdown').exists()).toBe(false)
    })

    it('discards a half-finished range on Escape', async () => {
      const wrapper = await openPanel(mountPicker())
      await startOption(wrapper, '09:00').trigger('click')
      await wrapper.find('.time-picker-wrap').trigger('keydown', { key: 'Escape' })

      expect(wrapper.emitted('update:start')).toBeUndefined()
      expect(wrapper.find('.time-dropdown').exists()).toBe(false)
    })

    it('closes on an outside click without committing', async () => {
      const wrapper = await openPanel(mountPicker({}, { attachTo: document.body }))
      await startOption(wrapper, '09:00').trigger('click')

      document.body.dispatchEvent(new MouseEvent('mousedown', { bubbles: true }))
      await wrapper.vm.$nextTick()

      expect(wrapper.emitted('update:start')).toBeUndefined()
      expect(wrapper.find('.time-dropdown').exists()).toBe(false)
      wrapper.unmount()
    })
  })

  describe('past times on the current date', () => {
    beforeEach(() => {
      vi.useFakeTimers()
      vi.setSystemTime(new Date(2026, 7, 7, 14, 30, 0))
    })

    afterEach(() => {
      vi.useRealTimers()
    })

    it('disables start hours already gone when the date is today', async () => {
      const wrapper = await openPanel(mountPicker({ selectedDate: '2026-08-07' }))

      expect(startOption(wrapper, '09:00').attributes('disabled')).toBeDefined()
      expect(startOption(wrapper, '16:00').attributes('disabled')).toBeUndefined()
    })

    it('leaves every hour selectable on a future date', async () => {
      const wrapper = await openPanel(mountPicker({ selectedDate: '2026-08-08' }))
      expect(startOption(wrapper, '09:00').attributes('disabled')).toBeUndefined()
    })

    it('ignores a click on a disabled start', async () => {
      const wrapper = await openPanel(mountPicker({ selectedDate: '2026-08-07' }))
      await startOption(wrapper, '09:00').trigger('click')

      expect(endOption(wrapper, '10:00').attributes('disabled')).toBeDefined()
    })
  })
})
