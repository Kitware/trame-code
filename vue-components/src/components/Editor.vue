<template>
  <div class="container"></div>
</template>

<script>
import * as monaco from "monaco-editor";

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
        language: "python",
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
      ...this.options,
    });

    this.editor.onDidChangeModelContent(() =>
      this.$emit("input", this.editor.getValue())
    );
  },
  beforeDestroy() {
    this.editor.dispose();
  },
};
</script>

<style scoped>
.container {
  width: 100%;
  height: 100%;
  padding: 0;
  margin: 0;
}
</style>
