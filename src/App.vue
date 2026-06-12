<template>
  <div v-if="isPublicRoute" class="public-layout">
    <router-view v-slot="{ Component }">
      <Transition name="page" mode="out-in">
        <component :is="Component" :key="route.name" />
      </Transition>
    </router-view>
  </div>

  <div v-else class="d-flex vh-100 overflow-hidden">
    <aside class="sidebar d-flex flex-column text-white p-3 shadow-sm" style="width: 250px; background-color: var(--sb-dark);">
      <div class="d-flex align-items-center mb-5 mt-3 px-2">
        <i class="bi bi-book text-sb-primary fs-4 me-2"></i>
        <h4 class="mb-0 fw-bold">StudyBuddy</h4>
      </div>

      <ul class="nav nav-pills flex-column mb-auto">
        <li v-if="userRole!== 'admin' && userRole !==  'superadmin'" class="nav-item mb-2">
          <router-link :to="userRole === 'tutor' ? '/tch-dashboard' : '/dashboard'" class="nav-link text-white opacity-75 d-flex align-items-center" active-class="active-nav">
            <i class="bi bi-grid-1x2 me-3"></i> Dashboard
          </router-link>
        </li>

        <li v-if="userRole!== 'admin' && userRole !==  'superadmin'" class="nav-item mb-2">
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
          <router-link to="/admin/reports" class="nav-link text-white opacity-75 d-flex align-items-center" active-class="active-nav">
            <i class="bi bi-bar-chart-line me-3"></i> Reports
          </router-link>
        </li>

        <li class="nav-item mb-2" v-if="userRole === 'admin'">
          <router-link to="/admin/support" class="nav-link text-white opacity-75 d-flex align-items-center" active-class="active-nav">
            <i class="bi bi-headset me-3"></i> Support Desk
          </router-link>
        </li>

        <li class="nav-item mb-2" v-if="userRole === 'superadmin'">
          <router-link to="/superadmin/dashboard" class="nav-link text-white opacity-75 d-flex align-items-center" active-class="active-nav">
            <i class="bi bi-grid-1x2 me-3"></i> Dashboard
          </router-link>
        </li>

        <li class="nav-item mb-2" v-if="userRole === 'superadmin'">
          <router-link to="/superadmin/institutions" class="nav-link text-white opacity-75 d-flex align-items-center" active-class="active-nav">
            <i class="bi bi-building me-3"></i> Institutions
          </router-link>
        </li>

        <li class="nav-item mb-2" v-if="userRole === 'superadmin'">
          <router-link to="/superadmin/users" class="nav-link text-white opacity-75 d-flex align-items-center" active-class="active-nav">
            <i class="bi bi-people me-3"></i> All Users
          </router-link>
        </li>

        <li class="nav-item mb-2" v-if="userRole === 'superadmin'">
          <router-link to="/superadmin/reports" class="nav-link text-white opacity-75 d-flex align-items-center" active-class="active-nav">
            <i class="bi bi-bar-chart-line me-3"></i> Reports
          </router-link>
        </li>

        <li class="nav-item mb-2">
          <button
           class="nav-link border-0 shadow-none bg-transparent text-white opacity-75 d-flex align-items-center sb-btn"
           @click="openLogoutModal"
           >
            <i class="bi bi-box-arrow-right me-3"></i> Log-out
          </button>
        </li>
      </ul>

      <!-- Footer utility items: Help and Theme toggle -->
      <div class="mt-auto pt-3 border-top border-secondary border-opacity-25 d-flex align-items-center justify-content-between px-2">
        <button
          class="btn p-0 text-white opacity-75 d-flex align-items-center sb-btn"
          @click="openSupport('Other')"
        >
          <i class="bi bi-question-circle me-2"></i> Help
        </button>
        <SbThemeToggle />
      </div>
    </aside>

    <SupportModal
      :open="isSupportModalOpen"
      :type="supportContextType"
      :context-id="supportContextId"
      @close="isSupportModalOpen = false"
    />

    <div
      v-if="showLogoutModal"
      ref="logoutModalRef"
      class="modal logout-modal show"
      id="logoutModal"
      tabindex="-1"
      role="dialog"
      aria-modal="true"
      style="display: block;"
      @click.self="closeLogoutModal"
    >
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content rounded-4">
          
          <div class="modal-header border-0">
            <h5 class="modal-title fw-bold">Confirm Logout</h5>
            <button type="button" class="btn-close" @click="closeLogoutModal"></button>
          </div>

          <div class="modal-body sb-muted">
            Are you sure you want to log out?
          </div>

          <div class="modal-footer border-0">
            <button
              class="btn btn-light sb-btn"
              @click="closeLogoutModal"
            >
              Cancel
            </button>

            <button
              class="btn bg-sb-primary text-white sb-btn"
              @click="logout"
            >
              Yes, Log out
            </button>
          </div>

        </div>
      </div>
    </div>

    <main
      class="app-main app-main-surface flex-grow-1 overflow-auto p-5 position-relative"
      :class="{ 'app-main-chat': route.name === 'chat' }"
    >
        <header class="app-page-header d-flex justify-content-between align-items-center mb-3 pb-3 border-bottom border-sb">
          
          <div v-if="route.path === '/dashboard'">
            <h2 class="fw-bold sb-text">Welcome back, {{ userFname }}!</h2>
            <p class="sb-muted">Here's your tutoring overview for today.</p>
          </div>

          <div v-if="route.path === '/tutee-profile'">
            <h2 class="fw-bold sb-text">My Profile</h2>
            <p class="sb-muted">Manage your personal information and tutoring preferences.</p>
          </div>

          <div v-if="route.path === '/book'">
            <h2 class="fw-bold sb-text">Book a Session</h2>
            <p class="sb-muted">
              Tell us what you need help with, and we'll match you with the right tutor.
            </p>
          </div>

          <div v-if="route.path === '/find-tutors'">
            <h2 class="fw-bold sb-text">Find Tutors</h2>
            <p class="sb-muted">Browse peer tutors matched to your learning needs.</p>
        </div>

          <div v-if="route.path === '/tuteeSessions'">
            <h2 class="fw-bold sb-text">Here are your sessions, {{ userFname}}!</h2>
            <p class="sb-muted">Browse and review pending, upcoming, and completed sessions and confirm ongoing sessions here.</p>
          </div>

          <div v-if="route.path.startsWith('/tuteeSessionDetails/')">
            <h2 class="fw-bold sb-text">Session Details</h2>
            <p class="sb-muted">Review your session here.</p>
          </div>

          <div v-if="route.path === '/tch-dashboard'">
            <h2 class="fw-bold sb-text">Welcome back, {{ userFname }}!</h2>
            <p class="sb-muted">Here's your tutoring overview for today.</p>
          </div>

          <div v-if="route.path === '/tutor-profile'">
            <h2 class="fw-bold sb-text">My Profile</h2>
            <p class="sb-muted">Manage your personal information and tutoring preferences.</p>
          </div>

          <div v-if="route.path === '/tch-wallet'">
            <h2 class="fw-bold sb-text">My Wallet</h2>
            <p class="sb-muted">Manage your earnings and cash-out requests.</p>
          </div>

          <div v-if="route.path === '/reports'">
            <h2 class="fw-bold sb-text">Sessions & Reports</h2>
            <p class="sb-muted">Track your tutoring history, earnings, and performance.</p>
          </div>

          <div v-if="route.path === '/tch-availability'">
            <h2 class="fw-bold sb-text">Your Schedule</h2>
            <p class="sb-muted">Set recurring weekly slots and add one-off date blocks when your schedule changes.</p>
          </div>

          <div v-if="route.path === '/admin/dashboard'">
            <h2 class="fw-bold sb-text">Admin Dashboard</h2>
            <p class="sb-muted">Platform overview and key performance metrics.</p>
          </div>

          <div v-if="route.path === '/admin/users'">
            <h2 class="fw-bold sb-text">Users</h2>
            <p class="sb-muted">Search, filter, and manage users.</p>
          </div>

          <div v-if="route.path === '/admin/withdrawals'">
            <h2 class="fw-bold sb-text">Cash Outs</h2>
            <p class="sb-muted">Search, filter, and manage user cash-outs.</p>
          </div>

          <div v-if="route.path === '/admin/reports'">
            <h2 class="fw-bold sb-text">Reports</h2>
            <p class="sb-muted">View and review platform analytics.</p>
          </div>

          <div v-if="route.path === '/admin/support'">
            <h2 class="fw-bold sb-text">Support Desk</h2>
            <p class="sb-muted">Claim, manage, and resolve user support tickets in real-time.</p>
          </div>

          <div v-if="route.path === '/superadmin/dashboard'">
            <h2 class="fw-bold sb-text">Dashboard</h2>
            <p class="sb-muted">Global platform overview and cross-institution performance.</p>
          </div>

          <div v-if="route.path === '/superadmin/institutions'">
            <h2 class="fw-bold sb-text">Institutions</h2>
            <p class="sb-muted">Add, activate, and manage all partner institutions.</p>
          </div>

          <div v-if="route.path === '/superadmin/users'">
            <h2 class="fw-bold sb-text">Users</h2>
            <p class="sb-muted">View and manage every user across all partner institutions.</p>
          </div>

          <div v-if="route.path === '/superadmin/reports'">
            <h2 class="fw-bold sb-text">Platform Reports</h2>
            <p class="sb-muted">Cross-institution analytics — filter by institution or view globally.</p>
          </div>

          <div v-if="route.path === '/tch-requestedSessions'">
            <div class="d-flex align-items-center gap-2 flex-wrap">
              <h2 class="fw-bold sb-text mb-1">Requested Sessions</h2>
              <span v-if="sessionStore.hasNewPendingRequests" class="request-alert-dot" aria-label="New requests available"></span>
            </div>
            <p class="sb-muted mb-0">
                Manage pending session requests.
            </p>
          </div>

          <div class="d-flex gap-3 align-items-center ms-auto">
            <router-link v-if="userRole === 'tutee' && route.path !== '/book'" to="/book" class="btn bg-sb-primary text-white px-4 py-2 rounded-3 fw-semibold shadow-sm sb-btn">
              Book Session
            </router-link>

            <router-link
              v-if="userRole === 'tutor' && route.path !== '/tch-requestedSessions'"
              to="/tch-requestedSessions"
              class="btn bg-sb-primary text-white px-4 py-2 rounded-3 fw-semibold shadow-sm pending-request-btn d-inline-flex align-items-center gap-2 sb-btn"
            >
              <span v-if="sessionStore.hasNewPendingRequests" class="pending-request-dot" aria-hidden="true"></span>
              <span>Manage Pending Sessions</span>
              <span
                v-if="sessionStore.requestedSessions.length > 0"
                class="pending-request-count pending-request-count-surface badge rounded-pill text-sb-primary border border-sb"
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
      <router-view v-slot="{ Component }">
        <Transition name="page" mode="out-in">
          <component :is="Component" :key="route.name" />
        </Transition>
      </router-view>
    </main>
  </div>

  <SbToast />
