import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/',
})

/*
  REQUEST INTERCEPTOR
  Automatically attach JWT token
*/
api.interceptors.request.use(
  (config) => {

    const authStore = useAuthStore()

    // Get token safely (Pinia OR localStorage)
    const token = authStore.token?.value || localStorage.getItem('access_token')

    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)


/*
  RESPONSE INTERCEPTOR
  Auto logout if token is invalid/expired
*/
api.interceptors.response.use(
  (response) => response,
  (error) => {

    if (error.response && error.response.status === 401) {

      const authStore = useAuthStore()

      console.warn("🔒 Session expired. Logging out...")

      authStore.logout()

      router.push('/login')
    }

    return Promise.reject(error)
  }
)

export default api