from pathlib import Path

from trame_code import __version__

# Compute local path to serve
serve_path = str(Path(__file__).with_name("serve").resolve())

# Version the served directory so a client re-fetches JS/CSS after an upgrade
# instead of getting a stale bundle from the browser cache.
serve_directory = f"__trame_code_{__version__}"

# Serve directory for JS/CSS files
serve = {serve_directory: serve_path}

# List of CSS files to load (usually from the serve path above)
styles = [f"{serve_directory}/style.css"]


def setup(app, **_kwargs):
    """Enable the client bundle matching the server's client_type."""
    client_type = getattr(app, "client_type", "vue3")
    if client_type == "react":
        app.enable_module(
            {
                "scripts": [f"{serve_directory}/trame-code-react.umd.cjs"],
                "react_use": ["trame_code_react"],
            }
        )
    else:
        app.enable_module(
            {
                "scripts": [f"{serve_directory}/trame-code.umd.js"],
                "vue_use": [("trame_code", {"serveDirectory": serve_directory})],
            }
        )
