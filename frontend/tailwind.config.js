/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        emergency: {
          50: '#eef4fb',
          100: '#d7e6f5',
          500: '#2f6fb0',
          600: '#245a91',
          700: '#1b3a5c',
          900: '#102438',
        },
        alert: {
          high: '#c0392b',
          medium: '#d68910',
          low: '#1e8449',
        },
      },
    },
  },
  plugins: [],
}
