import { flushPromises, mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
const { apiGet, apiDelete } = vi.hoisted(() => ({ apiGet: vi.fn(), apiDelete: vi.fn() }))
vi.mock('@/services/api/api', () => ({ default: { get: apiGet, delete: apiDelete } }))
import TutorSchedule from './TutorSchedule.vue'

let wrapper
const requestDelete = async () => {
  wrapper = mount(TutorSchedule, { attachTo: document.body })
  await flushPromises()
  await wrapper.get('.slot-pill').trigger('click')
  const button = wrapper
    .findAll('.day-actions button')
    .find((button) => button.text().includes('Delete weekly'))
  button.element.focus()
  await button.trigger('click')
  await flushPromises()
  return button
}
const dialogButtons = () => [
  ...document.querySelectorAll('[aria-labelledby="delete-weekly-title"] button'),
]

beforeEach(() => {
  setActivePinia(createPinia())
  apiGet.mockReset().mockImplementation(async (url) => ({
    data: url.includes('overrides') ? [] : [{ availability_id: 1, day: 'Fri', time_slot: '09:00' }],
  }))
  apiDelete.mockReset().mockResolvedValue({})
})
afterEach(() => {
  wrapper?.unmount()
})

describe('Recurring availability deletion', () => {
  it('does not delete on selection or cancel, explains recurrence, and restores focus', async () => {
    const trigger = await requestDelete()
    expect(apiDelete).not.toHaveBeenCalled()
    expect(document.getElementById('delete-weekly-description').textContent).toContain(
      'every Friday',
    )
    dialogButtons()[0].click()
    await flushPromises()
    expect(document.getElementById('delete-weekly-title')).toBeNull()
    expect(apiDelete).not.toHaveBeenCalled()
    expect(document.activeElement).toBe(trigger.element)
  })

  it('deletes the recurring slot only after confirmation', async () => {
    await requestDelete()
    dialogButtons()[1].click()
    await flushPromises()
    expect(apiDelete).toHaveBeenCalledExactlyOnceWith('/template-availability/1/')
    expect(document.getElementById('delete-weekly-title')).toBeNull()
  })

  it('retains failed deletions for retry without reporting success', async () => {
    apiDelete.mockRejectedValueOnce(new Error('offline'))
    await requestDelete()
    dialogButtons()[1].click()
    await flushPromises()
    expect(
      document.querySelector('[aria-labelledby="delete-weekly-title"] [role="alert"]').textContent,
    ).toContain('remaining slots are still selected')
    dialogButtons()[1].click()
    await flushPromises()
    expect(apiDelete).toHaveBeenCalledTimes(2)
    expect(document.getElementById('delete-weekly-title')).toBeNull()
  })

  it('retries only remaining slots after a partially successful batch', async () => {
    apiGet.mockImplementation(async (url) => ({
      data: url.includes('overrides')
        ? []
        : [
            { availability_id: 1, day: 'Fri', time_slot: '09:00' },
            { availability_id: 2, day: 'Fri', time_slot: '10:00' },
          ],
    }))
    apiDelete.mockResolvedValueOnce({}).mockRejectedValueOnce(new Error('offline'))
    wrapper = mount(TutorSchedule, { attachTo: document.body })
    await flushPromises()
    for (const slot of wrapper.findAll('.slot-pill')) await slot.trigger('click')
    await wrapper
      .findAll('.day-actions button')
      .find((button) => button.text().includes('Delete weekly'))
      .trigger('click')
    await flushPromises()
    dialogButtons()[1].click()
    await flushPromises()
    expect(document.getElementById('delete-weekly-description').textContent).toContain(
      '1 weekly slot',
    )
    dialogButtons()[1].click()
    await flushPromises()
    expect(apiDelete.mock.calls.map(([url]) => url)).toEqual([
      '/template-availability/1/',
      '/template-availability/2/',
      '/template-availability/2/',
    ])
  })
})
