# pytui.testing.mock_keys - Aligns with OpenTUI packages/core/src/testing/mock-keys.ts
# createMockKeys(renderer, options?) -> MockKeys with feed(sequence).


from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pytui.core.renderer import Renderer


class MockKeys:
    """向 renderer 注入键盘序列的辅助对象。"""

    def __init__(self, renderer: Renderer) -> None:
        self._renderer = renderer

    def feed(self, data: str | bytes) -> None:
        """注入按键序列（如 'a'、'\\x1b[C' 表示右箭头）。"""
        self._renderer.keyboard.feed(data)


def create_mock_keys(renderer: Renderer) -> MockKeys:
    """返回可向 renderer 注入按键的 MockKeys。"""
    return MockKeys(renderer)
