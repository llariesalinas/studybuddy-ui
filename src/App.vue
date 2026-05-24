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
        <li v-if="userRole!== 'admin'" class="nav-item mb-2">
          <router-link :to="userRole === 'tutor' ? '/tch-dashboard' : '/dashboard'" class="nav-link text-white opacity-75 d-flex align-items-center" active-class="active-nav">
            <i class="bi bi-grid-1x2 me-3"></i> Dashboard
          </router-link>
        </li>

        <li v-if="userRole!== 'admin'" class="nav-item mb-2">
          <router-link :to="userRole === 'tutor' ? '/tutor-profile' : '/tutee-profile'" class="nav-link text-white opacity-75 d-flex align-items-center">
            <i class="bi bi-person me-3"></i> Profile
          </router-link>
        </li>

        <li class="nav-item mb-2" v-if="userRole === 'tutee'">
          <router-link to="/tuteeSessions" class="nav-link text-white opacity-75 d-flex align-items-center" active-class="active-nav">
            <i class="bi bi-search me-3"></i> Sessions
          </router-link>
        </li>

        <li class="nav-item mb-2" v-if="userRole === 'tutor'">
          <router-link
            to="/tch-availability"
            class="nav-link text-white opacity-75 d-flex align-items-center"
            active-class="active-nav"
          >
            <i class="bi bi-calendar3 me-3"></i> Schedule
          </router-link>
        </li>

        <li class="nav-item mb-2" v-if="userRole === 'tutor'">
          <router-link to="/reports" class="nav-link text-white opacity-75 d-flex align-items-center" active-class="active-nav">
            <i class="bi bi-file-earmark-text me-3"></i> Sessions & Reports
          </router-link>
        </li>

        <li class="nav-item mb-2" v-if="userRole === 'tutor'">
          <router-link to="/tch-wallet" class="nav-link text-white opacity-75 d-flex align-items-center" active-class="active-nav">
            <i class="bi bi-wallet2 me-3"></i> Wallet
          </router-link>
        </li>

        <li class="nav-item mb-2" v-if="userRole === 'admin'">
          <router-link to="/admin/dashboard" class="nav-link text-white opacity-75 d-flex align-items-center" active-class="active-nav">
            <i class="bi bi-grid-1x2 me-3"></i> Dashboard
          </router-link>
        </li>

        <li class="nav-item mb-2" v-if="userRole === 'admin'">
          <router-link to="/admin/withdrawals" class="nav-link text-white opacity-75 d-flex align-items-center" active-class="active-nav">
            <i class="bi bi-wallet2 me-3"></i> Withdrawals
          </router-link>
        </li>

        <li class="nav-item mb-2" v-if="userRole === 'admin'">
          <router-link to="/admin/users" class="nav-link text-white opacity-75 d-flex align-items-center" active-class="active-nav">
            <i class="bi bi-people me-3"></i> Users
          </router-link>
        </li>

        <li class="nav-item mb-2" v-if="userRole === 'admin'">
          <router-link to="/admin/institutions" class="nav-link text-white opacity-75 d-flex align-items-center" active-class="active-nav">
            <i class="bi bi-building me-3"></i> Institutions
          </router-link>
        </li>

        <li class="nav-item mb-2" v-if="userRole === 'admin'">
          <router-link to="/admin/reports" class="nav-link text-white opacity-75 d-flex align-items-center" active-class="active-nav">
            <i class="bi bi-bar-chart-line me-3"></i> Reports
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
      </ul>
    </aside>

    <div ref="logoutModalRef" class="modal fade" id="logoutModal" tabindex="-1">
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

    <main
      class="app-main flex-grow-1 overflow-auto p-5 position-relative"
      :class="{ 'app-main-chat': route.name === 'chat' }"
      style="background-color: var(--sb-bg);"
    >
        <header class="app-page-header d-flex justify-content-between align-items-center mb-3 pb-3 border-bottom border-sb">
          
          <div v-if="route.path === '/dashboard'">
            <h2 class="fw-bold text-dark">Welcome back, {{ userFname }}!</h2>
            <p class="text-muted">Here's your tutoring overview for today.</p>
          </div>

          <div v-if="route.path === '/tutee-profile'">
            <h2 class="fw-bold text-dark">My Profile</h2>
            <p class="text-muted">Manage your personal information and tutoring preferences.</p>
          </div>

          <div v-if="route.path === '/book'">
            <h2 class="fw-bold text-dark">Book a Session</h2>
            <p class="text-muted">
              Tell us what you need help with, and we'll match you with the right tutor.
            </p>
          </div>

          <div v-if="route.path === '/find-tutors'">
            <h2 class="fw-bold text-dark">Find Tutors</h2>
            <p class="text-muted">Browse peer tutors matched to your learning needs.</p>
        </div>

          <div v-if="route.path === '/tuteeSessions'">
            <h2 class="fw-bold text-dark">Here are your sessions, {{ userFname}}!</h2>
            <p class="text-muted">Browse and review pending, upcoming, and completed sessions and confirm ongoing sessions here.</p>
          </div>

          <div v-if="route.path.startsWith('/tuteeSessionDetails/')">
            <h2 class="fw-bold text-dark">Session Details</h2>
            <p class="text-muted">Review your session here.</p>
          </div>

          <div v-if="route.path === '/tch-dashboard'">
            <h2 class="fw-bold text-dark">Welcome back, {{ userFname }}!</h2>
            <p class="text-muted">Here's your tutoring overview for today.</p>
          </div>

          <div v-if="route.path === '/tutor-profile'">
            <h2 class="fw-bold text-dark">My Profile</h2>
            <p class="text-muted">Manage your personal information and tutoring preferences.</p>
          </div>

          <div v-if="route.path === '/tch-wallet'">
            <h2 class="fw-bold text-dark">My Wallet</h2>
            <p class="text-muted">Manage your earnings and withdrawal requests.</p>
          </div>

          <div v-if="route.path === '/reports'">
            <h2 class="fw-bold text-dark">Sessions & Reports</h2>
            <p class="text-muted">Track your tutoring history, earnings, and performance.</p>
          </div>

          <div v-if="route.path === '/tch-availability'">
            <h2 class="fw-bold text-dark">Your Schedule</h2>
            <p class="text-muted">Set recurring weekly slots and add one-off date blocks when your schedule changes.</p>
          </div>

          <div v-if="route.path === '/admin/dashboard'">
            <h2 class="fw-bold text-dark">Admin Dashboard</h2>
            <p class="text-muted">Platform overview and key performance metrics.</p>
          </div>

          <div v-if="route.path === '/admin/users'">
            <h2 class="fw-bold text-dark">Users</h2>
            <p class="text-muted">Search, filter, and manage all platform users.</p>
          </div>

          <div v-if="route.path === '/admin/withdrawals'">
            <h2 class="fw-bold text-dark">Withdrawals</h2>
            <p class="text-muted">Search, filter, and manage all user withdrawals.</p>
          </div>

          <div v-if="route.path === '/admin/institutions'">
            <h2 class="fw-bold text-dark">Institutions</h2>
            <p class="text-muted">View and manage requests from partnered institutions.</p>
          </div>

          <div v-if="route.path === '/admin/reports'">
            <h2 class="fw-bold text-dark">Reports</h2>
            <p class="text-muted">View and review platform analytics.</p>
          </div>

          <div v-if="route.path === '/tch-requestedSessions'">
            <div class="d-flex align-items-center gap-2 flex-wrap">
              <h2 class="fw-bold mb-1">Requested Sessions</h2>
              <span v-if="sessionStore.hasNewPendingRequests" class="request-alert-dot" aria-label="New requests available"></span>
            </div>
            <p class="text-muted mb-0">
                Manage pending session requests.
            </p>
          </div>

          <div class="d-flex gap-3 align-items-center ms-auto">
            <router-link v-if="userRole === 'tutee' && route.path !== '/book'" to="/book" class="btn bg-sb-primary text-white px-4 py-2 rounded-3 fw-semibold shadow-sm">
              Book Session
            </router-link>

            <router-link
              v-if="userRole === 'tutor' && route.path !== '/tch-requestedSessions'"
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

            <div v-if="authStore.isAuthenticated && !isPublicRoute" class="d-flex align-items-center gap-2 ms-auto">
              <router-link to="/chat" class="chat-icon-btn" aria-label="Open chat">
                <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                </svg>
                <span
                  v-if="chatStore.totalUnread"
                  class="chat-unread-count"
                  :aria-label="`${chatStore.totalUnread} unread chat message${chatStore.totalUnread === 1 ? '' : 's'}`"
                >
                  {{ chatStore.totalUnread > 9 ? '9+' : chatStore.totalUnread }}
                </span>
              </router-link>
              <router-link
                v-if="chatStore.recentPopup && route.name !== 'chat'"
                :to="{ name: 'chat', query: { room: chatStore.recentPopup.roomId } }"
                class="chat-toast"
              >
                <strong>{{ chatStore.recentPopup.partnerName }}</strong>
                <span>{{ chatStore.recentPopup.content }}</span>
              </router-link>
              <NotificationBell />
            </div>
          </div>
        </header>
      <RatingReminderBanner v-if="authStore.isAuthenticated && !isPublicRoute && userRole === 'tutee'" />
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth' // Import auth store
import { useSessionsStore } from '@/stores/completedSessions'
import NotificationBell from '@/components/NotificationBell.vue'
import RatingReminderBanner from '@/components/RatingReminderBanner.vue'
import { useNotificationsStore } from '@/stores/notifications'
import { useChatStore } from '@/stores/chat'
import router from './router'
import * as bootstrap from 'bootstrap'
import { SESSION_POLL_INTERVAL_MS } from './config.js'

