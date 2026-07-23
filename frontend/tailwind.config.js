/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f0f4f9',
          100: '#e1e9f2',
          200: '#c2d2e5',
          300: '#94b2d3',
          400: '#5f8cb9',
          500: '#3f709d',
          600: '#315780',
          700: '#284668',
          800: '#233d59',
          900: '#1b2c40',
          950: '#111c2a',
        },
        navy: {
          900: '#0B132B',
          950: '#050A18',
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        display: ['Outfit', 'sans-serif'],
      },
      boxShadow: {
        'premium': '0 4px 20px -2px rgba(17, 28, 42, 0.08), 0 2px 8px -1px rgba(17, 28, 42, 0.04)',
        'premium-hover': '0 10px 25px -3px rgba(17, 28, 42, 0.12), 0 4px 12px -2px rgba(17, 28, 42, 0.06)',
        'glass': '0 8px 32px 0 rgba(0, 0, 0, 0.08)',
      },
      backdropBlur: {
        'xs': '2px',
      }
    },
  },
  plugins: [],
}
