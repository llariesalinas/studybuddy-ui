import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

export const useAuthStore = defineStore('auth', () => {
  const router = useRouter()

  // State
  const user = ref(null)

  // Getters (Used by router/index.js)
  const isAuthenticated = computed(() => user.value !== null)
  const userRole = computed(() => user.value?.role || null)

  // Actions
  const register = async (userData) => {
    // 1. Mock setting the user in state
    user.value = { email: userData.email, role: userData.role }

    // 2. Redirect to correct Preference Setup based on Role
    if (userData.role === 'tutor') {
      router.push('/tutor-setup')
    } else {
      router.push('/preferencesetup') // Tutee setup
    }
  }

  const login = async (credentials) => {
    // Mocking an API response: Assuming they are a student for this test,
    // but in real life, Django tells you what role they are.
    // Change 'tutee' to 'tutor' here to test the tutor login flow.
    user.value = { email: credentials.email, role: 'tutee' }

    // Redirect to correct Dashboard based on Role
    if (user.value.role === 'tutor') {
      router.push('/tch-dashboard')
    } else {
      router.push('/dashboard')
    }
  }

  const logout = () => {
    user.value = null
    router.push('/login')
  }

  return { user, isAuthenticated, userRole, register, login, logout }
})
