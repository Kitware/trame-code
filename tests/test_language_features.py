def test_completion_and_hover_props_serialize():
    """The completion/hover props are accepted and render onto the element."""
    from trame.app import get_server
    from trame.ui.html import DivLayout
    from trame.widgets import code

    server = get_server("test_language_features")
    with DivLayout(server):
        editor = code.Editor(
            language="python",
            completion="my_complete",
            hover="my_hover",
        )

    assert "completion" in editor._attr_names
    assert "hover" in editor._attr_names

    html = editor.html
    assert 'completion="my_complete"' in html
    assert 'hover="my_hover"' in html
