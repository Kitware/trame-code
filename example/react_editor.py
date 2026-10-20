"""Exercise the react build of the trame-code editor.

Checks the editor mounts, two-way binding works through value/onChange, and
the completion/hover callbacks still round-trip to Python.
"""

from trame.app import TrameApp
from trame.ui.mui import MuiLayout

from trame.widgets import code, html, mui, react

CANVAS, SURFACE, INK, MUTED, LINE = (
    "#F3F5F8",
    "#FFFFFF",
    "#172033",
    "#5A6474",
    "#DCE1E8",
)
ACCENT = "#0A7C8C"
SANS = "'IBM Plex Sans', system-ui, -apple-system, 'Segoe UI', sans-serif"
FONTS = (
    "https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500"
    "&family=IBM+Plex+Sans:wght@400;500;600&display=swap"
)
THEME = {
    "palette": {
        "mode": "light",
        "primary": {"main": ACCENT},
        "background": {"default": CANVAS, "paper": SURFACE},
        "text": {"primary": INK, "secondary": MUTED},
        "divider": LINE,
    },
    "typography": {
        "fontFamily": SANS,
        "fontSize": 13,
        "button": {"textTransform": "none", "fontWeight": 500},
    },
    "shape": {"borderRadius": 6},
    "components": {
        "MuiButton": {"defaultProps": {"disableElevation": True}},
        "MuiPaper": {"styleOverrides": {"outlined": {"borderColor": LINE}}},
    },
}

SAMPLE = """import vtk

sphere = vtk.vtkSphereSource()
sphere.SetRadius(1.0)
"""

WORDS = [
    ("vtkSphereSource", "class", "Create a polygonal sphere"),
    ("vtkConeSource", "class", "Create a polygonal cone"),
    ("SetRadius", "method", "SetRadius(self, radius: float) -> None"),
    ("SetThetaResolution", "method", "Set the number of points in theta"),
]


class EditorApp(TrameApp):
    def __init__(self, server=None):
        super().__init__(server, client_type="react")
        self.state.source = SAMPLE
        self.state.hits = []

        with MuiLayout(self.server, theme=THEME) as self.ui:
            mui.GlobalStyles(
                styles=f"@import url('{FONTS}'); body {{ background: {CANVAS}; }}"
            )
            with html.Div(
                style={
                    "display": "flex",
                    "flexDirection": "column",
                    "height": "100vh",
                    "background": CANVAS,
                }
            ):
                with html.Header(
                    style={
                        "background": SURFACE,
                        "borderBottom": f"1px solid {LINE}",
                        "display": "flex",
                        "alignItems": "baseline",
                        "gap": "10px",
                        "height": "52px",
                        "padding": "0 20px",
                    }
                ):
                    html.Span(
                        "trame-code",
                        style={
                            "fontWeight": 600,
                            "fontSize": "1.05rem",
                            "color": INK,
                            "letterSpacing": "-0.01em",
                        },
                    )
                    html.Span(
                        "react client",
                        style={"color": MUTED, "fontSize": "0.8rem"},
                    )
                    html.Div(style={"flex": "1"})
                    mui.Chip(
                        label=react.Bind("`${hits.length} callbacks`"),
                        size="small",
                        variant="outlined",
                    )
                    mui.Chip(
                        label=react.Bind("`${source.length} chars`"),
                        size="small",
                        variant="outlined",
                    )
                with mui.Paper(
                    variant="outlined",
                    style={"flex": "1", "margin": "16px", "overflow": "hidden"},
                ):
                    code.Editor(
                        value=react.Bind("source"),
                        onChange=react.Callback("source = $event"),
                        language="python",
                        theme="vs",
                        completion=self.complete,
                        hover=self.hover,
                    )

    def complete(self, _text, line, column):
        self.state.hits = [*self.state.hits, f"complete {line}:{column}"]
        return [
            {"label": label, "kind": kind, "detail": detail}
            for label, kind, detail in WORDS
        ]

    def hover(self, _text, line, column):
        self.state.hits = [*self.state.hits, f"hover {line}:{column}"]
        return f"**line {line}, col {column}**\n\nhover served from Python"


def main():
    EditorApp().server.start()


if __name__ == "__main__":
    main()
