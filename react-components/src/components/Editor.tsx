import { MonacoEnvironment } from "@shared/utils/monacoEnv";
import {
  SimpleLanguageInfoProvider,
  registerLanguages,
} from "@shared/utils/textmate";

import * as monaco from "monaco-editor";
import { useEffect, useRef } from "react";

type AnyProps = Record<string, any>;

interface EditorProps {
  value?: string;
  options?: monaco.editor.IStandaloneEditorConstructionOptions;
  language?: string;
  theme?: string;
  textmate?: AnyProps;
  completion?: string;
  hover?: string;
  completionTriggerCharacters?: string[];
  serveDirectory?: string;
  onChange?: (value: string) => void;
}

function completionItemKind(kind?: string) {
  const K = monaco.languages.CompletionItemKind;
  const map: Record<string, monaco.languages.CompletionItemKind> = {
    function: K.Function,
    method: K.Method,
    class: K.Class,
    instance: K.Variable,
    variable: K.Variable,
    module: K.Module,
    keyword: K.Keyword,
    statement: K.Snippet,
    param: K.Variable,
    property: K.Property,
    field: K.Field,
    constant: K.Constant,
    path: K.File,
  };
  return (kind && map[kind]) || K.Text;
}

const DEFAULT_OPTIONS = {
  language: "python",
  lineNumbers: "on",
  theme: "vs-dark",
} as monaco.editor.IStandaloneEditorConstructionOptions;

export default function Editor({
  value,
  options = DEFAULT_OPTIONS,
  language = "plaintext",
  theme = "vs-dark",
  textmate,
  completion,
  hover,
  completionTriggerCharacters = ["."],
  serveDirectory,
  onChange,
}: EditorProps) {
  if (serveDirectory) {
    MonacoEnvironment.setServeDirectory(serveDirectory);
  }
  const containerRef = useRef<HTMLDivElement | null>(null);
  const editorRef = useRef<monaco.editor.IStandaloneCodeEditor | null>(null);
  const providerRef = useRef<any>(null);
  const languageProvidersRef = useRef<{
    completion: monaco.IDisposable | null;
    hover: monaco.IDisposable | null;
  }>({ completion: null, hover: null });
  const lastValueRef = useRef<string | undefined>(value);

  // Providers register once per language but read the current trigger names
  // and handlers on every invocation.
  const latest = useRef<EditorProps>({});
  latest.current = { completion, hover, completionTriggerCharacters, onChange };

  function registerTextmate(config: AnyProps, inject: boolean) {
    const { languages, grammars, configs } = config;
    providerRef.current = new SimpleLanguageInfoProvider({
      monaco,
      grammars,
      configs,
      theme,
    });
    registerLanguages(
      languages,
      (v: string) => providerRef.current.fetchLanguageInfo(v),
      monaco,
    );
    if (inject) {
      providerRef.current.injectCSS();
    }
    return providerRef.current;
  }

  function disposeLanguageProviders() {
    const providers = languageProvidersRef.current;
    providers.completion?.dispose();
    providers.hover?.dispose();
    languageProvidersRef.current = { completion: null, hover: null };
  }

  function registerLanguageProviders(lang: string) {
    disposeLanguageProviders();
    if (!latest.current.completion && !latest.current.hover) {
      return;
    }
    const known = monaco.languages.getLanguages().some((l) => l.id === lang);
    if (lang && !known) {
      monaco.languages.register({ id: lang });
    }

    if (latest.current.completion) {
      languageProvidersRef.current.completion =
        monaco.languages.registerCompletionItemProvider(lang, {
          triggerCharacters: latest.current.completionTriggerCharacters,
          async provideCompletionItems(model, position, _context, token) {
            if (!window.trame?.trigger) {
              return { suggestions: [] };
            }
            let items: AnyProps[] = [];
            try {
              items = await window.trame.trigger(latest.current.completion, [
                model.getValue(),
                position.lineNumber,
                position.column - 1,
              ]);
            } catch {
              items = [];
            }
            if (token?.isCancellationRequested) {
              return { suggestions: [] };
            }
            if (!items) items = [];
            const word = model.getWordUntilPosition(position);
            const range = {
              startLineNumber: position.lineNumber,
              endLineNumber: position.lineNumber,
              startColumn: word.startColumn,
              endColumn: word.endColumn,
            };
            return {
              suggestions: items.map((it) => ({
                label: it.label,
                kind: completionItemKind(it.kind),
                detail: it.detail || "",
                documentation: it.documentation || undefined,
                insertText: it.insertText || it.label,
                range,
              })),
            };
          },
        });
    }

    if (latest.current.hover) {
      languageProvidersRef.current.hover =
        monaco.languages.registerHoverProvider(lang, {
          async provideHover(model, position, token) {
            if (!window.trame?.trigger) {
              return null;
            }
            let res: any = null;
            try {
              res = await window.trame.trigger(latest.current.hover, [
                model.getValue(),
                position.lineNumber,
                position.column - 1,
              ]);
            } catch {
              res = null;
            }
            if (token?.isCancellationRequested) {
              return null;
            }
            if (!res) return null;
            let contents: { value: string }[] = [];
            if (typeof res === "string") {
              contents = [{ value: res }];
            } else if (Array.isArray(res)) {
              contents = res.map((v: string) => ({ value: v }));
            } else if (res.contents) {
              contents = res.contents.map((v: string) => ({ value: v }));
            }
            if (!contents.length) return null;
            const word = model.getWordAtPosition(position);
            const range = word
              ? {
                  startLineNumber: position.lineNumber,
                  endLineNumber: position.lineNumber,
                  startColumn: word.startColumn,
                  endColumn: word.endColumn,
                }
              : undefined;
            return { range, contents };
          },
        });
    }
  }

  useEffect(() => {
    let provider = null;
    if (textmate) {
      provider = registerTextmate(textmate, false);
    }

    const editor = monaco.editor.create(containerRef.current as HTMLElement, {
      value: value ?? "",
      language,
      theme,
      ...options,
    });
    editorRef.current = editor;

    if (provider) {
      provider.injectCSS();
    }

    lastValueRef.current = editor.getValue();
    const subscription = editor.onDidChangeModelContent(() => {
      const newValue = editor.getValue();
      if (lastValueRef.current === newValue) {
        return;
      }
      lastValueRef.current = newValue;
      latest.current.onChange?.(newValue);
    });

    registerLanguageProviders(language);

    return () => {
      subscription.dispose();
      disposeLanguageProviders();
      editor.dispose();
      editorRef.current = null;
    };
    // Mount once: prop changes are handled by the effects below so the editor
    // is never torn down and recreated mid-edit.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const editor = editorRef.current;
    if (editor && value !== undefined && editor.getValue() !== value) {
      lastValueRef.current = value;
      editor.setValue(value);
    }
  }, [value]);

  useEffect(() => {
    editorRef.current?.updateOptions(options);
  }, [options]);

  useEffect(() => {
    const editor = editorRef.current;
    if (!editor) return;
    monaco.editor.setModelLanguage(editor.getModel() as monaco.editor.ITextModel, language);
    registerLanguageProviders(language);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [language]);

  useEffect(() => {
    editorRef.current?.updateOptions({ theme });
    providerRef.current?.updateTheme(theme);
  }, [theme]);

  useEffect(() => {
    if (textmate && editorRef.current) {
      registerTextmate(textmate, true);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [textmate]);

  return (
    <div
      ref={containerRef}
      style={{ width: "100%", height: "100%", padding: 0, margin: 0 }}
    />
  );
}
