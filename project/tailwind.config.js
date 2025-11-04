/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './apps/**/templates/**/*.html',
    './node_modules/flowbite/**/*.js',
    './apps/**/*.py',
    './**/*.html',
    './**/*.py',
  ],
  theme: {
    extend: {
      spacing: {
        '22': '5.5rem',
      },
      zIndex: {
        '35': 35,
      },
      colors: {
        'primary': {"50":"#eff6ff","100":"#dbeafe","200":"#bfdbfe","300":"#93c5fd","400":"#60a5fa","500":"#3b82f6","600":"#2563eb","700":"#1d4ed8","800":"#1e40af","900":"#1e3a8a","950":"#172554"},
        'fcfcfd': "#fcfcfd",
        '2b3544': "#2b3544"
      }
    },
  },
  plugins: [
    require('flowbite/plugin')
  ],
}