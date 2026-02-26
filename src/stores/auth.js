import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api/api' // Custom Axios instance

export const useAuthStore = defineStore('auth', () => {

  // --- STATE ---
  const token = ref(localStorage.getItem('access_token') || null)
  const user = ref(null)

  // --- GETTERS ---
  const isAuthenticated = computed(() => !!token.value)

  // --- ACTIONS ---

  // 1. The Login Function
  const login = async (credentials) => {
    const response = await api.post('login/', credentials)

    const receivedToken = response.data.access

    if (!receivedToken) {
      throw new Error("No token received from server.")
    }

    token.value = receivedToken
    localStorage.setItem('access_token', receivedToken)

    // ✅ Store user info properly
    user.value = {
      email: response.data.email,
      role: response.data.role,
      id: response.data.user_id,
      fname: response.data.fname,
      lname: response.data.lname
    }

    return response.data.role
  }

  // 2. The Logout Function
  const logout = () => {
    token.value = null
    user.value = null
    
    localStorage.removeItem('access_token')
    localStorage.removeItem('user_role')
  }

  // 3. Initialize Auth (Optional for refresh handling)
  const initializeAuth = () => {
    const storedRole = localStorage.getItem('user_role')

    if (token.value && storedRole) {
      user.value = {
        role: storedRole
      }
    }
  }

  return {
    token,
    user,
    isAuthenticated,
    login,
    logout,
    initializeAuth
  }
})