import { defineConfig } from 'vite';
import monacoEditorPlugin from 'vite-plugin-monaco-editor';
const DST_PATH = "../trame_code/module/serve";

export default defineConfig({
  plugins: [
    monacoEditorPlugin({globalAPI: true}),
  ],
  base: "./",
  build: {
    lib: {
      entry: "./src/use.js",
      name: "trame_code",
      format: "umd",
      fileName: "trame-code",
    },
    rollupOptions: {
      external: ["vue"],
      output: {
        globals: {
          vue: "Vue",
        },
      },
    },
    outDir: DST_PATH,
    assetsDir: ".",
  },
});