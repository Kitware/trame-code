from trame.app import get_server
from trame.ui.vuetify import SinglePageWithDrawerLayout
from trame.widgets import vuetify, code

from pathlib import Path

# -----------------------------------------------------------------------------
# Trame setup
# -----------------------------------------------------------------------------

server = get_server(client_type="vue2")
state, ctrl = server.state, server.controller


def path_to_node(path_item, node_map):
    _id = str(path_item.absolute())
    parent_id = str(path_item.absolute().parent.absolute())

    node = dict(id=_id, name=path_item.name, children=[])
    node_map[node.get("id")] = node

    if parent_id in node_map:
        children = node_map[parent_id].get("children")
        children.append(node)

    return node


def update_tree(base_path):
    files = {}
    root = Path(base_path)
    root_node = path_to_node(root, files)
    for file in root.rglob("*"):
        path_to_node(file, files)

    state.tree_files = root_node.get("children")


def load_file(full_paths):
    if full_paths:
        item = Path(full_paths[0])
        if item.is_file():
            if item.name.endswith(".py"):
                state.editor_lang = "python"
            else:
                state.editor_lang = "plaintext"

            with open(item) as content:
                state.editor_content = content.read()


# -----------------------------------------------------------------------------
# GUI
# -----------------------------------------------------------------------------

state.trame__title = "Viewer"

with SinglePageWithDrawerLayout(server) as layout:
    layout.title.set_text("Viewer")

    with layout.toolbar as toolbar:
        toolbar.dense = True
        vuetify.VSpacer()
        vuetify.VSelect(
            v_model=("editor_lang", "plaintext"),
            items=("editor_langs", ["plaintext", "python", "javascript", "html"]),
            dense=True,
            hide_details=True,
            style="max-width: 150px;",
            classes="mx-2",
        )
        vuetify.VSelect(
            v_model=("editor_theme", "vs-dark"),
            items=("editor_themes", ["vs", "vs-dark", "hc-black", "hc-light"]),
            dense=True,
            hide_details=True,
            style="max-width: 200px;",
        )

    with layout.drawer:
        vuetify.VTreeview(
            activatable=True,
            dense=True,
            items=("tree_files", []),
            update_active=(load_file, "[$event]"),
        )

    with layout.content:
        with vuetify.VContainer(fluid=True, classes="fill-height pa-0"):
            editor = code.Editor(
                style="width: 100%",
                value=("editor_content", ""),
                options=("editor_options", {}),
                language=("editor_lang", "plaintext"),
                theme=("editor_theme", "vs-dark"),
            )


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    update_tree(".")
    server.start()
