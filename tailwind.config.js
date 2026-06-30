/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    // Scanne les templates qui sont dans ton dossier config si tu en as
    "./config/templates/**/*.html",
    // Scanne tous les autres dossiers templates du projet (racine et sous-apps)
    "./config/templates/**/*.html",
    "./config/templates/**/*.html",
    "./config/templates/*.html",
    // Scanne tes fichiers JS pour Alpine.js
    "./**/static/**/*.js",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}