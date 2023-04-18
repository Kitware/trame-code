import { INITIAL, Registry, parseRawGrammar } from "vscode-textmate";

import { Color } from "monaco-editor/esm/vs/base/common/color.js";
import { TokenizationRegistry } from "monaco-editor/esm/vs/editor/common/languages";
import { generateTokensCSSForColorMap } from "monaco-editor/esm/vs/editor/common/languages/supports/tokenization.js";

import { onigLib } from "./onig";
import { MonacoEnvironment } from "./monacoEnv";

// ----------------------------------------------------------------------------
// Language provider
// ----------------------------------------------------------------------------

export class SimpleLanguageInfoProvider {
  constructor({ grammars, theme, monaco, configs }) {
    this.configs = configs;
    this.grammars = grammars;
    this.monaco = monaco;

    this.registry = new Registry({
      theme: MonacoEnvironment.getTextMateTheme(theme),
      onigLib,

      async loadGrammar(scopeName) {
        const scopeNameInfo = grammars[scopeName];
        if (scopeNameInfo == null) {
          return null;
        }

        const [type, grammar] = scopeNameInfo.content;
        return parseRawGrammar(grammar, `example.${type}`);
      },

      getInjections(scopeName) {
        return grammars?.[scopeName]?.injections;
      },
    });

    this.tokensProviderCache = new TokensProviderCache(this.registry);
  }

  updateTheme(themeName) {
    this.registry.setTheme(MonacoEnvironment.getTextMateTheme(themeName));
    this.injectCSS();
  }

  injectCSS() {
    const cssColors = this.registry.getColorMap();
    const colorMap = cssColors.map(Color.Format.CSS.parseHex);
    TokenizationRegistry.setColorMap(colorMap);
    const css = generateTokensCSSForColorMap(colorMap);
    const style = createStyleElementForColorsCSS("textmateStyle");
    style.innerHTML = css;
  }

  async fetchLanguageInfo(language) {
    const configuration = rehydrateRegexps(this.configs[language]);
    const tokensProvider = await this._getTokensProviderForLanguage(language);
    return { tokensProvider, configuration };
  }

  _getTokensProviderForLanguage(language) {
    const scopeName = this._getScopeNameForLanguage(language);
    if (scopeName == null) {
      return Promise.resolve(null);
    }

    const encodedLanguageId =
      this.monaco.languages.getEncodedLanguageId(language);
    return this.tokensProviderCache.createEncodedTokensProvider(
      scopeName,
      encodedLanguageId
    );
  }

  _getScopeNameForLanguage(language) {
    for (const [scopeName, grammar] of Object.entries(this.grammars)) {
      if (grammar.language === language) {
        return scopeName;
      }
    }
    return null;
  }
}

class TokensProviderCache {
  constructor(registry) {
    this.scopeNameToGrammar = new Map();
    this.registry = registry;
  }

  async createEncodedTokensProvider(scopeName, encodedLanguageId) {
    const grammar = await this.getGrammar(scopeName, encodedLanguageId);

    return {
      getInitialState() {
        return INITIAL;
      },

      tokenizeEncoded(line, state) {
        const tokenizeLineResult2 = grammar.tokenizeLine2(line, state);
        const { tokens, ruleStack: endState } = tokenizeLineResult2;
        return { tokens, endState };
      },
    };
  }

  getGrammar(scopeName, encodedLanguageId) {
    const grammar = this.scopeNameToGrammar.get(scopeName);
    if (grammar != null) {
      return grammar;
    }

    const grammarConfiguration = {};
    const promise = this.registry
      .loadGrammarWithConfiguration(
        scopeName,
        encodedLanguageId,
        grammarConfiguration
      )
      .then((grammar) => {
        if (grammar) {
          return grammar;
        } else {
          throw Error(`failed to load grammar for ${scopeName}`);
        }
      });
    this.scopeNameToGrammar.set(scopeName, promise);
    return promise;
  }
}

function createStyleElementForColorsCSS(selector) {
  const existingStyle = document.querySelector(`.${selector}`);
  if (existingStyle) {
    return existingStyle;
  }

  const style = document.createElement("style");
  style.classList.add(selector);
  const monacoColors = document.getElementsByClassName("monaco-colors")[0];
  if (monacoColors) {
    monacoColors.parentElement?.insertBefore(style, monacoColors.nextSibling);
  } else {
    let { head } = document;
    if (head == null) {
      head = document.getElementsByTagName("head")[0];
    }
    head?.appendChild(style);
  }
  return style;
}

// ----------------------------------------------------------------------------
// Language registration
// ----------------------------------------------------------------------------

export function registerLanguages(languages, fetchLanguageInfo, monaco) {
  for (const extensionPoint of languages) {
    const { id: languageId } = extensionPoint;
    monaco.languages.register(extensionPoint);

    // Lazy-load the tokens provider and configuration data.
    monaco.languages.onLanguage(languageId, async () => {
      const { tokensProvider, configuration } = await fetchLanguageInfo(
        languageId
      );

      if (tokensProvider != null) {
        monaco.languages.setTokensProvider(languageId, tokensProvider);
      }

      if (configuration != null) {
        monaco.languages.setLanguageConfiguration(languageId, configuration);
      }
    });
  }
}

// ----------------------------------------------------------------------------
// Regexp re-processing
// ----------------------------------------------------------------------------

const REGEXP_PROPERTIES = [
  // indentation
  "indentationRules.decreaseIndentPattern",
  "indentationRules.increaseIndentPattern",
  "indentationRules.indentNextLinePattern",
  "indentationRules.unIndentedLinePattern",

  // code folding
  "folding.markers.start",
  "folding.markers.end",

  // language's "word definition"
  "wordPattern",
];

export function rehydrateRegexps(rawConfiguration) {
  const out = JSON.parse(rawConfiguration);
  for (const property of REGEXP_PROPERTIES) {
    const value = getProp(out, property);
    if (typeof value === "string") {
      setProp(out, property, new RegExp(value));
    }
  }
  return out;
}

function getProp(obj, selector) {
  const components = selector.split(".");
  return components.reduce((acc, cur) => (acc != null ? acc[cur] : null), obj);
}

function setProp(obj, selector, value) {
  const components = selector.split(".");
  const indexToSet = components.length - 1;
  components.reduce((acc, cur, index) => {
    if (acc == null) {
      return acc;
    }

    if (index === indexToSet) {
      acc[cur] = value;
      return null;
    } else {
      return acc[cur];
    }
  }, obj);
}
