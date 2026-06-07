import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

const apiGet = vi.fn()
const apiPost = vi.fn()
const apiDelete = vi.fn()

vi.mock('@/services/api/api', () => ({
  default: {
    get: apiGet,
    post: apiPost,
    delete: apiDelete,
  },
}))

const { useSessionsStore } = await import('./completedSessions')

describe('completed sessions store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    apiGet.mockReset()
    apiPost.mockReset()
    apiDelete.mockReset()
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

  it('keeps schedule pills on their own dates even when a group id repeats', async () => {
    apiGet.mockResolvedValueOnce({
      data: [
        {
          id: 10,
          session_group_id: 'same-group',
          date: '2026-06-06',
          startTime: '09:00',
          endTime: '09:30',
          duration_hours: 0.5,
          status: 'Rejected',
        },
        {
          id: 11,
          session_group_id: 'same-group',
          date: '2026-06-10',
          startTime: '09:00',
          endTime: '09:30',
          duration_hours: 0.5,
          status: 'Rejected',
        },
      ],
    })

    const store = useSessionsStore()
    await store.fetchSessions()

    expect(store.sessions).toHaveLength(2)
    expect(store.sessions.map((session) => session.date)).toEqual([
      '2026-06-06',
      '2026-06-10',
    ])
  })

  it('dismisses a dashboard pill without removing it from the sessions store', async () => {
    apiGet
      .mockResolvedValueOnce({
        data: [
          {
            id: 21,
            session_group_id: 'cancelled-group',
            date: '2026-06-06',
            startTime: '09:00',
            endTime: '10:00',
            duration_hours: 1,
            status: 'Cancelled',
            dashboard_hidden_by_current_user: false,
          },
          {
            id: 30,
            date: '2026-06-07',
            startTime: '09:00',
            endTime: '10:00',
            duration_hours: 1,
            status: 'Rejected',
            dashboard_hidden_by_current_user: false,
          },
        ],
      })
      .mockResolvedValueOnce({
        data: [
          {
            id: 21,
            session_group_id: 'cancelled-group',
            date: '2026-06-06',
            startTime: '09:00',
            endTime: '10:00',
            duration_hours: 1,
            status: 'Cancelled',
            dashboard_hidden_by_current_user: true,
          },
          {
            id: 30,
            date: '2026-06-07',
            startTime: '09:00',
            endTime: '10:00',
            duration_hours: 1,
            status: 'Rejected',
            dashboard_hidden_by_current_user: false,
          },
        ],
      })
    apiDelete.mockResolvedValueOnce({ data: { hidden_booking_ids: [21] } })

    const store = useSessionsStore()
    await store.fetchSessions()
    await store.dismissDashboardPill(21)

    expect(apiDelete).toHaveBeenCalledWith('/bookings/21/dashboard-pill/')
    expect(store.sessions).toHaveLength(2)
    expect(store.sessions.find((session) => session.id === 21).dashboard_hidden_by_current_user).toBe(true)
    expect(store.sessions.find((session) => session.id === 30).dashboard_hidden_by_current_user).toBe(false)
  })
})
