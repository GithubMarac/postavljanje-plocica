import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react' // 👈 Fixed this line

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  base: '/postavljanje-plocica/', 
})