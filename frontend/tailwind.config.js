/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        instagram: {
          purple: '#833ab4',
          pink: '#fd1d1d',
          yellow: '#fcb045',
          dark: '#0f0f11',
          card: '#18181b',
          border: '#27272a'
        }
      }
    },
  },
  plugins: [],
}
