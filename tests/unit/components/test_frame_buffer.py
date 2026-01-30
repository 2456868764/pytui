# tests/unit/components/test_frame_buffer.py

import pytest

pytest.importorskip("pytui.components.frame_buffer")


class TestFrameBuffer:
    def test_get_buffer_after_render(self, mock_context, buffer_40x20):
        from pytui.components.frame_buffer import FrameBuffer
        from pytui.core.buffer import Cell

        fb = FrameBuffer(mock_context, {"width": 5, "height": 3})
        fb.x, fb.y, fb.width, fb.height = 0, 0, 5, 3
        assert fb.get_buffer() is None
        fb.render_self(buffer_40x20)
        buf = fb.get_buffer()
        assert buf is not None
        assert buf.width == 5
        assert buf.height == 3
        buf.set_cell(0, 0, Cell(char="X", fg=(255, 255, 255, 255)))
        fb.render_self(buffer_40x20)
        assert buffer_40x20.get_cell(0, 0).char == "X"

    def test_blits_to_parent_buffer(self, mock_context, buffer_40x20):
        from pytui.components.frame_buffer import FrameBuffer
        from pytui.core.buffer import Cell

        fb = FrameBuffer(mock_context, {"width": 4, "height": 2})
        fb.x, fb.y, fb.width, fb.height = 2, 1, 4, 2
        fb.render_self(buffer_40x20)
        inner = fb.get_buffer()
        assert inner is not None
        inner.set_cell(1, 0, Cell(char="Z"))
        fb.render_self(buffer_40x20)
        assert buffer_40x20.get_cell(2 + 1, 1 + 0).char == "Z"
