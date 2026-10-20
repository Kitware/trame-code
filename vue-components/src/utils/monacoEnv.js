import {
  getTextMateTheme,
  registerTextMateAlias,
  registerTextMateTheme,
} from "../themes";

const URL_MAPPER = {};
const LABEL_MAPPER = {
  json: "json",
  css: "css",
  scss: "css",
  less: "css",
  html: "html",
  handlebars: "html",
  razor: "html",
  typescript: "ts",
  javascript: "ts",
  js: "ts",
};

// The server serves the bundle from a versioned directory and tells the client
// which one: through the plugin options for vue, a widget prop for react.
let workerBaseUrl = "";

function setServeDirectory(serveDirectory) {
  workerBaseUrl = `${serveDirectory}/monacoeditorwork/`;
}

function DEFAULT_URL_MAPPER(v) {
  return `${workerBaseUrl}${v}.worker.bundle.js`;
}

function getWorker(_workerId, label) {
  const workerType = LABEL_MAPPER[label] || "editor";
  const urlMapper = URL_MAPPER[label] || DEFAULT_URL_MAPPER;
  return new Worker(urlMapper(workerType), { name: label, type: "module" });
}

function updateLabelMapper(key, value) {
  LABEL_MAPPER[key] = value;
}

function updateUrlMapper(key, value) {
  URL_MAPPER[key] = value;
}

export const MonacoEnvironment = {
  setServeDirectory,
  updateLabelMapper,
  updateUrlMapper,
  getWorker,
  // TextMate helper
  getTextMateTheme,
  registerTextMateTheme,
  registerTextMateAlias,
};

// Expose publicly
self.MonacoEnvironment = MonacoEnvironment;
