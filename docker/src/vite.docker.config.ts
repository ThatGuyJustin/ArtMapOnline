import { defineConfig, mergeConfig } from "vite";
import baseConfig from "./vite.config";

export default mergeConfig(baseConfig, defineConfig({
  server: {
    host: "0.0.0.0",
    port: 8001,
    strictPort: true,
    watch: {
      usePolling: true,
      interval: 1000,
      pollInterval: 1000,
    },
    ws: {
      clientPort: 8000,
    },
  },
}));
