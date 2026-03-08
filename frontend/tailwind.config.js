// tailwind.config.js — Tailwind CSS configuration
// Tailwind scans these files for class names and removes unused ones in production.

/** @type {import('tailwindcss').Config} */
export default {
  // content: tells Tailwind which files to scan for used class names.
  // Only classes found here will be in the final CSS bundle.
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts}"  // all Vue and JS files inside src/
  ],
  theme: {
    extend: {
      // Add custom colors or spacing here if needed
    }
  },
  plugins: []
}
