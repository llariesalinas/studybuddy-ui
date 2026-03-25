import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api/api'

export const useAuthStore = defineStore('auth', () => {

  // --- STATE ---
  const token = ref(localStorage.getItem('access_token') || null)
  const user = ref(null)  

  // --- GETTERS ---
  const isAuthenticated = computed(() => !!token.value)
  const userRole = computed(() => user.value?.role || null)

  // --- LOGIN ---
  const login = async (credentials) => {

    const response = await api.post('login/', credentials)

    const receivedToken = response.data.access

    if (!receivedToken) {
      throw new Error("No token received from server.")
    }

    // ✅ Save token in Pinia
    token.value = receivedToken

    // ✅ Save token in localStorage (IMPORTANT)
    localStorage.setItem('access_token', receivedToken)

    // ✅ Store user info
    user.value = {
      email: response.data.email,
      role: response.data.role,
      id: response.data.user_id,
      fname: response.data.fname,
      lname: response.data.lname
    }

    // Save role for refresh recovery
    localStorage.setItem('user_role', response.data.role)

    return response.data.role
  }

  // --- LOGOUT ---
  const logout = () => {

    token.value = null
    user.value = null

    localStorage.removeItem('access_token')
    localStorage.removeItem('user_role')
  }

  // --- INITIALIZE AUTH (for refresh) ---
  const initializeAuth = () => {

    const storedToken = localStorage.getItem('access_token')
    const storedRole = localStorage.getItem('user_role')

    if (storedToken) {
      token.value = storedToken
    }

    if (storedRole) {
      user.value = {
        role: storedRole
      }
    }
  }

  return {
    token,
    user,
    userRole,
    isAuthenticated,
    login,
    logout,
    initializeAuth
  }
})