import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const backendTarget =
  process.env.BACKEND_PROXY_TARGET ?? "http://localhost:8000";

export default defineConfig({
  appType: "spa",
  plugins: [react()],
  server: {
    proxy: {
      "/api": backendTarget,
      "/static": backendTarget,
      "/uploads": backendTarget,
    },
  },
});
