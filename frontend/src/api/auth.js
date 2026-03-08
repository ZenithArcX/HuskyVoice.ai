// ============================================================
// src/api/auth.js — Authentication API calls
//
// These functions call the FastAPI /api/auth/* endpoints.
// They return the Axios response data directly.
// Errors bubble up to the calling component to handle.
// ============================================================

import api from './axios'

/**
 * register — Create a new user account
 *
 * POST /api/auth/register
 *
 * @param {object} userData - { name, email, password, role }
 * @returns {object} - { id, name, email, role }
 * @throws {AxiosError} - 409 if email already exists, 422 if validation fails
 */
export async function register(userData) {
  // api.post returns a full Axios response object.
  // .data contains the actual JSON body from the server.
  const response = await api.post('/api/auth/register', userData)
  return response.data
}

/**
 * login — Authenticate with email + password
 *
 * POST /api/auth/login
 *
 * @param {object} credentials - { email, password }
 * @returns {object} - { access_token, token_type, user: { id, name, email, role } }
 * @throws {AxiosError} - 401 if credentials are wrong
 *
 * After calling this, store access_token in Pinia:
 *   authStore.login(data.access_token, data.user)
 */
export async function login(credentials) {
  const response = await api.post('/api/auth/login', credentials)
  return response.data
}
