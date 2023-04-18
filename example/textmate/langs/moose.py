from pathlib import Path

LANG = dict(
    id="moose",
    extensions=[
        ".i",
    ],
    aliases=["Moose"],
    filenames=[],
    firstLine="",
)

GRAMMAR = Path(__file__).with_name("moose.grammar.json").read_text()
GRAMMAR_TYPE = "json"

CONFIGURATION = Path(__file__).with_name("moose.config.json").read_text()
