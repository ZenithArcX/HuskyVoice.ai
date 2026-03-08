<!-- ============================================================
  EmployerDashboard.vue — Employer's management panel

  Layout: 2 columns
    Left  (narrow, sticky) — calendar + selected-day employee list
    Right (wide)           — full leave requests table
============================================================ -->

<template>
  <div class="max-w-7xl mx-auto">

    <h1 class="text-2xl font-bold text-gray-800 mb-6">Leave Management</h1>

    <!-- ── 2-column grid ──────────────────────────────────── -->
    <div class="flex gap-6 items-start">

      <!-- ═══════════════════════════════════════════════════
           LEFT COLUMN — Calendar + day detail
      ═══════════════════════════════════════════════════ -->
      <div class="w-72 flex-shrink-0 space-y-4 sticky top-6">

        <!-- Calendar card -->
        <div class="bg-white rounded-xl shadow p-4">

          <!-- Month nav -->
          <div class="flex items-center justify-between mb-3">
            <button
              @click="prevMonth"
              class="w-7 h-7 flex items-center justify-center rounded-full hover:bg-gray-100 text-gray-500 transition font-bold"
            >‹</button>
            <h2 class="text-sm font-semibold text-gray-800">{{ monthName }} {{ calendarYear }}</h2>
            <button
              @click="nextMonth"
              class="w-7 h-7 flex items-center justify-center rounded-full hover:bg-gray-100 text-gray-500 transition font-bold"
            >›</button>
          </div>

          <!-- Legend -->
          <div class="flex flex-wrap gap-x-3 gap-y-1 mb-3 text-[10px] text-gray-400">
            <span class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded bg-green-300 inline-block"></span>No leave</span>
            <span class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded bg-red-400 inline-block"></span>On leave</span>
            <span class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded bg-orange-300 inline-block"></span>Weekend</span>
          </div>

          <!-- Day-of-week headers -->
          <div class="grid grid-cols-7 mb-1">
            <div
              v-for="d in ['S','M','T','W','T','F','S']"
              :key="d + Math.random()"
              class="text-center text-[10px] font-semibold text-gray-400"
            >{{ d }}</div>
          </div>

          <!-- Day grid -->
          <div class="grid grid-cols-7 gap-0.5">
            <div v-for="n in firstDayOffset" :key="'e'+n"></div>
            <button
              v-for="day in daysInMonth"
              :key="day"
              @click="selectDate(day)"
              :class="[
                'aspect-square rounded flex items-center justify-center text-[11px] font-medium transition border',
                dayColorClass(day),
                selectedDate === dayStr(day)
                  ? 'border-blue-500 ring-1 ring-blue-400 scale-110 shadow'
                  : 'border-transparent hover:border-gray-300'
              ]"
            >{{ day }}</button>
          </div>
        </div>

        <!-- ── Selected date employee list ── -->
        <div v-if="selectedDate" class="bg-white rounded-xl shadow p-4">
          <h3 class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">
            {{ formatDate(selectedDate) }}
          </h3>

          <!-- No leaves -->
          <p
            v-if="leavesOnDay.length === 0"
            class="text-xs text-green-600 bg-green-50 rounded-lg px-3 py-2"
          >No employees on leave</p>

          <!-- One row per employee -->
          <div v-else class="space-y-2">
            <div
              v-for="leave in leavesOnDay"
              :key="leave.id"
              class="border-l-4 pl-3 py-1"
              :class="leave.status === 'Approved' ? 'border-green-400' : leave.status === 'Rejected' ? 'border-red-400' : 'border-yellow-400'"
            >
              <!-- Name + status badge -->
              <div class="flex items-center justify-between">
                <p class="text-sm font-semibold text-gray-800 truncate">{{ leave.user_name }}</p>
                <span class="ml-2 text-[10px] px-1.5 py-0.5 rounded-full font-medium flex-shrink-0" :class="statusBadgeClass(leave.status)">
                  {{ leave.status }}
                </span>
              </div>
              <!-- Leave type -->
              <p class="text-[11px] text-gray-400 mb-0.5">{{ leave.leave_type }}</p>
              <!-- Reason -->
              <p class="text-[11px] text-gray-500 italic leading-tight break-words">{{ leave.reason }}</p>

              <!-- Quick approve/reject for pending, edit for reviewed -->
              <div v-if="leave.status === 'Pending'" class="flex gap-2 mt-2">
                <button @click="openModal(leave, 'Approved')" class="text-[11px] bg-green-100 text-green-700 px-2 py-0.5 rounded hover:bg-green-200 transition">✓ Approve</button>
                <button @click="openModal(leave, 'Rejected')" class="text-[11px] bg-red-100 text-red-700 px-2 py-0.5 rounded hover:bg-red-200 transition">✕ Reject</button>
              </div>
              <button
                v-else
                @click="openEditModal(leave)"
                class="mt-2 text-[11px] bg-blue-50 text-blue-600 px-2 py-0.5 rounded hover:bg-blue-100 transition flex items-center gap-1"
              >✎ Edit decision</button>
            </div>
          </div>
        </div>

        <!-- Placeholder when nothing selected -->
        <div v-else class="bg-white rounded-xl shadow p-4 text-xs text-gray-400 text-center">
          Click a day to see who's on leave
        </div>

      </div>
      <!-- end LEFT column -->

      <!-- ═══════════════════════════════════════════════════
           RIGHT COLUMN — Full leave table
      ═══════════════════════════════════════════════════ -->
      <div class="flex-1 min-w-0">
        <h2 class="text-base font-semibold text-gray-700 mb-3">All Leave Requests</h2>

        <div v-if="loading" class="text-center py-12 text-gray-500">Loading...</div>
        <div v-else-if="error" class="text-center py-12 text-red-500">{{ error }}</div>
        <div v-else-if="leaves.length === 0" class="text-center py-12 text-gray-400">No leave requests found.</div>

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
              <tr v-for="leave in leaves" :key="leave.id" class="hover:bg-gray-50">
                <td class="px-4 py-3 text-sm text-gray-800">{{ leave.user_name || leave.user_id }}</td>
                <td class="px-4 py-3 text-sm text-gray-700">{{ leave.leave_type }}</td>
                <td class="px-4 py-3 text-sm text-gray-600 whitespace-nowrap">
                  {{ formatDate(leave.start_date) }}<br/>{{ formatDate(leave.end_date) }}
                </td>
                <td class="px-4 py-3 text-sm text-gray-600 max-w-xs truncate" :title="leave.reason">
                  {{ leave.reason }}
                </td>
                <td class="px-4 py-3">
                  <span class="px-2 py-1 rounded-full text-xs font-medium" :class="statusBadgeClass(leave.status)">
                    {{ leave.status }}
                  </span>
                </td>
                <td class="px-4 py-3">
                  <div v-if="leave.status === 'Pending'" class="flex gap-2">
                    <button @click="openModal(leave, 'Approved')" class="text-xs bg-green-100 text-green-700 px-3 py-1 rounded hover:bg-green-200 transition">Approve</button>
                    <button @click="openModal(leave, 'Rejected')" class="text-xs bg-red-100 text-red-700 px-3 py-1 rounded hover:bg-red-200 transition">Reject</button>
                  </div>
                  <button
                    v-else
                    @click="openEditModal(leave)"
                    class="text-xs bg-blue-50 text-blue-600 px-3 py-1 rounded hover:bg-blue-100 transition"
                  >✎ Edit</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <!-- end RIGHT column -->

    </div>
    <!-- end 2-col grid -->

    <!-- =====================================================
         ACTION MODAL — Approve / Reject confirmation
    ===================================================== -->
    <div
      v-if="modal.show"
      class="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-xl shadow-xl p-6 w-full max-w-md">
        <h2 class="text-lg font-bold mb-3">
          {{ modal.isEdit ? 'Edit Decision' : modal.targetStatus + ' Leave Request' }}
        </h2>
        <p class="text-sm text-gray-600 mb-4">
          Employee: <strong>{{ modal.leave?.user_name }}</strong><br/>
          Leave type: <strong>{{ modal.leave?.leave_type }}</strong>
        </p>

        <!-- Status toggle shown only in edit mode -->
        <div v-if="modal.isEdit" class="flex gap-3 mb-4">
          <button
            @click="modal.targetStatus = 'Approved'"
            :class="[
              'flex-1 py-1.5 rounded-lg text-sm font-semibold border-2 transition',
              modal.targetStatus === 'Approved'
                ? 'bg-green-600 text-white border-green-600'
                : 'bg-white text-green-700 border-green-300 hover:bg-green-50'
            ]"
          >✓ Approved</button>
          <button
            @click="modal.targetStatus = 'Rejected'"
            :class="[
              'flex-1 py-1.5 rounded-lg text-sm font-semibold border-2 transition',
              modal.targetStatus === 'Rejected'
                ? 'bg-red-600 text-white border-red-600'
                : 'bg-white text-red-700 border-red-300 hover:bg-red-50'
            ]"
          >✕ Rejected</button>
        </div>

        <label class="block text-sm font-medium text-gray-700 mb-1">{{ modal.isEdit ? 'Update note (optional)' : 'Add a note (optional)' }}</label>
        <textarea
          v-model="modal.note"
          rows="3"
          placeholder="e.g., Approved. Please ensure handover."
          class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 resize-none"
        ></textarea>

        <p v-if="modal.error" class="text-red-500 text-sm mt-2">{{ modal.error }}</p>

        <div class="flex gap-3 mt-4">
          <button
            @click="confirmAction"
            :disabled="modal.loading"
            class="flex-1 py-2 rounded-lg font-semibold text-white disabled:opacity-50 transition"
            :class="modal.targetStatus === 'Approved' ? 'bg-green-600 hover:bg-green-700' : 'bg-red-600 hover:bg-red-700'"
          >
            {{ modal.loading ? 'Processing...' : (modal.isEdit ? 'Save Changes' : `Confirm ${modal.targetStatus}`) }}
          </button>
          <button
            @click="closeModal"
            class="flex-1 py-2 rounded-lg font-semibold bg-gray-100 text-gray-700 hover:bg-gray-200 transition"
          >Cancel</button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { getAllLeaves, updateLeaveStatus } from '@/api/leave'

