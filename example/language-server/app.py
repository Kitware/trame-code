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


@ctrl.set("lang_server_request")
def forward_to_lang_server(language_id, action, payload):
    print("-" * 60)
    print(f"LANG({language_id}) - {action}")
    print(payload)
    print("-" * 60)
    # ctrl.lang_server_response(language_id, response_payload)


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
                language_servers="['python', 'moose', 'cmake']",
            )


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    load_python()
    server.start()
