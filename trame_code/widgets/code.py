"""Module compatible with vue2 and vue3. To use it, you need to install **trame-code**"""

from trame_client.widgets.core import AbstractElement

from .. import module

__all__ = [
    "Editor",
]


class HtmlElement(AbstractElement):
    def __init__(self, _elem_name, children=None, **kwargs):
        super().__init__(_elem_name, children, **kwargs)
        if self.server:
            self.server.enable_module(module)


# Expose your vue component(s)
class Editor(HtmlElement):
    """
    Monaco Editor component

    Properties:

    :param options:
    :param value:
    :param model_value:
    :param theme:
    :param language:
    :param textmate:
    :param completion: name of a server ``@trigger`` that returns completion
        items (list of {label, kind, detail, documentation, insertText}) for
        ``(code, line, column)``. line is 1-based, column 0-based.
    :param hover: name of a server ``@trigger`` that returns hover content (a
        markdown string, list of strings, or {contents: [...]}) for
        ``(code, line, column)``.

    Events:

    :param input:

    """

    def __init__(self, **kwargs):
        super().__init__(
            "vs-editor",
            **kwargs,
        )
        self._attr_names += [
            "options",
            "value",
            ("model_value", "modelValue"),
            "theme",
            "language",
            "textmate",
            "completion",
            "hover",
            ("completion_trigger_characters", "completionTriggerCharacters"),
        ]
        self._event_names += [
            "input",
        ]
