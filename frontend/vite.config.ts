import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// GitHub project pages serve from /<repo>/ — set base accordingly.
// Override with CERD_BASE when deploying elsewhere.
const base = process.env.CERD_BASE ?? "/cerd/";

export default defineConfig({
  base,
  plugins: [react()],
  build: { outDir: "dist", sourcemap: false },
});
