import api, { getApiPath } from '@/services/api/api'
import { useAuthStore } from '@/stores/auth'

const CACHE_PREFIX = 'sb'
const inflightRequests = new Map()

const canUseSessionStorage = () => typeof window !== 'undefined' && window.sessionStorage
const canUseLocalStorage = () => typeof window !== 'undefined' && window.localStorage

const getCurrentUserId = () => {
  try {
    const authStore = useAuthStore()
    if (authStore.user?.id) {
      return String(authStore.user.id)
    }
  } catch {
    // Pinia may not be active in low-level tests or early bootstrap.
  }

  if (canUseLocalStorage()) {
    return window.localStorage.getItem('user_id') || 'anon'
  }

  return 'anon'
}

const stableStringify = (value) => {
  if (value === null || typeof value !== 'object') {
    return JSON.stringify(value)
  }

  if (Array.isArray(value)) {
    return `[${value.map(stableStringify).join(',')}]`
  }

  return `{${Object.keys(value)
    .sort()
    .map((key) => `${JSON.stringify(key)}:${stableStringify(value[key])}`)
    .join(',')}}`
}

const encodeKeyPart = (value) => encodeURIComponent(String(value)).replace(/%/g, '~')

export const buildCacheKey = ({ url, params, scope = 'api', cacheKey, userId = getCurrentUserId() }) => {
  const path = cacheKey || getApiPath(url)
  const serializedParams = stableStringify(params || {})
  return [
    CACHE_PREFIX,
    encodeKeyPart(scope),
    encodeKeyPart(userId),
    encodeKeyPart(path),
    encodeKeyPart(serializedParams),
  ].join('-')
}

const readCache = (key) => {
  if (!canUseSessionStorage()) {
    return null
  }

  const raw = window.sessionStorage.getItem(key)
  if (!raw) {
    return null
  }

  try {
    const entry = JSON.parse(raw)
    if (!entry || typeof entry.expiresAt !== 'number' || !Object.prototype.hasOwnProperty.call(entry, 'value')) {
      window.sessionStorage.removeItem(key)
      return null
    }

    if (entry.expiresAt <= Date.now()) {
      window.sessionStorage.removeItem(key)
      return null
    }

    return entry.value
  } catch {
    window.sessionStorage.removeItem(key)
    return null
  }
}

const writeCache = (key, value, ttlMs, userId) => {
  if (!canUseSessionStorage() || !ttlMs || ttlMs <= 0) {
    return
  }

  const now = Date.now()
  window.sessionStorage.setItem(
    key,
    JSON.stringify({
      value,
      userId,
      cachedAt: now,
      expiresAt: now + ttlMs,
    }),
  )
}

export const cachedGet = async (url, {
  params,
  ttlMs,
  force = false,
  scope = 'api',
  cacheKey,
} = {}) => {
  const userId = getCurrentUserId()
  const key = buildCacheKey({ url, params, scope, cacheKey, userId })

  if (!force) {
    const cachedValue = readCache(key)
    if (cachedValue !== null) {
      return { data: cachedValue }
    }

    if (inflightRequests.has(key)) {
      return inflightRequests.get(key)
    }
  }

  const request = api.get(url, { params })
    .then((response) => {
      writeCache(key, response.data, ttlMs, userId)
      return { data: response.data }
    })
    .finally(() => {
      inflightRequests.delete(key)
    })

  inflightRequests.set(key, request)
  return request
}

export const clearApiCache = (scope) => {
  if (!canUseSessionStorage()) {
    return
  }

  const prefix = scope ? `${CACHE_PREFIX}-${encodeKeyPart(scope)}-` : `${CACHE_PREFIX}-`
  const keys = []

  for (let index = 0; index < window.sessionStorage.length; index += 1) {
    const key = window.sessionStorage.key(index)
    if (key?.startsWith(prefix)) {
      keys.push(key)
    }
  }

  keys.forEach((key) => window.sessionStorage.removeItem(key))
}
