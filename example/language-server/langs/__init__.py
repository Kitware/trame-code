from . import python, moose

ALL_LANGS = dict(languages=[], grammars={}, configs={})

python.register_lang(ALL_LANGS)
moose.register_lang(ALL_LANGS)
