import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0', // Listen on all interfaces for Render
    port: process.env.PORT || 4010, // Use PORT env var or default to 4010
    open: false, // Don't auto-open browser in production
    strictPort: false,
    hmr: {
      clientPort: process.env.PORT || 4010,
    },
  },
  preview: {
    host: '0.0.0.0', // For production preview
    port: process.env.PORT || 4010,
    strictPort: false,
  },
  build: {
    outDir: 'dist',
  },
}); 