/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#5B5FF9',
        'primary-hover': '#4B4FE9',
      }
    },
  },
  plugins: [],
}