// ── Data ──────────────────────────────────────────────────────
const leaves   = ref([])
const loading  = ref(false)
const error    = ref('')

// ── Calendar state ────────────────────────────────────────────
const today         = new Date()
const calendarYear  = ref(today.getFullYear())
const calendarMonth = ref(today.getMonth())   // 0-indexed (0=Jan)
const selectedDate  = ref(null)               // "YYYY-MM-DD" string or null

// ── Calendar computed helpers ─────────────────────────────────

const MONTH_NAMES = [
  'January','February','March','April','May','June',
  'July','August','September','October','November','December'
]

// Month name string e.g. "March"
const monthName = computed(() => MONTH_NAMES[calendarMonth.value])

// How many days are in the currently displayed month
const daysInMonth = computed(() =>
  new Date(calendarYear.value, calendarMonth.value + 1, 0).getDate()
)

// Which column (0=Sun … 6=Sat) the 1st of the month falls on
// Used to push the first day square into the right column
const firstDayOffset = computed(() =>
  new Date(calendarYear.value, calendarMonth.value, 1).getDay()
)

// Build "YYYY-MM-DD" string for a given day number in the current view
function dayStr(day) {
  const m = String(calendarMonth.value + 1).padStart(2, '0')
  const d = String(day).padStart(2, '0')
  return `${calendarYear.value}-${m}-${d}`
}

