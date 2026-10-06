import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// In dev, /api, /verify and /remove are proxied to Django so the app can use
// relative URLs. In production Django serves the built app itself.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://127.0.0.1:8000',
    },
  },
})
