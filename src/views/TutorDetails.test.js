import { flushPromises, mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

const { apiGet } = vi.hoisted(() => ({ apiGet: vi.fn() }))
vi.mock('@/services/api/api', () => ({ default: { get: apiGet } }))
vi.mock('vue-router', () => ({
  useRoute: () => ({ params: { id: 7 } }),
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
}))
import TutorDetails from './TutorDetails.vue'

let wrapper
let profile
let sessionDate
const mountProfile = async () => {
  wrapper = mount(TutorDetails, { global: { stubs: { RouterLink: true } } })
  await flushPromises()
  return wrapper
}

beforeEach(() => {
  setActivePinia(createPinia())
  vi.useFakeTimers({ toFake: ['Date'] })
  vi.setSystemTime(new Date('2026-10-16T00:00:00Z'))
  sessionDate = '2026-10-17'
  profile = {
    fname: 'Ana',
    lname: 'Cruz',
    hourly_rate: 100,
    rating_average: 0,
    total_sessions: 0,
    subjects: [],
  }
  apiGet.mockReset().mockImplementation(async (url) => ({
    data: url.includes('availability')
      ? {
          weeks: [
            {
              week_start: '2026-10-12',
              week_end: '2026-10-18',
              days: [
                {
                  date: sessionDate,
                  name: 'Saturday',
                  in_month: true,
                  is_past: false,
                  slots: [{ id: 1, time_slot: '16:00', is_booked: false }],
                },
              ],
            },
          ],
        }
      : profile,
  }))
})

afterEach(() => {
  wrapper?.unmount()
  vi.useRealTimers()
})

describe('TutorDetails truth and booking consequences', () => {
  it('preserves zero sessions and unrated tutors without fabricated subjects or biography', async () => {
    await mountProfile()
    expect(wrapper.text()).toContain('No ratings yet')
    expect(wrapper.findAll('.summary-row')[2].text()).toContain('Total Sessions0')
    expect(wrapper.text()).toContain('No subjects listed.')
    expect(wrapper.text()).toContain('No introduction provided yet.')
    expect(wrapper.text()).not.toMatch(
      /124|4\.7|Computer Science|Beginner Friendly|Web Development/,
    )
  })

  it('distinguishes unavailable statistics and rate from genuine zero values', async () => {
    profile = { fname: 'Ana', subjects: [] }
    await mountProfile()
    expect(wrapper.text()).toContain('Rating unavailable')
    expect(wrapper.findAll('.summary-row')[2].text()).toContain('Unavailable')
    expect(wrapper.get('.confirm-booking-btn').attributes('disabled')).toBeDefined()
    expect(wrapper.get('.confirm-booking-btn').text()).toBe('Rate unavailable')
  })

  it('shows the 12-hour rule and selected cancellation deadline in Manila time', async () => {
    await mountProfile()
    expect(wrapper.get('.policy-note').text()).toContain('12 hours')
    await wrapper.get('.slot-link').trigger('click')
    expect(wrapper.get('.policy-note').text()).toContain('Oct 17')
    expect(wrapper.get('.policy-note').text()).toMatch(/4:00\s*AM/)
    expect(wrapper.get('.policy-note').text()).toContain('Manila time')
    expect(wrapper.get('.policy-note').text()).not.toContain('24 hours')
  })

  it('warns before confirming a booking already inside the cutoff', async () => {
    sessionDate = '2026-10-16'
    await mountProfile()
    await wrapper.get('.slot-link').trigger('click')
    expect(wrapper.get('.policy-note').text()).toContain('no penalty-free cancellation window')
    expect(wrapper.get('.policy-note').text()).toContain('late-cancellation review')
  })

  it('offers retry rather than showing a fictitious profile after a failed load', async () => {
    apiGet.mockRejectedValueOnce(new Error('offline'))
    await mountProfile()
    expect(wrapper.get('[role="alert"]').text()).toContain('Try again')
    expect(wrapper.find('.profile-card').exists()).toBe(false)
    await wrapper.get('[role="alert"] button').trigger('click')
    await flushPromises()
    expect(wrapper.get('.profile-name').text()).toBe('Ana Cruz')
  })
})