/**
 * dayColorClass — returns Tailwind bg + text classes for a calendar square
 *
 * Priority:
 *  1. Weekend (Sat/Sun) → orange
 *  2. Any leave overlapping this day → red
 *  3. Otherwise → green
 */
function dayColorClass(day) {
  const dow = new Date(calendarYear.value, calendarMonth.value, day).getDay()

  // Weekend first — overrides everything else
  if (dow === 0 || dow === 6) {
    return 'bg-orange-200 text-orange-800 cursor-pointer'
  }

  const ds = dayStr(day)
  const hasLeave = leaves.value.some(l => ds >= l.start_date && ds <= l.end_date)

  return hasLeave
    ? 'bg-red-300 text-red-900 cursor-pointer'
    : 'bg-green-100 text-green-800 cursor-pointer'
}

// Leaves that cover the selected date (start_date ≤ selected ≤ end_date)
const leavesOnDay = computed(() => {
  if (!selectedDate.value) return []
  return leaves.value.filter(l =>
    selectedDate.value >= l.start_date && selectedDate.value <= l.end_date
  )
})

// ── Calendar navigation ───────────────────────────────────────

function prevMonth() {
  if (calendarMonth.value === 0) {
    calendarMonth.value = 11
    calendarYear.value--
  } else {
    calendarMonth.value--
  }
  selectedDate.value = null   // clear selection when switching months
}

