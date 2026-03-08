<!-- ============================================================
  App.vue — Root component
  
  This is the shell of the entire Vue application.
  <RouterView> is a placeholder — Vue Router swaps in the
  correct page component (LoginView, Dashboard, etc.) here
  based on the current URL.
  
  NavBar is shown on every page (it's outside RouterView).
============================================================ -->

<template>
  <!-- 
    min-h-screen: makes sure the app fills the full viewport height
    bg-gray-50: light gray background for the entire app
  -->
  <div class="min-h-screen bg-gray-50">
    <!-- NavBar renders on every page -->
    <NavBar />

    <!-- 
      RouterView renders the current page component.
      When URL = /login  → LoginView.vue renders here
      When URL = /dashboard → EmployeeDashboard.vue renders here
      etc.
    -->
    <main class="container mx-auto px-4 py-6">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import NavBar from '@/components/NavBar.vue'
</script>
