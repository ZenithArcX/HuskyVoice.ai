<!-- ============================================================
  NotFound.vue — 404 Page Not Found
  
  Shown when the user navigates to an undefined URL (/:pathMatch(.*)*).
  Provides a clear message and a link back to the home page.
============================================================ -->

<template>
  <div class="flex min-h-[80vh] items-center justify-center">
    <div class="text-center">
      <h1 class="text-7xl font-black text-blue-600 mb-4">404</h1>
      <p class="text-xl text-gray-700 font-semibold mb-2">Page Not Found</p>
      <p class="text-gray-500 mb-6">
        The page you're looking for doesn't exist or you don't have permission to view it.
      </p>
      <RouterLink
        to="/"
        class="inline-block bg-blue-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-blue-700 transition"
      >
        Go Home
      </RouterLink>
    </div>
  </div>
</template>

<script setup>
// No logic needed for the 404 page — it's purely presentational.
</script>
