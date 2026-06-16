"""Editor language features: completion from live in-process state.

This example shows the capability that distinguishes a callback-backed provider
from a language server: the suggestions come from a live Python object in the
running process, not from source text or type stubs. A language server cannot
offer these names, because they exist only at runtime.

Here the editor completes the keys of an in-memory ``DATASET`` when the cursor
is inside a ``dataset["..."]`` subscript, annotating each with the live value's
type and length. Swap ``DATASET`` for a loaded data file, a database schema, or
any live object and the same handler surfaces those names into the editor.

The contract (shared with the language-features example):

* completion returns a list of items, each a dict with key ``label`` (required)
  and optional ``kind``, ``detail``, ``documentation``, ``insertText``.
* positions are passed as ``line`` (1-based) and ``column`` (0-based).

Run with::

    pip install trame trame-vuetify trame-code
    python app.py
"""

import re

from trame.app import TrameApp
from trame.ui.vuetify3 import SinglePageLayout

from trame.widgets import code
from trame.widgets import vuetify3 as vuetify

# Stand-in for state that exists only at runtime (a loaded dataset, a live
# object graph, a fetched schema...). None of these names appear in the source.
DATASET = {
    "pressure": [0.0] * 1000,
    "density": [0.0] * 1000,
    "temperature": [0.0] * 1000,
    "velocity": [(0.0, 0.0, 0.0)] * 1000,
    "time_steps": list(range(50)),
}

# Match an unclosed string subscript at the cursor:  dataset["pre
_SUBSCRIPT_RE = re.compile(r"""\[\s*["']([^"']*)$""")

INITIAL_CODE = """# Live-state completion demo
#
# 1. Put the cursor between the empty quotes on the last line:  dataset[""]
# 2. Type a letter (p, d, t, or v). Suggestions appear automatically.
# 3. The keys are read live from the in-memory DATASET object
#    (pressure, density, temperature, velocity, time_steps),
#    each shown with its Python type and length.
#
# A language server cannot offer these: they exist only at runtime.

field = dataset[""]
"""


def _describe(value):
    """A short, live description of a value: type plus length when available."""
    type_name = type(value).__name__
    try:
        return f"{type_name}, len {len(value)}"
    except TypeError:
        return type_name


class LiveStateEditor(TrameApp):
    def __init__(self, server=None):
        super().__init__(server)
        self._build_ui()

    def _build_ui(self):
        self.state.trame__title = "Live-state completion"
        with SinglePageLayout(self.server) as self.ui:
            self.ui.title.set_text("Live-state completion")
            with self.ui.content:
                with vuetify.VContainer(fluid=True, classes="fill-height pa-0"):
                    code.Editor(
                        v_model=("live_code", INITIAL_CODE),
                        language="python",
                        theme="vs",
                        completion=self.live_complete,
                        # open the list as soon as the key string is entered
                        completion_trigger_characters=(
                            "completion_triggers",
                            ['"', "'", "["],
                        ),
                        # dict-key completion happens inside a string literal,
                        # where Monaco suppresses suggestions by default; enable
                        # them there, and drop document-word noise.
                        options=(
                            "live_editor_options",
                            {
                                "quickSuggestions": {
                                    "other": True,
                                    "comments": False,
                                    "strings": True,
                                },
                                "wordBasedSuggestions": False,
                                "minimap": {"enabled": False},
                            },
                        ),
                        style="width: 100%; height: 100%;",
                    )

    def live_complete(self, code_text, line, column):
        """Complete DATASET keys when the cursor is inside a string subscript."""
        lines = code_text.split("\n")
        if line < 1 or line > len(lines):
            return []
        prefix = lines[line - 1][:column]

        match = _SUBSCRIPT_RE.search(prefix)
        if not match:
            return []  # not inside a key subscript -> defer to others

        stub = match.group(1)
        return [
            {"label": key, "kind": "field", "detail": _describe(value)}
            for key, value in DATASET.items()
            if key.startswith(stub)
        ]


if __name__ == "__main__":
    app = LiveStateEditor()
    app.server.start()