const route = useRoute()
const authStore = useAuthStore()
const notificationsStore = useNotificationsStore()
const chatStore = useChatStore()
const sessionStore = useSessionsStore()
const logoutModalRef = ref(null)
let pendingSessionsRefreshId = null

const closeLogoutModal = () => {
  const modalElement = logoutModalRef.value

  if (!modalElement) {
    return
  }

  const modalInstance = bootstrap.Modal.getInstance(modalElement)
  modalInstance?.hide()

  document.body.classList.remove('modal-open')
  document.body.style.removeProperty('overflow')
  document.body.style.removeProperty('padding-right')
  document.querySelectorAll('.modal-backdrop').forEach(backdrop => backdrop.remove())
}

const logout = async () => {
  closeLogoutModal()
  chatStore.disconnectAll()
  authStore.logout()
  await router.push('/login')
}

const isPublicRoute = computed(() => {
  return ['home', 'login', 'register', 'preferencesetup', 'tutorpreferencesetup'].includes(route.name)
})

// Get the role from the store to control the sidebar links
const userRole = computed(() => authStore.user?.role?.toLowerCase() || null)
const userFname =  computed(() => authStore.user?.fname || null)

const refreshTutorPendingSessions = async () => {
  if (!authStore.isAuthenticated || userRole.value !== 'tutor') {
    return
  }

  await sessionStore.fetchSessions()
}

