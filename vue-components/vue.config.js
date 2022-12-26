const path = require("path");
const DST_PATH = "../trame_code/module/serve";
const MonacoWebpackPlugin = require("monaco-editor-webpack-plugin");
const { defineConfig } = require("@vue/cli-service");
const NodePolyfillPlugin = require("node-polyfill-webpack-plugin")

module.exports = defineConfig({
  transpileDependencies: true,
  outputDir: path.resolve(__dirname, DST_PATH),
  configureWebpack: {
    plugins: [
      new MonacoWebpackPlugin(),
      new NodePolyfillPlugin(),
    ],
  },
  lintOnSave: false,
});
