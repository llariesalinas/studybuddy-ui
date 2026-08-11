import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import { useAuthStore } from '@/stores/auth' // 1. Import the store
import { useThemeStore } from '@/stores/theme'
import { useSidebarStore } from '@/stores/sidebar'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'

// 1. Import Bootstrap CSS
import 'bootstrap/dist/css/bootstrap.min.css'
// 2. Import Bootstrap Icons
import 'bootstrap-icons/font/bootstrap-icons.css'
// 3. Import Plus Jakarta Sans (variable font, full weight range) — see ADR-0012
import '@fontsource-variable/plus-jakarta-sans'
import './assets/main.css'

const app = createApp(App)

// Global error boundary: keep one unhandled component error from crashing the app.
app.config.errorHandler = (err, instance, info) => {
  console.error('[vue:error]', info, err)
}

const pinia = createPinia()

pinia.use(piniaPluginPersistedstate)

app.use(pinia)
app.use(router)

// 2. Initialize Auth state to load the token into Axios
const authStore = useAuthStore()
authStore.initializeAuth()

const themeStore = useThemeStore()
themeStore.initTheme()

const sidebarStore = useSidebarStore()
sidebarStore.initSidebar()

app.mount('#app')
