/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#0f172a', // slate-900 for dark navy/charcoal
        card: '#1e293b', // slate-800 for lighter cards
        primary: '#4f46e5', // indigo-600
        primaryHover: '#4338ca', // indigo-700
        success: '#10b981', // emerald-500
        warning: '#f59e0b', // amber-500
        error: '#ef4444', // red-500
        textMain: '#f8fafc', // slate-50
        textMuted: '#94a3b8', // slate-400
        border: '#334155', // slate-700
      },
    },
  },
  plugins: [],
}
