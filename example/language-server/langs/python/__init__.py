from pathlib import Path

CONFIGURATION = Path(__file__).with_name("python.config.json").read_text()
GRAMMAR = Path(__file__).with_name("python.grammar.json").read_text()
GRAMMAR_TYPE = "json"


def register_lang(config):
    config["languages"].append(
        dict(
            id="python",
            extensions=[
                ".py",
                ".rpy",
                ".pyw",
                ".cpy",
                ".gyp",
                ".gypi",
                ".pyi",
                ".ipy",
                ".bzl",
                ".cconf",
                ".cinc",
                ".mcconf",
                ".sky",
                ".td",
                ".tw",
            ],
            aliases=["Python", "py"],
            filenames=["Snakefile", "BUILD", "BUCK", "TARGETS"],
            firstLine="^#!\\s*/?.*\\bpython[0-9.-]*\\b",
        )
    )
    config["configs"]["python"] = CONFIGURATION
    config["grammars"]["source.python"] = {
        "language": "python",
        "content": (GRAMMAR_TYPE, GRAMMAR),
    }
