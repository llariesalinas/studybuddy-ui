import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useProfileStore } from '@/stores/profile'

const GUEST_ONLY_ROUTE_NAMES = ['login', 'register']
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

    if (normalizedUserRole === 'tutor' && !profileStore.tutorOnboardingComplete) {
      const furthestStepIndex = !profileStore.profileCompleted
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

    // 2️⃣b Retroactive commission-terms gate (ADR-0010) — only reachable once onboarding is
    // already complete; a tutor still mid-onboarding accepts inline at the hourly-rate step.
    if (
      normalizedUserRole === 'tutor' &&
      profileStore.tutorOnboardingComplete &&
      !profileStore.commissionTermsAccepted &&
      to.name !== 'tutor-commission-terms'
    ) {
      return { name: 'tutor-commission-terms' }
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
