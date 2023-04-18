import monacoEditorPlugin from 'vite-plugin-monaco-editor';

export default {
  plugins: [
    monacoEditorPlugin({globalAPI: true}),
  ],
  base: "./",
  build: {
    lib: {
      entry: "./src/use.js",
      name: "trame_code",
      formats: ["umd"],
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
    outDir: "../trame_code/module/serve",
    assetsDir: ".",
    // sourcemap: true,
  },
};