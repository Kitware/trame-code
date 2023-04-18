from . import python, moose

configs = {
    "python": python.CONFIGURATION,
    "moose": moose.CONFIGURATION,
}

grammars = {
    "source.python": {
        "language": "python",
        "content": (python.GRAMMAR_TYPE, python.GRAMMAR),
    },
    "input.moose": {
        "language": "moose",
        "content": (moose.GRAMMAR_TYPE, moose.GRAMMAR),
    },
}

languages = [
    python.LANG,
    moose.LANG,
]


def to_dict():
    return dict(
        languages=languages,
        grammars=grammars,
        configs=configs,
    )