const handleVisibilityChange = async () => {
  if (!document.hidden) {
    await refreshTutorPendingSessions()
  }
}
onMounted(() => {
  if (authStore.isAuthenticated) {
    notificationsStore.fetchNotifications()
    chatStore.fetchRooms()
    chatStore.connectUpdates()
    if (userRole.value === 'tutor') {
      sessionStore.fetchSessions()
      document.addEventListener('visibilitychange', handleVisibilityChange)
      pendingSessionsRefreshId = window.setInterval(() => {
        refreshTutorPendingSessions()
      }, SESSION_POLL_INTERVAL_MS)
    }
  }
})

onBeforeUnmount(() => {
  closeLogoutModal()
  document.removeEventListener('visibilitychange', handleVisibilityChange)

  if (pendingSessionsRefreshId) {
    window.clearInterval(pendingSessionsRefreshId)
  }

  chatStore.disconnectAll()
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
  --sb-topbar-height: 60px;
  --sb-bell-size: 52px;
  --sb-bell-gap: 1.5rem;
  --sb-main-padding: 3rem;
  --sb-spring: cubic-bezier(0.16, 1, 0.3, 1);
  --sb-spring-fast: cubic-bezier(0.34, 1.56, 0.64, 1);
  --sb-t-quick: 120ms;
  --sb-t-normal: 250ms;
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
  background: var(--sb-danger);
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

.app-main {
  min-width: 0;
}

.app-main-chat {
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.app-page-header {
  min-height: var(--sb-topbar-height);
}

.chat-icon-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: var(--sb-bell-size);
  height: var(--sb-bell-size);
  border-radius: 50%;
  border: 1.5px solid #dee2e6;
  background: #fff;
  color: var(--sb-text-secondary);
  text-decoration: none;
  transition: background 0.15s, color 0.15s, border-color 0.15s;
  position: relative;
}
.chat-icon-btn:hover,
.chat-icon-btn.router-link-active {
  background: var(--sb-primary);
  color: #fff;
  border-color: var(--sb-primary);
}

.chat-unread-count {
  position: absolute;
  top: -4px;
  right: -4px;
  min-width: 20px;
  height: 20px;
  padding: 0 5px;
  border-radius: 999px;
  background: var(--sb-danger-bs);
  color: #ffffff;
  border: 2px solid #ffffff;
  font-size: 11px;
  font-weight: 800;
  line-height: 16px;
  text-align: center;
}

.chat-toast {
  position: absolute;
  top: calc(var(--sb-topbar-height) + 12px);
  right: calc(var(--sb-bell-size) + var(--sb-bell-gap) + 70px);
  z-index: 20;
  width: min(320px, calc(100vw - 48px));
  background: #ffffff;
  border: 1px solid var(--sb-card-border);
  border-radius: 8px;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.12);
  padding: 12px 14px;
  color: var(--sb-text-main);
  text-decoration: none;
}

.chat-toast strong,
.chat-toast span {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.chat-toast strong {
  font-size: 13px;
}

.chat-toast span {
  margin-top: 3px;
  color: var(--sb-text-secondary);
  font-size: 12px;
}

/* --- Button Haptics Utility --- */
.sb-btn {
  transition: transform var(--sb-t-quick) var(--sb-spring-fast),
              box-shadow var(--sb-t-quick) var(--sb-spring-fast),
              background-color var(--sb-t-quick) var(--sb-spring-fast);
  cursor: pointer;
}
.sb-btn:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.18);
}
.sb-btn:active:not(:disabled) {
  transform: scale(0.96) translateY(0);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
  transition-duration: 60ms;
}
.sb-btn:disabled,
.sb-btn[disabled] {
  opacity: 0.4;
  pointer-events: none;
}

