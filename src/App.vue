<template>
  <SbBgWash v-if="route.name !== 'home'" />

  <div v-if="isPublicRoute" class="public-layout">
    <router-view v-slot="{ Component }">
      <Transition name="page" mode="out-in">
        <component :is="Component" :key="route.name" />
      </Transition>
    </router-view>
  </div>

  <div v-else class="d-flex vh-100 overflow-hidden">
    <AppSidebar @logout="openLogoutModal" @open-support="() => openSupport('Other')" />

    <SupportModal
      :open="isSupportModalOpen"
      :context-type="supportContextType"
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
              class="btn bg-sb-primary text-white sb-btn sb-elevated sb-elevated--brand"
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
        <VerificationBanner @navigate="goToVerificationStatus" />
        <WalletDebtBanner @navigate="goToWallet" />
        <header class="app-page-header d-flex justify-content-between align-items-center mb-3 pb-3 border-bottom border-sb">
          
          <div v-if="route.path === '/dashboard'">
            <div class="app-page-header__title-row">
              <h2 class="fw-bold sb-text">Welcome back, {{ userFname }}!</h2>
              <router-link
                v-if="dashboardVerificationBadge"
                to="/application-status"
                class="dashboard-status-badge"
                :class="dashboardVerificationBadge.tone"
                :title="dashboardVerificationBadge.tooltip"
                :aria-label="`${dashboardVerificationBadge.label}. ${dashboardVerificationBadge.tooltip}. View application status.`"
              >
                <i :class="dashboardVerificationBadge.icon" aria-hidden="true"></i>
                <span>{{ dashboardVerificationBadge.label }}</span>
              </router-link>
            </div>
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
            <div class="app-page-header__title-row">
              <h2 class="fw-bold sb-text">Welcome back, {{ userFname }}!</h2>
              <router-link
                v-if="dashboardVerificationBadge"
                to="/application-status"
                class="dashboard-status-badge"
                :class="dashboardVerificationBadge.tone"
                :title="dashboardVerificationBadge.tooltip"
                :aria-label="`${dashboardVerificationBadge.label}. ${dashboardVerificationBadge.tooltip}. View application status.`"
              >
                <i :class="dashboardVerificationBadge.icon" aria-hidden="true"></i>
                <span>{{ dashboardVerificationBadge.label }}</span>
              </router-link>
            </div>
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

          <div v-if="route.path === '/admin/tutor-applications'">
            <h2 class="fw-bold sb-text">Applications</h2>
            <p class="sb-muted">Review submitted tutor and tutee screening documents.</p>
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

          <div v-if="route.path === '/superadmin/support'">
            <h2 class="fw-bold sb-text">SuperAdmin Support</h2>
            <p class="sb-muted">Claim and resolve escalated support tickets from institution admins.</p>
          </div>

          <div class="d-flex gap-3 align-items-center ms-auto">
            <button
              v-if="userRole === 'tutee' && route.path !== '/book'"
              type="button"
              class="btn bg-sb-primary text-white px-4 py-2 rounded-3 fw-semibold sb-btn sb-elevated sb-elevated--brand"
              @click="handleBookSessionClick"
            >
              Book Session
            </button>


            <div v-if="authStore.isAuthenticated && !isPublicRoute" class="d-flex align-items-center gap-2 ms-auto">
              <router-link to="/chat" class="chat-icon-btn sb-btn" aria-label="Open chat">
                <i class="bi bi-chat-dots fs-5" aria-hidden="true"></i>
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

  <template v-if="authStore.isAuthenticated && !isPublicRoute">
    <OngoingBookingBar />

    <template v-if="userRole === 'tutee'">
      <VenueConfirmModal
        :open="isVenueModalOpen"
        :location="activeSession.preferredLocation"
        :submitting="isSubmittingCheckIn"
        @close="dismissCheckIn('venue')"
        @confirm="handleVenueConfirmation"
      />
      <SessionCheckInModal
        :open="isMidpointModalOpen"
        :submitting="isSubmittingCheckIn"
        @close="dismissCheckIn('midpoint')"
        @confirm="handleMidpointCheckIn"
      />
    </template>
  </template>

  <SbToast />
