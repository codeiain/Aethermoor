import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // Strip /api prefix before forwarding to gateway — gateway listens at /auth/*, /players/*, /world/*
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        rewrite: (path: string) => path.replace(/^\/api/, ""),
      },
    },
  },
  build: {
    outDir: "dist",
    sourcemap: false,
    // Phaser is large — allow up to 4MB chunk without warning
    chunkSizeWarningLimit: 4096,
  },
});
