from pathlib import Path

from trame_code import __version__

# Compute local path to serve
serve_path = str(Path(__file__).with_name("serve").resolve())

# Version the served directory so a client re-fetches JS/CSS after an upgrade
# instead of getting a stale bundle from the browser cache.
serve_directory = f"__trame_code_{__version__}"

# Serve directory for JS/CSS files
serve = {serve_directory: serve_path}

# List of JS files to load (usually from the serve path above)
scripts = [f"{serve_directory}/trame-code.umd.js"]

# List of CSS files to load (usually from the serve path above)
styles = [f"{serve_directory}/style.css"]

# List of Vue plugins to install/load
vue_use = ["trame_code"]

# Uncomment to add entries to the shared state
# state = {}


# Optional if you want to execute custom initialization at module load
def setup(app, **kwargs):
    """Method called at initialization with possibly some custom keyword arguments"""
