# tests/integration/test_app_hello.py
"""Hello World 集成测试：挂载 Box+Text，渲染一帧，校验 buffer。"""

import pytest

pytest.importorskip("pytui.core.renderer")
pytest.importorskip("pytui.components.box")
pytest.importorskip("pytui.components.text")


def test_hello_renders_text():
    from pytui.core.renderer import Renderer
    from pytui.components import Box, Text

    r = Renderer(width=40, height=10, target_fps=0)
    box = Box(r.context, {"width": 40, "height": 10, "border": True})
    text = Text(r.context, {"content": "Hello"})
    box.add(text)
    r.root.add(box)
    r._render_frame()
    # 渲染后交换了双缓冲，新帧在 front_buffer
    buf = r.front_buffer
    found = False
    for y in range(10):
        for x in range(40):
            c = buf.get_cell(x, y)
            if c and c.char and "H" in c.char:
                found = True
                break
        if found:
            break
    assert found, "Expected 'Hello' to appear in back buffer"
