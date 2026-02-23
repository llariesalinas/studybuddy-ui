import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

export const useAuthStore = defineStore('auth', () => {
  // --- STATE ---
  // We initialize the token by checking if one already exists in the browser's memory
  const token = ref(localStorage.getItem('access_token') || null)
  const user = ref(null)

  // --- GETTERS ---
  // A clean way to check if someone is logged in anywhere in your app
  const isAuthenticated = computed(() => !!token.value)

  // --- ACTIONS ---

  // 1. The Login Function
  const login = async (credentials) => {
    // API_INTEGRATION_POINT: Update to Ry's actual login endpoint
    const response = await axios.post('http://127.0.0.1:8000/api/login/', credentials)

    // Assuming Django returns an object like { access: "eyJh...", refresh: "..." }
    // Adjust 'response.data.access' based on exactly what Ry's API sends back
    const receivedToken = response.data.access || response.data.token

    if (receivedToken) {
      setToken(receivedToken)
      // Optional: If Django returns user data (name, email), save it here
      if (response.data.user) {
        user.value = response.data.user
      }
    } else {
      throw new Error("No token received from server.")
    }
  }

  // 2. The Logout Function
  const logout = () => {
    token.value = null
    user.value = null
    localStorage.removeItem('access_token')

    // Strip the token off future Axios requests
    delete axios.defaults.headers.common['Authorization']
  }

  // 3. The Utility Function (Internal use)
  const setToken = (newToken) => {
    token.value = newToken
    // Save to browser storage so it survives refresh
    localStorage.setItem('access_token', newToken)

    // Automatically attach this token to the header of EVERY future Axios call
    // Django expects: "Authorization: Bearer <your_token>"
    axios.defaults.headers.common['Authorization'] = `Bearer ${newToken}`
  }

  // 4. Initialize Auth (Run this when the app first loads)
  const initializeAuth = () => {
    if (token.value) {
      // If a token exists in storage upon refresh, immediately attach it to Axios
      axios.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
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
