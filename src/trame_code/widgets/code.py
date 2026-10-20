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
        self.props += [
            "options",
            "value",
            "theme",
            "language",
            "textmate",
            ("completion_trigger_characters", "completionTriggerCharacters"),
            "completion",
            "hover",
        ]
        if self.server.client_type == "react":
            # React has no v-model: binding is an explicit value/on_change pair.
            self.events += [("on_change", "onChange")]
            # react_use takes no plugin options, so the serve directory that vue
            # receives through vue_use comes in as a prop.
            self.props += [("serve_directory", "serveDirectory")]
            self.serve_directory = module.serve_directory
        else:
            self.props += [("model_value", "modelValue")]
            self.events += ["input"]

        # Monaco pulls completion/hover results and needs them returned, so each
        # callable is registered as a trigger and the client invokes it by name.
        if completion is not None:
            self.completion = self.ctrl.trigger_name(completion)
        if hover is not None:
            self.hover = self.ctrl.trigger_name(hover)
