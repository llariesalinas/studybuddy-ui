import { mount } from '@vue/test-utils'
import { nextTick, reactive } from 'vue'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

let authStore
let profileStore
let sidebarStore
let toastStore
let push

vi.mock('@/stores/auth', () => ({ useAuthStore: () => authStore }))
vi.mock('@/stores/profile', () => ({ useProfileStore: () => profileStore }))
vi.mock('@/stores/sidebar', () => ({ useSidebarStore: () => sidebarStore }))
vi.mock('@/stores/toast', () => ({ useToastStore: () => toastStore }))
vi.mock('vue-router', () => ({ useRouter: () => ({ push }) }))

const { default: SbModeSwitcher } = await import('./SbModeSwitcher.vue')
const { default: AppSidebar } = await import('./AppSidebar.vue')

// Teleport renders into document.body, so a wrapper left mounted between tests strands its
// anchors. Track every mount and unmount it before the next test clears the body.
let mounted = []

const track = (wrapper) => {
  mounted.push(wrapper)
  return wrapper
}

afterEach(() => {
  mounted.forEach((wrapper) => wrapper.unmount())
  mounted = []
  document.body.innerHTML = ''
})

const mountSwitcher = () => track(mount(SbModeSwitcher, { attachTo: document.body }))

const mountSidebar = () =>
  track(
    mount(AppSidebar, {
      attachTo: document.body,
      global: {
        stubs: { RouterLink: { template: '<a><slot /></a>' }, SbThemeToggle: true },
      },
    })
  )

const cell = (wrapper, mode) => wrapper.find(`[data-test="mode-switch-${mode}"]`)

describe('SbModeSwitcher', () => {
  beforeEach(() => {
    push = vi.fn().mockResolvedValue(undefined)
    authStore = reactive({
      user: { role: 'Tutee' },
      switchMode: vi.fn().mockResolvedValue('tutor'),
    })
    profileStore = reactive({
      canTutor: true,
      canTutee: true,
      applicationStatus: 'approved',
      checkProfileStatus: vi.fn().mockResolvedValue(undefined),
    })
    sidebarStore = reactive({ collapsed: false })
    toastStore = { push: vi.fn() }
  })

  it('renders nothing for a role that cannot switch', () => {
    authStore.user.role = 'SuperAdmin'
    const wrapper = mountSwitcher()

    expect(wrapper.find('[data-test="mode-switch"]').exists()).toBe(false)
  })

  it('exposes a named radiogroup with the current mode checked', () => {
    const wrapper = mountSwitcher()
    const group = wrapper.find('[data-test="mode-switch"]')

    expect(group.attributes('role')).toBe('radiogroup')
    expect(group.attributes('aria-label')).toBe('Account mode')
    expect(cell(wrapper, 'tutee').attributes('aria-checked')).toBe('true')
    expect(cell(wrapper, 'tutor').attributes('aria-checked')).toBe('false')
  })

  it('styles itself rather than borrowing the sidebar classes it used to render', () => {
    const wrapper = mountSwitcher()

    expect(wrapper.find('.sb-mode').exists()).toBe(true)
    expect(wrapper.find('.sb-item').exists()).toBe(false)
    expect(wrapper.find('.sb-chip').exists()).toBe(false)
  })

  it('abbreviates on the collapsed rail but keeps the full accessible name', () => {
    sidebarStore.collapsed = true
    const wrapper = mountSwitcher()

    expect(cell(wrapper, 'tutor').text()).toBe('TR')
    expect(cell(wrapper, 'tutor').attributes('aria-label')).toBe('Tutor')
    expect(cell(wrapper, 'tutor').attributes('title')).toBe('Tutor')
    expect(wrapper.find('.sb-mode').classes()).toContain('sb-mode--collapsed')
  })

  it('keeps the selection on the committed role until the switch resolves', async () => {
    let resolveSwitch
    authStore.switchMode = vi.fn(() => new Promise((resolve) => { resolveSwitch = resolve }))

    const wrapper = mountSwitcher()
    await cell(wrapper, 'tutor').trigger('click')

    expect(authStore.switchMode).toHaveBeenCalledWith('tutor')
    expect(cell(wrapper, 'tutor').attributes('aria-checked')).toBe('false')
    expect(cell(wrapper, 'tutee').attributes('aria-checked')).toBe('true')
    expect(wrapper.find('[data-test="mode-switch"]').attributes('aria-busy')).toBe('true')

    authStore.user.role = 'Tutor'
    resolveSwitch('tutor')
    await nextTick()
    await nextTick()

    expect(cell(wrapper, 'tutor').attributes('aria-checked')).toBe('true')
  })

  it('ignores a click on the mode already in use', async () => {
    const wrapper = mountSwitcher()
    await cell(wrapper, 'tutee').trigger('click')

    expect(authStore.switchMode).not.toHaveBeenCalled()
  })

  it('moves focus with the arrow keys without switching mode', async () => {
    const wrapper = mountSwitcher()
    await wrapper.find('[data-test="mode-switch"]').trigger('keydown', { key: 'ArrowRight' })

    expect(document.activeElement).toBe(cell(wrapper, 'tutor').element)
    expect(cell(wrapper, 'tutor').attributes('tabindex')).toBe('0')
    expect(cell(wrapper, 'tutee').attributes('tabindex')).toBe('-1')
    expect(authStore.switchMode).not.toHaveBeenCalled()
  })

  it('opens a named setup dialog when the target mode is not provisioned', async () => {
    profileStore.canTutor = false
    const wrapper = mountSwitcher()
    await cell(wrapper, 'tutor').trigger('click')

    const dialog = document.querySelector('[role="dialog"]')
    expect(dialog).not.toBeNull()
    expect(authStore.switchMode).not.toHaveBeenCalled()

    const titleId = dialog.getAttribute('aria-labelledby')
    expect(document.getElementById(titleId).textContent).toContain('No Tutor account yet')
  })

  it('closes the dialog on Escape and restores focus to the cell that opened it', async () => {
    profileStore.canTutor = false
    const wrapper = mountSwitcher()
    await cell(wrapper, 'tutor').trigger('click')
    await nextTick()

    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }))
    await nextTick()

    expect(document.querySelector('[role="dialog"]')).toBeNull()
    expect(document.activeElement).toBe(cell(wrapper, 'tutor').element)
  })

  it('announces the busy state instead of disabling the focused cell', async () => {
    let resolveSwitch
    authStore.switchMode = vi.fn(() => new Promise((resolve) => { resolveSwitch = resolve }))

    const wrapper = mountSwitcher()
    await cell(wrapper, 'tutor').trigger('click')

    const status = wrapper.find('[data-test="mode-switch-status"]')
    expect(status.attributes('role')).toBe('status')
    expect(status.text()).toBe('Switching to Tutor mode')
    expect(cell(wrapper, 'tutor').attributes('disabled')).toBeUndefined()

    resolveSwitch('tutor')
  })

  it('reports a failed switch through the toast store', async () => {
    vi.spyOn(console, 'error').mockImplementation(() => {})
    authStore.switchMode = vi.fn().mockRejectedValue(new Error('nope'))

    const wrapper = mountSwitcher()
    await cell(wrapper, 'tutor').trigger('click')
    await nextTick()

    expect(toastStore.push).toHaveBeenCalledWith(
      'Could not switch modes. Please try again.',
      'error'
    )
    expect(cell(wrapper, 'tutee').attributes('aria-checked')).toBe('true')
  })
})

