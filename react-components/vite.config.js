import { fileURLToPath, URL } from "node:url";

import react from "@vitejs/plugin-react";
import monacoPlugin from "vite-plugin-monaco-editor";

const monacoEditorPlugin = monacoPlugin.default || monacoPlugin;

export default {
  base: "./",
  plugins: [react(), monacoEditorPlugin({ globalAPI: true })],
  define: {
    "process.env.NODE_ENV": JSON.stringify("production"),
  },
  resolve: {
    alias: {
      // utils/ and themes/ are client-agnostic and shared with vue-components
      // rather than duplicated.
      "@shared": fileURLToPath(
        new URL("../vue-components/src", import.meta.url),
      ),
    },
  },
  build: {
    lib: {
      entry: "./src/main.ts",
      name: "trame_code_react",
      formats: ["umd"],
      fileName: "trame-code-react",
    },
    // the vue build owns this directory and runs with --emptyOutDir
    emptyOutDir: false,
    rollupOptions: {
      external: ["react", "react-dom"],
      output: {
        globals: {
          react: "React",
          "react-dom": "ReactDOM",
        },
      },
    },
    outDir: "../src/trame_code/module/serve",
    assetsDir: ".",
  },
};
