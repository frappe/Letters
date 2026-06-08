import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import path from "path";

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "src"),
    },
  },
  build: {
    outDir: "../letters/public/js",
    emptyOutDir: true,
    rollupOptions: {
      input: "src/main.js",
      output: {
        entryFileNames: "letters-builder.js",
        assetFileNames: "letters-builder.[ext]",
      },
    },
  },
  server: {
    port: 8080,
    proxy: {
      "/api": "http://localhost:8000",
    },
  },
});
