import asyncio

from trame.app.asynchronous import create_task


class LanguageServerRunner:
    """Class for running a single language server"""

    def __init__(self, server, language, config):
        """The cmd is a list containing the command to run"""
        self.server = server
        self.language = language
        self.config = config

        self._start_task = None
        self._stop_task = None
        self._process = None
        self._io_tasks = []

        # In case we want to keep track of how many clients are using this
        self.use_count = 1

        self.setup_trigger()

    def setup_trigger(self):
        self.server.trigger("trame_code_lang_server")(self._on_lang_server_request)

    @property
    def cmd(self):
        return self.config.get("cmd", [])

    @property
    def client_config(self):
        return self.config.get("config", {})

    @property
    def is_running(self):
        return self._process is not None

    def stop(self):
        if self._stop_task is not None:
            # Already stopping
            return

        task = create_task(self._stop())
        self._stop_task = task

        def on_finished(future):
            if self.is_running:
                print(
                    f"Language server for {self.language} (command {self.cmd}) failed to stop!"
                )
            self._stop_task = None

        task.add_done_callback(on_finished)

    async def _stop(self):
        if self._process is not None:
            await self._process.terminate()
            self._process = None

        for task in self._io_tasks:
            task.cancel()

        self._io_tasks.clear()

    def start(self):
        task = create_task(self._start())
        self._start_task = task

        def on_finished(future):
            if not self.is_running:
                print(
                    f"Language server for {self.language} (command {self.cmd}) failed to start!"
                )
            self._start_task = None

        task.add_done_callback(on_finished)

    async def _start(self):
        proc = await asyncio.create_subprocess_exec(
            *self.cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        # Use the language as the name (for print statements)
        name = self.language

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

                    # print(f"RECEIVE {name}: {full_message}\n")
                    self._send_response(content.decode())

        async def handle_stderr():
            async for data in proc.stderr:
                print(f"Error from language server '{name}':", data.decode())

        stdout_task = create_task(handle_stdout())
        stderr_task = create_task(handle_stderr())

        self._process = proc
        self._io_tasks = [stdout_task, stderr_task]

        await proc.wait()

        print(f"Language server '{name}' has exited")

        self.stop()

    def _on_lang_server_request(self, language, action, payload):
        print(f"{language=}")
        if self.language != language:
            # Not for this runner
            return

        return self._send_request(action, payload)

    def _send_request(self, action, payload):
        """Send a request to the language server"""
        print("SEND:", payload)
        if self._process is None:
            # Still starting. Try again soon.
            loop = asyncio.get_running_loop()
            loop.call_soon(self._send_request, action, payload)
            return

        proc = self._process

        payload = payload.encode()
        prefix = f"Content-Length: {len(payload)}\r\n\r\n".encode()
        # print(f'SEND {name}: {prefix + payload}\n')
        proc.stdin.write(prefix + payload)

    def _send_response(self, data):
        """Send a response from the language server to the trame client"""
        print("RECEIVE:", data)
        self.server.protocol.publish(
            "trame.code.lang.server",
            dict(type="message", lang=self.language, data=data),
        )
