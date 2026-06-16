from trame_code.widgets.code import *


def initialize(server):
    from trame_code import module

    server.enable_module(module)
