// Reference implementation for language-server:
// => https://github.com/TypeFox/monaco-languageclient/blob/main/packages/examples/main/src/client/main.ts

import * as monaco from "monaco-editor";
import { MonacoServices } from "monaco-languageclient";
import { StandaloneServices } from "vscode/services";

import "../utils/monacoEnv";
import { WSLinkWebSocket } from "../utils/wslink";
import { createLanguageClient } from "../utils/langServer";
import { LanguageProvider, registerLanguages } from "../utils/textmate";

StandaloneServices.initialize();

export default {
  name: "VSEditor",
  inject: ["trame"],
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
    textmate: {
      type: Object,
    },
    languageServers: {
      type: Array,
      default: () => [],
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
      this.provider = new LanguageProvider({
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

    if (this.languageServers?.length) {
      MonacoServices.install();
      const masterWS = new WSLinkWebSocket(this.trame);

      // Create LanguageClient per language server
      for (let i = 0; i < this.languageServers.length; i++) {
        const langId = this.languageServers[i];
        const langIO = masterWS.createLanguageIO(langId);
        createLanguageClient(langIO);
      }
    }

    this.editor = monaco.editor.create(this.$el, {
      value: this.value,
      language: this.language,
      theme: this.theme,
      ...this.options,
    });

    if (provider) {
      provider.injectCSS();
    }

    this.editor.onDidChangeModelContent(() =>
      this.$emit("input", this.editor.getValue())
    );
  },
  beforeUnmount() {
    this.editor.dispose();
  },
  template: `<div style="width: 100%;height: 100%;padding: 0;margin: 0;"></div>`,
};
