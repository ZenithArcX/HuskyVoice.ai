<!-- ============================================================
  LoginView.vue — Login page
  
  Allows existing users to sign in with email and password.
  On success: stores JWT + user in Pinia, redirects to dashboard.
  On failure: shows an error message from the API.
  
  ROUTE: GET /login
============================================================ -->

<template>
  <div class="flex min-h-[80vh] items-center justify-center">
    <div class="w-full max-w-md bg-white rounded-xl shadow-lg p-8">

      <h1 class="text-2xl font-bold text-center text-blue-700 mb-6">Sign In</h1>

      <!-- Login form — @submit.prevent stops browser from refreshing the page -->
      <form @submit.prevent="handleLogin" class="space-y-4">

        <!-- Email field -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
          <input
            v-model="form.email"
            type="email"
            required
            placeholder="you@example.com"
            class="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-400"
          />
        </div>

        <!-- Password field -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Password</label>
          <input
            v-model="form.password"
            type="password"
            required
            placeholder="••••••••"
            class="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-400"
          />
        </div>

        <!-- Error message — shown only when errorMsg is non-empty -->
        <p v-if="errorMsg" class="text-red-500 text-sm text-center">{{ errorMsg }}</p>

        <!-- Submit button — disabled and shows spinner while loading -->
        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-blue-600 text-white py-2 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 transition"
        >
          {{ loading ? 'Signing in...' : 'Sign In' }}
        </button>
      </form>

      <!-- Link to registration page -->
      <p class="text-center text-sm text-gray-500 mt-4">
        Don't have an account?
        <RouterLink to="/register" class="text-blue-600 hover:underline">Register here</RouterLink>
      </p>

    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { login as loginApi } from '@/api/auth'
import { useAuthStore } from '@/store/auth'

const router = useRouter()
const authStore = useAuthStore()

// form is a reactive object — v-model binds input values here.
// When user types, form.email updates automatically.
const form = ref({
  email: '',
  password: ''
})

// loading prevents double-submit and disables the button during API call
const loading = ref(false)

// errorMsg stores any error text to display below the form
const errorMsg = ref('')

/**
 * handleLogin — Called when the form is submitted
 *
 * 1. Sets loading state (disables button)
 * 2. Calls the login API with email + password
 * 3. On success: saves token to Pinia, redirects based on role
 * 4. On failure: shows user-friendly error message
 */
async function handleLogin() {
  loading.value = true      // show spinner
  errorMsg.value = ''       // clear previous errors

  try {
    // Call POST /api/auth/login
    // Returns { access_token, token_type, user: { id, name, email, role } }
    const data = await loginApi(form.value)

    // Save token + user to Pinia (and localStorage for persistence)
    authStore.login(data.access_token, data.user)

    // Redirect to the correct dashboard based on role
    if (data.user.role === 'employer') {
      router.push('/employer')
    } else {
      router.push('/dashboard')
    }

  } catch (err) {
    // err.response.data.detail contains FastAPI's error message
    // e.g., "Invalid credentials" or "User not found"
    errorMsg.value = err.response?.data?.detail || 'Login failed. Please try again.'
  } finally {
    // Always reset loading, whether success or failure
    loading.value = false
  }
}
</script>
