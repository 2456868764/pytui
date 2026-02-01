# pytui.testing.test_renderer - Aligns with OpenTUI packages/core/src/testing/test-renderer.ts
# createTestRenderer(options) -> { renderer, mockInput, mockMouse, renderOnce, captureCharFrame, resize }.


from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pytui.core.renderer import Renderer


class MockTerminal:
    """无 TTY 的终端桩：固定尺寸，所有 I/O 为 no-op。"""

    def __init__(self, width: int = 80, height: int = 24) -> None:
        self._width = max(1, width)
        self._height = max(1, height)

    def get_size(self) -> tuple[int, int]:
        return (self._width, self._height)

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    def enter_alternate_screen(self) -> None:
        pass

    def exit_alternate_screen(self) -> None:
        pass

    def hide_cursor(self) -> None:
        pass

    def show_cursor(self) -> None:
        pass

    def set_raw_mode(self) -> None:
        pass

    def restore_mode(self) -> None:
        pass

    def enable_mouse(self) -> None:
        pass

    def disable_mouse(self) -> None:
        pass


def create_test_renderer(
    width: int = 80,
    height: int = 24,
    use_alternate_screen: bool = False,
    use_mouse: bool = False,
) -> Renderer:
    """创建用于测试的渲染器：无 TTY（MockTerminal）、不读 stdin，可注入 keypress。"""
    from pytui.core.renderer import Renderer

    terminal = MockTerminal(width, height)
    return Renderer(
        width=width,
        height=height,
        use_alternate_screen=use_alternate_screen,
        use_mouse=use_mouse,
        terminal=terminal,
    )
