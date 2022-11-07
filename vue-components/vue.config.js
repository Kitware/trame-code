const path = require("path");
const DST_PATH = "../trame_code/module/serve";
const MonacoWebpackPlugin = require("monaco-editor-webpack-plugin");
const { defineConfig } = require("@vue/cli-service");

module.exports = defineConfig({
  transpileDependencies: true,
  outputDir: path.resolve(__dirname, DST_PATH),
  configureWebpack: {
    plugins: [new MonacoWebpackPlugin()],
  },
});
