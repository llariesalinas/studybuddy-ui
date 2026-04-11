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

        <li class="nav-item mb-2">
          <router-link :to="userRole === 'tutor' ? '/tutor-profile' : '/tutee-profile'" class="nav-link text-white opacity-75 d-flex align-items-center">
            <i class="bi bi-person me-3"></i> Profile
          </router-link>
        </li>

        <li class="nav-item mb-2" v-if="userRole === 'tutee'">
          <router-link to="/tuteeSessions" class="nav-link text-white opacity-75 d-flex align-items-center" active-class="active-nav">
            <i class="bi bi-search me-3"></i> Sessions
          </router-link>
        </li>

        <li class="nav-item mb-2">
          <router-link
            :to="userRole === 'tutor' ? '/tch-availability' : '/schedule'"
            class="nav-link text-white opacity-75 d-flex align-items-center"
            active-class="active-nav"
          >
            <i class="bi bi-calendar3 me-3"></i> Schedule
          </router-link>
        </li>

        <li class="nav-item mb-2">
          <button 
           class="nav-link border-0 shadow-none bg-transparent text-white opacity-75 d-flex align-items-center"
           data-bs-toggle="modal" 
           data-bs-target="#logoutModal"
           >
            <i class="bi bi-box-arrow-right me-3"></i> Log-out
          </button>
        </li>

        <li class="nav-item mb-2" v-if="userRole === 'tutor'">
          <router-link to="/reports" class="nav-link text-white opacity-75 d-flex align-items-center" active-class="active-nav">
            <i class="bi bi-file-earmark-text me-3"></i> Sessions & Reports
          </router-link>
        </li>
      </ul>
    </aside>

    <div class="modal fade" id="logoutModal" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content rounded-4">
          
          <div class="modal-header border-0">
            <h5 class="modal-title fw-bold">Confirm Logout</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>

          <div class="modal-body text-muted">
            Are you sure you want to log out?
          </div>

          <div class="modal-footer border-0">
            <button 
              class="btn btn-light"
              data-bs-dismiss="modal"
            >
              Cancel
            </button>

            <button 
              class="btn bg-sb-primary text-white"
              @click="logout"
            >
              Yes, Log out
            </button>
          </div>

        </div>
      </div>
    </div>

    <main class="flex-grow-1 overflow-auto p-5" style="background-color: var(--sb-bg);">
        <header class="d-flex justify-content-between align-items-center mb-3 pb-3 border-bottom border-sb">
          
          <div v-if="route.path === '/dashboard'">
            <h2 class="fw-bold text-dark">Welcome back, {{ userFname }}!</h2>
            <p class="text-muted">Here's your tutoring overview for today.</p>
          </div>

          <div v-if="route.path === '/tuteeSessions'">
            <h2 class="fw-bold text-dark">Here are your sessions, {{ userFname}}!</h2>
            <p class="text-muted">Browse and review pending, upcoming, and completed sessions and confirm ongoing sessions here.</p>
          </div>

          <div v-if="route.path.startsWith('/tuteeSessionDetails/')">
            <h2 class="fw-bold text-dark">Session Details</h2>
            <p class="text-muted">Review your session here.</p>
          </div>

          <div class="d-flex gap-3 align-items-center">
            <NotificationBell v-if="authStore.isAuthenticated && !isPublicRoute" />

            <router-link v-if="userRole === 'tutee'" to="/book" class="btn bg-sb-primary text-white px-4 py-2 rounded-3 fw-semibold shadow-sm">
              Book Session
            </router-link>

            <router-link
              v-if="userRole === 'tutor'"
              to="/tch-requestedSessions"
              class="btn bg-sb-primary text-white px-4 py-2 rounded-3 fw-semibold shadow-sm pending-request-btn d-inline-flex align-items-center gap-2"
            >
              <span v-if="sessionStore.hasNewPendingRequests" class="pending-request-dot" aria-hidden="true"></span>
              <span>Manage Pending Sessions</span>
              <span
                v-if="sessionStore.requestedSessions.length > 0"
                class="pending-request-count badge rounded-pill bg-light text-sb-primary border border-sb"
                :aria-label="`${sessionStore.requestedSessions.length} pending session request${sessionStore.requestedSessions.length === 1 ? '' : 's'}`"
              >
                {{ sessionStore.requestedSessions.length }}
              </span>
            </router-link>
          </div>
        </header>
      <RatingReminderBanner v-if="authStore.isAuthenticated && !isPublicRoute && userRole === 'tutee'" />
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth' // Import auth store
import { useSessionsStore } from '@/stores/completedSessions'
import NotificationBell from '@/components/NotificationBell.vue'
import RatingReminderBanner from '@/components/RatingReminderBanner.vue'
import { useNotificationsStore } from '@/stores/notifications'
import router from './router'

const route = useRoute()
const authStore = useAuthStore()
const notificationsStore = useNotificationsStore()
const sessionStore = useSessionsStore()
const logout = () => {

  authStore.logout()
  router.push('/login') // Redirect to login after logout

  router.push
}

const hideSessionButton = computed(() => {
  const hiddenPages = [
    'book',
    'tutors',
    'tutor-details',
    'payment',
    'tch-dashboard',
    'tutorpreferencesetup',
    'tch-availability',
    'tch-availability',
    'tch-payments',
    'tch-requestedSessions',
    'booking-details'
  ]
  return !hiddenPages.includes(route.name)
})

const hideReqSessionsButton = computed(() => {
  const hiddenPages = [
    'book',
    'tutors',
    'tutor-details',
    'paymentTutee',
    'preferencesetup',
    'dashboard',
    'tch-requestedSessions'
  ]
  return !hiddenPages.includes(route.name)
})

const isPublicRoute = computed(() => {
  return ['home', 'login', 'register', 'preferencesetup', 'tutorpreferencesetup'].includes(route.name)
})

// Get the role from the store to control the sidebar links
const userRole = computed(() => authStore.user?.role?.toLowerCase() || null)
const userFname =  computed(() => authStore.user?.fname || null)
onMounted(() => {
  if (authStore.isAuthenticated) {
    notificationsStore.fetchNotifications()
    if (userRole.value === 'tutor') {
      sessionStore.fetchSessions()
    }
  }
})
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

.pending-request-btn {
  position: relative;
  transition: transform 180ms ease, box-shadow 180ms ease, filter 180ms ease;
}

.pending-request-count {
  font-size: 0.75rem;
  line-height: 1;
  min-width: 1.6rem;
  padding: 0.4rem 0.5rem;
}

.pending-request-btn:has(.pending-request-dot) {
  box-shadow: 0 0 0 3px rgba(0, 137, 90, 0.18), 0 10px 20px rgba(0, 137, 90, 0.18);
}

.pending-request-btn:has(.pending-request-dot):hover {
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.12);
}

.pending-request-dot {
  position: absolute;
  top: 7px;
  right: 8px;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #ef4444;
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.18);
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
