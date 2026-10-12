// Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
// SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: "../static",
    emptyOutDir: true,
  },
  server: {
    proxy: {
      "/api": "http://127.0.0.1:9000",
    },
  },
});
