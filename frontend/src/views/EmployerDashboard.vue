<!-- ============================================================
  EmployerDashboard.vue — Employer's management panel
  
  Displays all leave requests from all employees.
  Employer can approve or reject each Pending request inline.
  Status changes call the PATCH endpoint and immediately update the UI.
  
  ROUTE: GET /employer
============================================================ -->

<template>
  <div class="max-w-5xl mx-auto">

    <h1 class="text-2xl font-bold text-gray-800 mb-6">All Leave Requests</h1>

    <!-- Loading state -->
    <div v-if="loading" class="text-center py-12 text-gray-500">
      Loading all leave requests...
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="text-center py-12 text-red-500">{{ error }}</div>

    <!-- Empty state -->
    <div v-else-if="leaves.length === 0" class="text-center py-12 text-gray-400">
      No leave requests found.
    </div>

    <!-- Leave table — shown when data is available -->
    <div v-else class="bg-white rounded-xl shadow overflow-x-auto">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Employee</th>
            <th class="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Type</th>
            <th class="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Dates</th>
            <th class="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Reason</th>
            <th class="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Status</th>
            <th class="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <!-- One row per leave request -->
          <tr v-for="leave in leaves" :key="leave.id" class="hover:bg-gray-50">

            <!-- Employee name (from the leave's user_name field set by the API) -->
            <td class="px-4 py-3 text-sm text-gray-800">{{ leave.user_name || leave.user_id }}</td>

            <!-- Leave type -->
            <td class="px-4 py-3 text-sm text-gray-700">{{ leave.leave_type }}</td>

            <!-- Date range -->
            <td class="px-4 py-3 text-sm text-gray-600 whitespace-nowrap">
              {{ formatDate(leave.start_date) }}<br/>{{ formatDate(leave.end_date) }}
            </td>

            <!-- Reason (truncated to 50 chars to keep table clean) -->
            <td class="px-4 py-3 text-sm text-gray-600 max-w-xs truncate" :title="leave.reason">
              {{ leave.reason }}
            </td>

            <!-- Status badge -->
            <td class="px-4 py-3">
              <span class="px-2 py-1 rounded-full text-xs font-medium" :class="statusBadgeClass(leave.status)">
                {{ leave.status }}
              </span>
            </td>

            <!-- Action buttons — only shown for Pending leaves -->
            <td class="px-4 py-3">
              <div v-if="leave.status === 'Pending'" class="flex gap-2">

                <!-- Approve button -->
                <button
                  @click="openModal(leave, 'Approved')"
                  class="text-xs bg-green-100 text-green-700 px-3 py-1 rounded hover:bg-green-200 transition"
                >
                  Approve
                </button>

                <!-- Reject button -->
                <button
                  @click="openModal(leave, 'Rejected')"
                  class="text-xs bg-red-100 text-red-700 px-3 py-1 rounded hover:bg-red-200 transition"
                >
                  Reject
                </button>

              </div>
              <!-- Reviewed indicator for already-processed leaves -->
              <span v-else class="text-xs text-gray-400">Reviewed</span>
            </td>

          </tr>
        </tbody>
      </table>
    </div>

    <!-- -------------------------------------------------------
      ACTION MODAL — Pops up when employer clicks Approve/Reject.
      Employer can optionally add a note before confirming.
    ------------------------------------------------------- -->
    <div
      v-if="modal.show"
      class="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-xl shadow-xl p-6 w-full max-w-md">
        <h2 class="text-lg font-bold mb-3">
          {{ modal.targetStatus }} Leave Request
        </h2>
        <p class="text-sm text-gray-600 mb-4">
          Leave type: <strong>{{ modal.leave?.leave_type }}</strong>
        </p>

        <!-- Optional note textarea -->
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Add a note (optional)
        </label>
        <textarea
          v-model="modal.note"
          rows="3"
          placeholder="e.g., Approved. Please ensure handover."
          class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 resize-none"
        ></textarea>

        <!-- Error inside modal -->
        <p v-if="modal.error" class="text-red-500 text-sm mt-2">{{ modal.error }}</p>

        <div class="flex gap-3 mt-4">
          <!-- Confirm action -->
          <button
            @click="confirmAction"
            :disabled="modal.loading"
            class="flex-1 py-2 rounded-lg font-semibold text-white disabled:opacity-50 transition"
            :class="modal.targetStatus === 'Approved' ? 'bg-green-600 hover:bg-green-700' : 'bg-red-600 hover:bg-red-700'"
          >
            {{ modal.loading ? 'Processing...' : `Confirm ${modal.targetStatus}` }}
          </button>

          <!-- Cancel — close modal without doing anything -->
          <button
            @click="closeModal"
            class="flex-1 py-2 rounded-lg font-semibold bg-gray-100 text-gray-700 hover:bg-gray-200 transition"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { getAllLeaves, updateLeaveStatus } from '@/api/leave'

// leaves holds the full list of all employee leave requests
const leaves = ref([])
const loading = ref(false)
const error = ref('')

// modal is a reactive object that controls the confirmation popup state.
// reactive() is like ref() but for objects — no need for .value on nested properties.
const modal = reactive({
  show: false,         // whether the modal is visible
  leave: null,         // the leave object being actioned
  targetStatus: '',    // "Approved" or "Rejected"
  note: '',            // employer's optional note
  loading: false,      // button loading state inside modal
  error: ''            // error message inside the modal
})

/**
 * fetchLeaves — Loads all leave requests from the API
 * Called on component mount.
 */
async function fetchLeaves() {
  loading.value = true
  error.value = ''
  try {
    leaves.value = await getAllLeaves()
  } catch (err) {
    error.value = 'Failed to load leaves. Please refresh the page.'
  } finally {
    loading.value = false
  }
}

/**
 * openModal — Opens the approval/rejection confirmation modal
 *
 * @param {object} leave - The leave document being actioned
 * @param {string} status - "Approved" or "Rejected"
 */
function openModal(leave, status) {
  modal.leave = leave
  modal.targetStatus = status
  modal.note = ''
  modal.error = ''
  modal.loading = false
  modal.show = true
}

/**
 * closeModal — Hides the modal without taking any action
 */
function closeModal() {
  modal.show = false
  modal.leave = null
}

/**
 * confirmAction — Sends the approve/reject PATCH request to the API
 *
 * 1. Calls PATCH /api/leave/{id}/status with { status, note }
 * 2. On success: updates the leave status in the local array (no full re-fetch needed)
 *    This is an "optimistic update" — the UI updates immediately.
 * 3. Closes the modal
 */
async function confirmAction() {
  modal.loading = true
  modal.error = ''

  try {
    await updateLeaveStatus(modal.leave.id, {
      status: modal.targetStatus,
      note: modal.note || undefined    // don't send empty string
    })

    // Find the leave in the local array and update its status in-place.
    // This avoids a full API re-fetch and makes the UI feel instant.
    const target = leaves.value.find(l => l.id === modal.leave.id)
    if (target) {
      target.status = modal.targetStatus
      target.note = modal.note
    }

    closeModal()

  } catch (err) {
    modal.error = err.response?.data?.detail || 'Action failed. Please try again.'
  } finally {
    modal.loading = false
  }
}

/**
 * formatDate — Returns a human-readable date string
 * @param {string} isoStr
 * @returns {string} e.g. "Mar 15, 2024"
 */
function formatDate(isoStr) {
  if (!isoStr) return '—'
  return new Date(isoStr).toLocaleDateString('en-US', {
    year: 'numeric', month: 'short', day: 'numeric'
  })
}

/**
 * statusBadgeClass — Returns Tailwind badge classes for each status
 */
function statusBadgeClass(status) {
  const map = {
    'Pending':  'bg-yellow-100 text-yellow-700',
    'Approved': 'bg-green-100 text-green-700',
    'Rejected': 'bg-red-100 text-red-700'
  }
  return map[status] || 'bg-gray-100 text-gray-600'
}

onMounted(fetchLeaves)
</script>
