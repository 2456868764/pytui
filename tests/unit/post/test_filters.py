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
