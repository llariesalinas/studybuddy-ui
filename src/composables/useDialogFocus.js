import { nextTick, onBeforeUnmount, watch } from 'vue'

const openDialogs = []
const focusableSelector =
  'a[href], button:not(:disabled), input:not(:disabled):not([type="hidden"]), ' +
  'select:not(:disabled), textarea:not(:disabled), [tabindex]:not([tabindex="-1"])'

export function useDialogFocus(isOpen, dialogRef, close) {
  const entry = {}
  let previousFocus = null

  const release = () => {
    const index = openDialogs.indexOf(entry)
    if (index !== -1) openDialogs.splice(index, 1)
    document.removeEventListener('keydown', handleKeydown, true)
    if (previousFocus?.isConnected) previousFocus.focus()
    previousFocus = null
  }

  const controls = () =>
    [...(dialogRef.value?.querySelectorAll(focusableSelector) || [])].filter(
      (element) =>
        !element.closest('[hidden], [inert]') && element.getAttribute('tabindex') !== '-1',
    )

  function handleKeydown(event) {
    if (openDialogs.at(-1) !== entry) return
    if (event.key === 'Escape') {
      event.preventDefault()
      event.stopPropagation()
      close()
      return
    }
    if (event.key !== 'Tab') return
    const items = controls()
    const first = items[0]
    const last = items.at(-1)
    const active = document.activeElement
    if (!first) {
      event.preventDefault()
      dialogRef.value?.focus()
    } else if (event.shiftKey && (active === first || !items.includes(active))) {
      event.preventDefault()
      last.focus()
    } else if (!event.shiftKey && (active === last || !items.includes(active))) {
      event.preventDefault()
      first.focus()
    }
  }

  watch(
    isOpen,
    async (open) => {
      if (!open) {
        release()
        return
      }
      previousFocus = document.activeElement
      openDialogs.push(entry)
      document.addEventListener('keydown', handleKeydown, true)
      await nextTick()
      if (!isOpen.value || openDialogs.at(-1) !== entry) return
      if (!dialogRef.value?.contains(document.activeElement)) {
        const initialControl = controls()[0] || dialogRef.value
        initialControl?.focus()
      }
    },
    { immediate: true },
  )

  onBeforeUnmount(release)
}
