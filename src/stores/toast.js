import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useToastStore = defineStore('toast', () => {
  const toasts = ref([])
  let nextId = 0

  // `action` is an optional { label, handler } pair rendered as an inline button -- used by the
  // dual-role auto-switch toast to offer Undo, since that switch happens without the user asking.
  function push(message, type = 'success', duration = 3500, action = null) {
    const id = ++nextId
    toasts.value.push({ id, message, type, action })
    setTimeout(() => dismiss(id), duration)
  }

  function dismiss(id) {
    const idx = toasts.value.findIndex(t => t.id === id)
    if (idx !== -1) toasts.value.splice(idx, 1)
  }

  return { toasts, push, dismiss }
})
