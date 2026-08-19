import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useProfileStore } from '@/stores/profile'
import { useToastStore } from '@/stores/toast'
import { MODE_SWITCH_TOAST_MS } from '@/config'

const GUEST_ONLY_ROUTE_NAMES = ['login', 'register']
const MODE_LABELS = { tutor: 'Tutor', tutee: 'Tutee' }
const MODE_HOME = { tutor: '/tch-dashboard', tutee: '/dashboard' }

// The auto-switch happens without the user asking for it, so the toast both explains why the
// sidebar changed and hands the reversal back -- Undo restores the previous mode AND the route
// they came from, so an accidental switch costs nothing.
const announceModeSwitch = (targetRole, previousRole, currentPath) => {
  const toastStore = useToastStore()

  toastStore.push(
    `Switched to ${MODE_LABELS[targetRole]} mode`,
    'success',
    MODE_SWITCH_TOAST_MS,
    {
      label: 'Undo',
      handler: async () => {
        const authStore = useAuthStore()
        const profileStore = useProfileStore()

        try {
          await authStore.switchMode(previousRole)
          await profileStore.checkProfileStatus()

          if (router.currentRoute.value.fullPath !== currentPath) {
            return
          }

          // The motivating case for auto-switch is a notification deep link, which frequently
          // opens a fresh tab with no history to go back to -- landing the user nowhere. Fall
          // back to the restored mode's home so Undo always resolves somewhere valid.
          if (window.history.state?.back) {
            router.back()
          } else {
            await router.push(MODE_HOME[previousRole])
          }
        } catch (error) {
          console.error('Undo mode switch failed:', error)
          toastStore.push('Could not switch back. Try the sidebar switcher.', 'error')
        }
      }
    }
  )
}
const TUTOR_ONBOARDING_STEP_ORDER = [
  'tutorpreferencesetup',
  'tutor-subjects-setup',
  'tutor-verification-setup',
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [

    // ---------- PUBLIC ROUTES ----------
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/LandingPage.vue')
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/Login.vue')
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/Register.vue')
    },
    {
      path: '/tutor-application-submitted',
      name: 'tutor-application-submitted',
      component: () => import('@/views/TutorApplicationSubmitted.vue')
    },
    {
      path: '/forgot-password',
      name: 'forgot-password',
      component: () => import('@/views/ForgotPassword.vue')
    },
    {
      path: '/reset-password/:uid/:token',
      name: 'reset-password',
      component: () => import('@/views/ResetPassword.vue')
    },
    {
      path: '/password-reset/confirm',
      name: 'password-reset-confirm',
      component: () => import('@/views/ResetPassword.vue')
    },

    // ---------- STUDENT ROUTES ----------
    {
      path: '/preferencesetup',
      name: 'preferencesetup',
      component: () => import('@/views/PreferenceSetup.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('@/views/Dashboard.vue'),
      meta: { requiresAuth: true, role: 'Tutee' }
    },
    {
      path: '/tutee-profile',
      name: 'tutee-profile',
      component: () => import('@/views/TuteeProfile.vue'),
      meta: { requiresAuth: true, role: 'Tutee' }
    },
    {
      path: '/tuteeSessions',
      name: 'tuteeSessions',
      component: () => import('@/views/TuteeSessions.vue'),
      meta: { requiresAuth: true, role: 'Tutee'}
    },
    {
      path: '/tuteeSessionDetails/:id',
      name: 'tuteeSessionDetails',
      component: () => import('@/views/TuteeSessionDetailsFlow.vue'),
      meta: { requiresAuth: true, role: 'Tutee'}
    },
    {
      path: '/book',
      name: 'book',
      component: () => import('@/views/InitialBooking.vue'),
      meta: { requiresAuth: true, role: 'Tutee' }
    },
    {
      path: '/find-tutors',
      name: 'tutors',
      component: () => import('@/views/FindTutors.vue'),
      meta: { requiresAuth: true, role: 'Tutee' }
    },
    {
      path: '/tutor/:id',
      name: 'tutor-details',
      component: () => import('@/views/TutorDetails.vue'),
      meta: { requiresAuth: true, role: 'Tutee' }
    },
    {
      path: '/payment-tutee/:bookingId',
      name: 'PaymentTutee',
      component: () => import('@/views/PostSessionPaymentView.vue'),
      props: true,
      meta: { requiresAuth: true, role: 'Tutee' }
    },

    // ---------- TUTOR ROUTES ----------
    {
      path: '/tutor-setup',
      name: 'tutorpreferencesetup',
      component: () => import('@/views/TutorPreferenceSetup.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/tutor-setup/subjects',
      name: 'tutor-subjects-setup',
      component: () => import('@/views/TutorSubjectSetup.vue'),
      meta: { requiresAuth: true, role: 'Tutor' }
    },
    {
      path: '/tutor-setup/verification',
      name: 'tutor-verification-setup',
      component: () => import('@/views/TutorVerificationSetup.vue'),
      meta: { requiresAuth: true, role: 'Tutor' }
    },
    {
      path: '/tutor-commission-terms',
      name: 'tutor-commission-terms',
      component: () => import('@/views/TutorCommissionTermsAcceptance.vue'),
      meta: { requiresAuth: true, role: 'Tutor' }
    },
    {
      path: '/application-status',
      name: 'tutor-application-status',
      component: () => import('@/views/TutorApplicationStatus.vue'),
      meta: { requiresAuth: true, role: ['Tutor', 'Tutee'] }
    },
    {
      path: '/tch-dashboard',
      name: 'tch-dashboard',
      component: () => import('@/views/TutorDashboard.vue'),
      meta: { requiresAuth: true, role: 'Tutor' }
    },
    {
      path: '/tutor-profile',
      name: 'tutor-profile',
      component: () => import('@/views/TutorProfile.vue'),
      meta: { requiresAuth: true, role: 'Tutor' }
    },
    {
      path: '/tch-availability',
      name: 'tch-availability',
      component: () => import('@/views/TutorSchedule.vue'),
      meta: { requiresAuth: true, role: 'Tutor' }
    },
    {
      path: '/tch-payments',
      name: 'tch-payments',
      component: () => import('@/views/TutorPaymentScreen.vue'),
      meta: { requiresAuth: true, role: 'Tutor' }
    },
    {
      path: '/tch-wallet',
      name: 'tch-wallet',
      component: () => import('@/views/TutorWallet.vue'),
      meta: { requiresAuth: true, role: 'Tutor' }
    },
    {
      path: '/booking-details/:id',
      name: 'booking-details',
      component: () => import('@/views/TutorBookingDetailsFlow.vue'),
      meta: { requiresAuth: true, role: 'Tutor' }
    },

    // ---------- ADMIN ROUTES ----------
    {
      path: '/admin/dashboard',
      name: 'admin-dashboard',
      component: () => import('@/views/AdminDashboard.vue'),
      meta: { requiresAuth: true, role: 'Admin' }
    },
    {
      path: '/admin/withdrawals',
      name: 'admin-withdrawals',
      component: () => import('@/views/AdminWithdrawals.vue'),
      meta: { requiresAuth: true, role: 'Admin' }
    },
    {
      path: '/admin/users',
      name: 'admin-users',
      component: () => import('@/views/AdminUsers.vue'),
      meta: { requiresAuth: true, role: 'Admin' }
    },
    {
      path: '/admin/course-catalog',
      name: 'admin-course-catalog',
      component: () => import('@/views/AdminCourseCatalog.vue'),
      meta: { requiresAuth: true, role: ['Admin', 'SuperAdmin'] }
    },
    {
      path: '/admin/tutor-applications',
      name: 'admin-tutor-applications',
      component: () => import('@/views/AdminTutorApplications.vue'),
      meta: { requiresAuth: true, role: ['Admin', 'SuperAdmin'] }
    },
    {
      path: '/superadmin/institutions',
      name: 'superadmin-institutions',
      component: () => import('@/views/AdminInstitutions.vue'),
      meta: { requiresAuth: true, role: 'SuperAdmin' }
    },
    {
      path: '/admin/reports',
      name: 'admin-reports',
      component: () => import('@/views/AdminReports.vue'),
      meta: { requiresAuth: true, role: 'Admin' }
    },
    {
      path: '/admin/support',
      name: 'admin-support',
      component: () => import('@/views/AdminSupport.vue'),
      meta: { requiresAuth: true, role: 'Admin' }
    },


    // ---------- SUPERADMIN ROUTES ----------
    {
      path: '/superadmin/dashboard',
      name: 'superadmin-dashboard',
      component: () => import('@/views/SuperAdminDashboard.vue'),
      meta: { requiresAuth: true, role: 'SuperAdmin' }
    },
    {
      path: '/superadmin/users',
      name: 'superadmin-users',
      component: () => import('@/views/SuperAdminUsers.vue'),
      meta: { requiresAuth: true, role: 'SuperAdmin' }
    },
    {
      path: '/superadmin/reports',
      name: 'superadmin-reports',
      component: () => import('@/views/SuperAdminReports.vue'),
      meta: { requiresAuth: true, role: 'SuperAdmin' }
    },
    // Drill-downs behind the reports dashboard's ranked cards. One component serves both; `dataset`
    // selects the entry in REPORT_DETAIL_DATASETS that describes its columns and copy.
    {
      path: '/superadmin/reports/tutors',
      name: 'superadmin-report-tutors',
      component: () => import('@/views/SuperAdminReportDetail.vue'),
      meta: { requiresAuth: true, role: 'SuperAdmin', dataset: 'tutors' }
    },
    {
      path: '/superadmin/reports/subjects',
      name: 'superadmin-report-subjects',
      component: () => import('@/views/SuperAdminReportDetail.vue'),
      meta: { requiresAuth: true, role: 'SuperAdmin', dataset: 'subjects' }
    },
    {
      path: '/superadmin/support',
      name: 'superadmin-support',
      component: () => import('@/views/AdminSupport.vue'),
      meta: { requiresAuth: true, role: 'SuperAdmin' }
    },
    {
      path: '/superadmin/algorithm-demo',
      name: 'superadmin-algorithm-demo',
      component: () => import('@/views/SuperAdminAlgorithmDemo.vue'),
      meta: { requiresAuth: true, role: 'SuperAdmin' }
    },

    // ---------- SHARED ROUTES ----------
    {
      path: '/reports',
      name: 'reports',
      component: () => import('@/views/TutorSessionsReports.vue'),
      meta: { requiresAuth: true, role: 'Tutor' }
    },
    {
      path: '/chat',
      name: 'chat',
      component: () => import('@/views/Chat.vue'),
      meta: { requiresAuth: true }
    },


  ]
})

