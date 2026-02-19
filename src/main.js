import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

// 1. Import Bootstrap CSS
import 'bootstrap/dist/css/bootstrap.min.css'
// 2. Import Bootstrap Icons
import 'bootstrap-icons/font/bootstrap-icons.css'

const app = createApp(App)

app.use(router)
app.mount('#app')

// 3. Import Bootstrap JS at the end so it loads after the DOM
import 'bootstrap/dist/js/bootstrap.bundle.min.js'