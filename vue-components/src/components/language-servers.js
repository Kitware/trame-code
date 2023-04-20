import {
  toSocket,
  WebSocketMessageReader,
  WebSocketMessageWriter,
} from "vscode-ws-jsonrpc";
import normalizeUrl from "normalize-url";
import {
  CloseAction,
  ErrorAction,
  MonacoLanguageClient,
  // MonacoServices,
} from "monaco-languageclient";

// These already have language servers built-in, so we should
// skip them.
const skipServerLanguages = ["typescript"];

const registeredLanguages = [];

export function connectToLanguageServer(language, monaco) {
  if (registeredLanguages.includes(language.id)) {
    console.error(
      "Language server with id:",
      language.id,
      "has already been registered!"
    );
    return;
  }

  monaco.languages.register(language);
  registeredLanguages.push(language.id);

  if (skipServerLanguages.includes(language.id)) {
    // Skip this language if we need to
    return;
  }

  const url = createWsUrl("localhost", 4200, `/${language.id}`);
  const webSocket = new WebSocket(url);
  webSocket.onopen = () => onopen(webSocket, language.id);
}

function onopen(webSocket, type) {
  const socket = toSocket(webSocket);
  const reader = new WebSocketMessageReader(socket);
  const writer = new WebSocketMessageWriter(socket);

  const languageClient = createLanguageClient(
    {
      reader: reader,
      writer: writer,
    },
    type
  );

  languageClient.start();
  reader.onClose(() => languageClient.stop());
}

function createLanguageClient(transports, type) {
  return new MonacoLanguageClient({
    id: type,
    name: type,
    clientOptions: {
      // use a language id as a document selector
      documentSelector: [type],
      // disable the default error handler
      errorHandler: {
        error: () => ErrorAction.Continue,
        closed: () => CloseAction.DoNotRestart,
      },
    },
    // create a language client connection from the JSON RPC connection on demand
    connectionProvider: {
      get: () => Promise.resolve(transports),
    },
  });
}

function createWsUrl(hostname, port, path) {
  const protocol = location.protocol === "https:" ? "wss" : "ws";
  return normalizeUrl(`${protocol}://${hostname}:${port}${path}`);
}
