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
import { API_BASE_URL, ACCESS_REFRESH_INTERVAL_MS } from '../config.js'

let refreshIntervalId = null

const clearStudyBuddySessionCache = () => {
  if (typeof window === 'undefined' || !window.sessionStorage) {
    return
  }

  const keys = []
  for (let index = 0; index < window.sessionStorage.length; index += 1) {
    const key = window.sessionStorage.key(index)
    if (key?.startsWith('sb-')) {
      keys.push(key)
    }
  }
  keys.forEach((key) => window.sessionStorage.removeItem(key))
}

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

    const ngrokHeaders = API_BASE_URL.includes('ngrok')
      ? { 'ngrok-skip-browser-warning': 'true' }
      : {}

    const response = await axios.post(`${API_BASE_URL}token/refresh/`, {
      refresh: storedRefreshToken
    }, { headers: ngrokHeaders })

    const newAccessToken = response.data.access

    if (!newAccessToken) {
      throw new Error('No access token returned from refresh endpoint.')
    }

    updateAccessToken(newAccessToken)

    // Backend rotates refresh tokens (ROTATE_REFRESH_TOKENS) and blacklists the
    // old one, so persist the new refresh token or the next refresh will fail.
    const rotatedRefreshToken = response.data.refresh
    if (rotatedRefreshToken) {
      refreshToken.value = rotatedRefreshToken
      localStorage.setItem('refresh_token', rotatedRefreshToken)
    }

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

  const completeLogin = (authPayload) => {
    const receivedToken = authPayload.access
    const receivedRefreshToken = authPayload.refresh

    if (!receivedToken || !receivedRefreshToken) {
      throw new Error('Missing authentication token(s) from server.')
    }

    setTokens({
      accessToken: receivedToken,
      refreshTokenValue: receivedRefreshToken
    })

    const normalizedRole = normalizeRole(authPayload.role)
    const tutorRenewalStatus =
      authPayload.tutor_renewal_status ||
      authPayload.renewal_status ||
      authPayload.document_renewal_status ||
      null
    const tutorRenewalRequired = Boolean(
      authPayload.tutor_renewal_required ||
      authPayload.renewal_required ||
      authPayload.document_renewal_required ||
      authPayload.needs_document_renewal
    )

    user.value = {
      email: authPayload.email,
      role: normalizedRole,
      id: Number(authPayload.user_id),
      profile_id: Number(authPayload.profile_id),
      fname: authPayload.fname,
      lname: authPayload.lname,
      application_status: authPayload.application_status || null,
      tutor_renewal_status: tutorRenewalStatus,
      tutor_renewal_required: tutorRenewalRequired,
      profile_picture_url: null
    }

    localStorage.setItem('user_role', normalizedRole)
    localStorage.setItem('user_id', authPayload.user_id)
    localStorage.setItem('profile_id', authPayload.profile_id)
    localStorage.setItem('user_fname', authPayload.fname || '')
    localStorage.setItem('user_lname', authPayload.lname || '')
    if (authPayload.application_status) {
      localStorage.setItem('application_status', authPayload.application_status)
    } else {
      localStorage.removeItem('application_status')
    }
    if (tutorRenewalStatus) {
      localStorage.setItem('tutor_renewal_status', tutorRenewalStatus)
    } else {
      localStorage.removeItem('tutor_renewal_status')
    }
    if (tutorRenewalRequired) {
      localStorage.setItem('tutor_renewal_required', 'true')
    } else {
      localStorage.removeItem('tutor_renewal_required')
    }
    profileStore.resetProfileState()

    startSessionTracking()

    return authPayload.role
  }

  const login = async (credentialsOrPayload, options = {}) => {
    const responseData = options.completed
      ? credentialsOrPayload
      : (await api.post('login/', credentialsOrPayload)).data

    if (!options.completed && responseData.requires_2fa) {
      if (!responseData.challenge_id) {
        throw new Error('Missing email verification challenge from server.')
      }

      return {
        requires_2fa: true,
        challenge_id: responseData.challenge_id,
        debug_code: responseData.debug_code || null
      }
    }

    return completeLogin(responseData)
  }

  const logout = () => {
    // Best-effort server-side revocation: blacklist the refresh token.
    // Uses raw axios (not the api instance) to avoid the 401 interceptor recursing.
    const currentAccess = token.value || localStorage.getItem('access_token')
    const currentRefresh = refreshToken.value || localStorage.getItem('refresh_token')

    if (currentAccess && currentRefresh) {
      const ngrokHeaders = API_BASE_URL.includes('ngrok')
        ? { 'ngrok-skip-browser-warning': 'true' }
        : {}

      axios
        .post(
          `${API_BASE_URL}logout/`,
          { refresh: currentRefresh },
          { headers: { Authorization: `Bearer ${currentAccess}`, ...ngrokHeaders } }
        )
        .catch(() => {})
    }

    stopIdleSessionTracking()
    stopAccessTokenRefresh()
    clearStudyBuddySessionCache()

    token.value = null
    refreshToken.value = null
    user.value = null
    profileStore.resetProfileState()

    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user_role')
    localStorage.removeItem('user_id')
    localStorage.removeItem('profile_id')
    localStorage.removeItem('user_fname')
    localStorage.removeItem('user_lname')
    localStorage.removeItem('application_status')
    localStorage.removeItem('tutor_renewal_status')
    localStorage.removeItem('tutor_renewal_required')
    findTutorsStore.reset()

    // Clear any persisted Pinia stores in sessionStorage to prevent data leaks across sessions
    sessionStorage.clear()
  }

  // Merge updated display fields into the current user so the app shell
  // (greetings, avatar) reflects profile edits immediately, without a re-login.
  const patchUserProfile = (partial = {}) => {
    if (!user.value) {
      return
    }

    const allowedFields = ['fname', 'lname', 'profile_picture_url']
    const updates = {}

    allowedFields.forEach((field) => {
      if (field in partial) {
        updates[field] = partial[field]
      }
    })

    user.value = { ...user.value, ...updates }

    if ('fname' in updates) {
      localStorage.setItem('user_fname', updates.fname || '')
    }
    if ('lname' in updates) {
      localStorage.setItem('user_lname', updates.lname || '')
    }
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
      const storedUserId = localStorage.getItem('user_id')
      const storedProfileId = localStorage.getItem('profile_id')
      const storedFname = localStorage.getItem('user_fname')
      const storedLname = localStorage.getItem('user_lname')
      const storedApplicationStatus = localStorage.getItem('application_status')
      const storedTutorRenewalStatus = localStorage.getItem('tutor_renewal_status')
      const storedTutorRenewalRequired =
        localStorage.getItem('tutor_renewal_required') === 'true'
      user.value = {
        role: normalizeRole(storedRole),
        id: storedUserId ? parseInt(storedUserId) : undefined,
        profile_id: storedProfileId ? parseInt(storedProfileId) : undefined,
        fname: storedFname || '',
        lname: storedLname || '',
        application_status: storedApplicationStatus || null,
        tutor_renewal_status: storedTutorRenewalStatus || null,
        tutor_renewal_required: storedTutorRenewalRequired
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
    completeLogin,
    login,
    logout,
    patchUserProfile,
    initializeAuth
  }
})
