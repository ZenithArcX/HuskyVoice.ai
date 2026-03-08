<!-- ============================================================
  ApplyLeave.vue — Leave application form (employee only)
  
  Employees fill out this form to submit a new leave request.
  Validates dates client-side before sending to the API.
  On success: redirects to the dashboard so user can see their new leave.
  
  ROUTE: GET /apply
============================================================ -->

<template>
  <div class="max-w-2xl mx-auto">
    <div class="bg-white rounded-xl shadow-lg p-8">

      <h1 class="text-2xl font-bold text-gray-800 mb-6">Apply for Leave</h1>

      <!-- 
        @submit.prevent stops the default browser form submission
        (which would refresh the page) and calls handleSubmit instead.
      -->
      <form @submit.prevent="handleSubmit" class="space-y-5">

        <!-- Leave Type dropdown -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Leave Type</label>
          <select
            v-model="form.leave_type"
            required
            class="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-400"
          >
            <!-- 
              v-for renders one <option> per type.
              The value and display text are the same string here.
            -->
            <option v-for="type in leaveTypes" :key="type" :value="type">{{ type }}</option>
          </select>
        </div>

        <!-- Date range row -->
        <div class="grid grid-cols-2 gap-4">
          <!-- Start Date -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
            <input
              v-model="form.start_date"
              type="date"
              required
              :min="today"
              class="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-400"
            />
          </div>

          <!-- End Date -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">End Date</label>
            <input
              v-model="form.end_date"
              type="date"
              required
              :min="form.start_date || today"
              class="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-400"
            />
          </div>
        </div>

        <!-- Reason textarea -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Reason</label>
          <textarea
            v-model="form.reason"
            required
            rows="4"
            placeholder="Describe the reason for your leave (min 10 characters)"
            class="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-400 resize-none"
          ></textarea>
        </div>

        <!-- Client-side validation error -->
        <p v-if="validationError" class="text-red-500 text-sm">{{ validationError }}</p>

        <!-- API error -->
        <p v-if="errorMsg" class="text-red-500 text-sm">{{ errorMsg }}</p>

        <!-- Success message (briefly shown before redirect) -->
        <p v-if="successMsg" class="text-green-600 text-sm font-medium">{{ successMsg }}</p>

        <!-- Action buttons row -->
        <div class="flex gap-3">
          <button
            type="submit"
            :disabled="loading"
            class="flex-1 bg-blue-600 text-white py-2 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 transition"
          >
            {{ loading ? 'Submitting...' : 'Submit Leave Request' }}
          </button>

          <!-- Cancel goes back to the dashboard without submitting -->
          <RouterLink
            to="/dashboard"
            class="flex-1 text-center bg-gray-100 text-gray-700 py-2 rounded-lg font-semibold hover:bg-gray-200 transition"
          >
            Cancel
          </RouterLink>
        </div>

      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { applyLeave } from '@/api/leave'

const router = useRouter()

// The five leave types the backend accepts (must match Literal in models/leave.py)
const leaveTypes = [
  'Sick Leave',
  'Casual Leave',
  'Paid Leave',
  'Unpaid Leave',
  'Emergency Leave'
]

// form holds all input field values
const form = ref({
  leave_type: 'Sick Leave',   // default selection
  start_date: '',
  end_date: '',
  reason: ''
})

const loading = ref(false)
const errorMsg = ref('')
const validationError = ref('')
const successMsg = ref('')

/**
 * today — computed property that returns today's date as "YYYY-MM-DD"
 * Used as the :min attribute on date inputs to prevent selecting past dates
 * client-side (the backend also validates this).
 */
const today = computed(() => {
  return new Date().toISOString().split('T')[0]
})

/**
 * handleSubmit — Validates inputs and calls the leave API
 *
 * 1. Client-side validation (reason length, date order)
 * 2. Calls POST /api/leave/apply
 * 3. On success: shows confirmation, redirects to /dashboard
 * 4. On failure: parses and displays the API error message
 */
async function handleSubmit() {
  // Reset error states
  validationError.value = ''
  errorMsg.value = ''
  successMsg.value = ''

  // Client-side validation — quick sanity checks before hitting the API
  if (form.value.reason.trim().length < 10) {
    validationError.value = 'Reason must be at least 10 characters long.'
    return   // stop here, don't submit
  }
  if (form.value.end_date < form.value.start_date) {
    validationError.value = 'End date cannot be before start date.'
    return
  }

  loading.value = true
  try {
    await applyLeave(form.value)

    successMsg.value = 'Leave request submitted successfully! Redirecting...'

    // Wait 1.5 seconds then navigate back to the dashboard
    setTimeout(() => router.push('/dashboard'), 1500)

  } catch (err) {
    // Handle validation errors from the backend (Pydantic 422)
    if (err.response?.status === 422) {
      const detail = err.response.data.detail
      if (Array.isArray(detail)) {
        errorMsg.value = detail.map(d => d.msg).join(' | ')
      } else {
        errorMsg.value = detail
      }
    } else {
      errorMsg.value = err.response?.data?.detail || 'Failed to submit. Please try again.'
    }
  } finally {
    loading.value = false
  }
}
</script>
