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
<<<<<<< HEAD
<<<<<<< HEAD
        //meta: { requiresAuth: true, role: 'Tutee' }
=======
        meta: { requiresAuth: true, role: 'Tutee' }
>>>>>>> 55c05251b90d63bc5f9147814e303f15f12b9f22
=======
        //meta: { requiresAuth: true, role: 'Tutee' }
>>>>>>> 9fdd74f (Fixed Authentication tokens)
      },
      {
        path: '/tutor-setup', // Tutor onboarding
        name: 'tutorpreferencesetup',
        component: () => import('@/views/TutorPreferenceSetup.vue'),
        //meta: { requiresAuth: true, role: 'tutor' }
      },

      // --- TUTEE ROUTES (Student Dashboard) ---
      {
        path: '/dashboard',
        name: 'dashboard',
        component: Dashboard,
<<<<<<< HEAD
<<<<<<< HEAD
         //meta: { requiresAuth: true, role: 'Tutee' }
=======
         meta: { requiresAuth: true, role: 'Tutee' }
>>>>>>> 55c05251b90d63bc5f9147814e303f15f12b9f22
=======
         //meta: { requiresAuth: true, role: 'Tutee' }
>>>>>>> 9fdd74f (Fixed Authentication tokens)
      },
      {
        path: '/tutors',
        name: 'tutors',
        component: () => import('@/views/FindTutors.vue'),
<<<<<<< HEAD
<<<<<<< HEAD
        //meta: { requiresAuth: true, role: 'Tutee' }
=======
        meta: { requiresAuth: true, role: 'Tutee' }
>>>>>>> 55c05251b90d63bc5f9147814e303f15f12b9f22
=======
        //meta: { requiresAuth: true, role: 'Tutee' }
>>>>>>> 9fdd74f (Fixed Authentication tokens)
      },
      {
        path: '/book',
        name: 'book',
        component: () => import('@/views/InitialBooking.vue'),
<<<<<<< HEAD
<<<<<<< HEAD
        //meta: { requiresAuth: true, role: 'Tutee' }
=======
        meta: { requiresAuth: true, role: 'Tutee' }
>>>>>>> 55c05251b90d63bc5f9147814e303f15f12b9f22
=======
        //meta: { requiresAuth: true, role: 'Tutee' }
>>>>>>> 9fdd74f (Fixed Authentication tokens)
      },
      {
        path: '/tutor/:id',
        name: 'tutor-details',
        component: () => import('@/views/TutorDetails.vue'),
<<<<<<< HEAD
<<<<<<< HEAD
        //meta: { requiresAuth: true, role: 'Tutee' }
=======
        meta: { requiresAuth: true, role: 'Tutee' }
>>>>>>> 55c05251b90d63bc5f9147814e303f15f12b9f22
=======
        //meta: { requiresAuth: true, role: 'Tutee' }
>>>>>>> 9fdd74f (Fixed Authentication tokens)
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
<<<<<<< HEAD
<<<<<<< HEAD
        //meta: { requiresAuth: true, role: 'Tutor' }
=======
        meta: { requiresAuth: true, role: 'Tutor' }
>>>>>>> 55c05251b90d63bc5f9147814e303f15f12b9f22
=======
        //meta: { requiresAuth: true, role: 'Tutor' }
>>>>>>> 9fdd74f (Fixed Authentication tokens)
      },
      {
        path: '/tch-availability',
        name: 'tch-availability',
        component: () => import('@/views/TutorSchedule.vue'), // The availability view
<<<<<<< HEAD
<<<<<<< HEAD
        //meta: { requiresAuth: true, role: 'Tutor' }
=======
        meta: { requiresAuth: true, role: 'Tutor' }
>>>>>>> 55c05251b90d63bc5f9147814e303f15f12b9f22
=======
        //meta: { requiresAuth: true, role: 'Tutor' }
>>>>>>> 9fdd74f (Fixed Authentication tokens)
      },
      {
        path: '/tch-payments',
        name: 'tch-payments',
        component: () => import('@/views/TutorPaymentScreen.vue'), // The verification view
<<<<<<< HEAD
<<<<<<< HEAD
        //meta: { requiresAuth: true, role: 'Tutor' }
=======
        meta: { requiresAuth: true, role: 'Tutor' }
=======
        //meta: { requiresAuth: true, role: 'Tutor' }
>>>>>>> 9fdd74f (Fixed Authentication tokens)
      },
      {
        path: '/tch-completedSessions',
        name: 'tch-completedSessions',
        component: () => import('@/views/TutorCompletedSessions.vue'),
        //meta: { requiresAuth: true, role: 'tutor' }
>>>>>>> 55c05251b90d63bc5f9147814e303f15f12b9f22
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

  // If route requires auth and user is not logged in
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return next('/login')
  }

  // If route requires a specific role
  if (to.meta.role && authStore.userRole !== to.meta.role) {

    // Smart redirect based on actual role
    if (authStore.userRole === 'Tutee') {
      return next('/dashboard')
    }

    if (authStore.userRole === 'Tutor') {
      return next('/tch-dashboard')
    }

    return next('/') // fallback
  }

  next()
})

export default router
