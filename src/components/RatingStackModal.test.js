import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

let sessionsStore
let toastStore

vi.mock('@/stores/completedSessions', () => ({
  useSessionsStore: () => sessionsStore,
}))

vi.mock('@/stores/toast', () => ({
  useToastStore: () => toastStore,
}))

const { default: RatingStackModal } = await import('./RatingStackModal.vue')

const makeSession = (overrides = {}) => ({
  id: 1,
  subject: 'Math',
  tutor: 'Ada Tutor',
  date: '2026-06-07',
  startTime: '09:00',
  endTime: '10:00',
  ...overrides,
})

const mountModal = (props = {}) => mount(RatingStackModal, {
  props: {
    open: true,
    sessions: [makeSession()],
    ...props,
  },
  global: {
    stubs: {
      Teleport: true,
    },
  },
})

const submitButton = (wrapper) =>
  wrapper.findAll('button').find(button => button.text() === 'Submit Rating')

const setRating = async (wrapper, categoryIndex, score) => {
  const starButtons = wrapper.findAll('.rating-star-btn-sm')
  await starButtons[(categoryIndex * 5) + score - 1].trigger('click')
}

const completeRatings = async (wrapper, overallScore = 4) => {
  await setRating(wrapper, 0, 5)
  await setRating(wrapper, 1, 4)
  await setRating(wrapper, 2, 5)
  await setRating(wrapper, 3, overallScore)
}

describe('RatingStackModal', () => {
  beforeEach(() => {
    sessionsStore = {
      submitRating: vi.fn().mockResolvedValue({}),
    }
    toastStore = {
      push: vi.fn(),
    }
    document.body.style.overflow = ''
  })

  it('keeps submit disabled until every category has a rating', async () => {
    const wrapper = mountModal()

    expect(submitButton(wrapper).attributes('disabled')).toBeDefined()

    await setRating(wrapper, 0, 5)
    await setRating(wrapper, 1, 4)
    await setRating(wrapper, 2, 5)

    expect(submitButton(wrapper).attributes('disabled')).toBeDefined()

    await setRating(wrapper, 3, 4)

    expect(submitButton(wrapper).attributes('disabled')).toBeUndefined()
  })

  it('submits the overall rating and advances when another unrated session remains', async () => {
    const firstSession = makeSession({ id: 1, subject: 'Math' })
    const secondSession = makeSession({ id: 2, subject: 'Science' })
    let wrapper

    sessionsStore.submitRating = vi.fn(async () => {
      await wrapper.setProps({ sessions: [secondSession] })
    })
    wrapper = mountModal({ sessions: [firstSession, secondSession] })

    await completeRatings(wrapper, 3)
    await wrapper.find('textarea').setValue('Good pace.')
    await submitButton(wrapper).trigger('click')
    await flushPromises()

    expect(sessionsStore.submitRating).toHaveBeenCalledWith(1, 3, 'Good pace.')
    expect(wrapper.emitted('rated')).toEqual([[1]])
    expect(wrapper.emitted('close')).toBeUndefined()
    expect(wrapper.text()).toContain('Science')
  })

  it('closes after submitting the final unrated session', async () => {
    let wrapper

    sessionsStore.submitRating = vi.fn(async () => {
      await wrapper.setProps({ sessions: [] })
    })
    wrapper = mountModal({ sessions: [makeSession({ id: 7 })] })

    await completeRatings(wrapper, 5)
    await submitButton(wrapper).trigger('click')
    await flushPromises()

    expect(sessionsStore.submitRating).toHaveBeenCalledWith(7, 5, '')
    expect(wrapper.emitted('rated')).toEqual([[7]])
    expect(wrapper.emitted('close')).toEqual([[]])
  })
})
