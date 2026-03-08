<!-- ============================================================
  EmployeeDashboard.vue — Employee's leave history page
  
  Fetches and displays the current employee's leave requests.
  Each leave shows its type, dates, reason, and colour-coded status.
  Accessible only to users with role 'employee' (enforced by router guard).
  
  ROUTE: GET /dashboard
============================================================ -->

<template>
  <div class="max-w-4xl mx-auto">

    <!-- Page header -->
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-gray-800">My Leave Requests</h1>
      <RouterLink
        to="/apply"
        class="bg-blue-600 text-white px-4 py-2 rounded-lg font-semibold hover:bg-blue-700 transition"
      >
        + Apply for Leave
      </RouterLink>
    </div>

    <!-- Loading spinner — shown while API call is in progress -->
    <div v-if="loading" class="text-center py-12 text-gray-500">
      Loading your leaves...
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="text-center py-12 text-red-500">
      {{ error }}
    </div>

    <!-- Empty state — no leave requests yet -->
    <div v-else-if="leaves.length === 0" class="text-center py-12 text-gray-400">
      You haven't applied for any leave yet.
      <RouterLink to="/apply" class="text-blue-600 hover:underline ml-1">Apply now</RouterLink>
    </div>

    <!-- 
      Leave cards list
      v-for loops over the leaves array and renders one card per leave.
      :key uses the unique id to help Vue track list items efficiently.
    -->
    <div v-else class="space-y-4">
      <div
        v-for="leave in leaves"
        :key="leave.id"
        class="bg-white rounded-xl shadow p-5 border-l-4"
        :class="borderColor(leave.status)"
      >
        <!-- Card top row: leave type + status badge -->
        <div class="flex items-center justify-between mb-2">
          <h2 class="text-lg font-semibold text-gray-800">{{ leave.leave_type }}</h2>
          
          <!-- Status badge — colour changes based on status value -->
          <span
            class="px-3 py-1 rounded-full text-sm font-medium"
            :class="statusBadgeClass(leave.status)"
          >
            {{ leave.status }}
          </span>
        </div>

        <!-- Date range -->
        <p class="text-sm text-gray-500 mb-1">
          📅 {{ formatDate(leave.start_date) }} → {{ formatDate(leave.end_date) }}
        </p>

        <!-- Reason -->
        <p class="text-gray-700 text-sm mb-2">{{ leave.reason }}</p>

        <!-- Employer's note — shown only if the leave was reviewed and a note was left -->
        <p v-if="leave.note" class="text-sm text-indigo-600 italic">
          Note from employer: "{{ leave.note }}"
        </p>

        <!-- Submission timestamp -->
        <p class="text-xs text-gray-400 mt-2">
          Submitted: {{ formatDate(leave.created_at) }}
        </p>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getMyLeaves } from '@/api/leave'

// leaves holds the array of leave objects from the API
const leaves = ref([])

// loading shows/hides the loading spinner
const loading = ref(false)

// error stores an error message if the API call fails
const error = ref('')

/**
 * fetchLeaves — Calls the API and populates the leaves array
 *
 * Called automatically when the component mounts (onMounted).
 * getMyLeaves() calls GET /api/leave/my and returns the array.
 */
async function fetchLeaves() {
  loading.value = true
  error.value = ''
  try {
    leaves.value = await getMyLeaves()
  } catch (err) {
    error.value = 'Failed to fetch your leaves. Please try again.'
  } finally {
    loading.value = false
  }
}

/**
 * formatDate — Converts an ISO date string to human-readable format
 *
 * @param {string} isoStr - Date string like "2024-03-15" or full ISO timestamp
 * @returns {string} - e.g., "Mar 15, 2024"
 */
function formatDate(isoStr) {
  if (!isoStr) return '—'
  return new Date(isoStr).toLocaleDateString('en-US', {
    year: 'numeric', month: 'short', day: 'numeric'
  })
}

/**
 * statusBadgeClass — Returns Tailwind CSS classes for the status badge colour
 *
 * @param {string} status - "Pending" | "Approved" | "Rejected"
 * @returns {string} Tailwind class string
 */
function statusBadgeClass(status) {
  const map = {
    'Pending':  'bg-yellow-100 text-yellow-700',
    'Approved': 'bg-green-100 text-green-700',
    'Rejected': 'bg-red-100 text-red-700'
  }
  return map[status] || 'bg-gray-100 text-gray-600'
}

/**
 * borderColor — Returns a left-border colour class for the card
 * so the status is visually clear at a glance.
 */
function borderColor(status) {
  const map = {
    'Pending':  'border-yellow-400',
    'Approved': 'border-green-500',
    'Rejected': 'border-red-500'
  }
  return map[status] || 'border-gray-300'
}

// onMounted runs after the component is rendered in the DOM.
// This is the right place to call APIs (like useEffect in React).
onMounted(fetchLeaves)
</script>