/* --- Interactive Card/Item Haptics Utility --- */
.sb-interactive {
  transition: transform var(--sb-t-normal) var(--sb-spring),
              box-shadow var(--sb-t-normal) var(--sb-spring),
              border-color var(--sb-t-normal) var(--sb-spring),
              background-color var(--sb-t-normal) var(--sb-spring);
  cursor: pointer;
  border-bottom: 2px solid transparent;
}
.sb-interactive:hover {
  transform: translateY(-6px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.14);
  background-color: rgba(255, 255, 255, 0.08);
  border-bottom-color: var(--sb-primary);
}
.sb-interactive:active {
  transform: scale(0.98) translateY(0);
  transition-duration: 60ms;
}

/* --- Animation Keyframes --- */
@keyframes sb-bubble-in {
  from {
    opacity: 0;
    transform: translateY(12px) scale(0.94);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes sb-pulse-dot {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(0, 137, 90, 0.6);
  }
  50% {
    box-shadow: 0 0 0 8px rgba(0, 137, 90, 0);
  }
}

@keyframes sb-pop {
  0% {
    transform: scale(0.6);
    opacity: 0;
  }
  60% {
    transform: scale(1.3);
    opacity: 1;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

@keyframes sb-shake {
  0%   { transform: translateX(0); }
  15%  { transform: translateX(-5px); }
  30%  { transform: translateX(4px); }
  45%  { transform: translateX(-3px); }
  60%  { transform: translateX(2px); }
  75%  { transform: translateX(-1px); }
  100% { transform: translateX(0); }
}
</style>