</template>

<script setup>
import { computed, defineAsyncComponent, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth' // Import auth store
import { useProfileStore } from '@/stores/profile'
import { useSessionsStore } from '@/stores/completedSessions'
import { useActiveSessionStore } from '@/stores/activeSession'
import { useToastStore } from '@/stores/toast'
import { useDensityStore } from '@/stores/density'
import NotificationBell from '@/components/NotificationBell.vue'
import RatingReminderBanner from '@/components/RatingReminderBanner.vue'
import OngoingBookingBar from '@/components/OngoingBookingBar.vue'
import VenueConfirmModal from '@/components/VenueConfirmModal.vue'
import SessionCheckInModal from '@/components/SessionCheckInModal.vue'
import VerificationBanner from '@/components/VerificationBanner.vue'
import WalletDebtBanner from '@/components/WalletDebtBanner.vue'
import { useChatStore } from '@/stores/chat'
import router from './router'
import { SESSION_POLL_INTERVAL_MS } from './config.js'
import SbToast from '@/components/SbToast.vue'
import AppSidebar from '@/components/AppSidebar.vue'
import SbBgWash from '@/components/SbBgWash.vue'
const SupportModal = defineAsyncComponent(() => import('@/components/SupportModal.vue'))
const DEV_LIVE_REFRESH_KEY = 'studybuddy_dev_live_refresh'

const route = useRoute()
const authStore = useAuthStore()
const profileStore = useProfileStore()
const chatStore = useChatStore()
const sessionStore = useSessionsStore()
const activeSession = useActiveSessionStore()
const toastStore = useToastStore()
const densityStore = useDensityStore()
const logoutModalRef = ref(null)
const showLogoutModal = ref(false)

const isVenueModalOpen = ref(false)
const isMidpointModalOpen = ref(false)
const isSubmittingCheckIn = ref(false)

watch(
  () => activeSession.dueCheckIn,
  (due) => {
    isVenueModalOpen.value = due === 'venue'
    isMidpointModalOpen.value = due === 'midpoint'
  },
)

const dismissCheckIn = (event) => {
  if (isSubmittingCheckIn.value) {
    return
  }

  activeSession.dismiss(event)

  if (event === 'venue') {
    isVenueModalOpen.value = false
  } else {
    isMidpointModalOpen.value = false
  }
}

const handleVenueConfirmation = async (response) => {
  if (isSubmittingCheckIn.value) {
    return
  }

  isSubmittingCheckIn.value = true

  try {
    const bookingId = activeSession.activeBooking?.id
    await activeSession.confirmVenue(response)
    isVenueModalOpen.value = false

    if (response === 'no') {
      toastStore.push('Venue response saved. You can report a session issue if you need help.', 'warning')
      openSupport('Booking', bookingId)
    } else {
      toastStore.push('Venue confirmation saved.')
    }
  } catch (error) {
    toastStore.push(error.response?.data?.error || 'Failed to save venue confirmation.', 'error')
  } finally {
    isSubmittingCheckIn.value = false
  }
}

const handleMidpointCheckIn = async (response) => {
  if (isSubmittingCheckIn.value) {
    return
  }

  isSubmittingCheckIn.value = true

  try {
    const bookingId = activeSession.activeBooking?.id
    await activeSession.submitMidpointCheckIn(response)
    isMidpointModalOpen.value = false

    if (response === 'issues') {
      toastStore.push('Check-in saved. Opening support so you can tell us what happened.', 'warning')
      openSupport('Booking', bookingId)
    } else {
      toastStore.push('Thanks, your check-in was saved.')
    }
  } catch (error) {
    toastStore.push(error.response?.data?.error || 'Failed to save session check-in.', 'error')
  } finally {
    isSubmittingCheckIn.value = false
  }
}

const isSupportModalOpen = ref(false)
const supportContextType = ref('Other')
const supportContextId = ref(null)

const openSupport = (type = 'Other', id = null) => {
  supportContextType.value = type
  supportContextId.value = id
  isSupportModalOpen.value = true
}

const goToVerificationStatus = async (destination = '/application-status') => {
  await router.push(destination)
}

const goToWallet = async () => {
  await router.push('/tch-wallet')
}

const handleBookSessionClick = async () => {
  await router.push('/book')
}

const normalizeStatus = (value) => String(value || '').trim().toLowerCase().replace(/\s+/g, '_')

const dashboardVerificationBadge = computed(() => {
  if (!profileStore.loaded || !userRole.value) {
    return null
  }

  if (userRole.value === 'tutee') {
    const applicationStatus = normalizeStatus(profileStore.applicationStatus)
    const renewalStatus = normalizeStatus(profileStore.renewalStatus)
    const isVerified = applicationStatus === 'approved' && renewalStatus === 'verified'

    if (isVerified) {
      return {
        label: 'Verified',
        tone: 'is-verified',
        icon: 'bi bi-patch-check-fill',
        tooltip: 'You are verified',
      }
    }

    if (renewalStatus === 'due') {
      return {
        label: 'Unverified',
        tone: 'is-unverified',
        icon: 'bi bi-shield-exclamation',
        tooltip: 'Renewal required',
      }
    }

    if (renewalStatus === 'pending') {
      return {
        label: 'Unverified',
        tone: 'is-unverified',
        icon: 'bi bi-hourglass-split',
        tooltip: 'Renewal pending',
      }
    }

    if (renewalStatus === 'rejected') {
      return {
        label: 'Unverified',
        tone: 'is-unverified',
        icon: 'bi bi-exclamation-circle',
        tooltip: 'Renewal rejected',
      }
    }

    if (applicationStatus === 'pending') {
      return {
        label: 'Unverified',
        tone: 'is-unverified',
        icon: 'bi bi-hourglass-split',
        tooltip: 'Application pending',
      }
    }

    if (applicationStatus === 'rejected') {
      return {
        label: 'Unverified',
        tone: 'is-unverified',
        icon: 'bi bi-exclamation-circle',
        tooltip: 'Application rejected',
      }
    }

    return {
      label: 'Unverified',
      tone: 'is-unverified',
      icon: 'bi bi-shield',
      tooltip: 'Verification needed',
    }
  }

  if (userRole.value === 'tutor') {
    const applicationStatus = normalizeStatus(profileStore.applicationStatus)
    const renewalStatus = normalizeStatus(profileStore.tutorRenewalStatus)
    const isVerified = applicationStatus === 'approved' && renewalStatus === 'verified'

    if (isVerified) {
      return {
        label: 'Verified',
        tone: 'is-verified',
        icon: 'bi bi-patch-check-fill',
        tooltip: 'You are verified',
      }
    }

    if (renewalStatus === 'due') {
      return {
        label: 'Unverified',
        tone: 'is-unverified',
        icon: 'bi bi-arrow-repeat',
        tooltip: 'Renewal required',
      }
    }

    if (renewalStatus === 'pending') {
      return {
        label: 'Unverified',
        tone: 'is-unverified',
        icon: 'bi bi-hourglass-split',
        tooltip: 'Renewal pending',
      }
    }

    if (renewalStatus === 'rejected') {
      return {
        label: 'Unverified',
        tone: 'is-unverified',
        icon: 'bi bi-exclamation-circle',
        tooltip: 'Renewal rejected',
      }
    }

    if (applicationStatus === 'pending') {
      return {
        label: 'Unverified',
        tone: 'is-unverified',
        icon: 'bi bi-hourglass-split',
        tooltip: 'Application pending',
      }
    }

    if (applicationStatus === 'rejected') {
      return {
        label: 'Unverified',
        tone: 'is-unverified',
        icon: 'bi bi-exclamation-circle',
        tooltip: 'Application rejected',
      }
    }

    return {
      label: 'Unverified',
      tone: 'is-unverified',
      icon: 'bi bi-shield',
      tooltip: 'Verification needed',
    }
  }

  return null
})
let pendingSessionsRefreshId = null
let startupIdleId = null
let startupTimeoutId = null

const deferStartupWork = (callback) => {
  if (typeof window === 'undefined') {
    callback()
    return
  }

  if ('requestIdleCallback' in window) {
    startupIdleId = window.requestIdleCallback(callback, { timeout: 2000 })
    return
  }

  startupTimeoutId = window.setTimeout(callback, 800)
}

const cancelDeferredStartupWork = () => {
  if (startupIdleId && typeof window !== 'undefined' && 'cancelIdleCallback' in window) {
    window.cancelIdleCallback(startupIdleId)
  }

  if (startupTimeoutId) {
    window.clearTimeout(startupTimeoutId)
  }

  startupIdleId = null
  startupTimeoutId = null
}

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
  activeSession.stopPolling()
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
    'tutor-application-submitted',
    'forgot-password',
    'reset-password',
    'password-reset-confirm',
    'preferencesetup',
    'tutorpreferencesetup',
    'tutor-subjects-setup',
    'tutor-verification-setup'
  ].includes(route.name)
})

