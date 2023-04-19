from pathlib import Path

CONFIGURATION = Path(__file__).with_name("moose.config.json").read_text()
GRAMMAR = Path(__file__).with_name("moose.grammar.json").read_text()
GRAMMAR_TYPE = "json"


def register_lang(config):
    config["languages"].append(
        dict(
            id="moose",
            extensions=[
                ".i",
            ],
            aliases=["Moose"],
            filenames=[],
            firstLine="",
        )
    )
    config["configs"]["moose"] = CONFIGURATION
    config["grammars"]["input.moose"] = {
        "language": "moose",
        "content": (GRAMMAR_TYPE, GRAMMAR),
    }
