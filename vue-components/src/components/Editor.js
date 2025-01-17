import "../utils/monacoEnv";
import {
  SimpleLanguageInfoProvider,
  registerLanguages,
} from "../utils/textmate";

import * as monaco from "monaco-editor";

export default {
  name: "VSEditor",
  props: {
    modelValue: {
      type: String,
    },
    value: {
      type: String,
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
    textmate: {
      type: Object,
    },
  },
  watch: {
    modelValue(v) {
      if (this.editor && v !== undefined && this.editor.getValue() !== v) {
        this.editor.setValue(v);
      }
    },
    value(v) {
      if (this.editor && v !== undefined && this.editor.getValue() !== v) {
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
      if (this.provider) {
        this.provider.updateTheme(theme);
      }
    },
    textmate(config) {
      if (config) {
        const { languages, grammars, configs } = config;
        this.registerTextmateLanguageDefinitions(
          languages,
          grammars,
          configs,
          true
        );
      }
    },
  },
  methods: {
    registerTextmateLanguageDefinitions(languages, grammars, configs, inject) {
      this.provider = new SimpleLanguageInfoProvider({
        monaco,
        grammars,
        configs,
        theme: this.theme,
      });

      registerLanguages(
        languages,
        (v) => this.provider.fetchLanguageInfo(v),
        monaco
      );
      if (inject) {
        this.provider.injectCSS();
      }

      return this.provider;
    },
  },
  mounted() {
    let provider = null;
    if (this.textmate) {
      provider = this.registerTextmateLanguageDefinitions(
        this.textmate.languages,
        this.textmate.grammars,
        this.textmate.configs,
        false
      );
    }

    this.editor = monaco.editor.create(this.$el, {
      value: this.modelValue || this.value,
      language: this.language,
      theme: this.theme,
      ...this.options,
    });

    if (provider) {
      provider.injectCSS();
    }

    this.lastValue = this.editor.getValue();

    this.editor.onDidChangeModelContent(() => {
      const newValue = this.editor.getValue();
      if (this.lastValue === newValue) {
        return;
      }
      this.lastValue = newValue;
      this.$emit("update:modelValue", newValue);
      this.$emit("input", newValue);
    });
  },
  beforeUnmount() {
    this.editor.dispose();
  },
  template: `<div style="width: 100%;height: 100%;padding: 0;margin: 0;"></div>`,
};
