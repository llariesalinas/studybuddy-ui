import { beforeEach, describe, expect, it } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useDensityStore } from './density'

const densityAttr = () => document.documentElement.getAttribute('data-sb-density')

describe('density store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    document.documentElement.removeAttribute('data-sb-density')
  })

  it('defaults to comfortable with no attribute set', () => {
    const store = useDensityStore()
    expect(store.density).toBe('comfortable')
    expect(densityAttr()).toBeNull()
  })

  it('setDensity toggles the attribute both ways', () => {
    const store = useDensityStore()
    store.setDensity('compact')
    expect(store.density).toBe('compact')
    expect(densityAttr()).toBe('compact')
    store.setDensity('comfortable')
    expect(store.density).toBe('comfortable')
    expect(densityAttr()).toBeNull()
  })

  it('syncFromRole puts tutee, tutor and superadmin at compact density', () => {
    const store = useDensityStore()
    for (const role of ['tutee', 'tutor', 'superadmin']) {
      store.setDensity('comfortable')
      store.syncFromRole(role)
      expect(store.density, role).toBe('compact')
      expect(densityAttr(), role).toBe('compact')
    }
  })

  it('syncFromRole leaves admin at comfortable density', () => {
    const store = useDensityStore()
    store.setDensity('compact')
    store.syncFromRole('admin')
    expect(store.density).toBe('comfortable')
    expect(densityAttr()).toBeNull()
  })

  it('syncFromRole handles a logged-out role without throwing', () => {
    const store = useDensityStore()
    for (const role of [null, undefined, '']) {
      store.setDensity('compact')
      store.syncFromRole(role)
      expect(store.density).toBe('comfortable')
      expect(densityAttr()).toBeNull()
    }
  })

  it('syncFromRole is case-insensitive', () => {
    const store = useDensityStore()
    store.syncFromRole('Tutor')
    expect(store.density).toBe('compact')
    store.syncFromRole('Admin')
    expect(store.density).toBe('comfortable')
    store.syncFromRole('SuperAdmin')
    expect(store.density).toBe('compact')
  })
})
