import type { ComponentType } from "react";

import Editor from "./components/Editor";

interface Registry {
  register(tag: string, component: ComponentType<any>): void;
}

type RegisterTag = (tag: string, component: ComponentType<any>) => void;

export function install(registry: Registry | RegisterTag) {
  const register: RegisterTag =
    typeof registry === "function"
      ? registry
      : (tag, component) => registry.register(tag, component);

  register("vs-editor", Editor);
}
