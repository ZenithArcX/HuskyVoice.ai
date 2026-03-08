// ============================================================
// src/api/leave.js — Leave management API calls
//
// These functions call the FastAPI /api/leave/* endpoints.
// All of them require a valid JWT token (handled automatically
// by the Axios request interceptor in axios.js).
// ============================================================

import api from './axios'

/**
 * applyLeave — Employee submits a new leave request
 *
 * POST /api/leave/apply
 * Requires: employee role
 *
 * @param {object} leaveData - { leave_type, start_date, end_date, reason }
 *   leave_type: "Sick Leave" | "Casual Leave" | "Earned Leave" | "Maternity Leave" | "Paternity Leave"
 *   start_date: "YYYY-MM-DD"
 *   end_date:   "YYYY-MM-DD"
 *   reason:     string (min 10 chars)
 * @returns {object} - { message, id } of the created leave
 * @throws {AxiosError} - 403 if user is not an employee, 422 on validation error
 */
export async function applyLeave(leaveData) {
  const response = await api.post('/api/leave/apply', leaveData)
  return response.data
}

/**
 * getMyLeaves — Employee retrieves their own leave history
 *
 * GET /api/leave/my
 * Requires: any authenticated user
 *
 * @returns {Array} - Array of leave objects, sorted newest first
 *   Each leave: { id, user_id, leave_type, start_date, end_date,
 *                 reason, status, note, reviewed_by, reviewed_at, created_at }
 */
export async function getMyLeaves() {
  const response = await api.get('/api/leave/my')
  return response.data
}

/**
 * getAllLeaves — Employer retrieves ALL employees' leave requests
 *
 * GET /api/leave/all
 * Requires: employer role
 *
 * @returns {Array} - Array of all leave objects from all employees
 * @throws {AxiosError} - 403 if user is not an employer
 */
export async function getAllLeaves() {
  const response = await api.get('/api/leave/all')
  return response.data
}

/**
 * updateLeaveStatus — Employer approves or rejects a leave request
 *
 * PATCH /api/leave/{leaveId}/status
 * Requires: employer role
 *
 * @param {string} leaveId - MongoDB ObjectId string of the leave document
 * @param {object} statusData - { status: "Approved" | "Rejected", note?: string }
 * @returns {object} - { message: "Leave status updated" }
 * @throws {AxiosError} - 403 if not employer, 404 if leave not found
 */
export async function updateLeaveStatus(leaveId, statusData) {
  // Template literal builds the URL: /api/leave/abc123/status
  const response = await api.patch(`/api/leave/${leaveId}/status`, statusData)
  return response.data
}
