import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Replace 'games-misc' with your repository name
export default defineConfig({
  plugins: [react()],
  base: '/games-misc/',
})
