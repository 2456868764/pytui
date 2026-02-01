# pytui.testing.mock_mouse - Aligns with OpenTUI packages/core/src/testing/mock-mouse.ts
# createMockMouse(renderer) -> MockMouse with feed(data).


from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pytui.core.renderer import Renderer


class MockMouse:
    """向 renderer 注入鼠标序列的辅助对象；若 renderer 无 mouse 则先挂载 MouseHandler。"""

    def __init__(self, renderer: Renderer) -> None:
        self._renderer = renderer
        if not hasattr(renderer, "mouse") or renderer.mouse is None:
            from pytui.core.mouse import MouseHandler

            m = MouseHandler()
            m.on("mouse", lambda e: renderer.events.emit("mouse", e))
            renderer.mouse = m
        self._handler = renderer.mouse

    def feed(self, data: bytes | str) -> bytes:
        """注入原始字节（如 SGR 1006 序列）；返回未消费的字节。"""
        return self._handler.feed(data)


def create_mock_mouse(renderer: Renderer) -> MockMouse:
    """返回可向 renderer 注入鼠标事件的 MockMouse；必要时为 renderer 挂载 MouseHandler。"""
    return MockMouse(renderer)
