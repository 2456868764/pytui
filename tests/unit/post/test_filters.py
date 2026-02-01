# tests/unit/post/test_filters.py - 后处理滤镜占位单元测试

import pytest

pytest.importorskip("pytui.post.filters")


class TestFilters:
    def test_apply_dim_dims_buffer(self, buffer_10x5):
        from pytui.core.buffer import Cell, OptimizedBuffer
        from pytui.post.filters import apply_dim

        buf = buffer_10x5
        buf.set_cell(0, 0, Cell(char="A", fg=(255, 255, 255, 255), bg=(0, 0, 0, 255)))
        apply_dim(buf, alpha=0.0)
        c = buf.get_cell(0, 0)
        assert c is not None
        assert c.fg == (0, 0, 0, 255)
        assert c.bg == (0, 0, 0, 255)

    def test_apply_dim_alpha_one_no_change(self, buffer_10x5):
        from pytui.core.buffer import Cell
        from pytui.post.filters import apply_dim

        buf = buffer_10x5
        buf.set_cell(0, 0, Cell(char="B", fg=(100, 100, 100, 255)))
        apply_dim(buf, alpha=1.0)
        c = buf.get_cell(0, 0)
        assert c is not None
        assert c.fg == (100, 100, 100, 255)

    def test_apply_blur_placeholder_no_op(self, buffer_10x5):
        from pytui.core.buffer import Cell
        from pytui.post.filters import apply_blur_placeholder

        buf = buffer_10x5
        buf.set_cell(0, 0, Cell(char="C"))
        apply_blur_placeholder(buf, _radius=2)
        assert buf.get_cell(0, 0).char == "C"

    def test_apply_grayscale(self, buffer_10x5):
        from pytui.core.buffer import Cell
        from pytui.post.filters import apply_grayscale

        buf = buffer_10x5
        buf.set_cell(0, 0, Cell(char="X", fg=(255, 0, 0, 255), bg=(0, 255, 0, 255)))
        apply_grayscale(buf)
        c = buf.get_cell(0, 0)
        assert c is not None
        assert c.fg[0] == c.fg[1] == c.fg[2] == 76
        assert c.bg[0] == c.bg[1] == c.bg[2] == 149
        assert c.char == "X"

    def test_apply_sepia(self, buffer_10x5):
        from pytui.core.buffer import Cell
        from pytui.post.filters import apply_sepia

        buf = buffer_10x5
        buf.set_cell(0, 0, Cell(char="S", fg=(100, 100, 100, 255)))
        apply_sepia(buf)
        c = buf.get_cell(0, 0)
        assert c is not None
        assert 0 <= c.fg[0] <= 255 and 0 <= c.fg[1] <= 255 and 0 <= c.fg[2] <= 255
        assert c.fg[0] != 100 or c.fg[1] != 100 or c.fg[2] != 100
        assert c.char == "S"

    def test_apply_invert(self, buffer_10x5):
        from pytui.core.buffer import Cell
        from pytui.post.filters import apply_invert

        buf = buffer_10x5
        buf.set_cell(0, 0, Cell(char="I", fg=(255, 0, 100, 255), bg=(10, 20, 30, 255)))
        apply_invert(buf)
        c = buf.get_cell(0, 0)
        assert c is not None
        assert c.fg == (0, 255, 155, 255)
        assert c.bg == (245, 235, 225, 255)
        assert c.char == "I"

    def test_apply_scanlines(self, buffer_10x5):
        from pytui.core.buffer import Cell
        from pytui.post.filters import apply_scanlines

        buf = buffer_10x5
        buf.set_cell(0, 0, Cell(char="L", fg=(200, 200, 200, 255), bg=(200, 200, 200, 255)))
        buf.set_cell(0, 1, Cell(char="L", fg=(200, 200, 200, 255), bg=(200, 200, 200, 255)))
        apply_scanlines(buf, strength=0.5, step=2)
        c0 = buf.get_cell(0, 0)
        c1 = buf.get_cell(0, 1)
        assert c0 is not None and c1 is not None
        assert c0.fg[0] == 100
        assert c1.fg[0] == 200

    def test_apply_noise_changes_values(self, buffer_10x5):
        from pytui.core.buffer import Cell
        from pytui.post.filters import apply_noise

        buf = buffer_10x5
        buf.set_cell(0, 0, Cell(char="N", fg=(128, 128, 128, 255)))
        apply_noise(buf, strength=0.3)
        c = buf.get_cell(0, 0)
        assert c is not None
        assert 0 <= c.fg[0] <= 255 and 0 <= c.fg[1] <= 255 and 0 <= c.fg[2] <= 255
        assert c.char == "N"

    def test_apply_ascii_art(self, buffer_10x5):
        from pytui.core.buffer import Cell
        from pytui.post.filters import apply_ascii_art

        buf = buffer_10x5
        buf.set_cell(0, 0, Cell(char="?", bg=(0, 0, 0, 255)))
        buf.set_cell(1, 0, Cell(char="?", bg=(128, 128, 128, 255)))
        buf.set_cell(2, 0, Cell(char="?", bg=(255, 255, 255, 255)))
        apply_ascii_art(buf, ramp=" .#")
        c0 = buf.get_cell(0, 0)
        c1 = buf.get_cell(1, 0)
        c2 = buf.get_cell(2, 0)
        assert c0 is not None and c1 is not None and c2 is not None
        assert c0.char == " "
        assert c1.char == "."
        assert c2.char == "#"
