import "../utils/monacoEnv";
import {
  SimpleLanguageInfoProvider,
  registerLanguages,
} from "../utils/textmate";

import * as monaco from "monaco-editor";

// Map a normalized completion-kind string to a Monaco CompletionItemKind.
function completionItemKind(kind) {
  const K = monaco.languages.CompletionItemKind;
  const map = {
    function: K.Function,
    method: K.Method,
    class: K.Class,
    instance: K.Variable,
    variable: K.Variable,
    module: K.Module,
    keyword: K.Keyword,
    statement: K.Snippet,
    param: K.Variable,
    property: K.Property,
    field: K.Field,
    constant: K.Constant,
    path: K.File,
  };
  return map[kind] || K.Text;
}

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
    completion: {
      type: String,
    },
    hover: {
      type: String,
    },
    completionTriggerCharacters: {
      type: Array,
      default: () => ["."],
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
        this.registerLanguageProviders();
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
    disposeLanguageProviders() {
      if (this._completionProvider) {
        this._completionProvider.dispose();
        this._completionProvider = null;
      }
      if (this._hoverProvider) {
        this._hoverProvider.dispose();
        this._hoverProvider = null;
      }
    },
    registerLanguageProviders() {
      // Bridge Monaco language features to a Python callback exposed as a trame
      // trigger. The consumer sets the `completion` / `hover` props to trigger
      // names and registers the matching server triggers; no client JS needed.
      // Re-registering is safe: any previous registration is disposed first.
      this.disposeLanguageProviders();
      if (!this.completion && !this.hover) {
        return;
      }
      // Monaco only runs language features for a registered language. When no
      // textmate grammar registered it (e.g. a plain language= editor), register
      // the id here so completion/hover providers are actually consulted.
      const known = monaco.languages
        .getLanguages()
        .some((l) => l.id === this.language);
      if (this.language && !known) {
        monaco.languages.register({ id: this.language });
      }
      const self = this;
      if (this.completion) {
        this._completionProvider =
          monaco.languages.registerCompletionItemProvider(this.language, {
            triggerCharacters: this.completionTriggerCharacters,
            async provideCompletionItems(model, position, context, token) {
              if (!window.trame || !window.trame.trigger) {
                return { suggestions: [] };
              }
              let items = [];
              try {
                items = await window.trame.trigger(self.completion, [
                  model.getValue(),
                  position.lineNumber,
                  position.column - 1,
                ]);
              } catch (e) {
                items = [];
              }
              if (token && token.isCancellationRequested) {
                return { suggestions: [] };
              }
              if (!items) items = [];
              const word = model.getWordUntilPosition(position);
              const range = {
                startLineNumber: position.lineNumber,
                endLineNumber: position.lineNumber,
                startColumn: word.startColumn,
                endColumn: word.endColumn,
              };
              return {
                suggestions: items.map((it) => ({
                  label: it.label,
                  kind: completionItemKind(it.kind),
                  detail: it.detail || "",
                  documentation: it.documentation || undefined,
                  insertText: it.insertText || it.label,
                  range,
                })),
              };
            },
          });
      }
      if (this.hover) {
        this._hoverProvider = monaco.languages.registerHoverProvider(
          this.language,
          {
            async provideHover(model, position, token) {
              if (!window.trame || !window.trame.trigger) {
                return null;
              }
              let res = null;
              try {
                res = await window.trame.trigger(self.hover, [
                  model.getValue(),
                  position.lineNumber,
                  position.column - 1,
                ]);
              } catch (e) {
                res = null;
              }
              if (token && token.isCancellationRequested) {
                return null;
              }
              if (!res) return null;
              // Accept a markdown string, an array of strings, or { contents: [...] }.
              let contents = [];
              if (typeof res === "string") {
                contents = [{ value: res }];
              } else if (Array.isArray(res)) {
                contents = res.map((v) => ({ value: v }));
              } else if (res.contents) {
                contents = res.contents.map((v) => ({ value: v }));
              }
              if (!contents.length) return null;
              const word = model.getWordAtPosition(position);
              const range = word
                ? {
                    startLineNumber: position.lineNumber,
                    endLineNumber: position.lineNumber,
                    startColumn: word.startColumn,
                    endColumn: word.endColumn,
                  }
                : undefined;
              return { range, contents };
            },
          }
        );
      }
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

    this.registerLanguageProviders();
  },
  beforeUnmount() {
    this.disposeLanguageProviders();
    this.editor.dispose();
  },
  template: `<div style="width: 100%;height: 100%;padding: 0;margin: 0;"></div>`,
};
