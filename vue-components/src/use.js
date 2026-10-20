import components from "./components";
import { MonacoEnvironment } from "./utils/monacoEnv";

export function install(Vue, options) {
  if (options?.serveDirectory) {
    MonacoEnvironment.setServeDirectory(options.serveDirectory);
  }
  Object.keys(components).forEach((name) => {
    Vue.component(name, components[name]);
  });
}
