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
    :param completion: a callable ``fn(code, line, column)`` returning a list of
        completion items, each a dict with keys ``label`` (required), ``kind``,
        ``detail``, ``documentation``, ``insertText``. ``line`` is 1-based,
        ``column`` 0-based. Registered as a trigger internally so the client can
        invoke it and receive the returned items (Monaco needs the result back).
    :param hover: a callable ``fn(code, line, column)`` returning hover content:
        a markdown string, a list of markdown strings, ``{contents: [...]}``, or
        ``None``. Registered as a trigger internally like ``completion``.
    :param completion_trigger_characters: list of characters that open the
        completion list (defaults to ``["."]`` in the component).

    Events:

    :param input:

    """

    def __init__(self, completion=None, hover=None, **kwargs):
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
            ("completion_trigger_characters", "completionTriggerCharacters"),
        ]
        self._event_names += [
            "input",
        ]

        # `completion` / `hover` take a callable receiving (code, line, column).
        # Monaco pulls results from the provider and needs them returned, so the
        # callback is registered as a trigger internally and the client invokes
        # it by name and awaits the returned value.
        if completion is not None:
            self._attributes["completion_trigger"] = (
                f'completion="{self.ctrl.trigger_name(completion)}"'
            )
        if hover is not None:
            self._attributes["hover_trigger"] = (
                f'hover="{self.ctrl.trigger_name(hover)}"'
            )
