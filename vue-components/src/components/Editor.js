import "../utils/monacoEnv";
import { listen } from "vscode-ws-jsonrpc";
import { WSLinkWebSocket } from "../utils/wslink";
import {
  SimpleLanguageInfoProvider,
  registerLanguages,
} from "../utils/textmate";

import {
  MonacoServices,
  MonacoLanguageClient,
  createConnection,
  CloseAction,
  ErrorAction,
} from "monaco-languageclient";

import * as monaco from "monaco-editor";

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

    if (this.languageServers?.length) {
      const masterWS = WSLinkWebSocket(this.trame);
      MonacoServices.install(monaco);

      // Create LanguageClient per language server
      for (let i = 0; i < this.languageServers.length; i++) {
        const langId = this.languageServers[i];
        const webSocket = masterWS.createLanguageWS(langId);
        listen({
          webSocket,
          onConnection: (connection) => {
            const languageClient = new MonacoLanguageClient({
              name: `lang-client-${langId}`,
              clientOptions: {
                documentSelector: [langId],
                errorHandler: {
                  error: () => ErrorAction.Continue,
                  closed: () => CloseAction.Restart,
                },
              },

              connectionProvider: {
                get(errorHandler, closeHandler) {
                  return Promise.resolve(
                    createConnection(connection, errorHandler, closeHandler)
                  );
                },
              },
            });
            const disposable = languageClient.start();

            connection.onClose(function () {
              return disposable.dispose();
            });

            connection.onError(function (error) {
              console.log(error);
            });
          },
        });
      }

      masterWS.connectToLangServer();
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
