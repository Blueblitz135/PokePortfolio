/** Configure React builds, browser tests, and development proxies to FastAPI. */
import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

// Allow alternate backend hosts in development while defaulting to local FastAPI.
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
  test: {
    environment: "jsdom",
  },
});
