import copy
import shutil

from .language_server_runner import LanguageServerRunner

# This has keys of language names, like "python" or "cmake",
# and its value is a list of language servers for that type running.
RUNNING_LANGUAGE_SERVERS = {}

"""Example:

RUNNING_LANGUAGE_SERVERS = {
    "python": [
        <LanguageServerRunner1>,
        <LanguageServerRunner2>,
    ],
}

"""


class LanguageServerManager:
    """Language Server Manager

    The language server manager can be used to start and stop
    language server runners, and communicate with them.
    """

    def __init__(self, config, response_callback):
        """Initialize a language server manager

        A config is passed which has a structure like this:

        {
            "python": {
                "cmd": ["pylsp"],
                "config": {},
            },
            "cmake": {},
        }

        The "cmd" indicates the needed command to run to start the
        language server. The "config" is a config the client will use.

        The response_callback is the callback that is called anytime a runner
        this manager is subscribed to provides a response. The response callback
        should take two arguments: one for the language, and one for the data.
        """
        self._config = config
        self._response_callback = response_callback

        self._validate_config()

    @property
    def supported_languages(self):
        return list(self._config)

    @property
    def client_config(self):
        return {k: v["config"] for k, v in self._config.items()}

    def language_config(self, name):
        return self._config[name]

    def start(self):
        for name in self._config:
            self.start_language_server(name)

    def stop(self):
        for name in self._config:
            self.stop_language_server(name)

    def is_running(self, language):
        runner = self._get_matching_runner(language)
        return runner is not None and runner.is_running

    def start_language_server(self, language):
        runner = self._get_matching_runner(language)
        receive_response_func = self._receive_response
        if runner is not None:
            # We already have a matching language server running.
            # Subscribe to the response callbacks and return.
            # (does nothing if we are already subscribed)
            runner.subscribe(receive_response_func)
            return

        # Otherwise, make a new runner
        runner = LanguageServerRunner(language, self._config[language])
        runner.subscribe(receive_response_func)
        runner.start()

        currently_running = RUNNING_LANGUAGE_SERVERS.setdefault(language, [])
        currently_running.append(runner)

    def stop_language_server(self, language):
        runner = self._get_matching_runner(language)
        if runner is None:
            # There's no such runner
            return

        if not runner.is_running:
            # It's already not running
            self._remove_runner(runner)
            return

        receive_response_func = self._receive_response
        # Unsubscribe if we are subscribed
        # (this does nothing if we weren't subscribed)
        runner.unsubscribe(receive_response_func)

        if runner.use_count == 0:
            # No one is using the runner now. Stop and remove it.
            runner.stop()
            self._remove_runner(runner)

    def stop_all_language_servers(self):
        # This will stop all language servers, even the ones not managed by this instance
        for runners in RUNNING_LANGUAGE_SERVERS.values():
            for runner in runners:
                runner.stop()

        RUNNING_LANGUAGE_SERVERS.clear()

    def send_message(self, language, action, payload):
        runner = self._get_matching_runner(language)
        if runner is None:
            config = self.language_config(language)
            raise RunnerNotFound(f"language: {language}, config: {config}")

        runner.send(payload)

    def _validate_config(self):
        # Validate the config and fill missing keys with default values
        for name, config in self._config.items():
            if config is None:
                # Need to fill with an empty dict
                config = {}
                self._config[name] = config

            # Make sure the command is set
            if not config.get("cmd"):
                # No command was specified
                if DEFAULT_CONFIGS.get(name, {}).get("cmd"):
                    # We can use the default command if it is available
                    # Make a deep copy to ensure we don't modify the default
                    cmd = copy.deepcopy(DEFAULT_CONFIGS[name]["cmd"])
                    if not shutil.which(cmd[0]):
                        msg = (
                            f"The executable for the default command for '{name}' "
                            "could not be found. Please install it by running "
                            f"'pip install trame-code[{name}]' or specify a "
                            "different command."
                        )
                        raise ExecutableNotFound(msg)

                    config["cmd"] = cmd
                else:
                    msg = (
                        f"'{name}' does not have a default command ('cmd') and "
                        "a command must be specified"
                    )
                    raise InvalidConfig(msg)

            if not config.get("config"):
                # No client config was specified. Use the default if available,
                # but if not, just continue as a client config is not required.
                if DEFAULT_CONFIGS.get(name, {}).get("config"):
                    config["config"] = copy.deepcopy(DEFAULT_CONFIGS[name]["config"])
                else:
                    # Default to an empty dict
                    config["config"] = {}

    def _get_matching_runner(self, language):
        # Get the runner for the language that matches our config
        our_config = self._config[language]
        currently_running = RUNNING_LANGUAGE_SERVERS.get(language, [])
        for runner in currently_running:
            if runner.config == our_config:
                return runner

        return None

    def _remove_runner(self, runner):
        language = runner.language
        currently_running = RUNNING_LANGUAGE_SERVERS.setdefault(language, [])
        if runner in currently_running:
            currently_running.pop(currently_running.index(runner))

    def _receive_response(self, runner, data):
        # This is called when a runner receives a response
        self._response_callback(runner.language, data)


class InvalidConfig(Exception):
    pass


class ExecutableNotFound(Exception):
    pass


class RunnerNotFound(Exception):
    pass


# These can be installed via `pip install trame-code[<name>]`
DEFAULT_CONFIGS = {
    "python": {
        "cmd": ["pylsp"],
        "config": {},
    },
    "cmake": {
        "cmd": ["cmake-language-server"],
        "config": {},
    },
}
