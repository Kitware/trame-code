import asyncio

from trame_client.widgets.core import AbstractElement
from .. import module

from .language_server_manager import LanguageServerManager


class HtmlElement(AbstractElement):
    def __init__(self, _elem_name, children=None, **kwargs):
        super().__init__(_elem_name, children, **kwargs)
        if self.server:
            self.server.enable_module(module)


# Expose your vue component(s)
class Editor(HtmlElement):

    EDITOR_ID = 0

    def __init__(self, lang_config=None, **kwargs):
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

        ref = kwargs.get("ref")
        if ref is None:
            Editor.EDITOR_ID += 1
            ref = f"trame_code_editor_{Editor.EDITOR_ID}"

        self.__ref = ref
        self._attributes["ref"] = f'ref="{ref}"'

        self.__config_key = f"{ref}_config"

        self._language_server_manager = LanguageServerManager(self.server, lang_config)

        manager = self.language_server_manager
        self.server.state[self.__config_key] = manager.client_config
        self._attributes["languages"] = f':languages="{self.__config_key}"'

    @property
    def language_server_manager(self):
        return self._language_server_manager

    @property
    def supported_language_servers(self):
        return self.language_server_manager.supported_languages

    def start_language_servers(self):
        self.language_server_manager.start()

    def stop_language_servers(self):
        self.language_server_manager.stop()

    def stop_all_language_servers(self):
        self.language_server_manager.stop_all_language_servers()
