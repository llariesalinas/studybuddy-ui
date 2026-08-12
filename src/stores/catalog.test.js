import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

const cachedGet = vi.fn()
const clearApiCache = vi.fn()
const api = {
  delete: vi.fn(),
  get: vi.fn(),
  patch: vi.fn(),
  post: vi.fn(),
}

vi.mock('@/services/api/cache', () => ({
  cachedGet,
  clearApiCache,
}))

vi.mock('@/services/api/api', () => ({
  default: api,
}))

const { useCatalogStore } = await import('./catalog')

describe('catalog store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    cachedGet.mockReset()
    clearApiCache.mockReset()
    Object.values(api).forEach((mock) => mock.mockReset())
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

  it('manages the subject catalog globally on the taxonomy shape', async () => {
    const subject = {
      subject_code: 'python',
      subject_name: 'Python',
      department: 'Programming Languages',
      category: 'Technology & Computer Science',
    }
    api.get.mockResolvedValueOnce({ data: [subject] })
    api.post.mockResolvedValueOnce({ data: subject })
    api.patch.mockResolvedValueOnce({ data: { ...subject, subject_name: 'Python 3' } })
    api.delete.mockResolvedValueOnce({})

    const catalog = useCatalogStore()
    await catalog.fetchCourseCatalog()
    await catalog.addCatalogSubject(subject)
    await catalog.updateCatalogSubject('python', { subject_name: 'Python 3' })
    await catalog.removeCatalogSubject('python')

    expect(api.get).toHaveBeenCalledWith('/admin/course-catalog/')
    expect(api.post).toHaveBeenCalledWith('/admin/course-catalog/', subject)
    expect(api.patch).toHaveBeenCalledWith('/admin/course-catalog/python/', {
      subject_name: 'Python 3',
    })
    expect(api.delete).toHaveBeenCalledWith('/admin/course-catalog/python/')
    expect(catalog.courseCatalog).toEqual([])
    // Each mutation must burst the cached tutee-facing subjects/ fetch, or pickers built on
    // `subjects` keep serving a stale pre-change list until the cache's TTL expires.
    expect(clearApiCache).toHaveBeenCalledTimes(3)
    expect(clearApiCache).toHaveBeenCalledWith('catalog')
  })

  it('bursts the subjects cache when a subject is synced in locally', () => {
    const catalog = useCatalogStore()
    catalog.upsertLocalCatalogSubject({ subject_code: 'python', subject_name: 'Python' })

    expect(clearApiCache).toHaveBeenCalledWith('catalog')
  })
})