describe('SbModeSwitcher inside AppSidebar', () => {
  beforeEach(() => {
    push = vi.fn().mockResolvedValue(undefined)
    authStore = reactive({
      user: { fname: 'Ryan', lname: 'D', role: 'tutee', profile_picture_url: null },
      switchMode: vi.fn().mockResolvedValue('tutor'),
    })
    profileStore = reactive({
      canTutor: true,
      canTutee: true,
      applicationStatus: 'approved',
      checkProfileStatus: vi.fn().mockResolvedValue(undefined),
    })
    sidebarStore = reactive({ collapsed: false, toggle: vi.fn() })
    toastStore = { push: vi.fn() }
  })

  // Regression guard: the switcher is a multi-root fragment, so Vue never applies AppSidebar's
  // scope id to it. Any class it renders must be one it declares itself, or it renders unstyled.
  it('does not depend on the parent scope id to be styled', () => {
    const wrapper = mountSidebar()

    const group = wrapper.find('[data-test="mode-switch"]')
    expect(group.exists()).toBe(true)
    expect(group.classes()).toContain('sb-mode')

    const scopedAttr = Object.keys(wrapper.find('[data-test="logout"]').attributes()).find((name) =>
      name.startsWith('data-v-')
    )
    expect(scopedAttr).toBeDefined()
    expect(group.attributes(scopedAttr)).toBeUndefined()
  })

  it('mounts the switcher outside the footer row', () => {
    const wrapper = mountSidebar()

    expect(wrapper.find('.sb-footer [data-test="mode-switch"]').exists()).toBe(false)
    expect(wrapper.find('[data-test="mode-switch"]').exists()).toBe(true)
  })
})
