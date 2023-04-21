import { toSocket, WebSocketMessageReader, WebSocketMessageWriter } from "vscode-ws-jsonrpc";
import normalizeUrl from "normalize-url";
import { CloseAction, ErrorAction, MonacoLanguageClient, MonacoServices } from "monaco-languageclient";

export function connectToLanguageServers(monaco)
{
  // register Monaco languages
  // Note: the id must match the language server proxy path,
  // and it must also match the id that is assigned in Python.
  const languages = [
    // {
    //   id: "typescript",
    //   extensions: [".ts"],
    //   aliases: ["TypeScript", "ts", "TS", "Typescript", "typescript"],
    // },
    // {
    //   id: "moose",
    //   extensions: [".i"],
    //   aliases: ["MOOSE", "Moose", "moose"],
    // },
    // {
    //   id: "cmake",
    //   extensions: [".cmake", "CMakeLists.txt"],
    //   aliases: ["CMAKE", "CMake", "cmake"],
    // },
    // The C++ language servers cause us some issues
    // {
    //   id: "cpp",
    //   extensions: [".cpp", ".cxx", ".C", ".CC", ".cc"],
    //   aliases: ["C++", "c++", "cpp", "cxx"],
    // },
    {
      id: "python",
      extensions: [".py"],
      aliases: ["Python", "python", "py"],
    },
  ]
  languages.forEach(item => {
    monaco.languages.register(item);
  });

  // Install monaco services
  MonacoServices.install(monaco);

  // These already have language servers built-in, so we should
  // skip them.
  const skipServerLanguages = [
    "typescript",
  ];

  // Create web sockets for each language
  const baseUrl = "ws://localhost:4200";
  languages.forEach(item => {
    if (skipServerLanguages.includes(item.id)) {
      return;
    }

    const url = createWsUrl('localhost', 4200, `/${item.id}`);
    const webSocket = new WebSocket(url);
    webSocket.onopen = () => onopen(webSocket, item.id);
  });
};

function onopen(webSocket, type) {
  const socket = toSocket(webSocket);
  const reader = new WebSocketMessageReader(socket);
  const writer = new WebSocketMessageWriter(socket);

  const languageClient = createLanguageClient({
    reader: reader,
    writer: writer,
  }, type);

  languageClient.start();
  reader.onClose(() => languageClient.stop());
};

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
};

function createWsUrl(hostname, port, path) {
  const protocol = location.protocol === 'https:' ? 'wss' : 'ws';
  return normalizeUrl(`${protocol}://${hostname}:${port}${path}`);
};
