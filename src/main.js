import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import { useAuthStore } from '@/stores/auth' // 1. Import the store
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'

// 1. Import Bootstrap CSS
import 'bootstrap/dist/css/bootstrap.min.css'
// 2. Import Bootstrap Icons
import 'bootstrap-icons/font/bootstrap-icons.css'

const app = createApp(App)
const pinia = createPinia()

pinia.use(piniaPluginPersistedstate)

app.use(pinia)
app.use(router)

// 2. Initialize Auth state to load the token into Axios
const authStore = useAuthStore()
authStore.initializeAuth()

app.mount('#app')

// 3. Import Bootstrap JS at the end so it loads after the DOM
import 'bootstrap/dist/js/bootstrap.bundle.min.js'
