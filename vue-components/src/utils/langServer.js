import { MonacoLanguageClient } from "monaco-languageclient";
import { CloseAction, ErrorAction } from "vscode-languageclient";

export function createLanguageClient(langIO) {
  langIO.client = new MonacoLanguageClient({
    name: langIO.language,
    clientOptions: {
      documentSelector: [langIO.language],
      errorHandler: {
        error: () => ({ action: ErrorAction.Continue }),
        closed: () => ({ action: CloseAction.DoNotRestart }),
      },
    },
    connectionProvider: {
      get() {
        return Promise.resolve({ reader: langIO, writer: langIO });
      },
    },
  });
  langIO.client.start();
  return langIO.client;
}
