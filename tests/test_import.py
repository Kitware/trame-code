def test_import():
    from trame_code.widgets.code import Editor  # noqa: F401

    # For components only, the CustomWidget is also importable via trame
    from trame.widgets.code import Editor  # noqa: F401,F811
