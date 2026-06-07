import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useProfileStore } from '@/stores/profile'

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
      path: '/tch-requestedSessions',
      name: 'tch-requestedSessions',
      component: () => import('@/views/TutorRequestedSessions.vue'),
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
      path: '/admin/institutions',
      name: 'admin-institutions',
      component: () => import('@/views/AdminInstitutions.vue'),
      meta: { requiresAuth: true, role: 'Admin' }
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
router.beforeEach(async (to, from, next) => {
  // Clean up any lingering backdrops or modal styles
  document.querySelectorAll('.offcanvas-backdrop, .modal-backdrop').forEach(el => el.remove())
  document.body.classList.remove('modal-open', 'offcanvas-open')
  document.body.style.removeProperty('overflow')
  document.body.style.removeProperty('padding-right')

  const authStore = useAuthStore()
  const profileStore = useProfileStore()
  const normalizedUserRole = authStore.userRole?.toLowerCase?.() || null
  const normalizedRouteRole = to.meta.role?.toLowerCase?.() || null

  // 1️⃣ Protect routes requiring authentication
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return next('/login')
  }

  if (authStore.isAuthenticated) {

    // Ensure token exists
    if (!authStore.token) {
      return next('/login')
    }

    // 2️⃣ Load profile status
    if (!profileStore.loaded) {
      try {
        await profileStore.checkProfileStatus()
      } catch (error) {

        console.error("Profile check failed:", error)

        authStore.logout()
        return next('/login')
      }
    }

    // 3️⃣ Profile completion guard
    if (!profileStore.profileCompleted) {

      const role = normalizedUserRole

      if (to.path === '/preferencesetup' || to.path === '/tutor-setup') {
        return next()
      }

      if (role === 'tutor') {
        return next('/tutor-setup')
      }

      if (role === 'admin') {
        return next()
      }

      return next('/preferencesetup')
    }

    // 4️⃣ Role protection
    if (normalizedRouteRole && normalizedUserRole !== normalizedRouteRole) {

      if (normalizedUserRole === 'tutor') {
        return next('/tch-dashboard')
      }

      if (normalizedUserRole === 'tutee') {
        return next('/dashboard')
      }

      if (normalizedUserRole === 'admin') {
        return next('/admin/dashboard')
      }

      return next('/')
    }

  }

  next()

})

export default router
