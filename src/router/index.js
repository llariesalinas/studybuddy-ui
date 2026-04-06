import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useProfileStore } from '@/stores/profile'

import Dashboard from '@/views/Dashboard.vue'

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
      component: Dashboard,
      meta: { requiresAuth: true, role: 'Tutee' }
    },
    {
      path: '/tutee-profile',
      name: 'tutee-profile',
      component: () => import('@/views/TuteeProfile.vue'),
      meta: { requiresAuth: true, role: 'Tutee' }
    },
    {
      path: '/tutors',
      name: 'tutors',
      component: () => import('@/views/FindTutors.vue'),
      meta: { requiresAuth: true, role: 'Tutee' }
    },
    {
      path: '/book',
      name: 'book',
      component: () => import('@/views/InitialBooking.vue'),
      meta: { requiresAuth: true, role: 'Tutee' }
    },
    {
      path: '/tutor/:id',
      name: 'tutor-details',
      component: () => import('@/views/TutorDetails.vue'),
      meta: { requiresAuth: true, role: 'Tutee' }
    },
    {
      path: '/payment-tutee/:tutorId',
      name: 'PaymentTutee',
      component: () => import('@/views/PaymentScreenTutee.vue'),
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
      path: '/tch-requestedSessions',
      name: 'tch-requestedSessions',
      component: () => import('@/views/TutorRequestedSessions.vue'),
      meta: { requiresAuth: true, role: 'Tutor' }
    },
    {
      path: '/booking-details/:id',
      name: 'booking-details',
      component: () => import('@/views/BookingDetails.vue'),
      meta: { requiresAuth: true, role: 'Tutor' }
    },

    // ---------- SHARED ROUTES ----------
    {
      path: '/schedule',
      name: 'schedule',
      component: () => import('@/views/Schedule.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/reports',
      name: 'reports',
      component: () => import('@/views/SessionsReports.vue'),
      meta: { requiresAuth: true }
    },


  ]
})

/*
  GLOBAL NAVIGATION GUARD
*/
router.beforeEach(async (to, from, next) => {

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

      return next('/')
    }

  }

  next()

})

export default router
