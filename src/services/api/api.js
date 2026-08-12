import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'
import { API_BASE_URL, DEMO_BASIC_AUTH_USER, DEMO_BASIC_AUTH_PASSWORD } from '../../config.js'

const isNgrok = API_BASE_URL.includes('ngrok')
const PUBLIC_ENDPOINTS = [
  'login/',
  'register/',
  'login/verify-otp/',
  'login/resend-otp/',
  'password-reset/request/',
  'password-reset/confirm/',
  'token/refresh/',
  'partner-institutions/',
  'courses/',
  'subjects/',
]

const demoAuthHeader =
  DEMO_BASIC_AUTH_USER && DEMO_BASIC_AUTH_PASSWORD
    ? `Basic ${btoa(`${DEMO_BASIC_AUTH_USER}:${DEMO_BASIC_AUTH_PASSWORD}`)}`
    : ''

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    ...(isNgrok ? { 'ngrok-skip-browser-warning': 'true' } : {}),
    ...(demoAuthHeader ? { 'X-Demo-Auth': demoAuthHeader } : {}),
  },
})

let refreshPromise = null

export const getApiPath = (requestUrl = '') => {
  return String(requestUrl)
    .replace(API_BASE_URL, '')
    .replace(/^https?:\/\/[^/]+\/api\/?/i, '')
    .replace(/^\/api\/?/i, '')
    .replace(/^\/+/, '')
}

const isPublicEndpoint = (requestUrl = '') => {
  const path = getApiPath(requestUrl)

  return PUBLIC_ENDPOINTS.some((endpoint) => path === endpoint || path.startsWith(`${endpoint}?`))
}

const refreshAccessToken = async () => {
  if (!refreshPromise) {
    const authStore = useAuthStore()

    refreshPromise = authStore
      .refreshAccessToken()
      .finally(() => {
        refreshPromise = null
      })
  }

  return refreshPromise
}

api.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    const token = authStore.token || localStorage.getItem('access_token')

    if (token) {
      config.headers = config.headers ?? {}
      config.headers.Authorization = `Bearer ${token}`
    }

    return config
  },
  (error) => Promise.reject(error)
)

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    const authStore = useAuthStore()
    const refreshTokenValue = authStore.refreshToken || localStorage.getItem('refresh_token')
    const requestUrl = originalRequest?.url || ''
    const isPublicRequest = isPublicEndpoint(requestUrl)

    if (
      error.response &&
      error.response.status === 401 &&
      originalRequest &&
      !originalRequest._retry &&
      !isPublicRequest &&
      refreshTokenValue
    ) {
      originalRequest._retry = true

      try {
        const newAccessToken = await refreshAccessToken()

        originalRequest.headers = originalRequest.headers ?? {}
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`

        return api(originalRequest)
      } catch (refreshError) {
        const authStore = useAuthStore()
        authStore.logout()
        router.push('/login')

        return Promise.reject(refreshError)
      }
    }

    if (error.response && error.response.status === 401 && !isPublicRequest) {
      authStore.logout()
      router.push('/login')
    }

    return Promise.reject(error)
  }
)

export default api
