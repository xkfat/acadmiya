/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#3C50E0', // Bleu TailAdmin
        secondary: '#80CAEE',
        dark: '#1C2434',    // Bleu nuit Sidebar
        graybody: '#F1F5F9', // Gris clair Fond
      }
    },
  },
  plugins: [],
}