import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    // Send /api requests to the FastAPI backend, so we don't need CORS
    proxy: {
      '/api': 'http://127.0.0.1:8000',
    },
  },
})
