import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

let sessionsStore
let walletStore
let route
let router

const apiGet = vi.fn()

vi.mock('@/stores/completedSessions', () => ({
  useSessionsStore: () => sessionsStore,
}))

vi.mock('@/stores/wallet', () => ({
  useWalletStore: () => walletStore,
}))

vi.mock('@/services/api/api', () => ({
  default: {
    get: apiGet,
  },
}))

vi.mock('vue-router', () => ({
  useRoute: () => route,
  useRouter: () => router,
}))

const { default: TutorDashboard } = await import('./TutorDashboard.vue')

const mountDashboard = () =>
  mount(TutorDashboard, {
    global: {
      stubs: {
        RouterLink: true,
      },
    },
  })

describe('TutorDashboard', () => {
  beforeEach(() => {
    route = { query: {} }
    router = {
      push: vi.fn(),
    }
    sessionsStore = {
      fetchSessions: vi.fn().mockResolvedValue([]),
      upcomingSessions: [],
    }
    walletStore = {
      balance: 1250,
      fetchWallet: vi.fn().mockResolvedValue({}),
    }
    apiGet.mockReset()
    apiGet.mockResolvedValue({
      data: {
        total_sessions: 12,
        rating_average: 4.5,
        total_earnings: 9876,
        accepted_session_load: 3,
        session_load_limit: 10,
        upcoming_bookings: [],
      },
    })
  })

  it('loads wallet balance alongside the dashboard metrics', async () => {
    const wrapper = mountDashboard()

    await flushPromises()

    expect(walletStore.fetchWallet).toHaveBeenCalledTimes(1)
    expect(apiGet).toHaveBeenCalledWith('tutor-dashboard/')
    expect(wrapper.text()).toContain('Wallet Balance')
    expect(wrapper.text()).toContain('PHP 1,250')
  })
})
