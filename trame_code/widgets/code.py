from trame_client.widgets.core import AbstractElement
from .. import module


class HtmlElement(AbstractElement):
    def __init__(self, _elem_name, children=None, **kwargs):
        super().__init__(_elem_name, children, **kwargs)
        if self.server:
            self.server.enable_module(module)


# Expose your vue component(s)
class Editor(HtmlElement):
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
            ("language_servers", ":languageServers"),
        ]
        self._event_names += [
            "input",
        ]
        # Expose API via controller
        ctrl = self.server.controller
        self.server.trigger("trame_code_lang_server")(ctrl.lang_server_request)
        ctrl.lang_server_response = self.send_lang_response

    def register_language_server(self, language):
        self.server.js_call(self.__ref, "registerLanguageServer", language)

    def send_lang_response(self, lang, data):
        self.server.protocol.publish(
            "trame.lang.server", dict(type="message", lang=lang, data=data)
        )
