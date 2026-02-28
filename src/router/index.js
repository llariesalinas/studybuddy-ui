  import { createRouter, createWebHistory } from 'vue-router'
  import { useAuthStore } from '@/stores/auth' // Needed for the navigation guard
  import Dashboard from '@/views/Dashboard.vue'

  const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
      // --- PUBLIC ROUTES (No Sidebar) ---
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
        path: '/preferencesetup', // Student onboarding
        name: 'preferencesetup',
        component: () => import('@/views/PreferenceSetup.vue'),
        //meta: { requiresAuth: true, role: 'tutee' }
      },
      {
        path: '/tutor-setup', // Tutor onboarding
        name: 'tutorpreferencesetup',
        component: () => import('@/views/TutorPreferenceSetup.vue'),
        meta: { requiresAuth: true, role: 'tutor' }
      },

      // --- TUTEE ROUTES (Student Dashboard) ---
      {
        path: '/dashboard',
        name: 'dashboard',
        component: Dashboard,
        // meta: { requiresAuth: true, role: 'tutee' }
      },
      {
        path: '/tutors',
        name: 'tutors',
        component: () => import('@/views/FindTutors.vue'),
        //meta: { requiresAuth: true, role: 'tutee' }
      },
      {
        path: '/book',
        name: 'book',
        component: () => import('@/views/InitialBooking.vue'),
        //meta: { requiresAuth: true, role: 'tutee' }
      },
      {
        path: '/tutor/:id',
        name: 'tutor-details',
        component: () => import('@/views/TutorDetails.vue'),
        //meta: { requiresAuth: true, role: 'tutee' }
      },
      {
        path: '/payment-tutee/:tutorId',
        name: 'PaymentTutee',
        component: () => import('@/views/PaymentScreenTutee.vue'),
        props: true
      },

      // --- TUTOR ROUTES (Teaching Hub) ---
      {
        path: '/tch-dashboard',
        name: 'tch-dashboard',
        component: () => import('@/views/TutorDashboard.vue'),
        //meta: { requiresAuth: true, role: 'tutor' }
      },
      {
        path: '/tch-availability',
        name: 'tch-availability',
        component: () => import('@/views/TutorSchedule.vue'), // The availability view
        //meta: { requiresAuth: true, role: 'tutor' }
      },
      {
        path: '/tch-payments',
        name: 'tch-payments',
        component: () => import('@/views/TutorPaymentScreen.vue'), // The verification view
        //meta: { requiresAuth: true, role: 'tutor' }
      },

      // --- SHARED ROUTES ---
      {
        path: '/schedule',
        name: 'schedule',
        component: () => import('@/views/Schedule.vue'),
        //meta: { requiresAuth: true }
      },
      {
        path: '/reports',
        name: 'reports',
        component: () => import('@/views/SessionsReports.vue'),
        //meta: { requiresAuth: true }
      },
      {
        path: '/profile',
        name: 'profile',
        component: () => import('@/views/Profile.vue'),
        //meta: { requiresAuth: true }
      }
    ]
  })

  /**
   * STRATEGIC NAVIGATION GUARD
   * This checks the Pinia store before every route change.
   * It ensures users are logged in and have the correct ERD role.
   */
  router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return next('/login')
  }

  if (to.meta.role && authStore.userRole !== to.meta.role) {
    return next('/')
  }

  next()
})

export default router
