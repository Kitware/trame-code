import * as monaco from "monaco-editor";

import { connectToLanguageServers } from "./language-servers";

// vscode must be imported before starting the first editor
// see: https://github.com/TypeFox/monaco-languageclient/issues/412#issuecomment-1227347426
import "vscode";

export default {
  name: "VSEditor",
  props: {
    value: {
      type: String,
      default: "",
    },
    options: {
      type: Object,
      default: () => ({
        language: "moose",
        lineNumbers: "on",
        theme: "vs-dark",
      }),
    },
    language: {
      type: String,
      default: "plaintext",
    },
    theme: {
      type: String,
      default: "vs-dark",
    },
  },
  watch: {
    value(v) {
      if (this.editor) {
        console.log("value changed");
        this.editor.setValue(v);
      }
    },
    options(newOptions) {
      if (this.editor) {
        this.editor.updateOptions(newOptions);
      }
    },
    language(lang) {
      if (this.editor) {
        monaco.editor.setModelLanguage(this.editor.getModel(), lang);
      }
    },
    theme(theme) {
      if (this.editor) {
        this.editor.updateOptions({ theme });
      }
    },
  },
  methods: {},
  mounted() {
    this.editor = monaco.editor.create(this.$el, {
      value: this.value,
      language: this.language,
      theme: this.theme,
      model: monaco.editor.createModel(
        this.value,
        this.language,
      ),
      automaticLayout: true,
      ...this.options,
    });

    this.editor.onDidChangeModelContent(() =>
      this.$emit("input", this.editor.getValue())
    );

    // Connect to the language servers
    connectToLanguageServers(monaco);
  },
  beforeDestroy() {
    this.editor.dispose();
  },
};
