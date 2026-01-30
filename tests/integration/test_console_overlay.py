# tests/integration/test_console_overlay.py
"""Console Overlay 集成测试：挂载 ConsoleOverlay + ConsoleBuffer，渲染一帧，校验 buffer 内容。"""

import pytest

pytest.importorskip("pytui.core.console")
pytest.importorskip("pytui.core.renderer")


def test_console_overlay_renders_buffer_content():
    from pytui.core.console import ConsoleBuffer, ConsoleOverlay
    from pytui.core.renderer import Renderer

    r = Renderer(width=40, height=20, target_fps=0)
    buf = ConsoleBuffer()
    buf.append("Console line 1\nLine 2\nThird")
    overlay = ConsoleOverlay(r.context, {"buffer": buf, "width": 40, "height": 20})
    r.root.add(overlay)
    r._render_frame()
    front = r.front_buffer
    # Overlay at (0,0) draws first line "Console line 1"
    c0 = front.get_cell(0, 0)
    assert c0 and c0.char == "C", "Expected first char 'C' of overlay buffer at (0,0)"
