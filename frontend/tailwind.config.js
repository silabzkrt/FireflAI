/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        "primary": "#ffb3ad",
        "primary-container": "#ff5451",
        "on-primary-container": "#5c0008",
        "secondary": "#94de2d",
        "tertiary": "#4fdbc8",
        "background": "#1e100e",
        "surface": "#1e100e",
        "surface-variant": "#42302f",
        "on-surface": "#f9dcd9",
        "on-surface-variant": "#e4beba",
        "error-container": "#93000a",
        "on-error-container": "#ffdad6",
        "outline-variant": "#5b403e"
      },
      fontFamily: {
        "sans": ["Inter", "sans-serif"],
        "mono": ["JetBrains Mono", "monospace"]
      }
    },
  },
  plugins: [],
}
