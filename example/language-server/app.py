import asyncio

from trame.app import get_server
from trame.ui.vuetify import SinglePageWithDrawerLayout
from trame.widgets import vuetify, code

from pathlib import Path

# -----------------------------------------------------------------------------
# Trame setup
# -----------------------------------------------------------------------------

server = get_server()
state, ctrl = server.state, server.controller


def load_python():
    load_file("python", Path(__file__).parent / "files" / "python_example.py")


def load_moose():
    load_file("moose", Path(__file__).parent / "files" / "moose_example.i")


def load_javascript():
    load_file("javascript", Path(__file__).parent / "files" / "javascript_example.js")


def load_latex():
    load_file("latex", Path(__file__).parent / "files" / "latex_example.tex")


def load_file(lang, file_path):
    state.editor_lang = lang
    state.editor_content = file_path.read_text()


# -----------------------------------------------------------------------------
# Adhoc Language Server binding
# -----------------------------------------------------------------------------

proc = None


async def run(cmd, *args):
    global proc
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

                # print(f'RECEIVE: {full_message}\n')
                ctrl.lang_server_response("python", content.decode())

    async def handle_stderr():
        async for data in proc.stderr:
            print("Stderr from language server:", data.decode())

    loop = asyncio.get_event_loop()
    stdout_task = loop.create_task(handle_stdout())
    stderr_task = loop.create_task(handle_stderr())

    await proc.wait()

    stdout_task.cancel()
    stderr_task.cancel()


loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.create_task(run("pylsp"))


@ctrl.set("lang_server_request")
def forward_to_lang_server(language_id, action, payload):
    # print("-" * 60)
    # print(f"LANG({language_id}) - {action}")
    # print(payload)
    # print("-" * 60)
    if proc is not None:
        payload = payload.encode()
        prefix = f"Content-Length: {len(payload)}\r\n\r\n".encode()
        # print(f'SEND: {prefix + payload}\n')
        proc.stdin.write(prefix + payload)


# -----------------------------------------------------------------------------
# GUI
# -----------------------------------------------------------------------------

state.trame__title = "Language Server"

with SinglePageWithDrawerLayout(server) as layout:
    layout.title.set_text(state.trame__title)

    with layout.toolbar as toolbar:
        toolbar.dense = True
        vuetify.VSpacer()
        vuetify.VSelect(
            v_model=("editor_lang", "plaintext"),
            items=(
                "editor_langs",
                ["plaintext", "python", "javascript", "html", "moose"],
            ),
            dense=True,
            hide_details=True,
            style="max-width: 150px;",
            classes="mx-2",
        )
        vuetify.VSelect(
            v_model=("editor_theme",),
            items=(
                "editor_themes",
                ["vs", "vs-dark", "hc-black", "hc-light", "textmate"],
            ),
            dense=True,
            hide_details=True,
            style="max-width: 200px;",
        )

    with layout.drawer:
        with vuetify.VCol():
            vuetify.VBtn("Python", classes="mb-2", block=True, click=load_python)
            vuetify.VBtn("Moose", classes="mb-2", block=True, click=load_moose)
            vuetify.VBtn(
                "JavaScript", classes="mb-2", block=True, click=load_javascript
            )
            vuetify.VBtn("Latex", classes="mb-2", block=True, click=load_latex)

    with layout.content:
        with vuetify.VContainer(fluid=True, classes="fill-height pa-0"):
            editor = code.Editor(
                style="width: 100%",
                value=("editor_content", ""),
                options=("editor_options", {"automaticLayout": True}),
                language=("editor_lang", "plaintext"),
                theme=("editor_theme", "vs-dark"),
                language_servers="['python']",
                # language_servers="['python', 'moose', 'cmake']",
            )


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    load_python()
    server.start()
