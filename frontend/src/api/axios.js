// ============================================================
// src/api/axios.js — Configured Axios HTTP client
//
// Instead of using plain axios everywhere, we create a pre-configured
// "instance" that automatically:
//   1. Knows the base API URL (from .env)
//   2. Attaches the JWT Bearer token to every request
//   3. Logs the user out on a 401 Unauthorized response
// ============================================================

import axios from 'axios'

// Create a custom axios instance with default settings.
// import.meta.env.VITE_API_URL reads from the .env file.
// If not set, falls back to localhost:8000 for local dev.
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json'
  }
})

// -------------------------------------------------------
// REQUEST INTERCEPTOR
// Runs before EVERY request is sent.
// We read the JWT token from Pinia and attach it to
// the Authorization header as "Bearer <token>".
//
// Why do this here and not in every API call?
// Because it's DRY — we define it once and forget it.
// -------------------------------------------------------
api.interceptors.request.use(
  async (config) => {
    // Dynamic import avoids circular dependency:
    // axios.js loads before Pinia is mounted, but by the time
    // any HTTP request fires, Pinia is ready.
    const { useAuthStore } = await import('@/store/auth')
    const authStore = useAuthStore()

    // If we have a stored token, add it to the request header.
    // FastAPI's OAuth2PasswordBearer reads this header.
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }

    return config  // must return config or request is cancelled
  },
  (error) => Promise.reject(error)
)

// -------------------------------------------------------
// RESPONSE INTERCEPTOR
// Runs after EVERY response is received.
// If the server returns 401 Unauthorized (expired/invalid token),
// we automatically log the user out and redirect to /login.
// -------------------------------------------------------
api.interceptors.response.use(
  (response) => response,  // if success, pass through unchanged
  async (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid — force logout.
      const { useAuthStore } = await import('@/store/auth')
      const authStore = useAuthStore()
      authStore.logout()

      // Redirect to login page
      window.location.href = '/login'
    }
    return Promise.reject(error)  // propagate error to the calling function
  }
)

export default api
