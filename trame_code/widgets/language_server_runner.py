import asyncio

from trame.app.asynchronous import create_task


class LanguageServerRunner:
    """Class for running a single language server"""

    def __init__(self, language, config):
        """Create a language server runner

        config is the config object that must contain a "cmd" to run

        After initializing, you must subscribe callback functions to receive
        messages.
        """

        self.language = language
        self.config = config
        self.response_callbacks = []

        self._start_task = None
        self._stop_task = None
        self._process = None
        self._io_tasks = []

    @property
    def cmd(self):
        return self.config.get("cmd", [])

    @property
    def client_config(self):
        return self.config.get("config", {})

    @property
    def is_running(self):
        return self._process is not None

    @property
    def use_count(self):
        # Return the number of response listeners
        return len(self.response_callbacks)

    def subscribe(self, callback):
        """Subscribe a callback to the response callbacks list

        The callback should take two arguments: one for the runner,
        and one for the data.
        """
        if not self.is_subscribed(callback):
            self.response_callbacks.append(callback)

    def unsubscribe(self, callback):
        """Unsubscribe a callback (if subscribed) from the response callback list"""
        if self.is_subscribed(callback):
            self.response_callbacks.pop(callback)

    def unsubscribe_all(self):
        self.response_callbacks.clear()

    def is_subscribed(self, callback):
        return callback in self.response_callbacks

    def send(self, message):
        """Send a message to the language server"""
        return self._send_request(message)

    def start(self):
        """Start the language server"""
        task = create_task(self._start())
        self._start_task = task

        def on_finished(future):
            if not self.is_running:
                print(
                    f"Language server for {self.language} (command {self.cmd}) failed to start!"
                )
            self._start_task = None

        task.add_done_callback(on_finished)

    def stop(self):
        """Stop the language server"""
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

    async def _start(self):
        proc = await asyncio.create_subprocess_exec(
            *self.cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        language = self.language

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

                    # print(f"RECEIVE {language}: {full_message}\n")
                    self._receive_response(content.decode())

        async def handle_stderr():
            async for data in proc.stderr:
                print(f"Error from language server '{language}':", data.decode())

        stdout_task = create_task(handle_stdout())
        stderr_task = create_task(handle_stderr())

        self._process = proc
        self._io_tasks = [stdout_task, stderr_task]

        await proc.wait()

        print(f"Language server '{language}' has exited")

        self.stop()

    async def _stop(self):

        self.unsubscribe_all()

        if self._process is not None:
            await self._process.terminate()
            self._process = None

        for task in self._io_tasks:
            task.cancel()

        self._io_tasks.clear()

    def _send_request(self, message, attempt_number=0):
        """Send a message to the language server"""
        # print(f"SEND {self.language}:", payload)
        if self._process is None:
            # Still starting. Try again soon.
            if attempt_number > 10:
                print(f"Failed to send message to {self.language} language server")
                return

            loop = asyncio.get_running_loop()
            loop.call_soon(self._send_request, message, attempt_number + 1)
            return

        proc = self._process

        message = message.encode()
        prefix = f"Content-Length: {len(message)}\r\n\r\n".encode()
        # print(f'SEND {self.language}: {prefix + message}\n')
        proc.stdin.write(prefix + message)

    def _receive_response(self, data):
        """Send the response to all subscribed listeners"""
        # print(f"RECEIVE {self.language}:", data)
        for callback in self.response_callbacks:
            callback(self, data)
