"""Editor language features: completion + hover backed by a Python callback.

The ``completion`` and ``hover`` props on ``code.Editor`` each take a callable
that receives ``(code, line, column)`` and returns results. Here both are backed
by jedi, giving live Python completion and docstring-on-hover entirely
in-process, with no client-side JavaScript.

The contract:

* completion returns a list of items, each a dict with keys ``label`` (required),
  ``kind``, ``detail``, ``documentation``, ``insertText``.
* hover returns a markdown string, a list of markdown strings, or
  ``{"contents": [...]}`` (or ``None`` for no hover).
* positions are passed as ``line`` (1-based) and ``column`` (0-based), matching
  jedi's API directly.

Run with::

    pip install trame trame-vuetify trame-code jedi
    python app.py
"""

import jedi
from trame.app import TrameApp
from trame.ui.vuetify3 import SinglePageLayout

from trame.widgets import code
from trame.widgets import vuetify3 as v3

INITIAL_CODE = '''import math


def circle_area(radius):
    """Return the area of a circle with the given radius."""
    return math.pi * radius**2


# Type "math." below, or hover a name, to see completion and docstrings.
math.
'''


class PyCodeEditor(TrameApp):
    def __init__(self, server=None):
        super().__init__(server)
        self._build_ui()

    def _build_ui(self):
        self.state.trame__title = "PyEditor"
        with SinglePageLayout(self.server) as self.ui:
            self.ui.title.set_text("Editor language features (jedi)")
            with self.ui.content:
                with v3.VContainer(fluid=True, classes="fill-height pa-0"):
                    code.Editor(
                        v_model=("editor_code", INITIAL_CODE),
                        language="python",
                        theme="vs",
                        style="width: 100%; height: 100%;",
                        completion=self.on_completion,
                        hover=self.on_hover,
                    )

    def on_completion(self, code_text, line, column):
        """Completion items for (code, line, column): line 1-based, column 0-based."""
        try:
            completions = jedi.Script(code=code_text).complete(line, column)
        except Exception:
            return []
        return [
            {
                "label": c.name,
                "kind": c.type,
                "detail": (c.description or "")[:80],
            }
            for c in completions[:200]
        ]

    def on_hover(self, code_text, line, column):
        """Hover markdown (signature + docstring) for the symbol at the cursor."""
        try:
            definitions = jedi.Script(code=code_text).help(line, column)
        except Exception:
            return None
        if not definitions:
            return None
        definition = definitions[0]
        contents = []
        signatures = [s.to_string() for s in definition.get_signatures()]
        if signatures:
            contents.append("```python\n" + "\n".join(signatures) + "\n```")
        doc = definition.docstring(raw=True) or ""
        if doc:
            contents.append(doc)
        return {"contents": contents} if contents else None


if __name__ == "__main__":
    app = PyCodeEditor()
    app.server.start()
