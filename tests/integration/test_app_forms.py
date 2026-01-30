# tests/integration/test_app_forms.py

import pytest

pytest.importorskip("pytui.core.renderer")
pytest.importorskip("pytui.components.input")
pytest.importorskip("pytui.components.select")


def test_app_forms_input_select():
    from pytui.core.renderer import Renderer
    from pytui.components import Input, Select

    r = Renderer(width=40, height=10, target_fps=0)
    inp = Input(r.context, {"value": "hello", "width": 20, "height": 1})
    sel = Select(
        r.context,
        {"options": ["a", "b", "c"], "selected": 1, "width": 20, "height": 3},
    )
    r.root.add(inp)
    r.root.add(sel)
    r._render_frame()
    assert inp.value == "hello"
    assert sel.selected == "b"
