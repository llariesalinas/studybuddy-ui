import { createRouter, createWebHistory } from 'vue-router'
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

    // --- AUTHENTICATED ROUTES (With Sidebar) ---
    {
      path: '/dashboard',
      name: 'dashboard',
      component: Dashboard
    },
    {
      path: '/tutors',
      name: 'tutors',
      component: () => import('@/views/FindTutors.vue')
    },
    {
      path: '/schedule',
      name: 'schedule',
      component: () => import('@/views/Schedule.vue')
    },
    {
      path: '/reports',
      name: 'reports',
      component: () => import('@/views/SessionsReports.vue')
    }
  ]
})

export default router