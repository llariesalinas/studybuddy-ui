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

vi.mock('@/stores/profile', () => ({
  useProfileStore: () => ({
    loaded: true,
    checkProfileStatus: vi.fn(),
    profileCompleted: true,
    tutorOnboardingComplete: true,
    tutorSubjectsCompleted: true,
    commissionTermsAccepted: true,
  }),
}))

const { default: router } = await import('./index')

describe('router guard: corrupt session self-heal', () => {
  beforeEach(async () => {
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
