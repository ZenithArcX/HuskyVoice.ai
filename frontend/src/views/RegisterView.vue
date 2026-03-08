<!-- ============================================================
  RegisterView.vue — Registration page
  
  Allows new users to create an account.
  They can register as either an 'employee' or 'employer'.
  On success: redirects to /login with a success message.
  
  ROUTE: GET /register
============================================================ -->

<template>
  <div class="flex min-h-[80vh] items-center justify-center">
    <div class="w-full max-w-md bg-white rounded-xl shadow-lg p-8">

      <h1 class="text-2xl font-bold text-center text-blue-700 mb-6">Create Account</h1>

      <form @submit.prevent="handleRegister" class="space-y-4">

        <!-- Full name -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
          <input
            v-model="form.name"
            type="text"
            required
            placeholder="John Doe"
            class="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-400"
          />
        </div>

        <!-- Email -->
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

        <!-- Password -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Password</label>
          <input
            v-model="form.password"
            type="password"
            required
            placeholder="Min 8 chars, 1 uppercase, 1 lowercase, 1 number"
            class="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-400"
          />
        </div>

        <!-- Role selection — determines what the user can do in the app -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Register as</label>
          <!-- 
            v-model on a <select> binds to form.role.
            When user selects "Employer", form.role becomes 'employer'.
          -->
          <select
            v-model="form.role"
            class="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-400"
          >
            <option value="employee">Employee</option>
            <option value="employer">Employer</option>
          </select>
        </div>

        <!-- Success message (shown after successful registration) -->
        <p v-if="successMsg" class="text-green-600 text-sm text-center">{{ successMsg }}</p>

        <!-- Error message -->
        <p v-if="errorMsg" class="text-red-500 text-sm text-center">{{ errorMsg }}</p>

        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-blue-600 text-white py-2 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 transition"
        >
          {{ loading ? 'Creating account...' : 'Register' }}
        </button>
      </form>

      <p class="text-center text-sm text-gray-500 mt-4">
        Already have an account?
        <RouterLink to="/login" class="text-blue-600 hover:underline">Sign in</RouterLink>
      </p>

    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { register as registerApi } from '@/api/auth'

const router = useRouter()

// form holds all the input values
const form = ref({
  name: '',
  email: '',
  password: '',
  role: 'employee'    // default to employee
})

const loading = ref(false)
const errorMsg = ref('')
const successMsg = ref('')

/**
 * handleRegister — Called on form submission
 *
 * 1. Calls POST /api/auth/register with form data
 * 2. On success: shows success message, redirects to /login after 1.5s
 * 3. On failure:
 *    - 409 Conflict → "Email already registered"
 *    - 422 Unprocessable → Pydantic validation error (e.g., weak password)
 *    - other → generic error
 */
async function handleRegister() {
  loading.value = true
  errorMsg.value = ''
  successMsg.value = ''

  try {
    // Call POST /api/auth/register
    await registerApi(form.value)

    // Show success and redirect after a short delay
    successMsg.value = 'Account created! Redirecting to login...'
    setTimeout(() => router.push('/login'), 1500)

  } catch (err) {
    const status = err.response?.status
    if (status === 409) {
      errorMsg.value = 'This email is already registered.'
    } else if (status === 422) {
      // FastAPI validation errors come as an array under err.response.data.detail
      // We join them into one readable string.
      const details = err.response.data.detail
      if (Array.isArray(details)) {
        errorMsg.value = details.map(d => d.msg).join(' | ')
      } else {
        errorMsg.value = details
      }
    } else {
      errorMsg.value = 'Registration failed. Please try again.'
    }
  } finally {
    loading.value = false
  }
}
</script>
