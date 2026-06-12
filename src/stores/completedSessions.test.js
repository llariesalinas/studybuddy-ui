import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

const apiGet = vi.fn()
const apiPost = vi.fn()

vi.mock('@/services/api/api', () => ({
  default: {
    get: apiGet,
    post: apiPost,
  },
}))

const { useSessionsStore } = await import('./completedSessions')

describe('completed sessions store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    apiGet.mockReset()
    apiPost.mockReset()
    window.localStorage.clear()
  })

  it('posts a single rating score with the optional comment', async () => {
    apiPost.mockResolvedValueOnce({})
    apiGet
      .mockResolvedValueOnce({ data: [] })
      .mockResolvedValueOnce({
        data: {
          id: 42,
          tutee_confirmed: true,
          tutor_confirmed: true,
          rating_submitted: true,
          session: {
            status: 'Completed',
            rating: 4,
          },
        },
      })

    await useSessionsStore().submitRating(42, 4, 'Clear and helpful.')

    expect(apiPost).toHaveBeenCalledWith('/bookings/42/rating/', {
      rating_score: 4,
      comment: 'Clear and helpful.',
    })
  })
})
