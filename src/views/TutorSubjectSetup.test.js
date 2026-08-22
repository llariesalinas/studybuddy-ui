import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const fetchSubjectCatalog = vi.fn()
const fetchTutorSubjects = vi.fn()
const proposeTutorSubject = vi.fn()
const addTutorSubject = vi.fn()
const removeTutorSubject = vi.fn()

vi.mock('@/services/tutorOnboarding', () => ({
  fetchSubjectCatalog,
  fetchTutorSubjects,
  proposeTutorSubject,
  addTutorSubject,
  removeTutorSubject,
}))

vi.mock('@/stores/profile', () => ({
  useProfileStore: () => ({}),
}))

vi.mock('@/stores/toast', () => ({
  useToastStore: () => ({ push: vi.fn() }),
}))

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: vi.fn() }),
}))

const { default: TutorSubjectSetup } = await import('./TutorSubjectSetup.vue')

const APPROVED = {
  subject_code: 'MATH101',
  subject_name: 'College Algebra',
  category: 'Mathematics & Data Sciences',
  description: '',
  status: 'approved',
}

// A subject the tutor proposed themselves: it is in their selection but, being pending, never in
// the approved-only catalog response.
const PENDING = {
  subject_code: 'UNDERWATER-BASKET',
  subject_name: 'Underwater Basket Weaving',
  category: 'Hobbies & Arts',
  description: '',
  status: 'pending',
}

const mountSetup = () =>
  mount(TutorSubjectSetup, {
    global: {
      stubs: {
        TutorOnboardingShell: { template: '<div><slot /></div>' },
      },
    },
  })

describe('TutorSubjectSetup', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    fetchSubjectCatalog.mockResolvedValue([APPROVED])
    fetchTutorSubjects.mockResolvedValue([])
  })

  it('shows a pending proposed subject in the selection tray on load', async () => {
    fetchTutorSubjects.mockResolvedValue([APPROVED, PENDING])

    const wrapper = mountSetup()
    await flushPromises()

    expect(wrapper.text()).toContain('Selected 2/8')
    expect(wrapper.text()).toContain(PENDING.subject_name)
  })

  it('groups a pending subject under its own awaiting-review row', async () => {
    fetchTutorSubjects.mockResolvedValue([APPROVED, PENDING])

    const wrapper = mountSetup()
    await flushPromises()

    const group = wrapper.get('.pending-group')
    expect(group.text()).toContain('Awaiting admin review')
    expect(group.text()).toContain(PENDING.subject_name)
    expect(group.text()).not.toContain(APPROVED.subject_name)

    // The approved subject keeps the plain selected chip on the first row.
    const approvedChips = wrapper.findAll('.selection-tray > .subject-chip')
    expect(approvedChips).toHaveLength(1)
    expect(approvedChips[0].text()).toContain(APPROVED.subject_name)
  })

  it('flags a pending subject in the search results too', async () => {
    fetchTutorSubjects.mockResolvedValue([APPROVED, PENDING])

    const wrapper = mountSetup()
    await flushPromises()

    await wrapper.get('.search-input').setValue('weaving')

    const rows = wrapper.findAll('.result-row')
    expect(rows).toHaveLength(1)
    expect(rows[0].text()).toContain(PENDING.subject_name)
    expect(rows[0].get('.pending-flag').text()).toBe('Awaiting admin review')
  })

  it('drops a removed proposal from the catalog instead of stranding it', async () => {
    fetchTutorSubjects.mockResolvedValue([PENDING])
    removeTutorSubject.mockResolvedValue({})

    const wrapper = mountSetup()
    await flushPromises()

    await wrapper.get('.pending-group .subject-chip').trigger('click')
    await flushPromises()

    expect(removeTutorSubject).toHaveBeenCalledWith(PENDING.subject_code)
    // Neither selected nor left behind as a stale catalog entry.
    expect(wrapper.find('.pending-group').exists()).toBe(false)
    await wrapper.get('.search-input').setValue('weaving')
    expect(wrapper.findAll('.result-row')).toHaveLength(0)
  })

  it('shows a subject in the selection tray right after proposing it', async () => {
    proposeTutorSubject.mockResolvedValue(PENDING)

    const wrapper = mountSetup()
    await flushPromises()

    await wrapper.get('.propose-trigger').trigger('click')
    await wrapper.get('#proposal-name').setValue(PENDING.subject_name)
    await wrapper.get('#proposal-category').setValue(APPROVED.category)
    await wrapper.get('.proposal-form').trigger('submit')
    await flushPromises()

    expect(proposeTutorSubject).toHaveBeenCalledTimes(1)
    expect(wrapper.text()).toContain('Selected 1/8')
    expect(wrapper.text()).toContain(PENDING.subject_name)
  })
})
