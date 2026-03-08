// ============================================================
// src/router/index.js — Vue Router configuration
//
// Vue Router maps URLs to Vue components (pages).
// We also define a "navigation guard" that:
//   - Blocks unauthenticated users from accessing protected routes
//   - Blocks logged-in users from visiting /login or /register
//   - Blocks employees from accessing employer-only routes
//
// Routes use lazy loading: the component JS is only downloaded
// when the user first visits that route (better performance).
// ============================================================

import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/store/auth'

// Each route maps a URL path to a page component.
// meta contains custom flags we check in the navigation guard.
const routes = [
  {
    path: '/',
    // Redirect root URL to /login (will be redirected to dashboard if already logged in)
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    // Lazy loading: () => import(...) means the LoginView.js chunk
    // is only fetched when the user navigates to /login.
    component: () => import('@/views/LoginView.vue'),
    meta: {
      guestOnly: true   // redirect to dashboard if already logged in
    }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/RegisterView.vue'),
    meta: {
      guestOnly: true   // redirect to dashboard if already logged in
    }
  },
  {
    path: '/dashboard',
    name: 'EmployeeDashboard',
    component: () => import('@/views/EmployeeDashboard.vue'),
    meta: {
      requiresAuth: true,  // must be logged in
      role: 'employee'     // must be an employee
    }
  },
  {
    path: '/apply',
    name: 'ApplyLeave',
    component: () => import('@/views/ApplyLeave.vue'),
    meta: {
      requiresAuth: true,
      role: 'employee'
    }
  },
  {
    path: '/employer',
    name: 'EmployerDashboard',
    component: () => import('@/views/EmployerDashboard.vue'),
    meta: {
      requiresAuth: true,
      role: 'employer'     // only employers can access
    }
  },
  {
    path: '/:pathMatch(.*)*',   // matches any undefined URL
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue')
  }
]

// createRouter creates the router instance.
// createWebHistory() enables HTML5 History mode (clean URLs like /login)
// instead of hash mode (ugly URLs like /#/login).
const router = createRouter({
  history: createWebHistory(),
  routes
})

// -------------------------------------------------------
// NAVIGATION GUARD — runs before every route change
//
// to   = the route being navigated TO
// from = the route being navigated FROM
// -------------------------------------------------------
router.beforeEach((to, from) => {
  // Get auth state from Pinia.
  // NOTE: useAuthStore() must be called inside the guard function,
  // not at module level, because Pinia isn't ready until after app.use(pinia).
  const authStore = useAuthStore()

  // CASE 1: Route requires authentication and user is NOT logged in
  // → Redirect to /login
  if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    return { name: 'Login' }
  }

  // CASE 2: Route is for guests only (login/register) and user IS logged in
  // → Redirect to their respective dashboard
  if (to.meta.guestOnly && authStore.isLoggedIn) {
    return authStore.isEmployer
      ? { name: 'EmployerDashboard' }
      : { name: 'EmployeeDashboard' }
  }

  // CASE 3: Route requires a specific role and user has the wrong role
  // → Redirect to their own dashboard
  if (to.meta.role && authStore.user?.role !== to.meta.role) {
    return authStore.isEmployer
      ? { name: 'EmployerDashboard' }
      : { name: 'EmployeeDashboard' }
  }

  // Otherwise, allow navigation to proceed normally.
  // Returning undefined (or nothing) means "allow".
})

export default router
