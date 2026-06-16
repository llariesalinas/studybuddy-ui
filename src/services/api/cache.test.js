import { beforeEach, describe, expect, it, vi } from 'vitest'

const apiGet = vi.fn()
let authUser

vi.mock('@/services/api/api', () => ({
  default: {
    get: apiGet,
  },
  getApiPath: (requestUrl = '') => String(requestUrl).replace(/^\/api\/?/i, '').replace(/^\/+/, ''),
}))

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => ({
    user: authUser,
  }),
}))

const { buildCacheKey, cachedGet } = await import('./cache')

const makeDeferred = () => {
  let resolve
  let reject
  const promise = new Promise((promiseResolve, promiseReject) => {
    resolve = promiseResolve
    reject = promiseReject
  })

  return { promise, resolve, reject }
}

describe('api cache', () => {
  beforeEach(() => {
    vi.useRealTimers()
    apiGet.mockReset()
    authUser = null
    window.sessionStorage.clear()
    window.localStorage.clear()
  })

  it('returns { data } from a sessionStorage miss and caches the response', async () => {
    authUser = { id: 7 }
    apiGet.mockResolvedValueOnce({ data: [{ id: 1, name: 'Math' }] })

    const result = await cachedGet('subjects/', {
      params: { level: 'college' },
      ttlMs: 1000,
      scope: 'catalog',
    })

    expect(result).toEqual({ data: [{ id: 1, name: 'Math' }] })
    expect(apiGet).toHaveBeenCalledTimes(1)
    expect(apiGet).toHaveBeenCalledWith('subjects/', { params: { level: 'college' } })

    const key = buildCacheKey({
      url: 'subjects/',
      params: { level: 'college' },
      scope: 'catalog',
      userId: '7',
    })
    const cachedEntry = JSON.parse(window.sessionStorage.getItem(key))

    expect(cachedEntry.value).toEqual([{ id: 1, name: 'Math' }])
    expect(cachedEntry.userId).toBe('7')
  })

  it('returns cached sessionStorage data without calling the API', async () => {
    const key = buildCacheKey({
      url: 'courses/',
      params: { q: 'science' },
      scope: 'catalog',
      userId: 'anon',
    })

    window.sessionStorage.setItem(
      key,
      JSON.stringify({
        value: ['Biology'],
        userId: 'anon',
        cachedAt: Date.now(),
        expiresAt: Date.now() + 1000,
      }),
    )

    const result = await cachedGet('courses/', {
      params: { q: 'science' },
      ttlMs: 1000,
      scope: 'catalog',
    })

    expect(result).toEqual({ data: ['Biology'] })
    expect(apiGet).not.toHaveBeenCalled()
  })

  it('expires stale sessionStorage entries and refreshes them', async () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2026-06-06T00:00:00Z'))

    apiGet.mockResolvedValueOnce({ data: ['Fresh'] })
    const key = buildCacheKey({
      url: 'subjects/',
      scope: 'catalog',
      userId: 'anon',
    })

    window.sessionStorage.setItem(
      key,
      JSON.stringify({
        value: ['Stale'],
        userId: 'anon',
        cachedAt: Date.now() - 2000,
        expiresAt: Date.now() - 1,
      }),
    )

    const result = await cachedGet('subjects/', {
      ttlMs: 5000,
      scope: 'catalog',
    })

    expect(result).toEqual({ data: ['Fresh'] })
    expect(apiGet).toHaveBeenCalledTimes(1)
    expect(JSON.parse(window.sessionStorage.getItem(key)).value).toEqual(['Fresh'])
  })

  it('force refresh bypasses a valid cache entry', async () => {
    const key = buildCacheKey({
      url: 'payment-methods/',
      scope: 'catalog',
      userId: 'anon',
    })

    window.sessionStorage.setItem(
      key,
      JSON.stringify({
        value: ['Cached'],
        userId: 'anon',
        cachedAt: Date.now(),
        expiresAt: Date.now() + 1000,
      }),
    )
    apiGet.mockResolvedValueOnce({ data: ['Fresh'] })

    const result = await cachedGet('payment-methods/', {
      ttlMs: 1000,
      scope: 'catalog',
      force: true,
    })

    expect(result).toEqual({ data: ['Fresh'] })
    expect(apiGet).toHaveBeenCalledTimes(1)
    expect(JSON.parse(window.sessionStorage.getItem(key)).value).toEqual(['Fresh'])
  })

  it('dedupes concurrent in-flight requests for the same cache key', async () => {
    const deferred = makeDeferred()
    apiGet.mockReturnValueOnce(deferred.promise)

    const first = cachedGet('subjects/', { ttlMs: 1000, scope: 'catalog' })
    const second = cachedGet('subjects/', { ttlMs: 1000, scope: 'catalog' })

    expect(apiGet).toHaveBeenCalledTimes(1)

    deferred.resolve({ data: ['Algebra'] })

    await expect(first).resolves.toEqual({ data: ['Algebra'] })
    await expect(second).resolves.toEqual({ data: ['Algebra'] })
  })

  it('removes malformed cache entries before fetching fresh data', async () => {
    const key = buildCacheKey({
      url: 'subjects/',
      scope: 'catalog',
      userId: 'anon',
    })

    window.sessionStorage.setItem(key, '{bad json')
    apiGet.mockResolvedValueOnce({ data: ['Clean'] })

    const result = await cachedGet('subjects/', {
      ttlMs: 1000,
      scope: 'catalog',
    })

    expect(result).toEqual({ data: ['Clean'] })
    expect(apiGet).toHaveBeenCalledTimes(1)
    expect(JSON.parse(window.sessionStorage.getItem(key)).value).toEqual(['Clean'])
  })

  it('scopes cache keys by the current user', async () => {
    window.localStorage.setItem('user_id', 'user-a')
    apiGet.mockResolvedValueOnce({ data: ['User A'] })

    await expect(cachedGet('subjects/', { ttlMs: 1000, scope: 'catalog' })).resolves.toEqual({
      data: ['User A'],
    })

    window.localStorage.setItem('user_id', 'user-b')
    apiGet.mockResolvedValueOnce({ data: ['User B'] })

    await expect(cachedGet('subjects/', { ttlMs: 1000, scope: 'catalog' })).resolves.toEqual({
      data: ['User B'],
    })

    expect(apiGet).toHaveBeenCalledTimes(2)
    expect(window.sessionStorage.getItem(buildCacheKey({
      url: 'subjects/',
      scope: 'catalog',
      userId: 'user-a',
    }))).toContain('User A')
    expect(window.sessionStorage.getItem(buildCacheKey({
      url: 'subjects/',
      scope: 'catalog',
      userId: 'user-b',
    }))).toContain('User B')
  })
})
