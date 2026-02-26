<template>
  <div v-if="isPublicRoute" class="public-layout">
    <router-view />
  </div>

  <div v-else class="d-flex vh-100 overflow-hidden">
    <aside class="sidebar d-flex flex-column text-white p-3 shadow-sm" style="width: 250px; background-color: var(--sb-dark);">
      <div class="d-flex align-items-center mb-5 mt-3 px-2">
        <i class="bi bi-book text-sb-primary fs-4 me-2"></i>
        <h4 class="mb-0 fw-bold">StudyBuddy</h4>
      </div>

      <ul class="nav nav-pills flex-column mb-auto">
        <li class="nav-item mb-2">
          <router-link :to="userRole === 'tutor' ? '/tch-dashboard' : '/dashboard'" class="nav-link text-white opacity-75 d-flex align-items-center" active-class="active-nav">
            <i class="bi bi-grid-1x2 me-3"></i> Dashboard
          </router-link>
        </li>

        <li class="nav-item mb-2" v-if="userRole === 'tutee'">
          <router-link to="/tutors" class="nav-link text-white opacity-75 d-flex align-items-center" active-class="active-nav">
            <i class="bi bi-search me-3"></i> Find Tutors
          </router-link>
        </li>

        <li class="nav-item mb-2">
          <router-link to="/schedule" class="nav-link text-white opacity-75 d-flex align-items-center" active-class="active-nav">
            <i class="bi bi-calendar3 me-3"></i> Schedule
          </router-link>
        </li>

        <li class="nav-item mb-2" v-if="userRole === 'tutor'">
          <router-link to="/reports" class="nav-link text-white opacity-75 d-flex align-items-center" active-class="active-nav">
            <i class="bi bi-file-earmark-text me-3"></i> Sessions & Reports
          </router-link>
        </li>
      </ul>
    </aside>

    <main class="flex-grow-1 overflow-auto p-5" style="background-color: var(--sb-bg);">
      <header class="d-flex justify-content-between align-items-center mb-5 pb-3 border-bottom border-sb">
          <div>
            </div>
          <div class="d-flex gap-3 align-items-center">
            <router-link to="/book" class="btn bg-sb-primary text-white px-4 py-2 rounded-3 fw-semibold shadow-sm">
              Book Session
            </router-link>
            <div class="profileDropdown">
              <button 
              class="btn text-sb-primary fs-3 ms-2 transition-all hover-lift"
              @click="toggleDropdown"
              >
                <i class="bi bi-person-circle"></i>
              </button>
              <ul v-if="isOpen" class="dropdown-menu show position-absolute end-0 mt-2 me-2">
                <li>
                  <button class="btn btn-success dropdown-item text-center px-4"
                            @click="manageAccount">
                      Manage your account
                    </button>
                </li>
                <li><hr class="dropdown-divider"></li>
                <li><button class="btn btn-success dropdown-item text-danger text-center px-4"
                            @click="logout">
                      Log-out
                    </button>
                </li>
              </ul>
            </div>
          </div>
        </header>
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth' // Import auth store
import router from './router'

const route = useRoute()
const authStore = useAuthStore()
const isOpen = ref(false)

const toggleDropdown = () => {
  isOpen.value = !isOpen.value
}

const manageAccount = () => {
  setTimeout(() => {
    router.push('/profile')
  }, 500)
}

const logout = () => {

  setTimeout(() => {
    router.push('/')
  }, 500)

  router.push
}

const isPublicRoute = computed(() => {
  return ['home', 'login', 'register', 'preferencesetup', 'tutorpreferencesetup'].includes(route.name)
})

// Get the role from the store to control the sidebar links
const userRole = computed(() => authStore.userRole)
</script>

<style>
/* Global styles */
:root {
  --sb-dark: #0A1916;
  --sb-primary: #00895A; /* Your exact Figma Green */
  --sb-primary-hover: #00704A; /* Slightly darker for button hovers */
  --sb-bg: #F8F9FA;
  --sb-card-border: #EAEAEA;
}

body {
  background-color: var(--sb-bg);
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

/* --- Brand Color Utility Classes --- */
.text-sb-primary {
  color: var(--sb-primary) !important;
}

.bg-sb-primary {
  background-color: var(--sb-primary) !important;
}

.border-sb {
  border-color: var(--sb-card-border) !important;
}

/* Button Hover State */
.btn.bg-sb-primary:hover {
  background-color: var(--sb-primary-hover) !important;
  color: #ffffff !important;
}

/* --- Sidebar Navigation Styles --- */
.active-nav {
  background-color: rgba(0, 137, 90, 0.1) !important;
  color: var(--sb-primary) !important;
  font-weight: 600;
  border-radius: 8px;
  opacity: 1 !important;
}
.nav-link:hover {
  opacity: 1 !important;
}
</style>
