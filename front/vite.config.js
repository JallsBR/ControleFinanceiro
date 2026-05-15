import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

/** URL oficial do app em desenvolvimento (WSL2 + browser no Windows). */
const DEV_URL = 'http://localhost:2488/'

// https://vite.dev/config/
export default defineConfig({
  server: {
    // Só 127.0.0.1 — WSL2 encaminha localhost:2488 do Windows para aqui (evita abrir IP 172.x).
    host: 'localhost',
    port: 2488,
    strictPort: true,
    open: DEV_URL,
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
