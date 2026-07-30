import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  root: path.resolve(__dirname),
  build: {
    outDir: path.resolve(__dirname, 'dist'),
    emptyOutDir: true
  },
  plugins: [react()],
  server: {
    proxy: {
      '/odata': 'http://localhost:4004',
      '/api': 'http://localhost:4004'
    }
  }
})
