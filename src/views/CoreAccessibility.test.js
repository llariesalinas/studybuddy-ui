import { flushPromises, mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
const { apiGet } = vi.hoisted(() => ({ apiGet: vi.fn() }))
vi.mock('@/services/api/api', () => ({
  default: { get: apiGet },
  getApiPath: (url) => url,
}))
import Login from './Login.vue'
import Register from './Register.vue'
import ForgotPassword from './ForgotPassword.vue'
import ResetPassword from './ResetPassword.vue'
import TuteeSessions from './TuteeSessions.vue'
import { useSessionsStore } from '@/stores/completedSessions'

let wrapper
let router
beforeEach(async () => {
  setActivePinia(createPinia())
  apiGet.mockReset().mockResolvedValue({ data: [] })
  router = createRouter({
    history: createMemoryHistory(),
    routes: [{ path: '/:pathMatch(.*)*', component: { template: '<div />' } }],
  })
  await router.push('/login')
  await router.isReady()
})
afterEach(() => wrapper?.unmount())

describe('Core account and session accessibility', () => {
  it.each([
    ['login', Login],
    ['registration', Register],
    ['password recovery', ForgotPassword],
    ['password reset', ResetPassword],
  ])('associates %s fields with real labels and autofill purposes', async (_, component) => {
    wrapper = mount(component, { attachTo: document.body, global: { plugins: [router] } })
    await flushPromises()
    const fields = wrapper.findAll('input:not([type="checkbox"])')
    expect(fields.length).toBeGreaterThan(0)
    fields.forEach((field) => {
      expect(field.element.labels.length).toBeGreaterThan(0)
      expect(field.attributes('autocomplete')).toBeTruthy()
    })
    if (component === Register) {
      expect(wrapper.get('#register-institution').element.labels[0].textContent).toBe('Institution')
      expect(wrapper.get('#register-role').element.labels[0].textContent).toBe('I want to')
    }
  })

  it('provides a named native link to session details without requiring a row click', async () => {
    const store = useSessionsStore()
    store.fetchSessions = vi.fn().mockResolvedValue()
    store.sessions = [
      {
        id: 12,
        tutor: 'Ana Cruz',
        subject: 'Calculus',
        status: 'Upcoming',
        date: '2026-10-17',
        startTime: '09:00',
        endTime: '10:00',
      },
    ]
    wrapper = mount(TuteeSessions, { global: { plugins: [router] } })
    await flushPromises()
    const link = wrapper.get('a.session-details-link')
    expect(link.attributes('href')).toBe('/tuteeSessionDetails/12')
    expect(link.attributes('aria-label')).toContain('Calculus session with Ana Cruz')
    await link.trigger('click')
    await flushPromises()
    expect(router.currentRoute.value.path).toBe('/tuteeSessionDetails/12')
  })
})
