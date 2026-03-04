import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Dashboard from '@/views/Dashboard.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [

    // --- PUBLIC ROUTES ---
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

    // --- STUDENT ROUTES ---
    {
      path: '/preferencesetup',
      name: 'preferencesetup',
      component: () => import('@/views/PreferenceSetup.vue'),
      meta: { requiresAuth: true, role: 'Tutee' }
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('@/views/TuteeProfile.vue'),
      meta: { requiresAuth: true, role: 'Tutee'}
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: Dashboard,
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

    // --- TUTOR ROUTES ---
    {
      path: '/tutor-setup',
      name: 'tutorpreferencesetup',
      component: () => import('@/views/TutorPreferenceSetup.vue'),
      // meta: { requiresAuth: true, role: 'Tutor' }
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
      // meta: { requiresAuth: true, role: 'Tutor' }
    },
    {
      path: '/booking-details',
      name: 'booking-details',
      component: () => import('@/views/BookingDetails.vue'),
      meta: { requiresAuth: true, role: 'Tutor' }
    },

    // --- SHARED AUTH ROUTES ---
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
  NAVIGATION GUARD
  Protects routes based on authentication and role
*/
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  // If route requires authentication
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return next('/login')
  }

  // If route requires specific role
  if (to.meta.role && authStore.userRole !== to.meta.role) {

    if (authStore.userRole === 'Tutee') {
      return next('/dashboard')
    }

    if (authStore.userRole === 'Tutor') {
      return next('/tch-dashboard')
    }

    return next('/')
  }

  next()
})

export default router