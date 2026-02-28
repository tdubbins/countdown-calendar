import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, './src')
    }
  },
  server: {
    port: 8080
  },
  test: {
    globals: true,
    environment: 'jsdom',
    exclude: ['tests/e2e/**', 'node_modules/**']
  }
})
