const themes = import.meta.glob("./*.json");

const THEMES = {};
const ALIASES = {
  vs: "Light (Visual Studio)",
  "vs-light": "Light (Visual Studio)",
  "vs-dark": "Dark (Visual Studio)",
  "hc-black": "Dark High Contrast",
  "hc-light": "Light High Contrast",
};

export function getTextMateTheme(name) {
  return THEMES[name] || THEMES[ALIASES[name]];
}

export function registerTextMateTheme(data) {
  THEMES[data.name] = data;
}

export function registerTextMateAlias(src, dst) {
  ALIASES[src] = dst;
}

function updateMainColor(mainSettings, theme) {
  mainSettings.background =
    theme?.colors?.["editor.background"] || mainSettings.background;
  mainSettings.foreground =
    theme?.colors?.["editor.foreground"] || mainSettings.foreground;
}

function toTextmateTheme(v, allThemes) {
  const { name } = v;
  const mainSettings = { background: "", foreground: "" };
  const settings = [{ settings: mainSettings }];

  if (v.include) {
    const parentTheme = allThemes[v.include];
    updateMainColor(mainSettings, parentTheme);

    const parentSettings = toTextmateTheme(parentTheme, allThemes).settings;
    for (let i = 0; i < parentSettings.length; i++) {
      settings.push(parentSettings[i]);
    }
  }
  const currentSettings = v.tokenColors;
  for (let i = 0; i < currentSettings?.length || 0; i++) {
    settings.push(currentSettings[i]);
  }

  updateMainColor(mainSettings, v);

  return { name, settings };
}

const keys = [];
const values = [];
const resolvedMap = {};
for (const [key, value] of Object.entries(themes)) {
  keys.push(key);
  values.push(value);
}

Promise.all(values.map((v) => v())).then((results) => {
  for (let i = 0; i < results.length; i++) {
    resolvedMap[keys[i]] = results[i];
  }
  results.forEach((v) =>
    registerTextMateTheme(toTextmateTheme(v, resolvedMap))
  );
});
