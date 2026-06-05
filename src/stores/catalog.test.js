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

  it('keys receiving institutions by normalized provider', async () => {
    const instapayInstitutions = [{ code: 'INSTAPAY_BANK', name: 'Instapay Bank' }]
    const pesonetInstitutions = [{ code: 'PESONET_BANK', name: 'Pesonet Bank' }]

    cachedGet
      .mockResolvedValueOnce({ data: instapayInstitutions })
      .mockResolvedValueOnce({ data: pesonetInstitutions })

    const catalog = useCatalogStore()

    await expect(catalog.fetchReceivingInstitutions('InstaPay')).resolves.toEqual(instapayInstitutions)
    await expect(catalog.fetchReceivingInstitutions('PESONet')).resolves.toEqual(pesonetInstitutions)

    expect(cachedGet).toHaveBeenNthCalledWith(1, 'wallet/receiving-institutions/', expect.objectContaining({
      params: { provider: 'instapay' },
      scope: 'catalog',
      cacheKey: 'wallet/receiving-institutions/instapay',
    }))
    expect(cachedGet).toHaveBeenNthCalledWith(2, 'wallet/receiving-institutions/', expect.objectContaining({
      params: { provider: 'pesonet' },
      scope: 'catalog',
      cacheKey: 'wallet/receiving-institutions/pesonet',
    }))
    expect(catalog.receivingInstitutionsByProvider).toEqual({
      instapay: instapayInstitutions,
      pesonet: pesonetInstitutions,
    })
  })

  it('uses instapay as the receiving-institution provider fallback', async () => {
    const institutions = [{ code: 'DEFAULT_BANK', name: 'Default Bank' }]

    cachedGet.mockResolvedValueOnce({ data: institutions })

    const catalog = useCatalogStore()

    await expect(catalog.fetchReceivingInstitutions()).resolves.toEqual(institutions)

    expect(cachedGet).toHaveBeenCalledWith('wallet/receiving-institutions/', expect.objectContaining({
      params: { provider: 'instapay' },
      scope: 'catalog',
      cacheKey: 'wallet/receiving-institutions/instapay',
    }))
    expect(catalog.receivingInstitutionsByProvider.instapay).toEqual(institutions)
  })
})
