import wasmURL from "vscode-oniguruma/release/onig.wasm?url";
import {
  createOnigScanner,
  createOnigString,
  loadWASM,
} from "vscode-oniguruma";

export const onigLib = new Promise((resolve) => {
  fetch(wasmURL).then((response) => {
    loadWASM(response).then(() => {
      resolve({
        createOnigScanner,
        createOnigString,
      });
    });
  });
});
