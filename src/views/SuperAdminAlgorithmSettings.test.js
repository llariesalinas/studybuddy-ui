import { flushPromises, mount } from '@vue/test-utils'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

const preview = vi.fn()
const getWeights = vi.fn()
const updateWeights = vi.fn()
vi.mock('@/services/api/algorithmWeights', () => ({
  getAlgorithmWeights: getWeights, previewAlgorithmWeights: preview, updateAlgorithmWeights: updateWeights,
}))
vi.mock('@/services/api/algorithmDemo', () => ({
  searchAlgorithmDemoTutees: vi.fn(async () => ({
    data: { tutees: [{ id: '1', name: 'A' }, { id: '2', name: 'B' }] },
  })),
}))
const { default: Settings } = await import('./SuperAdminAlgorithmSettings.vue')

let wrapper
let requests
const row = (name, id = 1) => ({ tutor_id: id, name, hybrid_score: 0.5 })

describe('weight preview response ordering', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    requests = []
    preview.mockImplementation((id) => new Promise((resolve, reject) => {
      requests.push({ id, resolve: (rows) => resolve({ data: { rows } }), reject })
    }))
    getWeights.mockResolvedValue({ data: {
      preview_enabled: true,
      groups: [{ group: 'cbf', label: 'Match', weights: [
        { key: 'specific', label: 'Specific', value: 0.4, default: 0.4 },
      ] }],
    } })
  })

  afterEach(() => {
    wrapper?.unmount()
    vi.useRealTimers()
  })

  async function start() {
    wrapper = mount(Settings, { global: { stubs: {
      SbSelectModal: {
        props: ['modelValue', 'options'], emits: ['update:modelValue'],
        template: `<select @change="$emit('update:modelValue', $event.target.value)">
          <option value="">Select</option><option value="1">A</option><option value="2">B</option>
        </select>`,
      },
    } } })
    await flushPromises()
    await wrapper.get('select').setValue('1')
  }

  it('ignores old tutee rankings and baselines arriving after the new selection', async () => {
    await start()
    await wrapper.get('select').setValue('2')
    expect(requests.map((request) => request.id)).toEqual(['1', '1', '2', '2'])
    requests[2].resolve([row('B tutor', 2)])
    requests[3].resolve([row('B tutor', 2)])
    await flushPromises()
    requests[0].resolve([row('A tutor')])
    requests[1].resolve([row('A tutor')])
    await flushPromises()
    expect(wrapper.text()).toContain('B tutor')
    expect(wrapper.text()).not.toContain('A tutor')
    expect(wrapper.get('.rank-delta').text()).toBe('–')
  })

  it('invalidates a response as soon as sliders change, before the debounce expires', async () => {
    await start()
    requests[0].resolve([row('Baseline tutor')])
    await wrapper.get('input[type="range"]').setValue('80')
    requests[1].resolve([row('Old weights tutor')])
    await flushPromises()
    expect(wrapper.text()).toContain('Scoring')
    await vi.advanceTimersByTimeAsync(350)
    requests[2].resolve([row('New weights tutor')])
    await flushPromises()
    expect(wrapper.text()).toContain('New weights tutor')
    expect(wrapper.text()).not.toContain('Old weights tutor')
  })

  it('does not show an error from an obsolete request', async () => {
    await start()
    await wrapper.get('select').setValue('2')
    requests[2].resolve([row('B tutor')])
    requests[3].resolve([row('B tutor')])
    requests[1].reject(new Error('old network error'))
    await flushPromises()
    expect(wrapper.text()).toContain('B tutor')
    expect(wrapper.text()).not.toContain('Could not run')
  })
  it('keeps a pending debounce from replacing the refreshed preview after Save', async () => {
    await start()
    updateWeights.mockResolvedValueOnce(await getWeights())
    await wrapper.get('input[type="range"]').setValue('80')
    const saveButton = wrapper.findAll('button').find((button) => button.text() === 'Save')
    await saveButton.trigger('click')
    await flushPromises()
    requests[2].resolve([row('Saved tutor')])
    requests[3].resolve([row('Saved tutor')])
    await flushPromises()
    await vi.advanceTimersByTimeAsync(350)
    expect(requests).toHaveLength(4)
    expect(wrapper.text()).toContain('Saved tutor')
    expect(wrapper.text()).not.toContain('Scoring')
  })

})
