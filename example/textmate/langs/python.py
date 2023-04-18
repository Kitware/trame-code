from pathlib import Path

LANG = dict(
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

GRAMMAR = Path(__file__).with_name("python.grammar.json").read_text()
GRAMMAR_TYPE = "json"

CONFIGURATION = Path(__file__).with_name("python.config.json").read_text()
