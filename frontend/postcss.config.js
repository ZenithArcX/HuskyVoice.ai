// postcss.config.js — PostCSS plugin configuration
// PostCSS processes the CSS. Tailwind and Autoprefixer run as PostCSS plugins.

export default {
  plugins: {
    tailwindcss: {},     // runs Tailwind's utility classes generation
    autoprefixer: {},    // automatically adds vendor prefixes for browser compatibility
  }
}
