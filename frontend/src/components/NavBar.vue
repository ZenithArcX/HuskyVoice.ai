<!-- ============================================================
  NavBar.vue — Top navigation bar
  
  Shown on every page (rendered in App.vue).
  Displays different links based on whether the user is logged in
  and what role they have (employee vs employer).
============================================================ -->

<template>
  <nav class="bg-blue-700 text-white shadow-md">
    <div class="container mx-auto px-4 py-3 flex items-center justify-between">

      <!-- Brand logo / app name -->
      <RouterLink to="/" class="text-xl font-bold tracking-wide">
        HuskyVoice Leave
      </RouterLink>

      <!-- Navigation links — change based on auth state and role -->
      <div class="flex items-center gap-4">

        <!-- Shown ONLY when NOT logged in -->
        <template v-if="!authStore.isLoggedIn">
          <RouterLink to="/login" class="hover:underline">Login</RouterLink>
          <RouterLink to="/register" class="hover:underline">Register</RouterLink>
        </template>

        <!-- Shown when logged in as EMPLOYEE -->
        <template v-else-if="!authStore.isEmployer">
          <RouterLink to="/dashboard" class="hover:underline">My Leaves</RouterLink>
          <RouterLink to="/apply" class="hover:underline">Apply Leave</RouterLink>
        </template>

        <!-- Shown when logged in as EMPLOYER -->
        <template v-else>
          <RouterLink to="/employer" class="hover:underline">All Requests</RouterLink>
        </template>

        <!-- 
          Logout button — shown when ANY user is logged in.
          @click calls the logout action and redirects to /login.
        -->
        <button
          v-if="authStore.isLoggedIn"
          @click="handleLogout"
          class="bg-white text-blue-700 px-3 py-1 rounded font-semibold hover:bg-gray-100 transition"
        >
          Logout ({{ authStore.user?.name }})
        </button>

      </div>
    </div>
  </nav>
</template>

<script setup>
import { useAuthStore } from '@/store/auth'
import { useRouter } from 'vue-router'

// Get the Pinia auth store to check login state and user info
const authStore = useAuthStore()

// useRouter() gives access to the router for programmatic navigation
const router = useRouter()

/**
 * handleLogout — Clears Pinia state + localStorage, then navigates to /login
 *
 * authStore.logout() removes token and user from state and localStorage.
 * router.push('/login') changes the URL, triggering the router guard.
 */
function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>
