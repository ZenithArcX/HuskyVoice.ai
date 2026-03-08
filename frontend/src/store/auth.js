// ============================================================
// src/store/auth.js — Pinia Authentication Store
//
// This is the single source of truth for authentication state.
// It stores the JWT token and user info and persists them to
// localStorage so the user stays logged in after a page refresh.
//
// USAGE in any component:
//   import { useAuthStore } from '@/store/auth'
//   const authStore = useAuthStore()
//   authStore.login(token, user)
//   authStore.logout()
//   if (authStore.isLoggedIn) { ... }
// ============================================================

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

// defineStore takes a unique ID ('auth') and a setup function.
// The setup function uses refs and computeds just like a component.
export const useAuthStore = defineStore('auth', () => {

  // -------------------------------------------------------
  // STATE — reactive variables (like data() in Options API)
  // ref() makes a variable reactive — Vue tracks changes to it.
  // We initialize from localStorage so state survives refresh.
  // -------------------------------------------------------

  // token holds the JWT string, e.g. "eyJhbGciOiJIUzI1..."
  // On first load, try to restore from localStorage.
  const token = ref(localStorage.getItem('token') || null)

  // user holds the logged-in user's profile object: { id, name, email, role }
  // JSON.parse reads back the object stored as a string in localStorage.
  const user = ref(
    localStorage.getItem('user')
      ? JSON.parse(localStorage.getItem('user'))
      : null
  )

  // -------------------------------------------------------
  // GETTERS — derived/computed state (like computed properties)
  // computed() recalculates automatically when dependencies change.
  // -------------------------------------------------------

  // isLoggedIn is true when a token exists in state.
  // Used by the router guard to allow/deny access to protected routes.
  const isLoggedIn = computed(() => !!token.value)

  // isEmployer is true when the logged-in user has the 'employer' role.
  // Used to show/hide employer-only UI elements.
  const isEmployer = computed(() => user.value?.role === 'employer')

  // -------------------------------------------------------
  // ACTIONS — functions that modify state
  // -------------------------------------------------------

  /**
   * login — Store the token and user after successful authentication
   *
   * Called from LoginView.vue after the API returns a success response.
   * Saves to both Pinia state (reactive) and localStorage (persistent).
   *
   * @param {string} newToken - JWT access token from the API
   * @param {object} newUser  - User object { id, name, email, role }
   */
  function login(newToken, newUser) {
    token.value = newToken
    user.value = newUser

    // Persist to localStorage so the login survives a page refresh.
    // localStorage only stores strings, so we JSON.stringify the object.
    localStorage.setItem('token', newToken)
    localStorage.setItem('user', JSON.stringify(newUser))
  }

  /**
   * logout — Clear all authentication state
   *
   * Called on: logout button click, or when Axios interceptor
   * detects a 401 Unauthorized response (expired token).
   * Clears both Pinia reactive state and localStorage.
   */
  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  // Return everything that components or other modules need to access.
  // Only returned items are accessible via useAuthStore().
  return {
    token,
    user,
    isLoggedIn,
    isEmployer,
    login,
    logout
  }
})
