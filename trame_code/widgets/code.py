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
    :param theme:
    :param language:
    :param textmate:

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
            "theme",
            "language",
            "textmate",
        ]
        self._event_names += [
            "input",
        ]