</template>

<script setup>
import { computed, defineAsyncComponent, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth' // Import auth store
import { useSessionsStore } from '@/stores/completedSessions'
import NotificationBell from '@/components/NotificationBell.vue'
import RatingReminderBanner from '@/components/RatingReminderBanner.vue'
import { useChatStore } from '@/stores/chat'
import router from './router'
import { SESSION_POLL_INTERVAL_MS } from './config.js'
import SbToast from '@/components/SbToast.vue'
import SbThemeToggle from '@/components/SbThemeToggle.vue'
const SupportModal = defineAsyncComponent(() => import('@/components/SupportModal.vue'))

const route = useRoute()
const authStore = useAuthStore()
const chatStore = useChatStore()
const sessionStore = useSessionsStore()
const logoutModalRef = ref(null)
const showLogoutModal = ref(false)

const isSupportModalOpen = ref(false)
const supportContextType = ref('Other')
const supportContextId = ref(null)

const openSupport = (type = 'Other', id = null) => {
  supportContextType.value = type
  supportContextId.value = id
  isSupportModalOpen.value = true
}
let pendingSessionsRefreshId = null

const clearBootstrapModalState = () => {
  document.body.classList.remove('modal-open')
  document.body.style.removeProperty('overflow')
  document.body.style.removeProperty('padding-right')
  document.querySelectorAll('.modal-backdrop').forEach(backdrop => backdrop.remove())
}

const openLogoutModal = () => {
  clearBootstrapModalState()
  showLogoutModal.value = true
}

const closeLogoutModal = () => {
  showLogoutModal.value = false
  clearBootstrapModalState()
}

const logout = async () => {
  closeLogoutModal()
  await nextTick()
  chatStore.disconnectAll()
  authStore.logout()
  await router.replace('/login')
  await nextTick()
  closeLogoutModal()
  window.setTimeout(clearBootstrapModalState, 0)
}


const isPublicRoute = computed(() => {
  return [
    'home',
    'login',
    'register',
    'forgot-password',
    'reset-password',
    'password-reset-confirm',
    'preferencesetup',
    'tutorpreferencesetup'
  ].includes(route.name)
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
    deferStartupWork(() => {
      chatStore.fetchRooms()
      chatStore.connectUpdates()
    })

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

.pending-request-count-surface {
  background: var(--sb-card-bg);
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

.app-main-surface {
  background: var(--sb-bg);
}

.app-main-chat {
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.app-page-header {
  min-height: var(--sb-topbar-height);
}

.logout-modal {
  background: transparent;
}

.logout-modal .modal-content {
  border: 1px solid color-mix(in srgb, var(--sb-card-border) 82%, transparent);
  background: color-mix(in srgb, var(--sb-card-bg) 94%, transparent);
  color: var(--sb-text-main);
  box-shadow: 0 28px 80px rgba(0, 0, 0, 0.22);
}

.chat-icon-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: var(--sb-bell-size);
  height: var(--sb-bell-size);
  border-radius: 50%;
  border: 1.5px solid var(--sb-card-border);
  background: var(--sb-card-bg);
  color: var(--sb-text-muted);
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
  border: 2px solid var(--sb-card-bg);
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
  background: var(--sb-card-bg);
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
  color: var(--sb-text-muted);
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

/* --- Page Route Transition --- */
.page-enter-active {
  transition: opacity var(--sb-t-normal) var(--sb-spring),
              transform var(--sb-t-normal) var(--sb-spring);
}
.page-enter-from {
  opacity: 0;
  transform: translateY(8px);
}
.page-leave-active {
  transition: opacity var(--sb-t-quick) ease;
}
.page-leave-to {
  opacity: 0;
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

/* --- Layer A/B/C Keyframes --- */
@keyframes sb-stagger-in {
  from { opacity: 0; transform: translateY(10px); }
  to   { opacity: 1; transform: translateY(0); }
}

@keyframes sb-scale-in {
  from { opacity: 0; transform: scale(0.94); }
  to   { opacity: 1; transform: scale(1); }
}

@keyframes sb-tab-indicator {
  from { transform: scaleX(0); opacity: 0; }
  to   { transform: scaleX(1); opacity: 1; }
}

@keyframes sb-toast-in {
  from { opacity: 0; transform: translateY(-14px) scale(0.95); }
  to   { opacity: 1; transform: translateY(0)   scale(1); }
}

@keyframes sb-success-border {
  0%   { box-shadow: 0 0 0 0 rgba(0, 137, 90, 0.5); }
  60%  { box-shadow: 0 0 0 6px rgba(0, 137, 90, 0); }
  100% { box-shadow: none; }
}

/* --- Layer A: Stagger entrance --- */
.sb-stagger-item {
  animation: sb-stagger-in var(--sb-t-normal) var(--sb-spring) both;
  opacity: 0;
}

/* --- Layer A: Modal scale-in (all Bootstrap modals, no per-modal changes needed) --- */
.modal.show .modal-content {
  animation: sb-scale-in var(--sb-t-normal) var(--sb-spring) both;
}

/* --- Layer B: Skeleton shimmer --- */
.sb-skeleton {
  background: rgba(226, 232, 240, 0.86);
  border-radius: 12px;
}

/* --- Layer C: Success card border pulse --- */
.sb-success-card {
  animation: sb-success-border 600ms var(--sb-spring) both;
}

/* --- Accessibility: kill all motion for users who ask --- */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 1ms !important;
    animation-delay: 0ms !important;
    transition-duration: 1ms !important;
  }
}
</style>
