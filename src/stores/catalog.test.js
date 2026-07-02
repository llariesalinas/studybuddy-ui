import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

const cachedGet = vi.fn()

vi.mock('@/services/api/cache', () => ({
  cachedGet,
}))

const { useCatalogStore } = await import('./catalog')

describe('catalog store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    cachedGet.mockReset()
  })

  it('fetches and caches receiving institutions', async () => {
    const institutions = [{ code: 'GCASH', name: 'GCash' }]
    cachedGet.mockResolvedValueOnce({ data: institutions })

    const catalog = useCatalogStore()

    await expect(catalog.fetchReceivingInstitutions()).resolves.toEqual(institutions)

    expect(cachedGet).toHaveBeenCalledWith('wallet/receiving-institutions/', expect.objectContaining({
      scope: 'catalog',
      cacheKey: 'wallet/receiving-institutions',
    }))
    expect(catalog.receivingInstitutions).toEqual(institutions)
  })
})
