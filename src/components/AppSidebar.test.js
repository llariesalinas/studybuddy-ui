import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

let authStore
let sidebarStore

vi.mock('@/stores/auth', () => ({ useAuthStore: () => authStore }))
vi.mock('@/stores/sidebar', () => ({ useSidebarStore: () => sidebarStore }))

const { default: AppSidebar } = await import('./AppSidebar.vue')

const mountSidebar = () =>
  mount(AppSidebar, {
    global: {
      stubs: {
        RouterLink: { template: '<a><slot /></a>' },
        SbThemeToggle: true,
        SbModeSwitcher: true,
      },
    },
  })

describe('AppSidebar', () => {
  beforeEach(() => {
    authStore = {
      user: { fname: 'Ryan', lname: 'D', role: 'tutee', profile_picture_url: null },
    }
    sidebarStore = { collapsed: false, toggle: vi.fn() }
  })

  it('renders tutee nav items', () => {
    const wrapper = mountSidebar()
    const text = wrapper.text()
    expect(text).toContain('Dashboard')
    expect(text).toContain('Profile')
    expect(text).toContain('Sessions')
  })

  it('shows initials when no profile picture', () => {
    const wrapper = mountSidebar()
    expect(wrapper.text()).toContain('RD')
  })

  it('emits logout when the log out button is clicked', async () => {
    const wrapper = mountSidebar()
    await wrapper.get('[data-test="logout"]').trigger('click')
    expect(wrapper.emitted('logout')).toBeTruthy()
  })

  it('emits open-support when help is clicked', async () => {
    const wrapper = mountSidebar()
    await wrapper.get('[data-test="help"]').trigger('click')
    expect(wrapper.emitted('open-support')).toBeTruthy()
  })

  it('hides the Help button for superadmin', () => {
    authStore.user.role = 'superadmin'
    const wrapper = mountSidebar()
    expect(wrapper.find('[data-test="help"]').exists()).toBe(false)
  })

  it('calls toggle when the collapse button is clicked', async () => {
    const wrapper = mountSidebar()
    await wrapper.get('[data-test="collapse-toggle"]').trigger('click')
    expect(sidebarStore.toggle).toHaveBeenCalled()
  })

  it('adds the collapsed class when collapsed', () => {
    sidebarStore.collapsed = true
    const wrapper = mountSidebar()
    expect(wrapper.get('.sb-sidebar').classes()).toContain('sb-sidebar--collapsed')
  })
})
