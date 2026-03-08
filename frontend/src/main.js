// ============================================================
// src/main.js — Application bootstrap
//
// This is the entry point. It creates the Vue app, registers
// plugins, and mounts it to the #app div in index.html.
// ============================================================

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import './style.css'        // import Tailwind global styles

// createApp(App) creates a new Vue application instance.
// App.vue is the root component — everything renders inside it.
const app = createApp(App)

// createPinia() creates the state management store.
// app.use(pinia) registers it so all components can call useAuthStore() etc.
const pinia = createPinia()
app.use(pinia)

// app.use(router) registers Vue Router.
// After this, <RouterView> and <RouterLink> work in any component,
// and route guards start working.
app.use(router)

// app.mount('#app') finds the <div id="app"> in index.html
// and renders the entire Vue application inside it.
app.mount('#app')
