/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        cicor: {
          primary: '#1E40AF',   // Azul corporativo (navbar)
          light:   '#DBEAFE',   // Azul claro
          dark:    '#0C1E4D',   // Azul oscuro
        },
        modules: {
          commercial:  '#10B981', // Verde
          inventory:   '#3B82F6', // Azul
          accounting:  '#EF4444', // Rojo
          operations:  '#F97316', // Naranja
          hr:          '#A855F7', // Púrpura
        },
      },
      fontFamily: {
        sans:    ['Sora', 'sans-serif'],
        display: ['Lexend', 'sans-serif'],
        mono:    ['JetBrains Mono', 'monospace'],
      },
      animation: {
        'fade-in':        'fadeIn 0.3s ease-out',
        'slide-up':       'slideUp 0.35s cubic-bezier(0.16, 1, 0.3, 1)',
        'nav-slide-down': 'navSlideDown 0.25s cubic-bezier(0.16, 1, 0.3, 1) both',
        'pulse-dot':      'pulseDot 2s infinite',
      },
      keyframes: {
        fadeIn: {
          '0%':   { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%':   { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        navSlideDown: {
          '0%':   { opacity: '0', transform: 'translateY(-8px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        pulseDot: {
          '0%, 100%': { opacity: '1' },
          '50%':      { opacity: '0.4' },
        },
      },
      boxShadow: {
        'module': '0 4px 20px -2px rgba(0,0,0,0.12)',
        'card':   '0 1px 4px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.06)',
      },
    },
  },
  plugins: [],
}
