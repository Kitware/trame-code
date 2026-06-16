def test_completion_and_hover_register_as_triggers():
    """A callable passed to completion/hover is registered as a trigger and
    surfaces on the element as a trigger-name attribute."""
    from trame.app import get_server
    from trame.ui.html import DivLayout
    from trame.widgets import code

    def on_complete(code_text, line, column):
        return []

    def on_hover(code_text, line, column):
        return None

    server = get_server("test_language_features")
    with DivLayout(server):
        editor = code.Editor(
            language="python",
            completion=on_complete,
            hover=on_hover,
        )

    html = editor.html
    assert 'completion="' in html
    assert 'hover="' in html

    # the internal triggers resolve back to the original callables
    ctrl = server.controller
    assert ctrl.trigger_fn(server.trigger_name(on_complete)) is on_complete
    assert ctrl.trigger_fn(server.trigger_name(on_hover)) is on_hover
