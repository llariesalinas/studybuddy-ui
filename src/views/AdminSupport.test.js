import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

let route
let router
let toastStore

const apiGet = vi.fn()

vi.mock('@/services/api/api', () => ({
  default: {
    get: apiGet,
    post: vi.fn(),
  },
}))

vi.mock('@/stores/toast', () => ({
  useToastStore: () => toastStore,
}))

vi.mock('vue-router', () => ({
  useRoute: () => route,
  useRouter: () => router,
}))

const { default: AdminSupport } = await import('./AdminSupport.vue')

const ticket = (overrides) => ({
  id: 1,
  user: { id: 10, name: 'Ana Cruz', role: 'Student' },
  category: 'Other',
  subject: 'Subject',
  description: 'Description',
  status: 'Open',
  created_at: '2026-08-01T10:00:00Z',
  assigned_agent: null,
  assigned_agent_id: null,
  ...overrides,
})

const TICKETS = [
  ticket({ id: 1, status: 'Open', subject: 'Late cancellation review', category: 'Late_Cancellation' }),
  ticket({ id: 2, status: 'Escalated', subject: 'Refund needs platform access', category: 'Payment' }),
  ticket({ id: 3, status: 'Resolved', subject: 'Password reset', category: 'Technical' }),
  ticket({ id: 4, status: 'In_Progress', subject: 'Booking no-show', category: 'Booking' }),
]

const mountDesk = () => mount(AdminSupport)

const tabLabels = (wrapper) => wrapper.findAll('.filter-tab').map((tab) => tab.text())

const clickTab = async (wrapper, label) => {
  const tab = wrapper.findAll('.filter-tab').find((t) => t.text().startsWith(label))
  await tab.trigger('click')
  await flushPromises()
}

// The rendered rows, keyed by the ticket subject shown in each row.
const rowSubjects = (wrapper) =>
  wrapper.findAll('tbody tr').map((row) => row.text()).filter(Boolean)

describe('AdminSupport', () => {
  beforeEach(() => {
    router = { push: vi.fn() }
    toastStore = { push: vi.fn() }
    apiGet.mockReset()
    apiGet.mockResolvedValue({ data: TICKETS })
  })

  describe('SuperAdmin desk', () => {
    beforeEach(() => {
      route = { path: '/superadmin/support' }
    })

    it('renders no Escalated tab', async () => {
      const wrapper = mountDesk()
      await flushPromises()

      const labels = tabLabels(wrapper)
      expect(labels).toHaveLength(2)
      expect(labels.join(' ')).not.toContain('Escalated')
      expect(labels[0]).toContain('Open')
      expect(labels[1]).toContain('Resolved')
    })

    it('defaults to Open and lists escalated tickets alongside open ones', async () => {
      const wrapper = mountDesk()
      await flushPromises()

      const rows = rowSubjects(wrapper)
      expect(rows).toHaveLength(2)
      expect(wrapper.text()).toContain('Late cancellation review')
      expect(wrapper.text()).toContain('Refund needs platform access')
      expect(wrapper.text()).not.toContain('Password reset')
    })

    it('counts escalated tickets in the Open tab badge', async () => {
      const wrapper = mountDesk()
      await flushPromises()

      expect(tabLabels(wrapper)[0]).toContain('Open (2)')
    })

    it('shows a status badge so merged Open and Escalated rows stay distinguishable', async () => {
      const wrapper = mountDesk()
      await flushPromises()

      const badges = wrapper.findAll('tbody .badge').map((b) => b.text())
      expect(badges).toContain('Open')
      expect(badges).toContain('Escalated')
    })

    it('still filters the Resolved tab to resolved tickets only', async () => {
      const wrapper = mountDesk()
      await flushPromises()
      await clickTab(wrapper, 'Resolved')

      expect(rowSubjects(wrapper)).toHaveLength(1)
      expect(wrapper.text()).toContain('Password reset')
    })
  })

  describe('Admin desk', () => {
    beforeEach(() => {
      route = { path: '/admin/support' }
    })

    it('keeps its three tabs', async () => {
      const wrapper = mountDesk()
      await flushPromises()

      const labels = tabLabels(wrapper)
      expect(labels).toHaveLength(3)
      expect(labels[0]).toContain('Open')
      expect(labels[1]).toContain('In Progress')
      expect(labels[2]).toContain('Resolved')
    })

    it('excludes escalated tickets from its Open tab', async () => {
      const wrapper = mountDesk()
      await flushPromises()

      expect(tabLabels(wrapper)[0]).toContain('Open (1)')
      expect(wrapper.text()).toContain('Late cancellation review')
      expect(wrapper.text()).not.toContain('Refund needs platform access')
    })
  })
})
