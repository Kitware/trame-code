import onigWasm from "vscode-oniguruma/release/onig.wasm?init";
import {
  createOnigScanner,
  createOnigString,
  loadWASM,
} from "vscode-oniguruma";

await loadWASM({ instantiator: onigWasm, print: console.log });

export const onigLib = Promise.resolve({
  createOnigScanner,
  createOnigString,
});
