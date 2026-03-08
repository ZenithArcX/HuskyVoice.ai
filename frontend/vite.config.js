// vite.config.js — Vite build tool configuration
// Vite is the dev server + bundler for our Vue app.

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [
    vue()  // enables .vue Single File Component support
  ],
  resolve: {
    alias: {
      // '@' is a shorthand for the src/ directory.
      // Instead of "../../components/Foo" you write "@/components/Foo"
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  }
})
