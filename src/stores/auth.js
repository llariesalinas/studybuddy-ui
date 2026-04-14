import axios from 'axios'
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api/api'
import { useProfileStore } from '@/stores/profile'
import { useFindTutorsStore } from '@/stores/findTutors'
import {
  startIdleSessionTracking,
  stopIdleSessionTracking
} from '@/services/auth/idleSession'

const API_BASE_URL = 'http://127.0.0.1:8000/api/'
const ACCESS_REFRESH_INTERVAL_MS = 4 * 60 * 1000

let refreshIntervalId = null

export const useAuthStore = defineStore('auth', () => {
  const profileStore = useProfileStore()
  const findTutorsStore = useFindTutorsStore()

  const normalizeRole = (role) => {
    if (!role) {
      return null
    }

    return String(role).toLowerCase()
  }

  const handleIdleLogout = () => {
    logout()

    if (typeof window !== 'undefined' && window.location.pathname !== '/login') {
      window.location.replace('/login')
    }
  }

  const token = ref(localStorage.getItem('access_token') || null)
  const refreshToken = ref(localStorage.getItem('refresh_token') || null)
  const user = ref(null)

  const isAuthenticated = computed(() => !!token.value)
  const userRole = computed(() => user.value?.role || null)

  const setTokens = ({ accessToken, refreshTokenValue }) => {
    token.value = accessToken
    refreshToken.value = refreshTokenValue

    localStorage.setItem('access_token', accessToken)
    localStorage.setItem('refresh_token', refreshTokenValue)
  }

  const updateAccessToken = (accessToken) => {
    token.value = accessToken
    localStorage.setItem('access_token', accessToken)
  }

  const stopAccessTokenRefresh = () => {
    if (refreshIntervalId !== null && typeof window !== 'undefined') {
      window.clearInterval(refreshIntervalId)
      refreshIntervalId = null
    }
  }

  const refreshAccessToken = async () => {
    const storedRefreshToken = refreshToken.value || localStorage.getItem('refresh_token')

    if (!storedRefreshToken) {
      throw new Error('No refresh token available.')
    }

    const response = await axios.post(`${API_BASE_URL}token/refresh/`, {
      refresh: storedRefreshToken
    })

    const newAccessToken = response.data.access

    if (!newAccessToken) {
      throw new Error('No access token returned from refresh endpoint.')
    }

    updateAccessToken(newAccessToken)
    return newAccessToken
  }

  const startAccessTokenRefresh = () => {
    stopAccessTokenRefresh()

    if (typeof window === 'undefined' || !refreshToken.value) {
      return
    }

    refreshIntervalId = window.setInterval(async () => {
      try {
        await refreshAccessToken()
      } catch {
        logout()

        if (window.location.pathname !== '/login') {
          window.location.replace('/login')
        }
      }
    }, ACCESS_REFRESH_INTERVAL_MS)
  }

  const startSessionTracking = () => {
    startIdleSessionTracking(handleIdleLogout)
    startAccessTokenRefresh()
  }

  const login = async (credentials) => {
    const response = await api.post('login/', credentials)

    const receivedToken = response.data.access
    const receivedRefreshToken = response.data.refresh

    if (!receivedToken || !receivedRefreshToken) {
      throw new Error('Missing authentication token(s) from server.')
    }

    setTokens({
      accessToken: receivedToken,
      refreshTokenValue: receivedRefreshToken
    })

    user.value = {
      email: response.data.email,
      role: normalizeRole(response.data.role),
      id: response.data.user_id,
      fname: response.data.fname,
      lname: response.data.lname
    }

    localStorage.setItem('user_role', normalizeRole(response.data.role))
    profileStore.resetProfileState()

    startSessionTracking()

    return response.data.role
  }

  const logout = () => {
    stopIdleSessionTracking()
    stopAccessTokenRefresh()

    token.value = null
    refreshToken.value = null
    user.value = null
    profileStore.resetProfileState()

    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user_role')
    findTutorsStore.reset()
  }

  const initializeAuth = () => {
    const storedToken = localStorage.getItem('access_token')
    const storedRefreshToken = localStorage.getItem('refresh_token')
    const storedRole = localStorage.getItem('user_role')

    if (storedToken && storedRefreshToken) {
      token.value = storedToken
      refreshToken.value = storedRefreshToken
      startSessionTracking()
    }

    if (storedRole) {
      user.value = {
        role: normalizeRole(storedRole)
      }
    }
  }

  return {
    token,
    refreshToken,
    user,
    userRole,
    isAuthenticated,
    setTokens,
    updateAccessToken,
    refreshAccessToken,
    login,
    logout,
    initializeAuth
  }
})
