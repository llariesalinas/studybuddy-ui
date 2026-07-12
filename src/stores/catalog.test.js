import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

const cachedGet = vi.fn()
const api = {
  delete: vi.fn(),
  get: vi.fn(),
  patch: vi.fn(),
  post: vi.fn(),
}

vi.mock('@/services/api/cache', () => ({
  cachedGet,
}))

vi.mock('@/services/api/api', () => ({
  default: api,
}))

const { useCatalogStore } = await import('./catalog')

describe('catalog store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    cachedGet.mockReset()
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

  it('manages the subject catalog globally without institution parameters', async () => {
    const subject = {
      subject_code: 'CS101',
      subject_name: 'Introduction to Computing',
      department: 'Computer Science',
      category: 'BSCS',
    }
    api.get.mockResolvedValueOnce({ data: [subject] })
    api.post.mockResolvedValueOnce({ data: subject })
    api.patch.mockResolvedValueOnce({ data: { ...subject, subject_name: 'Computing' } })
    api.delete.mockResolvedValueOnce({})

    const catalog = useCatalogStore()
    await catalog.fetchCourseCatalog()
    await catalog.addCatalogSubject(subject)
    await catalog.updateCatalogSubject('CS101', { subject_name: 'Computing' })
    await catalog.removeCatalogSubject('CS101')

    expect(api.get).toHaveBeenCalledWith('/admin/course-catalog/')
    expect(api.post).toHaveBeenCalledWith('/admin/course-catalog/', subject)
    expect(api.patch).toHaveBeenCalledWith('/admin/course-catalog/CS101/', {
      subject_name: 'Computing',
    })
    expect(api.delete).toHaveBeenCalledWith('/admin/course-catalog/CS101/')
    expect(catalog.courseCatalog).toEqual([])
  })
})
