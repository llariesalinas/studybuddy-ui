import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const getAlgorithmDemoRecommendation = vi.fn()
const getAlgorithmDemoWhatIf = vi.fn()

vi.mock('@/services/api/algorithmDemo', () => ({
  getAlgorithmDemoRecommendation,
  getAlgorithmDemoWhatIf,
}))

const { default: AlgorithmDemoRankedList } = await import('./AlgorithmDemoRankedList.vue')

const makeRow = (overrides = {}) => ({
  tutor_id: 1,
  name: 'Maria Santos',
  hybrid_score: 0.845,
  cold_start: false,
  upcoming_week_load: 2,
  tie_group_id: null,
  cbf: {},
  cf: { score: null, neighbors: [] },
  ...overrides,
})

// Two tutors tied at 0.845 (Maria on 2 sessions, Jonas on 7) plus an untied
// tutor above them, which is the case the Tie Breaker exists to order.
const tiedRows = [
  makeRow({ tutor_id: 9, name: 'Ana Villanueva', hybrid_score: 0.912, upcoming_week_load: 4 }),
  makeRow({ tutor_id: 1, name: 'Maria Santos', upcoming_week_load: 2, tie_group_id: 0 }),
  makeRow({ tutor_id: 2, name: 'Jonas Reyes', upcoming_week_load: 7, tie_group_id: 0 }),
]

const mountList = async (rows) => {
  getAlgorithmDemoRecommendation.mockResolvedValue({ data: { rows, reason: null } })

  const wrapper = mount(AlgorithmDemoRankedList, {
    props: { tutees: [{ id: 5, name: 'Taylor Tutee' }] },
    global: {
      stubs: {
        SbSelectModal: true,
        AlgorithmDemoWeightTable: true,
        AlgorithmDemoBreakdown: {
          name: 'AlgorithmDemoBreakdown',
          props: ['row', 'tieGroup'],
          template: '<div class="breakdown-stub" />',
        },
      },
    },
  })

  await wrapper.vm.onTuteeChange(5)
  await flushPromises()
  return wrapper
}

const breakdown = (wrapper) => wrapper.findComponent({ name: 'AlgorithmDemoBreakdown' })

describe('AlgorithmDemoRankedList tie breaker', () => {
  beforeEach(() => {
    getAlgorithmDemoRecommendation.mockReset()
    getAlgorithmDemoWhatIf.mockReset()
  })

  it('renders scores at 3 decimals so an on-screen tie is a real tie', async () => {
    const wrapper = await mountList(tiedRows)

    const scores = wrapper.findAll('.score').map((node) => node.text())
    expect(scores).toEqual(['0.912', '0.845', '0.845'])
  })

  it('badges only the rows in a tie group', async () => {
    const wrapper = await mountList(tiedRows)

    const rowsWithBadge = wrapper
      .findAll('.tutor-row')
      .filter((row) => row.find('.sb-badge.tie').exists())
      .map((row) => row.text())

    expect(rowsWithBadge).toHaveLength(2)
    expect(rowsWithBadge[0]).toContain('Maria Santos')
    expect(rowsWithBadge[1]).toContain('Jonas Reyes')
  })

  it('passes the selected tutor tied peers with their ranks to the breakdown', async () => {
    const wrapper = await mountList(tiedRows)

    await wrapper.findAll('.tutor-row')[1].trigger('click')

    expect(breakdown(wrapper).props('tieGroup')).toEqual([
      expect.objectContaining({ tutor_id: 1, rank: 2, upcoming_week_load: 2 }),
      expect.objectContaining({ tutor_id: 2, rank: 3, upcoming_week_load: 7 }),
    ])
  })

  it('passes no tie group when the selected tutor score is unique', async () => {
    const wrapper = await mountList(tiedRows)

    await wrapper.findAll('.tutor-row')[0].trigger('click')

    expect(breakdown(wrapper).props('tieGroup')).toEqual([])
  })

  it('adds no badge when every score is unique', async () => {
    const wrapper = await mountList([
      makeRow({ tutor_id: 9, name: 'Ana Villanueva', hybrid_score: 0.912 }),
      makeRow({ tutor_id: 1, name: 'Maria Santos', hybrid_score: 0.845 }),
    ])

    expect(wrapper.find('.sb-badge.tie').exists()).toBe(false)
  })
})
