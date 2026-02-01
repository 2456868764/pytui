# tests/unit/core/test_buffer.py - Aligns with OpenTUI packages/core/src/buffer.test.ts
"""OptimizedBuffer 单元测试。"""

import pytest

pytest.importorskip("pytui.core.buffer")


class TestOptimizedBuffer:
    """缓冲区创建、读写、绘制、清空、ANSI。"""

    def test_new_and_clear(self, buffer_10x5):
        from pytui.core.buffer import Cell

        buf = buffer_10x5
        buf.clear()
        for y in range(5):
            for x in range(10):
                c = buf.get_cell(x, y)
                assert c is not None
                assert c.char == " "

    def test_set_get_cell_in_bounds(self, buffer_10x5):
        from pytui.core.buffer import Cell

        buf = buffer_10x5
        cell = Cell(char="X", fg=(255, 0, 0, 255))
        buf.set_cell(2, 1, cell)
        got = buf.get_cell(2, 1)
        assert got is not None
        assert got.char == "X"
        assert got.fg == (255, 0, 0, 255)

    def test_set_cell_out_of_bounds_ignored(self, buffer_10x5):
        from pytui.core.buffer import Cell

        buf = buffer_10x5
        cell = Cell(char="Y")
        buf.set_cell(100, 100, cell)  # 不抛错，忽略
        # 不越界写入
        buf.set_cell(9, 4, cell)
        assert buf.get_cell(9, 4).char == "Y"

    def test_get_cell_out_of_bounds_returns_none(self, buffer_10x5):
        buf = buffer_10x5
        assert buf.get_cell(10, 0) is None
        assert buf.get_cell(0, 5) is None

    def test_draw_text_clips_to_width(self, buffer_10x5):
        buf = buffer_10x5
        buf.draw_text("hello world too long", 0, 0, (255, 255, 255, 255))
        # 仅前 10 个字符
        for i, ch in enumerate("hello worl"):
            c = buf.get_cell(i, 0)
            assert c is not None and c.char == ch

    def test_fill_rect(self, buffer_10x5):
        from pytui.core.buffer import Cell

        buf = buffer_10x5
        cell = Cell(char="#", bg=(0, 0, 100, 255))
        buf.fill_rect(1, 1, 3, 2, cell)
        for dy in range(2):
            for dx in range(3):
                c = buf.get_cell(1 + dx, 1 + dy)
                assert c is not None and c.char == "#"

    def test_to_ansi_contains_escape_codes(self, buffer_10x5):
        from pytui.core.buffer import Cell

        buf = buffer_10x5
        buf.set_cell(0, 0, Cell(char="A", fg=(255, 0, 0, 255)))
        ansi = buf.to_ansi()
        assert "\x1b" in ansi
        assert "A" in ansi

    def test_to_ansi_includes_sgr_strikethrough_dim_reverse_blink(self, buffer_10x5):
        from pytui.core.buffer import Cell

        buf = buffer_10x5
        buf.set_cell(0, 0, Cell(char="X", strikethrough=True, dim=True, reverse=True, blink=True))
        ansi = buf.to_ansi()
        # SGR: dim=2, blink=5, reverse=7, strikethrough=9
        assert "2;" in ansi or "2m" in ansi
        assert "5;" in ansi or "5m" in ansi
        assert "7;" in ansi or "7m" in ansi
        assert "9;" in ansi or "9m" in ansi
        assert "X" in ansi

    def test_blend_color(self):
        from pytui.core.buffer import OptimizedBuffer

        fg = (255, 0, 0, 255)
        bg = (0, 0, 0, 255)
        r = OptimizedBuffer.blend_color(fg, bg, 0.5)
        assert r[0] == 127
        assert r[1] == 0
        assert r[2] == 0
        assert r[3] == 255
        r0 = OptimizedBuffer.blend_color(fg, bg, 0.0)
        assert r0 == bg
        r1 = OptimizedBuffer.blend_color(fg, bg, 1.0)
        assert r1 == fg

    def test_set_cell_with_alpha_blends(self, buffer_10x5):
        from pytui.core.buffer import Cell, OptimizedBuffer

        buf = buffer_10x5
        buf.set_cell(0, 0, Cell(char="X", fg=(100, 100, 100, 255), bg=(0, 0, 0, 255)))
        buf.set_cell_with_alpha(
            0, 0,
            Cell(char="Y", fg=(200, 200, 200, 255), bg=(50, 50, 50, 255)),
            alpha=0.5,
        )
        c = buf.get_cell(0, 0)
        assert c is not None
        assert c.char == "Y"
        assert 100 < c.fg[0] < 200
        assert 100 < c.fg[1] < 200

    def test_create_class_method(self):
        """Align buffer.test.ts: OptimizedBuffer.create(20, 5, 'unicode', { id: 'test-buffer' })."""
        from pytui.core.buffer import OptimizedBuffer

        buf = OptimizedBuffer.create(20, 5, "unicode", {"id": "test-buffer"})
        assert buf.width == 20
        assert buf.height == 5
        assert buf.width_method == "unicode"
        buf.destroy()

    def test_create_with_respect_alpha(self):
        from pytui.core.buffer import OptimizedBuffer

        buf = OptimizedBuffer.create(10, 10, "wcwidth", {"respect_alpha": True})
        assert buf.respect_alpha is True
        buf.destroy()

    def test_destroy_no_op_twice(self):
        from pytui.core.buffer import OptimizedBuffer

        buf = OptimizedBuffer.create(5, 5, "unicode")
        buf.destroy()
        buf.destroy()  # second call no-op

    def test_after_destroy_raises(self, buffer_10x5):
        """After destroy(), any use should raise (align OpenTUI guard())."""
        from pytui.core.buffer import Cell, OptimizedBuffer

        buf = OptimizedBuffer.create(10, 5, "unicode")
        buf.destroy()
        with pytest.raises(RuntimeError, match="destroyed"):
            buf.set_cell(0, 0, Cell(char="x"))
        with pytest.raises(RuntimeError, match="destroyed"):
            buf.get_cell(0, 0)
        with pytest.raises(RuntimeError, match="destroyed"):
            buf.clear()
        with pytest.raises(RuntimeError, match="destroyed"):
            buf.draw_text("hi", 0, 0, (255, 255, 255, 255))
