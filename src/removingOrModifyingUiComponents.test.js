// Single test file for the `fix/Removing-or-modifying-UI-components` branch. Everything this
// branch needs covered lives here rather than in a per-component file, so the branch adds one
// file instead of scattering several across src/.
//
// Companion plan: docs/plans/2026-08-10-removing-or-modifying-ui-components.md
//
// The store mocks below are file-wide, which is safe: CampusLocationModal.vue reads no stores,
// so only AppSidebar sees them.

import { mount } from '@vue/test-utils'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

let authStore
let sidebarStore

vi.mock('@/stores/auth', () => ({ useAuthStore: () => authStore }))
vi.mock('@/stores/sidebar', () => ({ useSidebarStore: () => sidebarStore }))

const { default: AppSidebar } = await import('@/components/AppSidebar.vue')
const { default: CampusLocationModal } = await import('@/components/CampusLocationModal.vue')

describe('AppSidebar support section', () => {
  const mountSidebar = () =>
    mount(AppSidebar, {
      global: {
        stubs: {
          RouterLink: { template: '<a><slot /></a>' },
          SbThemeToggle: true,
        },
      },
    })

  beforeEach(() => {
    authStore = {
      user: { fname: 'Ryan', lname: 'D', role: 'tutee', profile_picture_url: null },
    }
    sidebarStore = { collapsed: false, toggle: vi.fn() }
  })

  it('hides the whole support section for superadmin', () => {
    authStore.user.role = 'superadmin'
    const wrapper = mountSidebar()

    expect(wrapper.find('[data-test="help"]').exists()).toBe(false)
    // The "Support" section label must go with the button; the "Support Desk" nav item stays.
    const labels = wrapper.findAll('.sb-section-label').map((el) => el.text())
    expect(labels).not.toContain('Support')
  })

  // The counterpart -- every other role keeps Help and it still reaches SupportModal.
  it('keeps help for every other role', async () => {
    const wrapper = mountSidebar()

    await wrapper.get('[data-test="help"]').trigger('click')
    expect(wrapper.emitted('open-support')).toBeTruthy()
  })
})

// The anchored dialog is positioned from a measured rect. `getBoundingClientRect()` reports
// post-zoom coordinates, but the `left`/`top` written back are scaled by the root `zoom` the
// density system applies -- so the measurement has to be divided by the scale first, or the
// factor lands twice and the dialog drifts up and to the left of its anchor.
describe('CampusLocationModal anchored positioning', () => {
  const ANCHOR_RECT = { left: 100, top: 200, width: 400, height: 100 }

  let anchor
  let wrapper

  beforeEach(() => {
    vi.spyOn(window, 'requestAnimationFrame').mockImplementation((cb) => {
      cb()
      return 1
    })

    anchor = document.createElement('div')
    anchor.className = 'anchor'
    anchor.getBoundingClientRect = () => ANCHOR_RECT
    document.body.appendChild(anchor)
  })

  afterEach(() => {
    wrapper?.unmount()
    anchor.remove()
    document.documentElement.style.removeProperty('--sb-density-scale')
    vi.restoreAllMocks()
  })

  // Mount closed and then open, the way InitialBooking drives it -- the position watcher is not
  // `immediate`, so it only measures on the false -> true transition.
  const mountModal = async () => {
    const mounted = mount(CampusLocationModal, {
      props: { open: false, anchorSelector: '.anchor' },
      attachTo: document.body,
    })
    await mounted.setProps({ open: true })
    return mounted
  }

  const dialogStyle = () => document.querySelector('.campus-location-dialog').style

  it('centres on the anchor at comfortable density', async () => {
    document.documentElement.style.setProperty('--sb-density-scale', '1')
    wrapper = await mountModal()

    expect(dialogStyle().left).toBe('300px')
    expect(dialogStyle().top).toBe('250px')
  })

  it('divides out the root zoom at compact density', async () => {
    document.documentElement.style.setProperty('--sb-density-scale', '0.8')
    wrapper = await mountModal()

    // 300 / 0.8 and 250 / 0.8 -- rendered back down to (300, 250) by the 0.8 root zoom.
    expect(dialogStyle().left).toBe('375px')
    expect(dialogStyle().top).toBe('312.5px')
  })

  it('falls back to an unscaled measurement when the scale is missing', async () => {
    wrapper = await mountModal()

    expect(dialogStyle().left).toBe('300px')
    expect(dialogStyle().top).toBe('250px')
  })
})
