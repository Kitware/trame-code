import yaml

from trame.app import get_server
from trame.ui.vuetify import SinglePageWithDrawerLayout
from trame.widgets import vuetify, code

from pathlib import Path

import langs

# -----------------------------------------------------------------------------
# Trame setup
# -----------------------------------------------------------------------------

server = get_server()
state, ctrl = server.state, server.controller


parent_dir = Path(__file__).parent
files_dir = parent_dir / "files"


def load_python():
    load_file("python", files_dir / "python_example.py")


def load_moose():
    load_file("moose", files_dir / "moose_example.i")


def load_javascript():
    load_file("javascript", files_dir / "javascript_example.js")


def load_latex():
    load_file("latex", files_dir / "latex_example.tex")


def load_cmake():
    load_file("cmake", files_dir / "CMakeLists.txt")


def load_file(lang, file_path):
    state.editor_lang = lang
    state.editor_content = file_path.read_text()


config_file = parent_dir / "language_server_config.yml"
with open(config_file, "r") as rf:
    language_server_config = yaml.safe_load(rf)

# Alternatively, we can specify the dict here.
# Trame will fill in defaults for missing fields automatically.
# language_server_config = {
#     "python": {},
#     "cmake": {},
# }

state.editor_textmate = langs.ALL_LANGS

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
                ["plaintext", "python", "javascript", "html", "moose", "cmake"],
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
            vuetify.VBtn("CMake", classes="mb-2", block=True, click=load_cmake)

    with layout.content:
        with vuetify.VContainer(fluid=True, classes="fill-height pa-0"):
            editor = code.Editor(
                style="width: 100%",
                value=("editor_content", ""),
                options=("editor_options", {"automaticLayout": True}),
                language=("editor_lang", "plaintext"),
                theme=("editor_theme", "vs-dark"),
                textmate=("editor_textmate", None),
                lang_config=language_server_config,
            )

            editor.start_language_servers()

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    load_python()
    server.start()
