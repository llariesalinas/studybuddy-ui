import { ref } from 'vue'
import { defineStore } from 'pinia'

const STORAGE_KEY = 'sb-sidebar-collapsed'

export const useSidebarStore = defineStore('sidebar', () => {
  const collapsed = ref(false)

  function setCollapsed(value) {
    collapsed.value = Boolean(value)
    localStorage.setItem(STORAGE_KEY, collapsed.value ? '1' : '0')
  }

  function toggle() {
    setCollapsed(!collapsed.value)
  }

  function initSidebar() {
    collapsed.value = localStorage.getItem(STORAGE_KEY) === '1'
  }

  return { collapsed, setCollapsed, toggle, initSidebar }
})
