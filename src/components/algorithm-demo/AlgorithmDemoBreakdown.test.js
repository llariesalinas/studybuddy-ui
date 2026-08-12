import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import AlgorithmDemoBreakdown from './AlgorithmDemoBreakdown.vue'

// The curated S6 Katrina Katigbak -> T1 Marisol Aquino case documented in
// docs/architecture/algorithm-demo-guide.html, with S2 Gloria Garcia as the open
// neighbour. Katrina's baseline over all five of her ratings is 3.80, but her
// average over the four tutors she shares with Gloria is 4.25 — the divergence the
// panel has to label rather than leave a panelist to reconcile.
const NEIGHBOR_ID = 2
const TUTOR_ID = 1

const makeRow = () => ({
  tutor_id: TUTOR_ID,
  name: 'Marisol Aquino',
  hybrid_score: 0.927,
  cold_start: false,
  upcoming_week_load: 0,
  tie_group_id: null,
  cbf: Object.fromEntries(
    ['specific', 'general', 'expertise', 'course', 'year', 'level'].map((key) => [
      key,
      { value: 0.5, weight: 0.2 }
    ])
  ),
  cf: {
    score: 4.742,
    pool: 'peer',
    student_avg: 3.8,
    student_rating: 5,
    numerator: 2.81,
    denominator: 2.98,
    neighbors: [
      {
        neighbor_id: NEIGHBOR_ID,
        name: 'Gloria Garcia',
        similarity: 0.853,
        rating: 5,
        neighbor_avg: 4.0,
        deviation: 1.0,
        weighted: 0.853,
        co_rated_count: 4
      }
    ]
  }
})

const makeCoRated = (overrides = {}) => ({
  [NEIGHBOR_ID]: {
    student_avg_over_set: 4.25,
    neighbor_avg_over_set: 4.0,
    shared: [
      { tutor_id: 1, name: 'Marisol Aquino', last_name: 'Aquino', student_rating: 5, neighbor_rating: 5 },
      { tutor_id: 2, name: 'Benigno Bautista', last_name: 'Bautista', student_rating: 3, neighbor_rating: 3 },
      { tutor_id: 6, name: 'Fidel Fajardo', last_name: 'Fajardo', student_rating: 5, neighbor_rating: 4 },
      { tutor_id: 8, name: 'Hector Hidalgo', last_name: 'Hidalgo', student_rating: 4, neighbor_rating: 4 }
    ],
    ...overrides
  }
})

const mountBreakdown = (coRated = makeCoRated()) =>
  mount(AlgorithmDemoBreakdown, { props: { row: makeRow(), coRated } })

const toggle = (wrapper) => wrapper.find('.cf-corated-toggle')

describe('AlgorithmDemoBreakdown co-rated set', () => {
  it('keeps the co-rated set collapsed until asked', () => {
    const wrapper = mountBreakdown()

    expect(toggle(wrapper).text()).toContain('4 co-rated')
    expect(toggle(wrapper).attributes('aria-expanded')).toBe('false')
    expect(wrapper.find('.cf-corated').exists()).toBe(false)
  })

  it('expands to the shared tutors with both students scores', async () => {
    const wrapper = mountBreakdown()

    await toggle(wrapper).trigger('click')

    expect(toggle(wrapper).attributes('aria-expanded')).toBe('true')
    const headers = wrapper.findAll('.cf-corated-head[title]').map((n) => n.text())
    expect(headers).toEqual(['Aquino', 'Bautista', 'Fajardo', 'Hidalgo'])

    const cells = wrapper
      .findAll('.cf-corated-cell')
      .filter((n) => !n.classes('cf-corated-avg'))
      .map((n) => n.text())
    expect(cells).toEqual(['5', '3', '5', '4', '5', '3', '4', '4'])
  })

  it('labels the columns by surname with the full name on hover', async () => {
    const wrapper = mountBreakdown()

    await toggle(wrapper).trigger('click')

    const first = wrapper.findAll('.cf-corated-head[title]')[0]
    expect(first.text()).toBe('Aquino')
    expect(first.attributes('title')).toBe('Marisol Aquino')
  })

  it('shows the co-rated average distinctly from the baseline it is not', async () => {
    const wrapper = mountBreakdown()

    await toggle(wrapper).trigger('click')

    const averages = wrapper.findAll('.cf-corated-avg.cf-corated-cell').map((n) => n.text())
    expect(averages[0]).toContain('4.25')
    expect(averages[0]).toContain('feeds similarity')
    expect(averages[1]).toContain('4.00')

    // The two baselines the expansion could be confused with are named explicitly.
    const note = wrapper.find('.cf-corated-note').text()
    expect(note).toContain('4.00')
    expect(note).toContain('3.80')
  })

  it('renders shared ratings as read-only, keeping the neighbour slider the only control', async () => {
    const wrapper = mountBreakdown()

    await toggle(wrapper).trigger('click')

    expect(wrapper.find('.cf-corated').findAll('input')).toHaveLength(0)
    expect(wrapper.findAll('.cf-rate input[type="range"]')).toHaveLength(1)
  })

  it('closes again on a second click, keeping one neighbour open at a time', async () => {
    const wrapper = mountBreakdown()

    await toggle(wrapper).trigger('click')
    await toggle(wrapper).trigger('click')

    expect(wrapper.find('.cf-corated').exists()).toBe(false)
  })

  it('stays open across a what-if refetch and flashes only what changed', async () => {
    const wrapper = mountBreakdown()
    await toggle(wrapper).trigger('click')

    // Dragging Gloria's rating of the candidate tutor lands inside the co-rated set,
    // because Katrina has rated that tutor too — her cell and her average move.
    await wrapper.setProps({
      coRated: makeCoRated({
        neighbor_avg_over_set: 3.25,
        shared: [
          { tutor_id: 1, name: 'Marisol Aquino', last_name: 'Aquino', student_rating: 5, neighbor_rating: 2 },
          { tutor_id: 2, name: 'Benigno Bautista', last_name: 'Bautista', student_rating: 3, neighbor_rating: 3 },
          { tutor_id: 6, name: 'Fidel Fajardo', last_name: 'Fajardo', student_rating: 5, neighbor_rating: 4 },
          { tutor_id: 8, name: 'Hector Hidalgo', last_name: 'Hidalgo', student_rating: 4, neighbor_rating: 4 }
        ]
      })
    })

    expect(wrapper.find('.cf-corated').exists()).toBe(true)

    const flashed = wrapper.findAll('.cf-corated-cell.flash').map((n) => n.text())
    expect(flashed).toHaveLength(2)
    expect(flashed[0]).toBe('2')
    expect(flashed[1]).toContain('3.25')
  })

  it('closes when a different tutor is selected', async () => {
    const wrapper = mountBreakdown()
    await toggle(wrapper).trigger('click')

    await wrapper.setProps({ row: { ...makeRow(), tutor_id: 99, name: 'Fidel Fajardo' } })

    expect(wrapper.find('.cf-corated').exists()).toBe(false)
  })

  it('survives a neighbour with no co-rated entry in the map', async () => {
    const wrapper = mountBreakdown({})

    await toggle(wrapper).trigger('click')

    expect(wrapper.find('.cf-corated').exists()).toBe(false)
  })
})
