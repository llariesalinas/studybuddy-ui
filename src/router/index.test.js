import { beforeEach, describe, expect, it, vi } from 'vitest'

// Regression coverage for the corrupt-session self-heal in the global nav guard
// (docs/plans/2026-08-13-corrupt-auth-session-guard-fix.md): a token can survive in
// localStorage without its matching user_role, leaving isAuthenticated true with no
// role to redirect on. Without the fix, the GUEST_ONLY branch falls back to '/' and
// "Log in" silently no-ops when already on '/'.

const logoutMock = vi.fn()
let authState

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => authState,
}))

let profileState
const toast = { push: vi.fn(() => 1), dismiss: vi.fn() }
vi.mock('@/stores/toast', () => ({ useToastStore: () => toast }))
vi.mock('@/stores/profile', () => ({ useProfileStore: () => profileState }))
// Exercise real navigation and guards without loading page components or their unrelated stores.
vi.mock('vue-router', async (importOriginal) => {
  const actual = await importOriginal()
  return {
    ...actual,
    createRouter: (options) => actual.createRouter({
      ...options,
      routes: options.routes.map((route) => ({ ...route, component: { template: '<div />' } })),
    }),
  }
})

function resetProfile() {
  profileState = {
    loaded: true, checkProfileStatus: vi.fn(), profileCompleted: true,
    tutorOnboardingComplete: true, tutorSubjectsCompleted: true, tutorRateSet: true,
    commissionTermsAccepted: true, canTutee: true, canTutor: false,
  }
}

const { default: router } = await import('./index')

describe('router guard: corrupt session self-heal', () => {
  beforeEach(async () => {
    resetProfile()
    logoutMock.mockReset()
    // Mimics the real auth store's logout(): clears the inconsistent state so the
    // rest of the guard re-reads a consistent, logged-out session.
    logoutMock.mockImplementation(() => {
      authState.isAuthenticated = false
      authState.token = null
    })

    // Reset to a neutral, unguarded route between tests with a clean (logged-out) auth
    // state — otherwise a test that ends on e.g. '/login' makes the next test's
    // `router.push('/login')` a same-location no-op that never runs the guard (the
    // duplicate-navigation quirk this fix works around), and doing the reset while
    // still "authenticated with no role" would itself trigger the self-heal early.
    authState = { token: null, isAuthenticated: false, userRole: null, logout: logoutMock }
    await router.push('/tutor-application-submitted')

    // Now put the corrupt session under test in place.
    authState.token = 'stale-access-token'
    authState.isAuthenticated = true
  })

  it('logs out instead of bouncing back to the same page on a guest-only route', async () => {
    await router.push('/login')

    expect(logoutMock).toHaveBeenCalledOnce()
    expect(router.currentRoute.value.path).toBe('/login')
  })

  it('logs out and sends a requiresAuth route to /login', async () => {
    await router.push('/dashboard')

    expect(logoutMock).toHaveBeenCalledOnce()
    expect(router.currentRoute.value.path).toBe('/login')
  })

  it('leaves a real authenticated session (role resolved) alone', async () => {
    authState.userRole = 'Tutee'

    await router.push('/login')

    expect(logoutMock).not.toHaveBeenCalled()
    expect(router.currentRoute.value.path).toBe('/dashboard')
  })
})

describe('mode routing regressions', () => {
  beforeEach(async () => {
    vi.restoreAllMocks()
    toast.push.mockClear()
    toast.dismiss.mockClear()
    resetProfile()
    authState = { token: null, isAuthenticated: false, userRole: null }
    await router.push('/tutor-application-submitted')
    authState = {
      token: 'access', isAuthenticated: true, userRole: 'tutee', modeChangedElsewhere: false,
      switchMode: vi.fn(async (mode) => { authState.userRole = mode }),
    }
  })

  it('keeps a completed tutor with zero subjects out of onboarding', async () => {
    authState.userRole = 'tutor'
    profileState.tutorSubjectsCompleted = false
    await router.push('/tch-dashboard')
    expect(router.currentRoute.value.path).toBe('/tch-dashboard')
  })

  it('keeps initial setup mandatory when verification was carried', async () => {
    authState.userRole = 'tutor'
    profileState.tutorOnboardingComplete = false
    profileState.tutorRateSet = false
    await router.push('/tch-dashboard')
    expect(router.currentRoute.value.path).toBe('/tutor-setup')
  })

  it('runs tutor commission checks after automatic switching', async () => {
    profileState.canTutor = true
    profileState.commissionTermsAccepted = false
    await router.push('/tch-dashboard')
    expect(authState.switchMode).toHaveBeenCalledWith('tutor')
    expect(router.currentRoute.value.name).toBe('tutor-commission-terms')
  })

  it('runs verification setup checks after automatic switching', async () => {
    profileState.canTutor = true
    profileState.tutorOnboardingComplete = false
    await router.push('/tch-dashboard')
    expect(router.currentRoute.value.name).toBe('tutor-verification-setup')
  })

  it('undo returns to a page belonging to the restored mode', async () => {
    profileState.canTutor = true
    await router.push('/tch-dashboard')
    const action = toast.push.mock.calls.at(-1)[3]
    await action.handler()
    expect(authState.userRole).toBe('tutee')
    expect(router.currentRoute.value.path).toBe('/dashboard')
  })

  it('dismisses undo on subsequent navigation', async () => {
    profileState.canTutor = true
    await router.push('/tch-dashboard')
    toast.dismiss.mockClear()
    await router.push('/tch-wallet')
    expect(toast.dismiss).toHaveBeenCalledWith(1)
  })

  it('asks before switching after a detected other-device change and respects cancellation', async () => {
    profileState.canTutor = true
    authState.modeChangedElsewhere = true
    vi.spyOn(window, 'confirm').mockReturnValue(false)
    await router.push('/tch-dashboard')
    expect(window.confirm).toHaveBeenCalledOnce()
    expect(authState.switchMode).not.toHaveBeenCalled()
    expect(router.currentRoute.value.path).toBe('/dashboard')
  })

  it('allows a confirmed switch after a detected other-device change', async () => {
    profileState.canTutor = true
    authState.modeChangedElsewhere = true
    vi.spyOn(window, 'confirm').mockReturnValue(true)
    await router.push('/tch-dashboard')
    expect(authState.switchMode).toHaveBeenCalledOnce()
    expect(router.currentRoute.value.path).toBe('/tch-dashboard')
  })
})
