import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'

const API_BASE_URL = 'http://127.0.0.1:8000/api/'

const api = axios.create({
  baseURL: API_BASE_URL,
})

let refreshPromise = null

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

    if (
      error.response &&
      error.response.status === 401 &&
      originalRequest &&
      !originalRequest._retry &&
      !originalRequest.url?.includes('token/refresh/')
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

    if (error.response && error.response.status === 401) {
      const authStore = useAuthStore()
      authStore.logout()
      router.push('/login')
    }

    return Promise.reject(error)
  }
)

export default api
