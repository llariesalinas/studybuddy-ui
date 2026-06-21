import { beforeEach, describe, expect, it } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useSidebarStore } from './sidebar'

describe('sidebar store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
  })

  it('defaults to expanded', () => {
    const store = useSidebarStore()
    expect(store.collapsed).toBe(false)
  })

  it('toggle flips collapsed and persists', () => {
    const store = useSidebarStore()
    store.toggle()
    expect(store.collapsed).toBe(true)
    expect(localStorage.getItem('sb-sidebar-collapsed')).toBe('1')
    store.toggle()
    expect(store.collapsed).toBe(false)
    expect(localStorage.getItem('sb-sidebar-collapsed')).toBe('0')
  })

  it('setCollapsed sets an explicit value', () => {
    const store = useSidebarStore()
    store.setCollapsed(true)
    expect(store.collapsed).toBe(true)
  })

  it('initSidebar reads a persisted collapsed value', () => {
    localStorage.setItem('sb-sidebar-collapsed', '1')
    const store = useSidebarStore()
    store.initSidebar()
    expect(store.collapsed).toBe(true)
  })
})