/*
  GLOBAL NAVIGATION GUARD
*/
router.beforeEach(async (to) => {
  // Clean up any lingering backdrops or modal styles
  document.querySelectorAll('.offcanvas-backdrop, .modal-backdrop').forEach(el => el.remove())
  document.body.classList.remove('modal-open', 'offcanvas-open')
  document.body.style.removeProperty('overflow')
  document.body.style.removeProperty('padding-right')

  const authStore = useAuthStore()
  const profileStore = useProfileStore()
  const normalizedUserRole = authStore.userRole?.toLowerCase?.() || null
  const normalizedRouteRoles = Array.isArray(to.meta.role)
    ? to.meta.role.map((role) => role.toLowerCase())
    : to.meta.role
      ? [to.meta.role.toLowerCase()]
      : []

  // Self-heal a corrupt/partial session: a token can survive in localStorage without its
  // matching user_role (storage eviction, an extension clearing one key, manual edits).
  // Left unchecked, isAuthenticated reads true with no role to redirect on, and the
  // GUEST_ONLY branch below falls back to '/' — a silent no-op when already on '/' that
  // makes "Log in"/"Get started" look dead. Log out to restore a consistent state and let
  // the checks below run normally against it.
  if (authStore.isAuthenticated && !normalizedUserRole) {
    authStore.logout()
  }

  // 1️⃣ Protect routes requiring authentication
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return '/login'
  }

  // Keep already-authenticated users off guest-only pages (e.g. hitting /login via
  // the browser back button after a push-based post-login redirect).
  if (GUEST_ONLY_ROUTE_NAMES.includes(to.name) && authStore.isAuthenticated && authStore.token) {
    if (normalizedUserRole === 'tutor') return '/tch-dashboard'
    if (normalizedUserRole === 'tutee') return '/dashboard'
    if (normalizedUserRole === 'admin') return '/admin/dashboard'
    if (normalizedUserRole === 'superadmin') return '/superadmin/dashboard'
    return '/'
  }

  if (authStore.isAuthenticated) {

    // Ensure token exists
    if (!authStore.token) {
      return '/login'
    }

    // 2️⃣ Load profile status
    if (!profileStore.loaded) {
      try {
        await profileStore.checkProfileStatus()
      } catch (error) {

        console.error("Profile check failed:", error)

        authStore.logout()
        return '/login'
      }
    }

    // `canTutor` is in the condition because verification now carries over between roles: a tutee
    // who switches to Tutor gets an already-approved TutorApplication, which alone makes
    // tutorOnboardingComplete true. Without the capability check they would land on the tutor
    // dashboard with no hourly rate and no subjects.
    if (
      normalizedUserRole === 'tutor' &&
      (!profileStore.tutorOnboardingComplete || !profileStore.canTutor)
    ) {
      // tutorRateSet rather than profileCompleted: a switching tutee has already completed the
      // shared identity step, so keying step 0 off profileCompleted would skip the rate step.
      const furthestStepIndex = !profileStore.profileCompleted || !profileStore.tutorRateSet
        ? 0
        : !profileStore.tutorSubjectsCompleted
          ? 1
          : 2
      const nextOnboardingRoute = TUTOR_ONBOARDING_STEP_ORDER[furthestStepIndex]

      // Allow navigating back to any step at or behind the furthest one completed
      // (e.g. a "Back" button from Verify to Subjects) without bouncing forward
      // again; only skipping ahead of actual progress gets redirected.
      const targetStepIndex = TUTOR_ONBOARDING_STEP_ORDER.indexOf(to.name)
      const isAllowedOnboardingStep = targetStepIndex !== -1 && targetStepIndex <= furthestStepIndex

      if (!isAllowedOnboardingStep) return { name: nextOnboardingRoute }
    }

    // 2b. Retroactive commission-terms gate (ADR-0010) — only reachable once onboarding is
    // already complete; a tutor still mid-onboarding accepts inline at the hourly-rate step.
    if (
      normalizedUserRole === 'tutor' &&
      profileStore.tutorOnboardingComplete &&
      !profileStore.commissionTermsAccepted &&
      to.name !== 'tutor-commission-terms'
    ) {
      return { name: 'tutor-commission-terms' }
    }

    // 2c. Tutee-mode provisioning gate. `profileCompleted` only covers the shared identity step,
    // so a tutor who switches into Tutee mode passes it while having no Preference row at all.
    // The tutor side of this is already handled by the onboarding gate above.
    if (
      normalizedUserRole === 'tutee' &&
      profileStore.profileCompleted &&
      !profileStore.canTutee &&
      to.path !== '/preferencesetup'
    ) {
      return '/preferencesetup'
    }

    // 3️⃣ Profile completion guard
    if (!profileStore.profileCompleted) {

      const role = normalizedUserRole

      if (
        to.path === '/preferencesetup' ||
        to.path === '/tutor-setup' ||
        to.path === '/application-status'
      ) {
        return true
      }

      if (role === 'tutor') {
        return '/tutor-setup'
      }

      if (role === 'admin' || role === 'superadmin') {
        return true
      }

      return '/preferencesetup'
    }

    // 4️⃣ Role protection
    if (normalizedRouteRoles.length && !normalizedRouteRoles.includes(normalizedUserRole)) {

      // Dual-role auto-switch: `role` is the ACTIVE MODE, not a permission. If the account is
      // already provisioned for the mode this route wants, prompting would ask a question whose
      // answer is always yes -- so switch and continue. Bouncing here is not merely annoying: a
      // tutor browsing in Tutee mode who taps "your session starts in 15 minutes" would be
      // redirected off check-in, miss it, and take a Counted Strike (a flat wallet deduction) for
      // a mode toggle they never made. See docs/plans/2026-08-19-dual-role-mode-switch.md.
      const switchableTarget = normalizedRouteRoles.find(
        (routeRole) =>
          (routeRole === 'tutor' && profileStore.canTutor) ||
          (routeRole === 'tutee' && profileStore.canTutee)
      )

      if (switchableTarget && (normalizedUserRole === 'tutor' || normalizedUserRole === 'tutee')) {
        try {
          await authStore.switchMode(switchableTarget)
          await profileStore.checkProfileStatus()
          announceModeSwitch(switchableTarget, normalizedUserRole, to.fullPath)
          return true
        } catch (error) {
          console.error('Mode switch failed:', error)
          // Fall through to the ordinary redirect rather than stranding the user mid-navigation.
        }
      }

      if (normalizedUserRole === 'tutor') {
        return '/tch-dashboard'
      }

      if (normalizedUserRole === 'tutee') {
        return '/dashboard'
      }

      if (normalizedUserRole === 'admin') {
        return '/admin/dashboard'
      }

      if (normalizedUserRole === 'superadmin') {
        return '/superadmin/dashboard'
      }

      return '/'
    }

  }

  return true

})

export default router