function nextMonth() {
  if (calendarMonth.value === 11) {
    calendarMonth.value = 0
    calendarYear.value++
  } else {
    calendarMonth.value++
  }
  selectedDate.value = null
}

function selectDate(day) {
  const ds = dayStr(day)
  // Toggle: clicking the same date again deselects it
  selectedDate.value = selectedDate.value === ds ? null : ds
}

// ── Modal state ───────────────────────────────────────────────
const modal = reactive({
  show: false,
  leave: null,
  targetStatus: '',
  note: '',
  loading: false,
  error: '',
  isEdit: false    // true when re-editing an already-reviewed leave
})

// ── API calls ─────────────────────────────────────────────────

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

function openModal(leave, status) {
  modal.leave        = leave
  modal.targetStatus = status
  modal.note         = ''
  modal.error        = ''
  modal.loading      = false
  modal.isEdit       = false
  modal.show         = true
}

// Opens the modal pre-filled with the existing decision so employer can change it
function openEditModal(leave) {
  modal.leave        = leave
  modal.targetStatus = leave.status          // pre-select current status
  modal.note         = leave.note || ''      // pre-fill existing note
  modal.error        = ''
  modal.loading      = false
  modal.isEdit       = true
  modal.show         = true
}

function closeModal() {
  modal.show  = false
  modal.leave = null
}

async function confirmAction() {
  modal.loading = true
  modal.error   = ''
  try {
    await updateLeaveStatus(modal.leave.id, {
      status: modal.targetStatus,
      note: modal.note || undefined
    })
    // Optimistic update — patch the local array without re-fetching
    const target = leaves.value.find(l => l.id === modal.leave.id)
    if (target) {
      target.status = modal.targetStatus
      target.note   = modal.note
    }
    closeModal()
  } catch (err) {
    modal.error = err.response?.data?.detail || 'Action failed. Please try again.'
  } finally {
    modal.loading = false
  }
}

// ── Formatters ────────────────────────────────────────────────

function formatDate(isoStr) {
  if (!isoStr) return '—'
  // Append T00:00 so the date isn't shifted by timezone offset
  return new Date(isoStr + 'T00:00').toLocaleDateString('en-US', {
    year: 'numeric', month: 'short', day: 'numeric'
  })
}

function statusBadgeClass(status) {
  const map = {
    'Pending':  'bg-yellow-100 text-yellow-700',
    'Approved': 'bg-green-100  text-green-700',
    'Rejected': 'bg-red-100    text-red-700'
  }
  return map[status] || 'bg-gray-100 text-gray-600'
}

onMounted(fetchLeaves)
</script>
