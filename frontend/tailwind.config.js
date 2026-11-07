/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#0B0E14',
        panel: '#151921',
        panelBorder: '#222834',
        accentCyan: '#00F0FF',
        bullishGreen: '#00E676',
        bearishRed: '#FF3B30',
        warningGold: '#FFB300',
        vetoMagenta: '#D500F9',
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Courier New', 'monospace'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
