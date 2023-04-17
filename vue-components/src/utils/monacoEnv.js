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

function DEFAULT_URL_MAPPER(v) {
  return `__trame_code/monacoeditorwork/${v}.worker.bundle.js`;
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

self.MonacoEnvironment = {
  updateLabelMapper,
  updateUrlMapper,
  getWorker,
};
