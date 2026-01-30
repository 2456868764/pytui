# tests/unit/core/test_cell.py
"""Cell 单元测试。"""

import pytest

pytest.importorskip("pytui.core.buffer")


class TestCell:
    """Cell 默认值与转换。"""

    def test_default_values(self):
        from pytui.core.buffer import Cell

        c = Cell()
        assert c.char == " "
        assert c.fg == (255, 255, 255, 255)
        assert c.bg == (0, 0, 0, 0)
        assert c.bold is False
        assert c.italic is False
        assert c.underline is False

    def test_custom_values(self):
        from pytui.core.buffer import Cell

        c = Cell(char="x", fg=(1, 2, 3, 255), bold=True)
        assert c.char == "x"
        assert c.fg == (1, 2, 3, 255)
        assert c.bold is True

    def test_equality_for_diff(self):
        from pytui.core.buffer import Cell

        a = Cell(char="a", fg=(255, 0, 0, 255))
        b = Cell(char="a", fg=(255, 0, 0, 255))
        c = Cell(char="b", fg=(0, 255, 0, 255))
        assert a == b
        assert a != c

    def test_to_native_when_available(self):
        from pytui.core.buffer import Cell

        c = Cell(char="y", fg=(10, 20, 30, 255))
        native = c.to_native()
        # 无 native 时返回 None，有 native 时返回对象
        if native is not None:
            assert native.char == "y"
            assert native.fg == (10, 20, 30, 255)
