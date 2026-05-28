import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  cacheDir: process.env.VITE_CACHE_DIR || "node_modules/.vite",
  server: {
    port: 5173,
    proxy: {
      "/ecommerce": {
        target: process.env.VITE_API_PROXY_TARGET || process.env.VITE_API_URL || "http://localhost:4566",
        changeOrigin: true,
      },
      "/products": {
        target: process.env.VITE_API_PROXY_TARGET || process.env.VITE_API_URL || "http://localhost:4566",
        changeOrigin: true,
      },
    },
  },
});
