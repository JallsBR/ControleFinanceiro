import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  server: {
    // Só 127.0.0.1: o terminal mostra apenas Local (localhost), sem URLs de rede.
    // Porta alinhada com o URL local habitual (evita abrir :2486 quando o Vite só serve :2487).
    host: 'localhost',
    port: 2487,
    strictPort: true,
  },
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
})