// Get the role from the store to control the sidebar links
const userRole = computed(() => authStore.user?.role?.toLowerCase() || null)
const userFname =  computed(() => authStore.user?.fname || null)

watch(userRole, (role) => densityStore.syncFromRole(role), { immediate: true })

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

const refreshLiveSessionSurfaces = async () => {
  if (!authStore.isAuthenticated) {
    return
  }

  activeSession.currentTime = new Date()
  await sessionStore.fetchSessions({ force: true })
  await activeSession.refreshActive()
}

const handleDevLiveRefresh = async (event) => {
  if (event.key !== DEV_LIVE_REFRESH_KEY) {
    return
  }

  await refreshLiveSessionSurfaces()
}

onMounted(() => {
  if (authStore.isAuthenticated) {
    deferStartupWork(() => {
      chatStore.fetchRooms()
      chatStore.connectUpdates()
    })

    activeSession.startPolling()
    window.addEventListener('storage', handleDevLiveRefresh)

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
  cancelDeferredStartupWork()
  document.removeEventListener('visibilitychange', handleVisibilityChange)
  window.removeEventListener('storage', handleDevLiveRefresh)

  if (pendingSessionsRefreshId) {
    window.clearInterval(pendingSessionsRefreshId)
  }

  activeSession.stopPolling()
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
  transition: transform var(--sb-t-normal) var(--sb-spring);
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

.app-main {
  min-width: 0;
}

.app-main-surface {
  background: transparent;
}

.app-main-chat {
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.app-page-header {
  min-height: var(--sb-topbar-height);
}

.app-page-header__title-row {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  flex-wrap: wrap;
}

.app-page-header__title-row h2 {
  margin-bottom: 0;
}

.dashboard-status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.45rem 0.8rem;
  border-radius: 999px;
  font-size: 0.85rem;
  font-weight: 700;
  text-decoration: none;
  transition:
    transform var(--sb-t-normal) var(--sb-spring),
    box-shadow var(--sb-t-normal) var(--sb-spring);
}

.dashboard-status-badge:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 20px rgba(15, 23, 42, 0.08);
}

.dashboard-status-badge.is-verified {
  background: #e8f7f1;
  color: #0a7a51;
  border: 1px solid rgba(0, 137, 90, 0.18);
}

.dashboard-status-badge.is-unverified {
  background: #f3f4f6;
  color: #52606d;
  border: 1px solid #dce3e8;
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
  border-radius: 16px;
  border: 1px solid #dbe4dd;
  background: #ffffff;
  color: #153326;
  box-shadow: 0 12px 24px rgba(15, 23, 42, 0.06);
  text-decoration: none;
  transition:
    transform var(--sb-t-normal) var(--sb-spring),
    border-color var(--sb-t-normal) var(--sb-spring),
    box-shadow var(--sb-t-normal) var(--sb-spring),
    background-color var(--sb-t-normal) var(--sb-spring),
    color var(--sb-t-normal) var(--sb-spring);
  position: relative;
}

.chat-icon-btn:hover,
.chat-icon-btn.router-link-active {
  transform: translateY(-1px);
  border-color: #b9cfbf;
  background: #ffffff;
  color: #153326;
  box-shadow: 0 16px 28px rgba(15, 23, 42, 0.09);
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

</style>
