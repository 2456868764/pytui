# tests/integration/test_app_layout.py

import pytest

pytest.importorskip("pytui.core.renderer")
pytest.importorskip("pytui.components.box")
pytest.importorskip("pytui.components.text")


def test_app_layout_multi_children():
    from pytui.core.renderer import Renderer
    from pytui.components import Box, Text

    r = Renderer(width=50, height=15, target_fps=0)
    box = Box(r.context, {"width": 50, "height": 15, "border": True})
    t1 = Text(r.context, {"content": "A", "width": 10, "height": 1})
    t2 = Text(r.context, {"content": "B", "width": 10, "height": 1})
    box.add(t1)
    box.add(t2)
    r.root.add(box)
    r._render_frame()
    r.root.calculate_layout()
    assert box.width == 50
    assert box.height == 15
    assert len(box.children) == 2
