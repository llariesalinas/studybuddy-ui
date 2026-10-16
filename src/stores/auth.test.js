import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { reconcileRemoteMode } from '@/services/auth/modeRoutes'

const post = vi.fn()
const profile = { resetProfileState: vi.fn(), checkProfileStatus: vi.fn() }
vi.mock('axios', () => ({ default: { post } }))
vi.mock('@/services/api/api', () => ({ default: { post } }))
vi.mock('@/stores/profile', () => ({ useProfileStore: () => profile }))
vi.mock('@/stores/findTutors', () => ({ useFindTutorsStore: () => ({ reset: vi.fn() }) }))
vi.mock('@/stores/toast', () => ({ useToastStore: () => ({ push: vi.fn() }) }))
vi.mock('@/services/auth/idleSession', () => ({
  startIdleSessionTracking: vi.fn(), stopIdleSessionTracking: vi.fn(),
}))

const { useAuthStore } = await import('./auth')

describe('remote active mode changes', () => {
  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('reloads the new profile before announcing navigation readiness', async () => {
    const auth = useAuthStore()
    auth.user = { role: 'tutee' }
    auth.refreshToken = 'refresh'
    post.mockResolvedValueOnce({ data: { access: 'access', refresh: 'rotated', role: 'Tutor' } })
    let finishProfile
    profile.checkProfileStatus.mockImplementationOnce(() => new Promise((resolve) => {
      finishProfile = resolve
    }))
    const refresh = auth.refreshAccessToken()
    await Promise.resolve()
    expect(auth.userRole).toBe('tutor')
    expect(auth.modeChangedElsewhere).toBe(true)
    expect(auth.remoteModeRevision).toBe(0)
    expect(profile.resetProfileState).toHaveBeenCalledOnce()
    finishProfile()
    await refresh
    expect(auth.remoteModeRevision).toBe(1)
    expect(auth.refreshToken).toBe('rotated')

    const router = {
      currentRoute: { value: { meta: { role: 'Tutee' } } }, replace: vi.fn(),
    }
    await reconcileRemoteMode(router, auth.userRole)
    expect(router.replace).toHaveBeenCalledWith('/tch-dashboard')
  })

  it('retains shared routes after a remote switch', async () => {
    const router = {
      currentRoute: { value: { meta: { role: ['Tutor', 'Tutee'] } } }, replace: vi.fn(),
    }
    await reconcileRemoteMode(router, 'tutor')
    expect(router.replace).not.toHaveBeenCalled()
  })

  it('clears the remote-change confirmation flag after a local switch', async () => {
    const auth = useAuthStore()
    auth.user = { role: 'tutor' }
    auth.modeChangedElsewhere = true
    post.mockResolvedValueOnce({ data: { role: 'Tutee' } })
    await auth.switchMode('tutee')
    expect(auth.modeChangedElsewhere).toBe(false)
    expect(auth.userRole).toBe('tutee')
  })
})
