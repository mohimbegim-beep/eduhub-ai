/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./static/**/*.html",
    "./static/**/*.js",
    "./templates/**/*.html"
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        heading: ['Montserrat', 'sans-serif'],
      },
      colors: {
        main: '#030712',
        surface: 'rgba(11, 15, 25, 0.65)',
      }
    }
  },
  plugins: [],
}
