import asyncio

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

        self._running_language_servers = {}
        self.server.trigger("trame_code_lang_server")(self._lang_server_request)

    def register_language_server(self, language):
        self.server.js_call(self.__ref, "registerLanguageServer", language)

    def start_language_server(self, name, cmd, *args):
        if name in self._running_language_servers:
            raise RuntimeError(f"Language server for {name} is already running!")

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # Event loop isn't running. Make one.
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        loop.create_task(self._start_language_server(name, cmd, *args))

    def _send_lang_response(self, lang, data):
        self.server.protocol.publish(
            "trame.code.lang.server", dict(type="message", lang=lang, data=data)
        )

    def _lang_server_request(self, name, action, payload):
        if name not in self._running_language_servers:
            raise RuntimeError(f"No language server for '{name}' is running.")

        proc = self._running_language_servers[name]["process"]

        payload = payload.encode()
        prefix = f"Content-Length: {len(payload)}\r\n\r\n".encode()
        # print(f'SEND: {prefix + payload}\n')
        proc.stdin.write(prefix + payload)

    async def _start_language_server(self, name, cmd, *args):
        proc = await asyncio.create_subprocess_exec(
            cmd,
            *args,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        async def handle_stdout():
            async for data in proc.stdout:
                length_prefix = b"Content-Length: "
                if data.startswith(length_prefix):
                    # Read the content length
                    content_length = int(data[len(length_prefix) :])

                    # Skip over all other headers
                    full_message = data
                    line = data
                    while line and line.strip():
                        line = await proc.stdout.readline()
                        full_message += line

                    # Read the content
                    content = await proc.stdout.read(content_length)
                    full_message += content

                    # print(f"RECEIVE: {full_message}\n")
                    self._send_lang_response(name, content.decode())

        async def handle_stderr():
            async for data in proc.stderr:
                print(f"Error from language server '{name}':", data.decode())

        loop = asyncio.get_event_loop()
        stdout_task = loop.create_task(handle_stdout())
        stderr_task = loop.create_task(handle_stderr())

        self._running_language_servers[name] = {
            "process": proc,
            "tasks": [stdout_task, stderr_task],
        }

        await proc.wait()

        print(f"Language server '{name}' has exited")

        stdout_task.cancel()
        stderr_task.cancel()

        self._running_language_servers.pop(name)
