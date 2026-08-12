import { flushPromises, mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import SbExportModal from './SbExportModal.vue'
import { todayKey } from '@/utils/time'

const items = [
  { id: 'summary', label: 'Summary', fileLabel: 'summary' },
  { id: 'top_tutors', label: 'Top Tutors', fileLabel: 'top-tutors' },
  { id: 'transactions', label: 'Booking Transactions', fileLabel: 'transactions' },
]

const mountModal = (props = {}) => mount(SbExportModal, {
  props: {
    open: true,
    title: 'Export report',
    items,
    combinedFileLabel: 'report',
    ...props,
  },
  // The dialog is teleported to body, which would put it outside the wrapper's tree.
  global: { stubs: { teleport: true } },
})

const checkboxes = (wrapper) => wrapper.findAll('.sb-export-checkbox')
const exportButton = (wrapper) => wrapper.find('.sb-export-btn.is-primary')

describe('SbExportModal', () => {
  it('opens with every item ticked', async () => {
    const wrapper = mountModal()
    await flushPromises()

    expect(checkboxes(wrapper).every((input) => input.element.checked)).toBe(true)
    expect(exportButton(wrapper).text()).toContain('Export 3')
    expect(wrapper.findAll('.sb-export-manifest li')).toHaveLength(3)
  })

  it('disables Export once nothing is ticked', async () => {
    const wrapper = mountModal()
    await flushPromises()

    await wrapper.find('.sb-export-linkbtn').trigger('click')

    expect(exportButton(wrapper).attributes('disabled')).toBeDefined()
    expect(wrapper.find('.sb-export-manifest-empty').exists()).toBe(true)
    expect(wrapper.emitted('confirm')).toBeUndefined()
  })

  it('emits the ticked ids in declaration order, not click order', async () => {
    const wrapper = mountModal()
    await flushPromises()

    await wrapper.find('.sb-export-linkbtn').trigger('click')
    await checkboxes(wrapper)[2].setValue(true)
    await checkboxes(wrapper)[0].setValue(true)
    await exportButton(wrapper).trigger('click')

    expect(wrapper.emitted('confirm')[0][0].ids).toEqual(['summary', 'transactions'])
  })

  it('names the file after the only ticked item', async () => {
    const wrapper = mountModal()
    await flushPromises()

    await wrapper.find('.sb-export-linkbtn').trigger('click')
    await checkboxes(wrapper)[2].setValue(true)

    expect(wrapper.find('.sb-export-filename').text())
      .toBe(`studybuddy-transactions-${todayKey()}.csv`)
  })

  it('falls back to the combined label when several are ticked', async () => {
    const wrapper = mountModal()
    await flushPromises()

    expect(wrapper.find('.sb-export-filename').text())
      .toBe(`studybuddy-report-${todayKey()}.csv`)
  })

  it('honours fileExtension, so the analytics workbook previews as .xlsx', async () => {
    const wrapper = mountModal({ fileExtension: 'xlsx' })
    await flushPromises()

    expect(wrapper.find('.sb-export-filename').text())
      .toBe(`studybuddy-report-${todayKey()}.xlsx`)
  })

  it('renders nothing while closed', () => {
    const wrapper = mountModal({ open: false })
    expect(wrapper.find('.sb-export-dialog').exists()).toBe(false)
  })
})
